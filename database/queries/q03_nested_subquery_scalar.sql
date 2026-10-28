-- Query 03: Nested Subquery in WHERE Clause (Scalar Subquery)
-- Business Question: Find trips whose base fare is higher than the overall average base fare 
--                    of all trips in the entire transit network.
-- Concepts Demonstrated: Scalar subquery evaluation in WHERE clause.

USE transitmatrix;

SELECT 
    tr.trip_id,
    s.service_number,
    s.service_name,
    s.service_type,
    r.route_name,
    tr.trip_date,
    tr.base_fare,
    ROUND((SELECT AVG(base_fare) FROM trips), 2) AS network_avg_fare,
    ROUND(tr.base_fare - (SELECT AVG(base_fare) FROM trips), 2) AS premium_difference
FROM trips tr
JOIN services s ON tr.service_id = s.service_id
JOIN routes r ON tr.route_id = r.route_id
WHERE tr.base_fare > (SELECT AVG(base_fare) FROM trips)
ORDER BY tr.base_fare DESC, tr.trip_date ASC;

