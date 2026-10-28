# TransitMatrix - Transaction Concurrency, ACID Guarantees & Booking Contract

## 1. Purpose & Target Audience
This document specifies the database concurrency model, transaction boundaries, and isolation guarantees for the TransitMatrix system. It establishes the **binding schema contract** that Person 2 (Backend Engineer) and application developers must follow when implementing ticket reservations, seat inventory allocations, cancellations, and payment processing.

---

## 2. ACID Properties in TransitMatrix

### 2.1 Atomicity
- **Requirement:** A ticket booking consists of several steps:
  1. Verifying and locking seat inventory.
  2. Marking seats as unavailable (`is_available = FALSE`).
  3. Inserting the master `bookings` row.
  4. Inserting individual `tickets` rows.
  5. Generating payment receipts in `payments`.
- If any step fails (e.g., payment gateway rejection, network timeout, constraint violation), the database connection must issue an explicit `ROLLBACK`.
- No partial bookings or orphaned ticket records are ever committed.

### 2.2 Consistency
- Invariants enforced by MySQL database engine:
  - Referential integrity through foreign key constraints (`ON DELETE RESTRICT` or `CASCADE`).
  - Total passengers in `bookings` matches the count of child records in `tickets`.
  - Check constraints ensure `fare_amount >= 0` and `total_platforms >= 1`.
  - Seat inventory availability remains in a valid binary state (`TRUE` or `FALSE`).

### 2.3 Isolation
- Default MySQL InnoDB Isolation Level: **REPEATABLE READ**.
- For concurrent seat reservations, TransitMatrix enforces **Pessimistic Row-Level Locking** using `SELECT ... FOR UPDATE` on the `trip_seat_inventory` table.
- This prevents race conditions, dirty reads, non-repeatable reads, and phantom allocations without requiring full-table locks.

### 2.4 Durability
- Transaction commits write directly to MySQL Write-Ahead Logging (InnoDB Redo Log).
- Even during server power loss or container restarts, committed reservations are recovered intact from disk.

---

## 3. Concurrency Control Protocol: The Pessimistic Locking Sequence

### 3.1 Why Prior Read Is Insufficient
A naive application might execute:
1. `SELECT is_available FROM trip_seat_inventory WHERE trip_id = 1 AND seat_id = 10;`
2. If `is_available == True`, execute `UPDATE trip_seat_inventory SET is_available = FALSE ...`

Under high concurrency (e.g., two users booking the same seat at the same millisecond):
- User A reads `is_available = TRUE`.
- User B reads `is_available = TRUE`.
- Both attempt to update and book.
- Without database-level locking and constraints, both bookings succeed, creating a double-allocation catastrophe.

### 3.2 Canonical Booking Transaction Protocol (Contract for Person 2)

Person 2 MUST execute seat allocation using the following SQL protocol on a single connection:

```sql
-- Step 1: Begin an explicit transaction
START TRANSACTION;

-- Step 2: Acquire exclusive row lock on the requested seat inventory
SELECT inventory_id, trip_id, seat_id, is_available, lock_version
FROM trip_seat_inventory
WHERE trip_id = ? AND seat_id = ?
FOR UPDATE;

-- Step 3: Application check
-- If the row is not found or is_available is FALSE (0), raise error and ROLLBACK:
-- ROLLBACK;

-- Step 4: Reserve the seat atomically
UPDATE trip_seat_inventory
SET is_available = FALSE,
    reserved_at = NOW(),
    lock_version = lock_version + 1
WHERE trip_id = ?
  AND seat_id = ?
  AND is_available = TRUE;

-- Step 5: Verify affected row count
-- If cursor.rowcount != 1, concurrent collision occurred:
-- ROLLBACK;

-- Step 6: Insert booking record
INSERT INTO bookings (
    booking_reference, user_id, trip_id, booking_date,
    total_passengers, total_fare, booking_status
) VALUES (?, ?, ?, NOW(), ?, ?, 'CONFIRMED');

-- Step 7: Insert ticket record
INSERT INTO tickets (
    booking_id, passenger_id, seat_id,
    origin_station_id, destination_station_id,
    ticket_number, fare_amount, ticket_status
) VALUES (LAST_INSERT_ID(), ?, ?, ?, ?, ?, ?, 'CONFIRMED');

-- Step 8: Commit the transaction
COMMIT;
```

---

## 4. Multi-Layer Duplicate Booking Protection

TransitMatrix provides two independent defensive layers against duplicate seat bookings:

1. **Procedural Layer (Row Locks):**
   `SELECT ... FOR UPDATE` acquires an exclusive `X` lock on the specific index record in `trip_seat_inventory`. Any concurrent thread requesting the same row is blocked until the first transaction issues `COMMIT` or `ROLLBACK`.

2. **Schema Constraint Layer (Unique Index):**
   The table `trip_seat_inventory` defines:
   ```sql
   UNIQUE KEY uq_trip_seat (trip_id, seat_id)
   ```
   Furthermore, the application updates `is_available = TRUE` with predicate condition `is_available = TRUE`. If two transactions race past the lock, the second update matches 0 rows, triggering immediate failure and rollback.

---

## 5. Deadlock Avoidance Strategy

Deadlocks can occur when two transactions acquire locks in reverse orders (e.g., Transaction 1 locks Seat 10 then Seat 11; Transaction 2 locks Seat 11 then Seat 10).

To prevent deadlocks during multi-seat bookings (e.g., booking a group of 4 tickets):
1. **Sorted Lock Acquisition:**
   Person 2 MUST always sort `seat_id` values in ascending numerical order before issuing the `FOR UPDATE` query:
   ```sql
   SELECT seat_id, is_available
   FROM trip_seat_inventory
   WHERE trip_id = ? AND seat_id IN (?, ?, ?)
   ORDER BY seat_id ASC
   FOR UPDATE;
   ```
2. **Short Transaction Life Cycles:**
   Keep the transaction duration short. External operations (e.g., calling third-party payment gateways, sending SMS/emails) must NOT be executed inside the open database transaction lock window.

---

## 6. Waitlist and Cancellation Invariant Contract

1. **Cancellation Flow:**
   When a booking or ticket is cancelled:
   - Calculate refund amount based on time remaining before departure.
   - Update `tickets.ticket_status = 'CANCELLED'`.
   - Insert row into `cancellations`.
   - Check if an active waitlist entry exists for the same `(trip_id, seat_class)`.
   - If a waitlist entry exists:
     - Assign the freed `seat_id` to the top-ranked waitlisted passenger.
     - Update waitlist status to `'CONFIRMED'`.
   - If no waitlist entry exists:
     - Update `trip_seat_inventory.is_available = TRUE` and clear `reserved_at`.

2. **Stored Procedures Provided:**
   Person 2 may call the documented MySQL stored procedures directly:
   - `sp_create_atomic_booking(...)`
   - `sp_cancel_booking(...)`
   - `sp_process_waitlist_promotion(...)`

