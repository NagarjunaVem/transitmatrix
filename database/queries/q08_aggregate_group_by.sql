-- Query 08: Aggregate Functions with GROUP BY
-- Business Question: Summarize booking volumes, total ticket counts, total gross fare collected, 
--                    and average fare per ticket grouped by service type.
-- Concepts Demonstrated: COUNT(), SUM(), AVG(), ROUND(), GROUP BY.

USE transitmatrix;

SELECT 
    s.service_type,
    COUNT(DISTINCT b.booking_id) AS total_bookings,
    COUNT(t.ticket_id) AS total_tickets_sold,
    ROUND(SUM(t.fare_amount), 2) AS total_revenue_collected,
    ROUND(AVG(t.fare_amount), 2) AS average_ticket_price,
    ROUND(MIN(t.fare_amount), 2) AS minimum_fare_paid,
    ROUND(MAX(t.fare_amount), 2) AS maximum_fare_paid
FROM services s
JOIN trips tr ON s.service_id = tr.service_id
JOIN bookings b ON tr.trip_id = b.trip_id
JOIN tickets t ON b.booking_id = t.booking_id
WHERE b.booking_status IN ('CONFIRMED', 'PARTIALLY_CANCELLED')
GROUP BY s.service_type
ORDER BY total_revenue_collected DESC;

