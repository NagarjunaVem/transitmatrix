# TransitMatrix - Trip Journey Repository (Raw SQL Only)
# Parameterized queries and stored procedure invocation for trip management and search.

from typing import List, Dict, Any, Optional
from datetime import date


class TripRepository:

    @staticmethod
    def list_trips(
        connection,
        limit: int = 50,
        offset: int = 0,
        status: Optional[str] = None,
        trip_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            conditions = []
            params = []
            if status:
                conditions.append("tr.status = %s")
                params.append(status)
            if trip_date:
                conditions.append("tr.trip_date = %s")
                params.append(trip_date)

            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

            query = f"""
                SELECT tr.trip_id, tr.service_id, tr.route_id, tr.vehicle_id,
                       tr.trip_date, tr.scheduled_departure, tr.scheduled_arrival,
                       tr.actual_departure, tr.actual_arrival, tr.status, tr.base_fare,
                       tr.created_at,
                       s.service_number, s.service_name,
                       r.route_code, r.route_name,
                       v.vehicle_number
                FROM trips tr
                JOIN services s ON tr.service_id = s.service_id
                JOIN routes r ON tr.route_id = r.route_id
                JOIN vehicles v ON tr.vehicle_id = v.vehicle_id
                {where_clause}
                ORDER BY tr.scheduled_departure ASC
                LIMIT %s OFFSET %s
            """
            params.extend([limit, offset])
            cursor.execute(query, tuple(params))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(connection, trip_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT tr.trip_id, tr.service_id, tr.route_id, tr.vehicle_id,
                       tr.trip_date, tr.scheduled_departure, tr.scheduled_arrival,
                       tr.actual_departure, tr.actual_arrival, tr.status, tr.base_fare,
                       tr.created_at,
                       s.service_number, s.service_name,
                       r.route_code, r.route_name,
                       v.vehicle_number
                FROM trips tr
                JOIN services s ON tr.service_id = s.service_id
                JOIN routes r ON tr.route_id = r.route_id
                JOIN vehicles v ON tr.vehicle_id = v.vehicle_id
                WHERE tr.trip_id = %s
            """
            cursor.execute(query, (trip_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_trip(connection, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO trips (
                    service_id, route_id, vehicle_id, trip_date,
                    scheduled_departure, scheduled_arrival, status, base_fare
                ) VALUES (%s, %s, %s, %s, %s, %s, 'SCHEDULED', %s)
            """
            cursor.execute(
                query,
                (
                    data["service_id"],
                    data["route_id"],
                    data["vehicle_id"],
                    data["trip_date"],
                    data["scheduled_departure"],
                    data["scheduled_arrival"],
                    data["base_fare"]
                )
            )
            trip_id = cursor.lastrowid

            # Initialize seat inventory for the trip from vehicle seats
            inv_query = """
                INSERT INTO trip_seat_inventory (trip_id, seat_id, is_available)
                SELECT %s, seat_id, TRUE
                FROM seats
                WHERE vehicle_id = %s
            """
            cursor.execute(inv_query, (trip_id, data["vehicle_id"]))

            return trip_id
        finally:
            cursor.close()

    @staticmethod
    def update_trip(connection, trip_id: int, data: dict) -> bool:
        cursor = connection.cursor(dictionary=True)
        try:
            fields = []
            values = []
            for key, val in data.items():
                if val is not None:
                    fields.append(f"{key} = %s")
                    values.append(val)
            if not fields:
                return False

            values.append(trip_id)
            query = f"UPDATE trips SET {', '.join(fields)} WHERE trip_id = %s"
            cursor.execute(query, tuple(values))
            return cursor.rowcount > 0
        finally:
            cursor.close()

    @staticmethod
    def search_trips(
        connection,
        origin_code: str,
        destination_code: str,
        travel_date: date
    ) -> List[Dict[str, Any]]:
        """
        Executes stored procedure sp_search_trips with fallback to direct SQL multi-table join.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            try:
                cursor.callproc("sp_search_trips", (origin_code.upper(), destination_code.upper(), travel_date))
                for result in cursor.stored_results():
                    return result.fetchall()
            except Exception:
                # Direct SQL Join Fallback matching sp_search_trips
                query = """
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
                    ORDER BY tr.scheduled_departure ASC
                """
                cursor.execute(query, (origin_code.upper(), destination_code.upper(), travel_date))
                return cursor.fetchall()
            return []
        finally:
            cursor.close()
