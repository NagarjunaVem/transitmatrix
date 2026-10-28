# TransitMatrix - Payment Settlement Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PaymentCreateRequest(BaseModel):
    booking_id: int
    payment_method: str = Field(..., pattern="^(CREDIT_CARD|DEBIT_CARD|UPI|NET_BANKING|WALLET)$")
    amount: float = Field(..., gt=0.0)


class PaymentResponse(BaseModel):
    payment_id: int
    booking_id: int
    transaction_reference: str
    payment_method: str
    amount: float
    payment_status: str
    paid_at: datetime

    class Config:
        from_attributes = True
