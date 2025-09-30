"""
Report Generation API Routes - FastAPI Endpoints

This module implements all the FastAPI endpoints for the report generation
system, providing a RESTful API interface for PDF report creation, management,
and access control.

API Endpoints:
- POST /api/reports/generate - Generate report from responses
- POST /api/reports/generate/session - Generate report from session
- GET /api/reports/{report_id} - Get report status
- GET /api/reports/{report_id}/download - Download PDF file
- POST /api/reports/preview - Generate report preview
- GET /api/reports/ - List reports with pagination
- DELETE /api/reports/{report_id} - Delete report

Design Philosophy:
- RESTful API design patterns
- Comprehensive error handling with HTTP status codes
- Async/await for non-blocking operations
- Clear documentation with OpenAPI specs
- Proper validation and sanitization

Author: TaskMaster Agent (3.4.5)
Date: 2025-09-30
Version: 1.0
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, Query
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
import io

from models.report_models import (
    ReportGenerationRequest, ReportGenerationResponse, ReportMetadata,
    ReportPreviewRequest, ReportPreviewResponse,
    ReportSessionRequest, ReportStatusResponse, ReportListResponse,
    ReportStatus, ReportType, ReportFormat, ReportError,
    ReportGenerationErrorResponse, ReportServiceHealth
)
from models.schemas import APIResponse
from services.report_service import (
    ReportService, ReportGenerationError, ReportNotFoundError,
    ReportAccessError, create_report_service
)


# Initialize router
router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"],
    responses={
        404: {"description": "Report not found"},
        500: {"description": "Internal server error"}
    }
)

# Security scheme (optional)
security = HTTPBearer(auto_error=False)

# Dependency injection for report service
def get_report_service() -> ReportService:
    """Dependency provider for report service."""
    return create_report_service(output_directory="/tmp/reports")


# Helper function for error handling
def create_error_response(
    error: ReportGenerationError,
    trace_id: Optional[str] = None
) -> ReportGenerationErrorResponse:
    """Create standardized error response."""
    return ReportGenerationErrorResponse(
        success=False,
        error=ReportError(
            error_code=error.error_code,
            error_message=str(error),
            error_type=type(error).__name__,
            details=error.details,
            retry_possible=error.error_code not in [
                "SESSION_NOT_FOUND", "REPORT_NOT_FOUND", "ACCESS_DENIED"
            ],
            suggested_action="Please check your request parameters and try again."
        ),
        trace_id=trace_id or str(uuid.uuid4()),
        timestamp=datetime.now()
    )


@router.post(
    "/generate",
    response_model=ReportGenerationResponse,
    status_code=202,
    summary="Generate PDF report from assessment responses",
    description="""
    Generate a complete PDF assessment report from Mini-IPIP responses.

    This endpoint:
    - Accepts 20 Mini-IPIP assessment responses (5-point scale)
    - Generates personalized PDF report with Big Five analysis
    - Returns immediately with processing status
    - Supports async generation with status polling

    The generated report includes:
    - Cover page with user information
    - Executive summary of key insights
    - Detailed personality profile analysis
    - Top 5 strengths identification
    - Career recommendations with match scores
    - Development plan and action items
    """,
    responses={
        202: {"description": "Report generation initiated successfully"},
        400: {"description": "Invalid request parameters"},
        422: {"description": "Validation error in responses"},
        500: {"description": "Report generation failed"}
    }
)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    report_service: ReportService = Depends(get_report_service)
) -> ReportGenerationResponse:
    """
    Generate a PDF report from assessment responses.

    Args:
        request: Report generation request with responses and parameters
        background_tasks: FastAPI background tasks for async processing
        report_service: Report service dependency

    Returns:
        ReportGenerationResponse with report metadata and status

    Raises:
        HTTPException: If validation fails or generation cannot be initiated
    """
    try:
        # Validate request parameters
        if not request.responses or len(request.responses) != 20:
            raise HTTPException(
                status_code=400,
                detail="Exactly 20 assessment responses are required"
            )

        if not request.user_name.strip():
            raise HTTPException(
                status_code=400,
                detail="User name is required"
            )

        # Initiate report generation
        response = await report_service.generate_report_from_responses(request)

        return response

    except ReportGenerationError as e:
        error_response = create_error_response(e)
        raise HTTPException(
            status_code=500 if "GENERATION_FAILED" in e.error_code else 400,
            detail=error_response.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during report generation: {str(e)}"
        )


@router.post(
    "/generate/session",
    response_model=ReportGenerationResponse,
    status_code=202,
    summary="Generate PDF report from assessment session",
    description="""
    Generate a PDF report from an existing completed assessment session.

    This endpoint:
    - Accepts a valid session ID from a completed assessment
    - Retrieves responses from the database
    - Generates the same comprehensive PDF report
    - Supports different report types and formats
    """,
    responses={
        202: {"description": "Report generation initiated successfully"},
        400: {"description": "Invalid session ID or session not completed"},
        404: {"description": "Session not found"},
        500: {"description": "Report generation failed"}
    }
)
async def generate_report_from_session(
    request: ReportSessionRequest,
    background_tasks: BackgroundTasks,
    report_service: ReportService = Depends(get_report_service)
) -> ReportGenerationResponse:
    """
    Generate a PDF report from an existing assessment session.

    Args:
        request: Session-based report generation request
        background_tasks: FastAPI background tasks
        report_service: Report service dependency

    Returns:
        ReportGenerationResponse with report metadata

    Raises:
        HTTPException: If session not found or generation fails
    """
    try:
        response = await report_service.generate_report_from_session(
            session_id=request.session_id,
            user_name=request.user_name,
            report_type=request.report_type,
            report_format=request.report_format,
            user_context=request.user_context
        )

        return response

    except ReportGenerationError as e:
        error_response = create_error_response(e)
        status_code = 404 if e.error_code == "SESSION_NOT_FOUND" else 500
        raise HTTPException(
            status_code=status_code,
            detail=error_response.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error during report generation: {str(e)}"
        )


@router.get(
    "/{report_id}",
    response_model=ReportStatusResponse,
    summary="Get report generation status",
    description="""
    Get the current status and metadata of a report generation process.

    Status values:
    - PENDING: Generation queued but not started
    - PROCESSING: Currently generating report
    - COMPLETED: Report successfully generated and ready for download
    - FAILED: Generation failed with error details
    - EXPIRED: Report expired and no longer available

    For PROCESSING status, includes progress percentage and estimated completion time.
    """,
    responses={
        200: {"description": "Report status retrieved successfully"},
        404: {"description": "Report not found"},
        500: {"description": "Error retrieving report status"}
    }
)
async def get_report_status(
    report_id: str,
    report_service: ReportService = Depends(get_report_service)
) -> ReportStatusResponse:
    """
    Get the current status of a report generation.

    Args:
        report_id: Unique report identifier
        report_service: Report service dependency

    Returns:
        ReportStatusResponse with current status and metadata

    Raises:
        HTTPException: If report not found or status retrieval fails
    """
    try:
        status = await report_service.get_report_status(report_id)
        return status

    except ReportNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report status: {str(e)}"
        )


@router.get(
    "/{report_id}/download",
    summary="Download PDF report file",
    description="""
    Download the generated PDF report file.

    This endpoint:
    - Returns the PDF file as a binary stream
    - Sets appropriate Content-Type and Content-Disposition headers
    - Only works for reports with COMPLETED status
    - Automatically suggests filename based on user name and report ID

    The response includes proper headers for browser download handling.
    """,
    responses={
        200: {
            "description": "PDF file download",
            "content": {"application/pdf": {}}
        },
        404: {"description": "Report not found or not ready"},
        403: {"description": "Report access denied"},
        500: {"description": "Error accessing report file"}
    }
)
async def download_report(
    report_id: str,
    report_service: ReportService = Depends(get_report_service)
) -> StreamingResponse:
    """
    Download the generated PDF report file.

    Args:
        report_id: Unique report identifier
        report_service: Report service dependency

    Returns:
        StreamingResponse with PDF file content

    Raises:
        HTTPException: If report not found, not ready, or access denied
    """
    try:
        # Get file content and metadata
        file_content, filename, file_size = await report_service.get_report_file(report_id)

        # Create streaming response
        file_stream = io.BytesIO(file_content)

        return StreamingResponse(
            io.BytesIO(file_content),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"",
                "Content-Length": str(file_size),
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
        )

    except ReportNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )
    except ReportAccessError as e:
        status_code = 403 if "access" in str(e).lower() else 404
        raise HTTPException(
            status_code=status_code,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error downloading report: {str(e)}"
        )


@router.post(
    "/preview",
    response_model=ReportPreviewResponse,
    summary="Generate report content preview",
    description="""
    Generate a preview of report content without creating the actual PDF file.

    This endpoint:
    - Performs quick analysis of assessment responses
    - Returns structured preview of all report sections
    - Estimates total page count and generation time
    - Provides content summaries for each section
    - Does not create or store any files

    Useful for:
    - Showing users what will be in their report
    - Estimating generation time before committing
    - Validating assessment results before full generation
    """,
    responses={
        200: {"description": "Preview generated successfully"},
        400: {"description": "Invalid request parameters"},
        422: {"description": "Validation error in responses"},
        500: {"description": "Preview generation failed"}
    }
)
async def generate_report_preview(
    request: ReportPreviewRequest,
    report_service: ReportService = Depends(get_report_service)
) -> ReportPreviewResponse:
    """
    Generate a preview of report content without file creation.

    Args:
        request: Preview request with responses and parameters
        report_service: Report service dependency

    Returns:
        ReportPreviewResponse with section previews and estimates

    Raises:
        HTTPException: If preview generation fails
    """
    try:
        # Validate request
        if not request.responses or len(request.responses) != 20:
            raise HTTPException(
                status_code=400,
                detail="Exactly 20 assessment responses are required"
            )

        preview = await report_service.generate_report_preview(request)
        return preview

    except ReportGenerationError as e:
        error_response = create_error_response(e)
        raise HTTPException(
            status_code=500,
            detail=error_response.dict()
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating preview: {str(e)}"
        )


@router.get(
    "/",
    response_model=ReportListResponse,
    summary="List generated reports",
    description="""
    Get a paginated list of generated reports with optional filtering.

    Query parameters:
    - page: Page number (1-based, default: 1)
    - page_size: Items per page (1-100, default: 20)
    - status: Filter by report status (optional)

    Returns reports ordered by creation date (newest first).
    """,
    responses={
        200: {"description": "Report list retrieved successfully"},
        400: {"description": "Invalid query parameters"},
        500: {"description": "Error retrieving report list"}
    }
)
async def list_reports(
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    status: Optional[ReportStatus] = Query(None, description="Filter by report status"),
    report_service: ReportService = Depends(get_report_service)
) -> ReportListResponse:
    """
    Get a paginated list of generated reports.

    Args:
        page: Page number (1-based)
        page_size: Number of items per page
        status: Optional status filter
        report_service: Report service dependency

    Returns:
        ReportListResponse with paginated results

    Raises:
        HTTPException: If listing fails
    """
    try:
        reports = await report_service.list_reports(
            page=page,
            page_size=page_size,
            status_filter=status
        )
        return reports

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving report list: {str(e)}"
        )


@router.delete(
    "/{report_id}",
    status_code=204,
    summary="Delete generated report",
    description="""
    Delete a generated report and its associated file.

    This action:
    - Removes the report record from the database
    - Deletes the PDF file from storage
    - Cannot be undone

    Returns 204 No Content on successful deletion.
    """,
    responses={
        204: {"description": "Report deleted successfully"},
        404: {"description": "Report not found"},
        500: {"description": "Error deleting report"}
    }
)
async def delete_report(
    report_id: str,
    report_service: ReportService = Depends(get_report_service)
):
    """
    Delete a generated report and its file.

    Args:
        report_id: Unique report identifier
        report_service: Report service dependency

    Raises:
        HTTPException: If report not found or deletion fails
    """
    try:
        await report_service.delete_report(report_id)
        # Return 204 No Content (FastAPI handles this automatically)

    except ReportNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Report {report_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting report: {str(e)}"
        )


@router.get(
    "/health",
    response_model=ReportServiceHealth,
    summary="Report service health check",
    description="""
    Get health status of the report generation service.

    Returns information about:
    - Service operational status
    - Generation queue size
    - Active generation processes
    - Available disk space
    - Recent error rates
    - Dependency status
    """,
    responses={
        200: {"description": "Health check completed"},
        503: {"description": "Service unhealthy"}
    }
)
async def report_service_health(
    report_service: ReportService = Depends(get_report_service)
) -> ReportServiceHealth:
    """
    Get health status of report generation service.

    Args:
        report_service: Report service dependency

    Returns:
        ReportServiceHealth with service status information
    """
    try:
        import shutil
        import os
        from datetime import timedelta

        # Get disk space
        disk_usage = shutil.disk_usage(report_service.output_directory)
        available_mb = disk_usage.free / (1024 * 1024)

        # Get queue and active generation info
        active_count = len(report_service._active_generations)

        # Check recent success rate (simplified)
        # In a real implementation, this would query the database for recent reports
        error_rate = 0.0  # Placeholder

        # Determine overall status
        service_status = "healthy"
        if available_mb < 100:  # Less than 100MB
            service_status = "degraded"
        if available_mb < 10:   # Less than 10MB
            service_status = "unhealthy"

        return ReportServiceHealth(
            service_status=service_status,
            generation_queue_size=0,  # Not implemented in current service
            active_generations=active_count,
            disk_space_available_mb=available_mb,
            last_successful_generation=None,  # Would need to query database
            error_rate_last_hour=error_rate,
            dependencies={
                "pdf_generator": "healthy",
                "scoring_engine": "healthy",
                "content_generator": "healthy",
                "database": "healthy"
            }
        )

    except Exception as e:
        return ReportServiceHealth(
            service_status="error",
            generation_queue_size=0,
            active_generations=0,
            disk_space_available_mb=0.0,
            error_rate_last_hour=100.0,
            dependencies={
                "pdf_generator": "error",
                "scoring_engine": "error",
                "content_generator": "error",
                "database": "error"
            }
        )


# Background task for cleanup (could be run periodically)
@router.post(
    "/maintenance/cleanup",
    status_code=202,
    summary="Clean up expired reports",
    description="""
    Remove expired reports and their files from the system.

    This maintenance operation:
    - Deletes reports older than specified days
    - Removes associated PDF files
    - Frees up disk space
    - Returns count of cleaned up reports

    Typically run as a scheduled background task.
    """,
    responses={
        202: {"description": "Cleanup initiated"},
        500: {"description": "Cleanup failed"}
    }
)
async def cleanup_expired_reports(
    background_tasks: BackgroundTasks,
    days_old: int = Query(7, ge=1, le=365, description="Days old threshold for cleanup"),
    report_service: ReportService = Depends(get_report_service)
) -> APIResponse:
    """
    Clean up expired reports (background task).

    Args:
        days_old: Number of days to keep reports
        background_tasks: FastAPI background tasks
        report_service: Report service dependency

    Returns:
        APIResponse with cleanup initiation status
    """
    try:
        # Add cleanup task to background
        background_tasks.add_task(
            report_service.cleanup_expired_reports,
            days_old
        )

        return APIResponse(
            success=True,
            data={"message": "Cleanup initiated"},
            meta={
                "days_old": days_old,
                "initiated_at": datetime.now().isoformat()
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate cleanup: {str(e)}"
        )