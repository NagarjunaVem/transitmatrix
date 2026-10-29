# TransitMatrix — Person 3 (Frontend Engineer) Comprehensive Technical Report

## 1. Executive Summary & Role Definition

**Role:** Person 3 — Senior React Frontend Engineer  
**System:** TransitMatrix: Intelligent Railway and Public Transit Management System  
**Objective:** Architect, develop, and integrate a responsive, production-standard React web application that interfaces directly with Person 2's FastAPI backend and Person 1's MySQL 8.0+ relational database, completely avoiding mock or synthetic frontend data in production flows.

---

## 2. Technology Constraints & Architecture

1. **Framework & Tooling:**
   - React 18+ with Vite for fast HMR and optimized production bundling.
   - Pure JavaScript (ES6+), following standard academic and industry requirements.
   - Tailwind CSS for clean, consistent utility styling.
   - React Router v6 for client-side routing, protected layouts, and role-based access control.
   - TanStack Query (React Query) for server state caching and optimistic updates.
   - Axios HTTP client configured with centralized interceptors for automatic JWT Bearer token injection.
   - Recharts for responsive SVG-based data visualizations.
   - Lucide React for consistent icons.

2. **Zero-Mock Policy:**
   - All dashboard metrics, station directories, route stop sequences, timetables, seat inventories, reservations, reports, Database Lab SQL executions, and ML forecasts consume live REST API endpoints exposed by FastAPI.
   - Database credentials and connection secrets are strictly prohibited in the browser bundle.

---

## 3. Implemented Modules and Pages

### 3.1 System Dashboard (`src/pages/Dashboard.jsx`)
- **Key Performance Indicators (KPIs):** Net revenue, confirmed passenger counts, active calendar trips, and operational delay incidents calculated directly from MySQL reporting views (`v_route_performance`, `v_monthly_revenue`, `v_delay_summary`).
- **Commercial Charts:** Bar charts comparing gross revenue vs refunds across transit corridors using Recharts.
- **Delay Analytics:** Donut charts rendering operational root-cause classifications (signaling failure, adverse weather, rolling stock maintenance).
- **Upcoming Journeys Table:** Live view of scheduled trips, departure timestamps, and base fares.

### 3.2 Stations & Route Corridor Management (`src/pages/StationsRoutes.jsx`)
- **Station Directory:** Searchable table of physical station records, terminal coordinates, platform counts, and railway zone affiliations.
- **Add Station Modal:** Form for authorized Staff/Admin to insert new station records directly into the MySQL database.
- **Topological Route Halts Sequence:** Interactive visualizer rendering sequential intermediate stations, platform halt durations, distance offsets, and departure offsets for any selected transit corridor.

### 3.3 Services & Timetables (`src/pages/ServicesTimetables.jsx`)
- **Train Service Catalog:** Grid of active train services (Rajdhani, Shatabdi, Vande Bharat, Superfast, Express) with operating rakes and service numbers.
- **Filterable Timetable:** Calendar scheduled trips searchable by service number or route corridor with real-time operational status badges (`ON_TIME`, `DELAYED`, `SCHEDULED`, `CANCELLED`).

### 3.4 Passenger Booking & Seat Selection Map (`src/pages/Booking.jsx`)
- **Corridor Search:** Select origin station, destination station, and journey date to query scheduled trains.
- **Interactive Coach & Seat Map:** Real-time seat inventory layout displaying coaches, seat numbers, class tiers (1A, 2A, 3A, SL, CC, EC), fare multipliers, and vacancy states.
- **ACID Concurrency Flow:** Consumes `POST /api/bookings` with pessimistic row-level locking (`SELECT ... FOR UPDATE`), immediately alerting passengers if a concurrent conflict occurs.
- **Confirmation Receipt:** Displays PNR reference, individual ticket numbers, allocated coach/seat numbers, and total fare.

### 3.5 My Reservations & Ticket Cancellation (`src/pages/MyBookings.jsx`)
- **Manifest History:** Chronological list of confirmed reservations and travel permits for the authenticated user.
- **Automated Refund & Seat Release:** Allows passengers to cancel tickets with real-time refund calculation; triggers MySQL database procedures to immediately restore seat inventory.

### 3.6 Analytical Reports & CSV Auditing (`src/pages/Reports.jsx`)
- **Route Performance Manifest:** Detailed financial and operational summary per corridor.
- **Monthly Revenue Report:** Month-by-month financial receipts by route and train service type.
- **Delay Incident Summary:** Station-level delay incident frequency and duration analysis.
- **CSV Export Engine:** Generates and downloads authorized tabular CSV reports directly in the browser.

### 3.7 Database Lab & SQL Workbench (`src/pages/DatabaseLab.jsx`)
- **21 Advanced SQL Demonstrations:** Catalog covering multi-table joins, nested scalar/IN subqueries, correlated EXISTS queries, aggregates with GROUP BY & HAVING, recursive graph CTEs, window functions (`ROW_NUMBER`, `DENSE_RANK`, `LAG`/`LEAD`, running totals), views, indexes, and transactions.
- **Live SQL Runner:** Executes selected SQL queries against MySQL via `/api/database-lab/execute/{id}`, displaying actual elapsed runtime in milliseconds and returned rows.
- **EXPLAIN Plan Visualizer:** Renders the MySQL Query Optimizer execution plan (table access types, index keys used, and examined row estimates).
- **ER Model & Normalization Guide:** Explains the 18 normalized tables, primary keys, and 1NF, 2NF, 3NF/BCNF proofs.

### 3.8 AI/ML Demand Forecasting Engine (`src/pages/MLForecast.jsx`)
- **Model Evaluation Cards:** Displays Random Forest MAE, RMSE, and $R^2$ scores benchmarked against the historical route mean baseline (+71.66% MAE improvement).
- **Interactive Inference Calculator:** Allows users to pick any corridor, target travel date, and departure hour to compute predicted passenger demand with 90% confidence intervals.
- **Feature Importance Ranking:** Visualizes the impact of rush hour dynamic multipliers, corridor distance, and route historical means.
- **Persisted Predictions Table:** Queries the `demand_predictions` table to display saved forecasts.

### 3.9 Authentication & Access Control (`src/pages/Login.jsx`, `src/pages/Register.jsx`)
- **Role-Based Protection:** Centralized `AuthContext` managing JWT tokens and role verification (`ADMIN`, `STAFF`, `PASSENGER`).
- **Quick-Fill Demo Credentials:** Buttons to easily toggle between Admin, Staff, and Passenger accounts for presentations.

---

## 4. Build and Integration Verification

The frontend application was compiled and verified using Vite:
- Production bundle generated cleanly:
  - HTML entry: `dist/index.html`
  - Bundled CSS: `dist/assets/index-BHuS7PoX.css`
  - Bundled JavaScript: `dist/assets/index-BxJFYrYA.js`
- Zero build warnings or unresolved dependencies.

---

## 5. Execution Instructions

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The application is accessible at `http://localhost:5173`.
