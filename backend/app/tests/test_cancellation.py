# TransitMatrix - Cancellation and Refund Unit Tests

import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from app.services.cancellation_service import CancellationService
from app.schemas.cancellation import CancellationCreateRequest


def test_cancel_ticket_unauthorized_user():
    """
    Ensures a passenger cannot cancel another passenger's ticket (HTTP 403).
    """
    mock_conn = MagicMock()
    mock_conn.is_connected.return_value = True

    mock_ticket = {
        "ticket_id": 10,
        "booking_id": 1,
        "passenger_id": 1,
        "user_id": 99,  # Belongs to user 99
        "ticket_status": "CONFIRMED",
        "fare_amount": 1000.00
    }

    current_user = {"user_id": 42, "role": "PASSENGER"}  # Different user
    req = CancellationCreateRequest(ticket_id=10, cancellation_reason="Changed travel plans")

    with patch("app.services.cancellation_service.get_connection", return_value=mock_conn):
        with patch("app.repositories.cancellation_repository.CancellationRepository.get_ticket_for_cancellation", return_value=mock_ticket):
            with pytest.raises(HTTPException) as exc:
                CancellationService.cancel_ticket(current_user, req)

            assert exc.value.status_code == 403
            assert "Cannot cancel another user's ticket" in exc.value.detail
            mock_conn.rollback.assert_called_once()
