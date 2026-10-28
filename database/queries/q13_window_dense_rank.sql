-- Query 13: Window Function - DENSE_RANK()
-- Business Question: Rank transit routes based on total gross revenue generated from bookings, 
--                    without skipping rank values for tied amounts.
-- Concepts Demonstrated: DENSE_RANK() OVER (ORDER BY ...).

USE transitmatrix;

SELECT 
    r.route_id,
    r.route_code,
    r.route_name,
    COUNT(b.booking_id) AS total_bookings,
    SUM(b.total_fare) AS total_revenue,
    DENSE_RANK() OVER (
        ORDER BY SUM(b.total_fare) DESC
    ) AS revenue_rank
FROM routes r
JOIN trips tr ON r.route_id = tr.route_id
JOIN bookings b ON tr.trip_id = b.trip_id
WHERE b.booking_status IN ('CONFIRMED', 'PARTIALLY_CANCELLED')
GROUP BY r.route_id, r.route_code, r.route_name
ORDER BY revenue_rank ASC;

