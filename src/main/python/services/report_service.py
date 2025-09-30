"""
Report Service - Business Logic Layer for Report Generation

This module implements the service layer for report generation, following Clean
Architecture principles. It orchestrates between the API layer and the core
report generation components.

Key Responsibilities:
- Coordinate report generation workflows
- Manage report lifecycle and status tracking
- Handle database persistence for reports
- Integrate with core.report modules
- Provide sharing and access control

Design Philosophy:
- Single Responsibility Principle
- Dependency Inversion (depends on abstractions)
- Error handling with specific error types
- Full audit trail and provenance tracking

Author: TaskMaster Agent (3.4.5)
Date: 2025-09-30
Version: 1.0
"""

import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import sqlite3
import json

from core.report.pdf_generator import PDFReportGenerator, PDFGenerationOptions, GenerationResult
from core.report.content_generator import ContentGenerator
from core.scoring import ScoringEngine, DimensionScores
from models.database import ReportGeneration, AssessmentSession, Score
from models.schemas import QuestionResponse
from models.report_models import (
    ReportGenerationRequest, ReportGenerationResponse, ReportMetadata,
    ReportStatus, ReportType, ReportFormat, ReportQuality,
    ReportPreviewRequest, ReportPreviewResponse, ReportSectionPreview,
    ReportStatusResponse, ReportError, ReportGenerationErrorResponse,
    ReportShareRequest, ReportShareResponse, ReportListResponse, ReportListItem
)
from utils.database import get_db_connection


class ReportGenerationError(Exception):
    """Custom exception for report generation errors."""

    def __init__(self, message: str, error_code: str = "GENERATION_ERROR", details: Optional[Dict] = None):
        super().__init__(message)
        self.error_code = error_code
        self.details = details or {}


class ReportNotFoundError(ReportGenerationError):
    """Exception for when a report is not found."""

    def __init__(self, report_id: str):
        super().__init__(f"Report not found: {report_id}", "REPORT_NOT_FOUND")
        self.report_id = report_id


class ReportAccessError(ReportGenerationError):
    """Exception for report access violations."""

    def __init__(self, message: str, report_id: str):
        super().__init__(message, "ACCESS_DENIED")
        self.report_id = report_id


class ReportService:
    """
    Main service class for report generation operations.

    This class provides the business logic layer between the API endpoints
    and the core report generation components.
    """

    def __init__(self, output_directory: str = "/tmp/reports"):
        """
        Initialize the report service.

        Args:
            output_directory: Directory for storing generated reports
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)

        # Initialize core components
        self.pdf_generator = PDFReportGenerator()
        self.content_generator = ContentGenerator()
        self.scoring_engine = ScoringEngine()

        # Generation tracking
        self._active_generations: Dict[str, asyncio.Task] = {}

    async def generate_report_from_responses(
        self,
        request: ReportGenerationRequest
    ) -> ReportGenerationResponse:
        """
        Generate a complete report from assessment responses.

        Args:
            request: Report generation request with responses and parameters

        Returns:
            ReportGenerationResponse with report metadata and access information

        Raises:
            ReportGenerationError: If generation fails
        """
        # Generate unique report ID
        report_id = f"RPT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"

        try:
            # Create database record
            with get_db_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO report_generations
                    (session_id, report_type, report_format, report_title,
                     generation_status, generation_started_at, file_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    report_id,  # Using report_id as session_id for direct generation
                    request.report_type.value,
                    request.report_format.value,
                    f"{request.user_name} - 個人優勢評估報告",
                    ReportStatus.PROCESSING.value,
                    datetime.now(),
                    None  # Will be updated after generation
                ))
                conn.commit()

            # Start async generation
            generation_task = asyncio.create_task(
                self._generate_report_async(report_id, request)
            )
            self._active_generations[report_id] = generation_task

            # Return immediate response
            return ReportGenerationResponse(
                success=True,
                report_id=report_id,
                status=ReportStatus.PROCESSING,
                metadata=ReportMetadata(
                    report_id=report_id,
                    report_type=request.report_type,
                    report_format=request.report_format,
                    report_quality=request.report_quality,
                    user_name=request.user_name,
                    assessment_date=datetime.now(),
                    generation_timestamp=datetime.now(),
                    generation_time_seconds=0.0  # Will be updated
                ),
                download_url=f"/api/reports/{report_id}/download",
                expires_at=datetime.now() + timedelta(hours=72)
            )

        except Exception as e:
            # Update database with error
            with get_db_connection() as conn:
                conn.execute("""
                    UPDATE report_generations
                    SET generation_status = ?, error_message = ?, generation_completed_at = ?
                    WHERE session_id = ?
                """, (ReportStatus.FAILED.value, str(e), datetime.now(), report_id))
                conn.commit()

            raise ReportGenerationError(
                f"Failed to initiate report generation: {str(e)}",
                "GENERATION_INIT_FAILED"
            )

    async def _generate_report_async(
        self,
        report_id: str,
        request: ReportGenerationRequest
    ) -> None:
        """
        Async report generation worker.

        Args:
            report_id: Unique report identifier
            request: Report generation request
        """
        start_time = datetime.now()

        try:
            # Convert Pydantic models to core models
            scoring_responses = []
            for response in request.responses:
                scoring_responses.append(response)

            # Configure PDF generation options
            pdf_options = PDFGenerationOptions(
                include_charts=request.include_charts,
                include_watermark=False,
                include_page_numbers=True,
                quality=request.report_quality.value
            )

            # Generate the report
            generation_result = self.pdf_generator.generate_report_from_responses(
                responses=scoring_responses,
                user_name=request.user_name,
                assessment_date=datetime.now(),
                user_context=request.user_context or {},
                options=pdf_options
            )

            if not generation_result.success:
                raise ReportGenerationError(
                    generation_result.error_message or "PDF generation failed",
                    "PDF_GENERATION_FAILED"
                )

            # Move file to permanent location
            final_path = self.output_directory / f"{report_id}.pdf"
            if generation_result.file_path:
                import shutil
                shutil.move(generation_result.file_path, str(final_path))

            # Update database with success
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            with get_db_connection() as conn:
                conn.execute("""
                    UPDATE report_generations
                    SET generation_status = ?, file_path = ?, file_size_bytes = ?,
                        generation_completed_at = ?, generation_time_ms = ?
                    WHERE session_id = ?
                """, (
                    ReportStatus.COMPLETED.value,
                    str(final_path),
                    generation_result.file_size_bytes,
                    end_time,
                    generation_time * 1000,  # Convert to milliseconds
                    report_id
                ))
                conn.commit()

        except Exception as e:
            # Update database with failure
            end_time = datetime.now()
            generation_time = (end_time - start_time).total_seconds()

            with get_db_connection() as conn:
                conn.execute("""
                    UPDATE report_generations
                    SET generation_status = ?, error_message = ?,
                        generation_completed_at = ?, generation_time_ms = ?
                    WHERE session_id = ?
                """, (
                    ReportStatus.FAILED.value,
                    str(e),
                    end_time,
                    generation_time * 1000,
                    report_id
                ))
                conn.commit()

        finally:
            # Clean up active generation tracking
            if report_id in self._active_generations:
                del self._active_generations[report_id]

    async def generate_report_from_session(
        self,
        session_id: str,
        user_name: str,
        report_type: ReportType = ReportType.FULL_ASSESSMENT,
        report_format: ReportFormat = ReportFormat.PDF,
        user_context: Optional[Dict[str, Any]] = None
    ) -> ReportGenerationResponse:
        """
        Generate a report from an existing assessment session.

        Args:
            session_id: Valid assessment session identifier
            user_name: Name of the assessment taker
            report_type: Type of report to generate
            report_format: Output format for the report
            user_context: Additional context for recommendations

        Returns:
            ReportGenerationResponse with report metadata

        Raises:
            ReportGenerationError: If session not found or generation fails
        """
        # Validate session and get responses
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT ar.question_number, ar.response_value
                FROM assessment_responses ar
                JOIN assessment_sessions asess ON ar.session_id = asess.session_id
                WHERE asess.session_id = ? AND asess.status = 'COMPLETED'
                ORDER BY ar.question_number
            """, (session_id,))

            responses_data = cursor.fetchall()

            if not responses_data or len(responses_data) != 20:
                raise ReportGenerationError(
                    f"Session {session_id} not found or incomplete",
                    "SESSION_NOT_FOUND"
                )

        # Convert to QuestionResponse objects
        responses = []
        for question_num, response_value in responses_data:
            # Convert 7-point to 5-point scale if needed
            converted_score = self._convert_scale_7_to_5(response_value)
            responses.append(QuestionResponse(
                question_id=question_num,
                score=converted_score
            ))

        # Create request object
        request = ReportGenerationRequest(
            responses=responses,
            user_name=user_name,
            report_type=report_type,
            report_format=report_format,
            user_context=user_context,
            include_charts=True,
            include_recommendations=True
        )

        return await self.generate_report_from_responses(request)

    def _convert_scale_7_to_5(self, value_7_point: int) -> int:
        """Convert 7-point Likert scale to 5-point scale."""
        conversion_map = {1: 1, 2: 2, 3: 2, 4: 3, 5: 4, 6: 4, 7: 5}
        return conversion_map.get(value_7_point, 3)

    async def get_report_status(self, report_id: str) -> ReportStatusResponse:
        """
        Get the current status of a report generation.

        Args:
            report_id: Report identifier

        Returns:
            ReportStatusResponse with current status

        Raises:
            ReportNotFoundError: If report not found
        """
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT session_id, report_type, report_format, generation_status,
                       generation_started_at, generation_completed_at, generation_time_ms,
                       file_size_bytes, error_message, created_at, updated_at,
                       report_title, report_data
                FROM report_generations
                WHERE session_id = ?
            """, (report_id,))

            row = cursor.fetchone()
            if not row:
                raise ReportNotFoundError(report_id)

            # Calculate progress for processing reports
            progress_percentage = None
            estimated_completion = None

            if row[3] == ReportStatus.PROCESSING.value:
                # Estimate progress based on elapsed time
                started_at = datetime.fromisoformat(row[4])
                elapsed = (datetime.now() - started_at).total_seconds()
                estimated_total = 120  # Assume 2 minutes average generation time
                progress_percentage = min(int((elapsed / estimated_total) * 100), 95)
                estimated_completion = started_at + timedelta(seconds=estimated_total)
            elif row[3] == ReportStatus.COMPLETED.value:
                progress_percentage = 100

            # Build metadata if completed
            metadata = None
            if row[3] == ReportStatus.COMPLETED.value and row[6]:  # generation_time_ms exists
                metadata = ReportMetadata(
                    report_id=report_id,
                    report_type=ReportType(row[1]),
                    report_format=ReportFormat(row[2]),
                    report_quality=ReportQuality.STANDARD,  # Default
                    user_name="Unknown",  # Could enhance DB schema
                    assessment_date=datetime.fromisoformat(row[4]),
                    generation_timestamp=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
                    file_size_bytes=row[7],
                    generation_time_seconds=row[6] / 1000 if row[6] else 0.0
                )

            return ReportStatusResponse(
                report_id=report_id,
                status=ReportStatus(row[3]),
                metadata=metadata,
                progress_percentage=progress_percentage,
                estimated_completion=estimated_completion,
                error_message=row[8],
                created_at=datetime.fromisoformat(row[9]),
                updated_at=datetime.fromisoformat(row[10]) if row[10] else datetime.fromisoformat(row[9])
            )

    async def get_report_file(self, report_id: str) -> Tuple[bytes, str, int]:
        """
        Get the actual report file content.

        Args:
            report_id: Report identifier

        Returns:
            Tuple of (file_content, filename, file_size)

        Raises:
            ReportNotFoundError: If report not found
            ReportAccessError: If report not accessible
        """
        # Get report metadata
        status_response = await self.get_report_status(report_id)

        if status_response.status != ReportStatus.COMPLETED:
            raise ReportAccessError(
                f"Report {report_id} is not ready for download (status: {status_response.status.value})",
                report_id
            )

        # Get file path from database
        with get_db_connection() as conn:
            cursor = conn.execute("""
                SELECT file_path, file_size_bytes, report_title
                FROM report_generations
                WHERE session_id = ? AND generation_status = ?
            """, (report_id, ReportStatus.COMPLETED.value))

            row = cursor.fetchone()
            if not row or not row[0]:
                raise ReportNotFoundError(report_id)

            file_path, file_size, report_title = row

        # Read file content
        try:
            with open(file_path, 'rb') as f:
                content = f.read()

            # Generate filename
            filename = f"{report_title or 'report'}_{report_id}.pdf"

            return content, filename, len(content)

        except FileNotFoundError:
            raise ReportAccessError(
                f"Report file not found for {report_id}",
                report_id
            )
        except Exception as e:
            raise ReportAccessError(
                f"Failed to read report file for {report_id}: {str(e)}",
                report_id
            )

    async def generate_report_preview(
        self,
        request: ReportPreviewRequest
    ) -> ReportPreviewResponse:
        """
        Generate a preview of report content without creating the actual file.

        Args:
            request: Preview request with responses and parameters

        Returns:
            ReportPreviewResponse with section previews and estimates
        """
        preview_id = f"PREV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[:8].upper()}"

        try:
            # Convert responses to Big Five scores for preview
            scoring_responses = []
            for response in request.responses:
                scoring_responses.append(response)

            # Quick scoring calculation
            response_values = [0] * 20
            for response in request.responses:
                response_values[response.question_id - 1] = response.score

            scores_dict = self.scoring_engine.calculate_scores_from_api(
                response_values, scale_type="5-point"
            )

            # Generate content preview without full generation
            dimension_scores = self.scoring_engine.create_dimension_scores_object(scores_dict)

            # Create mock sections based on typical report structure
            sections = [
                ReportSectionPreview(
                    section_type="cover_page",
                    title="Cover Page",
                    chinese_title="封面",
                    content_summary="報告標題、使用者資訊、評估日期",
                    element_count=4,
                    estimated_pages=1.0
                ),
                ReportSectionPreview(
                    section_type="executive_summary",
                    title="Executive Summary",
                    chinese_title="執行摘要",
                    content_summary="關鍵洞察、核心優勢、職業建議摘要",
                    element_count=6,
                    estimated_pages=1.5
                ),
                ReportSectionPreview(
                    section_type="personality_profile",
                    title="Personality Profile",
                    chinese_title="個性特質分析",
                    content_summary="Big Five 人格特質分數與詳細說明",
                    element_count=8,
                    estimated_pages=2.0
                ),
                ReportSectionPreview(
                    section_type="strength_analysis",
                    title="Strength Analysis",
                    chinese_title="優勢分析",
                    content_summary="前五項核心優勢與發展建議",
                    element_count=10,
                    estimated_pages=2.5
                ),
                ReportSectionPreview(
                    section_type="career_recommendations",
                    title="Career Recommendations",
                    chinese_title="職業建議",
                    content_summary="推薦職位、匹配度分析、發展方向",
                    element_count=12,
                    estimated_pages=3.0
                )
            ]

            # Create assessment summary
            assessment_summary = {
                "big_five_scores": scores_dict,
                "dominant_traits": self._identify_dominant_traits(scores_dict),
                "assessment_quality": "high",
                "completion_time": "estimated"
            }

            total_pages = sum(section.estimated_pages for section in sections)

            return ReportPreviewResponse(
                preview_id=preview_id,
                user_name=request.user_name,
                assessment_summary=assessment_summary,
                sections=sections,
                total_estimated_pages=int(total_pages),
                generation_estimate_seconds=min(total_pages * 15, 120),  # Estimate 15 sec per page
                generated_at=datetime.now()
            )

        except Exception as e:
            raise ReportGenerationError(
                f"Failed to generate preview: {str(e)}",
                "PREVIEW_GENERATION_FAILED"
            )

    def _identify_dominant_traits(self, scores_dict: Dict[str, float]) -> List[str]:
        """Identify dominant personality traits from scores."""
        trait_thresholds = 15.0  # Above average threshold
        dominant = []

        for trait, score in scores_dict.items():
            if score > trait_thresholds:
                dominant.append(trait)

        return sorted(dominant, key=lambda t: scores_dict[t], reverse=True)[:3]

    async def list_reports(
        self,
        page: int = 1,
        page_size: int = 20,
        status_filter: Optional[ReportStatus] = None
    ) -> ReportListResponse:
        """
        List generated reports with pagination and filtering.

        Args:
            page: Page number (1-based)
            page_size: Number of items per page
            status_filter: Optional status filter

        Returns:
            ReportListResponse with paginated results
        """
        offset = (page - 1) * page_size

        # Build query with optional status filter
        base_query = """
            SELECT session_id, report_type, generation_status, created_at, file_size_bytes,
                   report_title
            FROM report_generations
        """
        count_query = "SELECT COUNT(*) FROM report_generations"

        params = []
        if status_filter:
            base_query += " WHERE generation_status = ?"
            count_query += " WHERE generation_status = ?"
            params.append(status_filter.value)

        base_query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([page_size, offset])

        with get_db_connection() as conn:
            # Get total count
            count_cursor = conn.execute(count_query, params[:-2] if status_filter else [])
            total_count = count_cursor.fetchone()[0]

            # Get paginated results
            cursor = conn.execute(base_query, params)
            rows = cursor.fetchall()

            # Convert to response objects
            reports = []
            for row in rows:
                reports.append(ReportListItem(
                    report_id=row[0],
                    report_type=ReportType(row[1]),
                    user_name=row[5] or "Unknown",  # From report_title, could be enhanced
                    status=ReportStatus(row[2]),
                    created_at=datetime.fromisoformat(row[3]),
                    file_size_bytes=row[4]
                ))

            has_next = (page * page_size) < total_count

            return ReportListResponse(
                reports=reports,
                total_count=total_count,
                page=page,
                page_size=page_size,
                has_next=has_next
            )

    async def delete_report(self, report_id: str) -> bool:
        """
        Delete a report and its associated file.

        Args:
            report_id: Report identifier

        Returns:
            True if deletion successful

        Raises:
            ReportNotFoundError: If report not found
        """
        with get_db_connection() as conn:
            # Get file path before deletion
            cursor = conn.execute("""
                SELECT file_path FROM report_generations WHERE session_id = ?
            """, (report_id,))

            row = cursor.fetchone()
            if not row:
                raise ReportNotFoundError(report_id)

            file_path = row[0]

            # Delete database record
            cursor = conn.execute("""
                DELETE FROM report_generations WHERE session_id = ?
            """, (report_id,))

            if cursor.rowcount == 0:
                raise ReportNotFoundError(report_id)

            conn.commit()

            # Delete file if exists
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception:
                    # Log warning but don't fail
                    pass

            return True

    async def cleanup_expired_reports(self, days_old: int = 7) -> int:
        """
        Clean up reports older than specified days.

        Args:
            days_old: Number of days to keep reports

        Returns:
            Number of reports cleaned up
        """
        cutoff_date = datetime.now() - timedelta(days=days_old)

        with get_db_connection() as conn:
            # Get file paths for cleanup
            cursor = conn.execute("""
                SELECT session_id, file_path FROM report_generations
                WHERE created_at < ?
            """, (cutoff_date,))

            old_reports = cursor.fetchall()

            # Delete database records
            cursor = conn.execute("""
                DELETE FROM report_generations WHERE created_at < ?
            """, (cutoff_date,))

            deleted_count = cursor.rowcount
            conn.commit()

            # Delete files
            for report_id, file_path in old_reports:
                if file_path and os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        # Log warning but continue
                        pass

            return deleted_count


# Convenience factory function
def create_report_service(output_directory: str = "/tmp/reports") -> ReportService:
    """
    Factory function to create a configured report service.

    Args:
        output_directory: Directory for storing generated reports

    Returns:
        Configured ReportService instance
    """
    return ReportService(output_directory)