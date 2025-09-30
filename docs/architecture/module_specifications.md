# Gallup 優勢測驗 - 模組規格與測試案例

---

**文件版本:** v1.0
**最後更新:** 2025-09-30
**主要作者:** 開發工程師
**狀態:** 開發中 (In Progress)

---

## 目錄

- [模組: AssessmentService](#模組-assessmentservice)
- [模組: ScoringEngine](#模組-scoringengine)
- [模組: StrengthMapper](#模組-strengthmapper)

---

## 模組: AssessmentService

**對應架構:** `src/main/python/services/assessment.py`
**對應 BDD:** `tests/features/assessment.feature`

---

### 規格 1: `create_assessment_session`

**描述:** 建立新的測驗會話，生成唯一 session_id

**契約式設計 (Design by Contract):**

**前置條件:**
1. `consent_given` 必須為 `True`
2. 資料庫連線正常

**後置條件:**
1. 回傳有效的 `session_id` (UUID v4 格式)
2. `sessions` 表新增一筆記錄
3. `created_at` 時間戳記已記錄

**不變性:**
1. 同一 `session_id` 不可重複
2. 所有 session 必須有 `consent_given=True`

---

### 測試情境與案例

#### ✅ TC-Session-001: 正常路徑
**描述:** 成功建立測驗會話

**測試步驟:**
```python
# Arrange
service = AssessmentService(db_connection)

# Act
session_id = service.create_assessment_session(consent=True)

# Assert
assert is_valid_uuid(session_id)
assert db.query("SELECT * FROM sessions WHERE id=?", session_id) is not None
```

#### ❌ TC-Session-002: 拒絕同意
**描述:** 用戶未同意隱私條款

**測試步驟:**
```python
# Arrange
service = AssessmentService(db_connection)

# Act & Assert
with pytest.raises(ConsentRequiredException):
    service.create_assessment_session(consent=False)
```

---

### 規格 2: `submit_responses`

**描述:** 批量提交問卷回答

**契約式設計:**

**前置條件:**
1. `session_id` 必須存在且有效
2. `responses` 必須包含所有 20 題
3. 每題分數範圍 1-5

**後置條件:**
1. `responses` 表新增 20 筆記錄
2. 會話狀態更新為 `completed`
3. `completed_at` 時間戳記已記錄

**不變性:**
1. 同一會話不可重複提交
2. 回答總數必須等於題目總數

---

### 測試情境

#### ✅ TC-Submit-001: 完整提交
```python
# Arrange
session_id = create_test_session()
responses = [{"question_id": i, "score": 3} for i in range(1, 21)]

# Act
result = service.submit_responses(session_id, responses)

# Assert
assert result.success is True
assert db.count("SELECT COUNT(*) FROM responses WHERE session_id=?", session_id) == 20
```

#### ❌ TC-Submit-002: 不完整回答
```python
# Arrange
session_id = create_test_session()
incomplete_responses = [{"question_id": i, "score": 3} for i in range(1, 15)]

# Act & Assert
with pytest.raises(IncompleteResponseException):
    service.submit_responses(session_id, incomplete_responses)
```

#### ❌ TC-Submit-003: 無效分數
```python
# Act & Assert
with pytest.raises(ValidationError):
    service.submit_responses(session_id, [{"question_id": 1, "score": 10}])
```

---

## 模組: ScoringEngine

**對應架構:** `src/main/python/core/scoring.py`

---

### 規格 1: `calculate_dimension_scores`

**描述:** 根據 Mini-IPIP 演算法計算五大人格向度分數

**契約式設計:**

**前置條件:**
1. 輸入包含 20 題完整回答
2. 反向計分題目已標記

**後置條件:**
1. 回傳 5 個向度分數 (Openness, Conscientiousness, Extraversion, Agreeableness, Neuroticism)
2. 每個分數範圍: 4-20 (4題 × 1-5分)
3. 反向計分題目已正確轉換

**不變性:**
1. 分數總和 = 原始回答總和（反向計分不改變總和）

---

### 測試情境

#### ✅ TC-Score-001: 標準計分
```python
# Arrange
responses = load_test_responses("standard_profile.json")

# Act
scores = engine.calculate_dimension_scores(responses)

# Assert
assert len(scores) == 5
assert all(4 <= score <= 20 for score in scores.values())
assert "openness" in scores
```

#### ✅ TC-Score-002: 反向計分驗證
```python
# Arrange
responses = [
    {"question_id": 2, "score": 5, "reverse_scored": True},  # 應轉為 1
]

# Act
processed = engine._apply_reverse_scoring(responses)

# Assert
assert processed[0]["score"] == 1  # 6 - 5 = 1
```

---

## 模組: StrengthMapper

**對應架構:** `src/main/python/core/strength_mapping.py`

---

### 規格 1: `map_to_strengths`

**描述:** 將五大人格向度映射到 12 個 Gallup 優勢面向

**契約式設計:**

**前置條件:**
1. 輸入包含 5 個有效的人格向度分數
2. 權重矩陣已載入

**後置條件:**
1. 回傳 12 個優勢面向分數
2. 分數已標準化至 0-100
3. 包含 provenance 追蹤資訊

**不變性:**
1. 所有優勢分數 >= 0
2. Top 5 優勢總和 > Bottom 5 優勢總和（合理性檢查）

---

### 測試情境

#### ✅ TC-Map-001: 正常映射
```python
# Arrange
dimension_scores = {
    "openness": 18,
    "conscientiousness": 16,
    "extraversion": 12,
    "agreeableness": 14,
    "neuroticism": 8
}

# Act
strengths = mapper.map_to_strengths(dimension_scores)

# Assert
assert len(strengths) == 12
assert all(0 <= s.score <= 100 for s in strengths)
assert strengths[0].rank == 1  # 最高分排第一
```

#### ✅ TC-Map-002: Provenance 追蹤
```python
# Act
strengths = mapper.map_to_strengths(dimension_scores, include_provenance=True)

# Assert
assert strengths[0].provenance.weight_version == "v1.0"
assert "openness" in strengths[0].provenance.contributing_dimensions
```

---

## 測試覆蓋率目標

| 模組 | 目標覆蓋率 | 當前狀態 |
|:-----|:-----------|:---------|
| AssessmentService | 90% | ⏳ 0% |
| ScoringEngine | 95% | ⏳ 0% |
| StrengthMapper | 95% | ⏳ 0% |
| API Routes | 80% | ⏳ 0% |

---

**下一步:** 實作 TDD 測試先行開發流程
**相關文檔:** [BDD Feature Files](../features/), [架構設計](../architecture/architecture_design.md)