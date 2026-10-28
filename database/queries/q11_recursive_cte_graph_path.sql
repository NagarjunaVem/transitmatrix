-- Query 11: Recursive Common Table Expression (Graph Reachability)
-- Business Question: Find all stations reachable from New Delhi (NDLS, station_id = 1) 
--                    within 1 to 2 transit connections (hops), computing cumulative distance.
-- Concepts Demonstrated: WITH RECURSIVE, graph edge traversal, recursion termination condition.

USE transitmatrix;

WITH RECURSIVE StationTransitGraph AS (
    -- Anchor Member: Direct 1-hop routes starting at New Delhi (station_id = 1)
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
    
    -- Recursive Member: Connecting to adjacent routes from current destination
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
ORDER BY hop_count ASC, cumulative_distance_km ASC;

