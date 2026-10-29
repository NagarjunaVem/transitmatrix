# TransitMatrix - Demand Prediction Repository (Raw SQL Only)
# Parameterized queries for machine learning forecast persistence and historical feature extraction.
# Strict raw SQL implementation adhering to MySQL 8.0+ schema definitions without ORM.

import json
from typing import List, Dict, Any, Optional
from datetime import date


class PredictionRepository:

    @staticmethod
    def save_prediction(
        connection,
        route_id: int,
        prediction_date: date,
        predicted_demand: int,
        confidence_interval_low: Optional[int],
        confidence_interval_high: Optional[int],
        model_version: str = "v1.0",
        model_name: str = "RandomForestRegressor",
        features_json: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Persists a predicted passenger demand record into demand_predictions using raw SQL.
        Safely handles duplicate keys (route_id, prediction_date, model_version) by updating.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO demand_predictions (
                    route_id, prediction_date, predicted_passenger_demand,
                    confidence_lower_bound, confidence_upper_bound,
                    model_name, model_version, features_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    predicted_passenger_demand = VALUES(predicted_passenger_demand),
                    confidence_lower_bound = VALUES(confidence_lower_bound),
                    confidence_upper_bound = VALUES(confidence_upper_bound),
                    features_json = VALUES(features_json)
            """
            json_str = json.dumps(features_json) if features_json else None
            cursor.execute(
                query,
                (
                    route_id,
                    prediction_date,
                    predicted_demand,
                    confidence_interval_low if confidence_interval_low is not None else max(0, predicted_demand - 15),
                    confidence_interval_high if confidence_interval_high is not None else predicted_demand + 15,
                    model_name,
                    model_version,
                    json_str
                )
            )
            return cursor.lastrowid
        finally:
            cursor.close()

    @staticmethod
    def get_predictions(
        connection,
        route_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieves persisted demand predictions joined with route metadata.
        Aliases columns to match Pydantic schema and frontend contracts.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            if route_id:
                query = """
                    SELECT dp.prediction_id, dp.route_id, r.route_code, r.route_name,
                           dp.prediction_date,
                           dp.predicted_passenger_demand AS predicted_demand,
                           dp.confidence_lower_bound AS confidence_interval_low,
                           dp.confidence_upper_bound AS confidence_interval_high,
                           dp.model_name, dp.model_version, dp.features_json,
                           dp.generated_at AS created_at
                    FROM demand_predictions dp
                    JOIN routes r ON dp.route_id = r.route_id
                    WHERE dp.route_id = %s
                    ORDER BY dp.prediction_date DESC, dp.prediction_id DESC
                    LIMIT %s
                """
                cursor.execute(query, (route_id, limit))
            else:
                query = """
                    SELECT dp.prediction_id, dp.route_id, r.route_code, r.route_name,
                           dp.prediction_date,
                           dp.predicted_passenger_demand AS predicted_demand,
                           dp.confidence_lower_bound AS confidence_interval_low,
                           dp.confidence_upper_bound AS confidence_interval_high,
                           dp.model_name, dp.model_version, dp.features_json,
                           dp.generated_at AS created_at
                    FROM demand_predictions dp
                    JOIN routes r ON dp.route_id = r.route_id
                    ORDER BY dp.prediction_date DESC, dp.prediction_id DESC
                    LIMIT %s
                """
                cursor.execute(query, (limit,))

            rows = cursor.fetchall()
            for row in rows:
                if row.get("features_json") and isinstance(row["features_json"], str):
                    try:
                        row["features_json"] = json.loads(row["features_json"])
                    except Exception:
                        pass
            return rows
        finally:
            cursor.close()

    @staticmethod
    def get_historical_features(connection) -> List[Dict[str, Any]]:
        """
        Extracts training dataset features directly using raw SQL without any ORM.
        Aggregates trip and booking demand across route, date, and hour intervals.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    r.route_id,
                    r.route_code,
                    r.total_distance_km,
                    r.duration_est_minutes,
                    tr.trip_id,
                    tr.service_id,
                    s.service_number,
                    s.service_type,
                    tr.trip_date,
                    HOUR(tr.scheduled_departure) AS departure_hour,
                    CASE 
                        WHEN (HOUR(tr.scheduled_departure) BETWEEN 7 AND 10) OR (HOUR(tr.scheduled_departure) BETWEEN 16 AND 20) 
                        THEN 1 ELSE 0 
                    END AS is_peak_hour,
                    DAYOFWEEK(tr.trip_date) AS day_of_week,
                    DAY(tr.trip_date) AS day_of_month,
                    MONTH(tr.trip_date) AS month_of_year,
                    QUARTER(tr.trip_date) AS quarter_of_year,
                    CASE WHEN DAYOFWEEK(tr.trip_date) IN (1, 7) THEN 1 ELSE 0 END AS is_weekend,
                    tr.base_fare AS avg_base_fare,
                    COUNT(DISTINCT tr.trip_id) AS trips_count,
                    COUNT(DISTINCT b.booking_id) AS booking_count,
                    COALESCE(SUM(CASE WHEN b.booking_status = 'CANCELLED' THEN 1 ELSE 0 END), 0) AS cancellations_count,
                    COALESCE(SUM(CASE WHEN b.booking_status <> 'CANCELLED' THEN b.total_passengers ELSE 0 END), 0) AS actual_passenger_demand
                FROM routes r
                JOIN trips tr ON r.route_id = tr.route_id
                JOIN services s ON tr.service_id = s.service_id
                LEFT JOIN bookings b ON tr.trip_id = b.trip_id
                GROUP BY 
                    r.route_id, r.route_code, r.total_distance_km, r.duration_est_minutes,
                    tr.trip_id, tr.service_id, s.service_number, s.service_type,
                    tr.trip_date, tr.scheduled_departure, tr.base_fare
                ORDER BY tr.trip_date ASC, tr.scheduled_departure ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()

    @staticmethod
    def get_route_historical_averages(connection) -> Dict[int, float]:
        """
        Computes historical average passenger demand per route using raw SQL.
        Useful for baseline prediction and cold-start fallback.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    r.route_id,
                    COALESCE(AVG(sub.trip_demand), 50.0) AS avg_demand
                FROM routes r
                LEFT JOIN (
                    SELECT tr.route_id, SUM(b.total_passengers) AS trip_demand
                    FROM trips tr
                    JOIN bookings b ON tr.trip_id = b.trip_id
                    WHERE b.booking_status <> 'CANCELLED'
                    GROUP BY tr.trip_id, tr.route_id
                ) sub ON r.route_id = sub.route_id
                GROUP BY r.route_id
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return {row["route_id"]: float(row["avg_demand"]) for row in rows}
        finally:
            cursor.close()
