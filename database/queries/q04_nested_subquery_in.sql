-- Query 04: Nested Subquery with IN Clause
-- Business Question: Identify passengers who have booked tickets on premium services 
--                    (VANDE_BHARAT or RAJDHANI services).
-- Concepts Demonstrated: IN operator with subquery projecting foreign key IDs.

USE transitmatrix;

SELECT 
    p.passenger_id,
    CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
    p.gender,
    p.age,
    p.id_card_type,
    p.email,
    p.phone_number
FROM passengers p
WHERE p.passenger_id IN (
    SELECT t.passenger_id
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    JOIN trips tr ON b.trip_id = tr.trip_id
    JOIN services s ON tr.service_id = s.service_id
    WHERE s.service_type IN ('VANDE_BHARAT', 'RAJDHANI')
      AND t.ticket_status = 'CONFIRMED'
)
ORDER BY p.first_name ASC, p.last_name ASC
LIMIT 30;

