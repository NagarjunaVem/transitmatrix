-- =============================================================================
-- TransitMatrix: Stored Procedures Specification
-- Storage Engine: InnoDB
-- MySQL 8.0+ Compatible
-- =============================================================================

USE transitmatrix;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. Procedure: sp_search_trips
-- Searches for available trips between an origin station and a destination
-- station on a specific date, checking route sequence and counting open seats.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_search_trips$$
CREATE PROCEDURE sp_search_trips(
    IN p_origin_code VARCHAR(10),
    IN p_destination_code VARCHAR(10),
    IN p_travel_date DATE
)
BEGIN
    SELECT 
        tr.trip_id,
        s.service_number,
        s.service_name,
        s.service_type,
        r.route_code,
        r.route_name,
        tr.trip_date,
        tr.scheduled_departure,
        tr.scheduled_arrival,
        tr.status AS trip_status,
        tr.base_fare,
        st_orig.station_name AS origin_station_name,
        st_dest.station_name AS destination_station_name,
        COUNT(tsi.inventory_id) AS total_seats,
        SUM(CASE WHEN tsi.is_available = TRUE THEN 1 ELSE 0 END) AS available_seats
    FROM trips tr
    JOIN services s ON tr.service_id = s.service_id
    JOIN routes r ON tr.route_id = r.route_id
    JOIN route_stops rs_orig ON r.route_id = rs_orig.route_id
    JOIN stations st_orig ON rs_orig.station_id = st_orig.station_id
    JOIN route_stops rs_dest ON r.route_id = rs_dest.route_id
    JOIN stations st_dest ON rs_dest.station_id = st_dest.station_id
    LEFT JOIN trip_seat_inventory tsi ON tr.trip_id = tsi.trip_id
    WHERE st_orig.station_code = p_origin_code
      AND st_dest.station_code = p_destination_code
      AND rs_orig.stop_sequence < rs_dest.stop_sequence
      AND tr.trip_date = p_travel_date
      AND tr.status NOT IN ('CANCELLED', 'COMPLETED')
    GROUP BY 
        tr.trip_id, s.service_number, s.service_name, s.service_type,
        r.route_code, r.route_name, tr.trip_date, tr.scheduled_departure,
        tr.scheduled_arrival, tr.status, tr.base_fare,
        st_orig.station_name, st_dest.station_name
    ORDER BY tr.scheduled_departure ASC;
END$$

-- -----------------------------------------------------------------------------
-- 2. Procedure: sp_get_seat_availability
-- Returns real-time coach-level seat layout and vacancy state for a trip.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_get_seat_availability$$
CREATE PROCEDURE sp_get_seat_availability(
    IN p_trip_id INT,
    IN p_coach_number VARCHAR(10)
)
BEGIN
    SELECT 
        st.seat_id,
        st.coach_number,
        st.seat_number,
        st.seat_class,
        st.seat_type,
        st.fare_multiplier,
        ROUND(tr.base_fare * st.fare_multiplier, 2) AS calculated_fare,
        tsi.is_available
    FROM trip_seat_inventory tsi
    JOIN seats st ON tsi.seat_id = st.seat_id
    JOIN trips tr ON tsi.trip_id = tr.trip_id
    WHERE tsi.trip_id = p_trip_id
      AND (p_coach_number IS NULL OR st.coach_number = p_coach_number)
    ORDER BY st.coach_number ASC, CAST(st.seat_number AS UNSIGNED) ASC;
END$$

-- -----------------------------------------------------------------------------
-- 3. Procedure: sp_create_atomic_booking
-- Full transactional reservation with row-level locking (SELECT ... FOR UPDATE).
-- Implements atomicity: reserves seat, inserts booking, issues ticket, and logs payment.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_create_atomic_booking$$
CREATE PROCEDURE sp_create_atomic_booking(
    IN p_user_id INT,
    IN p_trip_id INT,
    IN p_origin_station_id INT,
    IN p_dest_station_id INT,
    IN p_passenger_id INT,
    IN p_seat_id INT,
    IN p_fare_amount DECIMAL(10, 2),
    IN p_payment_method VARCHAR(20),
    OUT p_booking_id INT,
    OUT p_ticket_number VARCHAR(25),
    OUT p_status_message VARCHAR(100)
)
proc_block: BEGIN
    DECLARE v_is_available INT DEFAULT 0;
    DECLARE v_booking_ref VARCHAR(12);
    DECLARE v_new_booking_id INT;
    DECLARE v_ticket_no VARCHAR(25);
    DECLARE v_txn_ref VARCHAR(64);

    -- Declare error handler to rollback on any SQLEXCEPTION
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_booking_id = NULL;
        SET p_ticket_number = NULL;
        SET p_status_message = 'ERROR: Transaction rolled back due to database exception.';
    END;

    START TRANSACTION;

    -- Step 1: Exclusive Row Lock on the specific seat inventory
    SELECT is_available INTO v_is_available
    FROM trip_seat_inventory
    WHERE trip_id = p_trip_id 
      AND seat_id = p_seat_id
    FOR UPDATE;

    -- If seat does not exist or is already taken, abort and rollback
    IF v_is_available <> 1 THEN
        ROLLBACK;
        SET p_booking_id = NULL;
        SET p_ticket_number = NULL;
        SET p_status_message = 'FAILED: Requested seat is unavailable or already reserved.';
        LEAVE proc_block;
    END IF;

    -- Step 2: Update Seat Inventory to unavailable
    UPDATE trip_seat_inventory
    SET is_available = FALSE,
        reserved_at = NOW(),
        lock_version = lock_version + 1
    WHERE trip_id = p_trip_id 
      AND seat_id = p_seat_id
      AND is_available = TRUE;

    IF ROW_COUNT() <> 1 THEN
        ROLLBACK;
        SET p_booking_id = NULL;
        SET p_ticket_number = NULL;
        SET p_status_message = 'FAILED: Concurrency conflict during seat reservation.';
        LEAVE proc_block;
    END IF;

    -- Step 3: Generate PNR Reference and create Booking
    SET v_booking_ref = CONCAT('TM-', LPAD(FLOOR(RAND() * 90000000 + 10000000), 8, '0'));
    
    INSERT INTO bookings (
        booking_reference,
        user_id,
        trip_id,
        booking_date,
        total_passengers,
        total_fare,
        booking_status
    ) VALUES (
        v_booking_ref,
        p_user_id,
        p_trip_id,
        NOW(),
        1,
        p_fare_amount,
        'CONFIRMED'
    );

    SET v_new_booking_id = LAST_INSERT_ID();

    -- Step 4: Issue Passenger Ticket
    SET v_ticket_no = CONCAT('TKT-', DATE_FORMAT(NOW(), '%Y%m%d'), '-', LPAD(v_new_booking_id, 4, '0'));

    INSERT INTO tickets (
        booking_id,
        passenger_id,
        seat_id,
        origin_station_id,
        destination_station_id,
        ticket_number,
        fare_amount,
        ticket_status
    ) VALUES (
        v_new_booking_id,
        p_passenger_id,
        p_seat_id,
        p_origin_station_id,
        p_dest_station_id,
        v_ticket_no,
        p_fare_amount,
        'CONFIRMED'
    );

    -- Step 5: Record Payment
    SET v_txn_ref = CONCAT('TXN-', DATE_FORMAT(NOW(), '%Y%m%d%H%i%s'), '-', LPAD(FLOOR(RAND() * 9000 + 1000), 4, '0'));

    INSERT INTO payments (
        booking_id,
        transaction_reference,
        payment_method,
        amount,
        payment_status,
        paid_at
    ) VALUES (
        v_new_booking_id,
        v_txn_ref,
        p_payment_method,
        p_fare_amount,
        'SUCCESS',
        NOW()
    );

    -- Step 6: Commit Transaction
    COMMIT;

    SET p_booking_id = v_new_booking_id;
    SET p_ticket_number = v_ticket_no;
    SET p_status_message = 'SUCCESS: Booking and ticket confirmed successfully.';
END$$

-- -----------------------------------------------------------------------------
-- 4. Procedure: sp_cancel_booking
-- Cancels a ticket, calculates refund and fee, triggers seat release,
-- and attempts waitlist promotion.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_cancel_booking$$
CREATE PROCEDURE sp_cancel_booking(
    IN p_ticket_id INT,
    IN p_reason VARCHAR(255),
    OUT p_refund_amount DECIMAL(10, 2),
    OUT p_status_message VARCHAR(100)
)
proc_block: BEGIN
    DECLARE v_booking_id INT;
    DECLARE v_fare_amount DECIMAL(10, 2);
    DECLARE v_seat_id INT;
    DECLARE v_trip_id INT;
    DECLARE v_seat_class VARCHAR(10);
    DECLARE v_cancellation_fee DECIMAL(10, 2);
    DECLARE v_ticket_status VARCHAR(20);
    DECLARE v_promoted_pid INT;
    DECLARE v_promo_msg VARCHAR(100);

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_refund_amount = 0.00;
        SET p_status_message = 'ERROR: Cancellation rolled back due to database exception.';
    END;

    START TRANSACTION;

    -- Fetch ticket details with lock
    SELECT 
        t.booking_id, t.fare_amount, t.seat_id, t.ticket_status, b.trip_id, st.seat_class
    INTO 
        v_booking_id, v_fare_amount, v_seat_id, v_ticket_status, v_trip_id, v_seat_class
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    LEFT JOIN seats st ON t.seat_id = st.seat_id
    WHERE t.ticket_id = p_ticket_id
    FOR UPDATE;

    IF v_booking_id IS NULL THEN
        ROLLBACK;
        SET p_refund_amount = 0.00;
        SET p_status_message = 'FAILED: Ticket ID not found.';
        LEAVE proc_block;
    END IF;

    IF v_ticket_status = 'CANCELLED' THEN
        ROLLBACK;
        SET p_refund_amount = 0.00;
        SET p_status_message = 'FAILED: Ticket is already cancelled.';
        LEAVE proc_block;
    END IF;

    -- Cancellation policy: 15% cancellation fee, 85% refund
    SET v_cancellation_fee = ROUND(v_fare_amount * 0.15, 2);
    SET p_refund_amount = ROUND(v_fare_amount - v_cancellation_fee, 2);

    -- Insert into cancellations table (Trigger trg_cancellation_after_insert handles seat release)
    INSERT INTO cancellations (
        booking_id,
        ticket_id,
        cancellation_reason,
        cancellation_fee,
        refund_amount,
        refund_status,
        cancelled_at
    ) VALUES (
        v_booking_id,
        p_ticket_id,
        p_reason,
        v_cancellation_fee,
        p_refund_amount,
        'PROCESSED',
        NOW()
    );

    -- Check if all tickets in this booking are cancelled
    IF (SELECT COUNT(*) FROM tickets WHERE booking_id = v_booking_id AND ticket_status <> 'CANCELLED') = 0 THEN
        UPDATE bookings SET booking_status = 'CANCELLED' WHERE booking_id = v_booking_id;
    ELSE
        UPDATE bookings SET booking_status = 'PARTIALLY_CANCELLED' WHERE booking_id = v_booking_id;
    END IF;

    -- Commit cancellation changes
    COMMIT;

    -- Step 5: Check and promote next eligible passenger from waitlist
    IF v_seat_id IS NOT NULL AND v_seat_class IS NOT NULL THEN
        CALL sp_process_waitlist_promotion(v_trip_id, v_seat_class, v_seat_id, v_promoted_pid, v_promo_msg);
    END IF;

    SET p_status_message = 'SUCCESS: Ticket cancelled and refund processed.';
END$$

-- -----------------------------------------------------------------------------
-- 5. Procedure: sp_process_waitlist_promotion
-- Checks if any passenger is waiting in the queue for a trip and seat class,
-- and promotes the top queue item to the freed seat.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_process_waitlist_promotion$$
CREATE PROCEDURE sp_process_waitlist_promotion(
    IN p_trip_id INT,
    IN p_seat_class VARCHAR(10),
    IN p_freed_seat_id INT,
    OUT p_promoted_passenger_id INT,
    OUT p_status_message VARCHAR(100)
)
proc_block: BEGIN
    DECLARE v_waitlist_id INT;
    DECLARE v_passenger_id INT;
    DECLARE v_booking_id INT;
    DECLARE v_ticket_id INT;

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_promoted_passenger_id = NULL;
        SET p_status_message = 'ERROR: Waitlist promotion rolled back.';
    END;

    START TRANSACTION;

    -- Find the earliest waiting passenger in queue (FIFO)
    SELECT waitlist_id, passenger_id, booking_id
    INTO v_waitlist_id, v_passenger_id, v_booking_id
    FROM waitlists
    WHERE trip_id = p_trip_id
      AND seat_class = p_seat_class
      AND status = 'WAITING'
    ORDER BY waitlist_number ASC
    LIMIT 1
    FOR UPDATE;

    IF v_waitlist_id IS NULL THEN
        COMMIT;
        SET p_promoted_passenger_id = NULL;
        SET p_status_message = 'NOTICE: No eligible waitlist passengers found.';
        LEAVE proc_block;
    END IF;

    -- Re-allocate the seat inventory
    UPDATE trip_seat_inventory
    SET is_available = FALSE,
        reserved_at = NOW(),
        lock_version = lock_version + 1
    WHERE trip_id = p_trip_id 
      AND seat_id = p_freed_seat_id;

    -- Update the waitlisted ticket
    SELECT ticket_id INTO v_ticket_id
    FROM tickets
    WHERE booking_id = v_booking_id 
      AND passenger_id = v_passenger_id 
      AND ticket_status = 'WAITLISTED'
    LIMIT 1;

    IF v_ticket_id IS NOT NULL THEN
        UPDATE tickets
        SET seat_id = p_freed_seat_id,
            ticket_status = 'CONFIRMED'
        WHERE ticket_id = v_ticket_id;
    END IF;

    -- Mark waitlist entry as CONFIRMED
    UPDATE waitlists
    SET status = 'CONFIRMED'
    WHERE waitlist_id = v_waitlist_id;

    -- Update booking status to CONFIRMED
    UPDATE bookings
    SET booking_status = 'CONFIRMED'
    WHERE booking_id = v_booking_id;

    COMMIT;

    SET p_promoted_passenger_id = v_passenger_id;
    SET p_status_message = 'SUCCESS: Waitlisted passenger successfully promoted.';
END$$

-- -----------------------------------------------------------------------------
-- 6. Procedure: sp_route_revenue_report
-- Generates aggregate financial and operational summary for routes over a period.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_route_revenue_report$$
CREATE PROCEDURE sp_route_revenue_report(
    IN p_start_date DATE,
    IN p_end_date DATE
)
BEGIN
    SELECT 
        r.route_code,
        r.route_name,
        COUNT(DISTINCT b.booking_id) AS total_bookings,
        COUNT(DISTINCT t.ticket_id) AS total_tickets_issued,
        SUM(b.total_fare) AS gross_revenue,
        COALESCE(SUM(c.refund_amount), 0.00) AS total_refunds,
        (SUM(b.total_fare) - COALESCE(SUM(c.refund_amount), 0.00)) AS net_revenue
    FROM routes r
    JOIN trips tr ON r.route_id = tr.route_id
    JOIN bookings b ON tr.trip_id = b.trip_id
    LEFT JOIN tickets t ON b.booking_id = t.booking_id
    LEFT JOIN cancellations c ON t.ticket_id = c.ticket_id
    WHERE tr.trip_date BETWEEN p_start_date AND p_end_date
      AND b.booking_status IN ('CONFIRMED', 'CANCELLED', 'PARTIALLY_CANCELLED')
    GROUP BY r.route_code, r.route_name
    ORDER BY net_revenue DESC;
END$$

-- -----------------------------------------------------------------------------
-- 7. Procedure: sp_record_trip_delay
-- Inserts operational delay and updates trips table status accordingly.
-- -----------------------------------------------------------------------------
DROP PROCEDURE IF EXISTS sp_record_trip_delay$$
CREATE PROCEDURE sp_record_trip_delay(
    IN p_trip_id INT,
    IN p_station_id INT,
    IN p_delay_minutes INT,
    IN p_delay_reason VARCHAR(30),
    IN p_remarks VARCHAR(255)
)
BEGIN
    INSERT INTO delays (
        trip_id,
        station_id,
        delay_minutes,
        delay_reason,
        remarks,
        recorded_at
    ) VALUES (
        p_trip_id,
        p_station_id,
        p_delay_minutes,
        p_delay_reason,
        p_remarks,
        NOW()
    );
END$$

DELIMITER ;

