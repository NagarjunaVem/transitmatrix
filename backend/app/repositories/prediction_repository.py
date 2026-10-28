# TransitMatrix - Demand Prediction Repository (Raw SQL Only)
# Parameterized queries for machine learning forecast persistence and feature extraction.

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
        model_version: str,
        features_json: Optional[Dict[str, Any]]
    ) -> int:
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                INSERT INTO demand_predictions (
                    route_id, prediction_date, predicted_demand,
                    confidence_interval_low, confidence_interval_high,
                    model_version, features_json
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            json_str = json.dumps(features_json) if features_json else None
            cursor.execute(
                query,
                (
                    route_id, prediction_date, predicted_demand,
                    confidence_interval_low, confidence_interval_high,
                    model_version, json_str
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
        cursor = connection.cursor(dictionary=True)
        try:
            if route_id:
                query = """
                    SELECT dp.prediction_id, dp.route_id, r.route_code, r.route_name,
                           dp.prediction_date, dp.predicted_demand,
                           dp.confidence_interval_low, dp.confidence_interval_high,
                           dp.model_version, dp.features_json, dp.created_at
                    FROM demand_predictions dp
                    JOIN routes r ON dp.route_id = r.route_id
                    WHERE dp.route_id = %s
                    ORDER BY dp.prediction_date DESC
                    LIMIT %s
                """
                cursor.execute(query, (route_id, limit))
            else:
                query = """
                    SELECT dp.prediction_id, dp.route_id, r.route_code, r.route_name,
                           dp.prediction_date, dp.predicted_demand,
                           dp.confidence_interval_low, dp.confidence_interval_high,
                           dp.model_version, dp.features_json, dp.created_at
                    FROM demand_predictions dp
                    JOIN routes r ON dp.route_id = r.route_id
                    ORDER BY dp.prediction_date DESC
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
        Extracts training dataset features directly using raw SQL.
        Aggregates daily route passenger demand, base fares, and distance.
        """
        cursor = connection.cursor(dictionary=True)
        try:
            query = """
                SELECT 
                    r.route_id,
                    r.route_code,
                    r.total_distance_km,
                    r.duration_est_minutes,
                    tr.trip_date,
                    DAYOFWEEK(tr.trip_date) AS day_of_week,
                    MONTH(tr.trip_date) AS month_of_year,
                    AVG(tr.base_fare) AS avg_base_fare,
                    COUNT(DISTINCT tr.trip_id) AS trips_count,
                    COALESCE(SUM(b.total_passengers), 0) AS actual_passenger_demand
                FROM routes r
                JOIN trips tr ON r.route_id = tr.route_id
                LEFT JOIN bookings b ON tr.trip_id = b.trip_id AND b.booking_status <> 'CANCELLED'
                GROUP BY 
                    r.route_id, r.route_code, r.total_distance_km,
                    r.duration_est_minutes, tr.trip_date,
                    DAYOFWEEK(tr.trip_date), MONTH(tr.trip_date)
                ORDER BY tr.trip_date ASC, r.route_id ASC
            """
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
