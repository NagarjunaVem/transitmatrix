-- Query 14: Window Function - Cumulative Running Total
-- Business Question: Calculate daily booking revenue and cumulative progressive running total 
--                    of revenue over the operating calendar.
-- Concepts Demonstrated: SUM() OVER (ORDER BY ... ROWS UNBOUNDED PRECEDING).

USE transitmatrix;

WITH DailyRevenue AS (
    SELECT 
        DATE(booking_date) AS booking_day,
        COUNT(booking_id) AS bookings_count,
        SUM(total_fare) AS daily_fare_sum
    FROM bookings
    WHERE booking_status IN ('CONFIRMED', 'PARTIALLY_CANCELLED')
    GROUP BY DATE(booking_date)
)
SELECT 
    booking_day,
    bookings_count,
    daily_fare_sum,
    SUM(daily_fare_sum) OVER (
        ORDER BY booking_day ASC
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS running_cumulative_revenue,
    ROUND(
        AVG(daily_fare_sum) OVER (
            ORDER BY booking_day ASC
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS rolling_7day_avg_revenue
FROM DailyRevenue
ORDER BY booking_day ASC
LIMIT 30;

