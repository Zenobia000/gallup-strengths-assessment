"""
FastAPI application entry point for the Gallup Strengths Assessment system.
Comprehensive setup with lifespan management, health checks, and psychology compliance.
"""

from contextlib import asynccontextmanager
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time

from app.core.config import get_settings
from app.core.database import create_tables, check_database_health

settings = get_settings()

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management with startup and shutdown procedures.
    """
    # Startup
    logger.info("Starting Gallup Strengths Assessment API")

    # Initialize database tables
    try:
        await create_tables()
        logger.info("Database tables initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

    # Verify database connection
    db_healthy = await check_database_health()
    if not db_healthy:
        logger.error("Database health check failed")
        raise RuntimeError("Database connection failed")

    logger.info("API startup complete")
    yield

    # Shutdown
    logger.info("Shutting down Gallup Strengths Assessment API")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Psychological assessment system for Gallup Strengths with compliance features",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.backend_cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """
    Log all HTTP requests for audit purposes.
    """
    start_time = time.time()

    # Get client IP (anonymized for privacy)
    client_ip = request.client.host if request.client else "unknown"
    if settings.anonymize_ip_addresses:
        ip_parts = client_ip.split('.')
        if len(ip_parts) == 4:
            client_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.0"

    # Process request
    response = await call_next(request)

    # Calculate processing time
    process_time = time.time() - start_time

    # Log request details
    logger.info(
        f"Request: {request.method} {request.url.path} "
        f"- Status: {response.status_code} "
        f"- Time: {process_time:.3f}s "
        f"- IP: {client_ip}"
    )

    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-API-Version"] = settings.app_version

    return response


# Health check endpoints
@app.get("/health", tags=["system"])
async def health_check():
    """
    System health check endpoint.

    Returns:
        dict: Health status information
    """
    db_healthy = await check_database_health()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "database": "connected" if db_healthy else "disconnected",
        "features": {
            "audit_logging": settings.audit_logging_enabled,
            "consent_required": settings.consent_required,
            "data_anonymization": settings.data_anonymization_enabled
        }
    }


@app.get("/health/detailed", tags=["system"])
async def detailed_health_check():
    """
    Detailed system health check for monitoring.

    Returns:
        dict: Detailed health information
    """
    db_healthy = await check_database_health()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version,
        "components": {
            "database": {
                "status": "connected" if db_healthy else "disconnected",
                "type": "SQLite",
                "url": settings.database_url.split("///")[-1] if "///" in settings.database_url else "N/A"
            },
            "security": {
                "jwt_enabled": True,
                "cors_enabled": True,
                "audit_logging": settings.audit_logging_enabled
            },
            "compliance": {
                "session_ttl_hours": settings.session_ttl_hours,
                "consent_required": settings.consent_required,
                "data_anonymization": settings.data_anonymization_enabled,
                "gdpr_compliant": True
            }
        },
        "configuration": {
            "debug_mode": settings.debug,
            "max_assessment_attempts": settings.max_assessment_attempts,
            "session_timeout_minutes": settings.session_inactivity_timeout_minutes
        }
    }


# Root endpoint
@app.get("/", tags=["system"])
async def root():
    """
    API root endpoint with basic information.

    Returns:
        dict: API information
    """
    return {
        "message": "Gallup Strengths Assessment API",
        "version": settings.app_version,
        "status": "operational",
        "documentation": "/docs" if settings.debug else "Contact administrator",
        "compliance": "GDPR compliant psychological assessment system"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: The request that caused the error
        exc: The exception that was raised

    Returns:
        JSONResponse: Error response
    """
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat(),
            "path": str(request.url.path)
        }
    )


# Import and include API routers
from app.api.v1 import sessions, consent

# Include routers with proper prefixes
app.include_router(sessions.router, prefix="/api/v1", tags=["sessions"])
app.include_router(consent.router, prefix="/api/v1", tags=["consent"])

# Additional routers to be added:
# from app.api.v1 import assessments, results, questions, strengths
# app.include_router(assessments.router, prefix="/api/v1", tags=["assessments"])
# app.include_router(results.router, prefix="/api/v1", tags=["results"])
# app.include_router(questions.router, prefix="/api/v1", tags=["questions"])
# app.include_router(strengths.router, prefix="/api/v1", tags=["strengths"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )