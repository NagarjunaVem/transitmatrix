# TransitMatrix - Payment Endpoints

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from app.schemas.payment import PaymentResponse
from app.db.connection import get_db_connection
from app.repositories.payment_repository import PaymentRepository
from app.repositories.booking_repository import BookingRepository
from app.api.deps import get_current_user

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/booking/{booking_id}", response_model=PaymentResponse)
def get_payment_details(
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve payment transaction receipt for a given booking.
    """
    with get_db_connection() as conn:
        booking = BookingRepository.get_booking_by_id(conn, booking_id)
        if not booking:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")

        if current_user.get("role") == "PASSENGER" and booking["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")

        payment = PaymentRepository.get_payment_by_booking_id(conn, booking_id)
        if not payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment record not found")
        return PaymentResponse(**payment)
