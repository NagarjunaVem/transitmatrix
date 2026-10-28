# TransitMatrix - Route and Route Stops Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class RouteStopBase(BaseModel):
    station_id: int
    stop_sequence: int = Field(..., ge=1)
    distance_from_origin_km: float = Field(..., ge=0.0)
    departure_offset_minutes: int = Field(0, ge=0)
    arrival_offset_minutes: int = Field(0, ge=0)
    halt_duration_minutes: int = Field(0, ge=0)
    platform_number: int = Field(1, ge=1)


class RouteStopCreate(RouteStopBase):
    pass


class RouteStopResponse(RouteStopBase):
    stop_id: int
    route_id: int
    station_code: Optional[str] = None
    station_name: Optional[str] = None

    class Config:
        from_attributes = True


class RouteBase(BaseModel):
    route_code: str = Field(..., min_length=2, max_length=20)
    route_name: str = Field(..., min_length=2, max_length=100)
    origin_station_id: int
    destination_station_id: int
    total_distance_km: float = Field(..., gt=0.0)
    duration_est_minutes: int = Field(..., gt=0)
    is_active: bool = True


class RouteCreate(RouteBase):
    pass


class RouteResponse(RouteBase):
    route_id: int
    origin_station_code: Optional[str] = None
    origin_station_name: Optional[str] = None
    destination_station_code: Optional[str] = None
    destination_station_name: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class RouteDetailResponse(RouteResponse):
    stops: List[RouteStopResponse] = []
