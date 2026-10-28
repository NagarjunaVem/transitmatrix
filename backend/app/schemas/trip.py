# TransitMatrix - Trip Journey Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class TripBase(BaseModel):
    service_id: int
    route_id: int
    vehicle_id: int
    trip_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    base_fare: float = Field(..., gt=0.0)


class TripCreate(TripBase):
    pass


class TripUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(SCHEDULED|BOARDING|ON_TIME|DELAYED|CANCELLED|COMPLETED)$")
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    base_fare: Optional[float] = Field(None, gt=0.0)


class TripResponse(TripBase):
    trip_id: int
    status: str
    actual_departure: Optional[datetime] = None
    actual_arrival: Optional[datetime] = None
    created_at: Optional[datetime] = None
    service_number: Optional[str] = None
    service_name: Optional[str] = None
    route_code: Optional[str] = None
    route_name: Optional[str] = None
    vehicle_number: Optional[str] = None

    class Config:
        from_attributes = True


class TripSearchResultResponse(BaseModel):
    trip_id: int
    service_number: str
    service_name: str
    service_type: str
    route_code: str
    route_name: str
    trip_date: date
    scheduled_departure: datetime
    scheduled_arrival: datetime
    trip_status: str
    base_fare: float
    origin_station_name: str
    destination_station_name: str
    total_seats: int
    available_seats: int

    class Config:
        from_attributes = True
