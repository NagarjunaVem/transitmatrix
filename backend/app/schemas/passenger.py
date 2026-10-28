# TransitMatrix - Passenger Profile Pydantic Schemas

from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


class PassengerBase(BaseModel):
    user_id: Optional[int] = None
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    gender: str = Field(..., pattern="^(MALE|FEMALE|OTHER)$")
    age: int = Field(..., ge=1, le=120)
    id_card_type: str = Field(..., pattern="^(AADHAAR|PASSPORT|PAN|VOTER_ID|DRIVING_LICENSE)$")
    id_card_number: str = Field(..., min_length=4, max_length=50)
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None


class PassengerCreate(PassengerBase):
    pass


class PassengerResponse(PassengerBase):
    passenger_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
