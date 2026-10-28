# TransitMatrix - Service Catalog Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.services.transit_service import TransitService
from app.api.deps import require_roles

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("", response_model=List[ServiceResponse])
def get_services(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    List scheduled transit services (e.g. Rajdhani, Shatabdi, Vande Bharat).
    """
    return TransitService.list_services(limit, offset)


@router.get("/{service_id}", response_model=ServiceResponse)
def get_service(service_id: int):
    """
    Retrieve service catalog item by ID.
    """
    return TransitService.get_service_by_id(service_id)


@router.post("", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def create_service(
    request: ServiceCreate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Add a new train service to the transit catalog (Admin/Staff only).
    """
    return TransitService.create_service(request)
