# TransitMatrix - FastAPI Application Entry Point
# Intelligent Railway and Public Transit Management System (Raw SQL Only)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.config import settings
from app.db.connection import init_connection_pool

# Import all API route modules
from app.api.routes import (
    auth,
    stations,
    routes,
    services,
    vehicles,
    trips,
    passengers,
    bookings,
    payments,
    cancellations,
    delays,
    reports,
    db_lab,
    predictions,
    ml,
    waitlists,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Application startup: verify database connection pool
    try:
        init_connection_pool()
    except Exception as e:
        print(f"Warning: Connection pool initialization failed on startup: {e}")
    yield
    # Application shutdown cleanup


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent Railway and Public Transit Management System - Raw SQL MySQL 8.0+ Backend",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers under /api
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(stations.router, prefix=settings.API_V1_STR)
app.include_router(routes.router, prefix=settings.API_V1_STR)
app.include_router(services.router, prefix=settings.API_V1_STR)
app.include_router(vehicles.router, prefix=settings.API_V1_STR)
app.include_router(trips.router, prefix=settings.API_V1_STR)
app.include_router(passengers.router, prefix=settings.API_V1_STR)
app.include_router(bookings.router, prefix=settings.API_V1_STR)
app.include_router(payments.router, prefix=settings.API_V1_STR)
app.include_router(cancellations.router, prefix=settings.API_V1_STR)
app.include_router(delays.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(db_lab.router, prefix=settings.API_V1_STR)
app.include_router(predictions.router, prefix=settings.API_V1_STR)
app.include_router(ml.router, prefix=settings.API_V1_STR)
app.include_router(waitlists.router, prefix=settings.API_V1_STR)


@app.get("/api/health", tags=["Health"])
def health_check():
    """
    Service health check endpoint.
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "database": "MySQL 8.0+ (Raw SQL)"
    }
