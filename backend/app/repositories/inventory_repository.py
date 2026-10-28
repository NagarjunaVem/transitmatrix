# TransitMatrix - Inventory Repository (Raw SQL Only)
# Manages trip seat inventory and pessimistic concurrency locking (SELECT ... FOR UPDATE).

from typing import List, Dict, Any, Optional


class InventoryRepository:

    @staticmethod
    def get_trip_seat_map(connection, trip_id: int, coach_number: Optional[str] = None) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            if coach_number:
                query = """
                    SELECT s.seat_id, s.coach_number, s.seat_number, s.seat_class,
                           s.seat_type, s.fare_multiplier, tsi.is_available
                    FROM trip_seat_inventory tsi
                    JOIN seats s ON tsi.seat_id = s.seat_id
                    WHERE tsi.trip_id = %s AND s.coach_number = %s
                    ORDER BY s.coach_number ASC, s.seat_id ASC
                """
                cursor.execute(query, (trip_id, coach_number))
            else:
                query = """
                    SELECT s.seat_id, s.coach_number, s.seat_number, s.seat_class,
                           s.seat_type, s.fare_multiplier, tsi.is_available
                    FROM trip_seat_inventory tsi
                    JOIN seats s ON tsi.seat_id = s.seat_id
                    WHERE tsi.trip_id = %s
                    ORDER BY s.coach_number ASC, s.seat_id ASC
                """
                cursor.execute(query, (trip_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_seat_for_update(connection, trip_id: int, seat_id: int) -> Optional[Dict[str, Any]]:
        """
        Executes a pessimistic row-level lock on the specified seat inventory row using SELECT ... FOR UPDATE.
        Must be executed within an active transaction.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT tsi.inventory_id, tsi.trip_id, tsi.seat_id, tsi.is_available,
                       s.fare_multiplier, s.coach_number, s.seat_number, s.seat_class
                FROM trip_seat_inventory tsi
                JOIN seats s ON tsi.seat_id = s.seat_id
                WHERE tsi.trip_id = %s AND tsi.seat_id = %s
                FOR UPDATE
            """
            cursor.execute(query, (trip_id, seat_id))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def reserve_seat(connection, trip_id: int, seat_id: int) -> bool:
        """
        Marks seat as unavailable within the current transaction.
        Returns True only if 1 row was updated.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                UPDATE trip_seat_inventory
                SET is_available = FALSE, reserved_at = NOW()
                WHERE trip_id = %s AND seat_id = %s AND is_available = TRUE
            """
            cursor.execute(query, (trip_id, seat_id))
            return cursor.rowcount == 1
        finally:
            cursor.close()

    @staticmethod
    def release_seat(connection, trip_id: int, seat_id: int) -> bool:
        """
        Restores seat availability upon cancellation.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                UPDATE trip_seat_inventory
                SET is_available = TRUE, reserved_at = NULL
                WHERE trip_id = %s AND seat_id = %s
            """
            cursor.execute(query, (trip_id, seat_id))
            return cursor.rowcount == 1
        finally:
            cursor.close()
