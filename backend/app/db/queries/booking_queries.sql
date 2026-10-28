-- TransitMatrix: Booking and Concurrency Queries
-- File: backend/app/db/queries/booking_queries.sql

-- 1. Pessimistic Row Lock on Seat Inventory
SELECT tsi.inventory_id, tsi.trip_id, tsi.seat_id, tsi.is_available,
       s.fare_multiplier, s.coach_number, s.seat_number, s.seat_class
FROM trip_seat_inventory tsi
JOIN seats s ON tsi.seat_id = s.seat_id
WHERE tsi.trip_id = %s AND tsi.seat_id = %s
FOR UPDATE;

-- 2. Reserve Seat
UPDATE trip_seat_inventory
SET is_available = FALSE, reserved_at = NOW()
WHERE trip_id = %s AND seat_id = %s AND is_available = TRUE;

-- 3. Release Seat
UPDATE trip_seat_inventory
SET is_available = TRUE, reserved_at = NULL
WHERE trip_id = %s AND seat_id = %s;

-- 4. Insert Master Booking Header
INSERT INTO bookings (
    booking_reference, user_id, trip_id,
    total_passengers, total_fare, booking_status
) VALUES (%s, %s, %s, %s, %s, %s);

-- 5. Insert Ticket Allocation
INSERT INTO tickets (
    booking_id, passenger_id, seat_id,
    origin_station_id, destination_station_id,
    ticket_number, fare_amount, ticket_status
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);

-- 6. Insert Settlement Payment
INSERT INTO payments (
    booking_id, transaction_reference,
    payment_method, amount, payment_status
) VALUES (%s, %s, %s, %s, %s);
