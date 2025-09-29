"""
Pytest 配置檔案 - Gallup 優勢測驗專案
提供全專案共用的測試設備與配置

遵循 structure_guide.md 測試架構設計
"""

import pytest
import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import Mock
import sys
import os

# 添加 src 路徑到 Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "main" / "python"))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from api.main import app
from utils.database import get_db, Base
from models.database import *  # Import all ORM models


# ========================
# 測試資料庫設備
# ========================

@pytest.fixture(scope="session")
def temp_db_path() -> Generator[str, None, None]:
    """建立暫時資料庫檔案路徑"""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        yield tmp.name
    # 清理：測試結束後刪除暫時資料庫
    if os.path.exists(tmp.name):
        os.unlink(tmp.name)


@pytest.fixture(scope="session")
def test_engine(temp_db_path: str):
    """建立測試專用 SQLite 引擎"""
    engine = create_engine(
        f"sqlite:///{temp_db_path}",
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool,
        echo=False  # 設為 True 可看到 SQL 語句除錯
    )

    # 建立所有資料表
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理：關閉引擎
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_engine) -> Generator[Session, None, None]:
    """為每個測試函式提供獨立的資料庫會話"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine
    )

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()  # 確保測試間隔離
        session.close()


@pytest.fixture(scope="function")
def override_get_db(test_db_session: Session):
    """覆寫 FastAPI 的資料庫依賴"""
    def _override_get_db():
        try:
            yield test_db_session
        finally:
            pass  # session cleanup handled by test_db_session fixture

    return _override_get_db


# ========================
# API 測試設備
# ========================

@pytest.fixture(scope="function")
def client(override_get_db) -> TestClient:
    """FastAPI 測試客戶端"""
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    # 清理：移除依賴覆寫
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
async def async_client(override_get_db):
    """異步 HTTP 測試客戶端 (未來使用)"""
    app.dependency_overrides[get_db] = override_get_db

    # 此處可使用 httpx.AsyncClient 進行異步測試
    # 暫時保留基本結構
    pass


# ========================
# 測試資料設備
# ========================

@pytest.fixture
def sample_consent_data():
    """標準同意資料"""
    return {
        "agreed": True,
        "ip_address": "192.168.1.100",
        "user_agent": "Mozilla/5.0 (Test Browser)",
        "timestamp": "2025-09-30T10:00:00Z"
    }


@pytest.fixture
def sample_assessment_responses():
    """標準測驗回答資料 (高外向性檔案)"""
    return {
        "session_id": "test_session_123",
        "responses": [
            {"question_id": 1, "response": 7},   # 外向：我是聚會的靈魂人物
            {"question_id": 2, "response": 1},   # 外向：我話不多 (反向題)
            {"question_id": 3, "response": 7},   # 外向：我在人群中感到自在
            {"question_id": 4, "response": 2},   # 外向：我保持低調 (反向題)
            {"question_id": 5, "response": 6},   # 和善：我能感受他人情緒
            {"question_id": 6, "response": 2},   # 和善：我對他人不感興趣 (反向題)
            {"question_id": 7, "response": 5},   # 和善：我感受他人情緒
            {"question_id": 8, "response": 3},   # 和善：我對他人問題不感興趣 (反向題)
            {"question_id": 9, "response": 6},   # 嚴謹：我總是有備而來
            {"question_id": 10, "response": 3},  # 嚴謹：我把東西四處亂放 (反向題)
            {"question_id": 11, "response": 5},  # 嚴謹：我注意細節
            {"question_id": 12, "response": 4},  # 嚴謹：我把事情搞得一團糟 (反向題)
            {"question_id": 13, "response": 4},  # 神經質：我容易感到壓力
            {"question_id": 14, "response": 2},  # 神經質：我大部分時間都很放鬆 (反向題)
            {"question_id": 15, "response": 3},  # 神經質：我很容易擔心
            {"question_id": 16, "response": 1},  # 神經質：我很少感到憂鬱 (反向題)
            {"question_id": 17, "response": 5},  # 開放性：我詞彙豐富
            {"question_id": 18, "response": 3},  # 開放性：我難以理解抽象概念 (反向題)
            {"question_id": 19, "response": 2},  # 開放性：我對抽象概念不感興趣 (反向題)
            {"question_id": 20, "response": 1}   # 開放性：我沒有好的想像力 (反向題)
        ]
    }


@pytest.fixture
def expected_big_five_scores():
    """預期的 Big Five 分數 (對應 sample_assessment_responses)"""
    return {
        "extraversion": 85,      # 高分：7+7+1+6 = 21/28 → 75% + 調整
        "agreeableness": 65,     # 中高分：6+5+5+4 = 20/28 → 71%
        "conscientiousness": 70, # 中高分：6+5+4+3 = 18/28 → 64% + 調整
        "neuroticism": 35,       # 低分：4+6+3+7 = 20/28 → 71% → 29% (反轉)
        "openness": 60           # 中分：5+4+5+6 = 20/28 → 71%
    }


@pytest.fixture
def sample_strengths_mapping():
    """預期的優勢面向映射結果"""
    return {
        "top_strengths": [
            {
                "name": "影響與倡議",
                "score": 78,
                "confidence": "high",
                "primary_factor": "extraversion",
                "description": "能夠影響他人並推動倡議"
            },
            {
                "name": "協作與共好",
                "score": 72,
                "confidence": "medium",
                "primary_factor": "agreeableness",
                "description": "擅長團隊合作與促進共同利益"
            },
            {
                "name": "品質與完備",
                "score": 68,
                "confidence": "medium",
                "primary_factor": "conscientiousness",
                "description": "追求品質與工作完整性"
            }
        ],
        "bottom_strengths": [
            {
                "name": "壓力調節",
                "score": 42,
                "confidence": "medium",
                "primary_factor": "neuroticism_reversed",
                "description": "需要加強壓力管理技能"
            }
        ]
    }


# ========================
# Mock 物件設備
# ========================

@pytest.fixture
def mock_pdf_generator():
    """Mock PDF 生成器"""
    mock = Mock()
    mock.generate_report.return_value = b"fake_pdf_content"
    mock.generation_time = 0.5  # 模擬生成時間
    return mock


@pytest.fixture
def mock_email_service():
    """Mock 郵件服務 (未來功能)"""
    mock = Mock()
    mock.send_report.return_value = True
    return mock


# ========================
# 效能測試設備
# ========================

@pytest.fixture
def performance_benchmarks():
    """效能測試基準值"""
    return {
        "scoring_latency_ms": 10,      # 計分延遲上限
        "api_response_ms": 200,        # API 回應時間上限
        "pdf_generation_s": 1.0,       # PDF 生成時間上限
        "concurrent_users": 100        # 並發使用者數量
    }


# ========================
# 測試標記配置
# ========================

def pytest_configure(config):
    """註冊自定義測試標記"""
    config.addinivalue_line(
        "markers", "slow: 標記慢速測試 (>1秒)"
    )
    config.addinivalue_line(
        "markers", "integration: 標記整合測試"
    )
    config.addinivalue_line(
        "markers", "e2e: 標記端到端測試"
    )
    config.addinivalue_line(
        "markers", "performance: 標記效能測試"
    )
    config.addinivalue_line(
        "markers", "security: 標記安全測試"
    )


# ========================
# 測試資料清理
# ========================

@pytest.fixture(autouse=True)
def cleanup_test_data(test_db_session):
    """自動清理每個測試的資料"""
    yield
    # 測試後清理：確保資料表乾淨
    for table in reversed(Base.metadata.sorted_tables):
        test_db_session.execute(table.delete())
    test_db_session.commit()


# ========================
# 日誌配置
# ========================

@pytest.fixture(autouse=True)
def configure_test_logging():
    """配置測試環境日誌"""
    import logging

    # 測試期間降低日誌等級，避免干擾
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    yield

    # 恢復預設日誌等級
    logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.INFO)


# ========================
# 平行測試配置
# ========================

def pytest_collection_modifyitems(config, items):
    """修改測試項目，添加自動標記"""
    for item in items:
        # 自動標記慢速測試
        if "slow" in item.keywords:
            item.add_marker(pytest.mark.slow)

        # 自動標記整合測試
        if "integration" in item.fspath.basename:
            item.add_marker(pytest.mark.integration)

        # 自動標記 e2e 測試
        if "e2e" in item.fspath.basename:
            item.add_marker(pytest.mark.e2e)


# ========================
# 異步支援
# ========================

@pytest.fixture(scope="session")
def event_loop():
    """為異步測試提供 event loop"""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop

    loop.close()