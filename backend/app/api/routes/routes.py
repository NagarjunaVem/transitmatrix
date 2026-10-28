# TransitMatrix - Route Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List
from app.schemas.route import RouteCreate, RouteStopCreate, RouteResponse, RouteDetailResponse
from app.services.transit_service import TransitService
from app.api.deps import require_roles

router = APIRouter(prefix="/routes", tags=["Routes"])


@router.get("", response_model=List[RouteResponse])
def get_routes(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0)
):
    """
    List transit corridors and route lines.
    """
    return TransitService.list_routes(limit, offset)


@router.get("/{route_id}", response_model=RouteDetailResponse)
def get_route(route_id: int):
    """
    Retrieve route details with its complete ordered sequence of station stops.
    """
    return TransitService.get_route_details(route_id)


@router.post("", response_model=RouteDetailResponse, status_code=status.HTTP_201_CREATED)
def create_route(
    request: RouteCreate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Create a new transit route corridor (Admin/Staff only).
    """
    return TransitService.create_route(request)


@router.post("/{route_id}/stops", response_model=RouteDetailResponse, status_code=status.HTTP_201_CREATED)
def add_stop_to_route(
    route_id: int,
    request: RouteStopCreate,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Add an intermediate station stop to a route with sequence and halt offsets (Admin/Staff only).
    """
    return TransitService.add_route_stop(route_id, request)
