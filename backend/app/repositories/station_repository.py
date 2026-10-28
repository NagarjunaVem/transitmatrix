# TransitMatrix - Station Repository (Raw SQL Only)
# Parameterized queries executing against the 'stations' table.

from typing import List, Dict, Any, Optional


class StationRepository:

    @staticmethod
    def list_stations(connection, limit: int = 100, offset: int = 0, search: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            if search:
                query = """
                    SELECT station_id, station_code, station_name, city, state, zone,
                           total_platforms, latitude, longitude, is_active, created_at
                    FROM stations
                    WHERE station_code LIKE %s OR station_name LIKE %s OR city LIKE %s
                    ORDER BY station_name ASC
                    LIMIT %s OFFSET %s
                """
                like_term = f"%{search}%"
                cursor.execute(query, (like_term, like_term, like_term, limit, offset))
            else:
                query = """
                    SELECT station_id, station_code, station_name, city, state, zone,
                           total_platforms, latitude, longitude, is_active, created_at
                    FROM stations
                    ORDER BY station_name ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(connection, station_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT station_id, station_code, station_name, city, state, zone,
                       total_platforms, latitude, longitude, is_active, created_at
                FROM stations
                WHERE station_id = %s
            """
            cursor.execute(query, (station_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_by_code(connection, station_code: str) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT station_id, station_code, station_name, city, state, zone,
                       total_platforms, latitude, longitude, is_active, created_at
                FROM stations
                WHERE station_code = %s
            """
            cursor.execute(query, (station_code,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_station(connection, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO stations (
                    station_code, station_name, city, state, zone,
                    total_platforms, latitude, longitude, is_active
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    data["station_code"].upper(),
                    data["station_name"],
                    data["city"],
                    data["state"],
                    data["zone"],
                    data.get("total_platforms", 2),
                    data["latitude"],
                    data["longitude"],
                    data.get("is_active", True)
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def update_station(connection, station_id: int, data: dict) -> bool:
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

            values.append(station_id)
            query = f"UPDATE stations SET {', '.join(fields)} WHERE station_id = %s"
            cursor.execute(query, tuple(values))
            return cursor.rowcount > 0
        finally:
            cursor.close()

    @staticmethod
    def delete_station(connection, station_id: int) -> bool:
        cursor = connection.cursor(dictionary=True)
        try:
            cursor.execute("DELETE FROM stations WHERE station_id = %s", (station_id,))
            return cursor.rowcount > 0
        finally:
            cursor.close()
