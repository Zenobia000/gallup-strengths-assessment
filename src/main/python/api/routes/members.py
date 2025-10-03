"""
會員系統 API 路由 (Member System Routes)

提供會員相關的 RESTful API 端點:
- Week 1: 健康檢查, 基礎架構
- Week 2: 註冊/登入/登出, OAuth, 密碼找回
- Week 3+: 個人檔案管理, 評測綁定

設計原則:
- RESTful API 設計
- OpenAPI/Swagger 文檔
- 錯誤處理標準化
"""

from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime, timedelta
import secrets

# 內部模組導入
from api.dependencies import get_db, get_current_member, verify_refresh_token
from utils.member_crud import (
    create_member, get_member_by_id, get_member_by_email,
    update_member_info, soft_delete_member
)
from utils.auth_utils import (
    verify_password, validate_password_strength,
    create_access_token, create_refresh_token,
    hash_token, generate_verification_token
)
from models.member_models import EmailVerificationToken, AuthToken, AuditLog


# ==================== Pydantic Models (Request/Response Schemas) ====================

class MemberBase(BaseModel):
    """會員基礎 Schema"""
    email: EmailStr
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company: Optional[str] = None


class MemberCreate(BaseModel):
    """創建會員 Request Schema"""
    email: EmailStr
    password: str = Field(..., min_length=8, description="密碼 (最少8字元)")
    full_name: Optional[str] = Field(None, max_length=100)
    display_name: Optional[str] = Field(None, max_length=50)
    job_title: Optional[str] = Field(None, max_length=100)
    industry: Optional[str] = Field(None, max_length=50)
    company: Optional[str] = Field(None, max_length=100)

    @validator('password')
    def validate_password(cls, v):
        """驗證密碼強度"""
        valid, message = validate_password_strength(v)
        if not valid:
            raise ValueError(message)
        return v


class MemberUpdate(BaseModel):
    """更新會員 Request Schema"""
    full_name: Optional[str] = None
    display_name: Optional[str] = None
    job_title: Optional[str] = None
    industry: Optional[str] = None
    company: Optional[str] = None


class MemberResponse(MemberBase):
    """會員 Response Schema"""
    member_id: str
    email_verified: bool
    account_status: str
    account_type: str
    login_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Pydantic V2 (orm_mode in V1)


class HealthResponse(BaseModel):
    """健康檢查 Response"""
    status: str
    service: str
    version: str
    timestamp: datetime


# ==================== Router 初始化 ====================

router = APIRouter(
    prefix="/api/members",
    tags=["members"],
    responses={
        404: {"description": "Not found"},
        500: {"description": "Internal server error"}
    }
)


# ==================== API Endpoints ====================

@router.get(
    "/health",
    response_model=HealthResponse,
    summary="健康檢查",
    description="檢查會員系統 API 是否正常運作"
)
async def health_check():
    """
    健康檢查端點

    Returns:
        HealthResponse: 服務狀態資訊
    """
    return HealthResponse(
        status="healthy",
        service="member-system",
        version="1.0.0-week1",
        timestamp=datetime.utcnow()
    )


@router.get(
    "/",
    response_model=List[MemberResponse],
    summary="列出會員",
    description="取得會員清單 (分頁)"
)
async def list_members(
    skip: int = 0,
    limit: int = 100,
    account_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    列出會員清單

    Args:
        skip: 跳過筆數 (用於分頁)
        limit: 限制筆數 (最多100)
        account_status: 篩選帳號狀態 (active/suspended/deleted)
        db: 資料庫 Session

    Returns:
        List[MemberResponse]: 會員清單
    """
    # TODO: 實作查詢邏輯 (Week 1 佔位符)
    return []


@router.get(
    "/{member_id}",
    response_model=MemberResponse,
    summary="取得會員資訊",
    description="根據會員 ID 取得詳細資訊"
)
async def get_member(
    member_id: str,
    db: Session = Depends(get_db)
):
    """
    取得會員資訊

    Args:
        member_id: 會員 ID
        db: 資料庫 Session

    Returns:
        MemberResponse: 會員資訊

    Raises:
        HTTPException: 404 會員不存在
    """
    # TODO: 實作查詢邏輯
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not implemented yet (Week 2)"
    )


@router.post(
    "/register",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="註冊新會員",
    description="Email 註冊，自動生成驗證郵件"
)
async def register_member(
    member_data: MemberCreate,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    註冊新會員

    Args:
        member_data: 會員註冊資料
        request: FastAPI Request (用於取得 IP、User-Agent)
        db: 資料庫 Session

    Returns:
        MemberResponse: 新建的會員資訊

    Raises:
        HTTPException: 400 Email 已存在 或 密碼強度不足
    """
    try:
        # 檢查 Email 是否已存在
        existing_member = get_member_by_email(db, member_data.email)
        if existing_member:
            # 記錄審計日誌
            _log_audit(
                db, None, "register_attempt_duplicate_email",
                "auth", request, "failure",
                error_message=f"Email already exists: {member_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email address already registered"
            )

        # 建立會員
        member = create_member(
            db,
            email=member_data.email,
            password=member_data.password,
            full_name=member_data.full_name,
            display_name=member_data.display_name,
            job_title=member_data.job_title,
            industry=member_data.industry,
            company=member_data.company,
        )

        # 生成 Email 驗證 Token (W2-T002 會用到)
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)

        email_token = EmailVerificationToken(
            member_id=member.member_id,
            token=hash_token(verification_token),
            token_type="email_verification",
            expires_at=verification_expires
        )
        db.add(email_token)
        db.commit()

        # 記錄審計日誌
        _log_audit(
            db, member.member_id, "register_success",
            "auth", request, "success"
        )

        # TODO (W2-T002): 發送驗證郵件
        # send_verification_email(member.email, verification_token)

        return member

    except ValueError as e:
        # 密碼強度驗證失敗
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "register_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed. Please try again later."
        )


# ==================== Email 驗證端點 (W2-T002) ====================

class EmailVerificationRequest(BaseModel):
    """Email 驗證 Request Schema"""
    token: str = Field(..., min_length=32, description="驗證令牌")


@router.post(
    "/verify-email",
    summary="驗證 Email",
    description="使用驗證令牌啟用帳號"
)
async def verify_email(
    verification_data: EmailVerificationRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    驗證 Email 並啟用帳號

    Args:
        verification_data: 包含驗證令牌
        request: FastAPI Request
        db: 資料庫 Session

    Returns:
        dict: 驗證結果訊息

    Raises:
        HTTPException: 400 令牌無效或已過期
    """
    try:
        # 雜湊令牌進行查詢
        token_hash = hash_token(verification_data.token)

        # 查詢驗證令牌
        verification_token = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token_hash,
            EmailVerificationToken.token_type == "email_verification"
        ).first()

        if not verification_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification token"
            )

        # 檢查令牌是否有效
        if not verification_token.is_valid:
            if verification_token.used_at:
                detail = "Verification token has already been used"
            elif datetime.utcnow() >= verification_token.expires_at:
                detail = "Verification token has expired"
            else:
                detail = "Invalid verification token"

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=detail
            )

        # 取得會員
        member = get_member_by_id(db, verification_token.member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # 檢查是否已驗證
        if member.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )

        # 更新會員狀態
        member.email_verified = True
        member.email_verified_at = datetime.utcnow()

        # 標記令牌為已使用
        verification_token.mark_as_used()

        db.commit()

        # 記錄審計日誌
        _log_audit(
            db, member.member_id, "email_verification_success",
            "auth", request, "success"
        )

        return {
            "message": "Email verified successfully",
            "email": member.email,
            "verified_at": member.email_verified_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "email_verification_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email verification failed. Please try again."
        )


@router.post(
    "/resend-verification",
    summary="重新發送驗證郵件",
    description="為未驗證帳號重新發送驗證連結"
)
async def resend_verification(
    email_data: BaseModel,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    重新發送 Email 驗證連結

    Args:
        email_data: 包含 email 欄位
        request: FastAPI Request
        db: 資料庫 Session

    Returns:
        dict: 訊息

    Raises:
        HTTPException: 400 Email 不存在或已驗證
    """
    try:
        email = email_data.dict().get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is required"
            )

        # 查詢會員
        member = get_member_by_email(db, email)
        if not member:
            # 不透露 Email 是否存在 (安全考量)
            return {
                "message": "If the email exists, a verification link has been sent"
            }

        # 檢查是否已驗證
        if member.email_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already verified"
            )

        # 撤銷舊的驗證令牌
        old_tokens = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.member_id == member.member_id,
            EmailVerificationToken.token_type == "email_verification",
            EmailVerificationToken.used_at.is_(None)
        ).all()

        for token in old_tokens:
            token.mark_as_used()

        # 生成新的驗證令牌
        verification_token = generate_verification_token()
        verification_expires = datetime.utcnow() + timedelta(hours=24)

        new_token = EmailVerificationToken(
            member_id=member.member_id,
            token=hash_token(verification_token),
            token_type="email_verification",
            expires_at=verification_expires
        )
        db.add(new_token)
        db.commit()

        # TODO: 發送驗證郵件
        # send_verification_email(member.email, verification_token)

        # 記錄審計日誌
        _log_audit(
            db, member.member_id, "resend_verification_email",
            "auth", request, "success"
        )

        return {
            "message": "Verification email sent successfully",
            "email": member.email
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "resend_verification_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to send verification email"
        )


# ==================== 登入/登出端點 (W2-T003, W2-T009) ====================

class LoginRequest(BaseModel):
    """登入 Request Schema"""
    email: EmailStr
    password: str = Field(..., min_length=1, description="密碼")


class LoginResponse(BaseModel):
    """登入 Response Schema"""
    access_token: str
    refresh_token: str
    token_type: str = "Bearer"
    expires_in: int  # 秒數
    member: MemberResponse


@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Email 登入",
    description="使用 Email 和密碼登入，返回 JWT Token"
)
async def login(
    login_data: LoginRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    Email 登入

    Args:
        login_data: 登入資料 (Email + 密碼)
        request: FastAPI Request
        response: FastAPI Response (用於設定 Cookie)
        db: 資料庫 Session

    Returns:
        LoginResponse: Access Token, Refresh Token, 會員資訊

    Raises:
        HTTPException: 401 帳號或密碼錯誤, 403 帳號未啟用
    """
    try:
        # 查詢會員
        member = get_member_by_email(db, login_data.email)
        if not member:
            # 記錄失敗審計
            _log_audit(
                db, None, "login_failed_no_account",
                "auth", request, "failure",
                error_message=f"Email not found: {login_data.email}"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 驗證密碼
        if not verify_password(login_data.password, member.password_hash):
            # 記錄失敗審計
            _log_audit(
                db, member.member_id, "login_failed_wrong_password",
                "auth", request, "failure"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )

        # 檢查帳號狀態
        if not member.is_active:
            _log_audit(
                db, member.member_id, "login_failed_account_inactive",
                "auth", request, "failure",
                error_message=f"Account status: {member.account_status}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is {member.account_status}"
            )

        # 生成 JWT Tokens
        access_token = create_access_token(member.member_id, member.email)
        refresh_token = create_refresh_token(member.member_id, member.email)

        # 儲存 Refresh Token 到資料庫
        token_family = secrets.token_urlsafe(16)
        refresh_expires = datetime.utcnow() + timedelta(days=30)

        auth_token = AuthToken(
            member_id=member.member_id,
            token_hash=hash_token(refresh_token),
            token_family=token_family,
            device_info=request.headers.get("user-agent", "unknown")[:500],
            ip_address=_get_client_ip(request),
            expires_at=refresh_expires
        )
        db.add(auth_token)

        # 更新登入記錄
        member.last_login_at = datetime.utcnow()
        member.last_login_ip = _get_client_ip(request)
        member.login_count += 1

        db.commit()

        # 記錄成功審計
        _log_audit(
            db, member.member_id, "login_success",
            "auth", request, "success"
        )

        # 設定 HTTP-only Cookies (XSS 防護)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=True,  # HTTPS only
            samesite="lax",
            max_age=7 * 24 * 60 * 60  # 7 天
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=30 * 24 * 60 * 60  # 30 天
        )

        return LoginResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=7 * 24 * 60 * 60,
            member=member
        )

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "login_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed. Please try again."
        )


@router.post(
    "/logout",
    summary="登出",
    description="撤銷 Refresh Token 並清除 Cookies"
)
async def logout(
    request: Request,
    response: Response,
    current_member: dict = Depends(get_current_member),
    db: Session = Depends(get_db)
):
    """
    登出並撤銷 Token

    Args:
        request: FastAPI Request
        response: FastAPI Response
        current_member: 當前會員 (JWT payload)
        db: 資料庫 Session

    Returns:
        dict: 登出訊息

    Raises:
        HTTPException: 401 未授權
    """
    try:
        member_id = current_member["sub"]

        # 撤銷所有該會員的 Refresh Tokens (或只撤銷當前設備的)
        # 這裡我們撤銷所有 Token (強制所有設備登出)
        auth_tokens = db.query(AuthToken).filter(
            AuthToken.member_id == member_id,
            AuthToken.is_revoked == False
        ).all()

        for token in auth_tokens:
            token.revoke(reason="user_logout")

        db.commit()

        # 清除 Cookies
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

        # 記錄審計日誌
        _log_audit(
            db, member_id, "logout_success",
            "auth", request, "success"
        )

        return {
            "message": "Logged out successfully",
            "member_id": member_id
        }

    except Exception as e:
        db.rollback()
        _log_audit(
            db, current_member.get("sub"), "logout_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed. Please try again."
        )


# ==================== Refresh Token 端點 (W2-T005) ====================

class RefreshTokenRequest(BaseModel):
    """Refresh Token Request Schema"""
    refresh_token: str = Field(..., description="Refresh Token")


@router.post(
    "/refresh",
    summary="刷新 Access Token",
    description="使用 Refresh Token 換取新的 Access Token"
)
async def refresh_access_token(
    refresh_data: RefreshTokenRequest,
    request: Request,
    response: Response,
    db: Session = Depends(get_db)
):
    """
    使用 Refresh Token 換取新的 Access Token

    Args:
        refresh_data: Refresh Token
        request: FastAPI Request
        response: FastAPI Response
        db: 資料庫 Session

    Returns:
        dict: 新的 Access Token

    Raises:
        HTTPException: 401 Refresh Token 無效或已撤銷
    """
    try:
        # 驗證 Refresh Token
        payload = verify_token(refresh_data.refresh_token, "refresh")
        if payload is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )

        # 檢查 Token 是否在資料庫中且未撤銷
        token_hash = hash_token(refresh_data.refresh_token)
        auth_token = db.query(AuthToken).filter(
            AuthToken.token_hash == token_hash,
            AuthToken.member_id == payload["sub"]
        ).first()

        if not auth_token or not auth_token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token has been revoked"
            )

        # 生成新的 Access Token
        member_id = payload["sub"]
        member_email = payload["email"]
        new_access_token = create_access_token(member_id, member_email)

        # 更新 Token 最後使用時間
        auth_token.last_used_at = datetime.utcnow()
        db.commit()

        # 更新 Cookie
        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=7 * 24 * 60 * 60
        )

        # 記錄審計日誌
        _log_audit(
            db, member_id, "refresh_token_success",
            "auth", request, "success"
        )

        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 7 * 24 * 60 * 60
        }

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "refresh_token_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )


# ==================== 密碼找回端點 (W2-T008) ====================

class PasswordResetRequest(BaseModel):
    """密碼重設請求 Schema"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """密碼重設確認 Schema"""
    token: str = Field(..., min_length=32, description="重設令牌")
    new_password: str = Field(..., min_length=8, description="新密碼")

    @validator('new_password')
    def validate_new_password(cls, v):
        """驗證新密碼強度"""
        valid, message = validate_password_strength(v)
        if not valid:
            raise ValueError(message)
        return v


@router.post(
    "/reset-password",
    summary="請求密碼重設",
    description="發送密碼重設連結到 Email"
)
async def request_password_reset(
    reset_data: PasswordResetRequest,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    請求密碼重設 (發送重設連結)

    Args:
        reset_data: 包含 Email
        request: FastAPI Request
        db: 資料庫 Session

    Returns:
        dict: 訊息

    Note:
        為了安全，不論 Email 是否存在都返回成功訊息
    """
    try:
        # 查詢會員
        member = get_member_by_email(db, reset_data.email)
        if member:
            # 生成重設令牌
            reset_token = generate_verification_token()
            reset_expires = datetime.utcnow() + timedelta(hours=1)  # 1 小時有效

            # 撤銷舊的重設令牌
            old_tokens = db.query(EmailVerificationToken).filter(
                EmailVerificationToken.member_id == member.member_id,
                EmailVerificationToken.token_type == "password_reset",
                EmailVerificationToken.used_at.is_(None)
            ).all()

            for token in old_tokens:
                token.mark_as_used()

            # 建立新令牌
            new_token = EmailVerificationToken(
                member_id=member.member_id,
                token=hash_token(reset_token),
                token_type="password_reset",
                expires_at=reset_expires
            )
            db.add(new_token)
            db.commit()

            # TODO: 發送重設郵件
            # send_password_reset_email(member.email, reset_token)

            # 記錄審計日誌
            _log_audit(
                db, member.member_id, "password_reset_requested",
                "auth", request, "success"
            )

        # 始終返回成功訊息 (不透露 Email 是否存在)
        return {
            "message": "If the email exists, a password reset link has been sent"
        }

    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "password_reset_request_error",
            "auth", request, "error",
            error_message=str(e)
        )
        # 仍返回成功訊息 (避免透露資訊)
        return {
            "message": "If the email exists, a password reset link has been sent"
        }


@router.post(
    "/reset-password/confirm",
    summary="確認密碼重設",
    description="使用令牌重設密碼"
)
async def confirm_password_reset(
    confirm_data: PasswordResetConfirm,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    確認密碼重設 (使用令牌設定新密碼)

    Args:
        confirm_data: 包含令牌和新密碼
        request: FastAPI Request
        db: 資料庫 Session

    Returns:
        dict: 成功訊息

    Raises:
        HTTPException: 400 令牌無效或已過期
    """
    try:
        # 查詢重設令牌
        token_hash = hash_token(confirm_data.token)
        reset_token = db.query(EmailVerificationToken).filter(
            EmailVerificationToken.token == token_hash,
            EmailVerificationToken.token_type == "password_reset"
        ).first()

        if not reset_token or not reset_token.is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired password reset token"
            )

        # 取得會員
        member = get_member_by_id(db, reset_token.member_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Member not found"
            )

        # 更新密碼
        from utils.auth_utils import hash_password
        member.password_hash = hash_password(confirm_data.new_password)

        # 標記令牌為已使用
        reset_token.mark_as_used()

        # 撤銷所有 Refresh Tokens (強制重新登入)
        auth_tokens = db.query(AuthToken).filter(
            AuthToken.member_id == member.member_id,
            AuthToken.is_revoked == False
        ).all()

        for token in auth_tokens:
            token.revoke(reason="password_reset")

        db.commit()

        # 記錄審計日誌
        _log_audit(
            db, member.member_id, "password_reset_success",
            "auth", request, "success"
        )

        return {
            "message": "Password reset successfully",
            "email": member.email
        }

    except HTTPException:
        raise
    except ValueError as e:
        # 密碼強度驗證失敗
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        _log_audit(
            db, None, "password_reset_confirm_error",
            "auth", request, "error",
            error_message=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password reset failed. Please try again."
        )


# ==================== 會員資訊端點 ====================

@router.put(
    "/{member_id}",
    response_model=MemberResponse,
    summary="更新會員資訊",
    description="更新會員個人檔案"
)
async def update_member(
    member_id: str,
    member_data: MemberUpdate,
    db: Session = Depends(get_db)
):
    """
    更新會員資訊

    Args:
        member_id: 會員 ID
        member_data: 更新資料
        db: 資料庫 Session

    Returns:
        MemberResponse: 更新後的會員資訊

    Raises:
        HTTPException: 404 會員不存在
    """
    # TODO: Week 3 實作
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not implemented yet (Week 3)"
    )


@router.delete(
    "/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="刪除會員",
    description="軟刪除會員 (GDPR 合規)"
)
async def delete_member(
    member_id: str,
    db: Session = Depends(get_db)
):
    """
    刪除會員 (軟刪除)

    Args:
        member_id: 會員 ID
        db: 資料庫 Session

    Returns:
        None (204 No Content)

    Raises:
        HTTPException: 404 會員不存在
    """
    # TODO: Week 3 實作
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint not implemented yet (Week 3)"
    )


# ==================== 統計與搜尋端點 ====================

@router.get(
    "/stats/count",
    summary="會員統計",
    description="取得會員數量統計"
)
async def get_member_stats(
    account_status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    會員統計

    Args:
        account_status: 篩選帳號狀態
        db: 資料庫 Session

    Returns:
        dict: 統計資訊
    """
    # TODO: 實作統計邏輯
    return {
        "total": 0,
        "active": 0,
        "suspended": 0,
        "deleted": 0
    }


@router.get(
    "/search",
    response_model=List[MemberResponse],
    summary="搜尋會員",
    description="根據姓名搜尋會員"
)
async def search_members(
    q: str,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    搜尋會員

    Args:
        q: 搜尋關鍵字
        limit: 限制筆數
        db: 資料庫 Session

    Returns:
        List[MemberResponse]: 符合的會員清單
    """
    # TODO: 實作搜尋邏輯
    return []


# ==================== 錯誤處理範例 ====================

class ErrorResponse(BaseModel):
    """錯誤 Response Schema"""
    error: str
    detail: str
    timestamp: datetime


@router.get("/error-example", include_in_schema=False)
async def error_example():
    """錯誤處理範例 (不包含在 API 文檔中)"""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="This is an example error response"
    )


# ==================== 輔助函式 ====================

def _log_audit(
    db: Session,
    member_id: Optional[str],
    action: str,
    action_category: str,
    request: Request,
    status: str,
    error_message: Optional[str] = None,
    extra_data: Optional[dict] = None
):
    """
    記錄審計日誌

    Args:
        db: 資料庫 Session
        member_id: 會員 ID (可為 None)
        action: 操作動作
        action_category: 操作類別 (auth/profile/assessment/admin)
        request: FastAPI Request
        status: 狀態 (success/failure/error)
        error_message: 錯誤訊息 (optional)
        extra_data: 額外資料 (optional)
    """
    try:
        audit_log = AuditLog(
            member_id=member_id,
            action=action,
            action_category=action_category,
            ip_address=request.client.host if request.client else "unknown",
            user_agent=request.headers.get("user-agent", "unknown")[:500],
            request_method=request.method,
            request_path=str(request.url.path),
            status=status,
            error_message=error_message,
            extra_data=extra_data
        )
        db.add(audit_log)
        db.commit()
    except Exception as e:
        # 審計日誌失敗不應影響主流程
        print(f"Failed to log audit: {e}")
        db.rollback()


def _get_client_ip(request: Request) -> str:
    """
    取得客戶端 IP 位址 (支援反向代理)

    Args:
        request: FastAPI Request

    Returns:
        str: IP 位址
    """
    # 檢查反向代理 Header
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()

    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # 直接連線
    return request.client.host if request.client else "unknown"


# ==================== 路由資訊 ====================

def get_router_info():
    """取得路由資訊 (用於測試)"""
    return {
        "prefix": router.prefix,
        "tags": router.tags,
        "routes_count": len(router.routes)
    }
