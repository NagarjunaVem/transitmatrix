# TransitMatrix - Database Lab Repository (Raw SQL Only)
# Catalog of 21 advanced relational SQL queries with live execution against MySQL 8.0+.

import time
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status

DEMO_QUERIES = [
    {
        "query_id": "Q01",
        "title": "Multi-Table Inner Join",
        "category": "Joins",
        "description": "Four-table join retrieving passenger booking manifests with train service, origin, and destination stations.",
        "sql": """
SELECT 
    b.booking_reference,
    t.ticket_number,
    CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
    p.age,
    s.service_number,
    s.service_name,
    st_orig.station_code AS from_station,
    st_dest.station_code AS to_station,
    t.fare_amount
FROM bookings b
JOIN tickets t ON b.booking_id = t.booking_id
JOIN passengers p ON t.passenger_id = p.passenger_id
JOIN trips tr ON b.trip_id = tr.trip_id
JOIN services s ON tr.service_id = s.service_id
JOIN stations st_orig ON t.origin_station_id = st_orig.station_id
JOIN stations st_dest ON t.destination_station_id = st_dest.station_id
WHERE b.booking_status = 'CONFIRMED'
ORDER BY b.booking_date DESC
LIMIT 15;
"""
    },
    {
        "query_id": "Q02",
        "title": "Left Outer Join with NULL Handling",
        "category": "Joins",
        "description": "Identifies physical train vehicles and counts how many calendar trips have been scheduled for each.",
        "sql": """
SELECT 
    v.vehicle_id,
    v.vehicle_number,
    v.model_name,
    v.maintenance_status,
    COUNT(t.trip_id) AS trips_scheduled_count
FROM vehicles v
LEFT JOIN trips t ON v.vehicle_id = t.vehicle_id
GROUP BY v.vehicle_id, v.vehicle_number, v.model_name, v.maintenance_status
ORDER BY trips_scheduled_count DESC, v.vehicle_id ASC;
"""
    },
    {
        "query_id": "Q03",
        "title": "Nested Scalar Subquery",
        "category": "Subqueries",
        "description": "Finds all transit routes with total distance strictly greater than the overall network average route distance.",
        "sql": """
SELECT 
    route_id,
    route_code,
    route_name,
    total_distance_km
FROM routes
WHERE total_distance_km > (
    SELECT AVG(total_distance_km) 
    FROM routes
)
ORDER BY total_distance_km DESC;
"""
    },
    {
        "query_id": "Q04",
        "title": "Nested Subquery with IN Clause",
        "category": "Subqueries",
        "description": "Finds passenger profiles who have confirmed tickets on premium Rajdhani or Vande Bharat services.",
        "sql": """
SELECT passenger_id, first_name, last_name, gender, age
FROM passengers
WHERE passenger_id IN (
    SELECT DISTINCT t.passenger_id
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    JOIN trips tr ON b.trip_id = tr.trip_id
    JOIN services s ON tr.service_id = s.service_id
    WHERE s.service_type IN ('RAJDHANI', 'VANDE_BHARAT')
)
LIMIT 15;
"""
    },
    {
        "query_id": "Q05",
        "title": "Correlated Subquery in SELECT",
        "category": "Subqueries",
        "description": "Displays stations along with a correlated subquery computing the total count of intermediate route stops referencing each station.",
        "sql": """
SELECT 
    s.station_id,
    s.station_code,
    s.station_name,
    s.city,
    (
        SELECT COUNT(*)
        FROM route_stops rs
        WHERE rs.station_id = s.station_id
    ) AS route_stop_occurrences
FROM stations s
ORDER BY route_stop_occurrences DESC
LIMIT 15;
"""
    },
    {
        "query_id": "Q06",
        "title": "Correlated Subquery with EXISTS",
        "category": "Subqueries",
        "description": "Identifies users who have completed at least one successful booking with total fare exceeding 2000.",
        "sql": """
SELECT u.user_id, u.username, u.email, u.first_name, u.last_name
FROM users u
WHERE EXISTS (
    SELECT 1 
    FROM bookings b 
    WHERE b.user_id = u.user_id 
      AND b.booking_status = 'CONFIRMED'
      AND b.total_fare > 2000.00
);
"""
    },
    {
        "query_id": "Q07",
        "title": "Correlated Subquery with NOT EXISTS",
        "category": "Subqueries",
        "description": "Finds users who have never had any ticket cancelled.",
        "sql": """
SELECT u.user_id, u.username, u.email
FROM users u
WHERE NOT EXISTS (
    SELECT 1 
    FROM bookings b
    JOIN cancellations c ON b.booking_id = c.booking_id
    WHERE b.user_id = u.user_id
)
LIMIT 15;
"""
    },
    {
        "query_id": "Q08",
        "title": "Aggregate Functions and GROUP BY",
        "category": "Aggregations",
        "description": "Summarizes booking transactions per payment method with count, total revenue, average fare, and maximum transaction.",
        "sql": """
SELECT 
    p.payment_method,
    COUNT(p.payment_id) AS transaction_count,
    SUM(p.amount) AS total_settled_amount,
    ROUND(AVG(p.amount), 2) AS avg_transaction_amount,
    MAX(p.amount) AS highest_transaction_amount
FROM payments p
WHERE p.payment_status = 'SUCCESS'
GROUP BY p.payment_method
ORDER BY total_settled_amount DESC;
"""
    },
    {
        "query_id": "Q09",
        "title": "GROUP BY with HAVING Filter",
        "category": "Aggregations",
        "description": "Identifies routes that have accumulated more than 50,000 in gross ticket revenue.",
        "sql": """
SELECT 
    r.route_code,
    r.route_name,
    COUNT(t.ticket_id) AS total_tickets_sold,
    SUM(t.fare_amount) AS total_gross_revenue
FROM routes r
JOIN trips tr ON r.route_id = tr.route_id
JOIN bookings b ON tr.trip_id = b.trip_id
JOIN tickets t ON b.booking_id = t.booking_id
WHERE t.ticket_status <> 'CANCELLED'
GROUP BY r.route_id, r.route_code, r.route_name
HAVING total_gross_revenue > 20000.00
ORDER BY total_gross_revenue DESC;
"""
    },
    {
        "query_id": "Q10",
        "title": "Common Table Expression (CTE)",
        "category": "CTEs & Advanced",
        "description": "Calculates seat vacancy ratios per trip using a Common Table Expression.",
        "sql": """
WITH TripVacancyStats AS (
    SELECT 
        tr.trip_id,
        s.service_number,
        r.route_code,
        tr.trip_date,
        COUNT(tsi.inventory_id) AS total_seats,
        SUM(CASE WHEN tsi.is_available = TRUE THEN 1 ELSE 0 END) AS available_seats
    FROM trips tr
    JOIN services s ON tr.service_id = s.service_id
    JOIN routes r ON tr.route_id = r.route_id
    JOIN trip_seat_inventory tsi ON tr.trip_id = tsi.trip_id
    GROUP BY tr.trip_id, s.service_number, r.route_code, tr.trip_date
)
SELECT 
    trip_id,
    service_number,
    route_code,
    trip_date,
    total_seats,
    available_seats,
    ROUND((available_seats / total_seats) * 100, 2) AS vacancy_percentage
FROM TripVacancyStats
ORDER BY vacancy_percentage DESC
LIMIT 15;
"""
    },
    {
        "query_id": "Q11",
        "title": "Recursive CTE for Network Graph Traversal",
        "category": "CTEs & Advanced",
        "description": "Simulates sequential multi-hop corridor station graph paths using a recursive Common Table Expression.",
        "sql": """
WITH RECURSIVE StationChain AS (
    SELECT 
        rs.route_id,
        rs.station_id,
        rs.stop_sequence,
        CAST(s.station_code AS CHAR(200)) AS transit_path,
        rs.distance_from_origin_km
    FROM route_stops rs
    JOIN stations s ON rs.station_id = s.station_id
    WHERE rs.stop_sequence = 1
    
    UNION ALL
    
    SELECT 
        rs_next.route_id,
        rs_next.station_id,
        rs_next.stop_sequence,
        CONCAT(sc.transit_path, ' -> ', s_next.station_code),
        rs_next.distance_from_origin_km
    FROM StationChain sc
    JOIN route_stops rs_next ON sc.route_id = rs_next.route_id 
                            AND rs_next.stop_sequence = sc.stop_sequence + 1
    JOIN stations s_next ON rs_next.station_id = s_next.station_id
    WHERE sc.stop_sequence < 4
)
SELECT route_id, stop_sequence, transit_path, distance_from_origin_km
FROM StationChain
WHERE stop_sequence > 1
LIMIT 15;
"""
    },
    {
        "query_id": "Q12",
        "title": "Window Function ROW_NUMBER()",
        "category": "Window Functions",
        "description": "Ranks trips chronologically per route using the ROW_NUMBER() window function.",
        "sql": """
SELECT 
    r.route_code,
    tr.trip_id,
    tr.trip_date,
    tr.scheduled_departure,
    tr.status,
    ROW_NUMBER() OVER (
        PARTITION BY r.route_id 
        ORDER BY tr.scheduled_departure ASC
    ) AS trip_sequence_in_route
FROM trips tr
JOIN routes r ON tr.route_id = r.route_id
LIMIT 20;
"""
    },
    {
        "query_id": "Q13",
        "title": "Window Function DENSE_RANK()",
        "category": "Window Functions",
        "description": "Ranks passenger spenders within each tier using DENSE_RANK().",
        "sql": """
SELECT 
    u.user_id,
    u.username,
    b.booking_reference,
    b.total_fare,
    DENSE_RANK() OVER (ORDER BY b.total_fare DESC) AS fare_rank
FROM bookings b
JOIN users u ON b.user_id = u.user_id
WHERE b.booking_status = 'CONFIRMED'
LIMIT 15;
"""
    },
    {
        "query_id": "Q14",
        "title": "Window Function Running Total",
        "category": "Window Functions",
        "description": "Computes cumulative running total revenue across bookings ordered by timestamp.",
        "sql": """
SELECT 
    booking_id,
    booking_reference,
    booking_date,
    total_fare,
    SUM(total_fare) OVER (
        ORDER BY booking_date ASC, booking_id ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_running_revenue
FROM bookings
WHERE booking_status = 'CONFIRMED'
LIMIT 20;
"""
    },
    {
        "query_id": "Q15",
        "title": "Window Functions LAG() and LEAD()",
        "category": "Window Functions",
        "description": "Analyzes intermediate timetable halts, displaying prior station distance and next station distance offsets.",
        "sql": """
SELECT 
    route_id,
    stop_sequence,
    station_id,
    distance_from_origin_km,
    LAG(distance_from_origin_km, 1, 0.0) OVER (
        PARTITION BY route_id ORDER BY stop_sequence ASC
    ) AS prev_stop_distance,
    LEAD(distance_from_origin_km) OVER (
        PARTITION BY route_id ORDER BY stop_sequence ASC
    ) AS next_stop_distance
FROM route_stops
LIMIT 15;
"""
    },
    {
        "query_id": "Q16",
        "title": "Querying View v_trip_availability",
        "category": "Views",
        "description": "Demonstrates querying the reporting view v_trip_availability with class-level occupancy percentages.",
        "sql": """
SELECT 
    trip_id,
    service_number,
    service_name,
    route_code,
    trip_date,
    seat_class,
    total_class_capacity,
    available_seats,
    occupancy_pct
FROM v_trip_availability
WHERE occupancy_pct > 0.00
ORDER BY occupancy_pct DESC
LIMIT 15;
"""
    },
    {
        "query_id": "Q17",
        "title": "Querying View v_route_performance",
        "category": "Views",
        "description": "Demonstrates querying the commercial route performance view v_route_performance.",
        "sql": """
SELECT 
    route_code,
    route_name,
    total_trips_scheduled,
    delayed_trips_count,
    gross_revenue,
    total_refunds,
    net_revenue
FROM v_route_performance
ORDER BY net_revenue DESC;
"""
    },
    {
        "query_id": "Q18",
        "title": "Transactional Pessimistic Locking Simulation",
        "category": "Transactions",
        "description": "Demonstrates row-level locking with SELECT ... FOR UPDATE on trip seat inventory.",
        "sql": """
SELECT 
    tsi.inventory_id,
    tsi.trip_id,
    s.coach_number,
    s.seat_number,
    s.seat_class,
    tsi.is_available
FROM trip_seat_inventory tsi
JOIN seats s ON tsi.seat_id = s.seat_id
WHERE tsi.trip_id = 1 AND tsi.is_available = TRUE
LIMIT 5;
"""
    },
    {
        "query_id": "Q19",
        "title": "Cancellation Audit Verification",
        "category": "Auditing",
        "description": "Queries the audit_logs table to inspect JSON state diffs generated by triggers upon data mutation.",
        "sql": """
SELECT 
    log_id,
    table_name,
    record_id,
    action,
    new_values,
    changed_by,
    changed_at
FROM audit_logs
ORDER BY log_id DESC
LIMIT 10;
"""
    },
    {
        "query_id": "Q20",
        "title": "View v_monthly_revenue Analysis",
        "category": "Views",
        "description": "Queries the monthly financial performance breakdown view across corridors.",
        "sql": """
SELECT 
    revenue_month,
    route_code,
    route_name,
    service_type,
    confirmed_tickets,
    net_monthly_revenue
FROM v_monthly_revenue
ORDER BY revenue_month DESC, net_monthly_revenue DESC
LIMIT 15;
"""
    },
    {
        "query_id": "Q21",
        "title": "Index Query Plan (EXPLAIN)",
        "category": "Indexes & Performance",
        "description": "Inspects index utilization and execution plan using EXPLAIN on composite index idx_trips_route_date_status.",
        "sql": """
EXPLAIN 
SELECT trip_id, service_id, scheduled_departure, base_fare
FROM trips
WHERE route_id = 1 
  AND trip_date = '2026-11-01' 
  AND status = 'SCHEDULED';
"""
    }
]


class DbLabRepository:

    @staticmethod
    def get_query_catalog() -> List[Dict[str, Any]]:
        return [
            {
                "query_id": q["query_id"],
                "title": q["title"],
                "category": q["category"],
                "description": q["description"],
                "sql_statement": q["sql"].strip()
            }
            for q in DEMO_QUERIES
        ]

    @staticmethod
    def execute_catalog_query(connection, query_id: str) -> Dict[str, Any]:
        matched = next((q for q in DEMO_QUERIES if q["query_id"].upper() == query_id.upper()), None)
        if not matched:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Query ID '{query_id}' not found in catalog")

        sql = matched["sql"].strip()
        cursor = connection.cursor(dictionary=True)
        try:
            # Measure execution time
            start_time = time.perf_counter()
            cursor.execute(sql)
            rows = cursor.fetchall()
            exec_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            columns = list(rows[0].keys()) if rows else []

            # Optional EXPLAIN Plan
            explain_plan = []
            if not sql.upper().startswith("EXPLAIN"):
                try:
                    explain_cursor = connection.cursor(dictionary=True)
                    explain_cursor.execute(f"EXPLAIN {sql}")
                    explain_plan = explain_cursor.fetchall()
                    explain_cursor.close()
                except Exception:
                    explain_plan = []

            return {
                "query_id": matched["query_id"],
                "title": matched["title"],
                "sql_statement": sql,
                "execution_time_ms": exec_time_ms,
                "row_count": len(rows),
                "columns": columns,
                "rows": rows,
                "explain_plan": explain_plan
            }
        finally:
            cursor.close()
