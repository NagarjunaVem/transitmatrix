# TransitMatrix - Booking Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Dict, Any, Optional
from app.schemas.booking import BookingCreateRequest, BookingResponse, SeatMapItem
from app.services.booking_service import BookingService
from app.api.deps import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.get("/trip/{trip_id}/seats", response_model=List[SeatMapItem])
def get_trip_seat_map(
    trip_id: int,
    coach_number: Optional[str] = Query(None, description="Optional coach filter (e.g. A1, B1, S1)")
):
    """
    Get real-time seat availability map for a specific trip.
    """
    return BookingService.get_trip_seat_map(trip_id, coach_number)


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def create_booking(
    request: BookingCreateRequest,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Execute an atomic, multi-seat reservation using SELECT ... FOR UPDATE row-level locking.
    """
    return BookingService.create_booking(current_user["user_id"], request)


@router.get("/my-bookings", response_model=List[BookingResponse])
def get_my_bookings(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List bookings created by the authenticated user in reverse chronological order.
    """
    return BookingService.list_user_bookings(current_user["user_id"], limit, offset)


@router.get("/{booking_reference}", response_model=BookingResponse)
def get_booking_by_reference(
    booking_reference: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Retrieve booking and ticket details by PNR booking reference.
    """
    user_id = current_user["user_id"] if current_user.get("role") == "PASSENGER" else None
    return BookingService.get_booking_by_reference(booking_reference, user_id=user_id)
