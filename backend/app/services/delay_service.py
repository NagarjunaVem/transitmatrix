# TransitMatrix - Delay Tracking Service

from typing import List, Dict, Any, Optional
from app.db.connection import get_db_connection
from app.repositories.delay_repository import DelayRepository
from app.schemas.delay import DelayCreateRequest, DelayResponse, DelaySummaryReportItem


class DelayService:

    @staticmethod
    def record_delay(request: DelayCreateRequest):
        with get_db_connection() as conn:
            delay_id = DelayRepository.record_delay(
                connection=conn,
                trip_id=request.trip_id,
                station_id=request.station_id,
                delay_minutes=request.delay_minutes,
                delay_reason=request.delay_reason,
                incident_description=request.incident_description
            )
            conn.commit()
            delays = DelayRepository.list_delays(conn, limit=1, trip_id=request.trip_id)
            return delays[0] if delays else None

    @staticmethod
    def list_delays(limit: int = 50, offset: int = 0, trip_id: Optional[int] = None):
        with get_db_connection() as conn:
            return DelayRepository.list_delays(conn, limit, offset, trip_id)

    @staticmethod
    def get_delay_summary():
        with get_db_connection() as conn:
            return DelayRepository.get_delay_summary(conn)
