# TransitMatrix - Standalone Machine Learning Model Training Script
# Executes ML pipeline from command line: extracts raw SQL features, trains Random Forest,
# compares against baseline, evaluates MAE/RMSE, and persists model artifact.

import sys
import os

# Add backend directory to path so app modules can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ml.demand_forecasting import DemandForecaster


def main():
    print("==================================================================")
    print("TransitMatrix: Passenger Demand Forecasting Model Training Pipeline")
    print("==================================================================")
    print("[1/3] Extracting historical trip and booking features via raw SQL...")
    df = DemandForecaster.extract_training_data()
    print(f"      Extracted {len(df)} feature records from MySQL.")

    print("[2/3] Training RandomForestRegressor and Historical Average Baseline...")
    result = DemandForecaster.train_and_evaluate()

    if result.get("status") == "success":
        metrics = result["metrics"]
        print("[3/3] Training and Evaluation Complete:")
        print(f"      - Baseline MAE:      {metrics['baseline_mae']}")
        print(f"      - Baseline RMSE:     {metrics['baseline_rmse']}")
        print(f"      - Random Forest MAE:  {metrics['rf_mae']}")
        print(f"      - Random Forest RMSE: {metrics['rf_rmse']}")
        print(f"      - Artifact Saved To: {result['artifact_path']}")
    else:
        print(f"Notice: {result.get('message', 'Training incomplete')}")


if __name__ == "__main__":
    main()
