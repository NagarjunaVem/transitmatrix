#!/usr/bin/env python3
"""
TransitMatrix - Machine Learning Dataset Generator
Generates realistic historical transit demand dataset or extracts live records via raw SQL.
Clearly labels synthetic simulation data.
"""

import sys
import os
import argparse
import pandas as pd

# Add backend directory to sys.path so app modules can be loaded
BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from app.ml.demand_forecasting import DemandForecaster


def generate_dataset(output_path: str, samples: int = 400, mode: str = "auto") -> pd.DataFrame:
    """
    Generates or extracts passenger demand dataset.
    modes:
      'live': Extracts strictly from MySQL via raw SQL
      'synthetic': Generates simulated dataset
      'auto': Attempts live MySQL extraction first; if fewer than 20 rows, generates synthetic
    """
    print(f"[*] TransitMatrix ML Dataset Generation (Mode: {mode}, Samples: {samples})")

    df = pd.DataFrame()
    if mode in ("live", "auto"):
        print("    [1/2] Attempting live MySQL raw SQL extraction...")
        try:
            df = DemandForecaster.extract_training_data()
            print(f"          Retrieved {len(df)} live records from database.")
        except Exception as e:
            print(f"          Live extraction skipped: {e}")

    if mode == "synthetic" or (mode == "auto" and len(df) < 20):
        print("    [2/2] Generating realistic synthetic simulation dataset...")
        df_synth = DemandForecaster.generate_synthetic_data(num_samples=samples)
        if len(df) > 0:
            df = pd.concat([df_synth, df], ignore_index=True)
            print(f"          Merged {len(df_synth)} simulated records with {len(df) - len(df_synth)} live records.")
        else:
            df = df_synth
            print(f"          Generated {len(df_synth)} simulated records.")

    # Sort chronologically
    df = df.sort_values(by=["trip_date", "departure_hour"]).reset_index(drop=True)

    # Save to disk
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"[+] Dataset saved successfully to: {output_path}")

    # Dataset Summary
    print("\n================== Dataset Summary ==================")
    print(f"  Total Records:          {len(df)}")
    print(f"  Unique Routes:          {df['route_id'].nunique()}")
    print(f"  Date Range:             {df['trip_date'].min()} to {df['trip_date'].max()}")
    print(f"  Mean Passenger Demand:  {df['actual_passenger_demand'].mean():.2f}")
    print(f"  Min/Max Demand:         {df['actual_passenger_demand'].min()} / {df['actual_passenger_demand'].max()}")
    print(f"  Is Simulated Data:      {bool(df.get('is_simulated', pd.Series([False])).any())}")
    print("=====================================================\n")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TransitMatrix ML Dataset Generator")
    parser.add_argument("--output", "-o", type=str, default="./ml/data/demand_dataset.csv", help="Output CSV path")
    parser.add_argument("--samples", "-s", type=int, default=400, help="Number of samples to generate")
    parser.add_argument("--mode", "-m", type=str, choices=["auto", "live", "synthetic"], default="auto", help="Extraction mode")
    args = parser.parse_args()

    generate_dataset(output_path=args.output, samples=args.samples, mode=args.mode)
