# TransitMatrix - Transit Network Service
# Coordinates business logic for stations, routes, timetable services, rakes, and journeys.

from fastapi import HTTPException, status
from typing import List, Dict, Any, Optional
from datetime import date
from app.db.connection import get_db_connection
from app.repositories.station_repository import StationRepository
from app.repositories.route_repository import RouteRepository
from app.repositories.service_repository import ServiceRepository
from app.repositories.vehicle_repository import VehicleRepository
from app.repositories.trip_repository import TripRepository
from app.repositories.passenger_repository import PassengerRepository
from app.schemas.station import StationCreate, StationUpdate
from app.schemas.route import RouteCreate, RouteStopCreate
from app.schemas.service import ServiceCreate, ServiceUpdate
from app.schemas.vehicle import VehicleCreate, VehicleUpdate
from app.schemas.trip import TripCreate, TripUpdate
from app.schemas.passenger import PassengerCreate


class TransitService:

    # ---------------- Stations ----------------
    @staticmethod
    def list_stations(limit: int = 100, offset: int = 0, search: Optional[str] = None):
        with get_db_connection() as conn:
            return StationRepository.list_stations(conn, limit, offset, search)

    @staticmethod
    def get_station_by_id(station_id: int):
        with get_db_connection() as conn:
            station = StationRepository.get_by_id(conn, station_id)
            if not station:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
            return station

    @staticmethod
    def create_station(request: StationCreate):
        with get_db_connection() as conn:
            existing = StationRepository.get_by_code(conn, request.station_code)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Station code already exists")
            station_id = StationRepository.create_station(conn, request.model_dump())
            conn.commit()
            return StationRepository.get_by_id(conn, station_id)

    @staticmethod
    def update_station(station_id: int, request: StationUpdate):
        with get_db_connection() as conn:
            station = StationRepository.get_by_id(conn, station_id)
            if not station:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
            StationRepository.update_station(conn, station_id, request.model_dump(exclude_unset=True))
            conn.commit()
            return StationRepository.get_by_id(conn, station_id)

    @staticmethod
    def delete_station(station_id: int):
        with get_db_connection() as conn:
            station = StationRepository.get_by_id(conn, station_id)
            if not station:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Station not found")
            try:
                StationRepository.delete_station(conn, station_id)
                conn.commit()
            except Exception as e:
                conn.rollback()
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot delete station: {e}")
            return {"message": "Station deleted successfully"}

    # ---------------- Routes & Stops ----------------
    @staticmethod
    def list_routes(limit: int = 50, offset: int = 0):
        with get_db_connection() as conn:
            return RouteRepository.list_routes(conn, limit, offset)

    @staticmethod
    def get_route_details(route_id: int):
        with get_db_connection() as conn:
            route = RouteRepository.get_by_id(conn, route_id)
            if not route:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
            stops = RouteRepository.get_route_stops(conn, route_id)
            route["stops"] = stops
            return route

    @staticmethod
    def create_route(request: RouteCreate):
        if request.origin_station_id == request.destination_station_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Origin and destination stations must be different")

        with get_db_connection() as conn:
            existing = RouteRepository.get_by_code(conn, request.route_code)
            if existing:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Route code already exists")
            route_id = RouteRepository.create_route(conn, request.model_dump())
            conn.commit()
            return TransitService.get_route_details(route_id)

    @staticmethod
    def add_route_stop(route_id: int, request: RouteStopCreate):
        with get_db_connection() as conn:
            route = RouteRepository.get_by_id(conn, route_id)
            if not route:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Route not found")
            stop_id = RouteRepository.add_route_stop(conn, route_id, request.model_dump())
            conn.commit()
            return TransitService.get_route_details(route_id)

    # ---------------- Services ----------------
    @staticmethod
    def list_services(limit: int = 50, offset: int = 0):
        with get_db_connection() as conn:
            return ServiceRepository.list_services(conn, limit, offset)

    @staticmethod
    def get_service_by_id(service_id: int):
        with get_db_connection() as conn:
            service = ServiceRepository.get_by_id(conn, service_id)
            if not service:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
            return service

    @staticmethod
    def create_service(request: ServiceCreate):
        with get_db_connection() as conn:
            service_id = ServiceRepository.create_service(conn, request.model_dump())
            conn.commit()
            return ServiceRepository.get_by_id(conn, service_id)

    # ---------------- Vehicles ----------------
    @staticmethod
    def list_vehicles(limit: int = 50, offset: int = 0):
        with get_db_connection() as conn:
            return VehicleRepository.list_vehicles(conn, limit, offset)

    @staticmethod
    def get_vehicle_by_id(vehicle_id: int):
        with get_db_connection() as conn:
            vehicle = VehicleRepository.get_by_id(conn, vehicle_id)
            if not vehicle:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
            return vehicle

    @staticmethod
    def create_vehicle(request: VehicleCreate):
        with get_db_connection() as conn:
            vehicle_id = VehicleRepository.create_vehicle(conn, request.model_dump())
            conn.commit()
            return VehicleRepository.get_by_id(conn, vehicle_id)

    # ---------------- Trips & Search ----------------
    @staticmethod
    def list_trips(limit: int = 50, offset: int = 0, status: Optional[str] = None, trip_date: Optional[date] = None):
        with get_db_connection() as conn:
            return TripRepository.list_trips(conn, limit, offset, status, trip_date)

    @staticmethod
    def get_trip_by_id(trip_id: int):
        with get_db_connection() as conn:
            trip = TripRepository.get_by_id(conn, trip_id)
            if not trip:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
            return trip

    @staticmethod
    def create_trip(request: TripCreate):
        with get_db_connection() as conn:
            trip_id = TripRepository.create_trip(conn, request.model_dump())
            conn.commit()
            return TripRepository.get_by_id(conn, trip_id)

    @staticmethod
    def search_trips(origin_code: str, destination_code: str, travel_date: date):
        with get_db_connection() as conn:
            return TripRepository.search_trips(conn, origin_code, destination_code, travel_date)

    # ---------------- Passengers ----------------
    @staticmethod
    def list_passengers(user_id: Optional[int] = None, limit: int = 50, offset: int = 0):
        with get_db_connection() as conn:
            return PassengerRepository.list_passengers(conn, user_id, limit, offset)

    @staticmethod
    def create_passenger(request: PassengerCreate):
        with get_db_connection() as conn:
            passenger_id = PassengerRepository.create_passenger(conn, request.model_dump())
            conn.commit()
            return PassengerRepository.get_by_id(conn, passenger_id)
