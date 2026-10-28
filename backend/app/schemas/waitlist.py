# TransitMatrix - Waitlist Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class WaitlistCreateRequest(BaseModel):
    trip_id: int
    passenger_id: int
    booking_id: int
    seat_class: str = Field(..., pattern="^(1A|2A|3A|SL|CC|EC|GEN)$")


class WaitlistResponse(BaseModel):
    waitlist_id: int
    trip_id: int
    passenger_id: int
    passenger_name: Optional[str] = None
    booking_id: int
    booking_reference: Optional[str] = None
    seat_class: str
    waitlist_number: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class WaitlistPromotionResponse(BaseModel):
    trip_id: int
    seat_class: str
    freed_seat_id: int
    promoted_passenger_id: Optional[int] = None
    status_message: str
