# TransitMatrix - Machine Learning Service Layer
# Coordinates demand forecasting business logic, model evaluation, and repository persistence.
# Architecture: FastAPI Route -> Service -> Repository / ML Engine -> mysql.connector -> MySQL

from typing import Dict, Any, List, Optional
from datetime import date
from app.ml.demand_forecasting import DemandForecaster
from app.db.connection import get_db_connection
from app.repositories.prediction_repository import PredictionRepository


class MLService:

    @staticmethod
    def get_metrics() -> Dict[str, Any]:
        """
        Retrieves evaluation metrics for the active ML model compared against the baseline.
        """
        return DemandForecaster.get_model_metrics()

    @staticmethod
    def get_model_info() -> List[Dict[str, Any]]:
        """
        Enumerates registered machine learning models and version metadata.
        """
        return DemandForecaster.get_model_info()

    @staticmethod
    def forecast(
        route_id: int,
        target_date: date,
        departure_hour: Optional[int] = 8,
        persist: bool = True
    ) -> Dict[str, Any]:
        """
        Generates passenger demand inference with confidence bounds and optional MySQL persistence.
        """
        return DemandForecaster.predict_and_persist(
            route_id=route_id,
            target_date=target_date,
            departure_hour=departure_hour,
            persist=persist
        )

    @staticmethod
    def train() -> Dict[str, Any]:
        """
        Triggers chronological model training and evaluation against baseline.
        """
        return DemandForecaster.train_and_evaluate()

    @staticmethod
    def extract_features() -> List[Dict[str, Any]]:
        """
        Extracts raw SQL historical features without ORM.
        """
        with get_db_connection() as conn:
            return PredictionRepository.get_historical_features(conn)
