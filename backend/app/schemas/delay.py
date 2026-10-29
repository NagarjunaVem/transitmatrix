# TransitMatrix - Delay Tracking Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DelayCreateRequest(BaseModel):
    trip_id: int
    station_id: int
    delay_minutes: int = Field(..., ge=1)
    delay_reason: str = Field(..., pattern="^(WEATHER|TRACK_MAINTENANCE|SIGNAL_FAILURE|CONGESTION|TECHNICAL_GLITCH|ACCIDENT|OTHER)$")
    incident_description: Optional[str] = Field(None, max_length=255)


class DelayResponse(BaseModel):
    delay_id: int
    trip_id: int
    station_id: int
    station_name: Optional[str] = None
    station_code: Optional[str] = None
    delay_minutes: int
    delay_reason: str
    incident_description: Optional[str] = None
    recorded_at: datetime

    class Config:
        from_attributes = True

from app.schemas.report import DelaySummaryReportItem
