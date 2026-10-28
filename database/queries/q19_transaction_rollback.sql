-- Query 19: Transaction Rollback Demonstration (Atomicity & Error Recovery)
-- Business Question: Demonstrate transaction rollback when attempting to allocate an already-reserved 
--                    seat, verifying that partial inserts are completely undone.
-- Concepts Demonstrated: START TRANSACTION, validation check, ROLLBACK, database state unchanged.

USE transitmatrix;

-- Note initial counts
SELECT COUNT(*) AS initial_bookings_count FROM bookings;

-- Begin transaction attempt
START TRANSACTION;

-- Attempt to lock a seat that is already booked (or non-existent)
SET @req_trip_id = 1;
SET @req_seat_id = 1; -- previously reserved in Q18
SET @seat_is_free = 0;

SELECT is_available INTO @seat_is_free
FROM trip_seat_inventory
WHERE trip_id = @req_trip_id 
  AND seat_id = @req_seat_id
FOR UPDATE;

-- Simulating conditional application check
-- Because @seat_is_free = 0 (unavailable), we issue an intentional rollback
INSERT INTO bookings (
    booking_reference, user_id, trip_id, booking_date, total_passengers, total_fare, booking_status
) VALUES ('TM-FAIL0001', 8, 1, NOW(), 1, 999.00, 'PENDING');

-- Intentionally roll back to protect database consistency
ROLLBACK;

-- Verify that TM-FAIL0001 does not exist and count is identical to initial
SELECT COUNT(*) AS post_rollback_bookings_count FROM bookings;

SELECT * FROM bookings WHERE booking_reference = 'TM-FAIL0001';

