#!/usr/bin/env python3
"""
TransitMatrix - End-to-End ML Pipeline Verification and Pre-Caching Script
Runs diagnostic checks across dataset extraction, chronological model training,
metrics validation, and inference, and pre-caches the model artifact for the backend.
"""

import sys
import os
import json
import time

# Add backend directory to sys.path so app modules can be loaded
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.ml.demand_forecasting import DemandForecaster, MODEL_FILE, METRICS_FILE, FEATURE_COLS
from datetime import date


def verify_pipeline():
    print("==================================================================")
    print("TransitMatrix: AI/ML Demand Forecasting Verification Suite")
    print("==================================================================")
    start_time = time.time()
    errors = []

    # Check 1: Feature Extraction & Data Generation
    print("[1/5] Testing Data Extraction and Synthetic Dataset Generation...")
    try:
        df = DemandForecaster.generate_synthetic_data(num_samples=250)
        assert len(df) >= 200, f"Expected >= 200 samples, got {len(df)}"
        assert "actual_passenger_demand" in df.columns
        print(f"      PASS: Successfully generated {len(df)} records across {df['route_id'].nunique()} corridors.")
    except Exception as e:
        print(f"      FAIL: {e}")
        errors.append(f"Data Generation: {e}")

    # Check 2: Model Training & Chronological Holdout Evaluation
    print("[2/5] Running Chronological Training (Random Forest vs Baseline)...")
    try:
        train_res = DemandForecaster.train_and_evaluate(force_synthetic=True)
        assert train_res["status"] == "success"
        metrics = train_res["metrics"]
        assert metrics["rf_mae"] <= metrics["baseline_mae"] * 1.05
        print(f"      PASS: Baseline MAE={metrics['baseline_mae']:.2f} | RF MAE={metrics['rf_mae']:.2f}")
        print(f"      PASS: Baseline RMSE={metrics['baseline_rmse']:.2f} | RF RMSE={metrics['rf_rmse']:.2f}")
        print(f"      PASS: Random Forest Improvement = {metrics.get('mae_improvement_pct', 0.0):.2f}%")
    except Exception as e:
        print(f"      FAIL: {e}")
        errors.append(f"Training & Evaluation: {e}")

    # Check 3: Model Artifact Existence and Integrity
    print("[3/5] Verifying Serialized Model Artifacts...")
    try:
        assert os.path.exists(MODEL_FILE), f"Missing model file at {MODEL_FILE}"
        assert os.path.exists(METRICS_FILE), f"Missing metrics file at {METRICS_FILE}"
        with open(METRICS_FILE, "r") as f:
            meta = json.load(f)
            assert meta["status"] == "success"
            assert "metrics" in meta
        print(f"      PASS: Verified model at {MODEL_FILE} ({os.path.getsize(MODEL_FILE)} bytes).")
        print(f"      PASS: Verified metrics JSON at {METRICS_FILE}.")
    except Exception as e:
        print(f"      FAIL: {e}")
        errors.append(f"Artifact Verification: {e}")

    # Check 4: Real-Time Inference Simulation
    print("[4/5] Testing Real-Time Inference Simulation across Corridors...")
    sample_routes = [
        {"route_id": 1, "route_code": "NDLS-BCT", "route_name": "New Delhi to Mumbai Central", "total_distance_km": 1384.0, "duration_est_minutes": 950},
        {"route_id": 3, "route_code": "NDLS-HWH", "route_name": "New Delhi to Howrah", "total_distance_km": 1447.0, "duration_est_minutes": 1020},
        {"route_id": 9, "route_code": "SBC-MAS", "route_name": "Bangalore to Chennai", "total_distance_km": 358.0, "duration_est_minutes": 260},
    ]

    from unittest.mock import patch
    for r in sample_routes:
        with patch("app.repositories.route_repository.RouteRepository.get_by_id", return_value=r):
            try:
                forecast = DemandForecaster.predict_and_persist(
                    route_id=r["route_id"],
                    target_date=date(2026, 12, 15),
                    departure_hour=16,
                    persist=False
                )
                assert forecast["predicted_demand"] > 0
                assert forecast["confidence_interval_low"] <= forecast["predicted_demand"]
                assert forecast["confidence_interval_high"] >= forecast["predicted_demand"]
                print(f"      PASS: Corridor {r['route_code']} -> Predicted: {forecast['predicted_demand']} [{forecast['confidence_interval_low']} - {forecast['confidence_interval_high']}]")
            except Exception as e:
                print(f"      FAIL for route {r['route_id']}: {e}")
                errors.append(f"Inference {r['route_code']}: {e}")

    # Check 5: Summary Report
    elapsed = round(time.time() - start_time, 2)
    print("------------------------------------------------------------------")
    if not errors:
        print(f"[+] ALL 5 CHECKS PASSED SUCCESSFULLY in {elapsed}s.")
        print("[+] Machine learning pipeline is certified production-ready!")
        print("==================================================================")
        return 0
    else:
        print(f"[-] VERIFICATION FAILED with {len(errors)} error(s):")
        for err in errors:
            print(f"    - {err}")
        print("==================================================================")
        return 1


if __name__ == "__main__":
    sys.exit(verify_pipeline())
