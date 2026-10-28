-- =============================================================================
-- TransitMatrix: Intelligent Railway and Public Transit Management System
-- Database Schema Definition (MySQL 8.0+)
-- Storage Engine: InnoDB
-- Character Set: utf8mb4 / Collation: utf8mb4_unicode_ci
-- =============================================================================

CREATE DATABASE IF NOT EXISTS transitmatrix
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE transitmatrix;

-- -----------------------------------------------------------------------------
-- Disable foreign key checks during schema re-creation
-- -----------------------------------------------------------------------------
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS demand_predictions;
DROP TABLE IF EXISTS audit_logs;
DROP TABLE IF EXISTS delays;
DROP TABLE IF EXISTS waitlists;
DROP TABLE IF EXISTS cancellations;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS trip_seat_inventory;
DROP TABLE IF EXISTS trips;
DROP TABLE IF EXISTS seats;
DROP TABLE IF EXISTS vehicles;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS route_stops;
DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS stations;
DROP TABLE IF EXISTS passengers;
DROP TABLE IF EXISTS users;

SET FOREIGN_KEY_CHECKS = 1;

-- =============================================================================
-- 1. USERS TABLE
-- Authentication, authorization roles, and account credentials
-- =============================================================================
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('ADMIN', 'STAFF', 'PASSENGER') NOT NULL DEFAULT 'PASSENGER',
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(20) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_users_username UNIQUE (username),
    CONSTRAINT uq_users_email UNIQUE (email),
    CONSTRAINT uq_users_phone UNIQUE (phone_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 2. PASSENGERS TABLE
-- Profiles of individuals traveling on the transit network
-- =============================================================================
CREATE TABLE passengers (
    passenger_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    gender ENUM('MALE', 'FEMALE', 'OTHER') NOT NULL,
    age INT NOT NULL,
    id_card_type ENUM('AADHAAR', 'PASSPORT', 'PAN', 'VOTER_ID', 'DRIVING_LICENSE') NOT NULL,
    id_card_number VARCHAR(50) NOT NULL,
    email VARCHAR(100) NULL,
    phone_number VARCHAR(20) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_passenger_age CHECK (age >= 1 AND age <= 120),
    CONSTRAINT fk_passengers_user FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 3. STATIONS TABLE
-- Physical railway stations, terminals, and intermediate junctions
-- =============================================================================
CREATE TABLE stations (
    station_id INT AUTO_INCREMENT PRIMARY KEY,
    station_code VARCHAR(10) NOT NULL,
    station_name VARCHAR(100) NOT NULL,
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zone VARCHAR(20) NOT NULL,
    total_platforms INT NOT NULL DEFAULT 2,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_stations_code UNIQUE (station_code),
    CONSTRAINT chk_stations_platforms CHECK (total_platforms >= 1),
    CONSTRAINT chk_stations_latitude CHECK (latitude BETWEEN -90.0000000 AND 90.0000000),
    CONSTRAINT chk_stations_longitude CHECK (longitude BETWEEN -180.0000000 AND 180.0000000)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 4. ROUTES TABLE
-- Defined transit corridors connecting origin and destination stations
-- =============================================================================
CREATE TABLE routes (
    route_id INT AUTO_INCREMENT PRIMARY KEY,
    route_code VARCHAR(20) NOT NULL,
    route_name VARCHAR(100) NOT NULL,
    origin_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    total_distance_km DECIMAL(8, 2) NOT NULL,
    duration_est_minutes INT NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_routes_code UNIQUE (route_code),
    CONSTRAINT chk_routes_diff_stations CHECK (origin_station_id <> destination_station_id),
    CONSTRAINT chk_routes_distance CHECK (total_distance_km > 0.0),
    CONSTRAINT chk_routes_duration CHECK (duration_est_minutes > 0),
    CONSTRAINT fk_routes_origin FOREIGN KEY (origin_station_id)
        REFERENCES stations (station_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_routes_dest FOREIGN KEY (destination_station_id)
        REFERENCES stations (station_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 5. ROUTE STOPS TABLE
-- Ordered sequential intermediate halts along each route
-- =============================================================================
CREATE TABLE route_stops (
    stop_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    station_id INT NOT NULL,
    stop_sequence INT NOT NULL,
    distance_from_origin_km DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    departure_offset_minutes INT NOT NULL DEFAULT 0,
    arrival_offset_minutes INT NOT NULL DEFAULT 0,
    halt_duration_minutes INT NOT NULL DEFAULT 0,
    platform_number INT NOT NULL DEFAULT 1,
    CONSTRAINT uq_route_stop_sequence UNIQUE (route_id, stop_sequence),
    CONSTRAINT uq_route_stop_station UNIQUE (route_id, station_id),
    CONSTRAINT chk_route_stop_seq CHECK (stop_sequence >= 1),
    CONSTRAINT chk_route_stop_distance CHECK (distance_from_origin_km >= 0.0),
    CONSTRAINT chk_route_stop_halt CHECK (halt_duration_minutes >= 0),
    CONSTRAINT fk_route_stops_route FOREIGN KEY (route_id)
        REFERENCES routes (route_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_route_stops_station FOREIGN KEY (station_id)
        REFERENCES stations (station_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 6. SERVICES TABLE
-- Scheduled train service catalogs (e.g. Rajdhani, Shatabdi, Vande Bharat)
-- =============================================================================
CREATE TABLE services (
    service_id INT AUTO_INCREMENT PRIMARY KEY,
    service_number VARCHAR(20) NOT NULL,
    service_name VARCHAR(100) NOT NULL,
    service_type ENUM('RAJDHANI', 'SHATABDI', 'VANDE_BHARAT', 'SUPERFAST', 'EXPRESS', 'INTERCITY', 'SUBURBAN') NOT NULL,
    operating_days VARCHAR(50) NOT NULL DEFAULT 'MON,TUE,WED,THU,FRI,SAT,SUN',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_services_number UNIQUE (service_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 7. VEHICLES TABLE
-- Physical rolling stock train rakes assigned to operate trips
-- =============================================================================
CREATE TABLE vehicles (
    vehicle_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(30) NOT NULL,
    vehicle_type ENUM('LOCOMOTIVE_TRAIN', 'ELECTRIC_MULTIPLE_UNIT', 'METRO_RAIL', 'DIESEL_MULTIPLE_UNIT') NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    manufacture_year INT NOT NULL,
    total_coaches INT NOT NULL,
    total_capacity INT NOT NULL,
    maintenance_status ENUM('OPERATIONAL', 'UNDER_MAINTENANCE', 'DECOMMISSIONED') NOT NULL DEFAULT 'OPERATIONAL',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_vehicles_number UNIQUE (vehicle_number),
    CONSTRAINT chk_vehicles_coaches CHECK (total_coaches >= 1),
    CONSTRAINT chk_vehicles_capacity CHECK (total_capacity >= 1),
    CONSTRAINT chk_vehicles_year CHECK (manufacture_year >= 1990)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 8. SEATS TABLE
-- Physical seat positions within each coach of a vehicle
-- =============================================================================
CREATE TABLE seats (
    seat_id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_id INT NOT NULL,
    coach_number VARCHAR(10) NOT NULL,
    seat_number VARCHAR(10) NOT NULL,
    seat_class ENUM('1A', '2A', '3A', 'SL', 'CC', 'EC', 'GEN') NOT NULL,
    seat_type ENUM('LOWER', 'MIDDLE', 'UPPER', 'SIDE_LOWER', 'SIDE_UPPER', 'WINDOW', 'AISLE') NOT NULL,
    fare_multiplier DECIMAL(4, 2) NOT NULL DEFAULT 1.00,
    CONSTRAINT uq_vehicle_coach_seat UNIQUE (vehicle_id, coach_number, seat_number),
    CONSTRAINT chk_seats_multiplier CHECK (fare_multiplier > 0.0),
    CONSTRAINT fk_seats_vehicle FOREIGN KEY (vehicle_id)
        REFERENCES vehicles (vehicle_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 9. TRIPS TABLE
-- Specific date-bound journey instances for a service on a route
-- =============================================================================
CREATE TABLE trips (
    trip_id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    route_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    trip_date DATE NOT NULL,
    scheduled_departure DATETIME NOT NULL,
    scheduled_arrival DATETIME NOT NULL,
    actual_departure DATETIME NULL,
    actual_arrival DATETIME NULL,
    status ENUM('SCHEDULED', 'BOARDING', 'ON_TIME', 'DELAYED', 'CANCELLED', 'COMPLETED') NOT NULL DEFAULT 'SCHEDULED',
    base_fare DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_service_trip_date UNIQUE (service_id, trip_date),
    CONSTRAINT chk_trips_times CHECK (scheduled_arrival > scheduled_departure),
    CONSTRAINT chk_trips_fare CHECK (base_fare > 0.0),
    CONSTRAINT fk_trips_service FOREIGN KEY (service_id)
        REFERENCES services (service_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_trips_route FOREIGN KEY (route_id)
        REFERENCES routes (route_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_trips_vehicle FOREIGN KEY (vehicle_id)
        REFERENCES vehicles (vehicle_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 10. TRIP SEAT INVENTORY TABLE
-- Real-time availability state for each seat on a given trip
-- =============================================================================
CREATE TABLE trip_seat_inventory (
    inventory_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    seat_id INT NOT NULL,
    is_available BOOLEAN NOT NULL DEFAULT TRUE,
    reserved_at DATETIME NULL,
    held_until DATETIME NULL,
    lock_version INT NOT NULL DEFAULT 0,
    CONSTRAINT uq_trip_seat_inventory UNIQUE (trip_id, seat_id),
    CONSTRAINT fk_inventory_trip FOREIGN KEY (trip_id)
        REFERENCES trips (trip_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_inventory_seat FOREIGN KEY (seat_id)
        REFERENCES seats (seat_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 11. BOOKINGS TABLE
-- Reservation header representing a transaction by a user
-- =============================================================================
CREATE TABLE bookings (
    booking_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_reference VARCHAR(12) NOT NULL,
    user_id INT NOT NULL,
    trip_id INT NOT NULL,
    booking_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    total_passengers INT NOT NULL,
    total_fare DECIMAL(10, 2) NOT NULL,
    booking_status ENUM('PENDING', 'CONFIRMED', 'CANCELLED', 'PARTIALLY_CANCELLED', 'WAITLISTED') NOT NULL DEFAULT 'PENDING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_bookings_reference UNIQUE (booking_reference),
    CONSTRAINT chk_bookings_passengers CHECK (total_passengers >= 1),
    CONSTRAINT chk_bookings_fare CHECK (total_fare >= 0.0),
    CONSTRAINT fk_bookings_user FOREIGN KEY (user_id)
        REFERENCES users (user_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_trip FOREIGN KEY (trip_id)
        REFERENCES trips (trip_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 12. TICKETS TABLE
-- Individual passenger ticket issuance linked to bookings and seats
-- =============================================================================
CREATE TABLE tickets (
    ticket_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    passenger_id INT NOT NULL,
    seat_id INT NULL,
    origin_station_id INT NOT NULL,
    destination_station_id INT NOT NULL,
    ticket_number VARCHAR(25) NOT NULL,
    fare_amount DECIMAL(10, 2) NOT NULL,
    ticket_status ENUM('CONFIRMED', 'CANCELLED', 'WAITLISTED', 'RAC') NOT NULL DEFAULT 'CONFIRMED',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_tickets_number UNIQUE (ticket_number),
    CONSTRAINT chk_tickets_fare CHECK (fare_amount >= 0.0),
    CONSTRAINT fk_tickets_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_tickets_passenger FOREIGN KEY (passenger_id)
        REFERENCES passengers (passenger_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_tickets_seat FOREIGN KEY (seat_id)
        REFERENCES seats (seat_id)
        ON UPDATE CASCADE
        ON DELETE SET NULL,
    CONSTRAINT fk_tickets_origin FOREIGN KEY (origin_station_id)
        REFERENCES stations (station_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_tickets_dest FOREIGN KEY (destination_station_id)
        REFERENCES stations (station_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 13. PAYMENTS TABLE
-- Payment settlement records associated with bookings
-- =============================================================================
CREATE TABLE payments (
    payment_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    transaction_reference VARCHAR(64) NOT NULL,
    payment_method ENUM('CREDIT_CARD', 'DEBIT_CARD', 'UPI', 'NET_BANKING', 'WALLET') NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_status ENUM('SUCCESS', 'FAILED', 'REFUNDED', 'PENDING') NOT NULL DEFAULT 'PENDING',
    paid_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_payments_txn_ref UNIQUE (transaction_reference),
    CONSTRAINT chk_payments_amount CHECK (amount > 0.0),
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 14. CANCELLATIONS TABLE
-- Ticket cancellation logs and refund calculations
-- =============================================================================
CREATE TABLE cancellations (
    cancellation_id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    ticket_id INT NOT NULL,
    cancellation_reason VARCHAR(255) NULL,
    cancellation_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    refund_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    refund_status ENUM('PROCESSED', 'PENDING', 'REJECTED') NOT NULL DEFAULT 'PENDING',
    cancelled_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_cancellations_ticket UNIQUE (ticket_id),
    CONSTRAINT chk_cancellations_fee CHECK (cancellation_fee >= 0.0),
    CONSTRAINT chk_cancellations_refund CHECK (refund_amount >= 0.0),
    CONSTRAINT fk_cancellations_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_cancellations_ticket FOREIGN KEY (ticket_id)
        REFERENCES tickets (ticket_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 15. WAITLISTS TABLE
-- Waitlist management queue for fully booked journeys
-- =============================================================================
CREATE TABLE waitlists (
    waitlist_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    passenger_id INT NOT NULL,
    booking_id INT NOT NULL,
    seat_class ENUM('1A', '2A', '3A', 'SL', 'CC', 'EC', 'GEN') NOT NULL,
    waitlist_number INT NOT NULL,
    status ENUM('WAITING', 'CONFIRMED', 'CANCELLED', 'EXPIRED') NOT NULL DEFAULT 'WAITING',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_waitlists_queue UNIQUE (trip_id, seat_class, waitlist_number),
    CONSTRAINT chk_waitlists_num CHECK (waitlist_number >= 1),
    CONSTRAINT fk_waitlists_trip FOREIGN KEY (trip_id)
        REFERENCES trips (trip_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_waitlists_passenger FOREIGN KEY (passenger_id)
        REFERENCES passengers (passenger_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT,
    CONSTRAINT fk_waitlists_booking FOREIGN KEY (booking_id)
        REFERENCES bookings (booking_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 16. DELAYS TABLE
-- Trip delay events recorded at transit stations
-- =============================================================================
CREATE TABLE delays (
    delay_id INT AUTO_INCREMENT PRIMARY KEY,
    trip_id INT NOT NULL,
    station_id INT NOT NULL,
    delay_minutes INT NOT NULL,
    delay_reason ENUM('WEATHER', 'TRACK_MAINTENANCE', 'SIGNAL_FAILURE', 'CONGESTION', 'TECHNICAL_GLITCH', 'ACCIDENT', 'OTHER') NOT NULL,
    remarks VARCHAR(255) NULL,
    recorded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_delays_minutes CHECK (delay_minutes >= 0),
    CONSTRAINT fk_delays_trip FOREIGN KEY (trip_id)
        REFERENCES trips (trip_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE,
    CONSTRAINT fk_delays_station FOREIGN KEY (station_id)
        REFERENCES stations (station_id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 17. AUDIT LOGS TABLE
-- Security and compliance audit history tracking DML changes
-- =============================================================================
CREATE TABLE audit_logs (
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id VARCHAR(50) NOT NULL,
    action ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
    old_values JSON NULL,
    new_values JSON NULL,
    changed_by VARCHAR(100) NOT NULL DEFAULT 'SYSTEM',
    changed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================================================
-- 18. DEMAND PREDICTIONS TABLE
-- Machine learning forecasted passenger demands per route
-- =============================================================================
CREATE TABLE demand_predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    route_id INT NOT NULL,
    prediction_date DATE NOT NULL,
    predicted_passenger_demand INT NOT NULL,
    confidence_lower_bound INT NOT NULL,
    confidence_upper_bound INT NOT NULL,
    model_name VARCHAR(50) NOT NULL DEFAULT 'RandomForestRegressor',
    model_version VARCHAR(20) NOT NULL DEFAULT 'v1.0',
    generated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_predictions_date_model UNIQUE (route_id, prediction_date, model_version),
    CONSTRAINT chk_pred_demand CHECK (predicted_passenger_demand >= 0),
    CONSTRAINT chk_pred_lower CHECK (confidence_lower_bound >= 0),
    CONSTRAINT chk_pred_upper CHECK (confidence_upper_bound >= confidence_lower_bound),
    CONSTRAINT fk_predictions_route FOREIGN KEY (route_id)
        REFERENCES routes (route_id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

