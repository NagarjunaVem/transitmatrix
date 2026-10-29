# TransitMatrix - Demand Prediction Pydantic Schemas
# Request validation and response serialization for AI/ML forecasting pipeline.

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import date, datetime


class PredictionCreateRequest(BaseModel):
    route_id: int
    prediction_date: date
    predicted_demand: int = Field(..., ge=0, description="Predicted passenger count")
    confidence_interval_low: Optional[int] = Field(None, ge=0, description="Lower bound of 90% confidence interval")
    confidence_interval_high: Optional[int] = Field(None, ge=0, description="Upper bound of 90% confidence interval")
    model_version: str = Field("v1.0", description="Model version tag")
    features_json: Optional[Dict[str, Any]] = Field(None, description="Input features and metadata JSON")


class PredictionResponse(BaseModel):
    prediction_id: int
    route_id: int
    route_code: Optional[str] = None
    route_name: Optional[str] = None
    prediction_date: date
    predicted_demand: int
    confidence_interval_low: Optional[int] = None
    confidence_interval_high: Optional[int] = None
    model_name: Optional[str] = "RandomForestRegressor"
    model_version: str
    features_json: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ForecastQueryRequest(BaseModel):
    route_id: int = Field(..., description="Route ID to forecast")
    target_date: date = Field(..., description="Target travel date for forecasting")
    departure_hour: Optional[int] = Field(None, ge=0, le=23, description="Optional specific departure hour")


class ModelEvaluationMetrics(BaseModel):
    baseline_mae: float
    baseline_rmse: float
    baseline_r2: Optional[float] = None
    rf_mae: float
    rf_rmse: float
    rf_r2: Optional[float] = None
    mae_improvement_pct: Optional[float] = None
    rmse_improvement_pct: Optional[float] = None
    train_samples: int
    test_samples: int


class ModelMetricsResponse(BaseModel):
    status: str
    model_name: str
    model_version: str
    trained_at: Optional[str] = None
    artifact_path: Optional[str] = None
    metrics: ModelEvaluationMetrics
    feature_importance: Optional[Dict[str, float]] = None


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    is_trained: bool
    trained_at: Optional[str] = None
    artifact_path: str
    features: List[str]
    description: str
