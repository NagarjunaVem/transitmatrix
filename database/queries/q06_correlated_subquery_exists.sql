-- Query 06: Correlated Subquery with EXISTS
-- Business Question: Find all train services that have experienced at least one severe delay 
--                    incident exceeding 40 minutes.
-- Concepts Demonstrated: EXISTS predicate with correlated inner condition.

USE transitmatrix;

SELECT 
    s.service_id,
    s.service_number,
    s.service_name,
    s.service_type,
    s.operating_days
FROM services s
WHERE EXISTS (
    SELECT 1 
    FROM trips tr
    JOIN delays d ON tr.trip_id = d.trip_id
    WHERE tr.service_id = s.service_id
      AND d.delay_minutes >= 40
)
ORDER BY s.service_number ASC;

