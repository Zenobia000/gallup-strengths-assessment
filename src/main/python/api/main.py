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
from utils.database import get_db_connection
from api.routes import consent, reports_v4_only, v4_assessment, v4_data_collection
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
        from utils.database import get_database_manager
        import json

        db_manager = get_database_manager()
        raw_items = db_manager.get_assessment_items("mini_ipip_v1.0")

        questions = []
        for item in raw_items:
            # Skip situational questions if not requested
            if not include_situational and item.get("question_type") == "situational":
                continue

            question_data = {
                "id": item["item_id"],
                "text": item["text_chinese"],
                "dimension": item["dimension"],
                "reverse": bool(item["reverse_scored"]),
                "question_type": item.get("question_type", "traditional")
            }

            # Add situational question specific fields
            if item.get("question_type") == "situational":
                scenario_id = item.get("scenario_context")
                scenario_description = None

                # Get full scenario description from database
                if scenario_id:
                    try:
                        with db_manager.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute(
                                "SELECT description FROM situational_scenarios WHERE scenario_id = ?",
                                (scenario_id,)
                            )
                            result = cursor.fetchone()
                            if result:
                                scenario_description = result[0]
                    except Exception as e:
                        print(f"Error fetching scenario description: {e}")

                question_data["scenario_context"] = scenario_description or scenario_id

                # Parse custom response options
                if item.get("response_options"):
                    try:
                        response_options = json.loads(item["response_options"])
                        question_data["response_options"] = response_options
                    except json.JSONDecodeError:
                        pass

                # Parse dimension weights
                if item.get("dimension_weights"):
                    try:
                        dimension_weights = json.loads(item["dimension_weights"])
                        question_data["dimension_weights"] = dimension_weights
                    except json.JSONDecodeError:
                        pass

            questions.append(question_data)

        # Sort by item order
        questions.sort(key=lambda x: int(x["id"].split("_")[-1]) if "_" in x["id"] else int(x["id"]))

        return {
            "questions": questions,
            "total_count": len(questions),
            "traditional_count": len([q for q in questions if q.get("question_type", "traditional") == "traditional"]),
            "situational_count": len([q for q in questions if q.get("question_type") == "situational"]),
            "version": "mini_ipip_v1.0_enhanced",
            "instructions": "請根據您的真實感受，選擇最符合您情況的答案。",
            "scale": [
                {"value": 1, "label": "非常不同意"},
                {"value": 2, "label": "不同意"},
                {"value": 3, "label": "中立"},
                {"value": 4, "label": "同意"},
                {"value": 5, "label": "非常同意"}
            ]
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


# Include route modules - Functional grouping
app.include_router(consent.router, prefix="/api", tags=["Privacy"])
app.include_router(reports_v4_only.router, prefix="/api", tags=["Reports"])
app.include_router(v4_assessment.router, prefix="/api", tags=["Assessment"])
app.include_router(v4_data_collection.router, prefix="/api", tags=["Data Collection"])

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
        # Validate database schema
        with get_db_connection() as conn:
            conn.execute("SELECT name FROM sqlite_master WHERE type='table'")

        print("FastAPI application started successfully")
        print(f"Psychometric assessment system ready")
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