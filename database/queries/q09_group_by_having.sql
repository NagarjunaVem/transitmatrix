-- Query 09: Aggregates with GROUP BY and HAVING Clause
-- Business Question: Identify stations that have accumulated at least 2 delay incidents 
--                    where the average delay duration exceeds 30 minutes.
-- Concepts Demonstrated: GROUP BY with HAVING filter on aggregated properties.

USE transitmatrix;

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
ORDER BY average_delay_minutes DESC, total_delay_incidents DESC;

