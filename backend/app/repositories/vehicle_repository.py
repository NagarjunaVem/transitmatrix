# TransitMatrix - Rolling Stock Vehicle Repository (Raw SQL Only)
# Parameterized queries for train rakes, coaches, and seats.

from typing import List, Dict, Any, Optional


class VehicleRepository:

    @staticmethod
    def list_vehicles(connection, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT vehicle_id, vehicle_number, vehicle_type, model_name,
                       manufacture_year, total_coaches, total_capacity,
                       maintenance_status, created_at
                FROM vehicles
                ORDER BY vehicle_id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(connection, vehicle_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT vehicle_id, vehicle_number, vehicle_type, model_name,
                       manufacture_year, total_coaches, total_capacity,
                       maintenance_status, created_at
                FROM vehicles
                WHERE vehicle_id = %s
            """
            cursor.execute(query, (vehicle_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_vehicle(connection, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO vehicles (
                    vehicle_number, vehicle_type, model_name,
                    manufacture_year, total_coaches, total_capacity, maintenance_status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    data["vehicle_number"].upper(),
                    data["vehicle_type"],
                    data["model_name"],
                    data["manufacture_year"],
                    data["total_coaches"],
                    data["total_capacity"],
                    data.get("maintenance_status", "OPERATIONAL")
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def get_vehicle_seats(connection, vehicle_id: int) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT seat_id, vehicle_id, coach_number, seat_number,
                       seat_class, seat_type, fare_multiplier
                FROM seats
                WHERE vehicle_id = %s
                ORDER BY coach_number ASC, seat_id ASC
            """
            cursor.execute(query, (vehicle_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
