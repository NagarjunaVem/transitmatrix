# TransitMatrix - Machine Learning Demand Forecasting Module
# Preprocessing: pandas, NumPy.
# Modeling: scikit-learn RandomForestRegressor vs. Historical Average baseline.
# Evaluation: MAE, RMSE, R² with chronological train/test split.
# Raw SQL data extraction without ORM.

import os
import json
import logging
import numpy as np
import pandas as pd
from datetime import date, datetime
from typing import Dict, Any, Tuple, Optional, List
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib

from app.core.config import settings

logger = logging.getLogger("transitmatrix.ml")

MODEL_DIR = settings.ML_MODELS_DIR
MODEL_FILE = os.path.join(MODEL_DIR, f"demand_model_{settings.ML_MODEL_VERSION}.joblib")
METRICS_FILE = os.path.join(MODEL_DIR, f"metrics_{settings.ML_MODEL_VERSION}.json")

# Enriched feature set with temporal peak-hour indicators and seasonality
FEATURE_COLS = [
    "route_id",
    "total_distance_km",
    "duration_est_minutes",
    "departure_hour",
    "is_peak_hour",
    "day_of_week",
    "day_of_month",
    "month_of_year",
    "quarter_of_year",
    "is_weekend",
    "avg_base_fare",
    "cancellations_count",
    "route_hist_mean",
]

DEFAULT_ROUTES = {
    1: {"route_id": 1, "route_code": "NDLS-BCT", "route_name": "New Delhi to Mumbai Central", "total_distance_km": 1384.0, "duration_est_minutes": 950},
    2: {"route_id": 2, "route_code": "BCT-NDLS", "route_name": "Mumbai Central to New Delhi", "total_distance_km": 1384.0, "duration_est_minutes": 950},
    3: {"route_id": 3, "route_code": "NDLS-HWH", "route_name": "New Delhi to Howrah", "total_distance_km": 1447.0, "duration_est_minutes": 1020},
    4: {"route_id": 4, "route_code": "HWH-NDLS", "route_name": "Howrah to New Delhi", "total_distance_km": 1447.0, "duration_est_minutes": 1020},
    5: {"route_id": 5, "route_code": "NDLS-MAS", "route_name": "New Delhi to Chennai Central", "total_distance_km": 2180.0, "duration_est_minutes": 1710},
    6: {"route_id": 6, "route_code": "MAS-NDLS", "route_name": "Chennai Central to New Delhi", "total_distance_km": 2180.0, "duration_est_minutes": 1710},
    7: {"route_id": 7, "route_code": "BCT-ADI", "route_name": "Mumbai Central to Ahmedabad", "total_distance_km": 492.0, "duration_est_minutes": 380},
    8: {"route_id": 8, "route_code": "ADI-BCT", "route_name": "Ahmedabad to Mumbai Central", "total_distance_km": 492.0, "duration_est_minutes": 380},
    9: {"route_id": 9, "route_code": "SBC-MAS", "route_name": "Bangalore to Chennai", "total_distance_km": 358.0, "duration_est_minutes": 260},
    10: {"route_id": 10, "route_code": "MAS-SBC", "route_name": "Chennai to Bangalore", "total_distance_km": 358.0, "duration_est_minutes": 260},
    11: {"route_id": 11, "route_code": "CSMT-PUNE", "route_name": "Mumbai CSMT to Pune", "total_distance_km": 192.0, "duration_est_minutes": 195},
    12: {"route_id": 12, "route_code": "PUNE-CSMT", "route_name": "Pune to Mumbai CSMT", "total_distance_km": 192.0, "duration_est_minutes": 195},
    13: {"route_id": 13, "route_code": "NDLS-CDG", "route_name": "New Delhi to Chandigarh", "total_distance_km": 244.0, "duration_est_minutes": 200},
    14: {"route_id": 14, "route_code": "CDG-NDLS", "route_name": "Chandigarh to New Delhi", "total_distance_km": 244.0, "duration_est_minutes": 200},
    15: {"route_id": 15, "route_code": "HYB-BZA", "route_name": "Hyderabad to Vijayawada", "total_distance_km": 313.0, "duration_est_minutes": 270},
    16: {"route_id": 16, "route_code": "BZA-HYB", "route_name": "Vijayawada to Hyderabad", "total_distance_km": 313.0, "duration_est_minutes": 270},
    17: {"route_id": 17, "route_code": "NDLS-BSB", "route_name": "New Delhi to Varanasi", "total_distance_km": 765.0, "duration_est_minutes": 480},
    18: {"route_id": 18, "route_code": "BSB-NDLS", "route_name": "Varanasi to New Delhi", "total_distance_km": 765.0, "duration_est_minutes": 480},
}


def compute_peak_hour_flag(hour: int) -> int:
    """Returns 1 for rush hours (07:00-10:00 & 16:00-20:00), 0 otherwise."""
    return 1 if (7 <= hour <= 10 or 16 <= hour <= 20) else 0


class DemandForecaster:

    @staticmethod
    def extract_training_data() -> pd.DataFrame:
        """
        Extracts historical trip and booking demand data directly via raw SQL without ORM.
        """
        raw_data = []
        try:
            from app.db.connection import get_db_connection
            from app.repositories.prediction_repository import PredictionRepository
            with get_db_connection() as conn:
                raw_data = PredictionRepository.get_historical_features(conn)
        except Exception as e:
            logger.warning(f"Database feature extraction unavailable or DB offline: {e}")

        if not raw_data:
            return pd.DataFrame(columns=[
                "route_id", "route_code", "total_distance_km", "duration_est_minutes",
                "trip_id", "service_id", "service_number", "service_type",
                "trip_date", "departure_hour", "is_peak_hour", "day_of_week",
                "day_of_month", "month_of_year", "quarter_of_year",
                "is_weekend", "avg_base_fare", "trips_count", "booking_count",
                "cancellations_count", "actual_passenger_demand"
            ])

        df = pd.DataFrame(raw_data)
        df["trip_date"] = pd.to_datetime(df["trip_date"])
        df["total_distance_km"] = df["total_distance_km"].astype(float)
        df["duration_est_minutes"] = df["duration_est_minutes"].astype(int)
        df["departure_hour"] = df["departure_hour"].fillna(8).astype(int)
        df["is_peak_hour"] = df["departure_hour"].map(compute_peak_hour_flag).astype(int)
        df["day_of_week"] = df["day_of_week"].astype(int)
        df["day_of_month"] = df["trip_date"].dt.day.astype(int)
        df["month_of_year"] = df["month_of_year"].astype(int)
        df["quarter_of_year"] = df["trip_date"].dt.quarter.astype(int)
        df["is_weekend"] = df["is_weekend"].astype(int)
        df["avg_base_fare"] = df["avg_base_fare"].astype(float)
        df["cancellations_count"] = df["cancellations_count"].fillna(0).astype(int)
        df["actual_passenger_demand"] = df["actual_passenger_demand"].astype(int)
        return df

    @staticmethod
    def generate_synthetic_data(num_samples: int = 300) -> pd.DataFrame:
        """
        Generates realistic synthetic historical transit demand dataset when database has minimal seed.
        Clearly labeled as simulated data.
        """
        np.random.seed(42)
        base_date = pd.Timestamp("2026-06-01")
        records = []

        routes = [
            {"route_id": 1, "route_code": "NDLS-BCT", "dist": 1384.0, "dur": 950, "base_fare": 2400.0, "base_demand": 380},
            {"route_id": 2, "route_code": "BCT-NDLS", "dist": 1384.0, "dur": 950, "base_fare": 2400.0, "base_demand": 375},
            {"route_id": 3, "route_code": "NDLS-HWH", "dist": 1447.0, "dur": 1020, "base_fare": 2550.0, "base_demand": 390},
            {"route_id": 4, "route_code": "HWH-NDLS", "dist": 1447.0, "dur": 1020, "base_fare": 2550.0, "base_demand": 385},
            {"route_id": 5, "route_code": "NDLS-MAS", "dist": 2180.0, "dur": 1710, "base_fare": 3100.0, "base_demand": 340},
            {"route_id": 6, "route_code": "MAS-NDLS", "dist": 2180.0, "dur": 1710, "base_fare": 3100.0, "base_demand": 335},
            {"route_id": 7, "route_code": "BCT-ADI", "dist": 492.0, "dur": 380, "base_fare": 1250.0, "base_demand": 410},
            {"route_id": 8, "route_code": "ADI-BCT", "dist": 492.0, "dur": 380, "base_fare": 1250.0, "base_demand": 405},
            {"route_id": 9, "route_code": "SBC-MAS", "dist": 358.0, "dur": 260, "base_fare": 980.0, "base_demand": 430},
            {"route_id": 10, "route_code": "MAS-SBC", "dist": 358.0, "dur": 260, "base_fare": 980.0, "base_demand": 425},
            {"route_id": 11, "route_code": "CSMT-PUNE", "dist": 192.0, "dur": 195, "base_fare": 650.0, "base_demand": 450},
            {"route_id": 12, "route_code": "PUNE-CSMT", "dist": 192.0, "dur": 195, "base_fare": 650.0, "base_demand": 445},
            {"route_id": 13, "route_code": "NDLS-CDG", "dist": 244.0, "dur": 200, "base_fare": 750.0, "base_demand": 420},
            {"route_id": 14, "route_code": "CDG-NDLS", "dist": 244.0, "dur": 200, "base_fare": 750.0, "base_demand": 415},
            {"route_id": 15, "route_code": "HYB-BZA", "dist": 313.0, "dur": 270, "base_fare": 820.0, "base_demand": 360},
            {"route_id": 16, "route_code": "BZA-HYB", "dist": 313.0, "dur": 270, "base_fare": 820.0, "base_demand": 355},
            {"route_id": 17, "route_code": "NDLS-BSB", "dist": 765.0, "dur": 480, "base_fare": 1650.0, "base_demand": 395},
            {"route_id": 18, "route_code": "BSB-NDLS", "dist": 765.0, "dur": 480, "base_fare": 1650.0, "base_demand": 390},
        ]

        for day in range(num_samples // len(routes) + 5):
            cur_date = base_date + pd.Timedelta(days=day)
            day_of_week = cur_date.isoweekday()
            day_of_month = cur_date.day
            month = cur_date.month
            quarter = cur_date.quarter
            is_weekend = 1 if day_of_week in [6, 7] else 0
            weekend_mult = 1.15 if is_weekend else 1.0

            for r in routes:
                hour = int(np.random.choice([6, 8, 12, 16, 20]))
                is_peak = compute_peak_hour_flag(hour)
                peak_mult = 1.25 if is_peak else 0.95
                noise = np.random.normal(0, 15)

                demand = int(max(20, round(r["base_demand"] * weekend_mult * peak_mult + noise)))
                cancels = int(max(0, np.random.poisson(demand * 0.04)))

                records.append({
                    "route_id": r["route_id"],
                    "route_code": r["route_code"],
                    "total_distance_km": r["dist"],
                    "duration_est_minutes": r["dur"],
                    "trip_id": len(records) + 1,
                    "service_id": (r["route_id"] % 22) + 1,
                    "service_number": f"TMX-{r['route_id']:02d}",
                    "service_type": "EXPRESS",
                    "trip_date": cur_date,
                    "departure_hour": hour,
                    "is_peak_hour": is_peak,
                    "day_of_week": day_of_week,
                    "day_of_month": day_of_month,
                    "month_of_year": month,
                    "quarter_of_year": quarter,
                    "is_weekend": is_weekend,
                    "avg_base_fare": r["base_fare"],
                    "trips_count": 1,
                    "booking_count": demand + cancels,
                    "cancellations_count": cancels,
                    "actual_passenger_demand": demand,
                    "is_simulated": True
                })

        df = pd.DataFrame(records).sort_values(by=["trip_date", "departure_hour"]).reset_index(drop=True)
        return df

    @staticmethod
    def prepare_features(df: pd.DataFrame, train_split_idx: Optional[int] = None) -> Tuple[pd.DataFrame, pd.Series, Dict[int, float], float]:
        """
        Engineers features while strictly preventing future data leakage.
        Calculates route historical mean strictly from the training split.
        """
        df = df.copy()

        if train_split_idx is None:
            train_split_idx = int(len(df) * 0.8)

        train_df = df.iloc[:train_split_idx]
        route_means = train_df.groupby("route_id")["actual_passenger_demand"].mean().to_dict()
        overall_mean = float(train_df["actual_passenger_demand"].mean()) if len(train_df) > 0 else 50.0

        df["route_hist_mean"] = df["route_id"].map(lambda rid: route_means.get(rid, overall_mean)).astype(float)

        X = df[FEATURE_COLS]
        y = df["actual_passenger_demand"]

        return X, y, route_means, overall_mean

    @staticmethod
    def train_and_evaluate(force_synthetic: bool = False) -> Dict[str, Any]:
        """
        Trains RandomForestRegressor alongside historical-average baseline.
        Uses strictly chronological train/test split (no random split) to prevent temporal data leakage.
        Evaluates MAE, RMSE, and R² scores.
        """
        if force_synthetic:
            df = DemandForecaster.generate_synthetic_data(400)
            provenance = "synthetic_simulation"
        else:
            df = DemandForecaster.extract_training_data()
            if len(df) < 15 or (len(df) > 0 and (df["actual_passenger_demand"].std() < 5.0 or df["actual_passenger_demand"].max() < 15)):
                logger.info("Database contains uniform toy seed records; using realistic transit volume simulation dataset.")
                df = DemandForecaster.generate_synthetic_data(400)
                provenance = "synthetic_simulation"
            else:
                provenance = "mysql_live_data"

        df = df.sort_values(by=["trip_date", "departure_hour"]).reset_index(drop=True)

        split_idx = int(len(df) * 0.80)
        if split_idx == 0:
            split_idx = 1

        X, y, route_means, overall_mean = DemandForecaster.prepare_features(df, train_split_idx=split_idx)

        X_train, X_test = X.iloc[:split_idx], X.iloc[split_idx:]
        y_train, y_test = y.iloc[:split_idx], y.iloc[split_idx:]

        # 1. Historical-Average Baseline Model
        y_pred_baseline = X_test["route_hist_mean"].values
        baseline_mae = float(mean_absolute_error(y_test, y_pred_baseline))
        baseline_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_baseline)))
        try:
            baseline_r2 = float(r2_score(y_test, y_pred_baseline))
        except Exception:
            baseline_r2 = 0.0

        # 2. Random Forest Regressor Model
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            min_samples_split=3,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train, y_train)

        y_pred_rf = model.predict(X_test)
        rf_mae = float(mean_absolute_error(y_test, y_pred_rf))
        rf_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred_rf)))
        try:
            rf_r2 = float(r2_score(y_test, y_pred_rf))
        except Exception:
            rf_r2 = 0.0

        importances = {col: round(float(imp), 4) for col, imp in zip(FEATURE_COLS, model.feature_importances_)}
        importances = dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))

        mae_improvement = round(((baseline_mae - rf_mae) / baseline_mae) * 100, 2) if baseline_mae > 0 else 0.0
        rmse_improvement = round(((baseline_rmse - rf_rmse) / baseline_rmse) * 100, 2) if baseline_rmse > 0 else 0.0

        os.makedirs(MODEL_DIR, exist_ok=True)
        trained_at_iso = datetime.now().isoformat()

        artifact = {
            "model": model,
            "feature_cols": FEATURE_COLS,
            "route_means": route_means,
            "overall_mean": overall_mean,
            "version": settings.ML_MODEL_VERSION,
            "model_name": "RandomForestRegressor",
            "trained_at": trained_at_iso,
            "provenance": provenance,
            "metrics": {
                "baseline_mae": round(baseline_mae, 2),
                "baseline_rmse": round(baseline_rmse, 2),
                "baseline_r2": round(baseline_r2, 4),
                "rf_mae": round(rf_mae, 2),
                "rf_rmse": round(rf_rmse, 2),
                "rf_r2": round(rf_r2, 4),
                "mae_improvement_pct": mae_improvement,
                "rmse_improvement_pct": rmse_improvement,
                "train_samples": len(X_train),
                "test_samples": len(X_test),
            },
            "feature_importance": importances,
        }

        joblib.dump(artifact, MODEL_FILE)

        with open(METRICS_FILE, "w") as f:
            json.dump({
                "status": "success",
                "model_name": "RandomForestRegressor",
                "model_version": settings.ML_MODEL_VERSION,
                "trained_at": trained_at_iso,
                "artifact_path": MODEL_FILE,
                "metrics": artifact["metrics"],
                "feature_importance": importances,
                "provenance": provenance
            }, f, indent=2)

        return {
            "status": "success",
            "model_name": "RandomForestRegressor",
            "model_version": settings.ML_MODEL_VERSION,
            "trained_at": trained_at_iso,
            "artifact_path": MODEL_FILE,
            "metrics": artifact["metrics"],
            "feature_importance": importances,
            "provenance": provenance
        }

    @staticmethod
    def get_model_metrics() -> Dict[str, Any]:
        """
        Returns evaluation metrics of the currently saved model, or trains one if missing.
        """
        if os.path.exists(METRICS_FILE):
            try:
                with open(METRICS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass

        if os.path.exists(MODEL_FILE):
            try:
                artifact = joblib.load(MODEL_FILE)
                return {
                    "status": "success",
                    "model_name": artifact.get("model_name", "RandomForestRegressor"),
                    "model_version": artifact.get("version", settings.ML_MODEL_VERSION),
                    "trained_at": artifact.get("trained_at"),
                    "artifact_path": MODEL_FILE,
                    "metrics": artifact.get("metrics"),
                    "feature_importance": artifact.get("feature_importance")
                }
            except Exception:
                pass

        return DemandForecaster.train_and_evaluate()

    @staticmethod
    def get_model_info() -> List[Dict[str, Any]]:
        """
        Returns metadata for available models.
        """
        is_trained = os.path.exists(MODEL_FILE)
        trained_at = None
        if is_trained:
            try:
                artifact = joblib.load(MODEL_FILE)
                trained_at = artifact.get("trained_at")
            except Exception:
                pass

        return [
            {
                "model_name": "RandomForestRegressor",
                "model_version": settings.ML_MODEL_VERSION,
                "is_trained": is_trained,
                "trained_at": trained_at,
                "artifact_path": MODEL_FILE,
                "features": FEATURE_COLS,
                "description": "Ensemble Random Forest regressor with chronological train/test validation against historical route average baseline."
            },
            {
                "model_name": "HistoricalAverageBaseline",
                "model_version": "v1.0-baseline",
                "is_trained": is_trained,
                "trained_at": trained_at,
                "artifact_path": MODEL_FILE,
                "features": ["route_id"],
                "description": "Historical route average benchmark model predicting mean demand observed per corridor."
            }
        ]

    @staticmethod
    def predict_and_persist(
        route_id: int,
        target_date: date,
        departure_hour: Optional[int] = None,
        persist: bool = True
    ) -> Dict[str, Any]:
        """
        Loads fitted model, generates demand forecast with confidence intervals,
        and persists into MySQL demand_predictions using explicit raw SQL.
        """
        route = None
        try:
            from app.db.connection import get_db_connection
            from app.repositories.route_repository import RouteRepository
            with get_db_connection() as conn:
                route = RouteRepository.get_by_id(conn, route_id)
        except Exception:
            pass

        if not route:
            route = DEFAULT_ROUTES.get(route_id)

        if not route:
            raise ValueError(f"Route with ID {route_id} does not exist.")

        hour = departure_hour if departure_hour is not None else 8
        is_peak = compute_peak_hour_flag(hour)
        day_of_week = target_date.isoweekday()
        day_of_month = target_date.day
        month_of_year = target_date.month
        quarter_of_year = (month_of_year - 1) // 3 + 1
        is_weekend = 1 if day_of_week in [6, 7] else 0
        dist_km = float(route["total_distance_km"])
        dur_min = int(route["duration_est_minutes"])
        est_fare = round(dist_km * 1.85, 2)

        if not os.path.exists(MODEL_FILE):
            DemandForecaster.train_and_evaluate(force_synthetic=True)

        if os.path.exists(MODEL_FILE):
            artifact = joblib.load(MODEL_FILE)
            model = artifact["model"]
            route_means = artifact["route_means"]
            overall_mean = artifact["overall_mean"]

            route_hist_mean = route_means.get(route_id, overall_mean)

            input_dict = {
                "route_id": route_id,
                "total_distance_km": dist_km,
                "duration_est_minutes": dur_min,
                "departure_hour": hour,
                "is_peak_hour": is_peak,
                "day_of_week": day_of_week,
                "day_of_month": day_of_month,
                "month_of_year": month_of_year,
                "quarter_of_year": quarter_of_year,
                "is_weekend": is_weekend,
                "avg_base_fare": est_fare,
                "cancellations_count": max(0, int(round(route_hist_mean * 0.04))),
                "route_hist_mean": float(route_hist_mean),
            }

            X_input = pd.DataFrame([input_dict])[FEATURE_COLS]
            pred_float = float(model.predict(X_input)[0])
            predicted_demand = max(10, int(round(pred_float)))

            rmse = artifact.get("metrics", {}).get("rf_rmse", 25.0)
            margin = max(8, int(round(rmse * 1.645)))
        else:
            predicted_demand = max(30, int(round(dist_km * 0.35)))
            margin = max(5, int(round(predicted_demand * 0.15)))

        conf_low = max(0, predicted_demand - margin)
        conf_high = predicted_demand + margin

        features_meta = {
            "route_code": route["route_code"],
            "route_name": route["route_name"],
            "distance_km": dist_km,
            "duration_est_minutes": dur_min,
            "departure_hour": hour,
            "is_peak_hour": is_peak,
            "day_of_week": day_of_week,
            "day_of_month": day_of_month,
            "month_of_year": month_of_year,
            "quarter_of_year": quarter_of_year,
            "is_weekend": is_weekend,
            "avg_base_fare": est_fare,
            "confidence_margin": margin,
            "model_used": "RandomForestRegressor"
        }

        if persist:
            try:
                from app.db.connection import get_db_connection
                from app.repositories.prediction_repository import PredictionRepository
                with get_db_connection() as conn:
                    PredictionRepository.save_prediction(
                        connection=conn,
                        route_id=route_id,
                        prediction_date=target_date,
                        predicted_demand=predicted_demand,
                        confidence_interval_low=conf_low,
                        confidence_interval_high=conf_high,
                        model_version=settings.ML_MODEL_VERSION,
                        model_name="RandomForestRegressor",
                        features_json=features_meta
                    )
                    conn.commit()

                    records = PredictionRepository.get_predictions(conn, route_id=route_id, limit=1)
                    if records:
                        return records[0]
            except Exception:
                pass

        return {
            "prediction_id": 0,
            "route_id": route_id,
            "route_code": route["route_code"],
            "route_name": route["route_name"],
            "prediction_date": target_date,
            "predicted_demand": predicted_demand,
            "confidence_interval_low": conf_low,
            "confidence_interval_high": conf_high,
            "model_name": "RandomForestRegressor",
            "model_version": settings.ML_MODEL_VERSION,
            "features_json": features_meta,
            "created_at": datetime.now()
        }
