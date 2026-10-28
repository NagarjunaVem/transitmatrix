# TransitMatrix - Reporting Repository (Raw SQL Only)
# Queries analytical database views and reporting stored procedures.

from typing import List, Dict, Any, Optional
from datetime import date


class ReportRepository:

    @staticmethod
    def get_route_performance(connection) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT route_id, route_code, route_name, total_distance_km,
                       total_trips_scheduled, delayed_trips_count,
                       total_passengers_booked, gross_revenue, total_refunds, net_revenue
                FROM v_route_performance
                ORDER BY net_revenue DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_monthly_revenue(connection) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT revenue_month, route_code, route_name, service_type,
                       total_bookings, confirmed_tickets, total_collected_amount,
                       total_refund_amount, net_monthly_revenue
                FROM v_monthly_revenue
                ORDER BY revenue_month DESC, net_monthly_revenue DESC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_trip_availability_report(connection, trip_id: Optional[int] = None) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            if trip_id:
                query = """
                    SELECT trip_id, service_number, service_name, route_code,
                           trip_date, scheduled_departure, trip_status,
                           seat_class, total_class_capacity, available_seats,
                           reserved_seats, occupancy_pct
                    FROM v_trip_availability
                    WHERE trip_id = %s
                """
                cursor.execute(query, (trip_id,))
            else:
                query = """
                    SELECT trip_id, service_number, service_name, route_code,
                           trip_date, scheduled_departure, trip_status,
                           seat_class, total_class_capacity, available_seats,
                           reserved_seats, occupancy_pct
                    FROM v_trip_availability
                    ORDER BY trip_date ASC, trip_id ASC
                    LIMIT 100
                """
                cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_route_revenue_by_procedure(
        connection,
        route_id: int,
        start_date: date,
        end_date: date
    ) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_route_revenue_report", (route_id, start_date, end_date))
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                # Direct SQL fallback
                query = """
                    SELECT 
                        r.route_id,
                        r.route_code,
                        r.route_name,
                        COUNT(DISTINCT tr.trip_id) AS total_trips,
                        COUNT(DISTINCT b.booking_id) AS total_bookings,
                        COUNT(t.ticket_id) AS total_tickets_sold,
                        COALESCE(SUM(t.fare_amount), 0.00) AS gross_revenue,
                        COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds,
                        COALESCE(SUM(t.fare_amount), 0.00) - COALESCE(SUM(c.refund_amount), 0.00) AS net_revenue
                    FROM routes r
                    JOIN trips tr ON r.route_id = tr.route_id
                    LEFT JOIN bookings b ON tr.trip_id = b.trip_id
                    LEFT JOIN tickets t ON b.booking_id = t.booking_id AND t.ticket_status <> 'CANCELLED'
                    LEFT JOIN cancellations c ON b.booking_id = c.booking_id
                    WHERE r.route_id = %s
                      AND tr.trip_date BETWEEN %s AND %s
                    GROUP BY r.route_id, r.route_code, r.route_name
                """
                cursor.execute(query, (route_id, start_date, end_date))
                return cursor.fetchall()
            return []
        finally:
            cursor.close()
