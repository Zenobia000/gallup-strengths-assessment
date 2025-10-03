# 才幹 ID 映射問題記錄

## 問題描述

**發現時間**: 2025-10-03
**嚴重性**: 🔴 Critical
**狀態**: 🚧 In Progress

前端 `results.html` 顯示的才幹名稱與後端 API 返回的才幹 ID 完全不匹配，導致使用者看到錯誤的評測結果。

## 問題根源

### 當前架構問題

1. **評分引擎** (`v4_scoring_engine.py`):
   - 使用固定的 `self.dimensions` 陣列（按照特定順序）
   - 計算分數後按照**分數高低排序**
   - 返回的 `dimension_scores` 字典順序不穩定

2. **API 路由** (`v4_assessment_files.py`):
   - 使用 `enumerate()` 迭代 `dimension_scores.items()`
   - 將第一個維度標記為 `t1`，第二個為 `t2`...
   - **錯誤**：迭代順序取決於分數排序，不是固定的 T1-T12

3. **前端** (`results.html`):
   - 期望固定映射：`T1 = structured_execution`, `T2 = quality_perfectionism`, etc.
   - 實際收到：`t1 = exploration_innovation`（最高分的維度）

### 實際案例

Session `v4_d52cc95aa7e5` (戰略思維主導):

**預期結果**:
```
T3_exploration_innovation: 94.8  ← T3 應該是「探索與創新」
T4_analytical_insight: 89.7      ← T4 應該是「分析與洞察」
```

**實際返回**:
```json
{
  "t1_exploration_innovation": 94.8,  ← 錯誤：最高分被標為 t1
  "t2_analytical_insight": 89.7,      ← 錯誤：第二高分被標為 t2
  "t3_learning_growth": 86.0,         ← 錯誤：第三高分被標為 t3
  ...
}
```

**前端顯示**:
- T1 (結構化執行) 顯示為「探索與創新」的分數 ❌
- T2 (品質與完備) 顯示為「分析與洞察」的分數 ❌
- T3 (探索與創新) 顯示為「學習與成長」的分數 ❌

## 正確的映射關係

| T-ID | 英文名稱 | 中文名稱 | 領域 |
|------|----------|----------|------|
| T1 | structured_execution | 結構化執行 | EXECUTING |
| T2 | quality_perfectionism | 品質與完備 | EXECUTING |
| T3 | exploration_innovation | 探索與創新 | STRATEGIC_THINKING |
| T4 | analytical_insight | 分析與洞察 | STRATEGIC_THINKING |
| T5 | influence_advocacy | 影響與倡議 | INFLUENCING |
| T6 | collaboration_harmony | 協作與共好 | RELATIONSHIP_BUILDING |
| T7 | customer_orientation | 客戶導向 | INFLUENCING |
| T8 | learning_growth | 學習與成長 | STRATEGIC_THINKING |
| T9 | discipline_trust | 紀律與信任 | RELATIONSHIP_BUILDING |
| T10 | pressure_regulation | 壓力調節 | RELATIONSHIP_BUILDING |
| T11 | conflict_integration | 衝突整合 | INFLUENCING |
| T12 | responsibility_accountability | 責任與當責 | EXECUTING |

## 解決方案

### 方案 A：修改評分引擎返回格式（推薦）✅

**修改文件**: `src/main/python/core/scoring/v4_scoring_engine.py`

```python
def score_assessment(self, responses):
    # ... 計算 dimension_scores ...

    # 建立固定的 T-ID 映射
    reverse_mapping = {v: k for k, v in self.dimension_mapping.items()}

    # 返回時使用 T-ID 作為鍵
    result = {
        "dimension_scores": {
            reverse_mapping[dim]: score
            for dim, score in dimension_scores.items()
        },
        # ... 其他欄位
    }
```

### 方案 B：修改 API 路由層映射（當前實作）

**修改文件**: `src/main/python/api/routes/v4_assessment_files.py`

```python
# 建立固定映射
reverse_dim_mapping = {
    "structured_execution": "t1",
    "quality_perfectionism": "t2",
    # ... 全部 12 個
}

# 轉換為正確格式
formatted_scores = {}
for dim_name, score in scoring_result["dimension_scores"].items():
    t_id = reverse_dim_mapping.get(dim_name)
    if t_id:
        formatted_scores[f"{t_id}_{dim_name}"] = score
```

**問題**: 當前實作有bug，調試顯示mapping邏輯未執行。

## 當前進度

### 已完成 ✅
- [x] 識別問題根源
- [x] 建立正確的映射表
- [x] 在評分引擎中添加 `dimension_mapping`
- [x] 在 API 路由中添加 `reverse_dim_mapping`

### 待完成 ⏳
- [ ] 驗證 API 路由中的映射邏輯實際執行
- [ ] 清空舊測試數據並重新運行 UAT
- [ ] 確認前端正確顯示所有 12 個才幹
- [ ] 提交修復到 GitHub

## 測試驗證

### 驗證腳本

```python
# 檢查 API 返回格式
curl http://localhost:8005/api/assessment/results/{session_id} | python3 -c "
import sys, json
data = json.load(sys.stdin)
scores = data['scores']

expected = {
    't1': 'structured_execution',
    't2': 'quality_perfectionism',
    't3': 'exploration_innovation',
    # ...
}

for key in scores.keys():
    t_id = key.split('_')[0]
    dim_name = '_'.join(key.split('_')[1:])
    if expected.get(t_id) != dim_name:
        print(f'❌ {key}: 期望 {t_id}_{expected[t_id]}')
"
```

### UAT 測試需求

重新運行 4 組 UAT 測試，確認：
1. EXECUTING 主導者：T1, T2, T12 在 Top 4
2. STRATEGIC_THINKING 主導者：T3, T4, T8 在 Top 4
3. INFLUENCING 主導者：T5, T7, T11 在 Top 4
4. RELATIONSHIP_BUILDING 主導者：T6, T9, T10 在 Top 4

## 影響範圍

### 受影響功能
- ✅ 評測結果顯示 (results.html)
- ✅ 詳細報告 (report-detail.html)
- ✅ PDF 報告生成
- ✅ 職業原型分類

### 數據完整性
- 現有的測試數據仍然有效（維度分數正確）
- 只是顯示時的 ID 映射錯誤
- 修復後需清空舊數據重新測試

## 相關文件

- `src/main/python/core/scoring/v4_scoring_engine.py` - 評分引擎
- `src/main/python/api/routes/v4_assessment_files.py` - API 路由
- `src/main/resources/static/results.html` - 前端顯示
- `logs/test_*_*.log` - UAT 測試日誌

## 下一步行動

1. 重啟服務器，確認最新代碼生效
2. 添加調試輸出驗證映射邏輯
3. 運行單個測試案例檢查修復
4. 完整 UAT 測試驗證
5. 提交修復並更新文檔
