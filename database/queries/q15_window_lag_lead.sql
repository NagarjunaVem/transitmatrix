-- Query 15: Window Functions - LAG() and LEAD()
-- Business Question: On each route, analyze consecutive trip departures to compute 
--                    time elapsed since the previous train and time until the next train.
-- Concepts Demonstrated: LAG() and LEAD() analytic functions with TIMESTAMPDIFF.

USE transitmatrix;

SELECT 
    r.route_code,
    r.route_name,
    tr.trip_id,
    s.service_number,
    s.service_name,
    tr.trip_date,
    tr.scheduled_departure,
    LAG(tr.scheduled_departure, 1) OVER (
        PARTITION BY tr.route_id 
        ORDER BY tr.scheduled_departure ASC
    ) AS previous_train_departure,
    TIMESTAMPDIFF(
        HOUR,
        LAG(tr.scheduled_departure, 1) OVER (PARTITION BY tr.route_id ORDER BY tr.scheduled_departure ASC),
        tr.scheduled_departure
    ) AS hours_since_previous_train,
    LEAD(tr.scheduled_departure, 1) OVER (
        PARTITION BY tr.route_id 
        ORDER BY tr.scheduled_departure ASC
    ) AS next_train_departure
FROM trips tr
JOIN routes r ON tr.route_id = r.route_id
JOIN services s ON tr.service_id = s.service_id
ORDER BY r.route_code ASC, tr.scheduled_departure ASC
LIMIT 30;

