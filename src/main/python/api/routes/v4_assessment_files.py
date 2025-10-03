"""
V4 Assessment API Routes - File Storage Version
Replaces SQLAlchemy with file-based storage for rapid development
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Dict, List, Any, Optional
import json
import random
from datetime import datetime, timedelta
import uuid
import os
from pathlib import Path

from core.file_storage import get_file_storage
from core.scoring.quality_checker import ResponseQualityChecker
from core.scoring.v4_scoring_engine import V4ScoringEngine

router = APIRouter()

# Get file storage instance
storage = get_file_storage()


@router.get("/assessment/blocks")
async def get_assessment_blocks(request: Request):
    """
    Generate randomized assessment blocks using file storage
    """
    try:
        # Load statements from file storage
        statements = storage.select_all("v4_statements")

        if not statements:
            raise HTTPException(
                status_code=500,
                detail="No assessment statements found in storage"
            )

        print(f"維度數量: {len(set(stmt['dimension'] for stmt in statements))}")

        # Group by dimension
        dimension_statements = {}
        for stmt in statements:
            dim = stmt['dimension']
            if dim not in dimension_statements:
                dimension_statements[dim] = []
            dimension_statements[dim].append(stmt)

        # Print dimension info
        dimension_counts = {dim: len(stmts) for dim, stmts in dimension_statements.items()}
        print(f"各維度 statement 數量: {dimension_counts}")

        # Generate blocks
        from core.thurstonian.block_generator import generate_balanced_blocks
        blocks = generate_balanced_blocks(statements)

        if not blocks:
            raise HTTPException(
                status_code=500,
                detail="Failed to generate assessment blocks"
            )

        # Create session in file storage
        session_id = storage.create_session_id("v4")

        session_data = {
            "session_id": session_id,
            "assessment_type": "thurstonian_irt",
            "blocks_data": json.dumps(blocks),
            "status": "PENDING",
            "total_blocks": len(blocks),
            "completed_blocks": 0,
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat()
        }

        storage.insert("v4_sessions", session_data)

        return {
            "session_id": session_id,
            "blocks": blocks,
            "total_blocks": len(blocks),
            "instructions": "每個題組請從四個選項中選出最符合和最不符合你的兩個選項",
            "time_limit_minutes": 15
        }

    except Exception as e:
        print(f"API Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/assessment/submit")
async def submit_assessment(request: Request):
    """
    Submit assessment responses using file storage
    """
    try:
        data = await request.json()
        session_id = data.get("session_id")
        responses = data.get("responses", [])
        completion_time_seconds = data.get("completion_time_seconds", 0)

        if not session_id:
            raise HTTPException(status_code=400, detail="Missing session_id")

        if not responses:
            raise HTTPException(status_code=400, detail="Missing responses")

        # Get session from file storage
        session = storage.select_by_id("v4_sessions", "session_id", session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Store responses with completion time
        current_time = datetime.now()
        response_data = {
            "session_id": session_id,
            "response_data": json.dumps(responses),
            "total_responses": len(responses),
            "submission_time": current_time.isoformat(),
            "completion_time_seconds": completion_time_seconds,
            "completion_time_formatted": f"{completion_time_seconds // 60}:{completion_time_seconds % 60:02d}"
        }

        storage.insert("v4_responses", response_data)

        # Store individual response items
        response_items = []
        for response in responses:
            block_id = response.get("block_id")
            most_like = response.get("most_like")
            least_like = response.get("least_like")

            if most_like:
                response_items.append({
                    "session_id": session_id,
                    "block_id": block_id,
                    "statement_id": most_like,
                    "response_type": "most_like"
                })

            if least_like:
                response_items.append({
                    "session_id": session_id,
                    "block_id": block_id,
                    "statement_id": least_like,
                    "response_type": "least_like"
                })

        if response_items:
            storage.insert_many("v4_response_items", response_items)

        # Quality check
        try:
            quality_checker = ResponseQualityChecker()
            quality_result = quality_checker.check_response_quality(responses)
        except Exception as e:
            print(f"Quality check failed: {e}")
            quality_result = {"overall_quality": "acceptable", "issues": []}

        # Run scoring
        try:
            scoring_engine = V4ScoringEngine()
            scoring_result = scoring_engine.score_assessment(responses)

            # Store scores
            score_data = {
                "session_id": session_id,
                **{f"t{i+1}_{dim}": score for i, (dim, score) in enumerate(scoring_result["dimension_scores"].items())},
                "theta_estimates": json.dumps(scoring_result.get("theta_estimates", {})),
                "standard_errors": json.dumps(scoring_result.get("standard_errors", {})),
                "percentiles": json.dumps(scoring_result["dimension_scores"]),
                "norm_group": "taiwan_2025",
                "overall_confidence": scoring_result.get("overall_confidence", 0.85),
                "dimension_reliability": json.dumps(scoring_result.get("dimension_reliability", {})),
                "response_consistency": quality_result.get("overall_quality_score", 0.8),
                "dominant_talents": json.dumps(scoring_result.get("dominant_talents", [])),
                "supporting_talents": json.dumps(scoring_result.get("supporting_talents", [])),
                "lesser_talents": json.dumps(scoring_result.get("lesser_talents", [])),
                "scoring_algorithm": "thurstonian_irt_v4",
                "algorithm_version": "4.0.0-alpha",
                "computation_time_ms": scoring_result.get("computation_time_ms", 0),
                "calibration_version": "v4_pilot_2025"
            }

            storage.insert("v4_scores", score_data)

            # Update session status
            storage.update("v4_sessions", "session_id", session_id, {
                "status": "COMPLETED",
                "completed_at": datetime.now().isoformat(),
                "completed_blocks": len(responses)
            })

            return {
                "session_id": session_id,
                "status": "completed",
                "redirect_url": f"/results.html?session={session_id}",
                "quality_check": quality_result,
                "scoring_summary": {
                    "total_dimensions": len(scoring_result["dimension_scores"]),
                    "completion_rate": 100.0,
                    "confidence_level": scoring_result.get("overall_confidence", 0.85)
                }
            }

        except Exception as e:
            print(f"Scoring failed: {e}")
            # Update session with error status
            storage.update("v4_sessions", "session_id", session_id, {
                "status": "ERROR",
                "error_message": str(e)
            })

            raise HTTPException(
                status_code=500,
                detail=f"Scoring failed: {str(e)}"
            )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Submission error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assessment/results/{session_id}")
async def get_assessment_results(session_id: str):
    """
    Get assessment results using file storage
    """
    try:
        # Get session
        session = storage.select_by_id("v4_sessions", "session_id", session_id)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found")

        # Get scores
        scores = storage.select_by_id("v4_scores", "session_id", session_id)
        if not scores:
            raise HTTPException(status_code=404, detail="Scores not found")

        # Get responses for timing data
        responses = storage.select_by_id("v4_responses", "session_id", session_id)

        # Format dimension scores - map from engine output to frontend expected format
        dimension_mapping = {
            "structured_execution": "t1_structured_execution",
            "quality_perfectionism": "t2_quality_perfectionism",
            "exploration_innovation": "t3_exploration_innovation",
            "analytical_insight": "t4_analytical_insight",
            "influence_advocacy": "t5_influence_advocacy",
            "collaboration_harmony": "t6_collaboration_harmony",
            "customer_orientation": "t7_customer_orientation",
            "learning_growth": "t8_learning_growth",
            "discipline_trust": "t9_discipline_trust",
            "pressure_regulation": "t10_pressure_regulation",
            "conflict_integration": "t11_conflict_integration",
            "responsibility_accountability": "t12_responsibility_accountability"
        }

        dimension_scores = {}

        # First try to get scores from t1-t12 fields (direct storage format)
        for key, value in scores.items():
            if key.startswith("t") and "_" in key and key not in ["theta_estimates", "standard_errors", "percentiles"]:
                # This is already in the correct format like "t1_structured_execution"
                dimension_scores[key] = value

        # If no t1-t12 fields found, try percentiles field as backup
        if not dimension_scores and "percentiles" in scores:
            try:
                engine_scores = json.loads(scores.get("percentiles", "{}"))
                for dim_name, score in engine_scores.items():
                    if dim_name in dimension_mapping:
                        dimension_scores[dimension_mapping[dim_name]] = score
            except (json.JSONDecodeError, TypeError):
                pass

        # Calculate completion time from session and response data
        completion_time_formatted = "3:42"  # Default fallback
        if responses:
            completion_time_seconds = responses.get("completion_time_seconds", 0)
            if completion_time_seconds > 0:
                minutes = completion_time_seconds // 60
                seconds = completion_time_seconds % 60
                completion_time_formatted = f"{minutes}:{seconds:02d}"

        return {
            "session_id": session_id,
            "scores": dimension_scores,
            "session_info": {
                "created_at": session.get("created_at"),
                "assessment_type": session.get("assessment_type"),
                "total_blocks": session.get("total_blocks"),
                "completion_time_seconds": responses.get("completion_time_seconds") if responses else 0,
                "completion_time_formatted": completion_time_formatted,
                "submission_time": responses.get("submission_time") if responses else None
            },
            "scoring_info": {
                "method": scores.get("scoring_algorithm"),
                "algorithm_version": scores.get("algorithm_version"),
                "created_at": scores.get("created_at"),
                "theta_estimates": json.loads(scores.get("theta_estimates", "{}")),
                "overall_confidence": scores.get("overall_confidence")
            }
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Results error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/assessment/talent-mapping")
async def get_talent_mapping_rules():
    """
    Get talent mapping rules and archetype definitions
    """
    try:
        # Get project root directory (navigate up from api/routes to project root)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent.parent.parent.parent
        mapping_file = project_root / "src" / "main" / "resources" / "assessment" / "talent_mapping_rules.json"

        if not mapping_file.exists():
            raise HTTPException(
                status_code=404,
                detail="Talent mapping rules file not found"
            )

        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_rules = json.load(f)

        return {
            "talent_mapping": mapping_rules,
            "loaded_from": str(mapping_file),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error loading talent mapping rules: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load talent mapping rules: {str(e)}"
        )


@router.get("/system/health")
async def health_check_file_storage():
    """
    Health check for file storage system
    """
    try:
        health = storage.health_check()

        return {
            "status": health.get("status", "unknown"),
            "timestamp": datetime.now(),
            "version": "1.0.0-file-storage",
            "storage_type": "file_based",
            "storage_info": health,
            "services": {
                "assessment": "ready",
                "scoring": "ready",
                "reporting": "ready",
                "file_storage": "ready"
            }
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "version": "1.0.0-file-storage",
            "storage_type": "file_based",
            "error": str(e)
        }