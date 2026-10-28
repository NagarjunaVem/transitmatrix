-- Query 17: Query Against Reporting View (v_route_performance)
-- Business Question: Evaluate routes with the lowest average delay minutes and highest net revenues.
-- Concepts Demonstrated: Querying aggregation view with custom ranking calculations.

USE transitmatrix;

SELECT 
    route_code,
    route_name,
    origin_station,
    destination_station,
    total_trips_scheduled,
    trips_completed,
    avg_delay_minutes,
    total_tickets_sold,
    total_gross_revenue,
    total_refunds_issued,
    net_revenue
FROM v_route_performance
ORDER BY net_revenue DESC, avg_delay_minutes ASC;

