# TransitMatrix - Waitlist Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.schemas.waitlist import WaitlistCreateRequest, WaitlistResponse, WaitlistPromotionResponse
from app.services.waitlist_service import WaitlistService
from app.api.deps import require_roles, get_current_user

router = APIRouter(prefix="/waitlists", tags=["Waitlists"])


@router.get("/trip/{trip_id}", response_model=List[WaitlistResponse])
def get_trip_waitlist(
    trip_id: int,
    seat_class: Optional[str] = Query(None, pattern="^(1A|2A|3A|SL|CC|EC|GEN)$")
):
    """
    Get waiting queue passengers for a trip ordered by waitlist sequence.
    """
    return WaitlistService.get_trip_waitlist(trip_id, seat_class)


@router.post("", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
def add_to_waitlist(
    request: WaitlistCreateRequest,
    current_user=Depends(get_current_user)
):
    """
    Queue a passenger into the trip waitlist.
    """
    return WaitlistService.add_to_waitlist(request)


@router.post("/promote", response_model=WaitlistPromotionResponse)
def promote_waitlist_passenger(
    trip_id: int = Query(...),
    seat_class: str = Query(..., pattern="^(1A|2A|3A|SL|CC|EC|GEN)$"),
    freed_seat_id: int = Query(...),
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Executes stored procedure sp_process_waitlist_promotion to promote the top queue passenger.
    """
    return WaitlistService.promote_passenger(trip_id, seat_class, freed_seat_id)
