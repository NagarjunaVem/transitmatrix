-- Query 20: Stored Procedure Execution and Trigger Audit Verification
-- Business Question: Execute sp_search_trips and sp_cancel_booking, and verify that 
--                    audit triggers logged the state mutation into audit_logs.
-- Concepts Demonstrated: CALL stored procedures, OUT parameter handling, Trigger auditing verification.

USE transitmatrix;

-- Part 1: Search trips between New Delhi (NDLS) and Mumbai Central (BCT)
CALL sp_search_trips('NDLS', 'BCT', '2026-10-01');

-- Part 2: Cancel a confirmed ticket using the stored procedure
SET @refund_amt = 0.00;
SET @status_msg = '';

CALL sp_cancel_booking(1, 'Passenger emergency cancellation', @refund_amt, @status_msg);

SELECT @refund_amt AS calculated_refund, @status_msg AS execution_result;

-- Part 3: Verify the audit log created by the cancellation trigger
SELECT 
    log_id,
    table_name,
    record_id,
    action,
    new_values,
    changed_by,
    changed_at
FROM audit_logs
WHERE table_name = 'cancellations'
ORDER BY log_id DESC
LIMIT 5;

