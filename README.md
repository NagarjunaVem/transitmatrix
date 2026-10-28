# TransitMatrix: Intelligent Railway and Public Transit Management System

## 1. Project Overview
TransitMatrix is a database-driven railway and public transit management system. The core relational architecture is built on MySQL 8.0+ using InnoDB, designed strictly following normalized relational database theory (1NF, 2NF, 3NF, BCNF) with explicit raw SQL scripts and no ORM abstraction.

This repository implements the complete database and SQL engineering foundation (Person 1 deliverables), establishing a solid relational contract for backend API development, frontend dashboards, and machine learning demand forecasting.

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

### 2.6 Security & RBAC
- Roles: `transit_admin_role`, `transit_operator_role`, `transit_passenger_role`, `transit_analyst_role`.
- Dedicated service users provisioned following the Principle of Least Privilege.

---

## 3. Database Initialization Instructions

### Method A: One-Click Initializer (Recommended)
You can initialize and seed the entire database with a single click.

> [!NOTE]
> You only need to run **EITHER** `init_database.bat` **OR** `init_database.ps1` (not both). Both scripts execute the exact same database setup and verification tasks. `init_database.bat` is recommended for standard Windows use.

- **Option 1 (Recommended): Windows Command Prompt / Desktop Batch Script**
  Double-click `init_database.bat` in File Explorer, or open cmd and run:
  ```cmd
  init_database.bat
  ```

- **Option 2: PowerShell Script**
  Right-click and choose "Run with PowerShell", or execute:
  ```powershell
  .\init_database.ps1
  ```

The utility automatically:
1. Detects your MySQL / XAMPP installation (`C:\xampp` or `D:\xampp`).
2. Verifies live connection to port 3306.
3. Executes `schema.sql`, `indexes.sql`, `views.sql`, `triggers.sql`, `procedures.sql`, `security.sql`, and `seed.sql` in strict topological sequence.
4. Verifies and displays the live row counts for all 18 tables.
5. Offers an interactive prompt to execute the 21 advanced SQL query demonstrations.

---

### Method B: Single Command Script Sequence (Manual)
Ensure MySQL 8.0+ is running, then execute the SQL scripts in order:

```bash
# 1. Create schema and relational tables
mysql -u root -p < database/schema.sql

# 2. Create performance indexes
mysql -u root -p < database/indexes.sql

# 3. Create reporting views
mysql -u root -p < database/views.sql

# 4. Create triggers
mysql -u root -p < database/triggers.sql

# 5. Create stored procedures
mysql -u root -p < database/procedures.sql

# 6. Create RBAC roles and users
mysql -u root -p < database/security.sql

# 7. Seed sample data
mysql -u root -p < database/seed.sql
```

### Method B: Versioned Migrations
Alternatively, apply the versioned migrations located in `database/migrations/`:
- `V1__initial_schema.sql`
- `V2__views_and_indexes.sql`
- `V3__triggers_and_procedures.sql`
- `V4__security_roles.sql`
- `V5__sample_seed_data.sql`

---

## 4. Running Advanced SQL Demonstrations
To execute all 21 SQL query demonstrations:

```bash
mysql -u root -p transitmatrix < database/queries/all_queries_demonstration.sql
```

Individual query scripts are available under `database/queries/` (`q01` through `q21`).

---

## 5. Schema Contract for Team Members

### For Person 2 (Backend Engineer)
- **Database Driver:** `mysql-connector-python`.
- **Query Mode:** Use explicit parameterized raw SQL (`%s` placeholders). Never interpolate raw strings.
- **Seat Allocation Rule:** Always use `START TRANSACTION`, acquire lock with `SELECT ... FOR UPDATE` on `trip_seat_inventory`, update `is_available = FALSE`, insert `bookings` and `tickets`, then `COMMIT`. See `docs/concurrency-and-transactions.md` for complete transaction guidelines.
- **Stored Procedures:** You can call `sp_create_atomic_booking`, `sp_cancel_booking`, and `sp_search_trips` directly via `cursor.callproc(...)`.

### For Person 3 (Frontend Engineer)
- All station codes (e.g., `NDLS`, `BCT`, `HWH`) and service types correspond to realistic Indian transit hubs.
- Analytical reporting screens can pull directly from endpoints exposing `v_booking_details`, `v_trip_availability`, `v_route_performance`, and `v_delay_summary`.

### For Person 4 (Machine Learning Engineer)
- Extract historical training data by joining `bookings`, `tickets`, `trips`, and `delays`.
- Persist forecasted passenger counts directly into `demand_predictions` matching `(route_id, prediction_date, model_version)`.

---

## 6. Backend Setup & Execution Guide (Person 2)

### 6.1 Environment Configuration
Copy `.env.example` to `.env` and verify database credentials:
```bash
cp .env.example .env
```

### 6.2 Python Virtual Environment & Dependencies
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt
```

### 6.3 Run Database Migrations (Raw SQL)
To apply versioned migrations `V1` to `V5` automatically with tracking in `schema_version`:
```bash
python -m backend.app.db.migrate
```

### 6.4 Launch FastAPI Backend Server
```bash
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- Interactive Swagger UI: `http://localhost:8000/docs`
- ReDoc Documentation: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/api/health`

### 6.5 Run Automated Test Suite
```bash
pytest backend/tests -v
```

### 6.6 Machine Learning Demand Forecasting Pipeline
To run model training, evaluate MAE/RMSE against baseline, and serialize model artifact:
```bash
python ml/train_model.py
```

### 6.7 Docker Compose Deployment
To run both MySQL 8.0 and the FastAPI backend in synchronized containers:
```bash
docker compose up --build
```
