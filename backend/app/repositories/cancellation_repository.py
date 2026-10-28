# TransitMatrix - Cancellation Repository (Raw SQL Only)
# Parameterized queries for ticket cancellations and refund records.

from typing import Dict, Any, Optional, List


class CancellationRepository:

    @staticmethod
    def get_ticket_for_cancellation(connection, ticket_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT t.ticket_id, t.booking_id, t.passenger_id, t.seat_id,
                       t.ticket_number, t.fare_amount, t.ticket_status,
                       b.trip_id, b.user_id, tr.trip_date, tr.scheduled_departure
                FROM tickets t
                JOIN bookings b ON t.booking_id = b.booking_id
                JOIN trips tr ON b.trip_id = tr.trip_id
                WHERE t.ticket_id = %s
            """
            cursor.execute(query, (ticket_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_cancellation(
        connection,
        booking_id: int,
        ticket_id: int,
        cancellation_reason: Optional[str],
        cancellation_fee: float,
        refund_amount: float,
        refund_status: str = "PROCESSED"
    ) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO cancellations (
                    booking_id, ticket_id, cancellation_reason,
                    cancellation_fee, refund_amount, refund_status
                ) VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (booking_id, ticket_id, cancellation_reason, cancellation_fee, refund_amount, refund_status)
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def get_cancellation_by_ticket_id(connection, ticket_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT cancellation_id, booking_id, ticket_id,
                       cancellation_reason, cancellation_fee, refund_amount,
                       refund_status, cancelled_at
                FROM cancellations
                WHERE ticket_id = %s
            """
            cursor.execute(query, (ticket_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def get_cancellations_by_booking_id(connection, booking_id: int) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT cancellation_id, booking_id, ticket_id,
                       cancellation_reason, cancellation_fee, refund_amount,
                       refund_status, cancelled_at
                FROM cancellations
                WHERE booking_id = %s
            """
            cursor.execute(query, (booking_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
