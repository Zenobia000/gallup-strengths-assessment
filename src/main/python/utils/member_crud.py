"""
會員 CRUD 工具函式 (Member CRUD Utilities)

提供會員資料的基礎 CRUD 操作:
- 創建會員
- 查詢會員
- 更新會員
- 刪除會員 (軟刪除)

設計原則:
- 單一職責原則 (Single Responsibility)
- DRY (Don't Repeat Yourself)
- 型別安全 (Type Hints)
- 完整錯誤處理
"""

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid

from models.member_models import (
    Member,
    EmailVerificationToken,
    AuthToken,
    OAuthProvider,
    MemberAssessment,
    ShareLink,
    AuditLog
)
from utils.auth_utils import hash_password, generate_token_family_id


# ==================== 會員 CRUD ====================

def create_member(
    db: Session,
    email: str,
    password: Optional[str] = None,
    full_name: Optional[str] = None,
    **kwargs
) -> Member:
    """
    創建新會員

    Args:
        db: SQLAlchemy Session
        email: Email (唯一識別)
        password: 密碼 (OAuth 帳號可為 None)
        full_name: 全名
        **kwargs: 其他可選欄位

    Returns:
        Member: 新建的會員物件

    Raises:
        ValueError: Email 已存在

    Examples:
        >>> member = create_member(db, "user@example.com", "SecurePass123")
        >>> member.email
        'user@example.com'
    """
    # 檢查 Email 是否已存在
    existing = get_member_by_email(db, email)
    if existing:
        raise ValueError(f"Email '{email}' already exists")

    # 生成會員 ID
    member_id = str(uuid.uuid4())

    # 雜湊密碼 (如果有提供)
    password_hash = hash_password(password) if password else None

    # 建立會員物件
    member = Member(
        member_id=member_id,
        email=email.lower(),  # 統一小寫
        password_hash=password_hash,
        full_name=full_name,
        email_verified=False,  # 預設未驗證
        **kwargs
    )

    db.add(member)
    db.commit()
    db.refresh(member)

    return member


def get_member_by_id(db: Session, member_id: str) -> Optional[Member]:
    """
    根據會員 ID 查詢會員

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID

    Returns:
        Optional[Member]: 會員物件或 None
    """
    return db.query(Member).filter(
        and_(
            Member.member_id == member_id,
            Member.deleted_at.is_(None)  # 排除已刪除
        )
    ).first()


def get_member_by_email(db: Session, email: str) -> Optional[Member]:
    """
    根據 Email 查詢會員

    Args:
        db: SQLAlchemy Session
        email: Email

    Returns:
        Optional[Member]: 會員物件或 None
    """
    return db.query(Member).filter(
        and_(
            Member.email == email.lower(),
            Member.deleted_at.is_(None)
        )
    ).first()


def update_member(
    db: Session,
    member_id: str,
    **fields
) -> Optional[Member]:
    """
    更新會員資料

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID
        **fields: 要更新的欄位

    Returns:
        Optional[Member]: 更新後的會員物件或 None

    Examples:
        >>> member = update_member(db, "member-123", full_name="John Doe")
        >>> member.full_name
        'John Doe'
    """
    member = get_member_by_id(db, member_id)
    if not member:
        return None

    # 更新欄位
    for field, value in fields.items():
        if hasattr(member, field):
            setattr(member, field, value)

    member.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(member)

    return member


def soft_delete_member(db: Session, member_id: str) -> bool:
    """
    軟刪除會員 (GDPR 合規)

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID

    Returns:
        bool: 是否成功刪除

    Note:
        - 設定 deleted_at 時間戳記
        - 保留資料用於審計
        - 匿名化個人資料
    """
    member = get_member_by_id(db, member_id)
    if not member:
        return False

    # 匿名化個人資料
    member.email = f"deleted_{member.member_id}@anonymized.local"
    member.full_name = None
    member.display_name = None
    member.phone = None
    member.avatar_url = None
    member.account_status = "deleted"
    member.deleted_at = datetime.utcnow()

    # 撤銷所有 Token
    db.query(AuthToken).filter(
        AuthToken.member_id == member_id
    ).update({"is_revoked": True, "revoked_at": datetime.utcnow()})

    db.commit()

    return True


def list_members(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    account_status: Optional[str] = None
) -> List[Member]:
    """
    列出會員清單 (分頁)

    Args:
        db: SQLAlchemy Session
        skip: 跳過筆數
        limit: 限制筆數
        account_status: 篩選帳號狀態

    Returns:
        List[Member]: 會員清單
    """
    query = db.query(Member).filter(Member.deleted_at.is_(None))

    if account_status:
        query = query.filter(Member.account_status == account_status)

    return query.offset(skip).limit(limit).all()


# ==================== 會員登入與驗證 ====================

def record_login(
    db: Session,
    member_id: str,
    ip_address: str
) -> Member:
    """
    記錄會員登入

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID
        ip_address: IP 位址

    Returns:
        Member: 更新後的會員物件
    """
    member = get_member_by_id(db, member_id)
    if not member:
        raise ValueError("Member not found")

    member.last_login_at = datetime.utcnow()
    member.last_login_ip = ip_address
    member.login_count += 1

    db.commit()
    db.refresh(member)

    return member


def verify_member_email(
    db: Session,
    member_id: str
) -> Member:
    """
    標記會員 Email 為已驗證

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID

    Returns:
        Member: 更新後的會員物件
    """
    member = get_member_by_id(db, member_id)
    if not member:
        raise ValueError("Member not found")

    member.email_verified = True
    member.email_verified_at = datetime.utcnow()

    db.commit()
    db.refresh(member)

    return member


# ==================== OAuth Provider CRUD ====================

def link_oauth_provider(
    db: Session,
    member_id: str,
    provider: str,
    provider_user_id: str,
    provider_email: Optional[str] = None,
    provider_data: Optional[Dict] = None,
    is_primary: bool = False
) -> OAuthProvider:
    """
    綁定 OAuth 提供商

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID
        provider: 提供商名稱 (google/facebook)
        provider_user_id: 提供商使用者 ID
        provider_email: 提供商 Email
        provider_data: 額外資料
        is_primary: 是否為主要登入方式

    Returns:
        OAuthProvider: OAuth 綁定物件
    """
    # 檢查是否已綁定
    existing = db.query(OAuthProvider).filter(
        and_(
            OAuthProvider.member_id == member_id,
            OAuthProvider.provider == provider
        )
    ).first()

    if existing:
        raise ValueError(f"Already linked to {provider}")

    oauth = OAuthProvider(
        member_id=member_id,
        provider=provider,
        provider_user_id=provider_user_id,
        provider_email=provider_email,
        provider_data=provider_data,
        is_primary=is_primary
    )

    db.add(oauth)
    db.commit()
    db.refresh(oauth)

    return oauth


def get_oauth_provider(
    db: Session,
    provider: str,
    provider_user_id: str
) -> Optional[OAuthProvider]:
    """
    根據提供商和使用者 ID 查詢 OAuth 綁定

    Args:
        db: SQLAlchemy Session
        provider: 提供商名稱
        provider_user_id: 提供商使用者 ID

    Returns:
        Optional[OAuthProvider]: OAuth 綁定物件或 None
    """
    return db.query(OAuthProvider).filter(
        and_(
            OAuthProvider.provider == provider,
            OAuthProvider.provider_user_id == provider_user_id
        )
    ).first()


# ==================== 審計日誌 CRUD ====================

def create_audit_log(
    db: Session,
    member_id: Optional[str],
    action: str,
    action_category: str,
    ip_address: str,
    status: str = "success",
    **kwargs
) -> AuditLog:
    """
    創建審計日誌

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID (可為 None)
        action: 操作名稱
        action_category: 操作類別 (auth/profile/assessment/admin)
        ip_address: IP 位址
        status: 狀態 (success/failure/error)
        **kwargs: 其他可選欄位

    Returns:
        AuditLog: 審計日誌物件
    """
    log = AuditLog(
        member_id=member_id,
        action=action,
        action_category=action_category,
        ip_address=ip_address,
        status=status,
        **kwargs
    )

    db.add(log)
    db.commit()
    db.refresh(log)

    return log


def get_member_audit_logs(
    db: Session,
    member_id: str,
    limit: int = 50
) -> List[AuditLog]:
    """
    查詢會員的審計日誌

    Args:
        db: SQLAlchemy Session
        member_id: 會員 ID
        limit: 限制筆數

    Returns:
        List[AuditLog]: 審計日誌清單 (最新優先)
    """
    return db.query(AuditLog).filter(
        AuditLog.member_id == member_id
    ).order_by(
        AuditLog.created_at.desc()
    ).limit(limit).all()


# ==================== 工具函式 ====================

def count_members(
    db: Session,
    account_status: Optional[str] = None
) -> int:
    """
    統計會員數量

    Args:
        db: SQLAlchemy Session
        account_status: 篩選帳號狀態

    Returns:
        int: 會員數量
    """
    query = db.query(Member).filter(Member.deleted_at.is_(None))

    if account_status:
        query = query.filter(Member.account_status == account_status)

    return query.count()


def search_members_by_name(
    db: Session,
    name_query: str,
    limit: int = 20
) -> List[Member]:
    """
    根據姓名搜尋會員

    Args:
        db: SQLAlchemy Session
        name_query: 搜尋關鍵字
        limit: 限制筆數

    Returns:
        List[Member]: 符合的會員清單
    """
    return db.query(Member).filter(
        and_(
            Member.deleted_at.is_(None),
            or_(
                Member.full_name.ilike(f"%{name_query}%"),
                Member.display_name.ilike(f"%{name_query}%")
            )
        )
    ).limit(limit).all()
