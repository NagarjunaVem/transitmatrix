# TransitMatrix - Station Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.schemas.station import StationCreate, StationUpdate, StationResponse
from app.services.transit_service import TransitService
from app.api.deps import require_roles

router = APIRouter(prefix="/stations", tags=["Stations"])


@router.get("", response_model=List[StationResponse])
def get_stations(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    search: Optional[str] = None
):
    """
    List stations with optional text filtering on code, name, or city.
    """
    return TransitService.list_stations(limit, offset, search)


@router.get("/{station_id}", response_model=StationResponse)
def get_station(station_id: int):
    """
    Retrieve single station by ID.
    """
    return TransitService.get_station_by_id(station_id)


@router.post("", response_model=StationResponse, status_code=status.HTTP_201_CREATED)
def create_station(
    request: StationCreate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Create a new station (Admin/Staff only).
    """
    return TransitService.create_station(request)


@router.put("/{station_id}", response_model=StationResponse)
def update_station(
    station_id: int,
    request: StationUpdate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Update station details (Admin/Staff only).
    """
    return TransitService.update_station(station_id, request)


@router.delete("/{station_id}")
def delete_station(
    station_id: int,
    current_user=Depends(require_roles("ADMIN"))
):
    """
    Delete a station (Admin only).
    """
    return TransitService.delete_station(station_id)
