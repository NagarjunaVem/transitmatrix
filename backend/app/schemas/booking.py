# TransitMatrix - Booking and Ticket Pydantic Schemas

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BookingPassengerItem(BaseModel):
    passenger_id: int
    seat_id: int
    origin_station_id: int
    destination_station_id: int


class BookingCreateRequest(BaseModel):
    trip_id: int
    passengers: List[BookingPassengerItem] = Field(..., min_length=1)
    payment_method: str = Field("UPI", pattern="^(CREDIT_CARD|DEBIT_CARD|UPI|NET_BANKING|WALLET)$")


class TicketResponse(BaseModel):
    ticket_id: int
    booking_id: int
    ticket_number: str
    passenger_id: int
    passenger_name: Optional[str] = None
    seat_id: Optional[int] = None
    coach_number: Optional[str] = None
    seat_number: Optional[str] = None
    seat_class: Optional[str] = None
    seat_type: Optional[str] = None
    origin_station_id: int
    origin_station_name: Optional[str] = None
    destination_station_id: int
    destination_station_name: Optional[str] = None
    fare_amount: float
    ticket_status: str
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookingResponse(BaseModel):
    booking_id: int
    booking_reference: str
    user_id: int
    trip_id: int
    booking_date: datetime
    total_passengers: int
    total_fare: float
    booking_status: str
    tickets: List[TicketResponse] = []

    class Config:
        from_attributes = True


class SeatMapItem(BaseModel):
    seat_id: int
    coach_number: str
    seat_number: str
    seat_class: str
    seat_type: str
    fare_multiplier: float
    is_available: bool

    class Config:
        from_attributes = True
