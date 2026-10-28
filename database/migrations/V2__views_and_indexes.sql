-- =============================================================================
-- Migration V2: Database Views and Query-Driven Performance Indexes
-- Author: Person 1 (Database & SQL Engineer)
-- Description: Creates reporting views and B-Tree indexes for TransitMatrix
-- =============================================================================

-- -----------------------------------------------------------------------------
-- Views
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_booking_details AS
SELECT 
    b.booking_id,
    b.booking_reference,
    b.booking_date,
    b.booking_status,
    u.user_id,
    u.username,
    u.email AS user_email,
    CONCAT(u.first_name, ' ', u.last_name) AS booked_by,
    t.ticket_id,
    t.ticket_number,
    t.ticket_status,
    p.passenger_id,
    CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
    p.gender AS passenger_gender,
    p.age AS passenger_age,
    p.id_card_type,
    p.id_card_number,
    s.service_number,
    s.service_name,
    s.service_type,
    tr.trip_id,
    tr.trip_date,
    tr.scheduled_departure,
    tr.scheduled_arrival,
    st_orig.station_code AS origin_station_code,
    st_orig.station_name AS origin_station_name,
    st_dest.station_code AS destination_station_code,
    st_dest.station_name AS destination_station_name,
    v.vehicle_number,
    st.coach_number,
    st.seat_number,
    st.seat_class,
    st.seat_type,
    t.fare_amount,
    pay.transaction_reference,
    pay.payment_method,
    pay.payment_status
FROM bookings b
JOIN users u ON b.user_id = u.user_id
JOIN trips tr ON b.trip_id = tr.trip_id
JOIN services s ON tr.service_id = s.service_id
JOIN tickets t ON b.booking_id = t.booking_id
JOIN passengers p ON t.passenger_id = p.passenger_id
JOIN stations st_orig ON t.origin_station_id = st_orig.station_id
JOIN stations st_dest ON t.destination_station_id = st_dest.station_id
LEFT JOIN seats st ON t.seat_id = st.seat_id
LEFT JOIN vehicles v ON st.vehicle_id = v.vehicle_id
LEFT JOIN payments pay ON b.booking_id = pay.booking_id;

CREATE OR REPLACE VIEW v_trip_availability AS
SELECT 
    tr.trip_id,
    tr.trip_date,
    tr.status AS trip_status,
    s.service_number,
    s.service_name,
    r.route_code,
    r.route_name,
    st.seat_class,
    COUNT(tsi.inventory_id) AS total_inventory_seats,
    SUM(CASE WHEN tsi.is_available = TRUE THEN 1 ELSE 0 END) AS available_seats,
    SUM(CASE WHEN tsi.is_available = FALSE THEN 1 ELSE 0 END) AS reserved_seats,
    ROUND(
        (SUM(CASE WHEN tsi.is_available = FALSE THEN 1 ELSE 0 END) * 100.0) / 
        NULLIF(COUNT(tsi.inventory_id), 0), 2
    ) AS occupancy_percentage
FROM trips tr
JOIN services s ON tr.service_id = s.service_id
JOIN routes r ON tr.route_id = r.route_id
JOIN trip_seat_inventory tsi ON tr.trip_id = tsi.trip_id
JOIN seats st ON tsi.seat_id = st.seat_id
GROUP BY 
    tr.trip_id, tr.trip_date, tr.status,
    s.service_number, s.service_name,
    r.route_code, r.route_name,
    st.seat_class;

CREATE OR REPLACE VIEW v_route_performance AS
SELECT 
    r.route_id,
    r.route_code,
    r.route_name,
    st_orig.station_name AS origin_station,
    st_dest.station_name AS destination_station,
    r.total_distance_km,
    COUNT(DISTINCT tr.trip_id) AS total_trips_scheduled,
    SUM(CASE WHEN tr.status = 'COMPLETED' THEN 1 ELSE 0 END) AS trips_completed,
    SUM(CASE WHEN tr.status = 'CANCELLED' THEN 1 ELSE 0 END) AS trips_cancelled,
    COALESCE(ROUND(AVG(d.delay_minutes), 1), 0.0) AS avg_delay_minutes,
    COUNT(DISTINCT t.ticket_id) AS total_tickets_sold,
    COALESCE(SUM(t.fare_amount), 0.00) AS total_gross_revenue,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds_issued,
    COALESCE(SUM(t.fare_amount) - SUM(COALESCE(c.refund_amount, 0.00)), 0.00) AS net_revenue
FROM routes r
JOIN stations st_orig ON r.origin_station_id = st_orig.station_id
JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
LEFT JOIN trips tr ON r.route_id = tr.route_id
LEFT JOIN delays d ON tr.trip_id = d.trip_id
LEFT JOIN tickets t ON tr.trip_id = (SELECT b_sub.trip_id FROM bookings b_sub WHERE b_sub.booking_id = t.booking_id LIMIT 1)
LEFT JOIN cancellations c ON t.ticket_id = c.ticket_id
GROUP BY 
    r.route_id, r.route_code, r.route_name,
    st_orig.station_name, st_dest.station_name,
    r.total_distance_km;

CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    DATE_FORMAT(b.booking_date, '%Y-%m') AS booking_month,
    r.route_id,
    r.route_code,
    r.route_name,
    s.service_type,
    COUNT(DISTINCT b.booking_id) AS total_bookings_count,
    COUNT(DISTINCT t.ticket_id) AS total_tickets_issued,
    COALESCE(SUM(b.total_fare), 0.00) AS gross_booking_amount,
    COALESCE(SUM(c.cancellation_fee), 0.00) AS total_cancellation_fees,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refund_amount,
    COALESCE(SUM(b.total_fare) - SUM(COALESCE(c.refund_amount, 0.00)), 0.00) AS net_revenue
FROM bookings b
JOIN trips tr ON b.trip_id = tr.trip_id
JOIN routes r ON tr.route_id = r.route_id
JOIN services s ON tr.service_id = s.service_id
LEFT JOIN tickets t ON b.booking_id = t.booking_id
LEFT JOIN cancellations c ON t.ticket_id = c.ticket_id
WHERE b.booking_status IN ('CONFIRMED', 'CANCELLED', 'PARTIALLY_CANCELLED')
GROUP BY 
    DATE_FORMAT(b.booking_date, '%Y-%m'),
    r.route_id, r.route_code, r.route_name,
    s.service_type;

CREATE OR REPLACE VIEW v_delay_summary AS
SELECT 
    st.station_id,
    st.station_code,
    st.station_name,
    st.city,
    st.state,
    d.delay_reason,
    COUNT(d.delay_id) AS total_delay_incidents,
    ROUND(AVG(d.delay_minutes), 1) AS avg_delay_minutes,
    MIN(d.delay_minutes) AS min_delay_minutes,
    MAX(d.delay_minutes) AS max_delay_minutes,
    SUM(d.delay_minutes) AS total_delay_minutes_lost
FROM delays d
JOIN stations st ON d.station_id = st.station_id
GROUP BY 
    st.station_id, st.station_code, st.station_name,
    st.city, st.state, d.delay_reason;

CREATE OR REPLACE VIEW v_passenger_travel_history AS
SELECT 
    p.passenger_id,
    CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
    p.id_card_type,
    p.id_card_number,
    b.booking_reference,
    t.ticket_number,
    t.ticket_status,
    t.fare_amount,
    s.service_number,
    s.service_name,
    tr.trip_date,
    tr.scheduled_departure,
    tr.scheduled_arrival,
    st_orig.station_name AS origin_station,
    st_dest.station_name AS destination_station,
    st.coach_number,
    st.seat_number,
    st.seat_class
FROM passengers p
JOIN tickets t ON p.passenger_id = t.passenger_id
JOIN bookings b ON t.booking_id = b.booking_id
JOIN trips tr ON b.trip_id = tr.trip_id
JOIN services s ON tr.service_id = s.service_id
JOIN stations st_orig ON t.origin_station_id = st_orig.station_id
JOIN stations st_dest ON t.destination_station_id = st_dest.station_id
LEFT JOIN seats st ON t.seat_id = st.seat_id;

-- -----------------------------------------------------------------------------
-- Secondary Indexes
-- -----------------------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_trips_route_date_status ON trips (route_id, trip_date, status);
CREATE INDEX IF NOT EXISTS idx_inventory_trip_avail ON trip_seat_inventory (trip_id, is_available);
CREATE INDEX IF NOT EXISTS idx_route_stops_station_seq ON route_stops (station_id, route_id, stop_sequence);
CREATE INDEX IF NOT EXISTS idx_bookings_user_date ON bookings (user_id, booking_date DESC);
CREATE INDEX IF NOT EXISTS idx_tickets_booking_id ON tickets (booking_id);
CREATE INDEX IF NOT EXISTS idx_tickets_passenger_status ON tickets (passenger_id, ticket_status);
CREATE INDEX IF NOT EXISTS idx_payments_booking_status ON payments (booking_id, payment_status);
CREATE INDEX IF NOT EXISTS idx_waitlists_queue_search ON waitlists (trip_id, seat_class, status, waitlist_number ASC);
CREATE INDEX IF NOT EXISTS idx_delays_trip_recorded ON delays (trip_id, recorded_at);
CREATE INDEX IF NOT EXISTS idx_predictions_route_date ON demand_predictions (route_id, prediction_date);
CREATE INDEX IF NOT EXISTS idx_audit_table_record ON audit_logs (table_name, record_id, changed_at DESC);

