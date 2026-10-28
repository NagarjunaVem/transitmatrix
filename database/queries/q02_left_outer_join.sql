-- Query 02: Multi-Table Left Outer Join
-- Business Question: Identify all transit stations and determine how many routes originate 
--                    from each station, including terminal stations with no originating routes.
-- Concepts Demonstrated: LEFT OUTER JOIN, aggregation on NULLs, COALESCE.

USE transitmatrix;

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
ORDER BY originating_routes_count DESC, st.station_code ASC;

