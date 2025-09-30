"""
Report Models - Pydantic schemas for Report Generation API

This module defines all Pydantic models specifically for the report generation
system, following FastAPI best practices and clean architecture principles.

Key Models:
- ReportGenerationRequest/Response: API request/response models
- ReportStatusModels: Report status tracking
- ReportMetadata: Report generation metadata
- ReportPreview: Preview functionality models

Design Philosophy:
- Clear separation between API models and database models
- Strong validation for all report generation parameters
- Comprehensive error handling with specific error codes
- Full provenance tracking for explainability

Author: TaskMaster Agent (3.4.5)
Date: 2025-09-30
Version: 1.0
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, validator, root_validator
from models.schemas import QuestionResponse


class ReportFormat(str, Enum):
    """Supported report output formats."""
    PDF = "pdf"
    HTML = "html"  # Future support
    JSON = "json"  # Future support


class ReportStatus(str, Enum):
    """Report generation status values."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class ReportType(str, Enum):
    """Types of reports that can be generated."""
    FULL_ASSESSMENT = "full_assessment"
    EXECUTIVE_SUMMARY = "executive_summary"
    STRENGTH_PROFILE = "strength_profile"
    CAREER_GUIDANCE = "career_guidance"


class ReportQuality(str, Enum):
    """Report generation quality levels."""
    DRAFT = "draft"
    STANDARD = "standard"
    HIGH = "high"


# Request Models
class ReportGenerationRequest(BaseModel):
    """Request model for generating a new report from assessment responses."""
    responses: List[QuestionResponse] = Field(
        ...,
        min_items=20,
        max_items=20,
        description="Complete set of 20 Mini-IPIP assessment responses"
    )
    user_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the person taking the assessment"
    )
    report_type: ReportType = Field(
        default=ReportType.FULL_ASSESSMENT,
        description="Type of report to generate"
    )
    report_format: ReportFormat = Field(
        default=ReportFormat.PDF,
        description="Output format for the report"
    )
    report_quality: ReportQuality = Field(
        default=ReportQuality.STANDARD,
        description="Quality level for report generation"
    )
    user_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for personalized recommendations"
    )
    include_charts: bool = Field(
        default=True,
        description="Whether to include data visualization charts"
    )
    include_recommendations: bool = Field(
        default=True,
        description="Whether to include career and development recommendations"
    )

    @validator('responses')
    def validate_complete_responses(cls, v):
        """Ensure all 20 questions are answered."""
        question_ids = {r.question_id for r in v}
        expected_ids = set(range(1, 21))
        if question_ids != expected_ids:
            missing = expected_ids - question_ids
            extra = question_ids - expected_ids
            raise ValueError(f"Invalid question IDs. Missing: {missing}, Extra: {extra}")
        return v

    @validator('user_name')
    def validate_user_name(cls, v):
        """Validate user name format."""
        if not v.strip():
            raise ValueError("User name cannot be empty")
        return v.strip()


class ReportPreviewRequest(BaseModel):
    """Request model for generating a report preview without file generation."""
    responses: List[QuestionResponse] = Field(
        ...,
        min_items=20,
        max_items=20,
        description="Complete set of 20 Mini-IPIP assessment responses"
    )
    user_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the person taking the assessment"
    )
    sections: Optional[List[str]] = Field(
        None,
        description="Specific sections to preview (if None, all sections included)"
    )
    user_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for personalized recommendations"
    )


class ReportSessionRequest(BaseModel):
    """Request model for generating a report from an existing session."""
    session_id: str = Field(
        ...,
        description="Valid assessment session identifier"
    )
    user_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Name of the person taking the assessment"
    )
    report_type: ReportType = Field(
        default=ReportType.FULL_ASSESSMENT,
        description="Type of report to generate"
    )
    report_format: ReportFormat = Field(
        default=ReportFormat.PDF,
        description="Output format for the report"
    )
    report_quality: ReportQuality = Field(
        default=ReportQuality.STANDARD,
        description="Quality level for report generation"
    )
    user_context: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional context for personalized recommendations"
    )


# Response Models
class ReportMetadata(BaseModel):
    """Metadata about generated report."""
    report_id: str = Field(..., description="Unique report identifier")
    report_type: ReportType = Field(..., description="Type of report generated")
    report_format: ReportFormat = Field(..., description="Output format used")
    report_quality: ReportQuality = Field(..., description="Quality level used")
    user_name: str = Field(..., description="Assessment taker name")
    assessment_date: datetime = Field(..., description="Date of assessment")
    generation_timestamp: datetime = Field(..., description="Report generation timestamp")
    file_size_bytes: Optional[int] = Field(None, description="Generated file size")
    generation_time_seconds: float = Field(..., description="Time taken to generate report")
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall confidence in results")


class ReportGenerationResponse(BaseModel):
    """Response model for successful report generation."""
    success: bool = Field(True, description="Generation success status")
    report_id: str = Field(..., description="Unique report identifier")
    status: ReportStatus = Field(..., description="Current report status")
    metadata: ReportMetadata = Field(..., description="Report metadata")
    download_url: Optional[str] = Field(None, description="URL to download the report")
    share_url: Optional[str] = Field(None, description="Shareable URL for the report")
    expires_at: Optional[datetime] = Field(None, description="Report expiration timestamp")
    warnings: List[str] = Field(default_factory=list, description="Generation warnings")


class ReportStatusResponse(BaseModel):
    """Response model for report status queries."""
    report_id: str = Field(..., description="Report identifier")
    status: ReportStatus = Field(..., description="Current report status")
    metadata: Optional[ReportMetadata] = Field(None, description="Report metadata if available")
    progress_percentage: Optional[int] = Field(None, ge=0, le=100, description="Generation progress")
    estimated_completion: Optional[datetime] = Field(None, description="Estimated completion time")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    created_at: datetime = Field(..., description="Report creation timestamp")
    updated_at: datetime = Field(..., description="Last status update timestamp")


class ReportListItem(BaseModel):
    """Individual report item in list responses."""
    report_id: str = Field(..., description="Report identifier")
    report_type: ReportType = Field(..., description="Type of report")
    user_name: str = Field(..., description="Assessment taker name")
    status: ReportStatus = Field(..., description="Current status")
    created_at: datetime = Field(..., description="Creation timestamp")
    file_size_bytes: Optional[int] = Field(None, description="File size if completed")


class ReportListResponse(BaseModel):
    """Response model for listing reports."""
    reports: List[ReportListItem] = Field(..., description="List of reports")
    total_count: int = Field(..., ge=0, description="Total number of reports")
    page: int = Field(..., ge=1, description="Current page number")
    page_size: int = Field(..., ge=1, le=100, description="Number of items per page")
    has_next: bool = Field(..., description="Whether there are more pages")


# Preview Models
class ReportSectionPreview(BaseModel):
    """Preview of a single report section."""
    section_type: str = Field(..., description="Section type identifier")
    title: str = Field(..., description="Section title")
    chinese_title: str = Field(..., description="Chinese section title")
    content_summary: str = Field(..., description="Brief content summary")
    element_count: int = Field(..., ge=0, description="Number of content elements")
    estimated_pages: float = Field(..., ge=0, description="Estimated page count")


class ReportPreviewResponse(BaseModel):
    """Response model for report previews."""
    preview_id: str = Field(..., description="Unique preview identifier")
    user_name: str = Field(..., description="Assessment taker name")
    assessment_summary: Dict[str, Any] = Field(..., description="Assessment results summary")
    sections: List[ReportSectionPreview] = Field(..., description="Section previews")
    total_estimated_pages: int = Field(..., ge=1, description="Total estimated page count")
    generation_estimate_seconds: float = Field(..., ge=0, description="Estimated generation time")
    generated_at: datetime = Field(..., description="Preview generation timestamp")


# Error Models
class ReportError(BaseModel):
    """Report generation error model."""
    error_code: str = Field(..., description="Specific error code")
    error_message: str = Field(..., description="Human-readable error message")
    error_type: str = Field(..., description="Category of error")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    retry_possible: bool = Field(..., description="Whether retry is possible")
    suggested_action: Optional[str] = Field(None, description="Suggested action for user")


class ReportGenerationErrorResponse(BaseModel):
    """Response model for report generation failures."""
    success: bool = Field(False, description="Generation success status")
    error: ReportError = Field(..., description="Error information")
    report_id: Optional[str] = Field(None, description="Report ID if partially created")
    trace_id: str = Field(..., description="Error trace identifier")
    timestamp: datetime = Field(..., description="Error timestamp")


# Sharing Models
class ReportShareRequest(BaseModel):
    """Request model for creating report share links."""
    report_id: str = Field(..., description="Report identifier to share")
    expiry_hours: int = Field(
        default=72,
        ge=1,
        le=168,  # Max 1 week
        description="Share link expiry time in hours"
    )
    max_downloads: int = Field(
        default=1,
        ge=1,
        le=10,
        description="Maximum number of downloads allowed"
    )
    password_protected: bool = Field(
        default=False,
        description="Whether to protect with password"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        description="Password for protected links"
    )

    @validator('password')
    def validate_password_if_protected(cls, v, values):
        """Validate password is provided if protection is enabled."""
        if values.get('password_protected') and not v:
            raise ValueError("Password is required when password_protected is True")
        return v


class ReportShareResponse(BaseModel):
    """Response model for report sharing."""
    share_id: str = Field(..., description="Unique share identifier")
    share_url: str = Field(..., description="Shareable URL")
    report_id: str = Field(..., description="Associated report identifier")
    expires_at: datetime = Field(..., description="Share link expiration")
    max_downloads: int = Field(..., description="Maximum downloads allowed")
    current_downloads: int = Field(default=0, description="Current download count")
    password_protected: bool = Field(..., description="Whether password protected")
    created_at: datetime = Field(..., description="Share creation timestamp")


# Configuration Models
class ReportGenerationConfig(BaseModel):
    """Configuration options for report generation."""
    default_format: ReportFormat = Field(default=ReportFormat.PDF)
    default_quality: ReportQuality = Field(default=ReportQuality.STANDARD)
    max_generation_time_seconds: int = Field(default=300, ge=30, le=600)
    enable_caching: bool = Field(default=True)
    cache_ttl_hours: int = Field(default=24, ge=1, le=168)
    max_concurrent_generations: int = Field(default=5, ge=1, le=20)
    output_directory: str = Field(default="/tmp/reports")
    enable_sharing: bool = Field(default=True)
    default_share_expiry_hours: int = Field(default=72, ge=1, le=168)


# Statistics Models
class ReportGenerationStats(BaseModel):
    """Statistics about report generation system."""
    total_reports_generated: int = Field(..., ge=0, description="Total reports generated")
    reports_by_status: Dict[ReportStatus, int] = Field(..., description="Reports by status")
    reports_by_type: Dict[ReportType, int] = Field(..., description="Reports by type")
    average_generation_time_seconds: float = Field(..., ge=0, description="Average generation time")
    success_rate_percentage: float = Field(..., ge=0, le=100, description="Success rate")
    most_common_errors: List[str] = Field(..., description="Most common error types")
    generated_at: datetime = Field(..., description="Statistics generation timestamp")


# Health Check Models for Report Service
class ReportServiceHealth(BaseModel):
    """Health check model for report generation service."""
    service_status: str = Field(..., description="Overall service status")
    generation_queue_size: int = Field(..., ge=0, description="Current queue size")
    active_generations: int = Field(..., ge=0, description="Currently active generations")
    disk_space_available_mb: float = Field(..., ge=0, description="Available disk space")
    last_successful_generation: Optional[datetime] = Field(None, description="Last successful generation")
    error_rate_last_hour: float = Field(..., ge=0, le=100, description="Error rate in last hour")
    dependencies: Dict[str, str] = Field(..., description="Dependency status")