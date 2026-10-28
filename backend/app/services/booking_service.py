# TransitMatrix - Transactional Booking Service
# Executes atomic reservations with pessimistic concurrency locking (SELECT ... FOR UPDATE).

import uuid
from datetime import datetime, timezone
from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from mysql.connector import Error, errorcode
from app.db.connection import get_connection, get_db_connection
from app.repositories.inventory_repository import InventoryRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.payment_repository import PaymentRepository
from app.repositories.trip_repository import TripRepository
from app.schemas.booking import BookingCreateRequest, BookingResponse, SeatMapItem


class BookingService:

    @staticmethod
    def get_trip_seat_map(trip_id: int, coach_number: Optional[str] = None) -> List[SeatMapItem]:
        """
        Retrieves real-time seat availability map for a trip.
        """
        with get_db_connection() as conn:
            trip = TripRepository.get_by_id(conn, trip_id)
            if not trip:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
            seats = InventoryRepository.get_trip_seat_map(conn, trip_id, coach_number)
            return [SeatMapItem(**s) for s in seats]

    @staticmethod
    def create_booking(user_id: int, request: BookingCreateRequest) -> BookingResponse:
        """
        Atomic multi-table booking reservation.
        Enforces ACID properties with SELECT ... FOR UPDATE pessimistic row-level locking.
        """
        connection = get_connection()
        try:
            # Begin explicit transaction
            connection.start_transaction()

            # 1. Validate Trip
            trip = TripRepository.get_by_id(connection, request.trip_id)
            if not trip:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
            if trip["status"] in ("CANCELLED", "COMPLETED"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Cannot book seats for a trip with status '{trip['status']}'."
                )

            total_fare = 0.0
            passenger_tickets = []
            base_fare = float(trip["base_fare"])

            # 2. Lock and reserve each requested seat
            for item in request.passengers:
                # Row-level lock via SELECT ... FOR UPDATE
                seat_inv = InventoryRepository.get_seat_for_update(connection, request.trip_id, item.seat_id)
                if not seat_inv:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Seat ID {item.seat_id} is not mapped to trip {request.trip_id}."
                    )

                if not seat_inv["is_available"]:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Seat {seat_inv['coach_number']}-{seat_inv['seat_number']} ({seat_inv['seat_class']}) is already reserved."
                    )

                # Mark seat unavailable in inventory
                reserved = InventoryRepository.reserve_seat(connection, request.trip_id, item.seat_id)
                if not reserved:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail=f"Concurrent conflict: Seat {seat_inv['coach_number']}-{seat_inv['seat_number']} was just taken."
                    )

                multiplier = float(seat_inv.get("fare_multiplier", 1.0))
                ticket_fare = round(base_fare * multiplier, 2)
                total_fare += ticket_fare

                passenger_tickets.append({
                    "passenger_id": item.passenger_id,
                    "seat_id": item.seat_id,
                    "origin_station_id": item.origin_station_id,
                    "destination_station_id": item.destination_station_id,
                    "fare_amount": ticket_fare
                })

            # 3. Insert Master Booking Header
            # Generate unique 10-char PNR reference: TMX + 7 hex characters
            pnr_ref = "TMX" + uuid.uuid4().hex[:7].upper()
            total_passengers = len(request.passengers)

            booking_id = BookingRepository.create_booking(
                connection=connection,
                booking_reference=pnr_ref,
                user_id=user_id,
                trip_id=request.trip_id,
                total_passengers=total_passengers,
                total_fare=total_fare,
                booking_status="CONFIRMED"
            )

            # 4. Insert Individual Tickets
            for idx, pt in enumerate(passenger_tickets, start=1):
                ticket_num = f"TKT-{pnr_ref}-{idx:02d}"
                BookingRepository.create_ticket(
                    connection=connection,
                    booking_id=booking_id,
                    passenger_id=pt["passenger_id"],
                    seat_id=pt["seat_id"],
                    origin_station_id=pt["origin_station_id"],
                    destination_station_id=pt["destination_station_id"],
                    ticket_number=ticket_num,
                    fare_amount=pt["fare_amount"],
                    ticket_status="CONFIRMED"
                )

            # 5. Record Payment Receipt
            txn_ref = "TXN-" + datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S") + "-" + uuid.uuid4().hex[:6].upper()
            PaymentRepository.create_payment(
                connection=connection,
                booking_id=booking_id,
                transaction_reference=txn_ref,
                payment_method=request.payment_method,
                amount=total_fare,
                payment_status="SUCCESS"
            )

            # 6. Commit Atomic Transaction
            connection.commit()

            # Retrieve complete booking details for response
            booking_record = BookingRepository.get_booking_by_id(connection, booking_id)
            tickets = BookingRepository.get_booking_tickets(connection, booking_id)
            booking_record["tickets"] = tickets

            return BookingResponse(**booking_record)

        except (Error, Exception) as err:
            # Rollback all state changes upon error
            try:
                connection.rollback()
            except Exception:
                pass

            if isinstance(err, HTTPException):
                raise err

            if isinstance(err, Error) and err.errno == errorcode.ER_LOCK_DEADLOCK:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Database deadlock occurred during booking. Please retry."
                )

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Booking transaction failed: {str(err)}"
            )

        finally:
            if connection.is_connected():
                connection.close()

    @staticmethod
    def get_booking_by_reference(booking_reference: str, user_id: Optional[int] = None) -> BookingResponse:
        """
        Retrieves booking by PNR reference. Enforces authorization.
        """
        with get_db_connection() as conn:
            booking = BookingRepository.get_booking_by_reference(conn, booking_reference)
            if not booking:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

            # Validate passenger ownership if user_id is provided
            if user_id is not None and booking["user_id"] != user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to booking denied")

            tickets = BookingRepository.get_booking_tickets(conn, booking["booking_id"])
            booking["tickets"] = tickets
            return BookingResponse(**booking)

    @staticmethod
    def list_user_bookings(user_id: int, limit: int = 50, offset: int = 0) -> List[BookingResponse]:
        """
        Lists chronological bookings for a specific user.
        """
        with get_db_connection() as conn:
            bookings = BookingRepository.list_user_bookings(conn, user_id, limit, offset)
            result = []
            for b in bookings:
                tickets = BookingRepository.get_booking_tickets(conn, b["booking_id"])
                b["tickets"] = tickets
                result.append(BookingResponse(**b))
            return result
