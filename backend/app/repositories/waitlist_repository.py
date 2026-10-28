# TransitMatrix - Waitlist Repository (Raw SQL Only)
# Parameterized queries and stored procedure invocation for FIFO waitlist management.

from typing import List, Dict, Any, Optional


class WaitlistRepository:

    @staticmethod
    def get_trip_waitlist(
        connection,
        trip_id: int,
        seat_class: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            if seat_class:
                query = """
                    SELECT w.waitlist_id, w.trip_id, w.passenger_id,
                           CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
                           w.booking_id, b.booking_reference,
                           w.seat_class, w.waitlist_number, w.status, w.created_at
                    FROM waitlists w
                    JOIN passengers p ON w.passenger_id = p.passenger_id
                    JOIN bookings b ON w.booking_id = b.booking_id
                    WHERE w.trip_id = %s AND w.seat_class = %s
                    ORDER BY w.waitlist_number ASC
                """
                cursor.execute(query, (trip_id, seat_class))
            else:
                query = """
                    SELECT w.waitlist_id, w.trip_id, w.passenger_id,
                           CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
                           w.booking_id, b.booking_reference,
                           w.seat_class, w.waitlist_number, w.status, w.created_at
                    FROM waitlists w
                    JOIN passengers p ON w.passenger_id = p.passenger_id
                    JOIN bookings b ON w.booking_id = b.booking_id
                    WHERE w.trip_id = %s
                    ORDER BY w.seat_class ASC, w.waitlist_number ASC
                """
                cursor.execute(query, (trip_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_next_waitlist_number(connection, trip_id: int, seat_class: str) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT COALESCE(MAX(waitlist_number), 0) + 1 AS next_num
                FROM waitlists
                WHERE trip_id = %s AND seat_class = %s
            """
            cursor.execute(query, (trip_id, seat_class))
            row = cursor.fetchone()
            return row["next_num"] if row else 1
        finally:
            cursor.close()

    @staticmethod
    def add_to_waitlist(
        connection,
        trip_id: int,
        passenger_id: int,
        booking_id: int,
        seat_class: str
    ) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            next_num = WaitlistRepository.get_next_waitlist_number(connection, trip_id, seat_class)
            query = """
                INSERT INTO waitlists (
                    trip_id, passenger_id, booking_id, seat_class, waitlist_number, status
                ) VALUES (%s, %s, %s, %s, %s, 'WAITING')
            """
            cursor.execute(query, (trip_id, passenger_id, booking_id, seat_class, next_num))
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def promote_waitlist_passenger(
        connection,
        trip_id: int,
        seat_class: str,
        freed_seat_id: int
    ) -> Dict[str, Any]:
        """
        Executes stored procedure sp_process_waitlist_promotion.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            # Stored procedure arguments: trip_id, seat_class, freed_seat_id, OUT p_promoted_pid, OUT p_msg
            call_sql = "CALL sp_process_waitlist_promotion(%s, %s, %s, @p_promoted_pid, @p_msg)"
            cursor.execute(call_sql, (trip_id, seat_class, freed_seat_id))

            cursor.execute("SELECT @p_promoted_pid AS promoted_passenger_id, @p_msg AS status_message")
            out_result = cursor.fetchone()

            return {
                "trip_id": trip_id,
                "seat_class": seat_class,
                "freed_seat_id": freed_seat_id,
                "promoted_passenger_id": out_result["promoted_passenger_id"] if out_result else None,
                "status_message": out_result["status_message"] if out_result else "Promotion completed"
            }
        finally:
            cursor.close()
