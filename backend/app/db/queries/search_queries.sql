-- TransitMatrix: Trip Search Queries
-- File: backend/app/db/queries/search_queries.sql

-- Search trips between origin and destination on a given date with vacancy counts
SELECT 
    tr.trip_id,
    s.service_number,
    s.service_name,
    s.service_type,
    r.route_code,
    r.route_name,
    tr.trip_date,
    tr.scheduled_departure,
    tr.scheduled_arrival,
    tr.status AS trip_status,
    tr.base_fare,
    st_orig.station_name AS origin_station_name,
    st_dest.station_name AS destination_station_name,
    COUNT(tsi.inventory_id) AS total_seats,
    SUM(CASE WHEN tsi.is_available = TRUE THEN 1 ELSE 0 END) AS available_seats
FROM trips tr
JOIN services s ON tr.service_id = s.service_id
JOIN routes r ON tr.route_id = r.route_id
JOIN route_stops rs_orig ON r.route_id = rs_orig.route_id
JOIN stations st_orig ON rs_orig.station_id = st_orig.station_id
JOIN route_stops rs_dest ON r.route_id = rs_dest.route_id
JOIN stations st_dest ON rs_dest.station_id = st_dest.station_id
LEFT JOIN trip_seat_inventory tsi ON tr.trip_id = tsi.trip_id
WHERE st_orig.station_code = %s
  AND st_dest.station_code = %s
  AND rs_orig.stop_sequence < rs_dest.stop_sequence
  AND tr.trip_date = %s
  AND tr.status NOT IN ('CANCELLED', 'COMPLETED')
GROUP BY 
    tr.trip_id, s.service_number, s.service_name, s.service_type,
    r.route_code, r.route_name, tr.trip_date, tr.scheduled_departure,
    tr.scheduled_arrival, tr.status, tr.base_fare,
    st_orig.station_name, st_dest.station_name
ORDER BY tr.scheduled_departure ASC;
