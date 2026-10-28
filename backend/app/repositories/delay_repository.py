# TransitMatrix - Delay Tracking Repository (Raw SQL Only)
# Parameterized queries for incident recording and summary views.

from typing import List, Dict, Any, Optional


class DelayRepository:

    @staticmethod
    def record_delay(
        connection,
        trip_id: int,
        station_id: int,
        delay_minutes: int,
        delay_reason: str,
        incident_description: Optional[str] = None
    ) -> int:
        """
        Inserts a delay event.
        MySQL trigger 'trg_delays_after_insert' automatically updates trips.status to 'DELAYED'
        if delay_minutes >= 15.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO delays (
                    trip_id, station_id, delay_minutes,
                    delay_reason, incident_description
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (trip_id, station_id, delay_minutes, delay_reason, incident_description)
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def list_delays(connection, limit: int = 50, offset: int = 0, trip_id: Optional[int] = None) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            if trip_id:
                query = """
                    SELECT d.delay_id, d.trip_id, d.station_id, s.station_name, s.station_code,
                           d.delay_minutes, d.delay_reason, d.incident_description, d.recorded_at
                    FROM delays d
                    JOIN stations s ON d.station_id = s.station_id
                    WHERE d.trip_id = %s
                    ORDER BY d.recorded_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (trip_id, limit, offset))
            else:
                query = """
                    SELECT d.delay_id, d.trip_id, d.station_id, s.station_name, s.station_code,
                           d.delay_minutes, d.delay_reason, d.incident_description, d.recorded_at
                    FROM delays d
                    JOIN stations s ON d.station_id = s.station_id
                    ORDER BY d.recorded_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_delay_summary(connection) -> List[Dict[str, Any]]:
        """
        Queries the database view v_delay_summary.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT station_id, station_code, station_name, city,
                       total_delay_incidents, avg_delay_minutes,
                       max_delay_minutes, total_delay_minutes, primary_delay_reason
                FROM v_delay_summary
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
