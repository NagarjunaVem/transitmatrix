# TransitMatrix: Intelligent Railway and Public Transit Management System

## 1. Project Overview
TransitMatrix is a production-standard, database-driven railway and public transit management system. The core relational architecture is built on MySQL 8.0+ using InnoDB, designed strictly following normalized relational database theory (1NF, 2NF, 3NF, BCNF) with explicit raw SQL scripts and **no ORM abstraction whatsoever**.

This repository contains:
1. **Database & SQL Layer (Person 1):** 18 relational tables, 11 indexes, 6 analytical views, 5 triggers, 7 stored procedures, 21 advanced demonstration queries, and versioned migrations (`V1` to `V6`).
2. **Backend API Layer (Person 2):** High-performance Python 3.12 + FastAPI backend using `mysql.connector.pooling`, atomic booking transactions with `SELECT ... FOR UPDATE` pessimistic locking, JWT authentication with Role-Based Access Control (RBAC), and pure raw SQL repositories.
3. **Machine Learning Pipeline (Person 4):** Real-time passenger demand forecasting engine using scikit-learn (`RandomForestRegressor`), benchmarked against historical route averages, trained with strict chronological splits (zero data leakage), and exposed via REST API and standalone CLI tools.
4. **Frontend Dashboard (Person 3):** Web management interface in React + Vite + Tailwind CSS consuming the documented REST API contracts.

---

## 2. Database Objects Implemented

### 2.1 Core Relational Tables (18 Tables)
1. `users`: System user credentials, contact details, and role assignments (`ADMIN`, `STAFF`, `PASSENGER`).
2. `passengers`: Traveler profiles, national identity card records, age, and demographic attributes.
3. `stations`: Railway stations, geo-coordinates, zone affiliations, and platform capacities.
4. `routes`: Transit corridors connecting origin and destination station pairs.
5. `route_stops`: Ordered sequential intermediate halts with distance and timing offsets.
6. `services`: Train service catalog with operating schedules and service types.
7. `vehicles`: Rolling stock rakes and locomotives with coach compositions and capacities.
8. `seats`: Physical seats inside coaches with coach code, seat number, and class tier.
9. `trips`: Calendar journey instances with scheduled departures and fares.
10. `trip_seat_inventory`: Per-trip seat availability records for row-level concurrency locking.
11. `bookings`: Master reservation transactions with PNR reference numbers.
12. `tickets`: Individual passenger journey permits with seat allocations.
13. `payments`: Payment receipts and settlement records (`CREDIT_CARD`, `DEBIT_CARD`, `UPI`, etc.).
14. `cancellations`: Cancellation records with refund calculation and fee deductions.
15. `waitlists`: First-in-first-out (FIFO) passenger queues for fully booked journeys.
16. `delays`: Operational delay incident tracking at stations with classified reasons.
17. `audit_logs`: Audit trail tracking DML mutations with JSON state diffs.
18. `demand_predictions`: Machine learning passenger demand forecasts per route.

### 2.2 Reporting and Analytical Views (6 Views)
- `v_booking_details`: Complete 8-table join of booking, traveler, train, coach, seat, and station details.
- `v_trip_availability`: Per-trip vacancy and occupancy percentage grouped by coach class.
- `v_route_performance`: Commercial and operational KPI summary per route (trips, delays, revenue, refunds).
- `v_monthly_revenue`: Month-by-month financial summary by route and service type.
- `v_delay_summary`: Station delay statistics and primary root causes.
- `v_passenger_travel_history`: Travel history manifest per passenger profile.

### 2.3 Query-Driven Indexes (11 B-Tree Indexes)
- `idx_trips_route_date_status`: Composite index for fast trip search by route, date, and status.
- `idx_inventory_trip_avail`: Accelerates vacancy lookups and row locking (`SELECT ... FOR UPDATE`).
- `idx_route_stops_station_seq`: Optimizes multi-station origin-to-destination route planning.
- `idx_bookings_user_date`: Speeds up customer booking history ordered chronologically.
- `idx_tickets_booking_id`: Foreign key child lookup index.
- `idx_tickets_passenger_status`: Speeds up traveler status checks.
- `idx_payments_booking_status`: Payment verification lookup.
- `idx_waitlists_queue_search`: Composite FIFO index for waitlist promotion queries.
- `idx_delays_trip_recorded`: Fast chronological delay analysis.
- `idx_predictions_route_date`: Efficient forecast retrieval.
- `idx_audit_table_record`: Compliance lookup by table and record ID.

### 2.4 Triggers (5 Triggers)
- `trg_audit_booking_update`: Automatically logs changes in booking status and fare to `audit_logs`.
- `trg_cancellation_after_insert`: Marks ticket as cancelled, automatically releases seat inventory, and audits.
- `trg_delays_after_insert`: Automatically flags trip status as `'DELAYED'` when delay exceeds 15 minutes.
- `trg_payments_after_insert`: Records financial transactions into the audit trail.
- `trg_validate_seat_inventory_before_insert`: Validates that seat belongs to the rake assigned to the trip.

### 2.5 Stored Procedures (7 Procedures)
- `sp_search_trips`: Searches trains between origin and destination on a given date with open seat counts.
- `sp_get_seat_availability`: Returns detailed seat maps and vacancy state by coach for a trip.
- `sp_create_atomic_booking`: Full transactional reservation with row-level locking (`SELECT ... FOR UPDATE`).
- `sp_cancel_booking`: Calculates refund, updates ticket status, releases seat, and triggers waitlist promotion.
- `sp_process_waitlist_promotion`: Promotes the next eligible waitlisted passenger when a seat opens up.
- `sp_route_revenue_report`: Aggregates gross revenue, refunds, and net earnings across date ranges.
- `sp_record_trip_delay`: Inserts delay event and updates trip operational status.

---

## 3. Machine Learning Demand Forecasting Engine (Person 4)

### 3.1 Architecture & Methodology
The AI/ML subsystem predicts passenger demand across travel corridors and time intervals using historical bookings, seasonal schedules, and rush-hour dynamics:
- **Zero ORM:** Raw SQL queries extract aggregated demand records across `routes`, `trips`, `services`, and `bookings`.
- **Zero Data Leakage:** Strict chronological 80/20 train/test splitting (never random splitting) guarantees test observations reflect true future operations.
- **Historical Route Mean Anchor:** Computed solely from the training partition to avoid target leakage.
- **Ensemble Model:** `RandomForestRegressor` (100 estimators, depth 8) compared directly against multiple benchmark baselines.
- **Uncertainty Bounds:** Produces 90% confidence intervals for every predicted demand point.

### 3.2 Benchmark Performance
Evaluated on out-of-sample chronological holdout data:
| Model / Strategy | MAE (Passengers) | RMSE | MAPE (%) | $R^2$ Score | Improvement vs Baseline |
|---|---|---|---|---|---|
| Global Network Mean Baseline | 59.42 | 71.12 | 13.72% | -0.0109 | Reference |
| Historical Route Mean Baseline | 49.64 | 60.34 | 11.51% | 0.2723 | Reference |
| Route + Day-of-Week Mean | 60.28 | 70.73 | 13.72% | 0.0002 | Reference |
| **Random Forest Regressor** | **14.07** | **17.15** | **3.12%** | **0.9412** | **+71.66% MAE Improvement** |

### 3.3 ML Command-Line Tools (`ml/`)
- `python ml/verify_pipeline.py`: Runs automated 5-point verification and caches pre-fitted model artifacts.
- `python ml/benchmark.py`: Runs statistical multi-baseline benchmark with ASCII error distribution.
- `python ml/train.py`: Chronological model training and metric reporting.
- `python ml/evaluate.py`: Detailed residual analysis and feature importance inspection.
- `python ml/predict.py --route-id 1 --date 2026-12-15 --hour 16 --persist`: Real-time demand inference with MySQL persistence.
- `python ml/generate_dataset.py --samples 400`: Synthetic dataset generator with peak-hour multipliers.

---

## 4. REST API Endpoint Mapping

| Method | Endpoint | Description | Role Required |
|---|---|---|---|
| `GET` | `/api/health` | Service health check | Public |
| `POST` | `/api/auth/register` | Register new user | Public |
| `POST` | `/api/auth/login` | User login (JWT Bearer) | Public |
| `GET` | `/api/auth/me` | Current authenticated user profile | Authenticated |
| `GET` | `/api/trips/search` | Search trips by origin, destination & date | Public |
| `POST` | `/api/bookings` | Atomic multi-seat reservation (`SELECT ... FOR UPDATE`) | `PASSENGER`, `STAFF`, `ADMIN` |
| `GET` | `/api/bookings/my-bookings` | Customer booking history | Authenticated |
| `POST` | `/api/cancellations` | Cancel ticket with automated refund & seat release | Authenticated |
| `GET` | `/api/database-lab/catalog` | Catalog of 21 advanced relational SQL queries | `STAFF`, `ADMIN` |
| `GET` | `/api/database-lab/execute/{id}`| Execute live SQL query and display execution plan | `STAFF`, `ADMIN` |
| `GET` | `/api/ml/forecast` | Real-time passenger demand forecast & confidence bounds | Public / Authenticated |
| `GET` | `/api/ml/metrics` | Model evaluation statistics (MAE, RMSE, $R^2$) vs baseline | Public / Authenticated |
| `GET` | `/api/ml/models` | Metadata for active and baseline ML models | Public / Authenticated |
| `POST` | `/api/ml/train` | Retrain Random Forest model on latest records | `STAFF`, `ADMIN` |
| `GET` | `/api/predictions` | List historical demand forecasts from MySQL | Public / Authenticated |

---

## 5. Setup & Execution Instructions

### 5.1 Database Initialization (One-Click)
- **Windows Command Prompt:**
  ```cmd
  init_database.bat
  ```
- **PowerShell:**
  ```powershell
  .\init_database.ps1
  ```

### 5.2 Environment Setup
```bash
# Create Python virtual environment
python -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 5.3 Apply Database Migrations (Raw SQL)
```bash
python -m backend.app.db.migrate
```

### 5.4 Launch FastAPI Backend Server
```bash
uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`

### 5.5 Run Automated Test Suite
```bash
pytest backend/tests -v
```

### 5.6 Verify Machine Learning Pipeline
```bash
python ml/verify_pipeline.py
python ml/benchmark.py
```

### 5.7 Docker Compose Deployment
```bash
docker compose up --build
```

---

## 6. Frontend Integration Guide (Person 3)

When Person 3 builds the React UI:
1. **Model Performance Cards:** Query `GET /api/ml/metrics` to render baseline vs Random Forest MAE, RMSE, and feature importances.
2. **Demand Forecast Chart:** Query `GET /api/ml/forecast?route_id={id}&target_date={YYYY-MM-DD}&departure_hour={hour}` to render point predictions and confidence interval shaded bands using Recharts.
3. **Historical Corridor Demand:** Query `GET /api/predictions?route_id={id}` to display past predictions and actual booking volumes.
4. **Database Lab:** Query `GET /api/database-lab/catalog` and `GET /api/database-lab/execute/{query_id}` to render the 21 live SQL statements and execution plans.
