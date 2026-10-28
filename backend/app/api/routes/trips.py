# TransitMatrix - Trip Journey Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from datetime import date
from app.schemas.trip import TripCreate, TripUpdate, TripResponse, TripSearchResultResponse
from app.services.transit_service import TransitService
from app.api.deps import require_roles

router = APIRouter(prefix="/trips", tags=["Trips"])


@router.get("/search", response_model=List[TripSearchResultResponse])
def search_trips(
    origin_code: str = Query(..., description="Origin Station Code, e.g. NDLS"),
    destination_code: str = Query(..., description="Destination Station Code, e.g. MMCT"),
    travel_date: date = Query(..., description="Date of travel (YYYY-MM-DD)")
):
    """
    Search available trips between origin and destination on a given date.
    Executes stored procedure sp_search_trips with live seat counts.
    """
    return TransitService.search_trips(origin_code, destination_code, travel_date)


@router.get("", response_model=List[TripResponse])
def get_trips(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    status: Optional[str] = None,
    trip_date: Optional[date] = None
):
    """
    List scheduled journey trips with filtering options.
    """
    return TransitService.list_trips(limit, offset, status, trip_date)


@router.get("/{trip_id}", response_model=TripResponse)
def get_trip(trip_id: int):
    """
    Retrieve trip journey details by ID.
    """
    return TransitService.get_trip_by_id(trip_id)


@router.post("", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
def create_trip(
    request: TripCreate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Schedule a new journey trip and automatically initialize seat inventory (Admin/Staff only).
    """
    return TransitService.create_trip(request)
