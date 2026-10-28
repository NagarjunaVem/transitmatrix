# TransitMatrix - Rolling Stock Vehicle Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class SeatResponse(BaseModel):
    seat_id: int
    coach_number: str
    seat_number: str
    seat_class: str
    seat_type: str
    fare_multiplier: float

    class Config:
        from_attributes = True


class VehicleBase(BaseModel):
    vehicle_number: str = Field(..., min_length=2, max_length=30)
    vehicle_type: str = Field(..., pattern="^(LOCOMOTIVE_TRAIN|ELECTRIC_MULTIPLE_UNIT|METRO_RAIL|DIESEL_MULTIPLE_UNIT)$")
    model_name: str = Field(..., min_length=2, max_length=50)
    manufacture_year: int = Field(..., ge=1990)
    total_coaches: int = Field(..., ge=1)
    total_capacity: int = Field(..., ge=1)
    maintenance_status: str = Field("OPERATIONAL", pattern="^(OPERATIONAL|UNDER_MAINTENANCE|DECOMMISSIONED)$")


class VehicleCreate(VehicleBase):
    pass


class VehicleUpdate(BaseModel):
    maintenance_status: Optional[str] = Field(None, pattern="^(OPERATIONAL|UNDER_MAINTENANCE|DECOMMISSIONED)$")
    total_capacity: Optional[int] = Field(None, ge=1)


class VehicleResponse(VehicleBase):
    vehicle_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
