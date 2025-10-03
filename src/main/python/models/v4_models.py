"""
V4.0 Thurstonian IRT SQLAlchemy Models

V4 專用資料模型，支援：
- 四選二強制選擇評測 (Quartet Blocks)
- T1-T12 才幹維度系統
- Thurstonian IRT 計分
- 動態職業原型分析

設計原則：Linus 好品味 + 心理測量學標準
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any, Optional

# 使用與主要模型相同的Base
from models.database import Base


class V4Statement(Base):
    """V4 Thurstonian IRT 語句庫 - T1-T12 才幹維度"""
    __tablename__ = "v4_statements"

    id = Column(Integer, primary_key=True, autoincrement=True)
    statement_id = Column(String(10), unique=True, index=True, nullable=False)  # T1001, T1002等
    dimension = Column(String(5), nullable=False, index=True)  # T1-T12
    text = Column(Text, nullable=False)
    social_desirability = Column(Float, nullable=False)  # 1.0-7.0
    context = Column(String(20), nullable=False)  # work, team, general
    factor_loading = Column(Float, default=0.7, nullable=False)  # IRT參數

    # 校準參數 (待IRT校準更新)
    discrimination = Column(Float, default=1.0)  # a參數
    difficulty = Column(Float, default=0.0)      # d參數
    is_calibrated = Column(Boolean, default=False, nullable=False)
    calibration_version = Column(String(20), default="initial")

    # 時間戳記
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    response_items = relationship("V4ResponseItem", back_populates="statement")

    def __repr__(self):
        return f"<V4Statement(statement_id={self.statement_id}, dimension={self.dimension})>"


class V4Session(Base):
    """V4 評測會話 - 四選二強制選擇"""
    __tablename__ = "v4_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)
    consent_id = Column(String(36), ForeignKey("consents.consent_id"), nullable=False)

    # V4專用設定
    assessment_type = Column(String(20), default="thurstonian_irt", nullable=False)
    block_count = Column(Integer, nullable=False)  # 通常為9-15個blocks
    blocks_data = Column(JSON, nullable=False)  # 完整blocks配置

    # 會話狀態
    status = Column(String(20), default="PENDING", nullable=False)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=False)

    # 進度追蹤
    total_blocks = Column(Integer, nullable=False)
    completed_blocks = Column(Integer, default=0, nullable=False)

    # 元資料
    session_metadata = Column(JSON)  # 額外會話資料
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    consent = relationship("Consent", back_populates="v4_sessions")
    responses = relationship("V4Response", back_populates="session", cascade="all, delete-orphan")
    scores = relationship("V4Score", back_populates="session", uselist=False)
    archetype_result = relationship("V4ArchetypeResult", back_populates="session", uselist=False)

    def __repr__(self):
        return f"<V4Session(session_id={self.session_id}, status={self.status})>"

    @property
    def is_completed(self) -> bool:
        return self.status == "COMPLETED" and self.completed_blocks >= self.total_blocks

    @property
    def is_expired(self) -> bool:
        return datetime.utcnow() > self.expires_at

    @property
    def completion_percentage(self) -> float:
        if self.total_blocks == 0:
            return 0.0
        return (self.completed_blocks / self.total_blocks) * 100


class V4Response(Base):
    """V4 四選二強制選擇回答"""
    __tablename__ = "v4_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("v4_sessions.session_id"), nullable=False)
    block_id = Column(String(20), nullable=False)  # block_0, block_1等
    block_index = Column(Integer, nullable=False)  # 0-based順序

    # 四選二回答核心
    most_like_index = Column(Integer, nullable=False)    # 0-3, 最像的語句
    least_like_index = Column(Integer, nullable=False)   # 0-3, 最不像的語句

    # 計時與品質
    response_time_ms = Column(Integer, nullable=False)   # 回答時間
    is_valid_response = Column(Boolean, default=True)    # 回答有效性

    # 回答時間戳記
    answered_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    session = relationship("V4Session", back_populates="responses")
    response_items = relationship("V4ResponseItem", back_populates="response", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<V4Response(session_id={self.session_id}, block_id={self.block_id}, most={self.most_like_index}, least={self.least_like_index})>"

    @property
    def is_consistent(self) -> bool:
        """檢查回答一致性 - 最像和最不像不能是同一個"""
        return self.most_like_index != self.least_like_index


class V4ResponseItem(Base):
    """V4 回答項目詳細 - 記錄每個語句的選擇狀態"""
    __tablename__ = "v4_response_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    response_id = Column(Integer, ForeignKey("v4_responses.id"), nullable=False)
    statement_id = Column(String(10), ForeignKey("v4_statements.statement_id"), nullable=False)
    statement_index = Column(Integer, nullable=False)  # 0-3在block中的位置

    # 選擇狀態
    choice_type = Column(String(15), nullable=False)  # most_like, least_like, neutral, neutral

    # 時間戳記
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    response = relationship("V4Response", back_populates="response_items")
    statement = relationship("V4Statement", back_populates="response_items")

    def __repr__(self):
        return f"<V4ResponseItem(statement_id={self.statement_id}, choice={self.choice_type})>"


class V4Score(Base):
    """V4 Thurstonian IRT 計分結果"""
    __tablename__ = "v4_scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("v4_sessions.session_id"), nullable=False, unique=True)

    # T1-T12 維度分數 (標準化到0-100)
    t1_structured_execution = Column(Float, nullable=False)
    t2_quality_perfectionism = Column(Float, nullable=False)
    t3_exploration_innovation = Column(Float, nullable=False)
    t4_analytical_insight = Column(Float, nullable=False)
    t5_influence_advocacy = Column(Float, nullable=False)
    t6_collaboration_harmony = Column(Float, nullable=False)
    t7_customer_orientation = Column(Float, nullable=False)
    t8_learning_growth = Column(Float, nullable=False)
    t9_discipline_trust = Column(Float, nullable=False)
    t10_pressure_regulation = Column(Float, nullable=False)
    t11_conflict_integration = Column(Float, nullable=False)
    t12_responsibility_accountability = Column(Float, nullable=False)

    # Thurstonian IRT 技術參數
    theta_estimates = Column(JSON, nullable=False)    # 12維度theta值
    standard_errors = Column(JSON, nullable=False)    # 對應標準誤差
    information_matrix = Column(JSON)                  # Fisher Information

    # 百分位數與常模
    percentiles = Column(JSON, nullable=False)         # T1-T12百分位數
    norm_group = Column(String(50), default="taiwan_2025")

    # 品質指標
    overall_confidence = Column(Float, nullable=False)  # 整體信心分數0-1
    dimension_reliability = Column(JSON, nullable=False) # 各維度信度
    response_consistency = Column(Float, nullable=False) # 回答一致性

    # 才幹分層
    dominant_talents = Column(JSON, nullable=False)     # 主導才幹 (>75%)
    supporting_talents = Column(JSON, nullable=False)   # 支持才幹 (25-75%)
    lesser_talents = Column(JSON, nullable=False)       # 較弱才幹 (<25%)

    # 計分元資料
    scoring_algorithm = Column(String(30), default="thurstonian_irt_v4", nullable=False)
    algorithm_version = Column(String(20), nullable=False)
    computation_time_ms = Column(Float, nullable=False)
    calibration_version = Column(String(20), nullable=False)

    # 時間戳記
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    session = relationship("V4Session", back_populates="scores")

    def __repr__(self):
        return f"<V4Score(session_id={self.session_id}, confidence={self.overall_confidence:.2f})>"

    @property
    def t_dimension_scores(self) -> Dict[str, float]:
        """取得 T1-T12 維度分數字典"""
        return {
            'T1': self.t1_structured_execution,
            'T2': self.t2_quality_perfectionism,
            'T3': self.t3_exploration_innovation,
            'T4': self.t4_analytical_insight,
            'T5': self.t5_influence_advocacy,
            'T6': self.t6_collaboration_harmony,
            'T7': self.t7_customer_orientation,
            'T8': self.t8_learning_growth,
            'T9': self.t9_discipline_trust,
            'T10': self.t10_pressure_regulation,
            'T11': self.t11_conflict_integration,
            'T12': self.t12_responsibility_accountability
        }

    @property
    def top_5_talents(self) -> List[Dict[str, Any]]:
        """取得前5大才幹"""
        scores = self.t_dimension_scores
        sorted_talents = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {
                'dimension': dim,
                'score': score,
                'percentile': self.percentiles.get(dim, 50) if self.percentiles else 50
            }
            for dim, score in sorted_talents[:5]
        ]


class V4ArchetypeResult(Base):
    """V4 動態職業原型分析結果"""
    __tablename__ = "v4_archetype_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("v4_sessions.session_id"), nullable=False, unique=True)

    # 凱爾西四種原型 (基於T1-T12動態分析)
    primary_archetype = Column(String(30), nullable=False)      # 主要原型
    secondary_archetype = Column(String(30))                    # 次要原型
    archetype_confidence = Column(Float, nullable=False)        # 分類信心 0-1

    # 四種原型分數
    guardian_organizer_score = Column(Float, nullable=False)    # 組織守護者
    artisan_implementer_score = Column(Float, nullable=False)   # 推廣實踐家
    rational_architect_score = Column(Float, nullable=False)    # 系統建構者
    idealist_catalyst_score = Column(Float, nullable=False)     # 人文關懷家

    # 才幹組合分析
    talent_combination = Column(JSON, nullable=False)           # 才幹組合模式
    leadership_style = Column(String(50))                       # 領導風格
    work_preference = Column(JSON, nullable=False)              # 工作偏好
    stress_management = Column(JSON)                            # 壓力管理模式

    # 發展建議
    development_focus = Column(JSON, nullable=False)            # 發展重點
    stretch_opportunities = Column(JSON)                        # 延展機會
    potential_derailers = Column(JSON)                          # 潛在偏軌因子

    # 分析元資料
    analysis_algorithm = Column(String(30), default="dynamic_archetype_v4", nullable=False)
    algorithm_version = Column(String(20), nullable=False)
    analysis_confidence = Column(Float, nullable=False)         # 分析信心

    # 時間戳記
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    session = relationship("V4Session", back_populates="archetype_result")

    def __repr__(self):
        return f"<V4ArchetypeResult(session_id={self.session_id}, primary={self.primary_archetype})>"

    @property
    def archetype_scores(self) -> Dict[str, float]:
        """取得四種原型分數"""
        return {
            'guardian_organizer': self.guardian_organizer_score,
            'artisan_implementer': self.artisan_implementer_score,
            'rational_architect': self.rational_architect_score,
            'idealist_catalyst': self.idealist_catalyst_score
        }

    @property
    def is_high_confidence(self) -> bool:
        """檢查是否為高信心分析結果"""
        return self.archetype_confidence >= 0.75 and self.analysis_confidence >= 0.75


# 更新Consent模型以支援V4關聯
def update_consent_relationships():
    """更新Consent模型的關聯"""
    from models.database import Consent

    # 添加V4 sessions關聯
    Consent.v4_sessions = relationship("V4Session", back_populates="consent")


# 索引定義以優化查詢效能
def create_v4_indexes(engine):
    """建立V4專用索引"""
    from sqlalchemy import text

    with engine.connect() as conn:
        # V4 Sessions索引
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_v4_sessions_status ON v4_sessions(status, created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_v4_sessions_consent ON v4_sessions(consent_id)"))

        # V4 Responses索引
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_v4_responses_session ON v4_responses(session_id, block_index)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_v4_responses_timing ON v4_responses(answered_at, response_time_ms)"))

        # V4 Statements索引
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_v4_statements_dimension ON v4_statements(dimension, is_calibrated)"))

        # V4 Scores索引
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_v4_scores_confidence ON v4_scores(overall_confidence, created_at)"))


# V4資料表名稱列表
V4_TABLE_NAMES = [
    "v4_statements",
    "v4_sessions",
    "v4_responses",
    "v4_response_items",
    "v4_scores",
    "v4_archetype_results"
]