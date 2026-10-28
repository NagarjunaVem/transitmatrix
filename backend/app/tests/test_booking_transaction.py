# TransitMatrix - Transactional Booking Unit Tests
# Verifies atomic booking flow, rollback on error, and seat locking logic.

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.booking_service import BookingService
from app.schemas.booking import BookingCreateRequest, BookingPassengerItem


def test_booking_fails_when_trip_not_found():
    """
    Ensures that booking fails with HTTP 404 when the trip does not exist.
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True

    with patch("app.services.booking_service.get_connection", return_value=mock_conn):
        with patch("app.repositories.trip_repository.TripRepository.get_by_id", return_value=None):
            req = BookingCreateRequest(
                trip_id=9999,
                passengers=[
                    BookingPassengerItem(
                        passenger_id=1,
                        seat_id=10,
                        origin_station_id=1,
                        destination_station_id=2
                    )
                ],
                payment_method="UPI"
            )

            with pytest.raises(HTTPException) as exc:
                BookingService.create_booking(user_id=1, request=req)

            assert exc.value.status_code == 404
            mock_conn.rollback.assert_called_once()


def test_booking_fails_when_seat_already_reserved():
    """
    Ensures that booking fails with HTTP 409 Conflict when a seat is already reserved.
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True

    mock_trip = {
        "trip_id": 1,
        "status": "SCHEDULED",
        "base_fare": 500.00
    }
    # Mock seat inventory row with is_available = False
    mock_seat_inv = {
        "inventory_id": 101,
        "trip_id": 1,
        "seat_id": 10,
        "is_available": False,
        "coach_number": "A1",
        "seat_number": "01",
        "seat_class": "1A",
        "fare_multiplier": 1.5
    }

    with patch("app.services.booking_service.get_connection", return_value=mock_conn):
        with patch("app.repositories.trip_repository.TripRepository.get_by_id", return_value=mock_trip):
            with patch("app.repositories.inventory_repository.InventoryRepository.get_seat_for_update", return_value=mock_seat_inv):
                req = BookingCreateRequest(
                    trip_id=1,
                    passengers=[
                        BookingPassengerItem(
                            passenger_id=1,
                            seat_id=10,
                            origin_station_id=1,
                            destination_station_id=2
                        )
                    ],
                    payment_method="UPI"
                )

                with pytest.raises(HTTPException) as exc:
                    BookingService.create_booking(user_id=1, request=req)

                assert exc.value.status_code == 409
                assert "already reserved" in exc.value.detail
                mock_conn.rollback.assert_called_once()
