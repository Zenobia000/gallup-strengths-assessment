"""
API 依賴注入 (Dependency Injection)

提供 FastAPI 路由所需的各種依賴:
- 資料庫 Session
- 認證驗證 (JWT Token)
- Rate Limiting
- CORS 設定

設計原則:
- 依賴注入模式
- 資源自動清理
- 錯誤處理標準化
"""

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Optional, Generator
from pathlib import Path
import os

from utils.auth_utils import verify_token

# ==================== 資料庫依賴 ====================

# 資料庫路徑設定
PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATABASE_PATH = PROJECT_ROOT / "data" / "gallup_strengths.db"
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"

# 建立 SQLAlchemy Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite 特定設定
    echo=False,  # 生產環境設為 False
    pool_pre_ping=True,  # 連線前檢查
)

# 建立 SessionLocal 類別
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """
    取得資料庫 Session (依賴注入)

    使用方式:
        @router.get("/example")
        def example(db: Session = Depends(get_db)):
            pass

    Yields:
        Session: SQLAlchemy Session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ==================== 認證依賴 ====================

security = HTTPBearer()


def get_current_member(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    驗證並取得當前登入會員

    Args:
        credentials: Bearer Token
        db: 資料庫 Session

    Returns:
        dict: Token payload (包含 member_id, email 等)

    Raises:
        HTTPException: 401 Unauthorized
    """
    token = credentials.credentials
    payload = verify_token(token, "access")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 驗證會員是否存在且啟用
    from utils.member_crud import get_member_by_id
    member = get_member_by_id(db, payload["sub"])

    if member is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Member not found",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not member.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deleted"
        )

    return payload


def get_current_member_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
) -> Optional[dict]:
    """
    可選的會員驗證 (用於可登入/未登入都可存取的端點)

    Args:
        authorization: Bearer Token (optional)
        db: 資料庫 Session

    Returns:
        Optional[dict]: Token payload 或 None
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    token = authorization.split(" ")[1]
    payload = verify_token(token, "access")

    if payload is None:
        return None

    # 驗證會員是否存在
    from utils.member_crud import get_member_by_id
    member = get_member_by_id(db, payload["sub"])

    if member is None or not member.is_active:
        return None

    return payload


def verify_refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """
    驗證 Refresh Token

    Args:
        credentials: Bearer Token (Refresh Token)
        db: 資料庫 Session

    Returns:
        dict: Token payload

    Raises:
        HTTPException: 401 Unauthorized
    """
    token = credentials.credentials
    payload = verify_token(token, "refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 檢查 Refresh Token 是否已被撤銷
    from models.member_models import AuthToken
    from utils.auth_utils import hash_token

    token_hash = hash_token(token)
    auth_token = db.query(AuthToken).filter(
        AuthToken.token_hash == token_hash,
        AuthToken.member_id == payload["sub"]
    ).first()

    if auth_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found"
        )

    if not auth_token.is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has been revoked or expired"
        )

    return payload


# ==================== 管理員權限依賴 ====================

def get_current_admin(
    current_member: dict = Depends(get_current_member),
    db: Session = Depends(get_db)
) -> dict:
    """
    驗證當前用戶是否為管理員

    Args:
        current_member: 當前會員
        db: 資料庫 Session

    Returns:
        dict: Token payload

    Raises:
        HTTPException: 403 Forbidden
    """
    from utils.member_crud import get_member_by_id
    member = get_member_by_id(db, current_member["sub"])

    # 檢查是否有管理員權限 (根據 account_type)
    if member.account_type not in ["admin", "enterprise"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )

    return current_member


# ==================== Rate Limiting (預留) ====================

def rate_limit_check():
    """
    Rate Limiting 檢查 (Week 5 實作)

    TODO:
    - 實作 Redis 計數器
    - 設定不同端點的限制
    - 返回 429 Too Many Requests
    """
    pass


# ==================== CORS 設定 (預留) ====================

def get_allowed_origins() -> list:
    """
    取得允許的 CORS 來源 (Week 5 實作)

    Returns:
        list: 允許的來源清單
    """
    # 從環境變數或設定檔讀取
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")

    # 開發環境預設
    if not allowed_origins or allowed_origins == [""]:
        return [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
            "http://127.0.0.1:8000",
        ]

    return allowed_origins
