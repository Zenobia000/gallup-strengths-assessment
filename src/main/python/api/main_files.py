"""
FastAPI Application Entry Point - File Storage Version
Rapid development version using CSV/JSON files instead of database
"""

from datetime import datetime
from typing import Dict, Any
import uuid
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from core.config import get_settings
from models.schemas import HealthResponse
from core.file_storage import get_file_storage, initialize_file_storage

# Import file-based routes
from api.routes import v4_assessment_files
from api.middleware.error_handler import register_error_handlers

# Initialize file storage
initialize_file_storage()
storage = get_file_storage()

# Initialize FastAPI with file storage configuration
app = FastAPI(
    title="Gallup Strengths Assessment API - File Storage Version",
    description="快速開發版本 - 使用 CSV/JSON 文件存儲進行敏捷測試",
    version="1.0.0-file-storage",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url="/api/redoc"
)

# Configure CORS
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
    """Add request metadata for traceability"""
    request.state.request_id = str(uuid.uuid4())
    request.state.timestamp = datetime.utcnow()

    response = await call_next(request)

    response.headers["X-Request-ID"] = request.state.request_id
    response.headers["X-Timestamp"] = request.state.timestamp.isoformat()
    response.headers["X-API-Version"] = "1.0.0-file-storage"
    response.headers["X-Storage-Type"] = "file-based"

    return response


# Register error handlers
register_error_handlers(app)


# Enhanced Questions Endpoint - File Storage Version
@app.get("/api/assessment/questions", tags=["Assessment"])
async def get_questions(include_situational: bool = True):
    """Get assessment questions from file storage"""
    try:
        statements = storage.select_all("v4_statements")

        if not statements:
            raise HTTPException(
                status_code=500,
                detail="No statements found in file storage"
            )

        questions = []
        for item in statements:
            question_data = {
                "id": item.get("statement_id"),
                "text": item.get("text"),
                "dimension": item.get("dimension"),
                "context": item.get("context"),
                "social_desirability": item.get("social_desirability"),
                "question_type": "thurstonian_irt"
            }
            questions.append(question_data)

        # Sort by dimension and statement ID
        questions.sort(key=lambda x: (x["dimension"], x["id"]))

        return {
            "questions": questions,
            "total_count": len(questions),
            "dimensions": list(set(q["dimension"] for q in questions)),
            "version": "v4_thurstonian_irt_file_storage",
            "instructions": "這些是用於四選二強制選擇評測的語句，將組成評測題組。",
            "assessment_type": "thurstonian_irt",
            "response_format": "forced_choice_quartet",
            "storage_type": "file_based"
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load questions: {str(e)}"
        )


# Health Check Endpoint - File Storage Version
@app.get("/api/system/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """System health check for file storage version"""
    try:
        health = storage.health_check()

        if health["status"] != "healthy":
            raise Exception(health.get("error", "File storage unhealthy"))

        return HealthResponse(
            status="healthy",
            timestamp=datetime.utcnow(),
            version="1.0.0-file-storage",
            database_status="file_storage_ready",
            services={
                "assessment": "ready",
                "scoring": "ready",
                "reporting": "ready",
                "file_storage": "ready"
            }
        )

    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            timestamp=datetime.utcnow(),
            version="1.0.0-file-storage",
            database_status="file_storage_error",
            error=str(e)
        )


# Include file-based route modules
app.include_router(v4_assessment_files.router, prefix="/api", tags=["V4 Assessment - File Storage"])

# Mount static files
static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Application startup event
@app.on_event("startup")
async def startup_event():
    """Initialize file storage system"""
    try:
        health = storage.health_check()

        if health["status"] != "healthy":
            raise Exception(f"File storage not healthy: {health}")

        print("FastAPI application started successfully - FILE STORAGE VERSION")
        print(f"File storage ready - {health['table_count']} tables")
        print(f"API documentation: http://localhost:8004/api/docs")
        print(f"Storage path: {health['base_path']}")

    except Exception as e:
        print(f"Startup failed: {e}")
        raise


# Assessment frontend endpoint
@app.get("/assessment", include_in_schema=False)
async def assessment_page():
    """Serve the assessment frontend page."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    assessment_file = os.path.join(static_dir, "assessment.html")

    if os.path.exists(assessment_file):
        return FileResponse(assessment_file)
    else:
        raise HTTPException(status_code=404, detail="Assessment page not found")


# Static page endpoints
@app.get("/results.html", include_in_schema=False)
async def results_page():
    """Serve the results page directly."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    results_file = os.path.join(static_dir, "results.html")

    if os.path.exists(results_file):
        return FileResponse(results_file)
    else:
        raise HTTPException(status_code=404, detail="Results page not found")


@app.get("/landing.html", include_in_schema=False)
async def landing_page():
    """Serve the landing page directly."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    landing_file = os.path.join(static_dir, "landing.html")

    if os.path.exists(landing_file):
        return FileResponse(landing_file)
    else:
        raise HTTPException(status_code=404, detail="Landing page not found")


@app.get("/report-detail.html", include_in_schema=False)
async def report_detail_page():
    """Serve the report detail page directly."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    report_file = os.path.join(static_dir, "report-detail.html")

    if os.path.exists(report_file):
        return FileResponse(report_file)
    else:
        raise HTTPException(status_code=404, detail="Report detail page not found")


@app.get("/assessment.html", include_in_schema=False)
async def assessment_html_page():
    """Serve the assessment page directly as HTML."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    assessment_file = os.path.join(static_dir, "assessment.html")

    if os.path.exists(assessment_file):
        return FileResponse(assessment_file)
    else:
        raise HTTPException(status_code=404, detail="Assessment HTML page not found")


@app.get("/assessment-intro.html", include_in_schema=False)
async def assessment_intro_page():
    """Serve the assessment intro page directly."""
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "static")
    assessment_intro_file = os.path.join(static_dir, "assessment-intro.html")
    if os.path.exists(assessment_intro_file):
        return FileResponse(assessment_intro_file)
    else:
        raise HTTPException(status_code=404, detail="Assessment intro page not found")


# Root endpoint - Redirect to main entry
@app.get("/", include_in_schema=False)
async def root():
    """文件存儲版本系統根目錄 - 重定向到主入口頁面"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/static/index.html", status_code=302)

# API Info endpoint for developers
@app.get("/api/info", include_in_schema=False)
async def api_info():
    """API 系統資訊"""
    return JSONResponse({
        "message": "Gallup Strengths Assessment System v4.0 - File Storage Version",
        "storage_type": "file_based",
        "purpose": "rapid_development_testing",
        "api": {
            "documentation": "/api/docs",
            "health_check": "/api/system/health",
            "assessment_blocks": "/api/assessment/blocks",
            "assessment_submit": "/api/assessment/submit",
            "assessment_results": "/api/assessment/results/{session_id}"
        },
        "ui": {
            "main_entry": "/static/index.html",
            "landing": "/static/landing.html",
            "assessment_intro": "/static/assessment-intro.html",
            "assessment": "/static/assessment.html",
            "results": "/static/results.html",
            "report_detail": "/static/report-detail.html"
        },
        "advantages": [
            "快速數據修改和測試",
            "無需數據庫遷移",
            "易於備份和版本控制",
            "支持快速 try-and-error 開發"
        ]
    })


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main_files:app",
        host="0.0.0.0",
        port=8005,  # Use different port to avoid conflict
        reload=True,
        log_level="info"
    )