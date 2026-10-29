#!/usr/bin/env python3
"""
TransitMatrix - Machine Learning Model Training Pipeline
Executes chronological train/test split (no random split), trains Historical Average baseline
and Random Forest Regressor, evaluates MAE/RMSE/R2, and saves versioned model artifacts.
"""

import sys
import os
import argparse
import json

# Add backend directory to sys.path so app modules can be loaded
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.ml.demand_forecasting import DemandForecaster


def run_training(force_synthetic: bool = False):
    print("==================================================================")
    print("TransitMatrix: Passenger Demand Forecasting Model Training")
    print("==================================================================")

    print("[1/3] Loading feature dataset (Raw SQL extraction with chronological order)...")
    result = DemandForecaster.train_and_evaluate(force_synthetic=force_synthetic)

    if result.get("status") == "success":
        metrics = result["metrics"]
        importances = result.get("feature_importance", {})

        print("\n[2/3] Model Training & Chronological Evaluation Complete:")
        print("------------------------------------------------------------------")
        print(f"  Training Samples:      {metrics['train_samples']}")
        print(f"  Testing Samples:       {metrics['test_samples']} (Chronological Holdout)")
        print(f"  Model Version:         {result['model_version']}")
        print(f"  Data Provenance:       {result.get('provenance', 'unknown')}")
        print("------------------------------------------------------------------")
        print("  METRIC COMPARISON:      BASELINE       RANDOM FOREST   IMPROVEMENT")
        print(f"  MAE (Mean Abs Error):   {metrics['baseline_mae']:<14.2f} {metrics['rf_mae']:<15.2f} {metrics['mae_improvement_pct']}%")
        print(f"  RMSE (Root Mean Sq):    {metrics['baseline_rmse']:<14.2f} {metrics['rf_rmse']:<15.2f} {metrics['rmse_improvement_pct']}%")
        print(f"  R² Score (Variance):    {metrics.get('baseline_r2', 0.0):<14.4f} {metrics.get('rf_r2', 0.0):<15.4f}")
        print("------------------------------------------------------------------")

        print("\n[3/3] Feature Importance:")
        for feat, score in list(importances.items())[:6]:
            bar = "#" * int(score * 40)
            print(f"  - {feat:<22}: {score:.4f} | {bar}")

        print(f"\n[+] Saved fitted model artifact to: {result['artifact_path']}")
        print("==================================================================")
        return 0
    else:
        print(f"[-] Training failed or incomplete: {result.get('message')}")
        return 1


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TransitMatrix ML Model Training")
    parser.add_argument("--force-synthetic", action="store_true", help="Force synthetic data generation for offline training")
    args = parser.parse_args()

    sys.exit(run_training(force_synthetic=args.force_synthetic))
