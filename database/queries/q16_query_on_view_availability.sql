-- Query 16: Analytical Query Against View (v_trip_availability)
-- Business Question: Filter and retrieve trips where 3A or 2A coach occupancy is greater than 25%, 
--                    showing remaining seats available for booking.
-- Concepts Demonstrated: Querying custom MySQL view with predicates and sorting.

USE transitmatrix;

SELECT 
    trip_id,
    trip_date,
    service_number,
    service_name,
    route_code,
    route_name,
    seat_class,
    total_inventory_seats,
    available_seats,
    reserved_seats,
    occupancy_percentage
FROM v_trip_availability
WHERE seat_class IN ('2A', '3A')
  AND occupancy_percentage >= 25.0
ORDER BY occupancy_percentage DESC, trip_date ASC
LIMIT 25;

