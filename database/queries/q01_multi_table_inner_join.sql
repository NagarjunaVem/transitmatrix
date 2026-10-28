-- Query 01: Multi-Table Inner Join
-- Business Question: Retrieve complete passenger manifest with journey details, coach, seat, 
--                    route stations, service brand, and booking reference.
-- Concepts Demonstrated: Inner joins across 8 tables (bookings, tickets, passengers, trips,
--                        services, routes, stations, seats).

USE transitmatrix;

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
LIMIT 25;

