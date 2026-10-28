# TransitMatrix - Transit Service Catalog Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ServiceBase(BaseModel):
    service_number: str = Field(..., min_length=2, max_length=20)
    service_name: str = Field(..., min_length=2, max_length=100)
    service_type: str = Field(..., pattern="^(RAJDHANI|SHATABDI|VANDE_BHARAT|SUPERFAST|EXPRESS|INTERCITY|SUBURBAN)$")
    operating_days: str = "MON,TUE,WED,THU,FRI,SAT,SUN"
    is_active: bool = True


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    service_name: Optional[str] = None
    service_type: Optional[str] = None
    operating_days: Optional[str] = None
    is_active: Optional[bool] = None


class ServiceResponse(ServiceBase):
    service_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
