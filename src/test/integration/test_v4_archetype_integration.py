"""
Integration Test for V4 API with Career Archetype System

測試 v4 API 與職業原型系統的整合：
- 完整的評測流程
- 職業原型分析
- 前端資料格式驗證
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from fastapi.testclient import TestClient
from api.routes.v4_assessment import router
from fastapi import FastAPI

# 建立測試用的 FastAPI 應用
app = FastAPI()
app.include_router(router)
client = TestClient(app)


@pytest.fixture
def temp_database():
    """建立臨時資料庫用於測試"""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.db') as f:
        temp_db_path = f.name

    yield temp_db_path

    # 清理
    if os.path.exists(temp_db_path):
        os.unlink(temp_db_path)


@pytest.fixture
def setup_test_database(temp_database):
    """設定測試資料庫"""
    # 這裡需要初始化資料庫結構和基礎資料
    import sqlite3
    from utils.migrations.migration_004_career_archetypes import apply_migration

    conn = sqlite3.connect(temp_database)
    conn.execute('PRAGMA foreign_keys=ON')

    try:
        # 建立基礎表格
        conn.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT
            )
        ''')

        # 建立 v4 相關表格
        conn.execute('''
            CREATE TABLE IF NOT EXISTS v4_sessions (
                session_id TEXT PRIMARY KEY,
                blocks_data TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        conn.execute('''
            CREATE TABLE IF NOT EXISTS v4_assessment_results (
                session_id TEXT PRIMARY KEY,
                responses TEXT,
                theta_scores TEXT,
                norm_scores TEXT,
                profile TEXT,
                completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 套用職業原型遷移
        apply_migration(conn)
        conn.commit()

        yield temp_database

    finally:
        conn.close()


class TestV4ArchetypeIntegration:
    """測試 v4 API 與職業原型系統整合"""

    @patch('api.routes.v4_assessment.get_database_manager')
    def test_get_results_with_archetype_analysis(self, mock_db_manager):
        """測試獲取結果時包含職業原型分析"""
        # Mock 資料庫回應
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Mock v4_assessment_results 查詢
        mock_cursor.fetchone.return_value = [
            json.dumps([]),  # responses
            json.dumps({     # theta_scores
                'T1': 1.2, 'T2': 0.8, 'T3': 0.5, 'T4': 1.5,
                'T5': 0.3, 'T6': 0.7, 'T7': 0.2, 'T8': 1.0,
                'T9': 1.1, 'T10': 0.1, 'T11': -0.2, 'T12': 1.3
            }),
            json.dumps({}),  # norm_scores
            json.dumps({}),  # profile
            '2025-10-01 10:30:00'  # completed_at
        ]

        # Mock 職業原型相關查詢
        mock_cursor.fetchone.side_effect = [
            # 第一次：v4_assessment_results
            [
                json.dumps([]),
                json.dumps({
                    'T1': 1.2, 'T4': 1.5, 'T12': 1.3  # 高分才幹，應該對應 ARCHITECT
                }),
                json.dumps({}),
                json.dumps({}),
                '2025-10-01 10:30:00'
            ],
            # 第二次：career_archetypes (在 archetype_service 中)
            {
                'archetype_id': 'ARCHITECT',
                'archetype_name': '系統建構者',
                'archetype_name_en': 'System Architect',
                'keirsey_temperament': '理性者 (Rational)',
                'description': '天生的系統思考者與建構者',
                'mbti_correlates': '["INTJ", "INTP"]',
                'core_characteristics': '["系統性思維"]',
                'work_environment_preferences': '{}',
                'leadership_style': '策略型領導',
                'decision_making_style': '理性決策',
                'communication_style': '直接簡潔',
                'stress_indicators': '[]',
                'development_areas': '[]'
            }
        ]

        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        # 發送請求
        response = client.get("/api/v4/assessment/results/test_session_123")

        # 驗證回應
        assert response.status_code == 200
        data = response.json()

        # 驗證基本結果
        assert data["session_id"] == "test_session_123"
        assert "theta_scores" in data
        assert "completed_at" in data

        # 驗證職業原型分析結果
        assert "career_prototype" in data
        prototype = data["career_prototype"]
        assert "prototype_name" in prototype
        assert "prototype_hint" in prototype
        assert "suggested_roles" in prototype
        assert "key_contexts" in prototype
        assert "blind_spots" in prototype

        # 驗證原型分析詳細資訊（如果成功執行）
        if "archetype_analysis" in data:
            archetype = data["archetype_analysis"]
            assert "primary_archetype" in archetype
            assert "confidence_score" in archetype
            assert archetype["primary_archetype"]["archetype_name"] == "系統建構者"

    @patch('api.routes.v4_assessment.get_database_manager')
    def test_results_with_archetype_fallback(self, mock_db_manager):
        """測試職業原型分析失敗時的容錯機制"""
        # Mock 基本資料庫回應
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [
            json.dumps([]),
            json.dumps({'T1': 0.5}),
            json.dumps({}),
            json.dumps({}),
            '2025-10-01 10:30:00'
        ]

        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        # Mock archetype service 失敗
        with patch('services.archetype_service.get_archetype_service') as mock_service:
            mock_service.return_value.analyze_user_archetype.side_effect = Exception("Service error")

            response = client.get("/api/v4/assessment/results/test_session_fallback")

            # 驗證仍有容錯回應
            assert response.status_code == 200
            data = response.json()

            # 應該有容錯的職業原型資訊
            assert "career_prototype" in data
            prototype = data["career_prototype"]
            assert prototype["prototype_name"] == "系統建構者"
            assert "INTJ/ISTJ" in prototype["prototype_hint"]

    def test_results_not_found(self):
        """測試結果不存在的情況"""
        with patch('api.routes.v4_assessment.get_database_manager') as mock_db_manager:
            mock_conn = MagicMock()
            mock_cursor = MagicMock()
            mock_cursor.fetchone.return_value = None  # 沒有找到結果

            mock_conn.execute.return_value = mock_cursor
            mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
            mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

            response = client.get("/api/v4/assessment/results/nonexistent_session")
            assert response.status_code == 404
            assert "Results not found" in response.json()["detail"]


class TestArchetypeDataConsistency:
    """測試職業原型資料一致性"""

    @patch('api.routes.v4_assessment.get_database_manager')
    def test_archetype_data_format_consistency(self, mock_db_manager):
        """測試職業原型資料格式一致性"""
        # Mock 完整的成功回應
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # 建立符合預期格式的測試資料
        test_results = [
            json.dumps([]),  # responses
            json.dumps({     # theta_scores - 系統建構者典型分數
                'T1': 1.8,   # 結構化執行 (高)
                'T2': 1.2,   # 品質與完備
                'T3': 0.8,   # 探索與創新
                'T4': 2.1,   # 分析與洞察 (非常高)
                'T5': 0.3,   # 影響與倡議 (低)
                'T6': 0.1,   # 協作與共好 (低)
                'T7': 0.2,   # 客戶導向 (低)
                'T8': 1.5,   # 學習與成長 (高)
                'T9': 1.4,   # 紀律與信任
                'T10': -0.1, # 壓力調節 (低)
                'T11': -0.5, # 衝突整合 (低)
                'T12': 1.9   # 責任與當責 (非常高)
            }),
            json.dumps({}),  # norm_scores
            json.dumps({}),  # profile
            '2025-10-01 10:30:00'
        ]

        mock_cursor.fetchone.return_value = test_results

        # Mock 職業原型查詢
        archetype_data = {
            'archetype_id': 'ARCHITECT',
            'archetype_name': '系統建構者',
            'archetype_name_en': 'System Architect',
            'keirsey_temperament': '理性者 (Rational)',
            'description': '天生的系統思考者與建構者，擅長將複雜的資訊轉化為清晰的藍圖',
            'mbti_correlates': '["INTJ", "INTP", "ENTJ"]',
            'core_characteristics': '["系統性思維", "邏輯分析能力", "長期規劃"]',
            'work_environment_preferences': '{"structure": "high", "autonomy": "high"}',
            'leadership_style': '策略型領導，注重長期願景',
            'decision_making_style': '基於數據和邏輯分析',
            'communication_style': '直接、簡潔、事實導向',
            'stress_indicators': '["被迫做重複性工作", "缺乏自主權"]',
            'development_areas': '["人際關係建立", "情感表達"]'
        }

        # 設定多次查詢的回應
        mock_cursor.fetchone.side_effect = [test_results[0:5]] + [archetype_data] * 10

        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        response = client.get("/api/v4/assessment/results/architect_test")

        assert response.status_code == 200
        data = response.json()

        # 驗證職業原型資料結構
        assert "career_prototype" in data
        prototype = data["career_prototype"]

        # 檢查必要欄位
        required_fields = [
            "prototype_name", "prototype_hint", "suggested_roles",
            "key_contexts", "blind_spots", "partnership_suggestions"
        ]
        for field in required_fields:
            assert field in prototype, f"Missing required field: {field}"

        # 檢查資料類型
        assert isinstance(prototype["suggested_roles"], list)
        assert isinstance(prototype["key_contexts"], list)
        assert isinstance(prototype["blind_spots"], list)
        assert isinstance(prototype["partnership_suggestions"], list)

        # 檢查內容合理性
        assert len(prototype["suggested_roles"]) > 0
        assert len(prototype["key_contexts"]) > 0


class TestArchetypePerformance:
    """測試職業原型系統性能"""

    @patch('api.routes.v4_assessment.get_database_manager')
    def test_archetype_analysis_performance(self, mock_db_manager):
        """測試職業原型分析性能"""
        import time

        # Mock 快速回應
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = [
            json.dumps([]),
            json.dumps({'T1': 1.0}),
            json.dumps({}),
            json.dumps({}),
            '2025-10-01 10:30:00'
        ]

        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        # 測試回應時間
        start_time = time.time()
        response = client.get("/api/v4/assessment/results/performance_test")
        end_time = time.time()

        response_time = end_time - start_time

        # API 回應應該在合理時間內 (< 2 秒，即使包含職業原型分析)
        assert response_time < 2.0, f"Response time too slow: {response_time:.2f}s"
        assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__])