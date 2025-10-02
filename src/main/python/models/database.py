"""
SQLAlchemy Database Models - Gallup Strengths Assessment

定義所有資料表的 ORM 模型，支援:
- 同意記錄 (Consent)
- 測驗會話 (Assessment Sessions)
- 題目與回答 (Questions & Responses)
- 計分結果 (Scores)
- 優勢檔案 (Strengths Profiles)

遵循 Clean Architecture 原則與心理測量標準
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import json

Base = declarative_base()


class Consent(Base):
    """使用者同意記錄表"""
    __tablename__ = "consents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    consent_id = Column(String(36), unique=True, index=True, nullable=False)
    agreed = Column(Boolean, nullable=False)
    user_agent = Column(String(500), nullable=False)
    ip_address = Column(String(45))  # IPv6 支援
    consent_version = Column(String(10), default="v1.0", nullable=False)
    agreed_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    sessions = relationship("AssessmentSession", back_populates="consent")

    def __repr__(self):
        return f"<Consent(consent_id={self.consent_id}, agreed={self.agreed})>"


class AssessmentItem(Base):
    """測驗題目表 (Mini-IPIP 20題)"""
    __tablename__ = "assessment_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    item_id = Column(String(20), unique=True, index=True, nullable=False)  # "ipip_001"
    question_number = Column(Integer, nullable=False)  # 1-20
    question_text_zh = Column(Text, nullable=False)
    question_text_en = Column(Text)
    factor = Column(String(20), nullable=False)  # "extraversion", "agreeableness", etc.
    is_reverse_scored = Column(Boolean, default=False, nullable=False)
    scale_type = Column(String(10), default="likert_7", nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    responses = relationship("AssessmentResponse", back_populates="item")

    def __repr__(self):
        return f"<AssessmentItem(item_id={self.item_id}, factor={self.factor})>"


class AssessmentSession(Base):
    """測驗會話表"""
    __tablename__ = "assessment_sessions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)
    consent_id = Column(String(36), ForeignKey("consents.consent_id"), nullable=False)
    status = Column(String(20), default="PENDING", nullable=False)
    instrument_version = Column(String(20), default="mini_ipip_v1.0", nullable=False)
    started_at = Column(DateTime, default=func.now(), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime)
    total_questions = Column(Integer, default=20, nullable=False)
    answered_questions = Column(Integer, default=0, nullable=False)
    session_metadata = Column(JSON)  # 額外的會話資料
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    consent = relationship("Consent", back_populates="sessions")
    responses = relationship("AssessmentResponse", back_populates="session")
    scores = relationship("Score", back_populates="session")
    archetype_result = relationship("UserArchetypeResult", back_populates="session", uselist=False)
    job_recommendations = relationship("JobRecommendation", back_populates="session")

    def __repr__(self):
        return f"<AssessmentSession(session_id={self.session_id}, status={self.status})>"

    @property
    def is_completed(self) -> bool:
        """檢查測驗是否完成"""
        return self.status == "COMPLETED" and self.answered_questions >= self.total_questions

    @property
    def is_expired(self) -> bool:
        """檢查會話是否過期"""
        return datetime.utcnow() > self.expires_at

    def update_progress(self):
        """更新回答進度"""
        if self.answered_questions >= self.total_questions:
            self.status = "COMPLETED"
            if not self.completed_at:
                self.completed_at = datetime.utcnow()


class AssessmentResponse(Base):
    """測驗回答表"""
    __tablename__ = "assessment_responses"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.session_id"), nullable=False)
    item_id = Column(String(20), ForeignKey("assessment_items.item_id"), nullable=False)
    question_number = Column(Integer, nullable=False)  # 1-20
    response_value = Column(Integer, nullable=False)  # 1-7 for Likert scale
    response_time_ms = Column(Integer)  # 回答時間 (毫秒)
    answered_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    session = relationship("AssessmentSession", back_populates="responses")
    item = relationship("AssessmentItem", back_populates="responses")

    def __repr__(self):
        return f"<AssessmentResponse(session_id={self.session_id}, item_id={self.item_id}, response={self.response_value})>"

    @property
    def is_valid_response(self) -> bool:
        """驗證回答是否有效"""
        return 1 <= self.response_value <= 7


class Score(Base):
    """計分結果表"""
    __tablename__ = "scores"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.session_id"), nullable=False)

    # Big Five 原始分數 (4-28 for 7-point scale)
    raw_scores = Column(JSON, nullable=False)

    # 標準化分數 (0-100)
    standardized_scores = Column(JSON, nullable=False)

    # 百分位數 (0-100)
    percentiles = Column(JSON, nullable=False)

    # 計分品質指標
    confidence_level = Column(String(20), nullable=False)  # "high", "medium", "low"
    quality_flags = Column(JSON)  # 品質檢查旗標列表
    scoring_confidence = Column(Float)  # 數值信心分數 (0-1)

    # 計分元資料
    scoring_version = Column(String(20), nullable=False)
    computation_time_ms = Column(Float, nullable=False)
    norms_version = Column(String(20), default="taiwan_2025", nullable=False)

    # 優勢檔案 (可選)
    strengths_profile = Column(JSON)  # 完整優勢檔案
    top_strengths = Column(JSON)  # 前5名優勢摘要

    # 時間戳記
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    session = relationship("AssessmentSession", back_populates="scores")

    def __repr__(self):
        return f"<Score(session_id={self.session_id}, confidence={self.confidence_level})>"

    @property
    def big_five_summary(self) -> dict:
        """取得 Big Five 摘要"""
        if not self.standardized_scores:
            return {}

        scores = json.loads(self.standardized_scores) if isinstance(self.standardized_scores, str) else self.standardized_scores
        return {
            factor: round(score, 1)
            for factor, score in scores.items()
        }

    @property
    def dominant_factors(self) -> list:
        """取得主導人格因子 (分數 > 70)"""
        scores = self.big_five_summary
        return [
            factor for factor, score in scores.items()
            if score > 70
        ]

    def get_factor_percentile(self, factor: str) -> float:
        """取得特定因子的百分位數"""
        if not self.percentiles:
            return 50.0

        percentiles = json.loads(self.percentiles) if isinstance(self.percentiles, str) else self.percentiles
        return percentiles.get(factor, 50.0)


# Career Archetype System Models
class CareerArchetype(Base):
    """職業原型表 - 基於凱爾西氣質理論的4種原型"""
    __tablename__ = "career_archetypes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    archetype_id = Column(String(20), unique=True, index=True, nullable=False)
    archetype_name = Column(String(50), nullable=False)
    archetype_name_en = Column(String(50), nullable=False)
    keirsey_temperament = Column(String(50), nullable=False)
    mbti_correlates = Column(JSON, nullable=False)  # Array of MBTI types
    description = Column(Text, nullable=False)
    core_characteristics = Column(JSON, nullable=False)  # Array of characteristics
    work_environment_preferences = Column(JSON, nullable=False)  # Object
    leadership_style = Column(Text)
    decision_making_style = Column(Text)
    communication_style = Column(Text)
    stress_indicators = Column(JSON)  # Array
    development_areas = Column(JSON)  # Array
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    archetype_talents = relationship("ArchetypeTalent", back_populates="archetype")
    job_matches = relationship("ArchetypeJobMatch", back_populates="archetype")

    def __repr__(self):
        return f"<CareerArchetype(archetype_id={self.archetype_id}, name={self.archetype_name})>"


class TalentDimension(Base):
    """才幹維度表 - 12個核心才幹維度"""
    __tablename__ = "talent_dimensions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    dimension_id = Column(String(10), unique=True, index=True, nullable=False)  # T1-T12
    dimension_name = Column(String(50), nullable=False)
    dimension_name_en = Column(String(50), nullable=False)
    category = Column(String(20), nullable=False)  # executing, influencing, relationship, strategic
    description = Column(Text, nullable=False)
    behavioral_indicators = Column(JSON)  # Array
    development_strategies = Column(JSON)  # Array
    assessment_questions = Column(JSON)  # Array
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    archetype_talents = relationship("ArchetypeTalent", back_populates="dimension")

    def __repr__(self):
        return f"<TalentDimension(dimension_id={self.dimension_id}, name={self.dimension_name})>"


class ArchetypeTalent(Base):
    """原型與才幹關聯表 - 多對多關係，包含權重"""
    __tablename__ = "archetype_talents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    archetype_id = Column(String(20), ForeignKey("career_archetypes.archetype_id"), nullable=False)
    dimension_id = Column(String(10), ForeignKey("talent_dimensions.dimension_id"), nullable=False)
    talent_type = Column(String(20), nullable=False)  # primary, secondary, neutral, avoid
    weight = Column(Float, default=1.0, nullable=False)
    importance_level = Column(Integer, default=3, nullable=False)  # 1-5 scale
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    archetype = relationship("CareerArchetype", back_populates="archetype_talents")
    dimension = relationship("TalentDimension", back_populates="archetype_talents")

    def __repr__(self):
        return f"<ArchetypeTalent(archetype={self.archetype_id}, dimension={self.dimension_id}, type={self.talent_type})>"


class JobRole(Base):
    """職位角色表 - 具體職位定義"""
    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    role_id = Column(String(20), unique=True, index=True, nullable=False)
    role_name = Column(String(100), nullable=False)
    role_name_en = Column(String(100))
    industry_sector = Column(String(50), nullable=False)
    job_family = Column(String(50), nullable=False)
    seniority_level = Column(String(20), nullable=False)  # entry, mid, senior, executive
    description = Column(Text, nullable=False)
    key_responsibilities = Column(JSON, nullable=False)  # Array
    required_skills = Column(JSON, nullable=False)  # Array
    preferred_skills = Column(JSON)  # Array
    required_talents = Column(JSON, nullable=False)  # Array with weights
    beneficial_talents = Column(JSON)  # Array with weights
    education_requirements = Column(Text)
    experience_requirements = Column(Text)
    salary_range_min = Column(Integer)
    salary_range_max = Column(Integer)
    currency = Column(String(5), default="TWD")
    work_arrangement = Column(String(20))  # remote, hybrid, onsite
    career_growth_path = Column(JSON)  # Array
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    job_matches = relationship("ArchetypeJobMatch", back_populates="job_role")
    recommendations = relationship("JobRecommendation", back_populates="job_role")

    def __repr__(self):
        return f"<JobRole(role_id={self.role_id}, name={self.role_name})>"


class ArchetypeJobMatch(Base):
    """原型與職位關聯表 - 原型適合的職位推薦"""
    __tablename__ = "archetype_job_matches"

    id = Column(Integer, primary_key=True, autoincrement=True)
    archetype_id = Column(String(20), ForeignKey("career_archetypes.archetype_id"), nullable=False)
    role_id = Column(String(20), ForeignKey("job_roles.role_id"), nullable=False)
    match_score = Column(Float, nullable=False)  # 0.0-1.0
    match_reasoning = Column(JSON)  # Object with detailed reasoning
    confidence_level = Column(Float, default=0.8, nullable=False)
    priority_rank = Column(Integer)  # 1-N ranking
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 關聯
    archetype = relationship("CareerArchetype", back_populates="job_matches")
    job_role = relationship("JobRole", back_populates="job_matches")

    def __repr__(self):
        return f"<ArchetypeJobMatch(archetype={self.archetype_id}, role={self.role_id}, score={self.match_score})>"


class UserArchetypeResult(Base):
    """用戶職業原型分析結果表"""
    __tablename__ = "user_archetype_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.session_id"), nullable=False)
    primary_archetype_id = Column(String(20), ForeignKey("career_archetypes.archetype_id"), nullable=False)
    secondary_archetype_id = Column(String(20), ForeignKey("career_archetypes.archetype_id"))
    archetype_scores = Column(JSON, nullable=False)  # Object with all 4 scores
    dominant_talents = Column(JSON, nullable=False)  # Array
    supporting_talents = Column(JSON, nullable=False)  # Array
    lesser_talents = Column(JSON, nullable=False)  # Array
    confidence_score = Column(Float, nullable=False)
    analysis_metadata = Column(JSON)  # Object
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    session = relationship("AssessmentSession", back_populates="archetype_result")
    primary_archetype = relationship("CareerArchetype", foreign_keys=[primary_archetype_id])
    secondary_archetype = relationship("CareerArchetype", foreign_keys=[secondary_archetype_id])

    def __repr__(self):
        return f"<UserArchetypeResult(session={self.session_id}, primary={self.primary_archetype_id})>"


class JobRecommendation(Base):
    """職位推薦結果表"""
    __tablename__ = "job_recommendations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.session_id"), nullable=False)
    role_id = Column(String(20), ForeignKey("job_roles.role_id"), nullable=False)
    recommendation_type = Column(String(20), nullable=False)  # primary, stretch, development
    match_score = Column(Float, nullable=False)
    strength_alignment = Column(JSON, nullable=False)  # Object
    development_gaps = Column(JSON)  # Array
    recommendation_reasoning = Column(JSON, nullable=False)  # Object
    priority_rank = Column(Integer, nullable=False)
    confidence_level = Column(Float, nullable=False)
    is_featured = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    # 關聯
    session = relationship("AssessmentSession", back_populates="job_recommendations")
    job_role = relationship("JobRole", back_populates="recommendations")

    def __repr__(self):
        return f"<JobRecommendation(session={self.session_id}, role={self.role_id}, score={self.match_score})>"


class ReportGeneration(Base):
    """報告生成記錄表"""
    __tablename__ = "report_generations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(36), ForeignKey("assessment_sessions.session_id"), nullable=False)
    report_type = Column(String(50), nullable=False)  # "pdf", "json", "summary"
    report_format = Column(String(20), default="pdf", nullable=False)

    # 報告內容
    report_title = Column(String(200))
    report_data = Column(JSON)  # 報告結構化資料
    file_path = Column(String(500))  # 實際檔案路徑
    file_size_bytes = Column(Integer)

    # 生成狀態
    generation_status = Column(String(20), default="pending", nullable=False)
    generation_started_at = Column(DateTime)
    generation_completed_at = Column(DateTime)
    generation_time_ms = Column(Float)
    error_message = Column(Text)

    # 分享設定
    share_token = Column(String(64), unique=True, index=True)
    share_expires_at = Column(DateTime)
    access_count = Column(Integer, default=0, nullable=False)
    max_access_count = Column(Integer, default=1, nullable=False)

    # 時間戳記
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<ReportGeneration(session_id={self.session_id}, status={self.generation_status})>"

    @property
    def is_accessible(self) -> bool:
        """檢查報告是否可存取"""
        if self.generation_status != "completed":
            return False

        if self.share_expires_at and datetime.utcnow() > self.share_expires_at:
            return False

        if self.access_count >= self.max_access_count:
            return False

        return True

    def increment_access(self):
        """增加存取次數"""
        self.access_count += 1
        self.updated_at = datetime.utcnow()


# 索引定義
def create_indexes(engine):
    """建立效能最佳化索引"""
    from sqlalchemy import Index, text

    # 複合索引用於常見查詢
    Index('idx_session_status_created', AssessmentSession.status, AssessmentSession.created_at)
    Index('idx_response_session_question', AssessmentResponse.session_id, AssessmentResponse.question_number)
    Index('idx_score_confidence_created', Score.confidence_level, Score.created_at)
    Index('idx_report_status_created', ReportGeneration.generation_status, ReportGeneration.created_at)

    # 執行建立索引
    with engine.connect() as conn:
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_session_status_created ON assessment_sessions(status, created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_response_session_question ON assessment_responses(session_id, question_number)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_score_confidence_created ON scores(confidence_level, created_at)"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS idx_report_status_created ON report_generations(generation_status, created_at)"))


# 資料庫設定函式
def get_table_names():
    """取得所有資料表名稱"""
    return [
        "consents",
        "assessment_items",
        "assessment_sessions",
        "assessment_responses",
        "scores",
        "report_generations",
        # Career Archetypes System Tables
        "career_archetypes",
        "talent_dimensions",
        "archetype_talents",
        "job_roles",
        "archetype_job_matches",
        "user_archetype_results",
        "job_recommendations"
    ]


def validate_database_schema(engine):
    """驗證資料庫綱要完整性"""
    from sqlalchemy import inspect

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    expected_tables = get_table_names()

    missing_tables = set(expected_tables) - set(existing_tables)
    if missing_tables:
        raise RuntimeError(f"Missing database tables: {missing_tables}")

    return True