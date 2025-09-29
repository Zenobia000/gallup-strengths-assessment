# Gallup 優勢測驗 - 安全與隱私檢查清單

---

**文件版本:** v1.0
**最後更新:** 2025-09-30
**審查人員:** 技術負責人, 安全顧問
**狀態:** 審核中 (In Review)

---

**審查對象:** Gallup 優勢測驗 MVP v1.0
**審查日期:** 2025-09-30
**相關文檔:** [架構設計](../architecture/architecture_design.md)

---

## A. 核心安全原則

- [x] **最小權限:** SQLite 檔案權限限制為應用程式用戶
- [x] **縱深防禦:** API 驗證 + 資料庫約束 + 業務邏輯檢查
- [x] **預設安全:** 所有 API 預設需要 HTTPS
- [x] **攻擊面最小化:** 僅開放必要的 API 端點
- [ ] **職責分離:** 目前單體架構，Phase 2 考慮

---

## B. 數據生命週期安全與隱私

### B.1 數據分類與收集

- [x] **數據分類:**
  - 公開: 問卷題目、優勢定義
  - 內部: 匿名統計數據
  - 機密: 用戶回答、session_id
  - PII: IP 位址（若記錄）

- [x] **數據最小化:**
  - ✅ 僅收集測驗必要欄位
  - ✅ 不收集姓名、電子郵件
  - ✅ Session ID 為匿名標識

- [x] **用戶同意:**
  - ✅ 首頁明確隱私條款
  - ✅ API 強制檢查 `consent_given=True`
  - ✅ 提供資料刪除機制

### B.2 數據傳輸

- [ ] **傳輸加密:**
  - ⚠️ Development: HTTP (localhost)
  - ✅ Production: HTTPS only (Nginx + Let's Encrypt)
  - 🔧 Action: 確保 HSTS header

- [x] **內部傳輸:**
  - ✅ 單體架構，無網路通訊
  - N/A 服務間加密

- [ ] **證書管理:**
  - 🔧 Action: 設定 Certbot 自動更新
  - 🔧 Action: 監控證書過期告警

### B.3 數據儲存

- [ ] **儲存加密:**
  - ⚠️ SQLite 預設無加密
  - 🔧 Action: 評估 SQLCipher 或檔案系統層加密
  - ✅ 密碼/Token 使用 bcrypt (若有)

- [ ] **金鑰管理:**
  - 🔧 Action: PDF 分享 token 使用環境變數存儲 secret
  - 🔧 Action: 定期輪換 JWT secret (Phase 2)

- [x] **數據備份:**
  - 🔧 Action: 實作每日 SQLite 備份腳本
  - 🔧 Action: 備份檔案加密存儲

### B.4 數據使用與處理

- [x] **日誌安全:**
  - ✅ 使用結構化日誌（JSON）
  - ✅ 不記錄問卷回答內容
  - ✅ Session ID 部分遮罩（前8碼）

- [x] **第三方共享:**
  - ✅ 無第三方 API 整合
  - N/A 資料共享協議

### B.5 數據保留與銷毀

- [x] **保留策略:**
  - 30天: 完整測驗紀錄
  - 7天: PDF 分享連結
  - 永久: 匿名統計（僅計數）

- [ ] **安全銷毀:**
  - 🔧 Action: 實作定期清理過期資料的 Cron Job
  - 🔧 Action: 刪除操作使用 SQLite VACUUM

---

## C. 應用程式安全

### C.1 身份驗證

- [x] **Session 管理:**
  - ✅ 使用 UUID v4 作為 session_id
  - ✅ 無狀態設計，不需 cookie
  - N/A 密碼認證（匿名系統）

- [x] **暴力破解防護:**
  - 🔧 Action: API 加入 rate limiting (slowapi)
  - 🔧 Action: 監控異常請求頻率

### C.2 授權與訪問控制

- [x] **物件級別授權:**
  - ✅ Session ID 作為唯一標識
  - ✅ 無法猜測他人 session_id (UUID)

- [x] **功能級別授權:**
  - ✅ 提交回答需有效 session_id
  - ✅ 查看結果需完成測驗

### C.3 輸入驗證與輸出編碼

- [x] **防止注入攻擊:**
  - ✅ 使用 SQLAlchemy ORM（自動參數化）
  - ✅ Pydantic 自動驗證輸入
  - ✅ 無原生 SQL 拼接

- [x] **防止 XSS:**
  - ✅ FastAPI 自動 JSON 轉義
  - ✅ PDF 生成使用 ReportLab（非 HTML）
  - N/A 前端 CSP（純 API）

- [x] **防止 CSRF:**
  - ✅ 無狀態 API，無 cookie 認證
  - N/A CSRF token

### C.4 API 安全

- [x] **API 認證:**
  - ✅ Session-based 驗證
  - 🔧 Action: 考慮加入 API Key (Phase 2)

- [ ] **速率限制:**
  - 🔧 Action: 使用 slowapi 限制每 IP 請求頻率
  - 目標: 100 req/min per IP

- [x] **參數校驗:**
  - ✅ Pydantic BaseModel 驗證所有輸入
  - ✅ 分數範圍 1-5 強制檢查
  - ✅ Session ID UUID 格式驗證

- [x] **避免資料過度暴露:**
  - ✅ API 回傳使用 DTO (Pydantic schema)
  - ✅ 不回傳完整資料庫物件

### C.5 依賴庫安全

- [ ] **漏洞掃描:**
  - 🔧 Action: 加入 `pip-audit` 至 CI/CD
  - 🔧 Action: 啟用 GitHub Dependabot

- [ ] **更新策略:**
  - 🔧 Action: 每月檢查依賴更新
  - 🔧 Action: 設定自動化 PR for security patches

---

## D. 基礎設施與運維安全

### D.1 網路安全

- [ ] **防火牆:**
  - 🔧 Action: 僅開放 80/443 port
  - 🔧 Action: 使用 UFW 設定規則

- [ ] **DDoS 防護:**
  - 🔧 Action: Cloudflare proxy (Phase 2)
  - 🔧 Action: Nginx rate limiting

### D.2 機密管理

- [x] **安全儲存:**
  - ✅ 使用 `.env` 檔案（不進版控）
  - ✅ Production 使用環境變數
  - ✅ `.gitignore` 包含 `.env`, `*.db`

- [ ] **權限與輪換:**
  - 🔧 Action: 定期更換資料庫密碼（若用 PostgreSQL）
  - N/A 當前 SQLite 無密碼

### D.3 容器安全

- [ ] **最小化基礎鏡像:**
  - 🔧 Action: 使用 `python:3.11-slim` 基底
  - 🔧 Action: Multi-stage build 減少攻擊面

- [ ] **非 Root 運行:**
  - 🔧 Action: Dockerfile 加入 `USER appuser`

- [ ] **鏡像掃描:**
  - 🔧 Action: GitHub Actions 整合 Trivy 掃描

### D.4 日誌與監控

- [ ] **安全事件日誌:**
  - ✅ 記錄所有 API 請求
  - 🔧 Action: 加入失敗請求告警

- [ ] **安全告警:**
  - 🔧 Action: 設定異常流量監控
  - 🔧 Action: Sentry 錯誤追蹤整合

---

## E. 合規性

- [x] **GDPR 基本合規:**
  - ✅ 明確同意機制
  - ✅ 資料最小化原則
  - 🔧 Action: 實作「被遺忘權」API
  - 🔧 Action: 提供資料匯出功能

- [x] **無 PII 儲存:**
  - ✅ 系統不收集姓名/Email
  - ✅ Session ID 匿名化

---

## F. 審查結論與行動項

### 主要風險

| # | 風險描述 | 評級 | 狀態 |
|:-:|:---------|:-----|:-----|
| 1 | SQLite 資料未加密 | 中 | 🔧 待處理 |
| 2 | 無 API rate limiting | 高 | 🔧 待處理 |
| 3 | 備份策略未實作 | 中 | 🔧 待處理 |
| 4 | 容器以 root 運行 | 中 | 🔧 待處理 |
| 5 | 無依賴漏洞掃描 | 中 | 🔧 待處理 |

### 行動項

| # | 行動項 | 負責人 | 預計完成 | 狀態 |
|:-:|:-------|:-------|:---------|:-----|
| 1 | 實作 API rate limiting (slowapi) | 開發團隊 | 2025-10-05 | ⏳ 待辦 |
| 2 | 加入 pip-audit 至 CI/CD | DevOps | 2025-10-07 | ⏳ 待辦 |
| 3 | Dockerfile 非 root 用戶設定 | DevOps | 2025-10-10 | ⏳ 待辦 |
| 4 | 實作資料刪除 API | 開發團隊 | 2025-10-15 | ⏳ 待辦 |
| 5 | SQLite 備份 Cron Job | DevOps | 2025-10-20 | ⏳ 待辦 |

### 整體評估

**結論:**
- ✅ 核心安全設計合理
- ⚠️ 需完成 5 個高優先級行動項
- 🚀 建議完成行動項 1-3 後可進行內部測試
- 🔒 生產環境上線前必須完成所有行動項

---

## G. 生產準備就緒

### G.1 可觀測性

- [ ] **監控儀表板:** 🔧 Grafana + Prometheus (Phase 2)
- [x] **核心指標:** ✅ FastAPI `/metrics` endpoint
- [x] **日誌:** ✅ 結構化日誌（JSON）
- [ ] **追蹤:** 🔧 OpenTelemetry (Phase 2)
- [ ] **告警:** 🔧 Sentry 整合

### G.2 可靠性與彈性

- [x] **健康檢查:** ✅ `/health` endpoint
- [ ] **優雅關閉:** 🔧 處理 SIGTERM 信號
- [ ] **重試機制:** N/A（無外部依賴）
- [ ] **備份恢復:** 🔧 待實作

### G.3 性能與可擴展性

- [ ] **負載測試:** 🔧 使用 Locust 測試 1000 並發
- [ ] **容量規劃:** 🔧 評估 VPS 規格需求
- [x] **水平擴展:** ✅ 無狀態設計支援

### G.4 可維護性與文檔

- [x] **部署文檔:** ✅ README.md 包含部署指南
- [ ] **CI/CD:** 🔧 GitHub Actions 待建立
- [x] **配置管理:** ✅ `.env` 檔案分離
- [ ] **Feature Flags:** 🔧 Phase 2 考慮

---

**簽署:**
- **安全審查:** _______________ (待簽署)
- **專案負責人:** _______________ (待簽署)

---

**下次審查:** 完成所有行動項後（預計 2025-10-25）