# TransitMatrix - Passenger Profile Repository (Raw SQL Only)
# Parameterized queries executing against the 'passengers' table.

from typing import List, Dict, Any, Optional


class PassengerRepository:

    @staticmethod
    def get_by_id(connection, passenger_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT passenger_id, user_id, first_name, last_name, gender, age,
                       id_card_type, id_card_number, email, phone_number, created_at
                FROM passengers
                WHERE passenger_id = %s
            """
            cursor.execute(query, (passenger_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def list_passengers(connection, user_id: Optional[int] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            if user_id:
                query = """
                    SELECT passenger_id, user_id, first_name, last_name, gender, age,
                           id_card_type, id_card_number, email, phone_number, created_at
                    FROM passengers
                    WHERE user_id = %s
                    ORDER BY passenger_id ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (user_id, limit, offset))
            else:
                query = """
                    SELECT passenger_id, user_id, first_name, last_name, gender, age,
                           id_card_type, id_card_number, email, phone_number, created_at
                    FROM passengers
                    ORDER BY passenger_id ASC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def create_passenger(connection, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO passengers (
                    user_id, first_name, last_name, gender, age,
                    id_card_type, id_card_number, email, phone_number
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    data.get("user_id"),
                    data["first_name"],
                    data["last_name"],
                    data["gender"],
                    data["age"],
                    data["id_card_type"],
                    data["id_card_number"],
                    data.get("email"),
                    data.get("phone_number")
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()
