"""
V4.0 Data Collection API Routes
Task 8.1.4: Test data collection endpoints

Manages participant recruitment and data collection for calibration.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from datetime import datetime
import json

from services.v4_data_collector import get_data_collector

router = APIRouter(prefix="/api/v4/data-collection")


# Request/Response Models
class ParticipantRegistration(BaseModel):
    """Participant registration request"""
    age: Optional[int] = Field(None, ge=18, le=100)
    gender: Optional[str] = Field(None, pattern="^(male|female|other|prefer_not_to_say)$")
    education: Optional[str] = Field(None)
    test_group: str = Field("pilot", pattern="^(pilot|calibration|validation)$")
    metadata: Dict[str, Any] = Field(default_factory=dict)


class TestSessionRequest(BaseModel):
    """Test session request"""
    participant_id: str
    test_version: str = Field("v4", pattern="^(v3|v4)$")


class ResponseSubmission(BaseModel):
    """Response submission request"""
    session_id: str
    responses: List[Dict[str, Any]]
    completion_time_seconds: float = Field(..., gt=0)


class CollectionStats(BaseModel):
    """Data collection statistics"""
    total_participants: int
    target_sample_size: int
    completion_rate: float
    participants_by_group: Dict[str, int]
    complete_sessions: Dict[str, int]
    timing: Dict[str, float]
    quality: Dict[str, Any]


@router.post("/participants/register")
async def register_participant(registration: ParticipantRegistration):
    """
    Register a new test participant.

    Returns participant ID for tracking.
    """
    try:
        collector = get_data_collector()
        participant_id = collector.register_participant(
            age=registration.age,
            gender=registration.gender,
            education=registration.education,
            test_group=registration.test_group,
            **registration.metadata
        )

        return {
            "status": "success",
            "participant_id": participant_id,
            "test_group": registration.test_group,
            "message": f"Participant registered successfully in {registration.test_group} group"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/sessions/start")
async def start_test_session(request: TestSessionRequest):
    """
    Start a new test session for a participant.

    Creates session and returns blocks for testing.
    """
    try:
        collector = get_data_collector()

        # Generate blocks based on version
        if request.test_version == "v4":
            # Import here to avoid circular dependency
            from api.routes.v4_assessment import get_assessment_blocks, BlockRequest

            # Generate v4 blocks
            blocks_response = await get_assessment_blocks(BlockRequest(block_count=15))
            blocks_data = []
            for block in blocks_response.blocks:
                blocks_data.append({
                    'block_id': block.block_id,
                    'statement_ids': [s.id for s in block.statements]
                })
        else:
            # For v3, create simplified blocks
            blocks_data = []
            for i in range(30):
                blocks_data.append({
                    'block_id': i,
                    'pair': [f"S{i*2}", f"S{i*2+1}"]
                })

        # Start session
        session_id = collector.start_test_session(
            participant_id=request.participant_id,
            test_version=request.test_version,
            blocks_data=blocks_data
        )

        return {
            "status": "success",
            "session_id": session_id,
            "test_version": request.test_version,
            "blocks": blocks_data if request.test_version == "v4" else blocks_response.blocks,
            "total_blocks": len(blocks_data)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start session: {str(e)}")


@router.post("/sessions/submit")
async def submit_responses(submission: ResponseSubmission):
    """
    Submit test responses for a session.

    Validates and stores response data for calibration.
    """
    try:
        collector = get_data_collector()
        success = collector.save_responses(
            session_id=submission.session_id,
            responses=submission.responses,
            completion_time_seconds=submission.completion_time_seconds
        )

        if success:
            return {
                "status": "success",
                "session_id": submission.session_id,
                "message": "Responses saved successfully"
            }
        else:
            raise ValueError("Failed to save responses")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


@router.get("/stats", response_model=CollectionStats)
async def get_collection_statistics():
    """
    Get current data collection statistics.

    Returns overview of recruitment and data quality.
    """
    try:
        collector = get_data_collector()
        stats = collector.get_collection_stats()
        return CollectionStats(**stats)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")


@router.get("/participants/{participant_id}/progress")
async def get_participant_progress(participant_id: str):
    """
    Get progress for a specific participant.

    Returns session history and completion status.
    """
    try:
        collector = get_data_collector()
        progress = collector.get_participant_progress(participant_id)

        if 'error' in progress:
            raise HTTPException(status_code=404, detail=progress['error'])

        return progress

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.get("/export")
async def export_calibration_data(
    min_quality_score: float = Query(0.7, ge=0.0, le=1.0),
    test_version: str = Query("v4", pattern="^(v3|v4)$")
):
    """
    Export clean data for IRT calibration.

    Filters by quality score and returns formatted data.
    """
    try:
        collector = get_data_collector()
        responses, blocks = collector.export_for_calibration(
            min_quality_score=min_quality_score,
            test_version=test_version
        )

        # Get unique blocks
        unique_blocks = {}
        for block in blocks:
            block_id = block.get('block_id')
            if block_id not in unique_blocks:
                unique_blocks[block_id] = block

        return {
            "test_version": test_version,
            "total_responses": len(responses),
            "unique_blocks": len(unique_blocks),
            "min_quality_score": min_quality_score,
            "export_timestamp": datetime.utcnow().isoformat(),
            "data": {
                "responses": responses,
                "blocks": list(unique_blocks.values())
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")


@router.get("/recruitment/status")
async def get_recruitment_status():
    """
    Get recruitment status for pilot testing.

    Shows progress toward target sample size.
    """
    try:
        collector = get_data_collector()
        stats = collector.get_collection_stats()

        return {
            "target_sample_size": stats['target_sample_size'],
            "current_participants": stats['total_participants'],
            "completion_rate": f"{stats['completion_rate']:.1f}%",
            "participants_needed": max(0, stats['target_sample_size'] - stats['total_participants']),
            "by_group": stats['participants_by_group'],
            "recruitment_status": "complete" if stats['completion_rate'] >= 100 else "active"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recruitment status: {str(e)}")


@router.post("/quality/validate/{session_id}")
async def validate_session_quality(session_id: str):
    """
    Validate quality of a specific session.

    Returns quality flags and recommendations.
    """
    try:
        collector = get_data_collector()

        # Get session data
        with collector.db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT responses, completion_time_seconds, quality_flags
                FROM v4_test_sessions
                WHERE session_id = ?
            """, (session_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Session not found")

            responses = json.loads(result[0]) if result[0] else []
            completion_time = result[1] if result[1] else 0
            existing_flags = json.loads(result[2]) if result[2] else {}

        # Re-validate if needed
        if not existing_flags:
            quality_flags = collector._validate_responses(responses, completion_time)

            # Update database
            with collector.db_manager.get_connection() as conn:
                conn.execute("""
                    UPDATE v4_test_sessions
                    SET quality_flags = ?
                    WHERE session_id = ?
                """, (json.dumps(quality_flags), session_id))
                conn.commit()
        else:
            quality_flags = existing_flags

        # Generate recommendations
        recommendations = []
        if quality_flags.get('too_fast'):
            recommendations.append("Consider excluding: Completed too quickly")
        if quality_flags.get('straight_lining'):
            recommendations.append("Warning: Detected straight-lining pattern")
        if quality_flags.get('quality_score', 1.0) < 0.7:
            recommendations.append("Low quality: Consider exclusion from calibration")

        return {
            "session_id": session_id,
            "quality_flags": quality_flags,
            "quality_score": quality_flags.get('quality_score', 1.0),
            "recommendations": recommendations,
            "include_in_calibration": quality_flags.get('quality_score', 1.0) >= 0.7
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")