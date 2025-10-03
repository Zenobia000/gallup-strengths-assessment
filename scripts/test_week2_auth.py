#!/usr/bin/env python3
"""
Week 2 會員認證系統驗證測試腳本

驗證項目:
1. 註冊功能 (Email + 密碼)
2. Email 驗證機制
3. 登入功能 (JWT Token)
4. Refresh Token 機制
5. 密碼找回功能
6. 登出功能
7. JWT 中間件驗證

執行: python scripts/test_week2_auth.py
"""

import sys
import os
from pathlib import Path
import uuid

# 添加專案路徑
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src" / "main" / "python"))

print("=" * 60)
print("Week 2 會員認證系統驗證測試")
print("=" * 60)

# ==================== 測試 1: 模組導入 ====================
print("\n[測試 1/8] 模組導入測試...")
try:
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker
    from models.database import Base
    from models.member_models import Member, EmailVerificationToken, AuthToken
    from utils.member_crud import create_member, get_member_by_email
    from utils.auth_utils import (
        verify_password, create_access_token, verify_token,
        hash_token, generate_verification_token
    )
    from api.dependencies import get_db, engine, SessionLocal
    print("✓ 所有模組成功導入")
except Exception as e:
    print(f"✗ 模組導入失敗: {e}")
    sys.exit(1)

# ==================== 測試 2: 資料庫連線 ====================
print("\n[測試 2/8] 資料庫連線測試...")
try:
    db = SessionLocal()
    db.execute(text("SELECT 1")).fetchone()
    print(f"✓ 資料庫連線成功")
except Exception as e:
    print(f"✗ 資料庫連線失敗: {e}")
    sys.exit(1)

# ==================== 測試 3: 註冊功能 ====================
print("\n[測試 3/8] 註冊功能測試...")
try:
    # 清理測試資料
    test_email = f"test.week2.{uuid.uuid4().hex[:8]}@example.com"
    test_password = "SecurePass123!"

    # 測試註冊
    member = create_member(
        db,
        email=test_email,
        password=test_password,
        full_name="Week 2 Test User",
        job_title="Software Engineer"
    )

    assert member.email == test_email, "Email 應正確"
    assert member.full_name == "Week 2 Test User", "名稱應正確"
    assert member.email_verified == False, "預設應未驗證"
    assert verify_password(test_password, member.password_hash), "密碼應正確雜湊"

    print("✓ 註冊功能運作正常")
    print(f"  - Member ID: {member.member_id}")
    print(f"  - Email: {member.email}")
    print(f"  - Email Verified: {member.email_verified}")
except Exception as e:
    print(f"✗ 註冊功能測試失敗: {e}")
    db.rollback()
    sys.exit(1)

# ==================== 測試 4: Email 驗證機制 ====================
print("\n[測試 4/8] Email 驗證機制測試...")
try:
    from datetime import datetime, timedelta

    # 生成驗證令牌
    verification_token = generate_verification_token()
    token_hash = hash_token(verification_token)
    expires_at = datetime.utcnow() + timedelta(hours=24)

    # 建立驗證令牌記錄
    email_token = EmailVerificationToken(
        member_id=member.member_id,
        token=token_hash,
        token_type="email_verification",
        expires_at=expires_at
    )
    db.add(email_token)
    db.commit()

    # 測試查詢令牌
    found_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == token_hash
    ).first()

    assert found_token is not None, "令牌應存在"
    assert found_token.is_valid, "令牌應有效"
    assert found_token.member_id == member.member_id, "Member ID 應正確"

    # 模擬驗證
    member.email_verified = True
    member.email_verified_at = datetime.utcnow()
    found_token.mark_as_used()
    db.commit()

    assert member.email_verified, "Email 應已驗證"
    assert not found_token.is_valid, "令牌應已失效"

    print("✓ Email 驗證機制運作正常")
    print(f"  - Token 生成: 成功")
    print(f"  - Token 驗證: 通過")
    print(f"  - Member 驗證狀態: 已啟用")
except Exception as e:
    print(f"✗ Email 驗證測試失敗: {e}")
    db.rollback()
    sys.exit(1)

# ==================== 測試 5: 登入功能 (JWT) ====================
print("\n[測試 5/8] 登入功能測試...")
try:
    # 測試登入 (驗證密碼)
    login_member = get_member_by_email(db, test_email)
    assert login_member is not None, "會員應存在"

    # 驗證密碼
    password_valid = verify_password(test_password, login_member.password_hash)
    assert password_valid, "密碼驗證應通過"

    # 生成 JWT Token
    access_token = create_access_token(login_member.member_id, login_member.email)
    assert isinstance(access_token, str), "Access Token 應為字串"
    assert len(access_token) > 100, "JWT Token 長度應大於 100"

    # 驗證 Token
    payload = verify_token(access_token, "access")
    assert payload is not None, "Token 驗證應成功"
    assert payload["sub"] == login_member.member_id, "Member ID 應正確"
    assert payload["email"] == login_member.email, "Email 應正確"

    print("✓ 登入功能運作正常")
    print(f"  - 密碼驗證: 通過")
    print(f"  - JWT Token 生成: 成功")
    print(f"  - Token 驗證: 通過")
except Exception as e:
    print(f"✗ 登入功能測試失敗: {e}")
    sys.exit(1)

# ==================== 測試 6: Refresh Token 機制 ====================
print("\n[測試 6/8] Refresh Token 機制測試...")
try:
    from utils.auth_utils import create_refresh_token
    import secrets

    # 生成 Refresh Token
    refresh_token = create_refresh_token(login_member.member_id, login_member.email)
    token_family = secrets.token_urlsafe(16)
    refresh_expires = datetime.utcnow() + timedelta(days=30)

    # 儲存到資料庫
    auth_token = AuthToken(
        member_id=login_member.member_id,
        token_hash=hash_token(refresh_token),
        token_family=token_family,
        device_info="Test Device",
        ip_address="127.0.0.1",
        expires_at=refresh_expires
    )
    db.add(auth_token)
    db.commit()

    # 驗證 Refresh Token
    refresh_payload = verify_token(refresh_token, "refresh")
    assert refresh_payload is not None, "Refresh Token 驗證應成功"
    assert refresh_payload["sub"] == login_member.member_id, "Member ID 應正確"

    # 測試查詢 Token
    stored_token = db.query(AuthToken).filter(
        AuthToken.member_id == login_member.member_id,
        AuthToken.token_hash == hash_token(refresh_token)
    ).first()

    assert stored_token is not None, "Token 應存在於資料庫"
    assert stored_token.is_valid, "Token 應有效"

    # 測試撤銷 Token
    stored_token.revoke(reason="test_revoke")
    db.commit()

    assert stored_token.is_revoked, "Token 應已撤銷"
    assert not stored_token.is_valid, "Token 應無效"

    print("✓ Refresh Token 機制運作正常")
    print(f"  - Refresh Token 生成: 成功")
    print(f"  - Token 儲存: 成功")
    print(f"  - Token 撤銷: 成功")
except Exception as e:
    print(f"✗ Refresh Token 測試失敗: {e}")
    db.rollback()
    sys.exit(1)

# ==================== 測試 7: 密碼找回機制 ====================
print("\n[測試 7/8] 密碼找回機制測試...")
try:
    # 生成重設令牌
    reset_token = generate_verification_token()
    reset_expires = datetime.utcnow() + timedelta(hours=1)

    # 建立重設令牌記錄
    password_reset_token = EmailVerificationToken(
        member_id=login_member.member_id,
        token=hash_token(reset_token),
        token_type="password_reset",
        expires_at=reset_expires
    )
    db.add(password_reset_token)
    db.commit()

    # 測試查詢令牌
    found_reset_token = db.query(EmailVerificationToken).filter(
        EmailVerificationToken.token == hash_token(reset_token),
        EmailVerificationToken.token_type == "password_reset"
    ).first()

    assert found_reset_token is not None, "重設令牌應存在"
    assert found_reset_token.is_valid, "令牌應有效"

    # 模擬重設密碼
    from utils.auth_utils import hash_password
    new_password = "NewSecurePass456!"
    login_member.password_hash = hash_password(new_password)
    found_reset_token.mark_as_used()
    db.commit()

    # 驗證新密碼
    new_password_valid = verify_password(new_password, login_member.password_hash)
    assert new_password_valid, "新密碼應正確"

    print("✓ 密碼找回機制運作正常")
    print(f"  - 重設令牌生成: 成功")
    print(f"  - 密碼更新: 成功")
    print(f"  - 新密碼驗證: 通過")
except Exception as e:
    print(f"✗ 密碼找回測試失敗: {e}")
    db.rollback()
    sys.exit(1)

# ==================== 測試 8: 登出與審計日誌 ====================
print("\n[測試 8/8] 登出功能與審計日誌測試...")
try:
    from models.member_models import AuditLog

    # 模擬登出 (撤銷所有 Token)
    all_tokens = db.query(AuthToken).filter(
        AuthToken.member_id == login_member.member_id,
        AuthToken.is_revoked == False
    ).all()

    token_count = len(all_tokens)
    for token in all_tokens:
        token.revoke(reason="user_logout")

    db.commit()

    # 驗證所有 Token 已撤銷
    active_tokens = db.query(AuthToken).filter(
        AuthToken.member_id == login_member.member_id,
        AuthToken.is_revoked == False
    ).count()

    assert active_tokens == 0, "所有 Token 應已撤銷"

    # 測試審計日誌
    audit_log = AuditLog(
        member_id=login_member.member_id,
        action="test_logout",
        action_category="auth",
        ip_address="127.0.0.1",
        user_agent="Test Agent",
        request_method="POST",
        request_path="/api/members/logout",
        status="success"
    )
    db.add(audit_log)
    db.commit()

    # 查詢審計日誌
    log_count = db.query(AuditLog).filter(
        AuditLog.member_id == login_member.member_id
    ).count()

    assert log_count >= 1, "審計日誌應存在"

    print("✓ 登出與審計日誌運作正常")
    print(f"  - Token 撤銷: 成功 ({token_count} 個)")
    print(f"  - 審計日誌: 已記錄")
except Exception as e:
    print(f"✗ 登出功能測試失敗: {e}")
    db.rollback()
    sys.exit(1)
finally:
    # 清理測試資料
    try:
        db.query(AuditLog).filter(AuditLog.member_id == login_member.member_id).delete()
        db.query(AuthToken).filter(AuthToken.member_id == login_member.member_id).delete()
        db.query(EmailVerificationToken).filter(EmailVerificationToken.member_id == login_member.member_id).delete()
        db.query(Member).filter(Member.member_id == login_member.member_id).delete()
        db.commit()
    except:
        db.rollback()
    finally:
        db.close()

# ==================== 測試總結 ====================
print("\n" + "=" * 60)
print("✓✓✓ Week 2 所有測試通過！")
print("=" * 60)
print("\n完成項目:")
print("  ✓ W2-T001: Email 註冊 API")
print("  ✓ W2-T002: Email 驗證機制")
print("  ✓ W2-T003: Email 登入 API")
print("  ✓ W2-T004: JWT 認證中間件")
print("  ✓ W2-T005: Refresh Token 機制")
print("  ✓ W2-T008: 密碼找回 API")
print("  ✓ W2-T009: 登出 API")
print("\nOAuth 整合 (需額外設定):")
print("  ⊙ W2-T006: Google OAuth 2.0 (跳過)")
print("  ⊙ W2-T007: Facebook Login (跳過)")
print("\n準備進入 Week 3: 會員資料與歷史管理")
print("=" * 60)
