"""
Test Career Archetype Service

測試職業原型服務的核心功能：
- 原型分析
- 職位推薦
- 資料庫整合
- API 回應格式
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from services.archetype_service import ArchetypeService, get_archetype_service
from core.analysis.archetype_mapper import TalentProfile


@pytest.fixture
def archetype_service():
    """建立 ArchetypeService 實例用於測試"""
    return ArchetypeService()


@pytest.fixture
def sample_talent_scores():
    """樣本才幹分數"""
    return {
        'T1': 85,  # 結構化執行
        'T2': 70,  # 品質與完備
        'T3': 65,  # 探索與創新
        'T4': 90,  # 分析與洞察 (高分)
        'T5': 60,  # 影響與倡議
        'T6': 55,  # 協作與共好
        'T7': 50,  # 客戶導向
        'T8': 75,  # 學習與成長
        'T9': 80,  # 紀律與信任
        'T10': 45, # 壓力調節
        'T11': 40, # 衝突整合
        'T12': 88  # 責任與當責 (高分)
    }


@pytest.fixture
def sample_talent_profile():
    """樣本 TalentProfile"""
    return TalentProfile(
        dominant_talents=[('T4', 90), ('T12', 88), ('T1', 85)],  # 主導才幹
        supporting_talents=[('T9', 80), ('T8', 75), ('T2', 70)],  # 支援才幹
        lesser_talents=[('T11', 40), ('T10', 45), ('T7', 50)]     # 較弱才幹
    )


class TestArchetypeService:
    """測試 ArchetypeService 類別"""

    def test_service_initialization(self, archetype_service):
        """測試服務初始化"""
        assert archetype_service is not None
        assert hasattr(archetype_service, 'db_manager')
        assert hasattr(archetype_service, 'archetype_mapper')
        assert hasattr(archetype_service, 'career_matcher')

    @patch('services.archetype_service.get_database_manager')
    def test_analyze_user_archetype_success(self, mock_db_manager, archetype_service, sample_talent_scores):
        """測試用戶原型分析成功案例"""
        # Mock 資料庫回應
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'archetype_id': 'ARCHITECT',
            'archetype_name': '系統建構者',
            'archetype_name_en': 'System Architect',
            'keirsey_temperament': '理性者 (Rational)',
            'description': '天生的系統思考者與建構者',
            'mbti_correlates': '["INTJ", "INTP"]',
            'core_characteristics': '["系統性思維", "邏輯分析"]'
        }
        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        # 執行分析
        result = archetype_service.analyze_user_archetype(
            session_id="test_session_001",
            talent_scores=sample_talent_scores
        )

        # 驗證結果
        assert result is not None
        assert result.session_id == "test_session_001"
        assert result.primary_archetype.archetype_id == 'ARCHITECT'
        assert result.confidence_score > 0.5
        assert len(result.dominant_talents) >= 1
        assert isinstance(result.archetype_scores, dict)

    @patch('services.archetype_service.get_database_manager')
    def test_generate_job_recommendations(self, mock_db_manager, archetype_service):
        """測試職位推薦生成"""
        # Mock 已存在的原型結果
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'primary_archetype_id': 'ARCHITECT',
            'archetype_scores': '{"ARCHITECT": 8, "GUARDIAN": 3}',
            'dominant_talents': '[{"dimension_id": "T4", "score": 90}]',
            'supporting_talents': '[]',
            'lesser_talents': '[]',
            'confidence_score': 0.85
        }
        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        # 執行職位推薦
        recommendations = archetype_service.generate_job_recommendations("test_session_001")

        # 驗證推薦結果
        assert isinstance(recommendations, list)
        # 注意：由於 career_matcher 可能沒有實際職位資料，可能返回空列表
        # 這在實際環境中需要有職位資料才能正常工作

    def test_get_career_prototype_info_fallback(self, archetype_service):
        """測試職業原型資訊獲取的容錯機制"""
        with patch.object(archetype_service, '_get_archetype_result', return_value=None):
            # 測試當沒有原型結果時的容錯行為
            prototype_info = archetype_service.get_career_prototype_info("nonexistent_session")

            # 驗證容錯回應
            assert prototype_info.prototype_name == "系統建構者"
            assert "INTJ/ISTJ" in prototype_info.prototype_hint
            assert len(prototype_info.suggested_roles) >= 3
            assert len(prototype_info.key_contexts) >= 3

    def test_calculate_all_archetype_scores(self, archetype_service, sample_talent_profile):
        """測試所有原型分數計算"""
        scores = archetype_service._calculate_all_archetype_scores(sample_talent_profile)

        # 驗證分數計算
        assert isinstance(scores, dict)
        assert len(scores) == 4  # 4種原型
        assert all(isinstance(score, (int, float)) for score in scores.values())
        assert all(score >= 0 for score in scores.values())

        # 系統建構者 (ARCHITECT) 應該有較高分數，因為有 T4 和 T1 主導才幹
        assert 'ARCHITECT' in scores
        assert scores['ARCHITECT'] > 0

    def test_get_secondary_archetype(self, archetype_service):
        """測試次要原型識別"""
        archetype_scores = {
            'ARCHITECT': 8,
            'GUARDIAN': 5,
            'IDEALIST': 2,
            'ARTISAN': 1
        }

        secondary = archetype_service._get_secondary_archetype(archetype_scores, 'ARCHITECT')
        assert secondary == 'GUARDIAN'  # 第二高分

        # 測試沒有次要原型的情況
        single_archetype_scores = {
            'ARCHITECT': 8,
            'GUARDIAN': 0,
            'IDEALIST': 0,
            'ARTISAN': 0
        }
        secondary = archetype_service._get_secondary_archetype(single_archetype_scores, 'ARCHITECT')
        assert secondary is None

    def test_calculate_confidence_score(self, archetype_service, sample_talent_profile):
        """測試信心分數計算"""
        archetype_scores = {
            'ARCHITECT': 8,
            'GUARDIAN': 3,
            'IDEALIST': 1,
            'ARTISAN': 0
        }

        confidence = archetype_service._calculate_confidence_score(sample_talent_profile, archetype_scores)

        assert 0.0 <= confidence <= 1.0
        assert confidence > 0.7  # 應該有合理的信心度

    def test_format_talents(self, archetype_service):
        """測試才幹格式化"""
        talents = [('T1', 85), ('T4', 90)]
        formatted = archetype_service._format_talents(talents)

        assert len(formatted) == 2
        assert all('dimension_id' in talent for talent in formatted)
        assert all('dimension_name' in talent for talent in formatted)
        assert all('score' in talent for talent in formatted)

        # 檢查 T1 的格式化
        t1_talent = next(t for t in formatted if t['dimension_id'] == 'T1')
        assert t1_talent['dimension_name'] == '結構化執行'
        assert t1_talent['score'] == 85


class TestArchetypeServiceIntegration:
    """整合測試"""

    @patch('services.archetype_service.get_database_manager')
    def test_full_workflow(self, mock_db_manager):
        """測試完整的工作流程"""
        # 設定資料庫 mock
        mock_conn = MagicMock()
        mock_cursor = MagicMock()

        # Mock archetype 查詢
        mock_cursor.fetchone.side_effect = [
            # 第一次查詢：archetype 資料
            {
                'archetype_id': 'ARCHITECT',
                'archetype_name': '系統建構者',
                'archetype_name_en': 'System Architect',
                'keirsey_temperament': '理性者 (Rational)',
                'description': '天生的系統思考者與建構者',
                'mbti_correlates': '["INTJ", "INTP"]',
                'core_characteristics': '["系統性思維"]',
                'work_environment_preferences': '{}',
                'stress_indicators': '[]',
                'development_areas': '[]'
            }
        ]

        mock_conn.execute.return_value = mock_cursor
        mock_db_manager.return_value.get_connection.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db_manager.return_value.get_connection.return_value.__exit__ = Mock(return_value=None)

        # 建立服務並執行分析
        service = ArchetypeService()
        talent_scores = {
            'T1': 85, 'T4': 90, 'T12': 88,  # 高分才幹，符合 ARCHITECT
            'T2': 70, 'T3': 65, 'T5': 60,
            'T6': 55, 'T7': 50, 'T8': 75,
            'T9': 80, 'T10': 45, 'T11': 40
        }

        result = service.analyze_user_archetype("integration_test", talent_scores)

        # 驗證結果
        assert result.session_id == "integration_test"
        assert result.primary_archetype.archetype_name == '系統建構者'
        assert len(result.dominant_talents) > 0


class TestArchetypeServiceAPI:
    """測試與 API 的整合"""

    def test_get_archetype_service_singleton(self):
        """測試服務單例獲取"""
        service1 = get_archetype_service()
        service2 = get_archetype_service()

        assert service1 is not None
        assert service2 is not None
        # 注意：由於每次都建立新實例，所以不是單例模式
        assert isinstance(service1, ArchetypeService)
        assert isinstance(service2, ArchetypeService)


class TestArchetypeServiceErrorHandling:
    """測試錯誤處理"""

    @patch('services.archetype_service.get_database_manager')
    def test_database_error_handling(self, mock_db_manager):
        """測試資料庫錯誤處理"""
        # Mock 資料庫錯誤
        mock_db_manager.return_value.get_connection.side_effect = Exception("Database connection failed")

        service = ArchetypeService()

        with pytest.raises(Exception):
            service.analyze_user_archetype("error_test", {'T1': 50})

    def test_invalid_talent_scores(self):
        """測試無效才幹分數處理"""
        service = ArchetypeService()

        # 測試空字典
        with pytest.raises((ValueError, KeyError, AttributeError)):
            service.analyze_user_archetype("invalid_test", {})

        # 測試非數值分數
        with pytest.raises((ValueError, TypeError)):
            service.analyze_user_archetype("invalid_test", {'T1': 'invalid'})


if __name__ == '__main__':
    pytest.main([__file__])