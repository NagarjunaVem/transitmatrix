# TransitMatrix - Database Normalization & Anomaly Analysis

## 1. Introduction to Normalization
Normalization is a systematic database design technique based on functional dependencies that minimizes data redundancy and avoids update, insertion, and deletion anomalies.

This document demonstrates the step-by-step normalization process for the TransitMatrix railway management system from an unnormalized universal relation down through First Normal Form (1NF), Second Normal Form (2NF), Third Normal Form (3NF), and Boyce-Codd Normal Form (BCNF).

---

## 2. The Unnormalized Universal Relation (UNF)
Consider a naive transit reservation relation where all trip, passenger, vehicle, station, and booking data are stored in a single flat table:

```text
UNNORMALIZED_RESERVATION(
    pnr_number,
    booking_date,
    user_email,
    user_name,
    passenger_names,          -- Multi-valued attribute (repeating group)
    passenger_ages,           -- Multi-valued attribute (repeating group)
    service_number,
    service_name,
    vehicle_number,
    coach_seat_list,          -- Multi-valued attribute
    trip_date,
    origin_station_code,
    origin_station_name,
    destination_station_code,
    destination_station_name,
    route_distance_km,
    fare_paid,
    payment_txn_ref
)
```

### 2.1 Anomalies in the Unnormalized Relation
1. **Insertion Anomaly:**
   - A new train service (e.g., service number `20901`, Vande Bharat) cannot be inserted into the system until a passenger makes a booking on it, because `pnr_number` is missing.
   - A new station cannot be added unless a route or trip passes through it.

2. **Deletion Anomaly:**
   - If the only booking for trip `TRIP-101` is cancelled and its tuple is deleted, we lose the information that service `12951` exists, what its route distance is, and which stations it connects.

3. **Update / Modification Anomaly:**
   - If the name of station `NDLS` changes from "New Delhi" to "New Delhi Central", every single booking record that references `NDLS` must be updated. If some rows are missed, the database enters an inconsistent state.

---

## 3. First Normal Form (1NF)

### 3.1 Definition
A relation $R$ is in First Normal Form (1NF) if and only if:
1. Every attribute domain contains only atomic (indivisible) values.
2. There are no repeating groups or multi-valued attributes.
3. Each record is uniquely identifiable by a primary key.

### 3.2 Conversion to 1NF
In `UNNORMALIZED_RESERVATION`, attributes `passenger_names`, `passenger_ages`, and `coach_seat_list` contain multi-valued lists (e.g., `{"Aman Sharma", "Riya Sharma"}`).

To satisfy 1NF, we flatten repeating groups so that each row represents exactly one passenger ticket per booking:

```text
FLAT_TICKET_RESERVATION_1NF(
    pnr_number,
    booking_date,
    user_email,
    user_name,
    passenger_name,
    passenger_age,
    passenger_id_num,
    service_number,
    service_name,
    vehicle_number,
    coach_number,
    seat_number,
    trip_date,
    origin_station_code,
    origin_station_name,
    destination_station_code,
    destination_station_name,
    route_distance_km,
    ticket_fare,
    payment_txn_ref
)
```

**Composite Candidate Key in 1NF:**
$$\{\text{pnr\_number}, \text{passenger\_id\_num}\}$$
or
$$\{\text{service\_number}, \text{trip\_date}, \text{coach\_number}, \text{seat\_number}\}$$

While `FLAT_TICKET_RESERVATION_1NF` satisfies 1NF, it contains massive redundancy and violates 2NF due to partial dependencies.

---

## 4. Second Normal Form (2NF)

### 4.1 Definition
A relation $R$ is in Second Normal Form (2NF) if:
1. It is in 1NF.
2. Every non-prime attribute is **fully functionally dependent** on every candidate key of $R$.
   - No non-prime attribute depends on a proper subset of any candidate key (i.e., **no partial functional dependencies**).

### 4.2 Identifying Partial Dependencies in 1NF
Consider candidate key $K = \{\text{pnr\_number}, \text{passenger\_id\_num}\}$:
- $\text{pnr\_number} \to \{\text{booking\_date}, \text{user\_email}, \text{user\_name}, \text{payment\_txn\_ref}\}$
  - `booking_date`, `user_email`, etc., depend only on part of the candidate key (`pnr_number`). This is a **partial dependency**.
- $\text{passenger\_id\_num} \to \{\text{passenger\_name}, \text{passenger\_age}\}$
  - `passenger_name` depends only on `passenger_id_num`. This is a **partial dependency**.

### 4.3 2NF Decomposition
We decompose the table into separate relations where every non-key attribute depends on the whole primary key:

1. `BOOKING_2NF(pnr_number, booking_date, user_email, user_name, service_number, trip_date, payment_txn_ref)`
2. `PASSENGER_2NF(passenger_id_num, passenger_name, passenger_age)`
3. `TICKET_2NF(pnr_number, passenger_id_num, coach_number, seat_number, ticket_fare)`
4. `SERVICE_ROUTE_2NF(service_number, trip_date, service_name, vehicle_number, origin_station_code, origin_station_name, destination_station_code, destination_station_name, route_distance_km)`

Now, all partial dependencies are eliminated. Each non-prime attribute is fully dependent on its table's primary key.

---

## 5. Third Normal Form (3NF)

### 5.1 Definition
A relation $R$ is in Third Normal Form (3NF) if:
1. It is in 2NF.
2. There are **no transitive dependencies** for non-prime attributes:
   - For every non-trivial functional dependency $X \to Y$, either:
     - $X$ is a superkey of $R$, OR
     - $Y$ is a prime attribute (part of a candidate key).

### 5.2 Identifying Transitive Dependencies in 2NF Tables
Examine `BOOKING_2NF`:
- $\text{pnr\_number} \to \text{user\_email}$ (since `pnr_number` is PK)
- $\text{user\_email} \to \text{user\_name}$ (user name depends on user email)
- Therefore, $\text{pnr\_number} \to \text{user\_name}$ is a **transitive dependency** through `user_email`.

Examine `SERVICE_ROUTE_2NF`:
- $\text{service\_number} \to \text{origin\_station\_code}$
- $\text{origin\_station\_code} \to \text{origin\_station\_name}$
- Therefore, $\text{service\_number} \to \text{origin\_station\_name}$ is a **transitive dependency** through `origin_station_code`.

### 5.3 3NF Decomposition
To remove transitive dependencies, non-prime attributes determined by non-candidate keys are extracted into dedicated relations:

1. `users(user_id, email, username, ...)`
2. `bookings(booking_id, pnr_number, user_id, trip_id, ...)`
3. `stations(station_id, station_code, station_name, city, state, ...)`
4. `routes(route_id, route_code, origin_station_id, destination_station_id, total_distance_km)`
5. `services(service_id, service_number, service_name, service_type)`
6. `trips(trip_id, service_id, route_id, vehicle_id, trip_date, ...)`

Now, in each relation, every non-prime attribute is determined directly by the candidate key, eliminating transitive dependencies.

---

## 6. Boyce-Codd Normal Form (BCNF)

### 6.1 Definition
A relation $R$ is in Boyce-Codd Normal Form (BCNF, strictly stronger than 3NF) if and only if:
- For every non-trivial functional dependency $X \to Y$, $X$ is a **superkey** of $R$.

In 3NF, the condition allowed $Y$ to be a prime attribute even if $X$ was not a superkey. BCNF removes this exception.

### 6.2 BCNF Analysis of TransitMatrix Relations

Let us verify BCNF compliance for key relations:

#### 1. Relation `route_stops`
- Attributes: `{stop_id, route_id, station_id, stop_sequence, distance_from_origin_km, ...}`
- Candidate Keys:
  - $K_1 = \{\text{stop\_id}\}$
  - $K_2 = \{\text{route\_id}, \text{stop\_sequence}\}$
  - $K_3 = \{\text{route\_id}, \text{station\_id}\}$
- Functional Dependencies:
  - $\{\text{stop\_id}\} \to \text{All other attributes}$ (Determinant is candidate key $K_1$)
  - $\{\text{route\_id}, \text{stop\_sequence}\} \to \text{All other attributes}$ (Determinant is candidate key $K_2$)
  - $\{\text{route\_id}, \text{station\_id}\} \to \text{All other attributes}$ (Determinant is candidate key $K_3$)
- **Conclusion:** Every determinant is a superkey. `route_stops` is in **BCNF**.

#### 2. Relation `seats`
- Attributes: `{seat_id, vehicle_id, coach_number, seat_number, seat_class, seat_type, fare_multiplier}`
- Candidate Keys:
  - $K_1 = \{\text{seat\_id}\}$
  - $K_2 = \{\text{vehicle\_id}, \text{coach\_number}, \text{seat\_number}\}$
- Functional Dependencies:
  - $\{\text{seat\_id}\} \to \text{All other attributes}$ (Determinant is candidate key $K_1$)
  - $\{\text{vehicle\_id}, \text{coach\_number}, \text{seat\_number}\} \to \text{All other attributes}$ (Determinant is candidate key $K_2$)
- **Conclusion:** Every determinant is a superkey. `seats` is in **BCNF**.

#### 3. Relation `trip_seat_inventory`
- Attributes: `{inventory_id, trip_id, seat_id, is_available, reserved_at, held_until, lock_version}`
- Candidate Keys:
  - $K_1 = \{\text{inventory\_id}\}$
  - $K_2 = \{\text{trip\_id}, \text{seat\_id}\}$
- Functional Dependencies:
  - $\{\text{inventory\_id}\} \to \{\text{trip\_id}, \text{seat\_id}, \text{is\_available}, \dots\}$
  - $\{\text{trip\_id}, \text{seat\_id}\} \to \{\text{inventory\_id}, \text{is\_available}, \dots\}$
- **Conclusion:** Determinants are superkeys. `trip_seat_inventory` is in **BCNF**.

#### 4. Relation `cancellations`
- Attributes: `{cancellation_id, booking_id, ticket_id, cancellation_reason, cancellation_fee, refund_amount, refund_status, cancelled_at}`
- Candidate Keys:
  - $K_1 = \{\text{cancellation\_id}\}$
  - $K_2 = \{\text{ticket\_id}\}$
- Functional Dependencies:
  - $\{\text{cancellation\_id}\} \to \text{All other attributes}$
  - $\{\text{ticket\_id}\} \to \text{All other attributes}$
- **Conclusion:** Both determinants are superkeys. `cancellations` is in **BCNF**.

---

## 7. Mathematical Proofs of Decomposition Quality

### 7.1 Lossless Join Property
A decomposition of relation $R$ into $R_1$ and $R_2$ is a **lossless-join decomposition** with respect to a set of functional dependencies $F$ if and only if at least one of the following functional dependencies is in the closure $F^+$:
1. $(R_1 \cap R_2) \to R_1$
2. $(R_1 \cap R_2) \to R_2$

#### Proof for Decomposition of Booking and Ticket:
- Let $R(\text{booking\_id}, \text{booking\_reference}, \text{user\_id}, \text{trip\_id}, \text{ticket\_id}, \text{passenger\_id}, \text{seat\_id}, \text{ticket\_fare})$
- Decomposed into:
  - $R_1 = \text{bookings}(\text{booking\_id}, \text{booking\_reference}, \text{user\_id}, \text{trip\_id})$
  - $R_2 = \text{tickets}(\text{ticket\_id}, \text{booking\_id}, \text{passenger\_id}, \text{seat\_id}, \text{ticket\_fare})$
- Intersection:
  $$R_1 \cap R_2 = \{\text{booking\_id}\}$$
- In $R_1$, $\text{booking\_id}$ is the primary key, which implies:
  $$\{\text{booking\_id}\} \to R_1$$
- Since $(R_1 \cap R_2) \to R_1$ holds, the natural join $R_1 \bowtie R_2$ reconstructs $R$ with zero spurious tuples.
- **Result:** The decomposition is **strictly lossless**.

---

### 7.2 Dependency Preservation
A decomposition $\{R_1, R_2, \dots, R_k\}$ is dependency preserving if:
$$(F_1 \cup F_2 \cup \dots \cup F_k)^+ = F^+$$
where $F_i = \pi_{R_i}(F)$.

In the TransitMatrix relational design:
- Every functional dependency identified in `docs/functional-dependencies.md` has all its determinant and dependent attributes situated entirely within a single relation.
- As a consequence, all constraints can be enforced locally by primary key and unique constraints inside individual tables, without needing cross-table assertions.
- **Result:** The database schema is **100% dependency preserving**.

---

## 8. Summary Comparison

| Normal Form | Requirement Satisfied | Status in TransitMatrix |
|---|---|---|
| **1NF** | Atomic attribute values, no repeating groups, unique primary keys | Satisfied |
| **2NF** | In 1NF, no partial functional dependencies | Satisfied |
| **3NF** | In 2NF, no transitive functional dependencies | Satisfied |
| **BCNF** | For every non-trivial $X \to Y$, $X$ is a superkey | Satisfied |

