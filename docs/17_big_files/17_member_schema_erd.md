# 會員系統資料庫 Schema 設計 (ERD)

---

**文件版本**: v1.0
**最後更新**: 2025-10-03
**設計者**: Backend Team
**狀態**: 已完成設計

---

## 1. 核心表設計

### 1.1 Members (會員主表)

**表名**: `members`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| member_id | VARCHAR(36) | UNIQUE, NOT NULL, INDEX | 外部會員ID (UUID) |
| email | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Email (唯一登入識別) |
| email_verified | BOOLEAN | NOT NULL, DEFAULT FALSE | Email驗證狀態 |
| email_verified_at | DATETIME | NULL | Email驗證時間 |
| password_hash | VARCHAR(255) | NULL | bcrypt密碼雜湊 (OAuth可為空) |
| full_name | VARCHAR(100) | NULL | 全名 |
| display_name | VARCHAR(50) | NULL | 顯示名稱 |
| job_title | VARCHAR(100) | NULL | 職稱 |
| industry | VARCHAR(50) | NULL | 產業 |
| company | VARCHAR(100) | NULL | 公司 |
| phone | VARCHAR(20) | NULL | 電話 |
| avatar_url | VARCHAR(500) | NULL | 頭像URL |
| account_status | VARCHAR(20) | NOT NULL, DEFAULT 'active' | 帳號狀態 (active/suspended/deleted) |
| account_type | VARCHAR(20) | NOT NULL, DEFAULT 'free' | 帳號類型 (free/premium/enterprise) |
| privacy_settings | JSON | NULL | 隱私設定 |
| preferences | JSON | NULL | 偏好設定 |
| last_login_at | DATETIME | NULL | 最後登入時間 |
| last_login_ip | VARCHAR(45) | NULL | 最後登入IP (IPv6支援) |
| login_count | INTEGER | NOT NULL, DEFAULT 0 | 登入次數 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 建立時間 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW() | 更新時間 |
| deleted_at | DATETIME | NULL | 軟刪除時間 |

**索引**:
- `idx_members_email` ON (email)
- `idx_members_member_id` ON (member_id)
- `idx_members_status_created` ON (account_status, created_at)

---

### 1.2 Email Verification Tokens (Email 驗證令牌)

**表名**: `email_verification_tokens`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| member_id | VARCHAR(36) | NOT NULL, FK(members.member_id) | 會員ID |
| token | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | 驗證令牌 (SHA256) |
| token_type | VARCHAR(20) | NOT NULL | 令牌類型 (email_verification/password_reset) |
| expires_at | DATETIME | NOT NULL | 過期時間 |
| used_at | DATETIME | NULL | 使用時間 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 建立時間 |

**索引**:
- `idx_verification_token` ON (token)
- `idx_verification_member_type` ON (member_id, token_type)

---

### 1.3 Auth Tokens (認證令牌 - Refresh Tokens)

**表名**: `auth_tokens`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| member_id | VARCHAR(36) | NOT NULL, FK(members.member_id) | 會員ID |
| token_hash | VARCHAR(255) | UNIQUE, NOT NULL, INDEX | Refresh Token雜湊值 |
| token_family | VARCHAR(36) | NOT NULL, INDEX | Token家族ID (防止重放攻擊) |
| is_revoked | BOOLEAN | NOT NULL, DEFAULT FALSE | 撤銷狀態 |
| revoked_at | DATETIME | NULL | 撤銷時間 |
| revoke_reason | VARCHAR(100) | NULL | 撤銷原因 |
| device_info | VARCHAR(500) | NULL | 裝置資訊 |
| ip_address | VARCHAR(45) | NULL | 發行IP |
| expires_at | DATETIME | NOT NULL | 過期時間 |
| last_used_at | DATETIME | NULL | 最後使用時間 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 建立時間 |

**索引**:
- `idx_auth_tokens_hash` ON (token_hash)
- `idx_auth_tokens_member` ON (member_id, is_revoked)
- `idx_auth_tokens_family` ON (token_family)

---

### 1.4 OAuth Providers (OAuth 提供商綁定)

**表名**: `oauth_providers`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| member_id | VARCHAR(36) | NOT NULL, FK(members.member_id) | 會員ID |
| provider | VARCHAR(20) | NOT NULL | 提供商 (google/facebook/line) |
| provider_user_id | VARCHAR(255) | NOT NULL | 提供商使用者ID |
| provider_email | VARCHAR(255) | NULL | 提供商Email |
| provider_data | JSON | NULL | 提供商額外資料 |
| access_token | TEXT | NULL | Access Token (加密存儲) |
| refresh_token | TEXT | NULL | Refresh Token (加密存儲) |
| token_expires_at | DATETIME | NULL | Token過期時間 |
| is_primary | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否為主要登入方式 |
| linked_at | DATETIME | NOT NULL, DEFAULT NOW() | 綁定時間 |
| last_used_at | DATETIME | NULL | 最後使用時間 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW() | 更新時間 |

**複合唯一約束**:
- UNIQUE (provider, provider_user_id)
- UNIQUE (member_id, provider)

**索引**:
- `idx_oauth_provider_user` ON (provider, provider_user_id)
- `idx_oauth_member` ON (member_id)

---

### 1.5 Member Assessments (會員評測關聯)

**表名**: `member_assessments`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| member_id | VARCHAR(36) | NOT NULL, FK(members.member_id) | 會員ID |
| session_id | VARCHAR(36) | NOT NULL, UNIQUE, INDEX | 評測會話ID (可關聯至v4_sessions或assessment_sessions) |
| assessment_type | VARCHAR(20) | NOT NULL | 評測類型 (v4/mini_ipip) |
| assessment_title | VARCHAR(200) | NULL | 自訂評測標題 |
| assessment_notes | TEXT | NULL | 會員自訂筆記 |
| is_favorite | BOOLEAN | NOT NULL, DEFAULT FALSE | 是否收藏 |
| visibility | VARCHAR(20) | NOT NULL, DEFAULT 'private' | 可見性 (private/public/shared) |
| linked_at | DATETIME | NOT NULL, DEFAULT NOW() | 綁定時間 |
| completed_at | DATETIME | NULL | 完成時間 (冗餘,方便查詢) |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 建立時間 |
| updated_at | DATETIME | NOT NULL, DEFAULT NOW() | 更新時間 |

**索引**:
- `idx_member_assessments_member` ON (member_id, completed_at DESC)
- `idx_member_assessments_session` ON (session_id)

---

### 1.6 Share Links (分享連結管理)

**表名**: `share_links`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| share_id | VARCHAR(36) | UNIQUE, NOT NULL, INDEX | 分享ID (UUID) |
| member_id | VARCHAR(36) | NOT NULL, FK(members.member_id) | 會員ID (擁有者) |
| session_id | VARCHAR(36) | NOT NULL, FK(member_assessments.session_id) | 評測會話ID |
| share_token | VARCHAR(64) | UNIQUE, NOT NULL, INDEX | 分享令牌 (隨機生成) |
| link_type | VARCHAR(20) | NOT NULL, DEFAULT 'view_only' | 連結類型 (view_only/download) |
| access_password | VARCHAR(255) | NULL | 存取密碼雜湊 (可選) |
| expires_at | DATETIME | NULL | 過期時間 (NULL=永久) |
| max_access_count | INTEGER | NULL | 最大存取次數 (NULL=無限制) |
| access_count | INTEGER | NOT NULL, DEFAULT 0 | 實際存取次數 |
| is_revoked | BOOLEAN | NOT NULL, DEFAULT FALSE | 撤銷狀態 |
| revoked_at | DATETIME | NULL | 撤銷時間 |
| revoke_reason | VARCHAR(200) | NULL | 撤銷原因 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 建立時間 |
| last_accessed_at | DATETIME | NULL | 最後存取時間 |

**索引**:
- `idx_share_links_token` ON (share_token)
- `idx_share_links_member` ON (member_id, created_at DESC)
- `idx_share_links_session` ON (session_id)

---

### 1.7 Audit Logs (審計軌跡)

**表名**: `audit_logs`

| 欄位名稱 | 類型 | 約束 | 說明 |
|:--------|:-----|:-----|:-----|
| id | INTEGER | PRIMARY KEY, AUTOINCREMENT | 內部主鍵 |
| member_id | VARCHAR(36) | NULL, FK(members.member_id) | 會員ID (可為空,如登入失敗) |
| action | VARCHAR(50) | NOT NULL | 操作類型 (login/logout/profile_update/password_change等) |
| action_category | VARCHAR(20) | NOT NULL | 操作類別 (auth/profile/assessment/admin) |
| entity_type | VARCHAR(50) | NULL | 實體類型 (member/assessment/share_link等) |
| entity_id | VARCHAR(36) | NULL | 實體ID |
| ip_address | VARCHAR(45) | NOT NULL | 操作IP |
| user_agent | VARCHAR(500) | NULL | User Agent |
| request_method | VARCHAR(10) | NULL | HTTP方法 (GET/POST等) |
| request_path | VARCHAR(500) | NULL | 請求路徑 |
| status | VARCHAR(20) | NOT NULL | 狀態 (success/failure/error) |
| error_message | TEXT | NULL | 錯誤訊息 |
| metadata | JSON | NULL | 額外元資料 |
| created_at | DATETIME | NOT NULL, DEFAULT NOW() | 建立時間 |

**索引**:
- `idx_audit_logs_member` ON (member_id, created_at DESC)
- `idx_audit_logs_action` ON (action, created_at DESC)
- `idx_audit_logs_category_status` ON (action_category, status, created_at DESC)

---

## 2. 關聯關係圖

```
┌────────────────┐
│    Members     │ 1──────────────┐
│  (會員主表)     │                │
└────────────────┘                │
        │ 1                        │
        │                          │
        │ N                        │ N
        ▼                          ▼
┌──────────────────┐      ┌─────────────────────┐
│  Email Verify    │      │   Member            │
│  Tokens          │      │   Assessments       │ 1
│  (驗證令牌)       │      │  (評測關聯)          │───┐
└──────────────────┘      └─────────────────────┘   │
                                   │                 │
        ┌──────────────────────────┤                 │
        │                          │                 │
        │ N                        │ 1               │ N
        ▼                          ▼                 ▼
┌───────────────┐          ┌──────────────┐  ┌─────────────┐
│  Auth Tokens  │          │  V4Sessions  │  │ Share Links │
│ (Refresh令牌) │          │  or          │  │ (分享連結)   │
└───────────────┘          │  Assessment  │  └─────────────┘
        │ N                │  Sessions    │
        │                  └──────────────┘
        │
        └─> Members (FK)

┌─────────────────┐
│ OAuth Providers │ N
│ (OAuth綁定)     │───> Members (FK)
└─────────────────┘

┌──────────────┐
│  Audit Logs  │ N
│  (審計軌跡)   │───> Members (FK, 可為NULL)
└──────────────┘
```

---

## 3. 資料字典

### 3.1 Enum 定義

#### account_status (帳號狀態)
- `active`: 啟用中
- `suspended`: 暫停使用
- `deleted`: 已刪除 (軟刪除)

#### account_type (帳號類型)
- `free`: 免費會員
- `premium`: 付費會員
- `enterprise`: 企業會員

#### token_type (令牌類型)
- `email_verification`: Email驗證
- `password_reset`: 密碼重設

#### provider (OAuth提供商)
- `google`: Google
- `facebook`: Facebook
- `line`: LINE (未來支援)

#### assessment_type (評測類型)
- `v4`: V4.0 Thurstonian IRT評測
- `mini_ipip`: Mini-IPIP 20題評測

#### visibility (可見性)
- `private`: 私人 (僅會員本人)
- `public`: 公開 (所有人可見)
- `shared`: 已分享 (透過連結可見)

#### link_type (分享連結類型)
- `view_only`: 僅檢視
- `download`: 允許下載

#### action_category (操作類別)
- `auth`: 認證相關 (登入/登出)
- `profile`: 檔案相關 (更新資料)
- `assessment`: 評測相關 (綁定/分享)
- `admin`: 管理操作

---

## 4. 資料完整性規則

### 4.1 外鍵約束 (Foreign Key Constraints)
- `email_verification_tokens.member_id` → `members.member_id` (ON DELETE CASCADE)
- `auth_tokens.member_id` → `members.member_id` (ON DELETE CASCADE)
- `oauth_providers.member_id` → `members.member_id` (ON DELETE CASCADE)
- `member_assessments.member_id` → `members.member_id` (ON DELETE CASCADE)
- `share_links.member_id` → `members.member_id` (ON DELETE CASCADE)
- `audit_logs.member_id` → `members.member_id` (ON DELETE SET NULL)

### 4.2 唯一約束 (Unique Constraints)
- `members.email` (唯一Email)
- `members.member_id` (唯一會員ID)
- `oauth_providers.(provider, provider_user_id)` (同一提供商的使用者ID唯一)
- `oauth_providers.(member_id, provider)` (一個會員對同一提供商只能綁定一次)

### 4.3 檢查約束 (Check Constraints)
- `members.account_status` IN ('active', 'suspended', 'deleted')
- `members.account_type` IN ('free', 'premium', 'enterprise')
- `auth_tokens.expires_at` > NOW()
- `share_links.access_count` <= `share_links.max_access_count` (當max_access_count不為NULL時)

---

## 5. 安全性設計

### 5.1 敏感資料加密
- **密碼**: 使用 bcrypt (cost factor = 12)
- **OAuth Tokens**: 使用 AES-256-GCM 加密存儲
- **分享密碼**: 使用 bcrypt 雜湊

### 5.2 令牌管理
- **Access Token (JWT)**: 7天有效期, 無狀態, 存於HTTP-only Cookie
- **Refresh Token**: 30天有效期, 存於資料庫, 支援撤銷
- **Email驗證令牌**: 24小時有效期, 單次使用
- **密碼重設令牌**: 1小時有效期, 單次使用

### 5.3 審計軌跡
所有敏感操作記錄至 `audit_logs`:
- 登入/登出
- 密碼變更
- Email變更
- 帳號刪除
- OAuth綁定/解綁
- 評測分享建立/撤銷

---

## 6. 性能優化

### 6.1 索引策略
- **高頻查詢欄位**: email, member_id, token
- **複合索引**: (member_id, created_at) 用於歷史查詢
- **部分索引**: (is_revoked = FALSE) 用於活躍令牌查詢

### 6.2 資料分區 (未來考慮)
- 審計日誌按月分區
- 軟刪除會員資料歸檔

### 6.3 快取策略
- 會員基本資料 (Redis, TTL=15分鐘)
- OAuth提供商資料 (Redis, TTL=1小時)
- 評測歷史列表 (Redis, TTL=5分鐘)

---

## 7. GDPR 合規設計

### 7.1 資料主體權利
- **存取權**: 提供完整資料匯出API (`GET /api/members/data-export`)
- **更正權**: 支援所有欄位更新
- **刪除權**: 軟刪除 + 資料匿名化
- **可攜權**: JSON格式匯出

### 7.2 資料保留政策
- **活躍會員**: 無限期保留
- **已刪除會員**: 90天後永久刪除
- **審計日誌**: 保留1年
- **評測結果**: 隨會員刪除而匿名化 (保留統計用途)

---

## 8. 遷移計劃

### Phase 1: 核心表建立
- members, email_verification_tokens, auth_tokens

### Phase 2: OAuth與評測整合
- oauth_providers, member_assessments

### Phase 3: 分享與審計
- share_links, audit_logs

### Phase 4: 索引與優化
- 建立所有索引
- 效能測試與調整

---

**ERD 版本**: v1.0
**審核狀態**: 待技術負責人審核
**下一步**: 實作 SQLAlchemy ORM 模型
