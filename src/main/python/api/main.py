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
# NOTE: AssessmentService temporarily disabled - uses legacy MiniIPIPScorer
# TODO: Refactor AssessmentService to use ScoringEngine (Task: future)
# from services.assessment import AssessmentService
from utils.database import get_db_connection
from api.routes import consent, sessions, scoring, recommendations
from api.middleware.error_handler import register_error_handlers


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


# Register unified error handlers
register_error_handlers(app)


# Mini-IPIP Questions Endpoint
@app.get("/api/v1/questions", tags=["Assessment"])
async def get_questions():
    """Get Mini-IPIP 20-item questionnaire."""
    questions = [
        {"id": 1, "text": "我很有想像力", "dimension": "openness", "reverse": False},
        {"id": 2, "text": "我不會被藝術作品感動", "dimension": "openness", "reverse": True},
        {"id": 3, "text": "我不善於抽象思考", "dimension": "openness", "reverse": True},
        {"id": 4, "text": "我對許多事物都不感興趣", "dimension": "openness", "reverse": True},
        {"id": 5, "text": "我做事總是經過深思熟慮", "dimension": "conscientiousness", "reverse": False},
        {"id": 6, "text": "我經常忘記把東西放回原位", "dimension": "conscientiousness", "reverse": True},
        {"id": 7, "text": "我喜歡整潔有序", "dimension": "conscientiousness", "reverse": False},
        {"id": 8, "text": "我經常搞亂東西", "dimension": "conscientiousness", "reverse": True},
        {"id": 9, "text": "我是聚會的靈魂人物", "dimension": "extraversion", "reverse": False},
        {"id": 10, "text": "我不喜歡成為注意力的焦點", "dimension": "extraversion", "reverse": True},
        {"id": 11, "text": "我在群體中保持低調", "dimension": "extraversion", "reverse": True},
        {"id": 12, "text": "我與他人保持距離", "dimension": "extraversion", "reverse": True},
        {"id": 13, "text": "我對他人的問題感興趣", "dimension": "agreeableness", "reverse": False},
        {"id": 14, "text": "我對他人毫不關心", "dimension": "agreeableness", "reverse": True},
        {"id": 15, "text": "我感受他人的情緒", "dimension": "agreeableness", "reverse": False},
        {"id": 16, "text": "我不關心別人的問題", "dimension": "agreeableness", "reverse": True},
        {"id": 17, "text": "我經常感到憂鬱", "dimension": "neuroticism", "reverse": False},
        {"id": 18, "text": "我很少感到憂鬱", "dimension": "neuroticism", "reverse": True},
        {"id": 19, "text": "我容易受到打擊", "dimension": "neuroticism", "reverse": False},
        {"id": 20, "text": "我很少煩惱", "dimension": "neuroticism", "reverse": True}
    ]

    return {
        "questions": questions,
        "total_count": len(questions),
        "instructions": "請根據您的真實感受，選擇最符合您情況的答案。1=非常不同意，2=不同意，3=中立，4=同意，5=非常同意",
        "scale": [
            {"value": 1, "label": "非常不同意"},
            {"value": 2, "label": "不同意"},
            {"value": 3, "label": "中立"},
            {"value": 4, "label": "同意"},
            {"value": 5, "label": "非常同意"}
        ]
    }

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
app.include_router(scoring.router, tags=["Scoring"])
app.include_router(recommendations.router, tags=["Recommendations"])

# Report generation routes
from api.routes import reports
app.include_router(reports.router, prefix="/api/v1", tags=["Reports"])

# Cache administration routes
from api.routes import cache_admin
app.include_router(cache_admin.router, prefix="/api/v1", tags=["Cache"])


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