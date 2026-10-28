# TransitMatrix - Service Catalog Repository (Raw SQL Only)
# Parameterized queries executing against the 'services' table.

from typing import List, Dict, Any, Optional


class ServiceRepository:

    @staticmethod
    def list_services(connection, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT service_id, service_number, service_name, service_type,
                       operating_days, is_active, created_at
                FROM services
                ORDER BY service_id ASC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (limit, offset))
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(connection, service_id: int) -> Optional[Dict[str, Any]]:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT service_id, service_number, service_name, service_type,
                       operating_days, is_active, created_at
                FROM services
                WHERE service_id = %s
            """
            cursor.execute(query, (service_id,))
            return cursor.fetchone()
        finally:
            cursor.close()

    @staticmethod
    def create_service(connection, data: dict) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO services (
                    service_number, service_name, service_type,
                    operating_days, is_active
                ) VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(
                query,
                (
                    data["service_number"].upper(),
                    data["service_name"],
                    data["service_type"],
                    data.get("operating_days", "MON,TUE,WED,THU,FRI,SAT,SUN"),
                    data.get("is_active", True)
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def update_service(connection, service_id: int, data: dict) -> bool:
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

            values.append(service_id)
            query = f"UPDATE services SET {', '.join(fields)} WHERE service_id = %s"
            cursor.execute(query, tuple(values))
            return cursor.rowcount > 0
        finally:
            cursor.close()
