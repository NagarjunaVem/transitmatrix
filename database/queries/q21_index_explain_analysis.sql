-- Query 21: Indexing Impact & Execution Plan Analysis
-- Business Question: Evaluate the query execution plan with EXPLAIN to demonstrate 
--                    index usage (range scan on idx_trips_route_date_status).
-- Concepts Demonstrated: EXPLAIN, EXPLAIN ANALYZE, B-Tree index lookup vs Table Scan.

USE transitmatrix;

-- Query 1: EXPLAIN on Trips Search Query
EXPLAIN
SELECT 
    tr.trip_id,
    tr.trip_date,
    tr.status,
    tr.base_fare
FROM trips tr
WHERE tr.route_id = 1
  AND tr.trip_date BETWEEN '2026-10-01' AND '2026-10-31'
  AND tr.status = 'SCHEDULED';

-- Query 2: EXPLAIN on Route Stops Sequence Join
EXPLAIN
SELECT 
    rs.route_id,
    rs.stop_sequence,
    st.station_name
FROM route_stops rs
JOIN stations st ON rs.station_id = st.station_id
WHERE rs.station_id = 1;

-- Query 3: EXPLAIN on Seat Inventory Availability Check
EXPLAIN
SELECT 
    inventory_id,
    trip_id,
    seat_id,
    is_available
FROM trip_seat_inventory
WHERE trip_id = 5
  AND is_available = TRUE;

