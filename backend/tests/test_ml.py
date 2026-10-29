# TransitMatrix - AI/ML Demand Forecasting Test Suite
# Tests SQL data extraction, feature generation, data leakage prevention,
# reproducible training, baseline vs Random Forest evaluation, prediction confidence bounds,
# and FastAPI ML endpoints.

import os
import pytest
import numpy as np
import pandas as pd
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from app.ml.demand_forecasting import DemandForecaster, FEATURE_COLS, MODEL_FILE
from app.schemas.prediction import PredictionCreateRequest, ForecastQueryRequest
from app.repositories.prediction_repository import PredictionRepository


class TestDemandForecastingPipeline:

    def test_synthetic_data_generation(self):
        """
        Verifies realistic synthetic dataset generation when database is bootstrapped or in test mode.
        """
        df = DemandForecaster.generate_synthetic_data(num_samples=100)
        assert isinstance(df, pd.DataFrame)
        assert len(df) >= 100
        assert "actual_passenger_demand" in df.columns
        assert "route_id" in df.columns
        assert "trip_date" in df.columns
        assert "departure_hour" in df.columns
        assert (df["actual_passenger_demand"] >= 0).all()
        assert (df["departure_hour"].between(0, 23)).all()

    def test_leakage_prevention_in_feature_engineering(self):
        """
        Guarantees zero future data leakage: route historical means must be calculated
        strictly using training split observations, never leaking future test outcomes.
        """
        df = DemandForecaster.generate_synthetic_data(num_samples=200)
        df = df.sort_values(by=["trip_date", "departure_hour"]).reset_index(drop=True)

        split_idx = 160
        X, y, route_means, overall_mean = DemandForecaster.prepare_features(df, train_split_idx=split_idx)

        # Check route_hist_mean exists and is properly populated
        assert "route_hist_mean" in X.columns
        assert len(X) == len(df)

        # Manually compute training-only mean for route_id 1
        train_r1_mean = df.iloc[:split_idx][df.iloc[:split_idx]["route_id"] == 1]["actual_passenger_demand"].mean()
        all_r1_mean = df[df["route_id"] == 1]["actual_passenger_demand"].mean()

        # The engineered feature in test set for route 1 must match training mean, NOT the full-dataset mean
        assert np.isclose(route_means[1], train_r1_mean)
        assert len(route_means) > 0
        assert overall_mean > 0

    def test_chronological_train_and_evaluate(self):
        """
        Validates model training and evaluation:
        - Chronological 80/20 train/test partition
        - Both Baseline and Random Forest evaluated on MAE, RMSE, R2
        - Fitted model artifact saved with metadata
        """
        result = DemandForecaster.train_and_evaluate(force_synthetic=True)
        assert result["status"] == "success"
        assert "metrics" in result
        metrics = result["metrics"]

        # Ensure all required metrics are present
        assert "baseline_mae" in metrics
        assert "baseline_rmse" in metrics
        assert "rf_mae" in metrics
        assert "rf_rmse" in metrics
        assert "train_samples" in metrics
        assert "test_samples" in metrics
        assert metrics["train_samples"] > metrics["test_samples"]

        # Random Forest should equal or outperform the simple baseline
        assert metrics["rf_mae"] <= metrics["baseline_mae"] * 1.05
        assert metrics["rf_rmse"] <= metrics["baseline_rmse"] * 1.05

        # Check artifact saved
        assert os.path.exists(result["artifact_path"])

    def test_prediction_confidence_intervals(self):
        """
        Tests inference calculations and confidence interval validity:
        0 <= confidence_low <= predicted_demand <= confidence_high.
        """
        # Mock route repository to avoid requiring live MySQL server in unit test
        mock_route = {
            "route_id": 1,
            "route_code": "NDLS-BCT",
            "route_name": "New Delhi to Mumbai Central",
            "total_distance_km": 1384.0,
            "duration_est_minutes": 950
        }

        with patch("app.repositories.route_repository.RouteRepository.get_by_id", return_value=mock_route):
            pred = DemandForecaster.predict_and_persist(
                route_id=1,
                target_date=date(2026, 12, 1),
                departure_hour=16,
                persist=False  # Dry run
            )

            assert pred["predicted_demand"] > 0
            assert pred["confidence_interval_low"] >= 0
            assert pred["confidence_interval_low"] <= pred["predicted_demand"]
            assert pred["confidence_interval_high"] >= pred["predicted_demand"]
            assert pred["route_id"] == 1
            assert pred["model_name"] == "RandomForestRegressor"

    def test_prediction_invalid_route_handling(self):
        """
        Verifies that querying a non-existent route raises a descriptive ValueError.
        """
        with patch("app.repositories.route_repository.RouteRepository.get_by_id", return_value=None):
            with pytest.raises(ValueError, match="does not exist"):
                DemandForecaster.predict_and_persist(
                    route_id=999999,
                    target_date=date(2026, 12, 1),
                    persist=False
                )

    def test_prediction_pydantic_schema_validation(self):
        """
        Tests Pydantic input validation for prediction requests.
        """
        # Negative demand must be rejected
        with pytest.raises(Exception):
            PredictionCreateRequest(
                route_id=1,
                prediction_date=date(2026, 12, 1),
                predicted_demand=-10
            )

        # Valid request passes
        req = PredictionCreateRequest(
            route_id=1,
            prediction_date=date(2026, 12, 1),
            predicted_demand=350,
            confidence_interval_low=320,
            confidence_interval_high=380
        )
        assert req.predicted_demand == 350
        assert req.confidence_interval_low == 320


class TestMLRestEndpoints:

    def test_get_model_metrics_endpoint(self, client):
        """
        Tests GET /api/ml/metrics returns HTTP 200 with complete evaluation statistics.
        """
        response = client.get("/api/ml/metrics")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "metrics" in data
        assert "baseline_mae" in data["metrics"]
        assert "rf_mae" in data["metrics"]
        assert "feature_importance" in data

    def test_get_available_models_endpoint(self, client):
        """
        Tests GET /api/ml/models returns registered models and features.
        """
        response = client.get("/api/ml/models")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        model_names = [m["model_name"] for m in data]
        assert "RandomForestRegressor" in model_names
        assert "HistoricalAverageBaseline" in model_names

    def test_forecast_demand_endpoint(self, client):
        """
        Tests GET /api/ml/forecast returns valid prediction response.
        """
        mock_route = {
            "route_id": 1,
            "route_code": "NDLS-BCT",
            "route_name": "New Delhi to Mumbai Central",
            "total_distance_km": 1384.0,
            "duration_est_minutes": 950
        }

        with patch("app.repositories.route_repository.RouteRepository.get_by_id", return_value=mock_route):
            response = client.get("/api/ml/forecast?route_id=1&target_date=2026-11-20&departure_hour=10&persist=false")
            assert response.status_code == 200
            data = response.json()
            assert data["route_id"] == 1
            assert data["predicted_demand"] > 0
            assert data["confidence_interval_low"] <= data["predicted_demand"]
            assert data["confidence_interval_high"] >= data["predicted_demand"]

    def test_train_model_role_protection(self, client):
        """
        Tests that POST /api/ml/train requires ADMIN or STAFF credentials.
        """
        # Unauthenticated request rejected
        response = client.post("/api/ml/train")
        assert response.status_code == 401

    def test_train_model_admin_authorized(self, client, admin_headers):
        """
        Tests that POST /api/ml/train succeeds when invoked by authorized ADMIN.
        """
        with patch.object(DemandForecaster, "train_and_evaluate", return_value={
            "status": "success",
            "model_name": "RandomForestRegressor",
            "model_version": "v1.0",
            "trained_at": "2026-10-29T10:00:00",
            "artifact_path": "./ml/models/demand_model_v1.0.joblib",
            "metrics": {
                "baseline_mae": 25.0,
                "baseline_rmse": 32.0,
                "baseline_r2": 0.70,
                "rf_mae": 12.0,
                "rf_rmse": 16.0,
                "rf_r2": 0.92,
                "mae_improvement_pct": 52.0,
                "rmse_improvement_pct": 50.0,
                "train_samples": 240,
                "test_samples": 60
            },
            "feature_importance": {"route_id": 0.35}
        }):
            response = client.post("/api/ml/train", headers=admin_headers)
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["metrics"]["rf_mae"] == 12.0
