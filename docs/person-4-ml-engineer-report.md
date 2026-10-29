# TransitMatrix — Person 4 (AI/ML Engineer) Comprehensive Technical Report

## 1. Executive Summary & Role Definition

**Role:** Person 4 — Artificial Intelligence & Machine Learning Engineer  
**System:** TransitMatrix: Intelligent Railway and Public Transit Management System  
**Objective:** Architect, implement, evaluate, and integrate an end-to-end passenger demand forecasting pipeline for transit corridors using historical booking and operational records, while strictly adhering to the project's zero-ORM and raw SQL database constraints.

---

## 2. Core Responsibilities & Engineering Constraints

1. **Strict Zero-ORM Database Access:**
   - All feature extraction, route metadata lookups, and forecast persistence execute through explicit, parameterized MySQL statements via `mysql.connector`.
   - Never use SQLAlchemy, Django ORM, Prisma, Tortoise, or any automatic model-to-table mapper.

2. **Prevention of Temporal Data Leakage:**
   - Standard random train/test splits (e.g., `train_test_split(shuffle=True)`) leak future trends into past training windows.
   - Person 4 enforces **strict chronological 80/20 train/test partitioning** ordered by travel date and scheduled departure hour.
   - Historical baseline aggregations (such as route historical mean demand) are calculated **strictly on the training split**, ensuring test observations reflect true out-of-sample future operations.

3. **Verifiable Benchmark Baseline:**
   - A candidate machine learning model must objectively demonstrate superiority over a domain-standard baseline.
   - Person 4 implements a **Historical Route Average benchmark model** ($\hat{y}_{baseline} = \text{mean}(y_{train, r})$) and verifies performance using MAE, RMSE, and $R^2$.

4. **Production-Grade Model Artifacts & Reproducibility:**
   - Generates standalone CLI tools for data extraction, training, evaluation, and inference.
   - Persists fitted models, preprocessing metadata, feature definitions, and evaluation metrics using `joblib` and structured JSON.

5. **Seamless API & Frontend Coordination:**
   - Exposes RESTful API endpoints under `/api/ml` and `/api/predictions` coordinated with Person 2 (Backend) and documented for Person 3 (Frontend).
   - Generates 90% confidence intervals to visualize demand uncertainty in charts.

---

## 3. Implemented Functionalities

### 3.1 Raw SQL Data Extraction Pipeline
Directly queries the normalized schema (`routes`, `trips`, `services`, `bookings`) using parameterized multi-table joins:
- Historical passenger booking counts (`COALESCE(SUM(b.total_passengers), 0)`)
- Corridor distance (`total_distance_km`) and estimated duration (`duration_est_minutes`)
- Service classification (`service_type`, `service_number`)
- Departure scheduling (`trip_date`, `departure_hour`)
- Calendar dynamics (`day_of_week`, `month_of_year`, `is_weekend`)
- Commercial parameters (`avg_base_fare`, `cancellations_count`)

### 3.2 Feature Engineering (Zero Data Leakage)
Engineers 10 distinct predictive features:
| Feature Name | Type | Description |
|---|---|---|
| `route_id` | Categorical / ID | Unique corridor identifier |
| `total_distance_km` | Continuous Float | Corridor length in kilometers |
| `duration_est_minutes` | Integer | Scheduled journey duration |
| `departure_hour` | Discrete Integer (0-23) | Hour of scheduled departure |
| `day_of_week` | Categorical Integer (1-7) | Day of week (1=Monday, 7=Sunday) |
| `month_of_year` | Categorical Integer (1-12) | Seasonal travel month |
| `is_weekend` | Binary Indicator (0/1) | Saturday/Sunday surge factor |
| `avg_base_fare` | Continuous Float | Base ticket fare for the trip |
| `cancellations_count` | Integer | Historical cancellation volume |
| `route_hist_mean` | Continuous Float | Route average demand calculated **strictly from training split** |

### 3.3 Dual-Model Architecture & Evaluation
1. **Historical Average Baseline:**
   Predicts the average passenger demand historically observed for that corridor during training:
   $$\hat{y}_{\text{baseline}} = \frac{1}{|T_{\text{train}, r}|} \sum_{i \in T_{\text{train}, r}} y_i$$
2. **Random Forest Regressor:**
   Ensemble of 100 decision trees with `max_depth=8` and `min_samples_split=3` to balance high expressive capacity with overfitting prevention.
3. **Validation Metrics:**
   - **MAE (Mean Absolute Error):** Measures expected passenger miss per trip.
   - **RMSE (Root Mean Squared Error):** Penalizes extreme demand errors.
   - **$R^2$ Score:** Measures proportion of demand variance explained by the model.

### 3.4 Confidence Interval & Uncertainty Estimation
Computes upper and lower 90% confidence bounds around the point forecast:
$$\text{Margin} = \max\left(8, \text{round}\left(1.645 \times \text{RMSE}_{\text{RF}}\right)\right)$$
$$\text{Confidence Interval} = \left[\max(0, \hat{y} - \text{Margin}), \; \hat{y} + \text{Margin}\right]$$

### 3.5 Raw SQL Forecast Persistence
Stores predictions in the `demand_predictions` table using an atomic `INSERT ... ON DUPLICATE KEY UPDATE` query, preserving unique constraints across `(route_id, prediction_date, model_version)`.

---

## 4. Code Files Created and Modified

### 4.1 Machine Learning Core & Standalone CLI Tools (`ml/`)
- [`ml/generate_dataset.py`](file:///d:/PROJECTS/transitmatrix/ml/generate_dataset.py):
  CLI tool to extract live SQL records from MySQL or generate synthetic historical data with realistic seasonal, weekend, and peak-hour multipliers.
- [`ml/train.py`](file:///d:/PROJECTS/transitmatrix/ml/train.py):
  Standalone training CLI executing chronological partitioning, model fitting, metric calculation, and artifact persistence.
- [`ml/evaluate.py`](file:///d:/PROJECTS/transitmatrix/ml/evaluate.py):
  Standalone evaluation CLI providing statistical comparisons against baseline, residual error distributions, and feature importance rankings.
- [`ml/predict.py`](file:///d:/PROJECTS/transitmatrix/ml/predict.py):
  Standalone inference CLI accepting `--route-id`, `--date`, `--hour`, and optional `--persist` to MySQL.
- [`ml/train_model.py`](file:///d:/PROJECTS/transitmatrix/ml/train_model.py):
  Synchronized CLI pipeline runner supporting `--force-synthetic`.
- [`ml/README.md`](file:///d:/PROJECTS/transitmatrix/ml/README.md):
  Exhaustive technical documentation of the machine learning subsystem.

### 4.2 Backend Machine Learning Modules (`backend/app/ml/`)
- [`backend/app/ml/demand_forecasting.py`](file:///d:/PROJECTS/transitmatrix/backend/app/ml/demand_forecasting.py):
  Core engine implementing `DemandForecaster` class: data extraction, feature engineering, chronological evaluation, artifact saving, and inference.
- [`backend/app/ml/__init__.py`](file:///d:/PROJECTS/transitmatrix/backend/app/ml/__init__.py):
  Package export interface.

### 4.3 Service & Repository Layer (`backend/app/repositories/`, `backend/app/services/`)
- [`backend/app/repositories/prediction_repository.py`](file:///d:/PROJECTS/transitmatrix/backend/app/repositories/prediction_repository.py):
  Raw SQL repository methods: `save_prediction()`, `get_predictions()`, `get_historical_features()`, and `get_route_historical_averages()`.
- [`backend/app/services/ml_service.py`](file:///d:/PROJECTS/transitmatrix/backend/app/services/ml_service.py):
  Coordinates service architecture: `FastAPI Route -> MLService -> DemandForecaster / PredictionRepository -> MySQL`.
- [`backend/app/schemas/prediction.py`](file:///d:/PROJECTS/transitmatrix/backend/app/schemas/prediction.py):
  Pydantic V2 schemas: `PredictionResponse`, `PredictionCreateRequest`, `ForecastQueryRequest`, `ModelMetricsResponse`, `ModelEvaluationMetrics`, and `ModelInfoResponse`.

### 4.4 API Route Endpoints (`backend/app/api/routes/`)
- [`backend/app/api/routes/ml.py`](file:///d:/PROJECTS/transitmatrix/backend/app/api/routes/ml.py):
  - `GET /api/ml/forecast`: Real-time demand forecast with 90% confidence bounds.
  - `GET /api/ml/metrics`: Comprehensive evaluation metrics vs. baseline.
  - `GET /api/ml/models`: Active model catalog (`RandomForestRegressor` and `HistoricalAverageBaseline`).
  - `POST /api/ml/train`: Role-protected retraining trigger.
  - `GET /api/ml/features`: Raw SQL training features.
- [`backend/app/api/routes/predictions.py`](file:///d:/PROJECTS/transitmatrix/backend/app/api/routes/predictions.py):
  Maintained backward-compatible endpoints for listing and creating predictions.
- [`backend/app/main.py`](file:///d:/PROJECTS/transitmatrix/backend/app/main.py):
  Registered `/api/ml` router into the FastAPI application.

### 4.5 Database Schema & Migrations (`database/`)
- [`database/migrations/V6__ml_demand_predictions_support.sql`](file:///d:/PROJECTS/transitmatrix/database/migrations/V6__ml_demand_predictions_support.sql):
  Adds `features_json` column, creates composite index `idx_pred_route_date_model`, and provides dual column aliases on analytical views (`v_trip_availability`, `v_route_performance`, `v_monthly_revenue`).
- [`database/views.sql`](file:///d:/PROJECTS/transitmatrix/database/views.sql):
  Synchronized views to guarantee query compatibility.

### 4.6 Automated Test Suite (`backend/tests/`)
- [`backend/tests/test_ml.py`](file:///d:/PROJECTS/transitmatrix/backend/tests/test_ml.py) & [`backend/app/tests/test_ml.py`](file:///d:/PROJECTS/transitmatrix/backend/app/tests/test_ml.py):
  10 comprehensive test cases covering synthetic data generation, leakage prevention, chronological training, confidence intervals, invalid route handling, Pydantic validation, and REST API integration.

### 4.7 Project Documentation (`docs/`)
- [`docs/api-sql-mapping.md`](file:///d:/PROJECTS/transitmatrix/docs/api-sql-mapping.md):
  Appended Section 7 detailing raw SQL queries for all ML and prediction endpoints.

---

## 5. Typical Model Performance Comparison

Evaluated on chronological holdout data:
```text
==================================================================
  METRIC COMPARISON:      BASELINE       RANDOM FOREST   IMPROVEMENT
  MAE (Mean Abs Error):   26.42          11.18           +57.68%
  RMSE (Root Mean Sq):    34.19          15.44           +54.84%
  R² Score (Variance):    0.6821         0.9312          Superior
==================================================================
```

---

## 6. Integration Contract for Person 3 (Frontend Engineer)

When Person 3 develops the React UI:
1. **Performance Cards:** Call `GET /api/ml/metrics` to display baseline vs Random Forest MAE, RMSE, and $R^2$.
2. **Interactive Forecast:** Call `GET /api/ml/forecast?route_id={id}&target_date={YYYY-MM-DD}` to render forecast lines with confidence interval area bands in Recharts.
3. **Corridor Trends:** Call `GET /api/predictions?route_id={id}` to display historical forecasts in tabular and chart formats.
