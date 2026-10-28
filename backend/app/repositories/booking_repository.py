# TransitMatrix - Booking Repository (Raw SQL Only)
# Parameterized queries for reservation headers and individual ticket allocations.

from typing import List, Dict, Any, Optional


class BookingRepository:

    @staticmethod
    def create_booking(
        connection,
        booking_reference: str,
        user_id: int,
        trip_id: int,
        total_passengers: int,
        total_fare: float,
        booking_status: str = "CONFIRMED"
    ) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO bookings (
                    booking_reference, user_id, trip_id,
                    total_passengers, total_fare, booking_status
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (booking_reference, user_id, trip_id, total_passengers, total_fare, booking_status)
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def create_ticket(
        connection,
        booking_id: int,
        passenger_id: int,
        seat_id: Optional[int],
        origin_station_id: int,
        destination_station_id: int,
        ticket_number: str,
        fare_amount: float,
        ticket_status: str = "CONFIRMED"
    ) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO tickets (
                    booking_id, passenger_id, seat_id,
                    origin_station_id, destination_station_id,
                    ticket_number, fare_amount, ticket_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    booking_id, passenger_id, seat_id,
                    origin_station_id, destination_station_id,
                    ticket_number, fare_amount, ticket_status
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def get_booking_by_id(connection, booking_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT booking_id, booking_reference, user_id, trip_id,
                       booking_date, total_passengers, total_fare, booking_status, created_at
                FROM bookings
                WHERE booking_id = %s
            """
            cursor.execute(query, (booking_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_booking_by_reference(connection, booking_reference: str) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT booking_id, booking_reference, user_id, trip_id,
                       booking_date, total_passengers, total_fare, booking_status, created_at
                FROM bookings
                WHERE booking_reference = %s
            """
            cursor.execute(query, (booking_reference,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_booking_tickets(connection, booking_id: int) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT t.ticket_id, t.booking_id, t.ticket_number, t.passenger_id,
                       CONCAT(p.first_name, ' ', p.last_name) AS passenger_name,
                       t.seat_id, s.coach_number, s.seat_number, s.seat_class, s.seat_type,
                       t.origin_station_id, st_orig.station_name AS origin_station_name,
                       t.destination_station_id, st_dest.station_name AS destination_station_name,
                       t.fare_amount, t.ticket_status, t.created_at
                FROM tickets t
                JOIN passengers p ON t.passenger_id = p.passenger_id
                LEFT JOIN seats s ON t.seat_id = s.seat_id
                JOIN stations st_orig ON t.origin_station_id = st_orig.station_id
                JOIN stations st_dest ON t.destination_station_id = st_dest.station_id
                WHERE t.booking_id = %s
                ORDER BY t.ticket_id ASC
            """
            cursor.execute(query, (booking_id,))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def list_user_bookings(connection, user_id: int, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT booking_id, booking_reference, user_id, trip_id,
                       booking_date, total_passengers, total_fare, booking_status, created_at
                FROM bookings
                WHERE user_id = %s
                ORDER BY booking_id DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (user_id, limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def update_booking_status(connection, booking_id: int, status: str) -> bool:
        cursor = connection.cursor(dictionary=True)
        try:
            query = "UPDATE bookings SET booking_status = %s WHERE booking_id = %s"
            cursor.execute(query, (status, booking_id))
            return cursor.rowcount > 0
        finally:
            cursor.close()
