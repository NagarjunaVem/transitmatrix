-- Query 18: Transaction Control with Row-Level Locking and Commit
-- Business Question: Demonstrate end-to-end atomic reservation of a specific seat 
--                    using pessimistic locking (SELECT ... FOR UPDATE) and explicit COMMIT.
-- Concepts Demonstrated: START TRANSACTION, SELECT ... FOR UPDATE, UPDATE, INSERT, COMMIT.

USE transitmatrix;

-- Begin explicit atomic transaction
START TRANSACTION;

-- Step 1: Exclusive Row Lock on available seat in trip 1
SELECT inventory_id, trip_id, seat_id, is_available, lock_version
FROM trip_seat_inventory
WHERE trip_id = 1 
  AND seat_id = 1
  AND is_available = TRUE
FOR UPDATE;

-- Step 2: Mark seat as reserved
UPDATE trip_seat_inventory
SET is_available = FALSE,
    reserved_at = NOW(),
    lock_version = lock_version + 1
WHERE trip_id = 1 
  AND seat_id = 1
  AND is_available = TRUE;

-- Step 3: Insert master booking
INSERT INTO bookings (
    booking_reference,
    user_id,
    trip_id,
    booking_date,
    total_passengers,
    total_fare,
    booking_status
) VALUES (
    'TM-DEMO0001',
    8,
    1,
    NOW(),
    1,
    850.00,
    'CONFIRMED'
);

-- Step 4: Issue ticket
INSERT INTO tickets (
    booking_id,
    passenger_id,
    seat_id,
    origin_station_id,
    destination_station_id,
    ticket_number,
    fare_amount,
    ticket_status
) VALUES (
    LAST_INSERT_ID(),
    1,
    1,
    1,
    2,
    'TKT-DEMO-0001',
    850.00,
    'CONFIRMED'
);

-- Step 5: Settle payment
INSERT INTO payments (
    booking_id,
    transaction_reference,
    payment_method,
    amount,
    payment_status,
    paid_at
) VALUES (
    (SELECT booking_id FROM bookings WHERE booking_reference = 'TM-DEMO0001' LIMIT 1),
    'TXN-DEMO-0001',
    'UPI',
    850.00,
    'SUCCESS',
    NOW()
);

-- Step 6: Commit all changes atomically
COMMIT;

-- Verify results
SELECT b.booking_reference, b.booking_status, t.ticket_number, t.fare_amount, pay.payment_status
FROM bookings b
JOIN tickets t ON b.booking_id = t.booking_id
JOIN payments pay ON b.booking_id = pay.booking_id
WHERE b.booking_reference = 'TM-DEMO0001';

