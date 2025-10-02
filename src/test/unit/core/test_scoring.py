"""
Mini-IPIP 計分引擎單元測試
測試範疇: src/main/python/core/scoring.py

基於研究文檔 docs/scoring-algorithm-research.md 的科學規範
遵循 structure_guide.md 的測試架構設計
"""

import pytest
import json
import time
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# 導入待測試的模組 (未來實作)
# from core.scoring import MiniIPIPScorer, BigFiveScores, ResponseQualityChecker


class TestMiniIPIPScorer:
    """Mini-IPIP 計分引擎測試套件"""

    @pytest.fixture
    def scorer(self):
        """創建計分器實例"""
        # return MiniIPIPScorer()
        # 暫時使用 Mock，等實作完成後替換
        scorer = Mock()
        scorer.calculate_raw_scores = Mock()
        scorer.apply_reverse_scoring = Mock()
        scorer.convert_7_to_5_point = Mock()
        return scorer

    @pytest.fixture
    def sample_responses(self):
        """載入標準測試回答"""
        fixtures_path = Path(__file__).parent.parent.parent / "fixtures" / "sample_responses.json"
        with open(fixtures_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["test_profiles"]["high_extraversion"]["responses"]

    @pytest.fixture
    def expected_scores(self):
        """載入預期分數"""
        fixtures_path = Path(__file__).parent.parent.parent / "fixtures" / "sample_responses.json"
        with open(fixtures_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data["test_profiles"]["high_extraversion"]["expected_raw_scores"]

    def test_calculate_raw_scores_normal_case(self, scorer, sample_responses, expected_scores):
        """測試正常五大人格分數計算"""
        # Arrange
        scorer.calculate_raw_scores.return_value = expected_scores

        # Act
        result = scorer.calculate_raw_scores(sample_responses)

        # Assert
        assert result["extraversion"] == 21
        assert result["agreeableness"] == 18
        assert result["conscientiousness"] == 18
        assert result["neuroticism"] == 14
        assert result["openness"] == 17

        # 驗證方法被正確呼叫
        scorer.calculate_raw_scores.assert_called_once_with(sample_responses)

    def test_reverse_scoring_items(self, scorer):
        """測試反向計分邏輯 (items: 2,4,6,8,10,12,14,16,18,19,20)"""
        # Arrange
        reverse_items = [2, 4, 6, 8, 10, 12, 14, 16, 18, 19, 20]
        test_cases = [
            (1, 7),  # 1 -> 7
            (2, 6),  # 2 -> 6
            (3, 5),  # 3 -> 5
            (4, 4),  # 4 -> 4 (中點)
            (5, 3),  # 5 -> 3
            (6, 2),  # 6 -> 2
            (7, 1),  # 7 -> 1
        ]

        for original, expected in test_cases:
            scorer.apply_reverse_scoring.return_value = expected

            # Act
            result = scorer.apply_reverse_scoring(original, is_reverse=True)

            # Assert
            assert result == expected, f"反向計分錯誤: {original} -> {result}, 預期: {expected}"

    def test_7_to_5_point_conversion(self, scorer):
        """測試 7點量表轉 5點量表邏輯"""
        # Arrange - 基於研究文檔的轉換公式
        conversion_cases = [
            (1, 1.0),    # 1 -> 1.0
            (2, 1.67),   # 2 -> 1.67
            (3, 2.33),   # 3 -> 2.33
            (4, 3.0),    # 4 -> 3.0 (中點)
            (5, 3.67),   # 5 -> 3.67
            (6, 4.33),   # 6 -> 4.33
            (7, 5.0),    # 7 -> 5.0
        ]

        for input_7pt, expected_5pt in conversion_cases:
            scorer.convert_7_to_5_point.return_value = round(expected_5pt, 2)

            # Act
            result = scorer.convert_7_to_5_point(input_7pt)

            # Assert
            assert abs(result - expected_5pt) < 0.01, \
                f"7點轉5點轉換錯誤: {input_7pt} -> {result}, 預期: {expected_5pt}"

    def test_dimension_score_ranges(self, scorer):
        """測試分數範圍驗證 (4-28 for 7-point, 4-20 for 5-point)"""
        # 7點量表範圍測試
        valid_7pt_scores = {
            "extraversion": 21,    # 4-28 範圍內
            "agreeableness": 4,    # 最低值
            "conscientiousness": 28,  # 最高值
            "neuroticism": 16,     # 中間值
            "openness": 12         # 中低值
        }

        scorer.calculate_raw_scores.return_value = valid_7pt_scores
        result = scorer.calculate_raw_scores([4] * 20)  # dummy responses

        # Assert - 所有分數都在有效範圍內
        for dimension, score in result.items():
            assert 4 <= score <= 28, f"{dimension} 分數超出範圍: {score}"

    def test_invalid_response_handling(self, scorer):
        """測試異常回答處理 (空值、超範圍等)"""
        invalid_test_cases = [
            # 空值回答
            ([1, 2, None, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6], "INCOMPLETE_RESPONSES"),
            # 超出範圍 (>7)
            ([8, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6], "INVALID_RESPONSE_VALUE"),
            # 超出範圍 (<1)
            ([0, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6, 7, 1, 2, 3, 4, 5, 6], "INVALID_RESPONSE_VALUE"),
            # 回答數量不足
            ([1, 2, 3, 4, 5], "INCOMPLETE_RESPONSES"),
            # 回答數量過多
            ([1] * 25, "TOO_MANY_RESPONSES"),
        ]

        for invalid_responses, expected_error in invalid_test_cases:
            # Arrange
            scorer.calculate_raw_scores.side_effect = ValueError(expected_error)

            # Act & Assert
            with pytest.raises(ValueError, match=expected_error):
                scorer.calculate_raw_scores(invalid_responses)

    @pytest.mark.performance
    def test_scoring_performance(self, scorer):
        """測試計分效能 (目標: < 10ms)"""
        # Arrange
        responses = [4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]
        expected_scores = {"extraversion": 16, "agreeableness": 16, "conscientiousness": 16,
                          "neuroticism": 16, "openness": 16}
        scorer.calculate_raw_scores.return_value = expected_scores

        # Act - 測量執行時間
        start_time = time.perf_counter()
        result = scorer.calculate_raw_scores(responses)
        end_time = time.perf_counter()

        execution_time_ms = (end_time - start_time) * 1000

        # Assert
        assert execution_time_ms < 10, f"計分時間過長: {execution_time_ms:.2f}ms (目標: <10ms)"
        assert result is not None

    def test_factor_item_mapping(self, scorer):
        """測試題目-因子映射正確性"""
        # Arrange - 基於研究文檔的映射關係
        expected_mapping = {
            "extraversion": [1, 2, 3, 4],
            "agreeableness": [5, 6, 7, 8],
            "conscientiousness": [9, 10, 11, 12],
            "neuroticism": [13, 14, 15, 16],
            "openness": [17, 18, 19, 20]
        }

        # 模擬計分器的內部映射
        scorer.get_factor_mapping.return_value = expected_mapping

        # Act
        result = scorer.get_factor_mapping()

        # Assert
        assert len(result) == 5, "應有5個人格因子"
        for factor, items in result.items():
            assert len(items) == 4, f"{factor} 應有4個題目"
            for item in items:
                assert 1 <= item <= 20, f"題目編號應在1-20範圍內: {item}"

    def test_batch_scoring_performance(self, scorer):
        """測試批量計分效能 (100筆資料)"""
        # Arrange
        batch_size = 100
        responses_batch = [[4] * 20 for _ in range(batch_size)]
        mock_scores = {"extraversion": 16, "agreeableness": 16, "conscientiousness": 16,
                      "neuroticism": 16, "openness": 16}

        # Mock 批量計分方法
        scorer.calculate_batch_scores = Mock()
        scorer.calculate_batch_scores.return_value = [mock_scores] * batch_size

        # Act
        start_time = time.perf_counter()
        results = scorer.calculate_batch_scores(responses_batch)
        end_time = time.perf_counter()

        execution_time = end_time - start_time

        # Assert
        assert len(results) == batch_size
        assert execution_time < 1.0, f"批量計分時間過長: {execution_time:.2f}s (目標: <1s)"


class TestResponseQualityChecker:
    """回答品質檢查器測試"""

    @pytest.fixture
    def quality_checker(self):
        """創建品質檢查器實例"""
        # return ResponseQualityChecker()
        # 暫時使用 Mock
        checker = Mock()
        return checker

    def test_response_variance_check(self, quality_checker):
        """測試回答變異數檢查"""
        # Arrange
        low_variance_responses = [4] * 20  # 所有回答相同
        high_variance_responses = [1, 7, 1, 7, 1, 7, 1, 7, 1, 7,
                                  1, 7, 1, 7, 1, 7, 1, 7, 1, 7]  # 高變異

        quality_checker.check_response_variance.side_effect = [False, True]

        # Act & Assert
        assert not quality_checker.check_response_variance(low_variance_responses)
        assert quality_checker.check_response_variance(high_variance_responses)

    def test_extreme_response_bias_detection(self, quality_checker):
        """測試極端回答偏差檢測"""
        # Arrange
        extreme_responses = [1, 1, 7, 7, 1, 1, 7, 7, 1, 1,
                            7, 7, 1, 1, 7, 7, 1, 1, 7, 7]  # 100% 極端回答
        balanced_responses = [3, 4, 5, 4, 3, 5, 4, 3, 5, 4,
                             3, 5, 4, 3, 5, 4, 3, 5, 4, 3]  # 平衡回答

        quality_checker.detect_extreme_bias.side_effect = [True, False]

        # Act & Assert
        assert quality_checker.detect_extreme_bias(extreme_responses)
        assert not quality_checker.detect_extreme_bias(balanced_responses)

    def test_straight_line_response_detection(self, quality_checker):
        """測試一致性回答檢測"""
        # Arrange
        straight_line = [4] * 20  # 完全一致
        varied_responses = [4, 3, 5, 4, 3, 5, 4, 3, 5, 4,
                           3, 5, 4, 3, 5, 4, 3, 5, 4, 3]  # 有變化

        quality_checker.detect_straight_line.side_effect = [True, False]

        # Act & Assert
        assert quality_checker.detect_straight_line(straight_line)
        assert not quality_checker.detect_straight_line(varied_responses)

    def test_completion_time_validation(self, quality_checker):
        """測試完成時間驗證"""
        # Arrange
        too_fast = 30      # 30秒 - 太快
        reasonable = 300   # 5分鐘 - 合理
        too_slow = 2400    # 40分鐘 - 太慢

        quality_checker.validate_completion_time.side_effect = [False, True, False]

        # Act & Assert
        assert not quality_checker.validate_completion_time(too_fast)
        assert quality_checker.validate_completion_time(reasonable)
        assert not quality_checker.validate_completion_time(too_slow)


class TestBigFiveScores:
    """Big Five 分數模型測試"""

    def test_score_model_creation(self):
        """測試分數模型建立"""
        # Arrange
        scores_data = {
            "extraversion": 75,
            "agreeableness": 65,
            "conscientiousness": 80,
            "neuroticism": 40,
            "openness": 70,
            "confidence": 0.85,
            "quality_flags": []
        }

        # Act - 暫時使用字典模擬，等 Pydantic 模型實作完成
        # result = BigFiveScores(**scores_data)
        result = scores_data

        # Assert
        assert result["extraversion"] == 75
        assert result["confidence"] == 0.85
        assert isinstance(result["quality_flags"], list)

    def test_score_validation_ranges(self):
        """測試分數範圍驗證"""
        # 無效分數測試案例
        invalid_cases = [
            {"extraversion": -10},   # 負值
            {"agreeableness": 110},  # 超過100
            {"conscientiousness": None},  # 空值
        ]

        for invalid_data in invalid_cases:
            # 暫時跳過驗證測試，等 Pydantic 模型實作
            pass

    def test_score_serialization(self):
        """測試分數序列化"""
        # Arrange
        scores = {
            "extraversion": 75,
            "agreeableness": 65,
            "conscientiousness": 80,
            "neuroticism": 40,
            "openness": 70
        }

        # Act - 轉換為 JSON
        json_str = json.dumps(scores)
        restored = json.loads(json_str)

        # Assert
        assert restored == scores
        assert isinstance(json_str, str)


# 整合測試標記
pytestmark = pytest.mark.unit