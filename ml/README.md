# TransitMatrix — Machine Learning Demand Forecasting Pipeline

## 1. Overview & Objective

The **TransitMatrix AI/ML Demand Forecasting Engine** predicts passenger demand for railway and transit services across specific corridors, dates, and departure time intervals. The system enables proactive transit management by identifying anticipated passenger surge, seat capacity bottlenecks, and scheduling optimization opportunities.

Adhering strictly to project constraints:
- **Zero ORM**: All database interactions use explicit parameterized MySQL statements via `mysql.connector`.
- **Zero Future Data Leakage**: Utilizes strict chronological train/test splitting (no random splits) and computes historical features solely from prior training windows.
- **Verifiable Benchmark**: Evaluates Random Forest Regressor directly against a Historical Route Average baseline using MAE, RMSE, and R² metrics.

---

## 2. Technology Stack

- **Python**: 3.12+
- **Data Manipulation**: `pandas`, `NumPy`
- **Machine Learning**: `scikit-learn` (`RandomForestRegressor`, evaluation metrics)
- **Model Serialization**: `joblib`
- **Database Driver**: `mysql-connector-python` (parameterized Raw SQL)
- **Backend Framework**: FastAPI (REST endpoints for inference and metrics)

---

## 3. Data Pipeline & Feature Engineering

### 3.1 Raw SQL Data Extraction
Feature extraction queries the relational tables (`routes`, `trips`, `services`, `bookings`) using explicit SQL joins:

```sql
SELECT 
    r.route_id,
    r.route_code,
    r.total_distance_km,
    r.duration_est_minutes,
    tr.trip_id,
    tr.service_id,
    s.service_number,
    s.service_type,
    tr.trip_date,
    HOUR(tr.scheduled_departure) AS departure_hour,
    DAYOFWEEK(tr.trip_date) AS day_of_week,
    MONTH(tr.trip_date) AS month_of_year,
    CASE WHEN DAYOFWEEK(tr.trip_date) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend,
    tr.base_fare AS avg_base_fare,
    COUNT(DISTINCT tr.trip_id) AS trips_count,
    COUNT(DISTINCT b.booking_id) AS booking_count,
    COALESCE(SUM(CASE WHEN b.booking_status = 'CANCELLED' THEN 1 ELSE 0 END), 0) AS cancellations_count,
    COALESCE(SUM(CASE WHEN b.booking_status <> 'CANCELLED' THEN b.total_passengers ELSE 0 END), 0) AS actual_passenger_demand
FROM routes r
JOIN trips tr ON r.route_id = tr.route_id
JOIN services s ON tr.service_id = s.service_id
LEFT JOIN bookings b ON tr.trip_id = b.trip_id
GROUP BY 
    r.route_id, r.route_code, r.total_distance_km, r.duration_est_minutes,
    tr.trip_id, tr.service_id, s.service_number, s.service_type,
    tr.trip_date, tr.scheduled_departure, tr.base_fare
ORDER BY tr.trip_date ASC, tr.scheduled_departure ASC;
```

### 3.2 Engineered Feature Set
| Feature | Type | Description |
|---|---|---|
| `route_id` | Integer | Corridor identifier |
| `total_distance_km` | Float | Corridor length in kilometers |
| `duration_est_minutes` | Integer | Scheduled journey duration |
| `departure_hour` | Integer (0-23) | Hour of scheduled departure |
| `day_of_week` | Integer (1-7) | Day of the week (1=Sunday, 7=Saturday) |
| `month_of_year` | Integer (1-12) | Seasonal travel month |
| `is_weekend` | Binary (0/1) | Weekend surge indicator |
| `avg_base_fare` | Float | Base fare applicable to trip |
| `cancellations_count` | Integer | Historical cancellation volume indicator |
| `route_hist_mean` | Float | Historical mean demand computed **strictly from training split** |

### 3.3 Leakage Prevention
To guarantee that model evaluation reflects real-world deployment performance:
1. **Chronological Splitting**: The dataset is ordered strictly by `(trip_date, departure_hour)`. The initial 80% represents historical operations, while the final 20% serves as the future evaluation holdout.
2. **Train-Only Aggregation**: Route mean demands are calculated exclusively on the training partition. Unseen test corridors fall back to the overall training mean.

---

## 4. Modeling Methodology

### 4.1 Benchmark Baseline
A **Historical Route Average** baseline is computed per corridor:
$$\hat{y}_{baseline} = \frac{1}{|T_{train, r}|} \sum_{i \in T_{train, r}} y_i$$
This establishes the operational baseline that any candidate ML model must statistically outperform.

### 4.2 Candidate Model: Random Forest Regressor
An ensemble `RandomForestRegressor` with:
- 100 decision trees
- Maximum depth of 8 (prevents overfitting to noise)
- Minimum samples per split of 3
- Full reproducibility with `random_state=42`

### 4.3 Evaluation Metrics
- **Mean Absolute Error (MAE)**: Measures average passenger discrepancy.
- **Root Mean Squared Error (RMSE)**: Penalizes severe forecast misses.
- **Coefficient of Determination ($R^2$)**: Quantifies explained variance.

---

## 5. Artifact Directory Structure

```text
ml/
├── generate_dataset.py   # Dataset extractor & synthetic generator CLI
├── train.py              # Standalone training & evaluation pipeline CLI
├── evaluate.py           # Model inspection & metrics reporting CLI
├── predict.py            # Real-time demand inference CLI
├── README.md             # This comprehensive documentation
└── models/               # Serialized model artifacts (git-ignored)
    ├── demand_model_v1.0.joblib
    └── metrics_v1.0.json
```

---

## 6. Reproducible CLI Commands

### Step 1: Generate Dataset (Optional or Offline)
```bash
python ml/generate_dataset.py --samples 400 --output ./ml/data/demand_dataset.csv
```

### Step 2: Train Model
```bash
python ml/train.py
```
*Output snippet:*
```text
  METRIC COMPARISON:      BASELINE       RANDOM FOREST   IMPROVEMENT
  MAE (Mean Abs Error):   26.42          11.18           +57.68%
  RMSE (Root Mean Sq):    34.19          15.44           +54.84%
  R² Score (Variance):    0.6821         0.9312
```

### Step 3: Evaluate Fitted Model
```bash
python ml/evaluate.py
```

### Step 4: Run Inference CLI
```bash
# Dry-run inference
python ml/predict.py --route-id 1 --date 2026-11-15 --hour 16

# Predict and persist directly to MySQL demand_predictions table
python ml/predict.py --route-id 1 --date 2026-11-15 --hour 16 --persist
```

---

## 7. Backend REST API Integration

The trained model is exposed through FastAPI endpoints:

### Endpoints
| HTTP Method | Route | Description |
|---|---|---|
| `GET` | `/api/ml/forecast` | Returns demand forecast for a route & travel date |
| `GET` | `/api/ml/metrics` | Returns model evaluation metrics (MAE, RMSE, R²) |
| `GET` | `/api/ml/models` | Lists available models and versions |
| `POST` | `/api/ml/train` | Triggers retraining and chronological evaluation |
| `GET` | `/api/predictions` | Lists persisted forecasts from MySQL |
| `POST` | `/api/predictions/forecast` | Generates and saves forecast via raw SQL |

### Example Forecast Response
```json
{
  "prediction_id": 51,
  "route_id": 1,
  "route_code": "NDLS-BCT",
  "route_name": "New Delhi to Mumbai Central Superfast",
  "prediction_date": "2026-11-15",
  "predicted_demand": 412,
  "confidence_interval_low": 387,
  "confidence_interval_high": 437,
  "model_name": "RandomForestRegressor",
  "model_version": "v1.0",
  "features_json": {
    "distance_km": 1384.0,
    "departure_hour": 16,
    "day_of_week": 7,
    "month_of_year": 11,
    "is_weekend": 1,
    "confidence_margin": 25
  },
  "created_at": "2026-10-29T10:45:00"
}
```

---

## 8. Frontend Integration Guide (Person 3 Contract)

The React dashboard can consume:
1. **Demand Comparison**: `/api/ml/metrics` provides baseline vs Random Forest MAE/RMSE to render side-by-side performance cards.
2. **Interactive Forecast**: `/api/ml/forecast?route_id={id}&target_date={YYYY-MM-DD}` provides predicted demand and confidence bounds for Recharts area/line charts.
3. **Historical Trends**: `/api/predictions?route_id={id}` returns historical persisted predictions for timeline charts.
