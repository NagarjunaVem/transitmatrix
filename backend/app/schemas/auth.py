# TransitMatrix - Authentication Pydantic Schemas
# Request validation and JSON serialization models (no ORM)

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=100)
    role: str = Field("PASSENGER", pattern="^(ADMIN|STAFF|PASSENGER)$")
    first_name: str = Field(..., min_length=1, max_length=50)
    last_name: str = Field(..., min_length=1, max_length=50)
    phone_number: str = Field(..., min_length=5, max_length=20)


class UserLoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    username: str
    role: str


class UserProfileResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    first_name: str
    last_name: str
    phone_number: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Alias for backward-compatibility with schemas package
UserResponse = UserProfileResponse
