# TransitMatrix - Machine Learning Demand Prediction Endpoints

from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.schemas.prediction import PredictionCreateRequest, PredictionResponse
from app.db.connection import get_db_connection
from app.repositories.prediction_repository import PredictionRepository
from app.api.deps import require_roles

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.get("", response_model=List[PredictionResponse])
def get_predictions(
    route_id: Optional[int] = None,
    limit: int = Query(50, ge=1, le=200)
):
    """
    List persisted passenger demand predictions.
    """
    with get_db_connection() as conn:
        return PredictionRepository.get_predictions(conn, route_id, limit)


@router.post("", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def create_prediction(
    request: PredictionCreateRequest,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Persist a machine learning demand forecast into the MySQL database.
    """
    with get_db_connection() as conn:
        pred_id = PredictionRepository.save_prediction(
            connection=conn,
            route_id=request.route_id,
            prediction_date=request.prediction_date,
            predicted_demand=request.predicted_demand,
            confidence_interval_low=request.confidence_interval_low,
            confidence_interval_high=request.confidence_interval_high,
            model_version=request.model_version,
            features_json=request.features_json
        )
        conn.commit()
        preds = PredictionRepository.get_predictions(conn, route_id=request.route_id, limit=1)
        return preds[0]


@router.get("/features")
def get_training_features(current_user=Depends(require_roles("ADMIN", "STAFF"))):
    """
    Extracts raw SQL historical features for ML training (Person 4 coordination).
    """
    with get_db_connection() as conn:
        return PredictionRepository.get_historical_features(conn)
