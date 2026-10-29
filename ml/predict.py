#!/usr/bin/env python3
"""
TransitMatrix - Standalone Machine Learning Prediction Script
Generates passenger demand forecast for a specific route and travel date.
Computes 90% confidence intervals and optionally persists records into MySQL via raw SQL.
"""

import sys
import os
import argparse
from datetime import date, datetime

# Add backend directory to sys.path so app modules can be loaded
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.ml.demand_forecasting import DemandForecaster


def run_prediction(route_id: int, target_date_str: str, hour: int = 8, persist: bool = False):
    print("==================================================================")
    print("TransitMatrix: Real-Time Passenger Demand Inference")
    print("==================================================================")

    try:
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except ValueError:
        print(f"[-] Invalid date format: '{target_date_str}'. Use YYYY-MM-DD.")
        return 1

    print(f"[*] Querying Forecast for Route ID {route_id} on {target_date} (Departure: {hour:02d}:00)...")

    try:
        prediction = DemandForecaster.predict_and_persist(
            route_id=route_id,
            target_date=target_date,
            departure_hour=hour,
            persist=persist
        )
    except Exception as e:
        print(f"[-] Inference failed: {e}")
        return 1

    print("\n---------------------- FORECAST RESULTS --------------------------")
    print(f"  Route:                {prediction.get('route_code', 'N/A')} - {prediction.get('route_name', 'Route #' + str(route_id))}")
    print(f"  Travel Date:          {prediction.get('prediction_date')}")
    print(f"  Departure Hour:       {hour:02d}:00")
    print(f"  PREDICTED DEMAND:     {prediction.get('predicted_demand')} passengers")
    print(f"  90% Confidence Range: [{prediction.get('confidence_interval_low')} - {prediction.get('confidence_interval_high')}] passengers")
    print(f"  Model Employed:       {prediction.get('model_name', 'RandomForestRegressor')} ({prediction.get('model_version', 'v1.0')})")
    print(f"  Persisted to MySQL:   {'YES (ID: ' + str(prediction.get('prediction_id')) + ')' if persist else 'NO (Dry Run)'}")
    print("------------------------------------------------------------------")

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TransitMatrix Demand Forecaster CLI")
    parser.add_argument("--route-id", "-r", type=int, required=True, help="Route ID to predict for")
    parser.add_argument("--date", "-d", type=str, required=True, help="Target date in YYYY-MM-DD format")
    parser.add_argument("--hour", "-H", type=int, default=8, help="Scheduled departure hour (0-23)")
    parser.add_argument("--persist", "-p", action="store_true", help="Persist prediction into MySQL database")
    args = parser.parse_args()

    sys.exit(run_prediction(
        route_id=args.route_id,
        target_date_str=args.date,
        hour=args.hour,
        persist=args.persist
    ))
