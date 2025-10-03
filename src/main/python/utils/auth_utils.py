"""
認證工具模組 (Authentication Utilities)

提供會員認證相關的核心工具:
- 密碼雜湊與驗證 (bcrypt)
- JWT Token 生成與驗證
- Token 刷新機制
- 安全隨機令牌生成

設計原則:
- 遵循 OWASP 安全標準
- bcrypt cost factor = 12
- JWT 有效期管理
- 防止時序攻擊 (Timing Attack)
"""

import bcrypt
import jwt
import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import wraps


# ==================== 配置常數 ====================

# bcrypt 配置
BCRYPT_COST_FACTOR = 12  # 建議值: 12-14 (平衡安全性與效能)

# JWT 配置
JWT_SECRET_KEY = "your-secret-key-change-in-production"  # TODO: 從環境變數讀取
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 7 * 24 * 60  # 7天
JWT_REFRESH_TOKEN_EXPIRE_MINUTES = 30 * 24 * 60  # 30天

# Token 長度
VERIFICATION_TOKEN_LENGTH = 32  # 256 bits
SHARE_TOKEN_LENGTH = 32  # 256 bits


# ==================== 密碼雜湊工具 ====================

def hash_password(password: str) -> str:
    """
    使用 bcrypt 雜湊密碼

    Args:
        password: 明文密碼

    Returns:
        str: bcrypt 雜湊值 (包含 salt)

    Examples:
        >>> hashed = hash_password("SecurePass123")
        >>> len(hashed) == 60
        True
    """
    if not password:
        raise ValueError("Password cannot be empty")

    # bcrypt 需要 bytes
    password_bytes = password.encode('utf-8')

    # 生成 salt 並雜湊
    salt = bcrypt.gensalt(rounds=BCRYPT_COST_FACTOR)
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode('utf-8')


def verify_password(password: str, hashed_password: str) -> bool:
    """
    驗證密碼是否正確

    Args:
        password: 使用者輸入的明文密碼
        hashed_password: 儲存的 bcrypt 雜湊值

    Returns:
        bool: 密碼是否正確

    Examples:
        >>> hashed = hash_password("SecurePass123")
        >>> verify_password("SecurePass123", hashed)
        True
        >>> verify_password("WrongPass", hashed)
        False
    """
    if not password or not hashed_password:
        return False

    try:
        password_bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')

        # bcrypt.checkpw 內建時序攻擊防護
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        # 任何錯誤都返回 False (避免資訊洩漏)
        return False


# ==================== JWT Token 工具 ====================

def create_access_token(
    member_id: str,
    email: str,
    additional_claims: Optional[Dict] = None
) -> str:
    """
    創建 JWT Access Token

    Args:
        member_id: 會員 ID
        email: 會員 Email
        additional_claims: 額外的聲明 (claims)

    Returns:
        str: JWT Token

    Examples:
        >>> token = create_access_token("member-123", "user@example.com")
        >>> isinstance(token, str)
        True
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": member_id,  # Subject (會員ID)
        "email": email,
        "type": "access",
        "iat": now,  # Issued At
        "exp": expires_at,  # Expiration
    }

    if additional_claims:
        payload.update(additional_claims)

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def create_refresh_token(member_id: str, token_family: str) -> Tuple[str, str]:
    """
    創建 Refresh Token

    Args:
        member_id: 會員 ID
        token_family: Token 家族 ID (用於防重放攻擊)

    Returns:
        Tuple[str, str]: (JWT Token, Token Hash)

    Note:
        - 返回的 Token Hash 需存入資料庫
        - 原始 Token 僅返回給客戶端一次
    """
    now = datetime.utcnow()
    expires_at = now + timedelta(minutes=JWT_REFRESH_TOKEN_EXPIRE_MINUTES)

    # 生成隨機 JTI (JWT ID)
    jti = secrets.token_urlsafe(32)

    payload = {
        "sub": member_id,
        "type": "refresh",
        "jti": jti,
        "family": token_family,
        "iat": now,
        "exp": expires_at,
    }

    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    # 雜湊 JTI 用於資料庫存儲
    token_hash = hashlib.sha256(jti.encode()).hexdigest()

    return token, token_hash


def verify_token(token: str, token_type: str = "access") -> Optional[Dict]:
    """
    驗證 JWT Token

    Args:
        token: JWT Token
        token_type: Token 類型 (access/refresh)

    Returns:
        Optional[Dict]: Token payload 或 None (驗證失敗)

    Examples:
        >>> token = create_access_token("member-123", "user@example.com")
        >>> payload = verify_token(token, "access")
        >>> payload["sub"] == "member-123"
        True
    """
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET_KEY,
            algorithms=[JWT_ALGORITHM]
        )

        # 驗證 Token 類型
        if payload.get("type") != token_type:
            return None

        return payload

    except jwt.ExpiredSignatureError:
        # Token 已過期
        return None
    except jwt.InvalidTokenError:
        # Token 無效
        return None
    except Exception:
        # 其他錯誤
        return None


def decode_token_without_verification(token: str) -> Optional[Dict]:
    """
    解碼 Token (不驗證簽名和過期時間)

    警告: 僅用於除錯或提取過期 Token 的資訊

    Args:
        token: JWT Token

    Returns:
        Optional[Dict]: Token payload 或 None
    """
    try:
        payload = jwt.decode(
            token,
            options={"verify_signature": False, "verify_exp": False}
        )
        return payload
    except Exception:
        return None


# ==================== 隨機令牌生成工具 ====================

def generate_verification_token() -> str:
    """
    生成 Email 驗證令牌

    Returns:
        str: URL-safe 隨機令牌 (256 bits)

    Examples:
        >>> token = generate_verification_token()
        >>> len(token) >= 32
        True
    """
    return secrets.token_urlsafe(VERIFICATION_TOKEN_LENGTH)


def generate_share_token() -> str:
    """
    生成分享連結令牌

    Returns:
        str: URL-safe 隨機令牌 (256 bits)
    """
    return secrets.token_urlsafe(SHARE_TOKEN_LENGTH)


def generate_token_family_id() -> str:
    """
    生成 Token 家族 ID (用於 Refresh Token)

    Returns:
        str: UUID 格式的家族 ID
    """
    import uuid
    return str(uuid.uuid4())


def hash_token(token: str) -> str:
    """
    雜湊令牌 (用於資料庫存儲)

    Args:
        token: 原始令牌

    Returns:
        str: SHA256 雜湊值 (hex)

    Examples:
        >>> hashed = hash_token("my-secret-token")
        >>> len(hashed) == 64
        True
    """
    return hashlib.sha256(token.encode()).hexdigest()


# ==================== 安全工具 ====================

def constant_time_compare(val1: str, val2: str) -> bool:
    """
    常數時間字串比較 (防止時序攻擊)

    Args:
        val1: 字串1
        val2: 字串2

    Returns:
        bool: 是否相等

    Note:
        使用內建的 secrets.compare_digest
    """
    return secrets.compare_digest(val1, val2)


# ==================== 裝飾器 ====================

def require_valid_token(token_type: str = "access"):
    """
    JWT Token 驗證裝飾器

    Usage:
        @require_valid_token("access")
        def protected_route(payload: Dict):
            member_id = payload["sub"]
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(token: str, *args, **kwargs):
            payload = verify_token(token, token_type)
            if not payload:
                raise ValueError("Invalid or expired token")
            return func(payload, *args, **kwargs)
        return wrapper
    return decorator


# ==================== 密碼強度驗證 ====================

def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    驗證密碼強度

    規則:
    - 最少 8 個字元
    - 至少包含 1 個大寫字母
    - 至少包含 1 個小寫字母
    - 至少包含 1 個數字

    Args:
        password: 密碼

    Returns:
        Tuple[bool, str]: (是否有效, 錯誤訊息)

    Examples:
        >>> validate_password_strength("SecurePass123")
        (True, '')
        >>> validate_password_strength("weak")
        (False, '密碼至少需要 8 個字元')
    """
    if len(password) < 8:
        return False, "密碼至少需要 8 個字元"

    if not any(c.isupper() for c in password):
        return False, "密碼需包含至少 1 個大寫字母"

    if not any(c.islower() for c in password):
        return False, "密碼需包含至少 1 個小寫字母"

    if not any(c.isdigit() for c in password):
        return False, "密碼需包含至少 1 個數字"

    return True, ""


# ==================== 配置檢查 ====================

def check_security_config():
    """
    檢查安全配置是否正確

    警告:
    - 生產環境必須使用環境變數設定 JWT_SECRET_KEY
    - 建議 SECRET_KEY 至少 256 bits
    """
    if JWT_SECRET_KEY == "your-secret-key-change-in-production":
        import warnings
        warnings.warn(
            "JWT_SECRET_KEY 使用預設值！生產環境必須設定環境變數！",
            SecurityWarning
        )


class SecurityWarning(UserWarning):
    """安全配置警告"""
    pass


# 啟動時檢查配置
check_security_config()
