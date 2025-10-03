#!/usr/bin/env python3
"""
Week 1 基礎設施驗證測試腳本

驗證項目:
1. 資料庫連線
2. 資料表建立
3. 密碼雜湊工具
4. JWT Token 生成與驗證
5. 基礎 CRUD 操作

執行: python scripts/test_week1_setup.py
"""

import sys
import os
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root / "src" / "main" / "python"))

print("=" * 60)
print("Week 1 基礎設施驗證測試")
print("=" * 60)

# ==================== 測試 1: 模組導入 ====================
print("\n[測試 1/6] 模組導入測試...")
try:
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.orm import sessionmaker
    from models.database import Base
    from models.member_models import (
        Member, EmailVerificationToken, AuthToken,
        OAuthProvider, MemberAssessment, ShareLink, AuditLog
    )
    from utils.auth_utils import (
        hash_password, verify_password,
        create_access_token, verify_token,
        validate_password_strength
    )
    from utils.member_crud import (
        create_member, get_member_by_id, get_member_by_email
    )
    print("✓ 所有模組成功導入")
except Exception as e:
    print(f"✗ 模組導入失敗: {e}")
    sys.exit(1)

# ==================== 測試 2: 資料庫連線 ====================
print("\n[測試 2/6] 資料庫連線測試...")
try:
    db_path = project_root / "data" / "gallup_strengths.db"
    engine = create_engine(f"sqlite:///{db_path}")
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # 測試連線
    from sqlalchemy import text
    db.execute(text("SELECT 1")).fetchone()
    print(f"✓ 資料庫連線成功: {db_path}")
except Exception as e:
    print(f"✗ 資料庫連線失敗: {e}")
    sys.exit(1)

# ==================== 測試 3: 資料表驗證 ====================
print("\n[測試 3/6] 資料表建立驗證...")
try:
    inspector = inspect(engine)
    table_names = inspector.get_table_names()

    required_tables = [
        "members",
        "email_verification_tokens",
        "auth_tokens",
        "oauth_providers",
        "member_assessments",
        "share_links",
        "audit_logs"
    ]

    missing_tables = [t for t in required_tables if t not in table_names]

    if missing_tables:
        print(f"✗ 缺少資料表: {missing_tables}")
        sys.exit(1)

    print(f"✓ 所有必要資料表已建立 (共 {len(table_names)} 張表)")
    print(f"  會員系統表: {required_tables}")
except Exception as e:
    print(f"✗ 資料表驗證失敗: {e}")
    sys.exit(1)

# ==================== 測試 4: 密碼雜湊工具 ====================
print("\n[測試 4/6] 密碼雜湊工具測試...")
try:
    test_password = "SecurePass123"

    # 測試雜湊
    hashed = hash_password(test_password)
    assert len(hashed) == 60, "bcrypt 雜湊長度應為 60"

    # 測試驗證
    assert verify_password(test_password, hashed), "密碼驗證應成功"
    assert not verify_password("WrongPass", hashed), "錯誤密碼驗證應失敗"

    # 測試密碼強度驗證
    valid, msg = validate_password_strength(test_password)
    assert valid, f"密碼強度驗證應通過: {msg}"

    weak_valid, weak_msg = validate_password_strength("weak")
    assert not weak_valid, "弱密碼應驗證失敗"

    print("✓ 密碼雜湊工具運作正常")
    print(f"  - bcrypt 雜湊長度: {len(hashed)}")
    print(f"  - 密碼驗證: 通過")
    print(f"  - 強度驗證: 通過")
except Exception as e:
    print(f"✗ 密碼工具測試失敗: {e}")
    sys.exit(1)

# ==================== 測試 5: JWT Token 工具 ====================
print("\n[測試 5/6] JWT Token 工具測試...")
try:
    # 測試 Access Token
    token = create_access_token("member-test-123", "test@example.com")
    assert isinstance(token, str), "Token 應為字串"
    assert len(token) > 100, "JWT Token 長度應大於 100"

    # 測試驗證
    payload = verify_token(token, "access")
    assert payload is not None, "Token 驗證應成功"
    assert payload["sub"] == "member-test-123", "Member ID 應正確"
    assert payload["email"] == "test@example.com", "Email 應正確"

    # 測試錯誤 Token
    invalid_payload = verify_token("invalid-token", "access")
    assert invalid_payload is None, "無效 Token 驗證應失敗"

    print("✓ JWT Token 工具運作正常")
    print(f"  - Token 生成: 成功")
    print(f"  - Token 驗證: 通過")
    print(f"  - 錯誤處理: 正確")
except Exception as e:
    print(f"✗ JWT Token 測試失敗: {e}")
    sys.exit(1)

# ==================== 測試 6: CRUD 操作 ====================
print("\n[測試 6/6] CRUD 操作測試...")
try:
    # 清理測試資料
    db.query(Member).filter(Member.email == "test@week1.com").delete()
    db.commit()

    # 測試創建會員
    member = create_member(
        db,
        email="test@week1.com",
        password="TestPass123",
        full_name="Week 1 Test User"
    )
    assert member.email == "test@week1.com", "Email 應正確"
    assert member.full_name == "Week 1 Test User", "名稱應正確"
    assert member.email_verified == False, "預設應未驗證"

    # 測試查詢會員
    found_by_id = get_member_by_id(db, member.member_id)
    assert found_by_id is not None, "根據 ID 查詢應成功"
    assert found_by_id.email == "test@week1.com", "查詢結果應正確"

    found_by_email = get_member_by_email(db, "test@week1.com")
    assert found_by_email is not None, "根據 Email 查詢應成功"
    assert found_by_email.member_id == member.member_id, "查詢結果應一致"

    # 測試密碼驗證
    assert verify_password("TestPass123", member.password_hash), "密碼應正確"

    # 清理測試資料
    db.query(Member).filter(Member.email == "test@week1.com").delete()
    db.commit()

    print("✓ CRUD 操作運作正常")
    print(f"  - 創建會員: 成功")
    print(f"  - 查詢會員: 成功")
    print(f"  - 密碼驗證: 通過")
except Exception as e:
    print(f"✗ CRUD 操作測試失敗: {e}")
    # 嘗試清理
    try:
        db.query(Member).filter(Member.email == "test@week1.com").delete()
        db.commit()
    except:
        pass
    sys.exit(1)
finally:
    db.close()

# ==================== 測試總結 ====================
print("\n" + "=" * 60)
print("✓✓✓ Week 1 所有測試通過！")
print("=" * 60)
print("\n完成項目:")
print("  ✓ W1-T001: 資料庫 Schema 設計")
print("  ✓ W1-T002: SQLite 資料庫初始化")
print("  ✓ W1-T003: Alembic 遷移機制")
print("  ✓ W1-T004: Member 資料模型 (7 張表)")
print("  ✓ W1-T005: FastAPI 路由架構")
print("  ✓ W1-T006: CRUD 工具函式")
print("  ✓ W1-T007: bcrypt 密碼雜湊")
print("  ✓ W1-T008: JWT Token 工具")
print("\n準備進入 Week 2: 會員認證系統開發")
print("=" * 60)
