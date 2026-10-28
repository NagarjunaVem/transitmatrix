# TransitMatrix: API to Raw SQL Mapping Specification

This document maps every FastAPI REST endpoint to its exact underlying parameterized MySQL SQL statement, view, or stored procedure. **No ORM or query builder is used anywhere in the backend.**

---

## 1. Authentication Endpoints (`/api/auth`)

### 1.1 Register User
- **Method & Route:** `POST /api/auth/register`
- **Access Role:** Public
- **Raw SQL Operations:**
  ```sql
  -- Step 1: Check username uniqueness
  SELECT user_id, username, email FROM users WHERE username = %s;

  -- Step 2: Check email uniqueness
  SELECT user_id, username, email FROM users WHERE email = %s;

  -- Step 3: Insert user
  INSERT INTO users (
      username, email, password_hash, role,
      first_name, last_name, phone_number, is_active
  ) VALUES (%s, %s, %s, %s, %s, %s, %s, TRUE);
  ```

### 1.2 User Login
- **Method & Route:** `POST /api/auth/login`
- **Access Role:** Public
- **Raw SQL Operations:**
  ```sql
  SELECT user_id, username, email, password_hash, role, is_active
  FROM users
  WHERE username = %s;
  ```

### 1.3 Current User Profile
- **Method & Route:** `GET /api/auth/me`
- **Access Role:** Authenticated (`ADMIN`, `STAFF`, `PASSENGER`)
- **Raw SQL Operations:**
  ```sql
  SELECT user_id, username, email, role, first_name, last_name, phone_number, is_active, created_at
  FROM users
  WHERE user_id = %s;
  ```

---

## 2. Stations & Routes Endpoints (`/api/stations`, `/api/routes`)

### 2.1 List Stations
- **Method & Route:** `GET /api/stations`
- **Access Role:** Public
- **Raw SQL Operations:**
  ```sql
  SELECT station_id, station_code, station_name, city, state, zone,
         total_platforms, latitude, longitude, is_active, created_at
  FROM stations
  WHERE station_code LIKE %s OR station_name LIKE %s OR city LIKE %s
  ORDER BY station_name ASC
  LIMIT %s OFFSET %s;
  ```

### 2.2 Create Station
- **Method & Route:** `POST /api/stations`
- **Access Role:** `ADMIN`, `STAFF`
- **Raw SQL Operations:**
  ```sql
  INSERT INTO stations (
      station_code, station_name, city, state, zone,
      total_platforms, latitude, longitude, is_active
  ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
  ```

### 2.3 List Routes
- **Method & Route:** `GET /api/routes`
- **Access Role:** Public
- **Raw SQL Operations:**
  ```sql
  SELECT r.route_id, r.route_code, r.route_name,
         r.origin_station_id, st_orig.station_code AS origin_station_code, st_orig.station_name AS origin_station_name,
         r.destination_station_id, st_dest.station_code AS destination_station_code, st_dest.station_name AS destination_station_name,
         r.total_distance_km, r.duration_est_minutes, r.is_active, r.created_at
  FROM routes r
  JOIN stations st_orig ON r.origin_station_id = st_orig.station_id
  JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
  ORDER BY r.route_id ASC
  LIMIT %s OFFSET %s;
  ```

### 2.4 Get Route Stops Sequence
- **Method & Route:** `GET /api/routes/{route_id}`
- **Access Role:** Public
- **Raw SQL Operations:**
  ```sql
  SELECT rs.stop_id, rs.route_id, rs.station_id, rs.stop_sequence,
         rs.distance_from_origin_km, rs.departure_offset_minutes,
         rs.arrival_offset_minutes, rs.halt_duration_minutes, rs.platform_number,
         s.station_code, s.station_name
  FROM route_stops rs
  JOIN stations s ON rs.station_id = s.station_id
  WHERE rs.route_id = %s
  ORDER BY rs.stop_sequence ASC;
  ```

---

## 3. Trips and Search Endpoints (`/api/trips`)

### 3.1 Trip Search Between Origin & Destination
- **Method & Route:** `GET /api/trips/search`
- **Access Role:** Public
- **Stored Procedure / Raw SQL:**
  ```sql
  CALL sp_search_trips(%s, %s, %s);
  ```
  *Fallback Multi-Table Join:*
  ```sql
  SELECT 
      tr.trip_id, s.service_number, s.service_name, s.service_type,
      r.route_code, r.route_name, tr.trip_date, tr.scheduled_departure,
      tr.scheduled_arrival, tr.status AS trip_status, tr.base_fare,
      st_orig.station_name AS origin_station_name,
      st_dest.station_name AS destination_station_name,
      COUNT(tsi.inventory_id) AS total_seats,
      SUM(CASE WHEN tsi.is_available = TRUE THEN 1 ELSE 0 END) AS available_seats
  FROM trips tr
  JOIN services s ON tr.service_id = s.service_id
  JOIN routes r ON tr.route_id = r.route_id
  JOIN route_stops rs_orig ON r.route_id = rs_orig.route_id
  JOIN stations st_orig ON rs_orig.station_id = st_orig.station_id
  JOIN route_stops rs_dest ON r.route_id = rs_dest.route_id
  JOIN stations st_dest ON rs_dest.station_id = st_dest.station_id
  LEFT JOIN trip_seat_inventory tsi ON tr.trip_id = tsi.trip_id
  WHERE st_orig.station_code = %s
    AND st_dest.station_code = %s
    AND rs_orig.stop_sequence < rs_dest.stop_sequence
    AND tr.trip_date = %s
    AND tr.status NOT IN ('CANCELLED', 'COMPLETED')
  GROUP BY 
      tr.trip_id, s.service_number, s.service_name, s.service_type,
      r.route_code, r.route_name, tr.trip_date, tr.scheduled_departure,
      tr.scheduled_arrival, tr.status, tr.base_fare,
      st_orig.station_name, st_dest.station_name
  ORDER BY tr.scheduled_departure ASC;
  ```

---

## 4. Concurrency Booking and Cancellation (`/api/bookings`, `/api/cancellations`)

### 4.1 Seat Map Inquiry
- **Method & Route:** `GET /api/bookings/trip/{trip_id}/seats`
- **Access Role:** Public
- **Raw SQL Operations:**
  ```sql
  SELECT s.seat_id, s.coach_number, s.seat_number, s.seat_class,
         s.seat_type, s.fare_multiplier, tsi.is_available
  FROM trip_seat_inventory tsi
  JOIN seats s ON tsi.seat_id = s.seat_id
  WHERE tsi.trip_id = %s
  ORDER BY s.coach_number ASC, s.seat_id ASC;
  ```

### 4.2 ACID Atomic Booking Transaction
- **Method & Route:** `POST /api/bookings`
- **Access Role:** Authenticated (`PASSENGER`, `STAFF`, `ADMIN`)
- **Transaction Flow:**
  ```sql
  START TRANSACTION;

  -- Step 1: Pessimistic Row Lock on Seat Inventory
  SELECT tsi.inventory_id, tsi.trip_id, tsi.seat_id, tsi.is_available,
         s.fare_multiplier, s.coach_number, s.seat_number, s.seat_class
  FROM trip_seat_inventory tsi
  JOIN seats s ON tsi.seat_id = s.seat_id
  WHERE tsi.trip_id = %s AND tsi.seat_id = %s
  FOR UPDATE;

  -- Step 2: Mark Seat Reserved
  UPDATE trip_seat_inventory
  SET is_available = FALSE, reserved_at = NOW()
  WHERE trip_id = %s AND seat_id = %s AND is_available = TRUE;

  -- Step 3: Insert Master Booking Header
  INSERT INTO bookings (
      booking_reference, user_id, trip_id,
      total_passengers, total_fare, booking_status
  ) VALUES (%s, %s, %s, %s, %s, 'CONFIRMED');

  -- Step 4: Insert Ticket Permits
  INSERT INTO tickets (
      booking_id, passenger_id, seat_id,
      origin_station_id, destination_station_id,
      ticket_number, fare_amount, ticket_status
  ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'CONFIRMED');

  -- Step 5: Insert Payment Receipt
  INSERT INTO payments (
      booking_id, transaction_reference,
      payment_method, amount, payment_status
  ) VALUES (%s, %s, %s, %s, 'SUCCESS');

  COMMIT;
  -- If any step fails: ROLLBACK;
  ```

### 4.3 Ticket Cancellation & Refund
- **Method & Route:** `POST /api/cancellations`
- **Access Role:** Authenticated Owner or `ADMIN`/`STAFF`
- **Raw SQL Operations:**
  ```sql
  START TRANSACTION;

  SELECT t.ticket_id, t.booking_id, t.passenger_id, t.seat_id,
         t.ticket_number, t.fare_amount, t.ticket_status, b.trip_id, b.user_id
  FROM tickets t
  JOIN bookings b ON t.booking_id = b.booking_id
  WHERE t.ticket_id = %s;

  -- Insert cancellation record (Triggers 'trg_cancellation_after_insert' in MySQL)
  INSERT INTO cancellations (
      booking_id, ticket_id, cancellation_reason,
      cancellation_fee, refund_amount, refund_status
  ) VALUES (%s, %s, %s, %s, %s, 'PROCESSED');

  -- Trigger automatically runs:
  -- 1. UPDATE tickets SET ticket_status = 'CANCELLED' WHERE ticket_id = NEW.ticket_id;
  -- 2. UPDATE trip_seat_inventory SET is_available = TRUE WHERE trip_id = v_trip_id AND seat_id = v_seat_id;
  -- 3. INSERT INTO audit_logs ...

  COMMIT;
  ```

---

## 5. Reports & Analytics Endpoints (`/api/reports`)

### 5.1 Route Performance
- **Method & Route:** `GET /api/reports/route-performance`
- **Access Role:** `ADMIN`, `STAFF`
- **Raw SQL:**
  ```sql
  SELECT route_id, route_code, route_name, total_distance_km,
         total_trips_scheduled, delayed_trips_count,
         total_passengers_booked, gross_revenue, total_refunds, net_revenue
  FROM v_route_performance
  ORDER BY net_revenue DESC;
  ```

### 5.2 Monthly Revenue Summary
- **Method & Route:** `GET /api/reports/monthly-revenue`
- **Access Role:** `ADMIN`, `STAFF`
- **Raw SQL:**
  ```sql
  SELECT revenue_month, route_code, route_name, service_type,
         total_bookings, confirmed_tickets, total_collected_amount,
         total_refund_amount, net_monthly_revenue
  FROM v_monthly_revenue
  ORDER BY revenue_month DESC, net_monthly_revenue DESC;
  ```

### 5.3 Delay Station Incident Summary
- **Method & Route:** `GET /api/reports/delay-summary`
- **Access Role:** `ADMIN`, `STAFF`
- **Raw SQL:**
  ```sql
  SELECT station_id, station_code, station_name, city,
         total_delay_incidents, avg_delay_minutes,
         max_delay_minutes, total_delay_minutes, primary_delay_reason
  FROM v_delay_summary;
  ```

---

## 6. Database Lab Endpoints (`/api/database-lab`)

### 6.1 Query Catalog
- **Method & Route:** `GET /api/database-lab/catalog`
- **Access Role:** `ADMIN`, `STAFF`
- **Description:** Returns metadata and raw SQL for all 21 advanced relational queries.

### 6.2 Execute Live Query & Inspection
- **Method & Route:** `GET /api/database-lab/execute/{query_id}`
- **Access Role:** `ADMIN`, `STAFF`
- **Raw SQL:** Executes the selected query (`Q01` - `Q21`) directly against MySQL, measures runtime, and runs `EXPLAIN <query>`.
