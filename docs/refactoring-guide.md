# 程式碼重構指導 - Linus 好品味原則

> **Linus Torvalds**: "如果你需要超過3層縮排，你就已經完蛋了，應該修復你的程式。"

## 🚨 當前問題概況

**違反 3 層縮排原則的檔案**: 18 個
**總違規數量**: 1000+ 個
**最嚴重檔案**: `v4_assessment.py` (326個違規), `main.py` (130個違規)

## 🎯 重構策略：Extract Method Pattern

### 原則 1: 消除條件分支巢狀

**❌ 違反好品味的程式碼**:
```python
def process_responses(responses):
    for response in responses:
        if response.is_valid():
            if response.question_type == "multi":
                for option in response.options:
                    if option.selected:
                        # 第4層縮排！
                        process_option(option)
```

**✅ 好品味的程式碼**:
```python
def process_responses(responses):
    valid_responses = filter(lambda r: r.is_valid(), responses)
    for response in valid_responses:
        process_single_response(response)

def process_single_response(response):
    if response.question_type != "multi":
        return

    selected_options = filter(lambda o: o.selected, response.options)
    for option in selected_options:
        process_option(option)
```

### 原則 2: 提前返回 (Early Return)

**❌ 深層巢狀**:
```python
def calculate_score(data):
    if data:
        if data.is_valid():
            if data.has_responses():
                if len(data.responses) >= 20:
                    return compute_actual_score(data)
                else:
                    return error("insufficient responses")
            else:
                return error("no responses")
        else:
            return error("invalid data")
    else:
        return error("no data")
```

**✅ 好品味版本**:
```python
def calculate_score(data):
    if not data:
        return error("no data")

    if not data.is_valid():
        return error("invalid data")

    if not data.has_responses():
        return error("no responses")

    if len(data.responses) < 20:
        return error("insufficient responses")

    return compute_actual_score(data)
```

## 🔧 具體重構任務

### 立即重構文件 (Critical)

1. **v4_assessment.py** (326 violations)
   - 拆分 `submit_assessment` 函式
   - 提取計分邏輯為獨立函式
   - 簡化錯誤處理流程

2. **main.py** (130 violations)
   - 拆分應用程式初始化邏輯
   - 提取配置載入為獨立函式

3. **database.py** (41 violations)
   - 簡化查詢建構邏輯
   - 提取複雜 SQL 為獨立方法

### 重構模式範例

**針對 v4_assessment.py 的重構**:
```python
# 原始問題函式 (簡化示例)
async def submit_assessment(request: SubmitRequest):
    try:
        if request.responses:
            for resp in request.responses:
                if resp.block_id in valid_blocks:
                    if resp.most_like_index != resp.least_like_index:
                        # 第4層縮排！進行計分
                        pass

# 重構後
async def submit_assessment(request: SubmitRequest):
    validated_responses = validate_submission_responses(request.responses)
    scoring_result = calculate_scores_from_responses(validated_responses)
    return format_scoring_response(scoring_result)

def validate_submission_responses(responses):
    # 單一職責：只負責驗證
    pass

def calculate_scores_from_responses(responses):
    # 單一職責：只負責計分
    pass
```

## 📋 重構檢查清單

### 每個函式必須符合:
- [ ] 縮排深度 ≤ 3 層
- [ ] 函式長度 ≤ 20 行
- [ ] 單一職責原則
- [ ] 清晰的函式命名
- [ ] 最少的參數數量

### 重構優先順序:
1. **🔴 Critical**: API 端點函式 (影響用戶體驗)
2. **🟡 High**: 計分和分析邏輯 (影響結果準確性)
3. **🟢 Medium**: 工具函式和配置邏輯

## 💡 Linus 好品味指導原則

1. **消除特殊情況** - 讓邊界條件成為正常情況
2. **提取共同邏輯** - 相似的程式碼應該合併
3. **清晰的抽象** - 每個抽象層都應該有明確的目的
4. **快速失敗** - 錯誤應該盡早被發現和處理

> **Linus**: "好品味是一種直覺，讓你能夠從不同角度看問題，重寫它讓特殊情況消失，變成正常情況。"

## 🚀 重構行動計劃

### Phase 1: 緊急修復 (本週)
- 重構 `v4_assessment.py` 的 `submit_assessment` 函式
- 簡化 `database.py` 的查詢建構邏輯
- 標準化錯誤處理路徑

### Phase 2: 系統優化 (下週)
- 重構所有 API 端點函式
- 統一資料驗證邏輯
- 優化計分引擎結構

### Phase 3: 架構清理 (長期)
- 建立清晰的抽象層
- 消除重複邏輯
- 完善測試覆蓋

這次重構將讓程式碼從「能工作」提升到「優雅工作」，符合 Linus 對好程式碼的標準。