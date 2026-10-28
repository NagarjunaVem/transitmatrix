# TransitMatrix - Payment Repository (Raw SQL Only)
# Parameterized queries for transaction settlement tracking.

from typing import Dict, Any, Optional


class PaymentRepository:

    @staticmethod
    def create_payment(
        connection,
        booking_id: int,
        transaction_reference: str,
        payment_method: str,
        amount: float,
        payment_status: str = "SUCCESS"
    ) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO payments (
                    booking_id, transaction_reference,
                    payment_method, amount, payment_status
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (booking_id, transaction_reference, payment_method, amount, payment_status)
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def get_payment_by_booking_id(connection, booking_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT payment_id, booking_id, transaction_reference,
                       payment_method, amount, payment_status, paid_at
                FROM payments
                WHERE booking_id = %s
                ORDER BY payment_id DESC
                LIMIT 1
            """
            cursor.execute(query, (booking_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
