# TransitMatrix - Reporting & Analytics Endpoints

from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from datetime import date
from app.schemas.report import (
    RoutePerformanceReportItem,
    MonthlyRevenueReportItem,
    TripAvailabilityReportItem,
    DelaySummaryReportItem
)
from app.services.report_service import ReportService
from app.services.delay_service import DelayService
from app.api.deps import require_roles

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/route-performance", response_model=List[RoutePerformanceReportItem])
def get_route_performance(current_user=Depends(require_roles("ADMIN", "STAFF"))):
    """
    Returns commercial KPI performance metrics per route (queries view v_route_performance).
    """
    return ReportService.get_route_performance()


@router.get("/monthly-revenue", response_model=List[MonthlyRevenueReportItem])
def get_monthly_revenue(current_user=Depends(require_roles("ADMIN", "STAFF"))):
    """
    Returns month-by-month financial summary (queries view v_monthly_revenue).
    """
    return ReportService.get_monthly_revenue()


@router.get("/trip-availability", response_model=List[TripAvailabilityReportItem])
def get_trip_availability(
    trip_id: Optional[int] = None,
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Returns trip vacancy and occupancy percentage grouped by coach class (queries view v_trip_availability).
    """
    return ReportService.get_trip_availability(trip_id)


@router.get("/delay-summary", response_model=List[DelaySummaryReportItem])
def get_delay_summary(current_user=Depends(require_roles("ADMIN", "STAFF"))):
    """
    Returns station delay frequency, averages, and primary root causes (queries view v_delay_summary).
    """
    return DelayService.get_delay_summary()


@router.get("/route-revenue-procedure")
def get_route_revenue_procedure(
    route_id: int = Query(...),
    start_date: date = Query(...),
    end_date: date = Query(...),
    current_user=Depends(require_roles("ADMIN", "STAFF"))
):
    """
    Executes stored procedure sp_route_revenue_report across a specified date range.
    """
    return ReportService.get_route_revenue_report(route_id, start_date, end_date)
