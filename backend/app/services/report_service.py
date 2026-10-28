# TransitMatrix - Reporting Service

from typing import List, Dict, Any, Optional
from datetime import date
from app.db.connection import get_db_connection
from app.repositories.report_repository import ReportRepository


class ReportService:

    @staticmethod
    def get_route_performance():
        with get_db_connection() as conn:
            return ReportRepository.get_route_performance(conn)

    @staticmethod
    def get_monthly_revenue():
        with get_db_connection() as conn:
            return ReportRepository.get_monthly_revenue(conn)

    @staticmethod
    def get_trip_availability(trip_id: Optional[int] = None):
        with get_db_connection() as conn:
            return ReportRepository.get_trip_availability_report(conn, trip_id)

    @staticmethod
    def get_route_revenue_report(route_id: int, start_date: date, end_date: date):
        with get_db_connection() as conn:
            return ReportRepository.get_route_revenue_by_procedure(conn, route_id, start_date, end_date)
