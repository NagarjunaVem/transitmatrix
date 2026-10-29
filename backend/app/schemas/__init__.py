# TransitMatrix - Pydantic Schemas Package
from app.schemas.auth import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    UserProfileResponse,
    UserResponse,
)
from app.schemas.station import (
    StationBase,
    StationCreate,
    StationUpdate,
    StationResponse,
)
from app.schemas.route import (
    RouteStopBase,
    RouteStopCreate,
    RouteStopResponse,
    RouteBase,
    RouteCreate,
    RouteResponse,
    RouteDetailResponse,
)
from app.schemas.service import (
    ServiceBase,
    ServiceCreate,
    ServiceUpdate,
    ServiceResponse,
)
from app.schemas.vehicle import (
    SeatResponse,
    VehicleBase,
    VehicleCreate,
    VehicleUpdate,
    VehicleResponse,
)
from app.schemas.trip import (
    TripBase,
    TripCreate,
    TripUpdate,
    TripResponse,
    TripSearchResultResponse,
)
from app.schemas.passenger import (
    PassengerBase,
    PassengerCreate,
    PassengerResponse,
)
from app.schemas.booking import (
    BookingPassengerItem,
    BookingCreateRequest,
    TicketResponse,
    BookingResponse,
    SeatMapItem,
)
from app.schemas.payment import (
    PaymentCreateRequest,
    PaymentResponse,
)
from app.schemas.cancellation import (
    CancellationCreateRequest,
    CancellationResponse,
)
from app.schemas.delay import (
    DelayCreateRequest,
    DelayResponse,
)
from app.schemas.report import (
    RoutePerformanceReportItem,
    MonthlyRevenueReportItem,
    TripAvailabilityReportItem,
    DelaySummaryReportItem,
)
from app.schemas.db_lab import (
    QueryCatalogItem,
    QueryExecutionResponse,
)
from app.schemas.prediction import (
    PredictionCreateRequest,
    PredictionResponse,
    ForecastQueryRequest,
    ModelEvaluationMetrics,
    ModelMetricsResponse,
    ModelInfoResponse,
)
from app.schemas.waitlist import (
    WaitlistCreateRequest,
    WaitlistResponse,
    WaitlistPromotionResponse,
)
