-- =============================================================================
-- TransitMatrix: Query-Driven Indexes Specification
-- Storage Engine: InnoDB (B-Tree Indexes)
-- MySQL 8.0+ Compatible
-- =============================================================================

USE transitmatrix;

-- -----------------------------------------------------------------------------
-- 1. Index on Trips for Route and Date Searches
-- Query Pattern: Passenger searching for trains between two stations on a date.
-- Filters: WHERE route_id = ? AND trip_date = ? AND status IN (...)
-- -----------------------------------------------------------------------------
CREATE INDEX idx_trips_route_date_status 
ON trips (route_id, trip_date, status);

-- -----------------------------------------------------------------------------
-- 2. Index on Trip Seat Inventory for Availability and Locking
-- Query Pattern: SELECT ... FOR UPDATE or counting available seats per class.
-- Filters: WHERE trip_id = ? AND is_available = TRUE
-- -----------------------------------------------------------------------------
CREATE INDEX idx_inventory_trip_avail 
ON trip_seat_inventory (trip_id, is_available);

-- -----------------------------------------------------------------------------
-- 3. Composite Index on Route Stops for Journey Planning (Station A -> Station B)
-- Query Pattern: Finding routes where origin stop sequence < destination stop sequence.
-- Filters: WHERE station_id = ? JOIN route_stops on route_id
-- -----------------------------------------------------------------------------
CREATE INDEX idx_route_stops_station_seq 
ON route_stops (station_id, route_id, stop_sequence);

-- -----------------------------------------------------------------------------
-- 4. Index on Bookings for User History and Status
-- Query Pattern: Customer viewing past and upcoming bookings ordered by date.
-- Filters: WHERE user_id = ? ORDER BY booking_date DESC
-- -----------------------------------------------------------------------------
CREATE INDEX idx_bookings_user_date 
ON bookings (user_id, booking_date DESC);

-- -----------------------------------------------------------------------------
-- 5. Index on Tickets for Booking Child Lookups
-- Query Pattern: Retrieving all passenger tickets for a given booking.
-- Filters: WHERE booking_id = ?
-- -----------------------------------------------------------------------------
CREATE INDEX idx_tickets_booking_id 
ON tickets (booking_id);

-- -----------------------------------------------------------------------------
-- 6. Index on Tickets for Passenger Travel History
-- Query Pattern: Fetching traveler tickets by ID and status.
-- Filters: WHERE passenger_id = ? AND ticket_status = ?
-- -----------------------------------------------------------------------------
CREATE INDEX idx_tickets_passenger_status 
ON tickets (passenger_id, ticket_status);

-- -----------------------------------------------------------------------------
-- 7. Index on Payments for Verification and Settlement
-- Query Pattern: Auditing payments by booking and settlement status.
-- Filters: WHERE booking_id = ? AND payment_status = ?
-- -----------------------------------------------------------------------------
CREATE INDEX idx_payments_booking_status 
ON payments (booking_id, payment_status);

-- -----------------------------------------------------------------------------
-- 8. Index on Waitlists for Queue FIFO Promotion
-- Query Pattern: Finding the first waiting passenger to promote upon cancellation.
-- Filters: WHERE trip_id = ? AND seat_class = ? AND status = 'WAITING' ORDER BY waitlist_number ASC
-- -----------------------------------------------------------------------------
CREATE INDEX idx_waitlists_queue_search 
ON waitlists (trip_id, seat_class, status, waitlist_number ASC);

-- -----------------------------------------------------------------------------
-- 9. Index on Delays for Punctuality Reporting
-- Query Pattern: Aggregating delays per trip or station over time.
-- Filters: WHERE trip_id = ? ORDER BY recorded_at DESC
-- -----------------------------------------------------------------------------
CREATE INDEX idx_delays_trip_recorded 
ON delays (trip_id, recorded_at);

-- -----------------------------------------------------------------------------
-- 10. Index on Machine Learning Demand Predictions
-- Query Pattern: Fetching forecasted passenger demands for dashboard visualization.
-- Filters: WHERE route_id = ? AND prediction_date BETWEEN ? AND ?
-- -----------------------------------------------------------------------------
CREATE INDEX idx_predictions_route_date 
ON demand_predictions (route_id, prediction_date);

-- -----------------------------------------------------------------------------
-- 11. Index on Audit Logs for Administrative Inspection
-- Query Pattern: Viewing change log history for a table or record.
-- Filters: WHERE table_name = ? AND record_id = ? ORDER BY changed_at DESC
-- -----------------------------------------------------------------------------
CREATE INDEX idx_audit_table_record 
ON audit_logs (table_name, record_id, changed_at DESC);

