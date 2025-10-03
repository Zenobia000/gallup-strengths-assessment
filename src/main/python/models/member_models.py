"""
會員系統資料模型 (Member System Models)

定義會員認證與管理相關的所有資料表:
- Members (會員主表)
- Email Verification Tokens (Email驗證令牌)
- Auth Tokens (Refresh Tokens)
- OAuth Providers (OAuth綁定)
- Member Assessments (會員評測關聯)
- Share Links (分享連結)
- Audit Logs (審計軌跡)

設計原則:
- 遵循 GDPR 個人資料保護規範
- 支援軟刪除 (Soft Delete)
- 完整審計軌跡
- 安全性第一 (密碼雜湊, Token管理)
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey, JSON, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

from models.database import Base


class Member(Base):
    """會員主表"""
    __tablename__ = "members"

    # 主鍵與識別
    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    email = Column(String(255), unique=True, index=True, nullable=False)

    # Email驗證
    email_verified = Column(Boolean, nullable=False, default=False)
    email_verified_at = Column(DateTime)

    # 密碼 (bcrypt雜湊, OAuth帳號可為空)
    password_hash = Column(String(255))

    # 個人資料
    full_name = Column(String(100))
    display_name = Column(String(50))
    job_title = Column(String(100))
    industry = Column(String(50))
    company = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(500))

    # 帳號狀態
    account_status = Column(String(20), nullable=False, default="active")  # active/suspended/deleted
    account_type = Column(String(20), nullable=False, default="free")  # free/premium/enterprise

    # 設定 (JSON)
    privacy_settings = Column(JSON)  # 隱私設定
    preferences = Column(JSON)  # 偏好設定

    # 登入追蹤
    last_login_at = Column(DateTime)
    last_login_ip = Column(String(45))  # IPv6支援
    login_count = Column(Integer, nullable=False, default=0)

    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime)  # 軟刪除

    # 關聯
    verification_tokens = relationship("EmailVerificationToken", back_populates="member", cascade="all, delete-orphan")
    auth_tokens = relationship("AuthToken", back_populates="member", cascade="all, delete-orphan")
    oauth_providers = relationship("OAuthProvider", back_populates="member", cascade="all, delete-orphan")
    member_assessments = relationship("MemberAssessment", back_populates="member", cascade="all, delete-orphan")
    share_links = relationship("ShareLink", back_populates="member", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="member")

    def __repr__(self):
        return f"<Member(member_id={self.member_id}, email={self.email}, status={self.account_status})>"

    @property
    def is_active(self) -> bool:
        """檢查帳號是否啟用"""
        return self.account_status == "active" and self.deleted_at is None

    @property
    def is_verified(self) -> bool:
        """檢查 Email 是否已驗證"""
        return self.email_verified and self.email_verified_at is not None

    @property
    def privacy_settings_dict(self) -> Dict:
        """取得隱私設定字典"""
        if not self.privacy_settings:
            return {
                "marketing_emails": False,
                "data_for_research": False,
                "profile_visibility": "private"
            }
        return json.loads(self.privacy_settings) if isinstance(self.privacy_settings, str) else self.privacy_settings


class EmailVerificationToken(Base):
    """Email驗證令牌表"""
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False)

    # 令牌
    token = Column(String(64), unique=True, index=True, nullable=False)  # SHA256雜湊
    token_type = Column(String(20), nullable=False)  # email_verification/password_reset

    # 有效期
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime)

    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now())

    # 關聯
    member = relationship("Member", back_populates="verification_tokens")

    def __repr__(self):
        return f"<EmailVerificationToken(member_id={self.member_id}, type={self.token_type}, used={self.used_at is not None})>"

    @property
    def is_valid(self) -> bool:
        """檢查令牌是否有效"""
        return self.used_at is None and datetime.utcnow() < self.expires_at

    def mark_as_used(self):
        """標記令牌為已使用"""
        self.used_at = datetime.utcnow()


class AuthToken(Base):
    """認證令牌表 (Refresh Token)"""
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False)

    # Token
    token_hash = Column(String(255), unique=True, index=True, nullable=False)  # 雜湊值
    token_family = Column(String(36), nullable=False, index=True)  # Token家族ID (防重放攻擊)

    # 撤銷狀態
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime)
    revoke_reason = Column(String(100))

    # 裝置與網路資訊
    device_info = Column(String(500))
    ip_address = Column(String(45))

    # 有效期
    expires_at = Column(DateTime, nullable=False)
    last_used_at = Column(DateTime)

    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now())

    # 關聯
    member = relationship("Member", back_populates="auth_tokens")

    def __repr__(self):
        return f"<AuthToken(member_id={self.member_id}, revoked={self.is_revoked}, expires={self.expires_at})>"

    @property
    def is_valid(self) -> bool:
        """檢查令牌是否有效"""
        return not self.is_revoked and datetime.utcnow() < self.expires_at

    def revoke(self, reason: str = "manual_revoke"):
        """撤銷令牌"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        self.revoke_reason = reason


class OAuthProvider(Base):
    """OAuth提供商綁定表"""
    __tablename__ = "oauth_providers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False)

    # 提供商資訊
    provider = Column(String(20), nullable=False)  # google/facebook/line
    provider_user_id = Column(String(255), nullable=False)
    provider_email = Column(String(255))
    provider_data = Column(JSON)  # 額外提供商資料

    # Token (加密存儲)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expires_at = Column(DateTime)

    # 主要登入方式
    is_primary = Column(Boolean, nullable=False, default=False)

    # 時間戳記
    linked_at = Column(DateTime, nullable=False, default=func.now())
    last_used_at = Column(DateTime)
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 關聯
    member = relationship("Member", back_populates="oauth_providers")

    # 複合唯一約束
    __table_args__ = (
        Index('idx_oauth_provider_user', 'provider', 'provider_user_id', unique=True),
        Index('idx_oauth_member_provider', 'member_id', 'provider', unique=True),
    )

    def __repr__(self):
        return f"<OAuthProvider(member_id={self.member_id}, provider={self.provider}, primary={self.is_primary})>"

    @property
    def is_token_expired(self) -> bool:
        """檢查 Token 是否過期"""
        if not self.token_expires_at:
            return False
        return datetime.utcnow() > self.token_expires_at


class MemberAssessment(Base):
    """會員評測關聯表"""
    __tablename__ = "member_assessments"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False)

    # 評測會話 (可關聯至 v4_sessions 或 assessment_sessions)
    session_id = Column(String(36), unique=True, index=True, nullable=False)
    assessment_type = Column(String(20), nullable=False)  # v4/mini_ipip

    # 自訂資料
    assessment_title = Column(String(200))
    assessment_notes = Column(Text)

    # 標記與可見性
    is_favorite = Column(Boolean, nullable=False, default=False)
    visibility = Column(String(20), nullable=False, default="private")  # private/public/shared

    # 時間戳記
    linked_at = Column(DateTime, nullable=False, default=func.now())
    completed_at = Column(DateTime)  # 冗餘,方便查詢
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # 關聯
    member = relationship("Member", back_populates="member_assessments")
    share_links = relationship("ShareLink", back_populates="assessment")

    def __repr__(self):
        return f"<MemberAssessment(member_id={self.member_id}, session_id={self.session_id}, type={self.assessment_type})>"

    @property
    def is_completed(self) -> bool:
        """檢查評測是否完成"""
        return self.completed_at is not None


class ShareLink(Base):
    """分享連結管理表"""
    __tablename__ = "share_links"

    id = Column(Integer, primary_key=True, autoincrement=True)
    share_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    member_id = Column(String(36), ForeignKey("members.member_id"), nullable=False)
    session_id = Column(String(36), ForeignKey("member_assessments.session_id"), nullable=False)

    # 分享令牌
    share_token = Column(String(64), unique=True, index=True, nullable=False)
    link_type = Column(String(20), nullable=False, default="view_only")  # view_only/download

    # 存取控制
    access_password = Column(String(255))  # 密碼雜湊 (可選)
    expires_at = Column(DateTime)  # NULL = 永久
    max_access_count = Column(Integer)  # NULL = 無限制
    access_count = Column(Integer, nullable=False, default=0)

    # 撤銷狀態
    is_revoked = Column(Boolean, nullable=False, default=False)
    revoked_at = Column(DateTime)
    revoke_reason = Column(String(200))

    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now())
    last_accessed_at = Column(DateTime)

    # 關聯
    member = relationship("Member", back_populates="share_links")
    assessment = relationship("MemberAssessment", back_populates="share_links")

    def __repr__(self):
        return f"<ShareLink(share_id={self.share_id}, revoked={self.is_revoked}, accessed={self.access_count})>"

    @property
    def is_accessible(self) -> bool:
        """檢查連結是否可存取"""
        if self.is_revoked:
            return False

        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False

        if self.max_access_count and self.access_count >= self.max_access_count:
            return False

        return True

    def increment_access(self):
        """增加存取次數"""
        self.access_count += 1
        self.last_accessed_at = datetime.utcnow()

    def revoke(self, reason: str = "manual_revoke"):
        """撤銷連結"""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        self.revoke_reason = reason


class AuditLog(Base):
    """審計軌跡表"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    member_id = Column(String(36), ForeignKey("members.member_id"))  # 可為空 (登入失敗時)

    # 操作資訊
    action = Column(String(50), nullable=False, index=True)  # login/logout/profile_update等
    action_category = Column(String(20), nullable=False, index=True)  # auth/profile/assessment/admin

    # 實體資訊
    entity_type = Column(String(50))  # member/assessment/share_link等
    entity_id = Column(String(36))

    # 請求資訊
    ip_address = Column(String(45), nullable=False)
    user_agent = Column(String(500))
    request_method = Column(String(10))  # GET/POST等
    request_path = Column(String(500))

    # 狀態與錯誤
    status = Column(String(20), nullable=False)  # success/failure/error
    error_message = Column(Text)

    # 額外元資料 (避免與 SQLAlchemy metadata 衝突)
    extra_data = Column(JSON)

    # 時間戳記
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)

    # 關聯
    member = relationship("Member", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog(member_id={self.member_id}, action={self.action}, status={self.status})>"

    @property
    def is_success(self) -> bool:
        """檢查操作是否成功"""
        return self.status == "success"


# 複合索引定義 (提升查詢效能)
Index('idx_members_status_created', Member.account_status, Member.created_at)
Index('idx_verification_member_type', EmailVerificationToken.member_id, EmailVerificationToken.token_type)
Index('idx_auth_tokens_member_revoked', AuthToken.member_id, AuthToken.is_revoked)
Index('idx_member_assessments_member_completed', MemberAssessment.member_id, MemberAssessment.completed_at.desc())
Index('idx_share_links_member_created', ShareLink.member_id, ShareLink.created_at.desc())
Index('idx_audit_logs_category_status_created', AuditLog.action_category, AuditLog.status, AuditLog.created_at.desc())


# 資料表名稱列表
MEMBER_TABLE_NAMES = [
    "members",
    "email_verification_tokens",
    "auth_tokens",
    "oauth_providers",
    "member_assessments",
    "share_links",
    "audit_logs"
]
