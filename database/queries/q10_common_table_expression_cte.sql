-- Query 10: Common Table Expression (CTE)
-- Business Question: Calculate route net profitability by assembling gross ticket revenues 
--                    and deducting cancellation refunds using modular CTE blocks.
-- Concepts Demonstrated: WITH clause (Common Table Expression), multi-CTE joins.

USE transitmatrix;

WITH RouteGrossRevenue AS (
    SELECT 
        tr.route_id,
        COUNT(t.ticket_id) AS tickets_sold,
        SUM(t.fare_amount) AS gross_amount
    FROM trips tr
    JOIN bookings b ON tr.trip_id = b.trip_id
    JOIN tickets t ON b.booking_id = t.booking_id
    GROUP BY tr.route_id
),
RouteRefunds AS (
    SELECT 
        tr.route_id,
        COUNT(c.cancellation_id) AS tickets_cancelled,
        COALESCE(SUM(c.refund_amount), 0.00) AS total_refunded,
        COALESCE(SUM(c.cancellation_fee), 0.00) AS fees_retained
    FROM trips tr
    JOIN bookings b ON tr.trip_id = b.trip_id
    JOIN tickets t ON b.booking_id = t.booking_id
    JOIN cancellations c ON t.ticket_id = c.ticket_id
    GROUP BY tr.route_id
)
SELECT 
    r.route_id,
    r.route_code,
    r.route_name,
    r.total_distance_km,
    COALESCE(g.tickets_sold, 0) AS total_tickets_sold,
    COALESCE(rf.tickets_cancelled, 0) AS total_tickets_cancelled,
    COALESCE(g.gross_amount, 0.00) AS gross_revenue,
    COALESCE(rf.total_refunded, 0.00) AS refunds_paid,
    COALESCE(rf.fees_retained, 0.00) AS cancellation_fees_collected,
    ROUND(COALESCE(g.gross_amount, 0.00) - COALESCE(rf.total_refunded, 0.00), 2) AS net_retained_revenue
FROM routes r
LEFT JOIN RouteGrossRevenue g ON r.route_id = g.route_id
LEFT JOIN RouteRefunds rf ON r.route_id = rf.route_id
ORDER BY net_retained_revenue DESC;

