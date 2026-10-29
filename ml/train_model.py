#!/usr/bin/env python3
"""
TransitMatrix - Standalone Machine Learning Model Training Script
Executes ML pipeline from command line: extracts raw SQL features, trains Random Forest,
compares against baseline, evaluates MAE/RMSE/R2, and persists model artifact.
"""

import sys
import os
import argparse

# Add backend directory to path so app modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ml.demand_forecasting import DemandForecaster


def main():
    parser = argparse.ArgumentParser(description="TransitMatrix ML Model Training")
    parser.add_argument("--force-synthetic", action="store_true", help="Force synthetic data generation")
    args = parser.parse_args()

    print("==================================================================")
    print("TransitMatrix: Passenger Demand Forecasting Model Training Pipeline")
    print("==================================================================")
    print("[1/3] Extracting historical trip and booking features via raw SQL...")
    df = DemandForecaster.extract_training_data()
    print(f"      Extracted {len(df)} live feature records from MySQL.")

    print("[2/3] Training RandomForestRegressor and Historical Average Baseline...")
    result = DemandForecaster.train_and_evaluate(force_synthetic=args.force_synthetic)

    if result.get("status") == "success":
        metrics = result["metrics"]
        print("[3/3] Training and Chronological Evaluation Complete:")
        print(f"      - Baseline MAE:       {metrics['baseline_mae']}")
        print(f"      - Baseline RMSE:      {metrics['baseline_rmse']}")
        print(f"      - Baseline R²:        {metrics.get('baseline_r2', 0.0)}")
        print(f"      - Random Forest MAE:  {metrics['rf_mae']}")
        print(f"      - Random Forest RMSE: {metrics['rf_rmse']}")
        print(f"      - Random Forest R²:   {metrics.get('rf_r2', 0.0)}")
        print(f"      - MAE Improvement:    {metrics.get('mae_improvement_pct', 0.0)}%")
        print(f"      - Artifact Saved To:  {result['artifact_path']}")
    else:
        print(f"Notice: {result.get('message', 'Training incomplete')}")


if __name__ == "__main__":
    main()
