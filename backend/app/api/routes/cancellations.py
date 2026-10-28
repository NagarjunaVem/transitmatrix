# TransitMatrix - Cancellation Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Dict, Any
from app.schemas.cancellation import CancellationCreateRequest, CancellationResponse
from app.services.cancellation_service import CancellationService
from app.api.deps import get_current_user

router = APIRouter(prefix="/cancellations", tags=["Cancellations"])


@router.post("", response_model=CancellationResponse, status_code=status.HTTP_201_CREATED)
def cancel_ticket(
    request: CancellationCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Cancel an individual ticket, calculate refund, and release seat inventory.
    """
    return CancellationService.cancel_ticket(current_user, request)


@router.get("/booking/{booking_id}", response_model=List[CancellationResponse])
def get_cancellations_by_booking(
    booking_id: int,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List cancellation and refund records associated with a booking.
    """
    return CancellationService.get_cancellations_by_booking(booking_id)
