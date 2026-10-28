-- Query 12: Window Function - ROW_NUMBER()
-- Business Question: Rank tickets issued within each trip partitioned by coach class, 
--                    ordered by fare paid.
-- Concepts Demonstrated: ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...).

USE transitmatrix;

SELECT 
    tr.trip_id,
    s.service_number,
    s.service_name,
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
LIMIT 30;

