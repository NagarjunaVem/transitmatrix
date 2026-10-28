# TransitMatrix - Demand Prediction Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import date, datetime


class PredictionCreateRequest(BaseModel):
    route_id: int
    prediction_date: date
    predicted_demand: int = Field(..., ge=0)
    confidence_interval_low: Optional[int] = Field(None, ge=0)
    confidence_interval_high: Optional[int] = Field(None, ge=0)
    model_version: str = "v1.0"
    features_json: Optional[Dict[str, Any]] = None


class PredictionResponse(BaseModel):
    prediction_id: int
    route_id: int
    route_code: Optional[str] = None
    route_name: Optional[str] = None
    prediction_date: date
    predicted_demand: int
    confidence_interval_low: Optional[int] = None
    confidence_interval_high: Optional[int] = None
    model_version: str
    features_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
