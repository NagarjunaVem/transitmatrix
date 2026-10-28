# TransitMatrix - Station Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StationBase(BaseModel):
    station_code: str = Field(..., min_length=2, max_length=10)
    station_name: str = Field(..., min_length=2, max_length=100)
    city: str = Field(..., min_length=2, max_length=50)
    state: str = Field(..., min_length=2, max_length=50)
    zone: str = Field(..., min_length=2, max_length=20)
    total_platforms: int = Field(2, ge=1)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    is_active: bool = True


class StationCreate(StationBase):
    pass


class StationUpdate(BaseModel):
    station_name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zone: Optional[str] = None
    total_platforms: Optional[int] = Field(None, ge=1)
    latitude: Optional[float] = Field(None, ge=-90.0, le=90.0)
    longitude: Optional[float] = Field(None, ge=-180.0, le=180.0)
    is_active: Optional[bool] = None


class StationResponse(StationBase):
    station_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
