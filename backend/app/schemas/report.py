# TransitMatrix - Reporting and Analytics Pydantic Schemas

from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime


class RoutePerformanceReportItem(BaseModel):
    route_id: int
    route_code: str
    route_name: str
    total_distance_km: float
    total_trips_scheduled: int
    delayed_trips_count: int
    total_passengers_booked: int
    gross_revenue: float
    total_refunds: float
    net_revenue: float

    class Config:
        from_attributes = True


class MonthlyRevenueReportItem(BaseModel):
    revenue_month: str
    route_code: str
    route_name: str
    service_type: str
    total_bookings: int
    confirmed_tickets: int
    total_collected_amount: float
    total_refund_amount: float
    net_monthly_revenue: float

    class Config:
        from_attributes = True


class TripAvailabilityReportItem(BaseModel):
    trip_id: int
    service_number: str
    service_name: str
    route_code: str
    trip_date: date
    scheduled_departure: datetime
    trip_status: str
    seat_class: str
    total_class_capacity: int
    available_seats: int
    reserved_seats: int
    occupancy_pct: float

    class Config:
        from_attributes = True


class DelaySummaryReportItem(BaseModel):
    station_id: int
    station_code: str
    station_name: str
    city: str
    total_delay_incidents: int
    avg_delay_minutes: float
    max_delay_minutes: int
    total_delay_minutes: int
    primary_delay_reason: str

    class Config:
        from_attributes = True
