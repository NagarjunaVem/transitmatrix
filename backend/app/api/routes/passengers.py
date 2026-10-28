# TransitMatrix - Passenger Profile Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Dict, Any, Optional
from app.schemas.passenger import PassengerCreate, PassengerResponse
from app.services.transit_service import TransitService
from app.api.deps import get_current_user

router = APIRouter(prefix="/passengers", tags=["Passengers"])


@router.get("", response_model=List[PassengerResponse])
def get_passengers(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    List passengers. Regular passengers only see their own linked profiles; Admin/Staff see all.
    """
    user_id = current_user["user_id"] if current_user.get("role") == "PASSENGER" else None
    return TransitService.list_passengers(user_id=user_id, limit=limit, offset=offset)


@router.post("", response_model=PassengerResponse, status_code=status.HTTP_201_CREATED)
def create_passenger(
    request: PassengerCreate,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Create a new traveler passenger profile linked to current user.
    """
    if current_user.get("role") == "PASSENGER":
        request.user_id = current_user["user_id"]
    return TransitService.create_passenger(request)
