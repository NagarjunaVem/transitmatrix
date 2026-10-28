# TransitMatrix - Delay Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.schemas.delay import DelayCreateRequest, DelayResponse
from app.services.delay_service import DelayService
from app.api.deps import require_roles

router = APIRouter(prefix="/delays", tags=["Delays"])


@router.get("", response_model=List[DelayResponse])
def get_delays(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    trip_id: Optional[int] = None
):
    """
    List recorded delay incidents.
    """
    return DelayService.list_delays(limit, offset, trip_id)


@router.post("", response_model=DelayResponse, status_code=status.HTTP_201_CREATED)
def record_delay(
    request: DelayCreateRequest,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Record an operational transit delay incident.
    Triggers automatic status update to DELAYED if minutes >= 15.
    """
    return DelayService.record_delay(request)
