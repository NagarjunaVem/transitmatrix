-- =============================================================================
-- Migration V6: ML Demand Predictions Support & View Alignment
-- Author: Person 4 (TransitMatrix AI/ML Engineer)
-- Description: Extends demand_predictions table with features_json column,
--              ensures index optimization for ML forecasting queries,
--              and guarantees analytical views support dual column aliases.
-- =============================================================================

USE transitmatrix;

-- 1. Add features_json column if it doesn't already exist
SET @col_exists = (
    SELECT COUNT(*) 
    FROM information_schema.COLUMNS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'demand_predictions' 
      AND COLUMN_NAME = 'features_json'
);

SET @alter_sql = IF(
    @col_exists = 0,
    'ALTER TABLE demand_predictions ADD COLUMN features_json JSON NULL AFTER model_version;',
    'SELECT "Column features_json already exists" AS notice;'
);

PREPARE stmt FROM @alter_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 2. Ensure index exists for efficient route-date lookup
SET @idx_exists = (
    SELECT COUNT(*) 
    FROM information_schema.STATISTICS 
    WHERE TABLE_SCHEMA = DATABASE() 
      AND TABLE_NAME = 'demand_predictions' 
      AND INDEX_NAME = 'idx_pred_route_date_model'
);

SET @idx_sql = IF(
    @idx_exists = 0,
    'CREATE INDEX idx_pred_route_date_model ON demand_predictions (route_id, prediction_date, model_version);',
    'SELECT "Index idx_pred_route_date_model already exists" AS notice;'
);

PREPARE stmt FROM @idx_sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- 3. Update v_trip_availability with both total_inventory_seats/total_class_capacity & occupancy_percentage/occupancy_pct
CREATE OR REPLACE VIEW v_trip_availability AS
SELECT 
    tr.trip_id,
    tr.trip_date,
    tr.scheduled_departure,
    tr.status AS trip_status,
    s.service_number,
    s.service_name,
    r.route_code,
    r.route_name,
    st.seat_class,
    COUNT(tsi.inventory_id) AS total_inventory_seats,
    COUNT(tsi.inventory_id) AS total_class_capacity,
    SUM(CASE WHEN tsi.is_available = TRUE THEN 1 ELSE 0 END) AS available_seats,
    SUM(CASE WHEN tsi.is_available = FALSE THEN 1 ELSE 0 END) AS reserved_seats,
    ROUND(
        (SUM(CASE WHEN tsi.is_available = FALSE THEN 1 ELSE 0 END) * 100.0) / 
        NULLIF(COUNT(tsi.inventory_id), 0), 2
    ) AS occupancy_percentage,
    ROUND(
        (SUM(CASE WHEN tsi.is_available = FALSE THEN 1 ELSE 0 END) * 100.0) / 
        NULLIF(COUNT(tsi.inventory_id), 0), 2
    ) AS occupancy_pct
FROM trips tr
JOIN services s ON tr.service_id = s.service_id
JOIN routes r ON tr.route_id = r.route_id
JOIN trip_seat_inventory tsi ON tr.trip_id = tsi.trip_id
JOIN seats st ON tsi.seat_id = st.seat_id
GROUP BY 
    tr.trip_id, tr.trip_date, tr.scheduled_departure, tr.status,
    s.service_number, s.service_name,
    r.route_code, r.route_name,
    st.seat_class;

-- 4. Update v_route_performance with both gross_revenue/total_gross_revenue & total_refunds/total_refunds_issued
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
    SUM(CASE WHEN tr.status = 'DELAYED' THEN 1 ELSE 0 END) AS delayed_trips_count,
    COALESCE(ROUND(AVG(d.delay_minutes), 1), 0.0) AS avg_delay_minutes,
    COUNT(DISTINCT t.ticket_id) AS total_tickets_sold,
    COUNT(DISTINCT t.passenger_id) AS total_passengers_booked,
    COALESCE(SUM(t.fare_amount), 0.00) AS total_gross_revenue,
    COALESCE(SUM(t.fare_amount), 0.00) AS gross_revenue,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds_issued,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds,
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

-- 5. Update v_monthly_revenue with both booking_month/revenue_month & net_revenue/net_monthly_revenue
CREATE OR REPLACE VIEW v_monthly_revenue AS
SELECT 
    DATE_FORMAT(b.booking_date, '%Y-%m') AS booking_month,
    DATE_FORMAT(b.booking_date, '%Y-%m') AS revenue_month,
    r.route_id,
    r.route_code,
    r.route_name,
    s.service_type,
    COUNT(DISTINCT b.booking_id) AS total_bookings_count,
    COUNT(DISTINCT b.booking_id) AS total_bookings,
    COUNT(DISTINCT t.ticket_id) AS total_tickets_issued,
    COUNT(DISTINCT CASE WHEN t.ticket_status <> 'CANCELLED' THEN t.ticket_id END) AS confirmed_tickets,
    COALESCE(SUM(b.total_fare), 0.00) AS gross_booking_amount,
    COALESCE(SUM(b.total_fare), 0.00) AS total_collected_amount,
    COALESCE(SUM(c.cancellation_fee), 0.00) AS total_cancellation_fees,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refund_amount,
    COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds,
    COALESCE(SUM(b.total_fare) - SUM(COALESCE(c.refund_amount, 0.00)), 0.00) AS net_revenue,
    COALESCE(SUM(b.total_fare) - SUM(COALESCE(c.refund_amount, 0.00)), 0.00) AS net_monthly_revenue
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
