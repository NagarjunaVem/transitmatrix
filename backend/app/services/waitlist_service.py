# TransitMatrix - Waitlist Service
# Coordinates passenger queueing and seat promotion workflows.

from typing import List, Dict, Any, Optional
from app.db.connection import get_db_connection
from app.repositories.waitlist_repository import WaitlistRepository
from app.schemas.waitlist import WaitlistCreateRequest, WaitlistResponse, WaitlistPromotionResponse


class WaitlistService:

    @staticmethod
    def get_trip_waitlist(trip_id: int, seat_class: Optional[str] = None) -> List[WaitlistResponse]:
        with get_db_connection() as conn:
            records = WaitlistRepository.get_trip_waitlist(conn, trip_id, seat_class)
            return [WaitlistResponse(**r) for r in records]

    @staticmethod
    def add_to_waitlist(request: WaitlistCreateRequest) -> WaitlistResponse:
        with get_db_connection() as conn:
            waitlist_id = WaitlistRepository.add_to_waitlist(
                connection=conn,
                trip_id=request.trip_id,
                passenger_id=request.passenger_id,
                booking_id=request.booking_id,
                seat_class=request.seat_class
            )
            conn.commit()
            queue = WaitlistRepository.get_trip_waitlist(conn, request.trip_id, request.seat_class)
            match = next((q for q in queue if q["waitlist_id"] == waitlist_id), None)
            return WaitlistResponse(**match) if match else None

    @staticmethod
    def promote_passenger(trip_id: int, seat_class: str, freed_seat_id: int) -> WaitlistPromotionResponse:
        with get_db_connection() as conn:
            result = WaitlistRepository.promote_waitlist_passenger(conn, trip_id, seat_class, freed_seat_id)
            conn.commit()
            return WaitlistPromotionResponse(**result)
