# TransitMatrix - Cancellation and Refund Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CancellationCreateRequest(BaseModel):
    ticket_id: int
    cancellation_reason: Optional[str] = Field("Customer voluntary cancellation", max_length=255)


class CancellationResponse(BaseModel):
    cancellation_id: int
    booking_id: int
    ticket_id: int
    cancellation_reason: Optional[str] = None
    cancellation_fee: float
    refund_amount: float
    refund_status: str
    cancelled_at: datetime

    class Config:
        from_attributes = True
