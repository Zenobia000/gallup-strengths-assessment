# API 設計規範 (API Design Specification) - Gallup 會員系統

---

**文件版本:** `v1.0`
**最後更新:** `2025-10-03`
**主要作者:** `API 設計師`
**狀態:** `草稿 (Draft)`

---

## 1. 引言

### 1.1 目的
為 Gallup 優勢測驗會員系統的 API 提供統一、明確、易於遵循的介面契約。

### 1.2 基本資訊
- **Base URL (Production):** `https://api.gallup-strengths.com/api/v1`
- **Base URL (Staging):** `https://staging-api.gallup-strengths.com/api/v1`
- **Base URL (Development):** `http://localhost:8005/api`

---

## 2. 設計原則與約定

### 2.1 API 風格
- **風格:** RESTful
- **資源導向:** 使用名詞複數形式 (如 `/members`, `/assessments`)
- **無狀態:** 每個請求包含完整的認證資訊

### 2.2 請求與回應格式
- **Content-Type:** `application/json` (UTF-8)
- **日期時間:** ISO 8601 格式 (UTC), 例如: `2025-10-03T10:00:00Z`

### 2.3 命名約定
- **資源路徑:** 小寫, 連字符連接 (如 `/member-profiles`)
- **JSON 欄位:** `snake_case` (如 `member_id`, `created_at`)

### 2.4 標準 HTTP Headers
```
Authorization: Bearer {access_token}
Content-Type: application/json
Accept: application/json
X-Request-ID: {uuid}  # 可選，用於追蹤
```

---

## 3. 認證與授權

### 3.1 認證機制
- **方式:** JWT (JSON Web Token)
- **傳遞:** HTTP-only Cookie + Authorization Header (Bearer Token)
- **Token 類型:**
  - **Access Token:** 有效期 7 天
  - **Refresh Token:** 有效期 30 天

### 3.2 Token 回應格式
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 604800
}
```

---

## 4. 錯誤處理

### 4.1 標準錯誤回應格式
```json
{
  "error": {
    "code": "invalid_credentials",
    "message": "Email 或密碼錯誤",
    "details": {
      "field": "password",
      "reason": "Invalid password"
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000"
  }
}
```

### 4.2 常見錯誤碼

| HTTP 狀態 | 錯誤碼 | 說明 |
|:---|:---|:---|
| 400 | `invalid_request` | 請求參數錯誤或格式不正確 |
| 400 | `email_already_exists` | Email 已被註冊 |
| 400 | `weak_password` | 密碼強度不足 |
| 401 | `invalid_credentials` | 帳號或密碼錯誤 |
| 401 | `token_expired` | Token 已過期 |
| 401 | `email_not_verified` | Email 尚未驗證 |
| 403 | `access_denied` | 權限不足 |
| 404 | `member_not_found` | 會員不存在 |
| 409 | `oauth_account_conflict` | 社交帳號已綁定其他會員 |
| 429 | `rate_limit_exceeded` | 請求過於頻繁 |
| 500 | `internal_server_error` | 伺服器內部錯誤 |

---

## 5. API 端點詳述

### 5.1 認證相關 (Authentication)

#### `POST /members/auth/register`
**描述:** 註冊新會員

**請求體:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123",
  "full_name": "張三",
  "marketing_consent": false
}
```

**回應 (201 Created):**
```json
{
  "member": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "email_verified": false,
    "created_at": "2025-10-03T10:00:00Z"
  },
  "message": "註冊成功！請檢查您的 Email 完成驗證。"
}
```

---

#### `POST /members/auth/login`
**描述:** Email 登入

**請求體:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123"
}
```

**回應 (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 604800,
  "member": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "full_name": "張三"
  }
}
```

---

#### `POST /members/auth/login/google`
**描述:** Google OAuth 登入

**請求體:**
```json
{
  "id_token": "eyJhbGciOiJSUzI1NiIsImtpZCI6IjE4MmU0M2..."
}
```

**回應:** 同 `/login`

---

#### `POST /members/auth/refresh`
**描述:** 刷新 Access Token

**請求體:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**回應 (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 604800
}
```

---

#### `POST /members/auth/logout`
**描述:** 登出 (撤銷 Refresh Token)

**Headers:** `Authorization: Bearer {access_token}`

**回應 (204 No Content)**

---

#### `GET /members/auth/verify/{token}`
**描述:** 驗證 Email

**URL 參數:**
- `token` (string): Email 驗證令牌

**回應 (200 OK):**
```json
{
  "message": "Email 驗證成功！",
  "member": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "email_verified": true
  }
}
```

---

#### `POST /members/auth/password/forgot`
**描述:** 忘記密碼 (發送重設郵件)

**請求體:**
```json
{
  "email": "user@example.com"
}
```

**回應 (200 OK):**
```json
{
  "message": "密碼重設郵件已發送，請檢查您的信箱。"
}
```

---

#### `POST /members/auth/password/reset`
**描述:** 重設密碼

**請求體:**
```json
{
  "token": "reset_token_here",
  "new_password": "NewSecurePass123"
}
```

**回應 (200 OK):**
```json
{
  "message": "密碼重設成功！請使用新密碼登入。"
}
```

---

### 5.2 個人檔案相關 (Profile)

#### `GET /members/profile`
**描述:** 查看個人檔案

**Headers:** `Authorization: Bearer {access_token}`

**回應 (200 OK):**
```json
{
  "member": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "email_verified": true,
    "created_at": "2025-10-03T10:00:00Z",
    "last_login_at": "2025-10-03T15:30:00Z"
  },
  "profile": {
    "full_name": "張三",
    "display_name": "Sam",
    "job_title": "軟體工程師",
    "industry": "科技業",
    "company": "ABC 公司",
    "marketing_consent": false,
    "research_consent": true
  }
}
```

---

#### `PUT /members/profile`
**描述:** 更新個人檔案

**Headers:** `Authorization: Bearer {access_token}`

**請求體:**
```json
{
  "full_name": "張三",
  "job_title": "資深軟體工程師",
  "industry": "科技業",
  "company": "XYZ 公司"
}
```

**回應 (200 OK):**
```json
{
  "profile": {
    "full_name": "張三",
    "job_title": "資深軟體工程師",
    "industry": "科技業",
    "company": "XYZ 公司",
    "updated_at": "2025-10-03T16:00:00Z"
  }
}
```

---

#### `PATCH /members/profile/privacy`
**描述:** 更新隱私設定

**Headers:** `Authorization: Bearer {access_token}`

**請求體:**
```json
{
  "marketing_consent": true,
  "research_consent": false
}
```

**回應 (200 OK):**
```json
{
  "privacy": {
    "marketing_consent": true,
    "research_consent": false,
    "updated_at": "2025-10-03T16:05:00Z"
  }
}
```

---

#### `DELETE /members/account`
**描述:** 刪除帳號 (GDPR)

**Headers:** `Authorization: Bearer {access_token}`

**請求體:**
```json
{
  "password": "SecurePass123",
  "confirm_deletion": true
}
```

**回應 (200 OK):**
```json
{
  "message": "帳號已刪除。您的資料將在 30 天後永久移除。",
  "deletion_scheduled_at": "2025-11-03T16:10:00Z"
}
```

---

### 5.3 評測歷史相關 (Assessment History)

#### `GET /members/assessments`
**描述:** 查詢會員的評測歷史列表

**Headers:** `Authorization: Bearer {access_token}`

**Query 參數:**
- `page` (int, 可選): 頁碼 (預設 1)
- `per_page` (int, 可選): 每頁筆數 (預設 10, 最大 50)
- `sort_by` (string, 可選): 排序欄位 (`created_at`, `-created_at`)

**回應 (200 OK):**
```json
{
  "assessments": [
    {
      "session_id": "session_abc123",
      "completed_at": "2025-10-01T14:30:00Z",
      "top_talents": [
        {"id": "T1", "name": "結構化執行", "score": 92.5},
        {"id": "T3", "name": "探索創新", "score": 88.0}
      ],
      "archetype": {
        "primary": "系統建構者",
        "confidence": 0.85
      }
    },
    {
      "session_id": "session_xyz789",
      "completed_at": "2025-09-15T10:20:00Z",
      "top_talents": [
        {"id": "T2", "name": "品質完備", "score": 90.0}
      ]
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 10,
    "total": 2,
    "pages": 1
  }
}
```

---

#### `GET /members/assessments/{session_id}`
**描述:** 查看特定評測的完整報告

**Headers:** `Authorization: Bearer {access_token}`

**回應 (200 OK):**
```json
{
  "session": {
    "session_id": "session_abc123",
    "started_at": "2025-10-01T14:00:00Z",
    "completed_at": "2025-10-01T14:30:00Z",
    "total_time_minutes": 15
  },
  "results": {
    "talents": [
      {"id": "T1", "name": "結構化執行", "score": 92.5, "category": "執行力"},
      {"id": "T3", "name": "探索創新", "score": 88.0, "category": "戰略思維"}
    ],
    "archetype": {
      "primary": "系統建構者",
      "secondary": "推廣實踐家",
      "confidence": 0.85
    },
    "report_url": "/api/reports/download/session_abc123.pdf"
  }
}
```

---

#### `POST /members/assessments/{session_id}/share`
**描述:** 生成評測報告分享連結

**Headers:** `Authorization: Bearer {access_token}`

**請求體:**
```json
{
  "expires_in_days": 7,
  "password_protected": false
}
```

**回應 (201 Created):**
```json
{
  "share_link": {
    "token": "share_token_abc123",
    "url": "https://gallup-strengths.com/share/share_token_abc123",
    "expires_at": "2025-10-10T16:30:00Z",
    "access_count": 0,
    "created_at": "2025-10-03T16:30:00Z"
  }
}
```

---

#### `DELETE /members/shares/{token}`
**描述:** 撤銷分享連結

**Headers:** `Authorization: Bearer {access_token}`

**回應 (204 No Content)**

---

### 5.4 會員儀表板 (Dashboard)

#### `GET /members/dashboard`
**描述:** 查看會員儀表板摘要

**Headers:** `Authorization: Bearer {access_token}`

**回應 (200 OK):**
```json
{
  "member": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "full_name": "張三",
    "member_since": "2025-10-03T10:00:00Z"
  },
  "statistics": {
    "total_assessments": 5,
    "completed_this_month": 1,
    "last_assessment_date": "2025-10-01T14:30:00Z"
  },
  "latest_results": {
    "session_id": "session_abc123",
    "top_3_talents": [
      {"id": "T1", "name": "結構化執行", "score": 92.5},
      {"id": "T3", "name": "探索創新", "score": 88.0},
      {"id": "T5", "name": "影響倡議", "score": 85.0}
    ],
    "archetype": "系統建構者"
  },
  "recommendations": [
    "根據您的「結構化執行」優勢，建議考慮專案管理或系統架構相關職位。",
    "您的「探索創新」才幹與研發工作高度契合。"
  ]
}
```

---

## 6. 安全性考量

### 6.1 速率限制 (Rate Limiting)
- **認證端點:** 5 次/分鐘 (防暴力破解)
- **一般端點:** 60 次/分鐘
- **回應 Header:**
  ```
  X-RateLimit-Limit: 60
  X-RateLimit-Remaining: 45
  X-RateLimit-Reset: 1633046400
  ```

### 6.2 HTTPS 強制
- 所有 API 強制使用 HTTPS (TLS 1.3+)
- HTTP 請求自動重導向至 HTTPS

### 6.3 CORS 設定
```json
{
  "allowed_origins": [
    "https://gallup-strengths.com",
    "https://staging.gallup-strengths.com"
  ],
  "allowed_methods": ["GET", "POST", "PUT", "PATCH", "DELETE"],
  "allowed_headers": ["Authorization", "Content-Type"],
  "max_age": 3600
}
```

---

## 7. API 版本控制

### 7.1 版本策略
- **URL 路徑版本:** `/api/v1/members/...`
- **向後兼容變更:** 不增加版本號 (新增可選參數、新增欄位)
- **破壞性變更:** 必須增加主版本號 (v1 → v2)

### 7.2 棄用政策
- 提前 6 個月通知
- 回應 Header 標註: `Deprecation: true`
- 提供遷移指南

---

**文件審核記錄:**

| 日期 | 審核人 | 版本 | 變更摘要 |
|:---|:---|:---|:---|
| 2025-10-03 | API 設計師 | v1.0 | 初稿完成 |

---

*本文件遵循 RESTful API 最佳實踐與 OpenAPI 3.0 規範。*
