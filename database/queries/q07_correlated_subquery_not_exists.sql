-- Query 07: Correlated Subquery with NOT EXISTS
-- Business Question: Identify registered passenger users who have created an account 
--                    but have NEVER made a booking.
-- Concepts Demonstrated: NOT EXISTS predicate for set difference.

USE transitmatrix;

SELECT 
    u.user_id,
    u.username,
    u.email,
    CONCAT(u.first_name, ' ', u.last_name) AS full_name,
    u.phone_number,
    u.created_at
FROM users u
WHERE u.role = 'PASSENGER'
  AND NOT EXISTS (
      SELECT 1 
      FROM bookings b 
      WHERE b.user_id = u.user_id
  )
ORDER BY u.created_at ASC;

