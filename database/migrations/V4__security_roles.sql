-- =============================================================================
-- Migration V4: Security Roles and RBAC Privilege Grants
-- Author: Person 1 (Database & SQL Engineer)
-- Description: Establishes MySQL 8.0 roles for least-privilege operations
-- =============================================================================

USE transitmatrix;

CREATE ROLE IF NOT EXISTS 'transit_admin_role';
CREATE ROLE IF NOT EXISTS 'transit_operator_role';
CREATE ROLE IF NOT EXISTS 'transit_passenger_role';
CREATE ROLE IF NOT EXISTS 'transit_analyst_role';

GRANT ALL PRIVILEGES ON transitmatrix.* TO 'transit_admin_role';

GRANT SELECT, INSERT, UPDATE ON transitmatrix.trips TO 'transit_operator_role';
GRANT SELECT, UPDATE ON transitmatrix.trip_seat_inventory TO 'transit_operator_role';
GRANT SELECT, INSERT, UPDATE ON transitmatrix.bookings TO 'transit_operator_role';
GRANT SELECT, INSERT, UPDATE ON transitmatrix.tickets TO 'transit_operator_role';
GRANT SELECT, INSERT ON transitmatrix.payments TO 'transit_operator_role';
GRANT SELECT, INSERT ON transitmatrix.cancellations TO 'transit_operator_role';
GRANT SELECT, INSERT, UPDATE ON transitmatrix.waitlists TO 'transit_operator_role';
GRANT SELECT, INSERT ON transitmatrix.delays TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.stations TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.routes TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.route_stops TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.services TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.vehicles TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.seats TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.passengers TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.v_booking_details TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.v_trip_availability TO 'transit_operator_role';
GRANT SELECT ON transitmatrix.v_delay_summary TO 'transit_operator_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_search_trips TO 'transit_operator_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_get_seat_availability TO 'transit_operator_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_create_atomic_booking TO 'transit_operator_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_cancel_booking TO 'transit_operator_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_record_trip_delay TO 'transit_operator_role';

GRANT SELECT ON transitmatrix.stations TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.routes TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.route_stops TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.services TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.trips TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.seats TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.v_trip_availability TO 'transit_passenger_role';
GRANT SELECT ON transitmatrix.v_passenger_travel_history TO 'transit_passenger_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_search_trips TO 'transit_passenger_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_get_seat_availability TO 'transit_passenger_role';

GRANT SELECT ON transitmatrix.v_booking_details TO 'transit_analyst_role';
GRANT SELECT ON transitmatrix.v_trip_availability TO 'transit_analyst_role';
GRANT SELECT ON transitmatrix.v_route_performance TO 'transit_analyst_role';
GRANT SELECT ON transitmatrix.v_monthly_revenue TO 'transit_analyst_role';
GRANT SELECT ON transitmatrix.v_delay_summary TO 'transit_analyst_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON transitmatrix.demand_predictions TO 'transit_analyst_role';
GRANT SELECT ON transitmatrix.audit_logs TO 'transit_analyst_role';
GRANT EXECUTE ON PROCEDURE transitmatrix.sp_route_revenue_report TO 'transit_analyst_role';

-- -----------------------------------------------------------------------------
-- Users Provisioning and Default Roles
-- -----------------------------------------------------------------------------
CREATE USER IF NOT EXISTS 'tm_admin'@'%' IDENTIFIED BY 'AdminTransit#2026';
CREATE USER IF NOT EXISTS 'tm_operator'@'%' IDENTIFIED BY 'OperatorTransit#2026';
CREATE USER IF NOT EXISTS 'tm_passenger'@'%' IDENTIFIED BY 'PassengerTransit#2026';
CREATE USER IF NOT EXISTS 'tm_analyst'@'%' IDENTIFIED BY 'AnalystTransit#2026';

GRANT 'transit_admin_role' TO 'tm_admin'@'%';
GRANT 'transit_operator_role' TO 'tm_operator'@'%';
GRANT 'transit_passenger_role' TO 'tm_passenger'@'%';
GRANT 'transit_analyst_role' TO 'tm_analyst'@'%';

SET DEFAULT ROLE 'transit_admin_role' FOR 'tm_admin'@'%';
SET DEFAULT ROLE 'transit_operator_role' FOR 'tm_operator'@'%';
SET DEFAULT ROLE 'transit_passenger_role' FOR 'tm_passenger'@'%';
SET DEFAULT ROLE 'transit_analyst_role' FOR 'tm_analyst'@'%';

FLUSH PRIVILEGES;

