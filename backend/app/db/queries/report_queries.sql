-- TransitMatrix: Reporting Views Queries
-- File: backend/app/db/queries/report_queries.sql

-- Route commercial KPI summary
SELECT route_id, route_code, route_name, total_distance_km,
       total_trips_scheduled, delayed_trips_count,
       total_passengers_booked, gross_revenue, total_refunds, net_revenue
FROM v_route_performance
ORDER BY net_revenue DESC;

-- Monthly corridor revenue breakdown
SELECT revenue_month, route_code, route_name, service_type,
       total_bookings, confirmed_tickets, total_collected_amount,
       total_refund_amount, net_monthly_revenue
FROM v_monthly_revenue
ORDER BY revenue_month DESC, net_monthly_revenue DESC;

-- Class-level trip occupancy and availability
SELECT trip_id, service_number, service_name, route_code,
       trip_date, scheduled_departure, trip_status,
       seat_class, total_class_capacity, available_seats,
       reserved_seats, occupancy_pct
FROM v_trip_availability
ORDER BY trip_date ASC, trip_id ASC;

-- Station delay incident summary
SELECT station_id, station_code, station_name, city,
       total_delay_incidents, avg_delay_minutes,
       max_delay_minutes, total_delay_minutes, primary_delay_reason
FROM v_delay_summary;
