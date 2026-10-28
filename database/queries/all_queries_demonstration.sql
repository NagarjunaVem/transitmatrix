-- =============================================================================
-- TransitMatrix: Master SQL Query Demonstrations (21 Advanced Queries)
-- Author: Person 1 (Database & SQL Engineer)
-- Covers: Joins, Subqueries, EXISTS, NOT EXISTS, Aggregates, GROUP BY, HAVING,
--         CTEs, Recursive CTEs, Window Functions, Views, Transactions,
--         Stored Procedures, Triggers, and EXPLAIN Query Plans.
-- =============================================================================

USE transitmatrix;

-- -----------------------------------------------------------------------------
-- Q01: Multi-Table Inner Join (8 tables)
-- -----------------------------------------------------------------------------
SELECT 
    b.booking_reference AS pnr_number,
    t.ticket_number,
    CONCAT(p.first_name, ' ', p.last_name) AS traveler_name,
    p.gender,
    p.age,
    s.service_number,
    s.service_name,
    s.service_type,
    st_orig.station_code AS from_station,
    st_dest.station_code AS to_station,
    tr.trip_date,
    tr.scheduled_departure,
    st.coach_number,
    st.seat_number,
    st.seat_class,
    t.fare_amount,
    b.booking_status
FROM bookings b
JOIN tickets t ON b.booking_id = t.booking_id
JOIN passengers p ON t.passenger_id = p.passenger_id
JOIN trips tr ON b.trip_id = tr.trip_id
JOIN services s ON tr.service_id = s.service_id
JOIN routes r ON tr.route_id = r.route_id
JOIN stations st_orig ON r.origin_station_id = st_orig.station_id
JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
JOIN seats st ON t.seat_id = st.seat_id
WHERE b.booking_status = 'CONFIRMED'
ORDER BY tr.trip_date ASC, s.service_number ASC, st.coach_number ASC, CAST(st.seat_number AS UNSIGNED) ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q02: Left Outer Join for Station Route Analysis
-- -----------------------------------------------------------------------------
SELECT 
    st.station_id,
    st.station_code,
    st.station_name,
    st.city,
    st.state,
    st.total_platforms,
    COUNT(r.route_id) AS originating_routes_count,
    COALESCE(GROUP_CONCAT(r.route_code ORDER BY r.route_code SEPARATOR ', '), 'None') AS departing_route_codes
FROM stations st
LEFT JOIN routes r ON st.station_id = r.origin_station_id
GROUP BY 
    st.station_id, st.station_code, st.station_name, 
    st.city, st.state, st.total_platforms
ORDER BY originating_routes_count DESC, st.station_code ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q03: Scalar Nested Subquery in WHERE Clause
-- -----------------------------------------------------------------------------
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
ORDER BY tr.base_fare DESC, tr.trip_date ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q04: Nested Subquery with IN Clause
-- -----------------------------------------------------------------------------
SELECT 
    p.passenger_id,
    CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
    p.gender,
    p.age,
    p.id_card_type,
    p.email
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
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q05: Correlated Subquery in SELECT Clause
-- -----------------------------------------------------------------------------
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
ORDER BY total_delay_incidents DESC, r.total_distance_km DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q06: Correlated Subquery with EXISTS
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- Q07: Correlated Subquery with NOT EXISTS
-- -----------------------------------------------------------------------------
SELECT 
    u.user_id,
    u.username,
    u.email,
    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
    u.phone_number
FROM users u
WHERE u.role = 'PASSENGER'
  AND NOT EXISTS (
      SELECT 1 
      FROM bookings b 
      WHERE b.user_id = u.user_id
  )
ORDER BY u.created_at ASC;

-- -----------------------------------------------------------------------------
-- Q08: Aggregate Functions with GROUP BY
-- -----------------------------------------------------------------------------
SELECT 
    s.service_type,
    COUNT(DISTINCT b.booking_id) AS total_bookings,
    COUNT(t.ticket_id) AS total_tickets_sold,
    ROUND(SUM(t.fare_amount), 2) AS total_revenue_collected,
    ROUND(AVG(t.fare_amount), 2) AS average_ticket_price
FROM services s
JOIN trips tr ON s.service_id = tr.service_id
JOIN bookings b ON tr.trip_id = b.trip_id
JOIN tickets t ON b.booking_id = t.booking_id
WHERE b.booking_status IN ('CONFIRMED', 'PARTIALLY_CANCELLED')
GROUP BY s.service_type
ORDER BY total_revenue_collected DESC;

-- -----------------------------------------------------------------------------
-- Q09: GROUP BY and HAVING Clause
-- -----------------------------------------------------------------------------
SELECT 
    st.station_id,
    st.station_code,
    st.station_name,
    st.city,
    st.state,
    COUNT(d.delay_id) AS total_delay_incidents,
    ROUND(AVG(d.delay_minutes), 1) AS average_delay_minutes,
    SUM(d.delay_minutes) AS total_lost_minutes
FROM stations st
JOIN delays d ON st.station_id = d.station_id
GROUP BY 
    st.station_id, st.station_code, st.station_name, 
    st.city, st.state
HAVING COUNT(d.delay_id) >= 2 
   AND AVG(d.delay_minutes) > 30.0
ORDER BY average_delay_minutes DESC;

-- -----------------------------------------------------------------------------
-- Q10: Common Table Expression (CTE)
-- -----------------------------------------------------------------------------
WITH RouteGrossRevenue AS (
    SELECT 
        tr.route_id,
        COUNT(t.ticket_id) AS tickets_sold,
        SUM(t.fare_amount) AS gross_amount
    FROM trips tr
    JOIN bookings b ON tr.trip_id = b.trip_id
    JOIN tickets t ON b.booking_id = t.booking_id
    GROUP BY tr.route_id
),
RouteRefunds AS (
    SELECT 
        tr.route_id,
        COUNT(c.cancellation_id) AS tickets_cancelled,
        COALESCE(SUM(c.refund_amount), 0.00) AS total_refunded,
        COALESCE(SUM(c.cancellation_fee), 0.00) AS fees_retained
    FROM trips tr
    JOIN bookings b ON tr.trip_id = b.trip_id
    JOIN tickets t ON b.booking_id = t.booking_id
    JOIN cancellations c ON t.ticket_id = c.ticket_id
    GROUP BY tr.route_id
)
SELECT 
    r.route_id,
    r.route_code,
    r.route_name,
    COALESCE(g.tickets_sold, 0) AS total_tickets_sold,
    COALESCE(rf.tickets_cancelled, 0) AS total_tickets_cancelled,
    COALESCE(g.gross_amount, 0.00) AS gross_revenue,
    COALESCE(rf.total_refunded, 0.00) AS refunds_paid,
    ROUND(COALESCE(g.gross_amount, 0.00) - COALESCE(rf.total_refunded, 0.00), 2) AS net_retained_revenue
FROM routes r
LEFT JOIN RouteGrossRevenue g ON r.route_id = g.route_id
LEFT JOIN RouteRefunds rf ON r.route_id = rf.route_id
ORDER BY net_retained_revenue DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q11: Recursive CTE Graph Search
-- -----------------------------------------------------------------------------
WITH RECURSIVE StationTransitGraph AS (
    SELECT 
        r.origin_station_id AS start_station_id,
        st_orig.station_code AS start_code,
        r.destination_station_id AS current_station_id,
        st_dest.station_code AS current_code,
        1 AS hop_count,
        CAST(CONCAT(st_orig.station_code, ' -> ', st_dest.station_code) AS CHAR(255)) AS full_path,
        r.total_distance_km AS cumulative_distance_km
    FROM routes r
    JOIN stations st_orig ON r.origin_station_id = st_orig.station_id
    JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
    WHERE r.origin_station_id = 1
    
    UNION ALL
    
    SELECT 
        g.start_station_id,
        g.start_code,
        next_r.destination_station_id,
        st_next.station_code,
        g.hop_count + 1,
        CAST(CONCAT(g.full_path, ' -> ', st_next.station_code) AS CHAR(255)),
        g.cumulative_distance_km + next_r.total_distance_km
    FROM StationTransitGraph g
    JOIN routes next_r ON g.current_station_id = next_r.origin_station_id
    JOIN stations st_next ON next_r.destination_station_id = st_next.station_id
    WHERE g.hop_count < 2
      AND next_r.destination_station_id <> g.start_station_id
)
SELECT 
    hop_count,
    start_code,
    current_code AS destination_code,
    full_path,
    cumulative_distance_km
FROM StationTransitGraph
ORDER BY hop_count ASC, cumulative_distance_km ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q12: Window Function - ROW_NUMBER()
-- -----------------------------------------------------------------------------
SELECT 
    tr.trip_id,
    s.service_number,
    st.coach_number,
    st.seat_number,
    st.seat_class,
    t.ticket_number,
    t.fare_amount,
    ROW_NUMBER() OVER (
        PARTITION BY tr.trip_id, st.seat_class 
        ORDER BY t.fare_amount DESC, t.ticket_id ASC
    ) AS class_ticket_rank
FROM tickets t
JOIN bookings b ON t.booking_id = b.booking_id
JOIN trips tr ON b.trip_id = tr.trip_id
JOIN services s ON tr.service_id = s.service_id
JOIN seats st ON t.seat_id = st.seat_id
WHERE t.ticket_status = 'CONFIRMED'
ORDER BY tr.trip_id ASC, st.seat_class ASC, class_ticket_rank ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q13: Window Function - DENSE_RANK()
-- -----------------------------------------------------------------------------
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
ORDER BY revenue_rank ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q14: Window Function - Cumulative Running Total
-- -----------------------------------------------------------------------------
WITH DailyRevenue AS (
    SELECT 
        DATE(booking_date) AS booking_day,
        COUNT(booking_id) AS bookings_count,
        SUM(total_fare) AS daily_fare_sum
    FROM bookings
    WHERE booking_status IN ('CONFIRMED', 'PARTIALLY_CANCELLED')
    GROUP BY DATE(booking_date)
)
SELECT 
    booking_day,
    bookings_count,
    daily_fare_sum,
    SUM(daily_fare_sum) OVER (
        ORDER BY booking_day ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_cumulative_revenue
FROM DailyRevenue
ORDER BY booking_day ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q15: Window Functions - LAG() and LEAD()
-- -----------------------------------------------------------------------------
SELECT 
    r.route_code,
    tr.trip_id,
    s.service_number,
    tr.scheduled_departure,
    LAG(tr.scheduled_departure, 1) OVER (
        PARTITION BY tr.route_id 
        ORDER BY tr.scheduled_departure ASC
    ) AS previous_train_departure,
    LEAD(tr.scheduled_departure, 1) OVER (
        PARTITION BY tr.route_id 
        ORDER BY tr.scheduled_departure ASC
    ) AS next_train_departure
FROM trips tr
JOIN routes r ON tr.route_id = r.route_id
JOIN services s ON tr.service_id = s.service_id
ORDER BY r.route_code ASC, tr.scheduled_departure ASC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q16: Query on View v_trip_availability
-- -----------------------------------------------------------------------------
SELECT 
    trip_id,
    trip_date,
    service_number,
    service_name,
    seat_class,
    total_inventory_seats,
    available_seats,
    reserved_seats,
    occupancy_percentage
FROM v_trip_availability
WHERE seat_class = '3A'
ORDER BY occupancy_percentage DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q17: Query on View v_route_performance
-- -----------------------------------------------------------------------------
SELECT 
    route_code,
    route_name,
    total_trips_scheduled,
    trips_completed,
    avg_delay_minutes,
    total_tickets_sold,
    net_revenue
FROM v_route_performance
ORDER BY net_revenue DESC
LIMIT 10;

-- -----------------------------------------------------------------------------
-- Q18: Transaction Demonstration with Locking and Commit
-- -----------------------------------------------------------------------------
START TRANSACTION;

SELECT inventory_id, trip_id, seat_id, is_available
FROM trip_seat_inventory
WHERE trip_id = 2 AND seat_id = 2 FOR UPDATE;

UPDATE trip_seat_inventory
SET is_available = FALSE, reserved_at = NOW(), lock_version = lock_version + 1
WHERE trip_id = 2 AND seat_id = 2 AND is_available = TRUE;

COMMIT;

-- -----------------------------------------------------------------------------
-- Q19: Transaction Rollback Demonstration
-- -----------------------------------------------------------------------------
START TRANSACTION;

INSERT INTO bookings (
    booking_reference, user_id, trip_id, booking_date, total_passengers, total_fare, booking_status
) VALUES ('TM-TESTFAIL', 8, 1, NOW(), 1, 999.00, 'PENDING');

ROLLBACK;

-- -----------------------------------------------------------------------------
-- Q20: Stored Procedure & Trigger Audit Verification
-- -----------------------------------------------------------------------------
CALL sp_search_trips('NDLS', 'BCT', '2026-10-01');

-- -----------------------------------------------------------------------------
-- Q21: EXPLAIN Query Plan Analysis
-- -----------------------------------------------------------------------------
EXPLAIN
SELECT tr.trip_id, tr.trip_date, tr.status
FROM trips tr
WHERE tr.route_id = 1
  AND tr.trip_date BETWEEN '2026-10-01' AND '2026-10-31'
  AND tr.status = 'SCHEDULED';

