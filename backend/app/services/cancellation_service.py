# TransitMatrix - Cancellation Service
# Handles ticket cancellations, refund calculations, and seat release.

from fastapi import HTTPException, status
from typing import Optional, Dict, Any, List
from mysql.connector import Error
from app.db.connection import get_connection, get_db_connection
from app.repositories.cancellation_repository import CancellationRepository
from app.repositories.booking_repository import BookingRepository
from app.repositories.inventory_repository import InventoryRepository
from app.schemas.cancellation import CancellationCreateRequest, CancellationResponse


class CancellationService:

    @staticmethod
    def cancel_ticket(
        current_user: Dict[str, Any],
        request: CancellationCreateRequest
    ) -> CancellationResponse:
        """
        Executes ticket cancellation with refund calculation and automatic seat inventory release.
        """
        connection = get_connection()
        try:
            connection.start_transaction()

            ticket = CancellationRepository.get_ticket_for_cancellation(connection, request.ticket_id)
            if not ticket:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

            # Check authorization: Passenger can only cancel their own tickets
            if current_user.get("role") == "PASSENGER" and ticket["user_id"] != current_user["user_id"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot cancel another user's ticket")

            if ticket["ticket_status"] == "CANCELLED":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket is already cancelled")

            # Check if ticket already has a cancellation record
            existing_cancellation = CancellationRepository.get_cancellation_by_ticket_id(connection, request.ticket_id)
            if existing_cancellation:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cancellation record already exists")

            # Calculate cancellation fee (15% standard fee, minimum 50, capped at fare)
            fare = float(ticket["fare_amount"])
            cancellation_fee = round(min(fare, max(50.0, fare * 0.15)), 2)
            refund_amount = round(max(0.0, fare - cancellation_fee), 2)

            # Insert cancellation record
            # MySQL trigger 'trg_cancellation_after_insert' automatically:
            # 1. Updates tickets.ticket_status = 'CANCELLED'
            # 2. Updates trip_seat_inventory.is_available = TRUE
            # 3. Records entry in audit_logs
            cancellation_id = CancellationRepository.create_cancellation(
                connection=connection,
                booking_id=ticket["booking_id"],
                ticket_id=request.ticket_id,
                cancellation_reason=request.cancellation_reason,
                cancellation_fee=cancellation_fee,
                refund_amount=refund_amount,
                refund_status="PROCESSED"
            )

            # Check remaining active tickets in booking to update master booking status
            tickets = BookingRepository.get_booking_tickets(connection, ticket["booking_id"])
            active_tickets = [t for t in tickets if t["ticket_id"] != request.ticket_id and t["ticket_status"] != "CANCELLED"]

            if not active_tickets:
                BookingRepository.update_booking_status(connection, ticket["booking_id"], "CANCELLED")
            else:
                BookingRepository.update_booking_status(connection, ticket["booking_id"], "PARTIALLY_CANCELLED")

            # Fallback explicit seat release if triggers were disabled or bypassed
            if ticket.get("seat_id"):
                InventoryRepository.release_seat(connection, ticket["trip_id"], ticket["seat_id"])

            connection.commit()

            cancellation_record = CancellationRepository.get_cancellation_by_ticket_id(connection, request.ticket_id)
            return CancellationResponse(**cancellation_record)

        except (Error, Exception) as err:
            try:
                connection.rollback()
            except Exception:
                pass

            if isinstance(err, HTTPException):
                raise err

            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Cancellation failed: {str(err)}"
            )
        finally:
            if connection.is_connected():
                connection.close()

    @staticmethod
    def get_cancellations_by_booking(booking_id: int) -> List[CancellationResponse]:
        with get_db_connection() as conn:
            records = CancellationRepository.get_cancellations_by_booking_id(conn, booking_id)
            return [CancellationResponse(**r) for r in records]
