# TransitMatrix - Route Repository (Raw SQL Only)
# Explicit parameterized queries for routes and ordered intermediate stops.

from typing import List, Dict, Any, Optional


class RouteRepository:

    @staticmethod
    def list_routes(connection, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT r.route_id, r.route_code, r.route_name,
                       r.origin_station_id, st_orig.station_code AS origin_station_code, st_orig.station_name AS origin_station_name,
                       r.destination_station_id, st_dest.station_code AS destination_station_code, st_dest.station_name AS destination_station_name,
                       r.total_distance_km, r.duration_est_minutes, r.is_active, r.created_at
                FROM routes r
                JOIN stations st_orig ON r.origin_station_id = st_orig.station_id
                JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
                ORDER BY r.route_id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(connection, route_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT r.route_id, r.route_code, r.route_name,
                       r.origin_station_id, st_orig.station_code AS origin_station_code, st_orig.station_name AS origin_station_name,
                       r.destination_station_id, st_dest.station_code AS destination_station_code, st_dest.station_name AS destination_station_name,
                       r.total_distance_km, r.duration_est_minutes, r.is_active, r.created_at
                FROM routes r
                JOIN stations st_orig ON r.origin_station_id = st_orig.station_id
                JOIN stations st_dest ON r.destination_station_id = st_dest.station_id
                WHERE r.route_id = %s
            """
            cursor.execute(query, (route_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_by_code(connection, route_code: str) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT route_id, route_code, route_name, origin_station_id,
                       destination_station_id, total_distance_km, duration_est_minutes, is_active
                FROM routes
                WHERE route_code = %s
            """
            cursor.execute(query, (route_code,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_route(connection, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO routes (
                    route_code, route_name, origin_station_id,
                    destination_station_id, total_distance_km, duration_est_minutes, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    data["route_code"].upper(),
                    data["route_name"],
                    data["origin_station_id"],
                    data["destination_station_id"],
                    data["total_distance_km"],
                    data["duration_est_minutes"],
                    data.get("is_active", True)
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def get_route_stops(connection, route_id: int) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT rs.stop_id, rs.route_id, rs.station_id, rs.stop_sequence,
                       rs.distance_from_origin_km, rs.departure_offset_minutes,
                       rs.arrival_offset_minutes, rs.halt_duration_minutes, rs.platform_number,
                       s.station_code, s.station_name
                FROM route_stops rs
                JOIN stations s ON rs.station_id = s.station_id
                WHERE rs.route_id = %s
                ORDER BY rs.stop_sequence ASC
            """
            cursor.execute(query, (route_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def add_route_stop(connection, route_id: int, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO route_stops (
                    route_id, station_id, stop_sequence, distance_from_origin_km,
                    departure_offset_minutes, arrival_offset_minutes, halt_duration_minutes, platform_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    route_id,
                    data["station_id"],
                    data["stop_sequence"],
                    data["distance_from_origin_km"],
                    data.get("departure_offset_minutes", 0),
                    data.get("arrival_offset_minutes", 0),
                    data.get("halt_duration_minutes", 0),
                    data.get("platform_number", 1)
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()
