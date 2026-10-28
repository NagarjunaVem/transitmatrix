# TransitMatrix - Functional Dependencies Analysis

## 1. Introduction to Functional Dependencies
A functional dependency (FD) is a constraint between two sets of attributes in a relational database. Given a relation $R$, a set of attributes $X \subseteq R$ functionally determines another set $Y \subseteq R$ (denoted $X \to Y$) if and only if each $X$-value in $R$ is associated with exactly one $Y$-value in $R$.

Formally:
$$\forall t_1, t_2 \in R, \quad t_1[X] = t_2[X] \implies t_1[Y] = t_2[Y]$$

Below, we document the minimal set of non-trivial functional dependencies for each relation in the TransitMatrix database, along with candidate key proofs via attribute closures $X^+$.

---

## 2. Functional Dependencies per Relation

### 2.1 Relation `users`
**Attributes:** `{user_id, username, email, password_hash, role, first_name, last_name, phone_number, is_active, created_at, updated_at}`

- $FD_1: \{\text{user\_id}\} \to \{\text{username}, \text{email}, \text{password\_hash}, \text{role}, \text{first\_name}, \text{last\_name}, \text{phone\_number}, \text{is\_active}, \text{created\_at}, \text{updated\_at}\}$
- $FD_2: \{\text{username}\} \to \{\text{user\_id}, \text{email}, \text{password\_hash}, \text{role}, \text{first\_name}, \text{last\_name}, \text{phone\_number}, \text{is\_active}, \text{created\_at}, \text{updated\_at}\}$
- $FD_3: \{\text{email}\} \to \{\text{user\_id}, \text{username}, \text{password\_hash}, \text{role}, \text{first\_name}, \text{last\_name}, \text{phone\_number}, \text{is\_active}, \text{created\_at}, \text{updated\_at}\}$
- $FD_4: \{\text{phone\_number}\} \to \{\text{user\_id}, \text{username}, \text{email}, \text{password\_hash}, \text{role}, \text{first\_name}, \text{last\_name}, \text{is\_active}, \text{created\_at}, \text{updated\_at}\}$

**Candidate Keys:**
- $\{\text{user\_id}\}^+ = \text{All attributes}$
- $\{\text{username}\}^+ = \text{All attributes}$
- $\{\text{email}\}^+ = \text{All attributes}$
- $\{\text{phone\_number}\}^+ = \text{All attributes}$

---

### 2.2 Relation `passengers`
**Attributes:** `{passenger_id, user_id, first_name, last_name, gender, age, id_card_type, id_card_number, email, phone_number, created_at, updated_at}`

- $FD_1: \{\text{passenger\_id}\} \to \{\text{user\_id}, \text{first\_name}, \text{last\_name}, \text{gender}, \text{age}, \text{id\_card\_type}, \text{id\_card\_number}, \text{email}, \text{phone\_number}, \text{created\_at}, \text{updated\_at}\}$
- $FD_2: \{\text{id\_card\_type}, \text{id\_card\_number}\} \to \{\text{passenger\_id}, \text{user\_id}, \text{first\_name}, \text{last\_name}, \text{gender}, \text{age}, \text{email}, \text{phone\_number}, \text{created\_at}, \text{updated\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{passenger\_id}\}$
- Alternate Key: $\{\text{id\_card\_type}, \text{id\_card\_number}\}$

---

### 2.3 Relation `stations`
**Attributes:** `{station_id, station_code, station_name, city, state, zone, total_platforms, latitude, longitude, is_active, created_at}`

- $FD_1: \{\text{station\_id}\} \to \{\text{station\_code}, \text{station\_name}, \text{city}, \text{state}, \text{zone}, \text{total\_platforms}, \text{latitude}, \text{longitude}, \text{is\_active}, \text{created\_at}\}$
- $FD_2: \{\text{station\_code}\} \to \{\text{station\_id}, \text{station\_name}, \text{city}, \text{state}, \text{zone}, \text{total\_platforms}, \text{latitude}, \text{longitude}, \text{is\_active}, \text{created\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{station\_id}\}$
- Alternate Key: $\{\text{station\_code}\}$

---

### 2.4 Relation `routes`
**Attributes:** `{route_id, route_code, route_name, origin_station_id, destination_station_id, total_distance_km, duration_est_minutes, is_active, created_at}`

- $FD_1: \{\text{route\_id}\} \to \{\text{route\_code}, \text{route\_name}, \text{origin\_station\_id}, \text{destination\_station\_id}, \text{total\_distance\_km}, \text{duration\_est\_minutes}, \text{is\_active}, \text{created\_at}\}$
- $FD_2: \{\text{route\_code}\} \to \{\text{route\_id}, \text{route\_name}, \text{origin\_station\_id}, \text{destination\_station\_id}, \text{total\_distance\_km}, \text{duration\_est\_minutes}, \text{is\_active}, \text{created\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{route\_id}\}$
- Alternate Key: $\{\text{route\_code}\}$

---

### 2.5 Relation `route_stops`
**Attributes:** `{stop_id, route_id, station_id, stop_sequence, distance_from_origin_km, departure_offset_minutes, arrival_offset_minutes, halt_duration_minutes, platform_number}`

- $FD_1: \{\text{stop\_id}\} \to \{\text{route\_id}, \text{station\_id}, \text{stop\_sequence}, \text{distance\_from\_origin\_km}, \text{departure\_offset\_minutes}, \text{arrival\_offset\_minutes}, \text{halt\_duration\_minutes}, \text{platform\_number}\}$
- $FD_2: \{\text{route\_id}, \text{stop\_sequence}\} \to \{\text{stop\_id}, \text{station\_id}, \text{distance\_from\_origin\_km}, \text{departure\_offset\_minutes}, \text{arrival\_offset\_minutes}, \text{halt\_duration\_minutes}, \text{platform\_number}\}$
- $FD_3: \{\text{route\_id}, \text{station\_id}\} \to \{\text{stop\_id}, \text{stop\_sequence}, \text{distance\_from\_origin\_km}, \text{departure\_offset\_minutes}, \text{arrival\_offset\_minutes}, \text{halt\_duration\_minutes}, \text{platform\_number}\}$

**Candidate Keys:**
- Primary Key: $\{\text{stop\_id}\}$
- Alternate Candidate Keys: $\{\text{route\_id}, \text{stop\_sequence}\}$, $\{\text{route\_id}, \text{station\_id}\}$

---

### 2.6 Relation `services`
**Attributes:** `{service_id, service_number, service_name, service_type, operating_days, is_active, created_at}`

- $FD_1: \{\text{service\_id}\} \to \{\text{service\_number}, \text{service\_name}, \text{service\_type}, \text{operating\_days}, \text{is\_active}, \text{created\_at}\}$
- $FD_2: \{\text{service\_number}\} \to \{\text{service\_id}, \text{service\_name}, \text{service\_type}, \text{operating\_days}, \text{is\_active}, \text{created\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{service\_id}\}$
- Alternate Key: $\{\text{service\_number}\}$

---

### 2.7 Relation `vehicles`
**Attributes:** `{vehicle_id, vehicle_number, vehicle_type, model_name, manufacture_year, total_coaches, total_capacity, maintenance_status, created_at}`

- $FD_1: \{\text{vehicle\_id}\} \to \{\text{vehicle\_number}, \text{vehicle\_type}, \text{model\_name}, \text{manufacture\_year}, \text{total\_coaches}, \text{total\_capacity}, \text{maintenance\_status}, \text{created\_at}\}$
- $FD_2: \{\text{vehicle\_number}\} \to \{\text{vehicle\_id}, \text{vehicle\_type}, \text{model\_name}, \text{manufacture\_year}, \text{total\_coaches}, \text{total\_capacity}, \text{maintenance\_status}, \text{created\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{vehicle\_id}\}$
- Alternate Key: $\{\text{vehicle\_number}\}$

---

### 2.8 Relation `seats`
**Attributes:** `{seat_id, vehicle_id, coach_number, seat_number, seat_class, seat_type, fare_multiplier}`

- $FD_1: \{\text{seat\_id}\} \to \{\text{vehicle\_id}, \text{coach\_number}, \text{seat\_number}, \text{seat\_class}, \text{seat\_type}, \text{fare\_multiplier}\}$
- $FD_2: \{\text{vehicle\_id}, \text{coach\_number}, \text{seat\_number}\} \to \{\text{seat\_id}, \text{seat\_class}, \text{seat\_type}, \text{fare\_multiplier}\}$

**Candidate Keys:**
- Primary Key: $\{\text{seat\_id}\}$
- Alternate Candidate Key: $\{\text{vehicle\_id}, \text{coach\_number}, \text{seat\_number}\}$

---

### 2.9 Relation `trips`
**Attributes:** `{trip_id, service_id, route_id, vehicle_id, trip_date, scheduled_departure, scheduled_arrival, actual_departure, actual_arrival, status, base_fare, created_at, updated_at}`

- $FD_1: \{\text{trip\_id}\} \to \{\text{service\_id}, \text{route\_id}, \text{vehicle\_id}, \text{trip\_date}, \text{scheduled\_departure}, \text{scheduled\_arrival}, \text{actual\_departure}, \text{actual\_arrival}, \text{status}, \text{base\_fare}, \text{created\_at}, \text{updated\_at}\}$
- $FD_2: \{\text{service\_id}, \text{trip\_date}\} \to \{\text{trip\_id}, \text{route\_id}, \text{vehicle\_id}, \text{scheduled\_departure}, \text{scheduled\_arrival}, \text{actual\_departure}, \text{actual\_arrival}, \text{status}, \text{base\_fare}, \text{created\_at}, \text{updated\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{trip\_id}\}$
- Alternate Candidate Key: $\{\text{service\_id}, \text{trip\_date}\}$

---

### 2.10 Relation `trip_seat_inventory`
**Attributes:** `{inventory_id, trip_id, seat_id, is_available, reserved_at, held_until, lock_version}`

- $FD_1: \{\text{inventory\_id}\} \to \{\text{trip\_id}, \text{seat\_id}, \text{is\_available}, \text{reserved\_at}, \text{held\_until}, \text{lock\_version}\}$
- $FD_2: \{\text{trip\_id}, \text{seat\_id}\} \to \{\text{inventory\_id}, \text{is\_available}, \text{reserved\_at}, \text{held\_until}, \text{lock\_version}\}$

**Candidate Keys:**
- Primary Key: $\{\text{inventory\_id}\}$
- Alternate Candidate Key: $\{\text{trip\_id}, \text{seat\_id}\}$

---

### 2.11 Relation `bookings`
**Attributes:** `{booking_id, booking_reference, user_id, trip_id, booking_date, total_passengers, total_fare, booking_status, created_at, updated_at}`

- $FD_1: \{\text{booking\_id}\} \to \{\text{booking\_reference}, \text{user\_id}, \text{trip\_id}, \text{booking\_date}, \text{total\_passengers}, \text{total\_fare}, \text{booking\_status}, \text{created\_at}, \text{updated\_at}\}$
- $FD_2: \{\text{booking\_reference}\} \to \{\text{booking\_id}, \text{user\_id}, \text{trip\_id}, \text{booking\_date}, \text{total\_passengers}, \text{total\_fare}, \text{booking\_status}, \text{created\_at}, \text{updated\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{booking\_id}\}$
- Alternate Key: $\{\text{booking\_reference}\}$

---

### 2.12 Relation `tickets`
**Attributes:** `{ticket_id, booking_id, passenger_id, seat_id, origin_station_id, destination_station_id, ticket_number, fare_amount, ticket_status, created_at, updated_at}`

- $FD_1: \{\text{ticket\_id}\} \to \{\text{booking\_id}, \text{passenger\_id}, \text{seat\_id}, \text{origin\_station\_id}, \text{destination\_station\_id}, \text{ticket\_number}, \text{fare\_amount}, \text{ticket\_status}, \text{created\_at}, \text{updated\_at}\}$
- $FD_2: \{\text{ticket\_number}\} \to \{\text{ticket\_id}, \text{booking\_id}, \text{passenger\_id}, \text{seat\_id}, \text{origin\_station\_id}, \text{destination\_station\_id}, \text{fare\_amount}, \text{ticket\_status}, \text{created\_at}, \text{updated\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{ticket\_id}\}$
- Alternate Key: $\{\text{ticket\_number}\}$

---

### 2.13 Relation `payments`
**Attributes:** `{payment_id, booking_id, transaction_reference, payment_method, amount, payment_status, paid_at}`

- $FD_1: \{\text{payment\_id}\} \to \{\text{booking\_id}, \text{transaction\_reference}, \text{payment\_method}, \text{amount}, \text{payment\_status}, \text{paid\_at}\}$
- $FD_2: \{\text{transaction\_reference}\} \to \{\text{payment\_id}, \text{booking\_id}, \text{payment\_method}, \text{amount}, \text{payment\_status}, \text{paid\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{payment\_id}\}$
- Alternate Key: $\{\text{transaction\_reference}\}$

---

### 2.14 Relation `cancellations`
**Attributes:** `{cancellation_id, booking_id, ticket_id, cancellation_reason, cancellation_fee, refund_amount, refund_status, cancelled_at}`

- $FD_1: \{\text{cancellation\_id}\} \to \{\text{booking\_id}, \text{ticket\_id}, \text{cancellation\_reason}, \text{cancellation\_fee}, \text{refund\_amount}, \text{refund\_status}, \text{cancelled\_at}\}$
- $FD_2: \{\text{ticket\_id}\} \to \{\text{cancellation\_id}, \text{booking\_id}, \text{cancellation\_reason}, \text{cancellation\_fee}, \text{refund\_amount}, \text{refund\_status}, \text{cancelled\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{cancellation\_id}\}$
- Alternate Key: $\{\text{ticket\_id}\}$ (A single ticket is cancelled at most once)

---

### 2.15 Relation `waitlists`
**Attributes:** `{waitlist_id, trip_id, passenger_id, booking_id, seat_class, waitlist_number, status, created_at, updated_at}`

- $FD_1: \{\text{waitlist\_id}\} \to \{\text{trip\_id}, \text{passenger\_id}, \text{booking\_id}, \text{seat\_class}, \text{waitlist\_number}, \text{status}, \text{created\_at}, \text{updated\_at}\}$
- $FD_2: \{\text{trip\_id}, \text{seat\_class}, \text{waitlist\_number}\} \to \{\text{waitlist\_id}, \text{passenger\_id}, \text{booking\_id}, \text{status}, \text{created\_at}, \text{updated\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{waitlist\_id}\}$
- Alternate Candidate Key: $\{\text{trip\_id}, \text{seat\_class}, \text{waitlist\_number}\}$

---

### 2.16 Relation `delays`
**Attributes:** `{delay_id, trip_id, station_id, delay_minutes, delay_reason, remarks, recorded_at}`

- $FD_1: \{\text{delay\_id}\} \to \{\text{trip\_id}, \text{station\_id}, \text{delay\_minutes}, \text{delay\_reason}, \text{remarks}, \text{recorded\_at}\}$

**Candidate Key:**
- Primary Key: $\{\text{delay\_id}\}$

---

### 2.17 Relation `audit_logs`
**Attributes:** `{log_id, table_name, record_id, action, old_values, new_values, changed_by, changed_at}`

- $FD_1: \{\text{log\_id}\} \to \{\text{table\_name}, \text{record\_id}, \text{action}, \text{old\_values}, \text{new\_values}, \text{changed\_by}, \text{changed\_at}\}$

**Candidate Key:**
- Primary Key: $\{\text{log\_id}\}$

---

### 2.18 Relation `demand_predictions`
**Attributes:** `{prediction_id, route_id, prediction_date, predicted_passenger_demand, confidence_lower_bound, confidence_upper_bound, model_name, model_version, generated_at}`

- $FD_1: \{\text{prediction\_id}\} \to \{\text{route\_id}, \text{prediction\_date}, \text{predicted\_passenger\_demand}, \text{confidence\_lower\_bound}, \text{confidence\_upper\_bound}, \text{model\_name}, \text{model\_version}, \text{generated\_at}\}$
- $FD_2: \{\text{route\_id}, \text{prediction\_date}, \text{model\_version}\} \to \{\text{prediction\_id}, \text{predicted\_passenger\_demand}, \text{confidence\_lower\_bound}, \text{confidence\_upper\_bound}, \text{model\_name}, \text{generated\_at}\}$

**Candidate Keys:**
- Primary Key: $\{\text{prediction\_id}\}$
- Alternate Candidate Key: $\{\text{route\_id}, \text{prediction\_date}, \text{model\_version}\}$

---

## 3. Summary of Determinants and Closure Verification
For all relations $R$ in the TransitMatrix schema, every non-trivial functional dependency $X \to Y$ has a determinant $X$ that is a superkey of $R$. This property directly establishes that each relation satisfies Boyce-Codd Normal Form (BCNF), eliminating redundancy and update anomalies.

