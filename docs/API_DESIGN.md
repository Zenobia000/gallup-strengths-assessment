# API 設計規範 - Gallup 優勢測驗系統

---

**文件版本 (Document Version):** `v1.0.0`
**最後更新 (Last Updated):** `2025-09-25`
**主要作者/設計師 (Lead Author/Designer):** `TaskMaster Hub + Claude Code`
**審核者 (Reviewers):** `Sunny (Project Lead), 心理測量專家待定`
**狀態 (Status):** `草稿 (Draft) - Phase 2 API 設計`
**相關文檔:** `[PRD.md](./PRD.md), [ARCHITECTURE.md](./ARCHITECTURE.md)`

---

## 目錄 (Table of Contents)

1. [引言](#1-引言-introduction)
2. [設計原則與約定](#2-設計原則與約定)
3. [認證與授權](#3-認證與授權)
4. [通用 API 行為](#4-通用-api-行為)
5. [錯誤處理](#5-錯誤處理)
6. [API 端點詳述](#6-api-端點詳述)
7. [資料模型定義](#7-資料模型定義)
8. [心理測量特定設計](#8-心理測量特定設計)

---

## 1. 引言 (Introduction)

### 1.1 目的 (Purpose)
為 Gallup 優勢測驗系統提供完整的 RESTful API 規範，確保心理測量數據的準確性、隱私保護和可解釋性。

### 1.2 目標讀者 (Target Audience)
前端開發者、測試工程師、心理測量專家、系統整合者

### 1.3 快速入門 (Quick Start)
```bash
# 系統健康檢查
curl --request GET \
  --url http://localhost:8000/api/v1/health

# 開始測驗流程
curl --request POST \
  --url http://localhost:8000/api/v1/consent \
  --header 'Content-Type: application/json' \
  --data '{"agreed": true, "user_agent": "browser/1.0"}'
```

---

## 2. 設計原則與約定

### 2.1 API 風格 (API Style)
- **風格**: RESTful + 心理測量領域特化
- **原則**:
  - 資源導向設計
  - 無狀態會話管理
  - 完整可解釋性追蹤
  - 隱私優先設計

### 2.2 基本 URL (Base URL)
```
Production:  https://gallup-strengths.example.com/api/v1
Development: http://localhost:8000/api/v1
```

### 2.3 請求與回應格式
- **Content-Type**: `application/json`
- **字符集**: UTF-8
- **日期格式**: ISO 8601 (`2025-09-25T10:30:00Z`)

### 2.4 命名約定
- **端點**: 小寫 + 連字符 (`/assessment-sessions`)
- **JSON 欄位**: snake_case (`created_at`, `session_id`)
- **常數**: 大寫 (`PENDING`, `COMPLETED`)

---

## 3. 認證與授權

### 3.1 認證機制
**MVP階段**: 無認證 (匿名會話)
**未來**: JWT Bearer Token

```http
Authorization: Bearer <session_token>
```

### 3.2 授權範圍
- `assessment:take` - 參與測驗
- `assessment:view` - 查看結果
- `reports:download` - 下載報告

---

## 4. 通用 API 行為

### 4.1 響應標準格式
```json
{
  "success": true,
  "data": { ... },
  "meta": {
    "timestamp": "2025-09-25T10:30:00Z",
    "version": "v1.0",
    "request_id": "uuid4-string"
  }
}
```

### 4.2 冪等性設計
- `POST /consent` - 使用 idempotency key
- `POST /session/submit` - 基於 session_id 冪等
- `GET /report/{session_id}.pdf` - 緩存生成結果

---

## 5. 錯誤處理

### 5.1 標準錯誤格式
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid assessment response format",
    "details": {
      "field": "responses",
      "expected": "array of integers 1-7"
    },
    "trace_id": "uuid4-string"
  },
  "meta": {
    "timestamp": "2025-09-25T10:30:00Z",
    "request_id": "uuid4-string"
  }
}
```

### 5.2 心理測量特定錯誤碼
- `PSYCH_001`: 測驗回答不完整
- `PSYCH_002`: 李克特量表值超出範圍
- `PSYCH_003`: 計分演算法執行失敗
- `PSYCH_004`: 權重矩陣版本不匹配
- `PRIVACY_001`: 同意條款未接受
- `SESSION_001`: 會話已過期

---

## 6. API 端點詳述

### 6.1 同意管理 (Consent Management)

#### POST /consent
記錄用戶對隱私條款的同意

**請求**:
```json
{
  "agreed": true,
  "user_agent": "Mozilla/5.0...",
  "ip_address": "192.168.1.1",
  "consent_version": "v1.0"
}
```

**回應**:
```json
{
  "success": true,
  "data": {
    "consent_id": "consent_123",
    "agreed_at": "2025-09-25T10:30:00Z",
    "expires_at": "2026-09-25T10:30:00Z"
  }
}
```

### 6.2 測驗會話管理 (Assessment Sessions)

#### POST /sessions/start
開始新的測驗會話

**請求**:
```json
{
  "consent_id": "consent_123",
  "instrument": "mini_ipip_v1.0"
}
```

**回應**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "instrument_version": "mini_ipip_v1.0",
    "total_items": 20,
    "estimated_duration": 300,
    "created_at": "2025-09-25T10:30:00Z",
    "expires_at": "2025-09-25T11:30:00Z"
  }
}
```

#### GET /sessions/{session_id}/items
獲取測驗題目

**回應**:
```json
{
  "success": true,
  "data": {
    "items": [
      {
        "item_id": "ipip_001",
        "text": "我是聚會的核心人物",
        "scale_type": "likert_7",
        "reverse_scored": false,
        "dimension": "extraversion"
      }
    ],
    "instructions": "請根據您的實際情況選擇最符合的選項",
    "scale_labels": {
      "1": "非常不同意",
      "4": "中立",
      "7": "非常同意"
    }
  }
}
```

#### POST /sessions/{session_id}/submit
提交測驗回答

**請求**:
```json
{
  "responses": [
    {"item_id": "ipip_001", "response": 5},
    {"item_id": "ipip_002", "response": 3}
  ],
  "completion_time": 245,
  "metadata": {
    "browser": "Chrome 119",
    "screen_size": "1920x1080",
    "interruptions": 2
  }
}
```

**回應**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "status": "COMPLETED",
    "submitted_at": "2025-09-25T10:35:00Z",
    "basic_scores": {
      "extraversion": 72,
      "agreeableness": 85,
      "conscientiousness": 63,
      "neuroticism": 34,
      "openness": 78,
      "honesty_humility": 67
    },
    "next_step": "/sessions/sess_abc123/results"
  }
}
```

### 6.3 結果分析 (Results Analysis)

#### GET /sessions/{session_id}/results
獲取優勢面向分析結果

**回應**:
```json
{
  "success": true,
  "data": {
    "session_id": "sess_abc123",
    "analysis_completed_at": "2025-09-25T10:35:30Z",
    "strength_scores": {
      "結構化執行": 68,
      "品質與完備": 75,
      "探索與創新": 82,
      "分析與洞察": 79,
      "影響與倡議": 71,
      "協作與共好": 88,
      "客戶導向": 73,
      "學習與成長": 84,
      "紀律與信任": 72,
      "壓力調節": 65,
      "衝突整合": 69,
      "責任與當責": 76
    },
    "top_strengths": [
      {
        "name": "協作與共好",
        "score": 88,
        "description": "您天生具備優秀的團隊合作能力",
        "development_tips": ["主動承擔團隊協調角色", "培養跨部門溝通技巧"]
      }
    ],
    "risk_areas": [
      {
        "name": "壓力調節",
        "score": 65,
        "concern": "在高壓環境下可能需要額外支持",
        "mitigation": ["建立壓力監控機制", "學習放鬆技巧"]
      }
    ],
    "provenance": {
      "algorithm_version": "v1.0.0",
      "weights_version": "v1.0.0",
      "calculated_at": "2025-09-25T10:35:30Z",
      "confidence_level": 0.85
    }
  }
}
```

### 6.4 決策建議 (Decision Support)

#### POST /sessions/{session_id}/recommendations
生成職缺推薦和改善建議

**請求**:
```json
{
  "recommendation_types": ["job_roles", "improvement_actions"],
  "context": {
    "current_role": "software_engineer",
    "career_stage": "mid_level",
    "industry_preference": ["tech", "finance"]
  }
}
```

**回應**:
```json
{
  "success": true,
  "data": {
    "job_recommendations": [
      {
        "role_id": "ROLE_TECH_LEAD",
        "title": "技術團隊領導",
        "match_score": 0.87,
        "reasoning": {
          "primary_strengths": ["協作與共好", "學習與成長"],
          "supporting_strengths": ["分析與洞察"],
          "rule_id": "TECH_LEAD_RULE_v1"
        },
        "requirements": {
          "必要條件": "協作與共好 ≥85, 學習與成長 ≥80",
          "加分條件": "分析與洞察 ≥75"
        }
      }
    ],
    "improvement_recommendations": [
      {
        "area": "壓力調節",
        "current_score": 65,
        "target_score": 75,
        "priority": "HIGH",
        "actions": [
          {
            "action": "建立每日冥想練習",
            "timeframe": "4週",
            "expected_impact": "+5分"
          }
        ]
      }
    ],
    "generated_at": "2025-09-25T10:36:00Z",
    "valid_until": "2025-12-25T10:36:00Z"
  }
}
```

### 6.5 報告生成 (Report Generation)

#### GET /sessions/{session_id}/reports/pdf
生成並下載 PDF 報告

**查詢參數**:
- `format`: `standard` | `detailed` | `coaching`
- `language`: `zh-TW` | `en-US`

**回應**:
```http
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="strength_analysis_sess_abc123.pdf"
Content-Length: 245760

[PDF Binary Data]
```

#### POST /sessions/{session_id}/share
生成一次性分享連結

**請求**:
```json
{
  "expires_in": 86400,
  "access_type": "view_only",
  "password_protected": true
}
```

**回應**:
```json
{
  "success": true,
  "data": {
    "share_id": "share_xyz789",
    "share_url": "https://app.example.com/shared/share_xyz789",
    "expires_at": "2025-09-26T10:36:00Z",
    "access_count_limit": 1,
    "password": "temp123"
  }
}
```

---

## 7. 資料模型定義

### 7.1 Session (測驗會話)
```json
{
  "session_id": "string",
  "consent_id": "string",
  "instrument_version": "string",
  "status": "PENDING | IN_PROGRESS | COMPLETED | EXPIRED",
  "created_at": "datetime",
  "expires_at": "datetime",
  "metadata": {
    "user_agent": "string",
    "completion_time": "integer (seconds)",
    "interruptions": "integer"
  }
}
```

### 7.2 StrengthScore (優勢分數)
```json
{
  "session_id": "string",
  "big_five": {
    "extraversion": "integer (0-100)",
    "agreeableness": "integer (0-100)",
    "conscientiousness": "integer (0-100)",
    "neuroticism": "integer (0-100)",
    "openness": "integer (0-100)"
  },
  "hexaco": {
    "honesty_humility": "integer (0-100)"
  },
  "strength_facets": {
    "結構化執行": "integer (0-100)",
    // ... 其餘 11 個面向
  },
  "provenance": {
    "algorithm_version": "string",
    "weights_version": "string",
    "calculated_at": "datetime",
    "confidence_intervals": "object"
  }
}
```

### 7.3 JobRecommendation (職缺推薦)
```json
{
  "role_id": "string",
  "title": "string",
  "match_score": "float (0-1)",
  "reasoning": {
    "primary_strengths": ["string"],
    "supporting_strengths": ["string"],
    "rule_id": "string",
    "rule_version": "string"
  },
  "requirements": {
    "必要條件": "string",
    "加分條件": "string"
  }
}
```

---

## 8. 心理測量特定設計

### 8.1 可解釋性要求
所有 API 回應都必須包含：
- `provenance`: 計算過程追蹤
- `confidence_level`: 置信水準
- `algorithm_version`: 演算法版本
- `rule_id`: 適用規則標識

### 8.2 隱私保護措施
- 24小時後自動清理原始回答資料
- 分享連結單次使用後自動失效
- 所有個人化資料匿名化處理
- 完整審計日誌記錄

### 8.3 心理測量品質控制
- 回答一致性檢查 (Consistency Check)
- 反向題目校正驗證
- 極值回應模式偵測
- 快速作答警告機制

### 8.4 跨文化適應性預留
```json
{
  "cultural_context": {
    "locale": "zh-TW",
    "cultural_weights": "v1.0_zh_TW",
    "norm_group": "taiwanese_adult"
  }
}
```

---

## 9. API 版本控制與生命週期

### 9.1 版本控制策略
- **URL 版本控制**: `/api/v1/`, `/api/v2/`
- **語意化版本**: `v1.0.0` (major.minor.patch)
- **向後相容性**: 次版本更新保證相容

### 9.2 棄用策略
1. **通知期**: 6個月前預告
2. **過渡期**: 並行維護 2 個版本
3. **HTTP Headers**: `Sunset: Sat, 31 Dec 2025 23:59:59 GMT`

---

**API 設計審查檢查清單**:
- [ ] 所有端點都支援可解釋性追蹤？
- [ ] 隱私保護措施是否完整？
- [ ] 心理測量學要求是否滿足？
- [ ] 錯誤處理是否涵蓋所有場景？
- [ ] API 文檔是否完整可測試？

**由 TaskMaster Phase 2 API 設計系統產生** 🔗🤖