# TransitMatrix - Database Lab Service

from typing import List, Dict, Any
from app.db.connection import get_db_connection
from app.repositories.db_lab_repository import DbLabRepository


class DbLabService:

    @staticmethod
    def get_query_catalog() -> List[Dict[str, Any]]:
        return DbLabRepository.get_query_catalog()

    @staticmethod
    def execute_query(query_id: str) -> Dict[str, Any]:
        with get_db_connection() as conn:
            return DbLabRepository.execute_catalog_query(conn, query_id)
