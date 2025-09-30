# Report Generation API - Task 3.4.5 Implementation

## Overview

本實作完成了基於 task-3.4.3 報告內容生成邏輯的完整 FastAPI 報告生成服務。該 API 提供了從評估問卷回應到 PDF 報告的完整工作流程，遵循 Clean Architecture 原則和 FastAPI 最佳實務。

## API Endpoints

### 1. POST `/api/reports/generate`
**從評估問卷回應生成報告**

```json
{
  "responses": [
    {"question_id": 1, "score": 4},
    {"question_id": 2, "score": 2},
    // ... 20 total responses
  ],
  "user_name": "張小明",
  "report_type": "full_assessment",
  "report_format": "pdf",
  "report_quality": "standard",
  "user_context": {
    "industry_preference": "technology",
    "experience_level": "mid-level"
  },
  "include_charts": true,
  "include_recommendations": true
}
```

**Response (202 Accepted):**
```json
{
  "success": true,
  "report_id": "RPT-20250930-A1B2C3D4",
  "status": "processing",
  "metadata": {
    "report_id": "RPT-20250930-A1B2C3D4",
    "report_type": "full_assessment",
    "report_format": "pdf",
    "user_name": "張小明",
    "assessment_date": "2025-09-30T10:30:00Z",
    "generation_timestamp": "2025-09-30T10:30:00Z"
  },
  "download_url": "/api/reports/RPT-20250930-A1B2C3D4/download",
  "expires_at": "2025-10-03T10:30:00Z",
  "warnings": []
}
```

### 2. GET `/api/reports/{report_id}`
**取得報告生成狀態**

**Response (200 OK):**
```json
{
  "report_id": "RPT-20250930-A1B2C3D4",
  "status": "completed",
  "metadata": {
    "report_id": "RPT-20250930-A1B2C3D4",
    "report_type": "full_assessment",
    "report_format": "pdf",
    "user_name": "張小明",
    "assessment_date": "2025-09-30T10:30:00Z",
    "generation_timestamp": "2025-09-30T10:30:00Z",
    "file_size_bytes": 2048576,
    "generation_time_seconds": 45.2,
    "confidence_score": 0.87
  },
  "progress_percentage": 100,
  "created_at": "2025-09-30T10:30:00Z",
  "updated_at": "2025-09-30T10:30:45Z"
}
```

### 3. GET `/api/reports/{report_id}/download`
**下載 PDF 報告檔案**

**Response (200 OK):**
- Content-Type: `application/pdf`
- Content-Disposition: `attachment; filename="張小明_個人優勢評估報告_RPT-20250930-A1B2C3D4.pdf"`
- Binary PDF content

### 4. POST `/api/reports/preview`
**預覽報告內容（不生成檔案）**

```json
{
  "responses": [
    {"question_id": 1, "score": 4},
    // ... 20 total responses
  ],
  "user_name": "張小明",
  "sections": ["executive_summary", "strength_analysis"],
  "user_context": {
    "industry_preference": "technology"
  }
}
```

**Response (200 OK):**
```json
{
  "preview_id": "PREV-20250930-X1Y2Z3W4",
  "user_name": "張小明",
  "assessment_summary": {
    "big_five_scores": {
      "openness": 16.5,
      "conscientiousness": 18.2,
      "extraversion": 14.8,
      "agreeableness": 17.1,
      "neuroticism": 12.3
    },
    "dominant_traits": ["conscientiousness", "agreeableness", "openness"],
    "assessment_quality": "high"
  },
  "sections": [
    {
      "section_type": "cover_page",
      "title": "Cover Page",
      "chinese_title": "封面",
      "content_summary": "報告標題、使用者資訊、評估日期",
      "element_count": 4,
      "estimated_pages": 1.0
    },
    {
      "section_type": "executive_summary",
      "title": "Executive Summary",
      "chinese_title": "執行摘要",
      "content_summary": "關鍵洞察、核心優勢、職業建議摘要",
      "element_count": 6,
      "estimated_pages": 1.5
    }
  ],
  "total_estimated_pages": 8,
  "generation_estimate_seconds": 120,
  "generated_at": "2025-09-30T10:30:00Z"
}
```

### 5. GET `/api/reports/`
**列出已生成的報告**

**Query Parameters:**
- `page`: 頁碼 (default: 1)
- `page_size`: 每頁項目數 (default: 20, max: 100)
- `status`: 狀態篩選 (optional)

**Response (200 OK):**
```json
{
  "reports": [
    {
      "report_id": "RPT-20250930-A1B2C3D4",
      "report_type": "full_assessment",
      "user_name": "張小明",
      "status": "completed",
      "created_at": "2025-09-30T10:30:00Z",
      "file_size_bytes": 2048576
    }
  ],
  "total_count": 1,
  "page": 1,
  "page_size": 20,
  "has_next": false
}
```

### 6. DELETE `/api/reports/{report_id}`
**刪除報告**

**Response (204 No Content)**

### 7. GET `/api/reports/health`
**報告服務健康檢查**

**Response (200 OK):**
```json
{
  "service_status": "healthy",
  "generation_queue_size": 0,
  "active_generations": 2,
  "disk_space_available_mb": 15360.5,
  "last_successful_generation": "2025-09-30T10:29:45Z",
  "error_rate_last_hour": 2.1,
  "dependencies": {
    "pdf_generator": "healthy",
    "scoring_engine": "healthy",
    "content_generator": "healthy",
    "database": "healthy"
  }
}
```

## 架構設計

### 檔案結構
```
src/main/python/
├── api/routes/reports.py          # FastAPI 路由定義
├── models/report_models.py        # Pydantic 資料模型
├── services/report_service.py     # 業務邏輯服務層
└── core/report/                   # 核心報告生成模組
    ├── content_generator.py       # 內容生成器
    ├── pdf_generator.py          # PDF 生成器
    ├── report_template.py        # 報告模板
    └── chart_renderer.py         # 圖表渲染器
```

### 關鍵整合點

1. **與 core.report 模組整合**
   - 使用 `PDFReportGenerator` 進行 PDF 生成
   - 使用 `ContentGenerator` 進行內容生成
   - 使用 `ScoringEngine` 進行分數計算

2. **與 core.recommendation 系統整合**
   - 使用 `RecommendationEngine` 生成職業建議
   - 整合 `StrengthProfile` 和 `JobRecommendation`

3. **資料庫整合**
   - 使用現有的 `ReportGeneration` 表
   - 支援狀態追蹤和檔案管理
   - 實作清理和維護功能

## 技術特色

### 1. 非同步處理
- 報告生成採用非同步模式
- 立即返回狀態，支援輪詢查詢
- 背景任務處理長時間操作

### 2. 錯誤處理
- 自定義異常類型 (`ReportGenerationError`)
- 詳細的錯誤代碼和訊息
- HTTP 狀態碼對應

### 3. 驗證機制
- Pydantic 模型驗證
- 問卷回應完整性檢查
- 參數範圍和格式驗證

### 4. 檔案管理
- 安全的檔案下載
- 自動檔案清理
- 磁碟空間監控

## 使用範例

### Python 客戶端範例
```python
import httpx
import asyncio

async def generate_report():
    client = httpx.AsyncClient()

    # 1. 生成報告
    response = await client.post("/api/reports/generate", json={
        "responses": [{"question_id": i, "score": 4} for i in range(1, 21)],
        "user_name": "測試用戶",
        "report_type": "full_assessment"
    })

    report_data = response.json()
    report_id = report_data["report_id"]

    # 2. 輪詢狀態
    while True:
        status_response = await client.get(f"/api/reports/{report_id}")
        status = status_response.json()["status"]

        if status == "completed":
            break
        elif status == "failed":
            raise Exception("Report generation failed")

        await asyncio.sleep(2)

    # 3. 下載 PDF
    pdf_response = await client.get(f"/api/reports/{report_id}/download")

    with open("report.pdf", "wb") as f:
        f.write(pdf_response.content)

    print("Report downloaded successfully!")
```

### cURL 範例
```bash
# 生成報告
curl -X POST "http://localhost:8000/api/reports/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "responses": [
      {"question_id": 1, "score": 4},
      {"question_id": 2, "score": 3}
    ],
    "user_name": "測試用戶",
    "report_type": "full_assessment"
  }'

# 檢查狀態
curl "http://localhost:8000/api/reports/RPT-20250930-A1B2C3D4"

# 下載報告
curl -O "http://localhost:8000/api/reports/RPT-20250930-A1B2C3D4/download"
```

## 效能考量

### 生成時間
- 標準報告：60-120 秒
- 高品質報告：120-180 秒
- 預覽模式：2-5 秒

### 檔案大小
- 平均 PDF 大小：1.5-3 MB
- 包含圖表：2-4 MB
- 純文字版本：0.5-1 MB

### 併發處理
- 支援最多 5 個併發生成
- 佇列管理和優先級排序
- 資源使用監控

## 安全考量

### 資料保護
- 問卷回應資料驗證
- 檔案存取權限控制
- 自動檔案過期清理

### 訪問控制
- 報告 ID 基於 UUID 生成
- 下載連結時效性控制
- 可選的密碼保護機制

## 監控和維護

### 健康檢查
- 服務狀態監控
- 磁碟空間警告
- 錯誤率追蹤

### 維護功能
- 過期報告自動清理
- 統計資料收集
- 系統效能監控

---

**實作完成狀態：✅ 完整實作所有需求功能**

1. ✅ POST /api/reports/generate - 從評估問卷回應生成報告
2. ✅ GET /api/reports/{report_id} - 取得已生成的報告狀態
3. ✅ GET /api/reports/{report_id}/download - 下載 PDF 檔案
4. ✅ POST /api/reports/preview - 預覽報告內容（不生成檔案）
5. ✅ 使用已完成的 core.report 模組群組
6. ✅ 整合 core.scoring.ScoringEngine 進行分數計算
7. ✅ 整合 core.recommendation 系統
8. ✅ 遵循 FastAPI 最佳實務和 Clean Architecture 原則
9. ✅ 實作適當的錯誤處理和驗證
10. ✅ 支援非同步處理和資料庫記錄