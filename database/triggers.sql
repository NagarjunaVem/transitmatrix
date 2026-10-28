-- =============================================================================
-- TransitMatrix: Database Triggers Specification
-- Storage Engine: InnoDB
-- MySQL 8.0+ Compatible
-- =============================================================================

USE transitmatrix;

DELIMITER $$

-- -----------------------------------------------------------------------------
-- 1. Trigger: trg_audit_booking_update
-- Automatically records booking status updates into audit_logs.
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

-- -----------------------------------------------------------------------------
-- 2. Trigger: trg_cancellation_after_insert
-- When a cancellation record is created:
-- 1) Updates ticket status to 'CANCELLED'.
-- 2) Releases the seat in trip_seat_inventory if the ticket had a seat assigned.
-- -----------------------------------------------------------------------------
DROP TRIGGER IF EXISTS trg_cancellation_after_insert$$
CREATE TRIGGER trg_cancellation_after_insert
AFTER INSERT ON cancellations
FOR EACH ROW
BEGIN
    DECLARE v_seat_id INT;
    DECLARE v_trip_id INT;

    -- Fetch the seat_id and trip_id for the cancelled ticket
    SELECT t.seat_id, b.trip_id 
    INTO v_seat_id, v_trip_id
    FROM tickets t
    JOIN bookings b ON t.booking_id = b.booking_id
    WHERE t.ticket_id = NEW.ticket_id;

    -- Mark the ticket status as CANCELLED
    UPDATE tickets 
    SET ticket_status = 'CANCELLED'
    WHERE ticket_id = NEW.ticket_id;

    -- If the ticket had a reserved seat, release it back to available inventory
    IF v_seat_id IS NOT NULL AND v_trip_id IS NOT NULL THEN
        UPDATE trip_seat_inventory
        SET is_available = TRUE,
            reserved_at = NULL,
            lock_version = lock_version + 1
        WHERE trip_id = v_trip_id 
          AND seat_id = v_seat_id;
    END IF;

    -- Record audit entry for cancellation
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

-- -----------------------------------------------------------------------------
-- 3. Trigger: trg_delays_after_insert
-- Updates the trip status to 'DELAYED' when a delay exceeding 15 minutes is recorded.
-- -----------------------------------------------------------------------------
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

    -- Audit log for operational delay tracking
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

-- -----------------------------------------------------------------------------
-- 4. Trigger: trg_payments_after_insert
-- Logs every payment transaction into audit_logs for financial audit trail.
-- -----------------------------------------------------------------------------
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

-- -----------------------------------------------------------------------------
-- 5. Trigger: trg_validate_seat_inventory_before_insert
-- Ensures that the seat being added to a trip belongs to the vehicle assigned to that trip.
-- -----------------------------------------------------------------------------
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

DELIMITER ;

