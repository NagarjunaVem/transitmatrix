-- =============================================================================
-- Migration V3: Triggers and Stored Procedures for TransitMatrix
-- Author: Person 1 (Database & SQL Engineer)
-- Description: Business rules, audit triggers, and transactional stored procedures
-- =============================================================================

USE transitmatrix;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- Triggers
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_audit_booking_update$$
CREATE TRIGGER trg_audit_booking_update
AFTER UPDATE ON bookings
FOR EACH ROW
BEGIN
    IF OLD.booking_status <> NEW.booking_status OR OLD.total_fare <> NEW.total_fare THEN
        INSERT INTO audit_logs (
            table_name,
            record_id,
            action,
            old_values,
            new_values,
            changed_by,
            changed_at
        ) VALUES (
            'bookings',
            CAST(NEW.booking_id AS CHAR),
            'UPDATE',
            JSON_OBJECT(
                'booking_status', OLD.booking_status,
                'total_fare', OLD.total_fare,
                'total_passengers', OLD.total_passengers
            ),
            JSON_OBJECT(
                'booking_status', NEW.booking_status,
                'total_fare', NEW.total_fare,
                'total_passengers', NEW.total_passengers
            ),
            USER(),
            NOW()
        );
    END IF;
END$$

DROP TRIGGER IF EXISTS trg_cancellation_after_insert$$
CREATE TRIGGER trg_cancellation_after_insert
AFTER INSERT ON cancellations
FOR EACH ROW
BEGIN
    DECLARE v_seat_id INT;
    DECLARE v_trip_id INT;

    SELECT t.seat_id, b.trip_id 
    INTO v_seat_id, v_trip_id
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    WHERE t.ticket_id = NEW.ticket_id;

    UPDATE tickets 
    SET ticket_status = 'CANCELLED'
    WHERE ticket_id = NEW.ticket_id;

    IF v_seat_id IS NOT NULL AND v_trip_id IS NOT NULL THEN
        UPDATE trip_seat_inventory
        SET is_available = TRUE,
            reserved_at = NULL,
            lock_version = lock_version + 1
        WHERE trip_id = v_trip_id 
          AND seat_id = v_seat_id;
    END IF;

    INSERT INTO audit_logs (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        changed_by,
        changed_at
    ) VALUES (
        'cancellations',
        CAST(NEW.cancellation_id AS CHAR),
        'INSERT',
        NULL,
        JSON_OBJECT(
            'booking_id', NEW.booking_id,
            'ticket_id', NEW.ticket_id,
            'cancellation_fee', NEW.cancellation_fee,
            'refund_amount', NEW.refund_amount,
            'refund_status', NEW.refund_status
        ),
        USER(),
        NOW()
    );
END$$

DROP TRIGGER IF EXISTS trg_delays_after_insert$$
CREATE TRIGGER trg_delays_after_insert
AFTER INSERT ON delays
FOR EACH ROW
BEGIN
    IF NEW.delay_minutes >= 15 THEN
        UPDATE trips
        SET status = 'DELAYED'
        WHERE trip_id = NEW.trip_id
          AND status IN ('SCHEDULED', 'BOARDING', 'ON_TIME');
    END IF;

    INSERT INTO audit_logs (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        changed_by,
        changed_at
    ) VALUES (
        'delays',
        CAST(NEW.delay_id AS CHAR),
        'INSERT',
        NULL,
        JSON_OBJECT(
            'trip_id', NEW.trip_id,
            'station_id', NEW.station_id,
            'delay_minutes', NEW.delay_minutes,
            'delay_reason', NEW.delay_reason
        ),
        USER(),
        NOW()
    );
END$$

DROP TRIGGER IF EXISTS trg_payments_after_insert$$
CREATE TRIGGER trg_payments_after_insert
AFTER INSERT ON payments
FOR EACH ROW
BEGIN
    INSERT INTO audit_logs (
        table_name,
        record_id,
        action,
        old_values,
        new_values,
        changed_by,
        changed_at
    ) VALUES (
        'payments',
        CAST(NEW.payment_id AS CHAR),
        'INSERT',
        NULL,
        JSON_OBJECT(
            'booking_id', NEW.booking_id,
            'transaction_reference', NEW.transaction_reference,
            'amount', NEW.amount,
            'payment_status', NEW.payment_status,
            'payment_method', NEW.payment_method
        ),
        USER(),
        NOW()
    );
END$$

DROP TRIGGER IF EXISTS trg_validate_seat_inventory_before_insert$$
CREATE TRIGGER trg_validate_seat_inventory_before_insert
BEFORE INSERT ON trip_seat_inventory
FOR EACH ROW
BEGIN
    DECLARE v_trip_vehicle_id INT;
    DECLARE v_seat_vehicle_id INT;

    SELECT vehicle_id INTO v_trip_vehicle_id FROM trips WHERE trip_id = NEW.trip_id;
    SELECT vehicle_id INTO v_seat_vehicle_id FROM seats WHERE seat_id = NEW.seat_id;

    IF v_trip_vehicle_id IS NULL OR v_seat_vehicle_id IS NULL OR v_trip_vehicle_id <> v_seat_vehicle_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Integrity Error: Seat does not belong to the vehicle assigned to this trip.';
    END IF;
END$$

-- -----------------------------------------------------------------------------
-- Stored Procedures
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

    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_booking_id = NULL;
        SET p_ticket_number = NULL;
        SET p_status_message = 'ERROR: Transaction rolled back due to database exception.';
    END;

    START TRANSACTION;

    SELECT is_available INTO v_is_available
    FROM trip_seat_inventory
    WHERE trip_id = p_trip_id 
      AND seat_id = p_seat_id
    FOR UPDATE;

    IF v_is_available <> 1 THEN
        ROLLBACK;
        SET p_booking_id = NULL;
        SET p_ticket_number = NULL;
        SET p_status_message = 'FAILED: Requested seat is unavailable or already reserved.';
        LEAVE proc_block;
    END IF;

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

    COMMIT;

    SET p_booking_id = v_new_booking_id;
    SET p_ticket_number = v_ticket_no;
    SET p_status_message = 'SUCCESS: Booking and ticket confirmed successfully.';
END$$

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

    SET v_cancellation_fee = ROUND(v_fare_amount * 0.15, 2);
    SET p_refund_amount = ROUND(v_fare_amount - v_cancellation_fee, 2);

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

    IF (SELECT COUNT(*) FROM tickets WHERE booking_id = v_booking_id AND ticket_status <> 'CANCELLED') = 0 THEN
        UPDATE bookings SET booking_status = 'CANCELLED' WHERE booking_id = v_booking_id;
    ELSE
        UPDATE bookings SET booking_status = 'PARTIALLY_CANCELLED' WHERE booking_id = v_booking_id;
    END IF;

    COMMIT;

    IF v_seat_id IS NOT NULL AND v_seat_class IS NOT NULL THEN
        CALL sp_process_waitlist_promotion(v_trip_id, v_seat_class, v_seat_id, v_promoted_pid, v_promo_msg);
    END IF;

    SET p_status_message = 'SUCCESS: Ticket cancelled and refund processed.';
END$$

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

    UPDATE trip_seat_inventory
    SET is_available = FALSE,
        reserved_at = NOW(),
        lock_version = lock_version + 1
    WHERE trip_id = p_trip_id 
      AND seat_id = p_freed_seat_id;

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

    UPDATE waitlists
    SET status = 'CONFIRMED'
    WHERE waitlist_id = v_waitlist_id;

    UPDATE bookings
    SET booking_status = 'CONFIRMED'
    WHERE booking_id = v_booking_id;

    COMMIT;

    SET p_promoted_passenger_id = v_passenger_id;
    SET p_status_message = 'SUCCESS: Waitlisted passenger successfully promoted.';
END$$

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

