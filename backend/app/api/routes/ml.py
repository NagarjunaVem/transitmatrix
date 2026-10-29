# TransitMatrix - Machine Learning Forecast & Model Evaluation Endpoints
# Exposes REST API endpoints for model metrics, available models, and real-time inference.
# Architecture: FastAPI Route -> MLService -> DemandForecaster / PredictionRepository -> MySQL

from fastapi import APIRouter, Depends, Query, status, HTTPException
from typing import List, Optional, Dict, Any
from datetime import date
from app.schemas.prediction import (
    PredictionResponse,
    ModelMetricsResponse,
    ModelInfoResponse,
)
from app.services.ml_service import MLService
from app.api.deps import require_roles

router = APIRouter(prefix="/ml", tags=["Machine Learning"])


@router.get("/metrics", response_model=ModelMetricsResponse)
def get_model_metrics():
    """
    Returns the evaluation metrics of the currently saved model compared against the baseline.
    Metrics include MAE, RMSE, R² scores, and feature importance rankings.
    """
    try:
        return MLService.get_metrics()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve model metrics: {str(e)}"
        )


@router.get("/models", response_model=List[ModelInfoResponse])
def get_available_models():
    """
    Returns metadata regarding registered ML models, status, version, and feature definitions.
    """
    return MLService.get_model_info()


@router.get("/forecast", response_model=PredictionResponse)
def forecast_demand(
    route_id: int = Query(..., ge=1, description="Route ID to forecast"),
    target_date: date = Query(..., description="Target travel date in YYYY-MM-DD"),
    departure_hour: Optional[int] = Query(8, ge=0, le=23, description="Scheduled departure hour (0-23)"),
    persist: bool = Query(True, description="Whether to persist the prediction into MySQL")
):
    """
    Generates passenger demand forecast for a given corridor and date.
    Calculates 90% confidence bounds and persists to MySQL via raw SQL.
    """
    try:
        return MLService.forecast(
            route_id=route_id,
            target_date=target_date,
            departure_hour=departure_hour,
            persist=persist
        )
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(ve))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forecast generation failed: {str(e)}"
        )


@router.post("/train", response_model=ModelMetricsResponse)
def train_model(
    current_user: Dict[str, Any] = Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Triggers chronological model training (Random Forest vs Historical Average baseline)
    and returns MAE/RMSE evaluation metrics. Restricted to ADMIN and STAFF.
    """
    try:
        return MLService.train()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Model training failed: {str(e)}"
        )


@router.get("/features")
def get_training_features(
    current_user: Dict[str, Any] = Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Extracts raw SQL historical features for ML training and data analysis.
    """
    return MLService.extract_features()
