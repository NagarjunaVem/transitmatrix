# TransitMatrix - Rolling Stock Vehicle Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List
from app.schemas.vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from app.services.transit_service import TransitService
from app.api.deps import require_roles

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("", response_model=List[VehicleResponse])
def get_vehicles(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    List rolling stock rakes and train vehicles.
    """
    return TransitService.list_vehicles(limit, offset)


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle(vehicle_id: int):
    """
    Retrieve train vehicle specifications by ID.
    """
    return TransitService.get_vehicle_by_id(vehicle_id)


@router.post("", response_model=VehicleResponse, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    request: VehicleCreate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Register a new vehicle rake into the system (Admin/Staff only).
    """
    return TransitService.create_vehicle(request)
