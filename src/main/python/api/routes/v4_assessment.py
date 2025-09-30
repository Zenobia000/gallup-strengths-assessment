"""
V4.0 Assessment API Routes - Thurstonian IRT Implementation

Implements forced-choice assessment endpoints for the v4.0 system.
Uses quartet blocks with four-choose-two response format.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import uuid

from fastapi import APIRouter, HTTPException, Request, Depends
from pydantic import BaseModel, Field

from core.v4.block_designer import QuartetBlockDesigner
from core.v4.irt_scorer import ThurstonianIRTScorer
from core.v4.normative_scoring import NormativeScorer
from core.v4.irt_calibration import ThurstonianIRTCalibrator
from data.v4_statements import STATEMENT_POOL, DIMENSION_MAPPING
from utils.database import get_database_manager
from pathlib import Path


router = APIRouter(prefix="/api/v4")


# Request/Response Models
class BlockRequest(BaseModel):
    """Request for assessment blocks"""
    session_id: Optional[str] = Field(None, description="Session ID for tracking")
    block_count: Optional[int] = Field(15, description="Number of blocks to generate")


class Statement(BaseModel):
    """Individual statement in a block"""
    id: str
    text: str
    dimension: str


class AssessmentBlock(BaseModel):
    """Quartet block with four statements"""
    block_id: int
    statements: List[Statement]
    instructions: str = "選擇最符合與最不符合您的陳述"


class BlocksResponse(BaseModel):
    """Response containing assessment blocks"""
    session_id: str
    blocks: List[AssessmentBlock]
    total_blocks: int
    estimated_time_minutes: int


class ResponseItem(BaseModel):
    """Single response to a block"""
    block_id: int
    most_like_index: int = Field(..., ge=0, le=3)
    least_like_index: int = Field(..., ge=0, le=3)
    response_time_ms: Optional[int] = None


class SubmitRequest(BaseModel):
    """Submit assessment responses"""
    session_id: str
    responses: List[ResponseItem]
    completion_time_seconds: Optional[int] = None


class DimensionScore(BaseModel):
    """Score for a single dimension"""
    dimension: str
    theta_score: float
    percentile: float
    t_score: float
    stanine: int
    interpretation: str


class ScoreResponse(BaseModel):
    """Complete scoring results"""
    session_id: str
    timestamp: datetime
    dimension_scores: List[DimensionScore]
    top_strengths: List[Dict[str, Any]]
    development_areas: List[Dict[str, Any]]
    profile_type: str
    fit_statistics: Dict[str, float]


# Initialize components
block_designer = None  # Initialize on first use
irt_scorer = None  # Initialize on first use
norm_scorer = NormativeScorer(Path('data/v4_normative_data.json'))


def get_irt_scorer():
    """Lazy initialization of IRT scorer"""
    global irt_scorer
    if irt_scorer is None:
        # Load calibrated parameters if available
        param_file = Path('models/v4_parameters.json')
        if param_file.exists():
            with open(param_file, 'r', encoding='utf-8') as f:
                params = json.load(f)
                irt_scorer = ThurstonianIRTScorer(
                    item_parameters=params['item_parameters'],
                    dimension_means=params.get('dimension_means'),
                    dimension_covariances=params.get('dimension_covariances')
                )
        else:
            # Use default parameters
            irt_scorer = ThurstonianIRTScorer()
    return irt_scorer


@router.get("/assessment/blocks", response_model=BlocksResponse)
async def get_assessment_blocks(request: BlockRequest = BlockRequest()):
    """
    Generate forced-choice assessment blocks.

    Returns quartet blocks with balanced dimension coverage.
    """
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())

        # Initialize block designer if needed
        global block_designer
        if block_designer is None:
            block_designer = QuartetBlockDesigner(STATEMENT_POOL)

        # Design blocks
        blocks_data = block_designer.design_blocks(
            num_blocks=request.block_count
        )

        # Format blocks for response
        blocks = []
        for i, block in enumerate(blocks_data):
            statements = []
            for stmt_id in block['statement_ids']:
                stmt = next(s for s in STATEMENT_POOL if s['id'] == stmt_id)
                statements.append(Statement(
                    id=stmt['id'],
                    text=stmt['text'],
                    dimension=stmt['dimension']
                ))

            blocks.append(AssessmentBlock(
                block_id=i,
                statements=statements
            ))

        # Store blocks in session for later scoring
        db_manager = get_database_manager()
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO v4_sessions (session_id, blocks_data, created_at)
                VALUES (?, ?, datetime('now'))
            """, (session_id, json.dumps(blocks_data)))
            conn.commit()

        return BlocksResponse(
            session_id=session_id,
            blocks=blocks,
            total_blocks=len(blocks),
            estimated_time_minutes=len(blocks) * 1  # ~1 minute per block
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate blocks: {str(e)}")


@router.post("/assessment/submit", response_model=ScoreResponse)
async def submit_assessment(request: SubmitRequest):
    """
    Submit assessment responses and calculate scores.

    Uses Thurstonian IRT scoring with normative conversion.
    """
    try:
        # Validate responses
        if not request.responses:
            raise ValueError("No responses provided")

        # Check for duplicate block IDs
        block_ids = [r.block_id for r in request.responses]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("Duplicate block responses detected")

        # Retrieve session blocks
        db_manager = get_database_manager()
        with db_manager.get_connection() as conn:
            cursor = conn.execute(
                "SELECT blocks_data FROM v4_sessions WHERE session_id = ?",
                (request.session_id,)
            )
            result = cursor.fetchone()
            if not result:
                raise ValueError(f"Session {request.session_id} not found")

            blocks_data = json.loads(result[0])

        # Format responses for scoring
        formatted_responses = []
        for resp in request.responses:
            if resp.most_like_index == resp.least_like_index:
                raise ValueError(f"Block {resp.block_id}: Cannot select same item as most and least")

            block = blocks_data[resp.block_id]
            formatted_responses.append({
                'block_id': resp.block_id,
                'statement_ids': block['statement_ids'],
                'most_like_index': resp.most_like_index,
                'least_like_index': resp.least_like_index,
                'response_time_ms': resp.response_time_ms
            })

        # Calculate IRT scores
        scorer = get_irt_scorer()
        theta_scores = scorer.score(formatted_responses, blocks_data)

        # Convert to normative scores
        norm_scores = norm_scorer.compute_norm_scores(theta_scores)

        # Get strength profile
        profile = norm_scorer.get_strength_profile(norm_scores)

        # Calculate fit statistics
        fit_stats = scorer.calculate_fit_statistics(formatted_responses, blocks_data, theta_scores)

        # Format dimension scores
        dimension_scores = []
        for dim, score in norm_scores.items():
            dimension_scores.append(DimensionScore(
                dimension=dim,
                theta_score=theta_scores[dim],
                percentile=score.percentile,
                t_score=score.t_score,
                stanine=score.stanine,
                interpretation=score.interpretation
            ))

        # Store results
        with db_manager.get_connection() as conn:
            conn.execute("""
                INSERT INTO v4_assessment_results
                (session_id, responses, theta_scores, norm_scores, profile, completed_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
            """, (
                request.session_id,
                json.dumps(formatted_responses),
                json.dumps(theta_scores),
                json.dumps({k: v.__dict__ for k, v in norm_scores.items()}),
                json.dumps(profile)
            ))
            conn.commit()

        return ScoreResponse(
            session_id=request.session_id,
            timestamp=datetime.utcnow(),
            dimension_scores=dimension_scores,
            top_strengths=profile['top_strengths'],
            development_areas=profile['development_areas'],
            profile_type=profile['profile_type'],
            fit_statistics=fit_stats
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scoring failed: {str(e)}")


@router.get("/assessment/results/{session_id}")
async def get_results(session_id: str):
    """
    Retrieve assessment results for a session.
    """
    try:
        db_manager = get_database_manager()
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT responses, theta_scores, norm_scores, profile, completed_at
                FROM v4_assessment_results
                WHERE session_id = ?
            """, (session_id,))
            result = cursor.fetchone()

            if not result:
                raise HTTPException(status_code=404, detail="Results not found")

            return {
                "session_id": session_id,
                "completed_at": result[4],
                "theta_scores": json.loads(result[1]),
                "norm_scores": json.loads(result[2]),
                "profile": json.loads(result[3])
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")


@router.post("/calibration/run")
async def run_calibration(sample_size: int = 1000, max_iterations: int = 50):
    """
    Run IRT calibration on collected response data.

    This endpoint is for system administrators only.
    """
    try:
        # Collect response data from database
        db_manager = get_database_manager()
        with db_manager.get_connection() as conn:
            cursor = conn.execute("""
                SELECT responses FROM v4_assessment_results
                ORDER BY completed_at DESC
                LIMIT ?
            """, (sample_size,))

            all_responses = []
            for row in cursor.fetchall():
                responses = json.loads(row[0])
                all_responses.extend(responses)

        if len(all_responses) < 100:
            raise ValueError("Insufficient data for calibration (minimum 100 responses)")

        # Run calibration
        calibrator = ThurstonianIRTCalibrator()

        # Get unique blocks
        blocks = {}
        for resp in all_responses:
            block_id = resp['block_id']
            if block_id not in blocks:
                blocks[block_id] = resp['statement_ids']

        # Calibrate parameters
        results = calibrator.calibrate(
            responses=all_responses,
            blocks=list(blocks.values()),
            max_iter=max_iterations
        )

        # Save calibrated parameters
        param_file = Path('models/v4_parameters.json')
        param_file.parent.mkdir(exist_ok=True)

        with open(param_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

        # Reinitialize scorer with new parameters
        global irt_scorer
        irt_scorer = None

        return {
            "status": "success",
            "samples_used": len(all_responses),
            "iterations": results['iterations'],
            "convergence": results['converged'],
            "final_likelihood": results['log_likelihood']
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Calibration failed: {str(e)}")


@router.get("/health")
async def health_check():
    """V4 system health check"""
    return {
        "status": "healthy",
        "version": "4.0.0",
        "model": "Thurstonian IRT",
        "components": {
            "block_designer": "ready",
            "irt_scorer": "ready" if irt_scorer else "not initialized",
            "norm_scorer": "ready",
            "calibration": "available"
        }
    }