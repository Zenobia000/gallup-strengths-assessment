# V4.0 頁面串接邏輯文檔

## 系統架構概覽

### 服務部署
- **前端服務**: http://localhost:3000
- **API 服務**: http://localhost:8004

### 頁面清單

| 頁面 | URL | 用途 | 狀態 |
|------|-----|------|------|
| **landing.html** | http://localhost:3000/landing.html | 商業導向首頁 | ✅ 正常 |
| **assessment.html** | http://localhost:3000/assessment.html | 新版評測頁面 | ✅ 已修正 |
| **v4_assessment.html** | http://localhost:3000/v4_assessment.html | V4.0評測頁面 | ✅ 已修正 |
| **results.html** | http://localhost:3000/results.html | 結果展示頁 | ✅ 正常 |

## 頁面流程圖

```
[landing.html]
    ↓ (點擊"開始測評")
[assessment.html 或 v4_assessment.html]
    ↓ (完成15個區塊選擇)
[results.html]
```

## 詳細串接邏輯

### 1. Landing Page (landing.html)
**功能**: 商業導向的首頁，展示價值主張
**關鍵元素**:
- 英雄區塊 (Hero Section)
- 信任標誌 (Trust Signals)
- CTA 按鈕："立即開始免費測評"
- **跳轉邏輯**:
  ```javascript
  // 應該跳轉到評測頁面
  <a href="/assessment.html" class="btn-primary">立即開始免費測評 →</a>
  ```

### 2. Assessment Page (assessment.html)
**功能**: 標準評測流程頁面
**API 調用**:
- **初始化**: `GET http://localhost:8004/api/assessment/blocks?block_count=15`
  - 獲取15個四選二區塊
  - 獲取 session_id
- **提交**: `POST http://localhost:8004/api/assessment/submit`
  ```json
  {
    "session_id": "xxx",
    "responses": [
      {
        "block_id": 0,
        "most_like_index": 0,
        "least_like_index": 3,
        "response_time_ms": 5000
      }
    ],
    "completion_time_seconds": 300
  }
  ```
- **跳轉邏輯**: 提交成功後跳轉到 `/results.html?session=${sessionId}`

### 3. V4 Assessment Page (v4_assessment.html)
**功能**: V4.0 版本的評測頁面（備選）
**特點**:
- 更精緻的UI設計
- 漸變背景和動畫效果
- 選擇摘要顯示
**API 調用**: 與 assessment.html 相同
**跳轉邏輯**: 與 assessment.html 相同

### 4. Results Page (results.html)
**功能**: 展示評測結果
**數據獲取**:
- 從 URL 參數獲取 session_id
- 調用 `GET http://localhost:8004/api/assessment/results/{session_id}`
**展示內容**:
- 12維度雷達圖
- 前5大優勢
- 發展建議
- 升級付費選項

## API 端點總覽

| 端點 | 方法 | 用途 |
|------|------|------|
| `/api/system/health` | GET | 系統健康檢查 |
| `/api/assessment/blocks` | GET | 獲取評測區塊 |
| `/api/assessment/submit` | POST | 提交評測答案 |
| `/api/assessment/results/{session_id}` | GET | 獲取評測結果 |

## 常見問題與解決方案

### 問題1: 頁面一直轉圈
**原因**: API 路徑錯誤（使用相對路徑而非完整URL）
**解決**:
```javascript
// 錯誤
fetch('/api/assessment/blocks')

// 正確
fetch('http://localhost:8004/api/assessment/blocks')
```

### 問題2: CORS 錯誤
**原因**: 跨域請求被阻擋
**解決**: API 已配置 CORS 中間件允許來自 localhost:3000 的請求

### 問題3: 提交數據格式錯誤
**關鍵點**:
- `most_like_index` 和 `least_like_index` 必須是 0-3 的整數
- `completion_time_seconds` 而非 `completion_time`
- responses 陣列必須過濾掉 undefined 值

## 建議的頁面選擇

**推薦使用**: `assessment.html`
- 原因：已完全修正並測試通過
- 簡潔清晰的UI
- 完整的錯誤處理

**備選方案**: `v4_assessment.html`
- 更美觀的設計
- 適合展示用途
- 也已修正API路徑

## 測試流程

1. 訪問 http://localhost:3000/landing.html
2. 點擊"立即開始免費測評"
3. 在評測頁面完成15個區塊的選擇
4. 提交後自動跳轉到結果頁
5. 查看個人化報告

## 注意事項

1. **確保服務運行**:
   - 前端: port 3000
   - API: port 8004

2. **Session 管理**:
   - Session ID 由 API 生成
   - 前端需保存並傳遞

3. **數據完整性**:
   - 每個區塊必須選擇一個"最像"和一個"最不像"
   - 不能選擇同一個選項

---

*更新時間: 2025-10-02*