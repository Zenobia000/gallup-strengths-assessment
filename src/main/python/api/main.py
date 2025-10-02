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
from fastapi.staticfiles import StaticFiles

from core.config import get_settings
from models.schemas import (
    HealthResponse,
    ConsentRequest,
    ConsentResponse,
    SessionStartRequest,
    SessionStartResponse,
    APIResponse
)
# NOTE: AssessmentService temporarily disabled - uses legacy MiniIPIPScorer
# TODO: Refactor AssessmentService to use ScoringEngine (Task: future)
# from services.assessment import AssessmentService
from database.engine import get_session
# Import new SQLAlchemy-based V4 assessment
from api.routes import reports_v4_only
from api.routes import v4_assessment_sqlalchemy
# from api.routes import consent, v4_data_collection
from api.middleware.error_handler import register_error_handlers


# Initialize FastAPI with psychometric-focused configuration
app = FastAPI(
    title="Gallup Strengths Assessment API",
    description="心理測量與決策支援系統 - 將公領域人格量表轉化為可執行的決策建議",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
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
    response.headers["X-API-Version"] = "1.0.0"

    return response


# Register unified error handlers
register_error_handlers(app)


# Enhanced Questions Endpoint - Database Driven with Situational Support
@app.get("/api/assessment/questions", tags=["Assessment"])
async def get_questions(include_situational: bool = True):
    """
    Get assessment questions from database.

    Supports both traditional Mini-IPIP and situational questions.
    """
    try:
        from database.engine import get_session
        from models.v4_models import V4Statement
        import json

        questions = []
        with get_session() as session:
            raw_items = session.query(V4Statement).all()

            for item in raw_items:
                # V4 statements are all for Thurstonian IRT
                # Access all attributes while session is active
                question_data = {
                    "id": item.statement_id,
                    "text": item.text,
                    "dimension": item.dimension,
                    "context": item.context,
                    "social_desirability": item.social_desirability,
                    "question_type": "thurstonian_irt"
                }
                questions.append(question_data)

        # Sort by dimension and statement ID
        questions.sort(key=lambda x: (x["dimension"], x["id"]))

        return {
            "questions": questions,
            "total_count": len(questions),
            "dimensions": list(set(q["dimension"] for q in questions)),
            "version": "v4_thurstonian_irt",
            "instructions": "這些是用於四選二強制選擇評測的語句，將組成評測題組。",
            "assessment_type": "thurstonian_irt",
            "response_format": "forced_choice_quartet"
        }

    except Exception as e:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load questions: {str(e)}"
        )

# Health Check Endpoint - Simple and focused
@app.get("/api/system/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """
    System health check endpoint.

    Tests database connectivity and returns system status.
    Implements the "do one thing well" principle.
    """
    try:
        # Test database connection
        from database.engine import get_database_engine
        engine = get_database_engine()
        health = engine.health_check()

        if health["status"] != "healthy":
            raise Exception(health.get("error", "Database unhealthy"))

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0",
            database_status="connected",
            services={
                "assessment": "ready",
                "scoring": "ready",
                "reporting": "ready",
                "v4_engine": "ready"
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


# Include route modules - Functional grouping
# app.include_router(consent.router, prefix="/api", tags=["Privacy"])
app.include_router(reports_v4_only.router, prefix="/api", tags=["Reports"])
app.include_router(v4_assessment_sqlalchemy.router, prefix="/api", tags=["V4 Assessment"])
# app.include_router(v4_data_collection.router, prefix="/api", tags=["Data Collection"])

# Mount static files for frontend
import os
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Application startup event
@app.on_event("startup")
async def startup_event():
    """
    Initialize application resources.

    Sets up database connections and validates configuration.
    Follows fail-fast principle.
    """
    try:
        # Initialize database engine and validate schema
        from database.engine import get_database_engine
        engine = get_database_engine()
        health = engine.health_check()

        if health["status"] != "healthy":
            raise Exception(f"Database not healthy: {health}")

        print("FastAPI application started successfully")
        print(f"V4 SQLAlchemy database ready - {health['table_count']} tables")
        print(f"API documentation: http://localhost:8004/api/docs")

    except Exception as e:
        print(f"Startup failed: {e}")
        raise


# Assessment frontend endpoint
@app.get("/assessment", include_in_schema=False)
async def assessment_page():
    """Serve the assessment frontend page."""
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    assessment_file = os.path.join(static_dir, "assessment.html")

    if os.path.exists(assessment_file):
        return FileResponse(assessment_file)
    else:
        raise HTTPException(status_code=404, detail="Assessment page not found")

# V4 Pilot test frontend endpoint
@app.get("/v4-pilot", include_in_schema=False)
async def v4_pilot_page():
    """Serve the v4 pilot test frontend page."""
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    pilot_file = os.path.join(static_dir, "v4_pilot_test.html")

    if os.path.exists(pilot_file):
        return FileResponse(pilot_file)
    else:
        raise HTTPException(status_code=404, detail="V4 pilot test page not found")

# Additional frontend endpoints
@app.get("/results.html", include_in_schema=False)
async def results_page():
    """Serve the assessment results display page."""
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    results_file = os.path.join(static_dir, "results.html")

    if os.path.exists(results_file):
        return FileResponse(results_file)
    else:
        raise HTTPException(status_code=404, detail="Results page not found")

@app.get("/report-detail.html", include_in_schema=False)
async def report_detail_page():
    """Serve the detailed report page."""
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    report_file = os.path.join(static_dir, "report-detail.html")

    if os.path.exists(report_file):
        return FileResponse(report_file)
    else:
        raise HTTPException(status_code=404, detail="Report detail page not found")

@app.get("/landing.html", include_in_schema=False)
async def landing_page():
    """Serve the landing page."""
    from fastapi.responses import FileResponse
    import os

    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    landing_file = os.path.join(static_dir, "landing.html")

    if os.path.exists(landing_file):
        return FileResponse(landing_file)
    else:
        raise HTTPException(status_code=404, detail="Landing page not found")

# Root endpoint redirect
@app.get("/", include_in_schema=False)
async def root():
    """Redirect root to API documentation."""
    return JSONResponse({
        "message": "Gallup Strengths Assessment API",
        "documentation": "/api/docs",
        "health_check": "/api/system/health",
        "assessment": "/assessment"
    })


if __name__ == "__main__":
    import uvicorn

    # Development server configuration
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=True,
        log_level="info"
    )