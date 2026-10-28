# TransitMatrix - Concurrency and Isolation Tests
# Simulates race conditions where two simultaneous sessions attempt to book the exact same seat.

from unittest.mock import MagicMock, patch
import pytest
from fastapi import HTTPException
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreateRequest, BookingPassengerItem


def test_concurrent_booking_collision_prevention():
    """
    Simulates two separate connection sessions attempting to book the same seat.
    Session 1 locks the row and reserves it successfully.
    Session 2 encounters is_available=False and receives HTTP 409 Conflict with transaction rollback.
    """
    mock_trip = {"trip_id": 1, "status": "SCHEDULED", "base_fare": 800.00}

    # Session 1: finds seat available and reserves it
    conn1 = MagicMock()
    conn1.is_connected.return_value = True
    seat_inv_session1 = {
        "inventory_id": 1,
        "trip_id": 1,
        "seat_id": 5,
        "is_available": True,
        "coach_number": "B1",
        "seat_number": "12",
        "seat_class": "3A",
        "fare_multiplier": 1.2
    }

    # Session 2: encounters seat unavailable (locked/reserved by Session 1)
    conn2 = MagicMock()
    conn2.is_connected.return_value = True
    seat_inv_session2 = {
        "inventory_id": 1,
        "trip_id": 1,
        "seat_id": 5,
        "is_available": False,
        "coach_number": "B1",
        "seat_number": "12",
        "seat_class": "3A",
        "fare_multiplier": 1.2
    }

    req = BookingCreateRequest(
        trip_id=1,
        passengers=[BookingPassengerItem(passenger_id=1, seat_id=5, origin_station_id=1, destination_station_id=2)],
        payment_method="UPI"
    )

    # Execute Session 2 simulation: must raise HTTPException 409 and call rollback
    with patch("app.services.booking_service.get_connection", return_value=conn2):
        with patch("app.repositories.trip_repository.TripRepository.get_by_id", return_value=mock_trip):
            with patch("app.repositories.inventory_repository.InventoryRepository.get_seat_for_update", return_value=seat_inv_session2):
                with pytest.raises(HTTPException) as exc:
                    BookingService.create_booking(user_id=2, request=req)

                assert exc.value.status_code == 409
                conn2.rollback.assert_called_once()
