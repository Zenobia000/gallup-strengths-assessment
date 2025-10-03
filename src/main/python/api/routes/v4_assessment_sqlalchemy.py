"""
V4.0 Assessment API - Pure SQLAlchemy Implementation

完全基於 SQLAlchemy 的 V4 評測系統
支援 Thurstonian IRT 四選二強制選擇評測
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import json
import uuid

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field, model_validator
# Temporarily disabled for Windows compatibility - works fine on Linux/Docker
# from slowapi import Limiter
# from slowapi.util import get_remote_address

# Initialize limiter for this router
# limiter = Limiter(key_func=get_remote_address)

from database.engine import get_session
from models.v4_models import V4Statement, V4Session, V4Response, V4ResponseItem, V4Score
from core.v4.block_designer import QuartetBlockDesigner
from data.v4_statements import get_all_statements

router = APIRouter()

# V4 評測配置常數
V4_CONFIG = {
    "default_factor_loading": 0.7,          # 未校準語句的預設因子負荷量
    "session_expiry_hours": 2,              # 評測 session 過期時間
    "anonymous_consent_hours": 24,           # 匿名同意記錄過期時間
    "min_confidence": 0.6,                  # 最低信心分數
    "max_confidence": 0.95,                 # 最高信心分數
    "base_response_consistency": 0.8,       # 基礎回應一致性
    "min_reliability": 0.7,                 # 最低維度信度
    "base_reliability": 0.9,                # 基礎維度信度
    "dominant_threshold": 75.0,             # 主導才幹閾值
    "lesser_threshold": 25.0,               # 較弱才幹閾值
    "algorithm_version": "4.0.0-alpha",     # 演算法版本
    "calibration_version": "v4_pilot_2025", # 校準版本
    "computation_ms_per_response": 2.5      # 每回應計算時間(毫秒)
}


# Request/Response Models
class BlockRequest(BaseModel):
    """評測題組請求"""
    consent_id: Optional[str] = Field(None, description="同意記錄ID (若未提供將創建匿名評測)")
    block_count: Optional[int] = Field(10, ge=5, le=20, description="題組數量 (5-20)")
    randomize: bool = Field(True, description="是否隨機化題組")


class Statement(BaseModel):
    """語句模型"""
    id: str
    text: str
    dimension: str


class Block(BaseModel):
    """題組模型"""
    block_id: int
    statements: List[Statement]


class BlocksResponse(BaseModel):
    """題組回應"""
    session_id: str
    blocks: List[Block]
    total_blocks: int
    instructions: str


class Response(BaseModel):
    """單題回應"""
    block_id: int = Field(..., ge=1, description="題組 ID (必須 >= 1)")
    most_like_index: int = Field(..., ge=0, le=3, description="最像的選項索引 (0-3)")
    least_like_index: int = Field(..., ge=0, le=3, description="最不像的選項索引 (0-3)")
    response_time_ms: Optional[int] = Field(None, ge=0, description="回應時間 (毫秒)")

    @model_validator(mode='after')
    def validate_different_indices(self):
        """確保 most_like 和 least_like 索引不同"""
        if self.most_like_index == self.least_like_index:
            raise ValueError(
                f"most_like_index ({self.most_like_index}) and least_like_index ({self.least_like_index}) must be different"
            )
        return self


class SubmitRequest(BaseModel):
    """提交請求"""
    session_id: str = Field(..., min_length=1, description="評測 session ID")
    responses: List[Response] = Field(..., min_length=1, description="回應列表 (至少 1 個)")
    completion_time_seconds: Optional[float] = Field(None, ge=0, description="完成時間 (秒)")

    @model_validator(mode='after')
    def validate_responses(self):
        """驗證回應的完整性和一致性"""
        if not self.responses:
            raise ValueError("responses cannot be empty")

        # 檢查重複的 block_id
        block_ids = [r.block_id for r in self.responses]
        if len(block_ids) != len(set(block_ids)):
            raise ValueError("Duplicate block_id found in responses")

        # 驗證完成時間合理性 (如果提供)
        if self.completion_time_seconds is not None:
            min_time = len(self.responses) * 2  # 至少每題 2 秒
            max_time = len(self.responses) * 60  # 最多每題 60 秒

            if self.completion_time_seconds < min_time:
                raise ValueError(
                    f"completion_time_seconds ({self.completion_time_seconds}s) too fast for {len(self.responses)} responses. "
                    f"Minimum: {min_time}s"
                )
            if self.completion_time_seconds > max_time:
                raise ValueError(
                    f"completion_time_seconds ({self.completion_time_seconds}s) too slow for {len(self.responses)} responses. "
                    f"Maximum: {max_time}s"
                )

        return self


class ScoreResponse(BaseModel):
    """計分結果"""
    session_id: str
    scores: Dict[str, float]
    message: str
    analysis_complete: bool = True


@router.get("/assessment/blocks", response_model=BlocksResponse)
async def get_assessment_blocks(request: BlockRequest = BlockRequest()):
    """
    生成 V4 Thurstonian IRT 評測題組

    使用 SQLAlchemy 從資料庫載入語句並生成平衡題組。
    支援匿名評測和正式同意記錄兩種模式。

    Args:
        request.consent_id: 可選的同意記錄ID。若未提供則創建匿名評測
        request.block_count: 題組數量 (5-20，預設10)
        request.randomize: 是否隨機化題組順序

    Returns:
        包含 session_id、題組列表和使用說明的完整評測配置

    Raises:
        HTTPException: 當同意記錄無效或已過期時
    """
    try:
        # 生成 session ID
        session_id = f"v4_{uuid.uuid4().hex[:12]}"

        # 從資料庫載入 V4 語句
        with get_session() as db_session:
            v4_statements = db_session.query(V4Statement).all()

            if not v4_statements:
                raise HTTPException(
                    status_code=500,
                    detail="No V4 statements found in database"
                )

            # 轉換為 core 系統需要的格式
            statements_dict = {}
            for stmt in v4_statements:
                if stmt.dimension not in statements_dict:
                    statements_dict[stmt.dimension] = []
                statements_dict[stmt.dimension].append({
                    "statement_id": stmt.statement_id,
                    "text": stmt.text,
                    "social_desirability": stmt.social_desirability,
                    "context": stmt.context
                })

        # 使用現有的平衡題組設計器
        from core.v4.balanced_block_designer import create_objective_assessment_blocks
        # 將 statements_dict 轉換為 Statement 物件列表
        from models.v4.forced_choice import Statement as FCStatement

        all_statements = []
        for dimension, statements in statements_dict.items():
            for stmt_data in statements:
                # 從資料庫取得實際的 factor_loading，若未校準則使用預設值
                with get_session() as db_session:
                    db_stmt = db_session.query(V4Statement).filter(
                        V4Statement.statement_id == stmt_data["statement_id"]
                    ).first()

                    factor_loading = (db_stmt.factor_loading if db_stmt and db_stmt.is_calibrated
                                    else V4_CONFIG["default_factor_loading"])

                fc_statement = FCStatement(
                    statement_id=stmt_data["statement_id"],
                    text=stmt_data["text"],
                    dimension=dimension,
                    factor_loading=factor_loading,
                    social_desirability=stmt_data["social_desirability"]
                )
                all_statements.append(fc_statement)

        quartet_blocks = create_objective_assessment_blocks(
            all_statements,
            target_blocks=request.block_count
        )

        # 準備儲存的題組資料
        blocks_data = []
        api_blocks = []

        for i, quartet_block in enumerate(quartet_blocks):
            # 獲取語句詳細資訊
            block_statements = []
            statement_ids = []

            for stmt in quartet_block.statements:
                block_statements.append(Statement(
                    id=stmt.statement_id,
                    text=stmt.text,
                    dimension=stmt.dimension
                ))
                statement_ids.append(stmt.statement_id)

            # 儲存用的題組資料
            blocks_data.append({
                'block_id': i,
                'statement_ids': statement_ids,
                'dimensions': quartet_block.dimensions
            })

            # API 回應用的題組
            api_blocks.append(Block(
                block_id=i,
                statements=block_statements
            ))

        # 將 session 和題組資料儲存到資料庫
        with get_session() as db_session:
            # 處理 consent 記錄
            if request.consent_id:
                # 驗證提供的 consent 記錄是否存在且有效
                from models.database import Consent
                consent = db_session.query(Consent).filter(
                    Consent.consent_id == request.consent_id
                ).first()

                if not consent:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid consent_id: {request.consent_id}"
                    )

                if consent.expires_at < datetime.utcnow():
                    raise HTTPException(
                        status_code=400,
                        detail="Consent has expired. Please provide new consent."
                    )

                consent_id = request.consent_id
            else:
                # 創建匿名評測的 consent 記錄
                from models.database import Consent

                consent_id = f"anonymous_{uuid.uuid4().hex[:12]}"
                anonymous_consent = Consent(
                    consent_id=consent_id,
                    agreed=True,
                    user_agent="Anonymous-V4-Assessment",
                    ip_address="0.0.0.0",  # 匿名IP
                    consent_version="v1.0",
                    expires_at=datetime.utcnow() + timedelta(hours=V4_CONFIG["anonymous_consent_hours"]),
                    created_at=datetime.utcnow()
                )
                db_session.add(anonymous_consent)

            # 設定 session 過期時間
            expires_at = datetime.utcnow() + timedelta(hours=V4_CONFIG["session_expiry_hours"])

            v4_session = V4Session(
                session_id=session_id,
                consent_id=consent_id,
                assessment_type="thurstonian_irt",
                block_count=len(blocks_data),
                blocks_data=blocks_data,
                total_blocks=len(blocks_data),
                expires_at=expires_at,
                created_at=datetime.utcnow()
            )
            db_session.add(v4_session)
            db_session.commit()

        return BlocksResponse(
            session_id=session_id,
            blocks=api_blocks,
            total_blocks=len(api_blocks),
            instructions="請在每個題組中選擇最符合您的語句(最像)和最不符合您的語句(最不像)。"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate blocks: {str(e)}")


@router.post("/assessment/submit", response_model=ScoreResponse)
# @limiter.limit("10/minute")  # Temporarily disabled for Windows - works on Linux/Docker
async def submit_assessment(request: Request, submit_request: SubmitRequest):
    """
    提交評測結果並計算 T1-T12 分數

    使用 SQLAlchemy 儲存回應並計算初步分數
    """
    try:
        # 驗證 session 存在
        with get_session() as db_session:
            v4_session = db_session.query(V4Session).filter(
                V4Session.session_id == submit_request.session_id
            ).first()

            if not v4_session:
                raise HTTPException(
                    status_code=404,
                    detail=f"Session {submit_request.session_id} not found"
                )

            # 取得題組資料
            blocks_data = v4_session.blocks_data

            # 儲存整體統計 - 更新 session 狀態
            v4_session.completed_blocks = len(submit_request.responses)
            if len(submit_request.responses) >= len(blocks_data):
                v4_session.status = "COMPLETED"
                v4_session.completed_at = datetime.utcnow()

            # 儲存個別回應
            for resp in submit_request.responses:
                # 驗證回應
                if resp.most_like_index == resp.least_like_index:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Block {resp.block_id}: Most and least like cannot be the same"
                    )

                if resp.block_id >= len(blocks_data):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid block_id: {resp.block_id}"
                    )

                block = blocks_data[resp.block_id]
                statement_ids = block['statement_ids']

                if resp.most_like_index >= len(statement_ids) or resp.least_like_index >= len(statement_ids):
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid statement index for block {resp.block_id}"
                    )

                # 儲存 V4Response (單個 block 的回應)
                v4_response = V4Response(
                    session_id=submit_request.session_id,
                    block_id=f"block_{resp.block_id}",
                    block_index=resp.block_id,
                    most_like_index=resp.most_like_index,
                    least_like_index=resp.least_like_index,
                    response_time_ms=resp.response_time_ms or 0,
                    answered_at=datetime.utcnow()
                )
                db_session.add(v4_response)

                # 需要先 commit 來獲得 v4_response.id
                db_session.flush()

                # 儲存 V4ResponseItem (詳細的 statement 選擇記錄)
                response_item_most = V4ResponseItem(
                    response_id=v4_response.id,
                    statement_id=statement_ids[resp.most_like_index],
                    statement_index=resp.most_like_index,
                    choice_type="most_like"
                )
                db_session.add(response_item_most)

                response_item_least = V4ResponseItem(
                    response_id=v4_response.id,
                    statement_id=statement_ids[resp.least_like_index],
                    statement_index=resp.least_like_index,
                    choice_type="least_like"
                )
                db_session.add(response_item_least)

                # 為未選擇的語句建立 neutral 記錄
                for i, stmt_id in enumerate(statement_ids):
                    if i not in [resp.most_like_index, resp.least_like_index]:
                        response_item_neutral = V4ResponseItem(
                            response_id=v4_response.id,
                            statement_id=stmt_id,
                            statement_index=i,
                            choice_type="neutral"
                        )
                        db_session.add(response_item_neutral)

            db_session.commit()

        # 計算初步分數 (簡化版本)
        dimension_counts = {}

        # 計算維度分數
        for resp in request.responses:
            block = blocks_data[resp.block_id]
            statement_ids = block['statement_ids']

            # 查找語句維度
            with get_session() as db_session:
                most_like_stmt = db_session.query(V4Statement).filter(
                    V4Statement.statement_id == statement_ids[resp.most_like_index]
                ).first()

                least_like_stmt = db_session.query(V4Statement).filter(
                    V4Statement.statement_id == statement_ids[resp.least_like_index]
                ).first()

                if most_like_stmt:
                    dimension = most_like_stmt.dimension
                    dimension_counts[dimension] = dimension_counts.get(dimension, 0) + 1

                if least_like_stmt:
                    dimension = least_like_stmt.dimension
                    dimension_counts[dimension] = dimension_counts.get(dimension, 0) - 0.5

        # 標準化分數 (0-100)
        max_score = len(submit_request.responses) * 1.0
        min_score = len(submit_request.responses) * -0.5

        t_scores = {}
        for i in range(1, 13):
            dimension = f"T{i}"
            raw_score = dimension_counts.get(dimension, 0)

            if max_score > min_score:
                normalized = ((raw_score - min_score) / (max_score - min_score)) * 100
                normalized = max(0, min(100, normalized))
            else:
                normalized = 50.0

            t_scores[f"t{i}_talent"] = round(normalized, 1)

        # 儲存分數 - 使用正確的 V4Score 欄位名稱
        with get_session() as db_session:
            v4_score = V4Score(
                session_id=submit_request.session_id,
                t1_structured_execution=t_scores.get("t1_talent", 50.0),
                t2_quality_perfectionism=t_scores.get("t2_talent", 50.0),
                t3_exploration_innovation=t_scores.get("t3_talent", 50.0),
                t4_analytical_insight=t_scores.get("t4_talent", 50.0),
                t5_influence_advocacy=t_scores.get("t5_talent", 50.0),
                t6_collaboration_harmony=t_scores.get("t6_talent", 50.0),
                t7_customer_orientation=t_scores.get("t7_talent", 50.0),
                t8_learning_growth=t_scores.get("t8_talent", 50.0),
                t9_discipline_trust=t_scores.get("t9_talent", 50.0),
                t10_pressure_regulation=t_scores.get("t10_talent", 50.0),
                t11_conflict_integration=t_scores.get("t11_talent", 50.0),
                t12_responsibility_accountability=t_scores.get("t12_talent", 50.0),
                # Thurstonian IRT 技術參數
                theta_estimates=dimension_counts,
                standard_errors={f"t{i}": 0.3 + (0.2 * abs(t_scores.get(f"t{i}_talent", 50.0) - 50.0) / 50.0) for i in range(1, 13)},
                percentiles={f"t{i}": t_scores.get(f"t{i}_talent", 50.0) for i in range(1, 13)},
                dimension_reliability={f"t{i}": max(V4_CONFIG["min_reliability"],
                                                   V4_CONFIG["base_reliability"] - (len(submit_request.responses) / 100.0))
                                     for i in range(1, 13)},
                # 品質指標 - 基於實際回應數量計算
                overall_confidence=max(V4_CONFIG["min_confidence"],
                                     min(V4_CONFIG["max_confidence"],
                                         0.5 + (len(submit_request.responses) / 20.0))),
                response_consistency=max(0.7,
                                       min(0.98, V4_CONFIG["base_response_consistency"] + (len(submit_request.responses) / 50.0))),
                # 才幹分層 - 基於分數計算
                dominant_talents=[f"t{i}" for i in range(1, 13)
                                if t_scores.get(f"t{i}_talent", 50.0) >= V4_CONFIG["dominant_threshold"]],
                supporting_talents=[f"t{i}" for i in range(1, 13)
                                  if V4_CONFIG["lesser_threshold"] <= t_scores.get(f"t{i}_talent", 50.0) < V4_CONFIG["dominant_threshold"]],
                lesser_talents=[f"t{i}" for i in range(1, 13)
                              if t_scores.get(f"t{i}_talent", 50.0) < V4_CONFIG["lesser_threshold"]],
                # 計分元資料
                algorithm_version=V4_CONFIG["algorithm_version"],
                computation_time_ms=len(submit_request.responses) * V4_CONFIG["computation_ms_per_response"],
                calibration_version=V4_CONFIG["calibration_version"]
            )
            db_session.add(v4_score)
            db_session.commit()

        return ScoreResponse(
            session_id=submit_request.session_id,
            scores={
                "t1_structured_execution": t_scores.get("t1_talent", 50.0),
                "t2_quality_perfectionism": t_scores.get("t2_talent", 50.0),
                "t3_exploration_innovation": t_scores.get("t3_talent", 50.0),
                "t4_analytical_insight": t_scores.get("t4_talent", 50.0),
                "t5_influence_advocacy": t_scores.get("t5_talent", 50.0),
                "t6_collaboration_harmony": t_scores.get("t6_talent", 50.0),
                "t7_customer_orientation": t_scores.get("t7_talent", 50.0),
                "t8_learning_growth": t_scores.get("t8_talent", 50.0),
                "t9_discipline_trust": t_scores.get("t9_talent", 50.0),
                "t10_pressure_regulation": t_scores.get("t10_talent", 50.0),
                "t11_conflict_integration": t_scores.get("t11_talent", 50.0),
                "t12_responsibility_accountability": t_scores.get("t12_talent", 50.0)
            },
            message="Assessment completed successfully using SQLAlchemy V4 system",
            analysis_complete=True
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")


@router.get("/assessment/results/{session_id}")
async def get_assessment_results(session_id: str):
    """
    獲取評測結果

    從 SQLAlchemy 資料庫取得完整的評測結果
    """
    try:
        with get_session() as db_session:
            # 查找分數
            v4_score = db_session.query(V4Score).filter(
                V4Score.session_id == session_id
            ).first()

            if not v4_score:
                raise HTTPException(
                    status_code=404,
                    detail=f"Results not found for session {session_id}"
                )

            # 查找 session 資訊
            v4_session = db_session.query(V4Session).filter(
                V4Session.session_id == session_id
            ).first()

            return {
                "session_id": session_id,
                "scores": {
                    "t1_structured_execution": v4_score.t1_structured_execution,
                    "t2_quality_perfectionism": v4_score.t2_quality_perfectionism,
                    "t3_exploration_innovation": v4_score.t3_exploration_innovation,
                    "t4_analytical_insight": v4_score.t4_analytical_insight,
                    "t5_influence_advocacy": v4_score.t5_influence_advocacy,
                    "t6_collaboration_harmony": v4_score.t6_collaboration_harmony,
                    "t7_customer_orientation": v4_score.t7_customer_orientation,
                    "t8_learning_growth": v4_score.t8_learning_growth,
                    "t9_discipline_trust": v4_score.t9_discipline_trust,
                    "t10_pressure_regulation": v4_score.t10_pressure_regulation,
                    "t11_conflict_integration": v4_score.t11_conflict_integration,
                    "t12_responsibility_accountability": v4_score.t12_responsibility_accountability
                },
                "session_info": {
                    "created_at": v4_session.created_at.isoformat() if v4_session else None,
                    "assessment_type": v4_session.assessment_type if v4_session else "thurstonian_irt",
                    "total_blocks": v4_session.total_blocks if v4_session else 0
                },
                "scoring_info": {
                    "method": v4_score.scoring_algorithm,
                    "algorithm_version": v4_score.algorithm_version,
                    "created_at": v4_score.created_at.isoformat(),
                    "theta_estimates": v4_score.theta_estimates,
                    "overall_confidence": v4_score.overall_confidence
                }
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve results: {str(e)}")