# TransitMatrix - Machine Learning Demand Forecasting Module
# Preprocessing: pandas, NumPy.
# Model: scikit-learn RandomForestRegressor vs. Historical Average baseline.
# Evaluation: MAE, RMSE with chronological train/test split.
# Raw SQL data extraction without ORM.

import os
import json
import numpy as np
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, Tuple, Optional
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib

from app.core.config import settings
from app.db.connection import get_db_connection
from app.repositories.prediction_repository import PredictionRepository

MODEL_DIR = settings.ML_MODELS_DIR
MODEL_FILE = os.path.join(MODEL_DIR, f"demand_model_{settings.ML_MODEL_VERSION}.joblib")


class DemandForecaster:

    @staticmethod
    def extract_training_data() -> pd.DataFrame:
        """
        Extracts historical trip and booking data directly via raw SQL without ORM.
        """
        with get_db_connection() as conn:
            raw_data = PredictionRepository.get_historical_features(conn)

        if not raw_data:
            # Return empty dataframe with expected columns
            return pd.DataFrame(columns=[
                "route_id", "route_code", "total_distance_km", "duration_est_minutes",
                "trip_date", "day_of_week", "month_of_year", "avg_base_fare",
                "trips_count", "actual_passenger_demand"
            ])

        df = pd.DataFrame(raw_data)
        df["trip_date"] = pd.to_datetime(df["trip_date"])
        df["total_distance_km"] = df["total_distance_km"].astype(float)
        df["duration_est_minutes"] = df["duration_est_minutes"].astype(int)
        df["avg_base_fare"] = df["avg_base_fare"].astype(float)
        df["actual_passenger_demand"] = df["actual_passenger_demand"].astype(int)
        return df

    @staticmethod
    def train_and_evaluate() -> Dict[str, Any]:
        """
        Trains RandomForestRegressor alongside historical-average baseline.
        Uses chronological train/test split to prevent temporal data leakage.
        """
        df = DemandForecaster.extract_training_data()

        if len(df) < 5:
            # Fallback for minimal bootstrap data
            return {
                "status": "insufficient_data",
                "message": f"Need at least 5 historical data points, currently have {len(df)}",
                "samples_count": len(df)
            }

        # Chronological sort
        df = df.sort_values(by="trip_date").reset_index(drop=True)

        feature_cols = [
            "route_id", "total_distance_km", "duration_est_minutes",
            "day_of_week", "month_of_year", "avg_base_fare"
        ]
        target_col = "actual_passenger_demand"

        X = df[feature_cols]
        y = df[target_col]

        # Chronological 80/20 train/test split
        split_idx = int(len(df) * 0.8)
        if split_idx == 0:
            split_idx = 1

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # 1. Historical-Average Baseline Model
        # Predicts mean demand observed per route in the training split
        route_means = df.iloc[:split_idx].groupby("route_id")[target_col].mean().to_dict()
        overall_mean = float(y_train.mean()) if len(y_train) > 0 else 0.0

        if len(X_test) > 0:
            y_pred_baseline = X_test["route_id"].map(lambda rid: route_means.get(rid, overall_mean)).values
            baseline_mae = float(mean_absolute_error(y_test, y_pred_baseline))
            baseline_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_baseline)))
        else:
            baseline_mae = 0.0
            baseline_rmse = 0.0

        # 2. Random Forest Regressor Model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=6,
            random_state=42
        )
        model.fit(X_train, y_train)

        if len(X_test) > 0:
            y_pred_rf = model.predict(X_test)
            rf_mae = float(mean_absolute_error(y_test, y_pred_rf))
            rf_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_rf)))
        else:
            rf_mae = 0.0
            rf_rmse = 0.0

        # Save trained artifact and metadata
        os.makedirs(MODEL_DIR, exist_ok=True)
        artifact = {
            "model": model,
            "feature_cols": feature_cols,
            "route_means": route_means,
            "overall_mean": overall_mean,
            "version": settings.ML_MODEL_VERSION,
            "trained_at": datetime.now().isoformat(),
            "metrics": {
                "baseline_mae": round(baseline_mae, 2),
                "baseline_rmse": round(baseline_rmse, 2),
                "rf_mae": round(rf_mae, 2),
                "rf_rmse": round(rf_rmse, 2),
                "train_samples": len(X_train),
                "test_samples": len(X_test)
            }
        }
        joblib.dump(artifact, MODEL_FILE)

        return {
            "status": "success",
            "model_version": settings.ML_MODEL_VERSION,
            "artifact_path": MODEL_FILE,
            "metrics": artifact["metrics"]
        }

    @staticmethod
    def predict_and_persist(route_id: int, target_date: date) -> Dict[str, Any]:
        """
        Loads saved model, generates demand prediction with confidence intervals,
        and persists the record into the MySQL demand_predictions table.
        """
        # Load route properties via raw SQL
        with get_db_connection() as conn:
            from app.repositories.route_repository import RouteRepository
            route = RouteRepository.get_by_id(conn, route_id)

        if not route:
            raise ValueError(f"Route with ID {route_id} does not exist.")

        day_of_week = target_date.isoweekday()  # 1 (Monday) to 7 (Sunday)
        month_of_year = target_date.month

        # Check if saved model exists
        if os.path.exists(MODEL_FILE):
            artifact = joblib.load(MODEL_FILE)
            model = artifact["model"]
            feature_cols = artifact["feature_cols"]

            # Assume typical fare ~ 2.0 per km
            est_fare = float(route["total_distance_km"]) * 2.0
            row_dict = {
                "route_id": route_id,
                "total_distance_km": float(route["total_distance_km"]),
                "duration_est_minutes": int(route["duration_est_minutes"]),
                "day_of_week": day_of_week,
                "month_of_year": month_of_year,
                "avg_base_fare": est_fare
            }
            X_input = pd.DataFrame([row_dict])[feature_cols]

            predicted_val = float(model.predict(X_input)[0])
            predicted_demand = max(10, int(round(predicted_val)))
        else:
            # Fallback estimation based on distance and route capacity
            predicted_demand = max(50, int(float(route["total_distance_km"]) * 0.4))

        # Confidence interval (+/- 15% standard error)
        margin = max(5, int(predicted_demand * 0.15))
        conf_low = max(0, predicted_demand - margin)
        conf_high = predicted_demand + margin

        features_meta = {
            "route_code": route["route_code"],
            "distance_km": float(route["total_distance_km"]),
            "day_of_week": day_of_week,
            "month_of_year": month_of_year
        }

        # Persist prediction to MySQL using raw SQL
        with get_db_connection() as conn:
            pred_id = PredictionRepository.save_prediction(
                connection=conn,
                route_id=route_id,
                prediction_date=target_date,
                predicted_demand=predicted_demand,
                confidence_interval_low=conf_low,
                confidence_interval_high=conf_high,
                model_version=settings.ML_MODEL_VERSION,
                features_json=features_meta
            )
            conn.commit()

            records = PredictionRepository.get_predictions(conn, route_id=route_id, limit=1)
            return records[0]
