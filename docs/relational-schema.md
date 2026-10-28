# TransitMatrix - Relational Schema Specification

## 1. Relational Database Notation
In relational database theory, a schema is represented as:
$$R(A_1, A_2, \dots, A_n)$$
where $R$ is the relation name, and $A_i$ are attributes.
- **Underline**: Denotes Primary Key (PK).
- **Dashed underline / [AK]**: Denotes Alternate / Candidate Key.
- **Italics / [FK]**: Denotes Foreign Key.

---

## 2. Table Specifications

### 2.1 Relation: `users`
Represents registered user accounts for administrative, counter, and passenger interactions.

```text
users(
    user_id [PK],
    username [AK],
    email [AK],
    password_hash,
    role,
    first_name,
    last_name,
    phone_number [AK],
    is_active,
    created_at,
    updated_at
)
```

- **Primary Key:** `user_id` (INT AUTO_INCREMENT)
- **Candidate Keys:** `username` (VARCHAR(50)), `email` (VARCHAR(100)), `phone_number` (VARCHAR(20))
- **Attributes & Domain Constraints:**
  - `role`: ENUM('ADMIN', 'STAFF', 'PASSENGER') DEFAULT 'PASSENGER'
  - `is_active`: BOOLEAN DEFAULT TRUE
  - `password_hash`: VARCHAR(255) NOT NULL

---

### 2.2 Relation: `passengers`
Passenger profiles containing traveler identification required by railway regulations.

```text
passengers(
    passenger_id [PK],
    user_id [FK],
    first_name,
    last_name,
    gender,
    age,
    id_card_type,
    id_card_number,
    email,
    phone_number,
    created_at,
    updated_at
)
```

- **Primary Key:** `passenger_id` (INT AUTO_INCREMENT)
- **Foreign Key:** `user_id` REFERENCES `users(user_id)` ON UPDATE CASCADE ON DELETE SET NULL
- **Check Constraints:**
  - `CHECK (age >= 1 AND age <= 120)`
- **Domain Constraints:**
  - `gender`: ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL
  - `id_card_type`: ENUM('AADHAAR', 'PASSPORT', 'PAN', 'VOTER_ID', 'DRIVING_LICENSE') NOT NULL

---

### 2.3 Relation: `stations`
Physical transit stations and railway terminals.

```text
stations(
    station_id [PK],
    station_code [AK],
    station_name,
    city,
    state,
    zone,
    total_platforms,
    latitude,
    longitude,
    is_active,
    created_at
)
```

- **Primary Key:** `station_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `station_code` (VARCHAR(10) UNIQUE)
- **Check Constraints:**
  - `CHECK (total_platforms >= 1)`
  - `CHECK (latitude BETWEEN -90.0 AND 90.0)`
  - `CHECK (longitude BETWEEN -180.0 AND 180.0)`

---

### 2.4 Relation: `routes`
Transit corridor connecting an origin station and a destination station.

```text
routes(
    route_id [PK],
    route_code [AK],
    route_name,
    origin_station_id [FK],
    destination_station_id [FK],
    total_distance_km,
    duration_est_minutes,
    is_active,
    created_at
)
```

- **Primary Key:** `route_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `route_code` (VARCHAR(20) UNIQUE)
- **Foreign Keys:**
  - `origin_station_id` REFERENCES `stations(station_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `destination_station_id` REFERENCES `stations(station_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Check Constraints:**
  - `CHECK (origin_station_id <> destination_station_id)`
  - `CHECK (total_distance_km > 0)`
  - `CHECK (duration_est_minutes > 0)`

---

### 2.5 Relation: `route_stops`
Intermediate halts along a route in strictly indexed order.

```text
route_stops(
    stop_id [PK],
    route_id [FK],
    station_id [FK],
    stop_sequence,
    distance_from_origin_km,
    departure_offset_minutes,
    arrival_offset_minutes,
    halt_duration_minutes,
    platform_number
)
```

- **Primary Key:** `stop_id` (INT AUTO_INCREMENT)
- **Candidate Keys (Composite):**
  - `(route_id, stop_sequence)` UNIQUE
  - `(route_id, station_id)` UNIQUE
- **Foreign Keys:**
  - `route_id` REFERENCES `routes(route_id)` ON UPDATE CASCADE ON DELETE CASCADE
  - `station_id` REFERENCES `stations(station_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Check Constraints:**
  - `CHECK (stop_sequence >= 1)`
  - `CHECK (distance_from_origin_km >= 0)`
  - `CHECK (halt_duration_minutes >= 0)`

---

### 2.6 Relation: `services`
Catalog of operational train services.

```text
services(
    service_id [PK],
    service_number [AK],
    service_name,
    service_type,
    operating_days,
    is_active,
    created_at
)
```

- **Primary Key:** `service_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `service_number` (VARCHAR(20) UNIQUE)
- **Domain Constraints:**
  - `service_type`: ENUM('RAJDHANI', 'SHATABDI', 'VANDE_BHARAT', 'SUPERFAST', 'EXPRESS', 'INTERCITY', 'SUBURBAN')

---

### 2.7 Relation: `vehicles`
Physical rakes / locomotives deployed for trips.

```text
vehicles(
    vehicle_id [PK],
    vehicle_number [AK],
    vehicle_type,
    model_name,
    manufacture_year,
    total_coaches,
    total_capacity,
    maintenance_status,
    created_at
)
```

- **Primary Key:** `vehicle_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `vehicle_number` (VARCHAR(30) UNIQUE)
- **Domain Constraints:**
  - `vehicle_type`: ENUM('LOCOMOTIVE_TRAIN', 'ELECTRIC_MULTIPLE_UNIT', 'METRO_RAIL', 'DIESEL_MULTIPLE_UNIT')
  - `maintenance_status`: ENUM('OPERATIONAL', 'UNDER_MAINTENANCE', 'DECOMMISSIONED') DEFAULT 'OPERATIONAL'
- **Check Constraints:**
  - `CHECK (total_coaches >= 1)`
  - `CHECK (total_capacity >= 1)`
  - `CHECK (manufacture_year >= 1990)`

---

### 2.8 Relation: `seats`
Individual physical seats within a vehicle's coach.

```text
seats(
    seat_id [PK],
    vehicle_id [FK],
    coach_number,
    seat_number,
    seat_class,
    seat_type,
    fare_multiplier
)
```

- **Primary Key:** `seat_id` (INT AUTO_INCREMENT)
- **Candidate Key (Composite):** `(vehicle_id, coach_number, seat_number)` UNIQUE
- **Foreign Key:** `vehicle_id` REFERENCES `vehicles(vehicle_id)` ON UPDATE CASCADE ON DELETE CASCADE
- **Domain Constraints:**
  - `seat_class`: ENUM('1A', '2A', '3A', 'SL', 'CC', 'EC', 'GEN')
  - `seat_type`: ENUM('LOWER', 'MIDDLE', 'UPPER', 'SIDE_LOWER', 'SIDE_UPPER', 'WINDOW', 'AISLE')
- **Check Constraints:**
  - `CHECK (fare_multiplier > 0.0)`

---

### 2.9 Relation: `trips`
Scheduled instance of a service running on a specific date along a route.

```text
trips(
    trip_id [PK],
    service_id [FK],
    route_id [FK],
    vehicle_id [FK],
    trip_date,
    scheduled_departure,
    scheduled_arrival,
    actual_departure,
    actual_arrival,
    status,
    base_fare,
    created_at,
    updated_at
)
```

- **Primary Key:** `trip_id` (INT AUTO_INCREMENT)
- **Candidate Key (Composite):** `(service_id, trip_date)` UNIQUE
- **Foreign Keys:**
  - `service_id` REFERENCES `services(service_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `route_id` REFERENCES `routes(route_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `vehicle_id` REFERENCES `vehicles(vehicle_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Domain Constraints:**
  - `status`: ENUM('SCHEDULED', 'BOARDING', 'ON_TIME', 'DELAYED', 'CANCELLED', 'COMPLETED') DEFAULT 'SCHEDULED'
- **Check Constraints:**
  - `CHECK (scheduled_arrival > scheduled_departure)`
  - `CHECK (base_fare > 0.0)`

---

### 2.10 Relation: `trip_seat_inventory`
Granular per-trip seat availability tracking record enabling row-level locking.

```text
trip_seat_inventory(
    inventory_id [PK],
    trip_id [FK],
    seat_id [FK],
    is_available,
    reserved_at,
    held_until,
    lock_version
)
```

- **Primary Key:** `inventory_id` (INT AUTO_INCREMENT)
- **Candidate Key (Composite):** `(trip_id, seat_id)` UNIQUE
- **Foreign Keys:**
  - `trip_id` REFERENCES `trips(trip_id)` ON UPDATE CASCADE ON DELETE CASCADE
  - `seat_id` REFERENCES `seats(seat_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Integrity Rule:** `(trip_id, seat_id)` uniqueness guarantees that no two transactions can allocate the same seat on the same trip.

---

### 2.11 Relation: `bookings`
Parent reservation record.

```text
bookings(
    booking_id [PK],
    booking_reference [AK],
    user_id [FK],
    trip_id [FK],
    booking_date,
    total_passengers,
    total_fare,
    booking_status,
    created_at,
    updated_at
)
```

- **Primary Key:** `booking_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `booking_reference` (VARCHAR(12) UNIQUE, PNR format: TM-XXXXXXXX)
- **Foreign Keys:**
  - `user_id` REFERENCES `users(user_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `trip_id` REFERENCES `trips(trip_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Domain Constraints:**
  - `booking_status`: ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'PARTIALLY_CANCELLED', 'WAITLISTED') DEFAULT 'PENDING'
- **Check Constraints:**
  - `CHECK (total_passengers >= 1)`
  - `CHECK (total_fare >= 0.0)`

---

### 2.12 Relation: `tickets`
Individual passenger travel coupon under a booking.

```text
tickets(
    ticket_id [PK],
    booking_id [FK],
    passenger_id [FK],
    seat_id [FK],
    origin_station_id [FK],
    destination_station_id [FK],
    ticket_number [AK],
    fare_amount,
    ticket_status,
    created_at,
    updated_at
)
```

- **Primary Key:** `ticket_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `ticket_number` (VARCHAR(25) UNIQUE)
- **Foreign Keys:**
  - `booking_id` REFERENCES `bookings(booking_id)` ON UPDATE CASCADE ON DELETE CASCADE
  - `passenger_id` REFERENCES `passengers(passenger_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `seat_id` REFERENCES `seats(seat_id)` ON UPDATE CASCADE ON DELETE SET NULL
  - `origin_station_id` REFERENCES `stations(station_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `destination_station_id` REFERENCES `stations(station_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Domain Constraints:**
  - `ticket_status`: ENUM('CONFIRMED', 'CANCELLED', 'WAITLISTED', 'RAC') DEFAULT 'CONFIRMED'
- **Check Constraints:**
  - `CHECK (fare_amount >= 0.0)`

---

### 2.13 Relation: `payments`
Financial transaction receipt for a booking.

```text
payments(
    payment_id [PK],
    booking_id [FK],
    transaction_reference [AK],
    payment_method,
    amount,
    payment_status,
    paid_at
)
```

- **Primary Key:** `payment_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `transaction_reference` (VARCHAR(64) UNIQUE)
- **Foreign Key:** `booking_id` REFERENCES `bookings(booking_id)` ON UPDATE CASCADE ON DELETE CASCADE
- **Domain Constraints:**
  - `payment_method`: ENUM('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING', 'WALLET')
  - `payment_status`: ENUM('SUCCESS', 'FAILED', 'REFUNDED', 'PENDING') DEFAULT 'PENDING'
- **Check Constraints:**
  - `CHECK (amount > 0.0)`

---

### 2.14 Relation: `cancellations`
Cancellation record for calculating refunds and releasing inventory.

```text
cancellations(
    cancellation_id [PK],
    booking_id [FK],
    ticket_id [FK],
    cancellation_reason,
    cancellation_fee,
    refund_amount,
    refund_status,
    cancelled_at
)
```

- **Primary Key:** `cancellation_id` (INT AUTO_INCREMENT)
- **Candidate Key:** `ticket_id` (UNIQUE, one cancellation entry per ticket)
- **Foreign Keys:**
  - `booking_id` REFERENCES `bookings(booking_id)` ON UPDATE CASCADE ON DELETE CASCADE
  - `ticket_id` REFERENCES `tickets(ticket_id)` ON UPDATE CASCADE ON DELETE CASCADE
- **Check Constraints:**
  - `CHECK (cancellation_fee >= 0.0)`
  - `CHECK (refund_amount >= 0.0)`

---

### 2.15 Relation: `waitlists`
Queue for travelers awaiting seat vacancy.

```text
waitlists(
    waitlist_id [PK],
    trip_id [FK],
    passenger_id [FK],
    booking_id [FK],
    seat_class,
    waitlist_number,
    status,
    created_at,
    updated_at
)
```

- **Primary Key:** `waitlist_id` (INT AUTO_INCREMENT)
- **Candidate Key (Composite):** `(trip_id, seat_class, waitlist_number)` UNIQUE
- **Foreign Keys:**
  - `trip_id` REFERENCES `trips(trip_id)` ON UPDATE CASCADE ON DELETE CASCADE
  - `passenger_id` REFERENCES `passengers(passenger_id)` ON UPDATE CASCADE ON DELETE RESTRICT
  - `booking_id` REFERENCES `bookings(booking_id)` ON UPDATE CASCADE ON DELETE CASCADE
- **Check Constraints:**
  - `CHECK (waitlist_number >= 1)`

---

### 2.16 Relation: `delays`
Operational tracking of delayed trips at stations.

```text
delays(
    delay_id [PK],
    trip_id [FK],
    station_id [FK],
    delay_minutes,
    delay_reason,
    remarks,
    recorded_at
)
```

- **Primary Key:** `delay_id` (INT AUTO_INCREMENT)
- **Foreign Keys:**
  - `trip_id` REFERENCES `trips(trip_id)` ON UPDATE CASCADE ON DELETE CASCADE
  - `station_id` REFERENCES `stations(station_id)` ON UPDATE CASCADE ON DELETE RESTRICT
- **Check Constraints:**
  - `CHECK (delay_minutes >= 0)`

---

### 2.17 Relation: `audit_logs`
Security and administrative change tracking table.

```text
audit_logs(
    log_id [PK],
    table_name,
    record_id,
    action,
    old_values,
    new_values,
    changed_by,
    changed_at
)
```

- **Primary Key:** `log_id` (BIGINT AUTO_INCREMENT)
- **Attributes:**
  - `action`: ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL
  - `old_values`: JSON
  - `new_values`: JSON

---

### 2.18 Relation: `demand_predictions`
Outputs from the machine learning forecasting pipeline.

```text
demand_predictions(
    prediction_id [PK],
    route_id [FK],
    prediction_date,
    predicted_passenger_demand,
    confidence_lower_bound,
    confidence_upper_bound,
    model_name,
    model_version,
    generated_at
)
```

- **Primary Key:** `prediction_id` (INT AUTO_INCREMENT)
- **Candidate Key (Composite):** `(route_id, prediction_date, model_version)` UNIQUE
- **Foreign Key:** `route_id` REFERENCES `routes(route_id)` ON UPDATE CASCADE ON DELETE CASCADE
- **Check Constraints:**
  - `CHECK (predicted_passenger_demand >= 0)`
  - `CHECK (confidence_lower_bound >= 0)`
  - `CHECK (confidence_upper_bound >= confidence_lower_bound)`

