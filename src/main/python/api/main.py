"""
FastAPI Application Entry Point - Gallup Strengths Assessment

This module implements the main FastAPI application following Linus Torvalds
philosophy of "good taste" - simple, clean, and doing one thing well.

Key Principles:
- No more than 3 levels of indentation
- Functions should be short and focused
- Clear, descriptive naming without prefixes like "enhanced_"
- Explainability and provenance tracking built-in
"""

from datetime import datetime
from typing import Dict, Any
import uuid

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from core.config import get_settings
from models.schemas import (
    HealthResponse,
    ConsentRequest,
    ConsentResponse,
    SessionStartRequest,
    SessionStartResponse,
    APIResponse
)
from services.assessment import AssessmentService
from utils.database import get_db_connection
from api.routes import consent, sessions


# Initialize FastAPI with psychometric-focused configuration
app = FastAPI(
    title="Gallup Strengths Assessment API",
    description="心理測量與決策支援系統 - 將公領域人格量表轉化為可執行的決策建議",
    version="1.0.0",
    docs_url="/api/v1/docs",
    openapi_url="/api/v1/openapi.json",
    redoc_url="/api/v1/redoc"
)

# Configure CORS for development - following MVP pragmatism
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_request_metadata(request: Request, call_next):
    """
    Add request metadata for psychometric traceability.

    Every request gets a unique ID for audit trails and provenance tracking.
    This follows the "explainability by design" principle.
    """
    request.state.request_id = str(uuid.uuid4())
    request.state.timestamp = datetime.utcnow()

    response = await call_next(request)

    # Add metadata headers for traceability
    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Timestamp"] = request.state.timestamp.isoformat()
    response.headers["X-API-Version"] = "v1.0.0"

    return response


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler following psychometric error standards.

    Provides consistent error format with trace IDs for debugging
    while protecting sensitive information.
    """
    request_id = getattr(request.state, 'request_id', str(uuid.uuid4()))

    return JSONResponse(
        status_code=500,
        content=APIResponse(
            success=False,
            error={
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "trace_id": request_id
            },
            meta={
                "timestamp": datetime.utcnow().isoformat(),
                "request_id": request_id
            }
        ).dict()
    )


# Health Check Endpoint - Simple and focused
@app.get("/api/v1/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """
    System health check endpoint.

    Tests database connectivity and returns system status.
    Implements the "do one thing well" principle.
    """
    try:
        # Test database connection
        with get_db_connection() as conn:
            cursor = conn.execute("SELECT 1")
            cursor.fetchone()

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database_status="connected",
            services={
                "assessment": "ready",
                "scoring": "ready",
                "reporting": "ready"
            }
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database_status="error",
            error=str(e)
        )


# Include route modules - Clean separation of concerns
app.include_router(consent.router, prefix="/api/v1", tags=["Consent"])
app.include_router(sessions.router, prefix="/api/v1", tags=["Sessions"])


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize application resources.

    Sets up database connections and validates configuration.
    Follows fail-fast principle.
    """
    try:
        # Validate database schema
        with get_db_connection() as conn:
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")

        print("FastAPI application started successfully")
        print(f"Psychometric assessment system ready")
        print(f"API documentation: http://localhost:8002/api/v1/docs")

    except Exception as e:
        print(f"Startup failed: {e}")
        raise


# Root endpoint redirect
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return JSONResponse({
        "message": "Gallup Strengths Assessment API",
        "documentation": "/api/v1/docs",
        "health_check": "/api/v1/health"
    })


if __name__ == "__main__":
    import uvicorn

    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )