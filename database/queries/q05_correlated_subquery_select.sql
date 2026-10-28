-- Query 05: Correlated Subquery in SELECT Clause
-- Business Question: Display each route with its base distance, total trips scheduled, 
--                    and a dynamically calculated count of delay incidents recorded on that route.
-- Concepts Demonstrated: Correlated subquery executing per outer relation row.

USE transitmatrix;

SELECT 
    r.route_id,
    r.route_code,
    r.route_name,
    r.total_distance_km,
    (
        SELECT COUNT(tr.trip_id)
        FROM trips tr
        WHERE tr.route_id = r.route_id
    ) AS total_trips,
    (
        SELECT COUNT(d.delay_id)
        FROM delays d
        JOIN trips tr ON d.trip_id = tr.trip_id
        WHERE tr.route_id = r.route_id
    ) AS total_delay_incidents,
    (
        SELECT COALESCE(ROUND(AVG(d.delay_minutes), 1), 0.0)
        FROM delays d
        JOIN trips tr ON d.trip_id = tr.trip_id
        WHERE tr.route_id = r.route_id
    ) AS avg_delay_minutes
FROM routes r
ORDER BY total_delay_incidents DESC, r.total_distance_km DESC;

