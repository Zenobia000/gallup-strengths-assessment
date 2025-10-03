# WBS 開發計劃 (Work Breakdown Structure) - Gallup 優勢測驗會員系統

---

**文件版本 (Document Version):** `v1.0`
**最後更新 (Last Updated):** `2025-10-03`
**專案名稱 (Project):** Gallup 優勢測驗會員系統
**規劃週期 (Timeline):** 6 週 (2025-10-05 ~ 2025-11-15)
**狀態 (Status):** `規劃中 (Planning)`

---

## 目錄 (Table of Contents)

1. [專案總覽 (Project Overview)](#專案總覽-project-overview)
2. [開發里程碑 (Development Milestones)](#開發里程碑-development-milestones)
3. [Week 1: 基礎設施與資料層](#week-1-基礎設施與資料層)
4. [Week 2: 會員認證系統](#week-2-會員認證系統)
5. [Week 3: 會員資料與歷史管理](#week-3-會員資料與歷史管理)
6. [Week 4: 儀表板與前端整合](#week-4-儀表板與前端整合)
7. [Week 5: 安全性與合規](#week-5-安全性與合規)
8. [Week 6: 測試與部署準備](#week-6-測試與部署準備)
9. [關鍵路徑與依賴關係](#關鍵路徑與依賴關係)
10. [風險管理計劃](#風險管理計劃)

---

## 專案總覽 (Project Overview)

### 專案目標
建立完整的會員系統,支援使用者註冊、登入、個人檔案管理、評測歷史追蹤,並整合現有的 Gallup 優勢評測引擎。

### 技術架構
- **後端**: Python 3.11+, FastAPI 0.100+
- **資料庫**: SQLite (MVP), 預留 PostgreSQL 遷移路徑
- **認證**: JWT + HTTP-only Cookies, OAuth 2.0 (Google/Facebook)
- **前端**: TypeScript, React (假設), 響應式設計 (RWD)
- **外部服務**: SendGrid (Email), OAuth Providers

### 交付成果
1. 完整的會員 RESTful API (`/api/members/*`)
2. 資料庫 Schema 與遷移腳本
3. 前端會員管理介面 (註冊/登入/儀表板)
4. 單元測試 + 整合測試 (覆蓋率 ≥80%)
5. API 文檔 (OpenAPI/Swagger)
6. 部署腳本與文檔

---

## 開發里程碑 (Development Milestones)

| 里程碑 ID | 里程碑名稱 | 目標日期 | 關鍵交付成果 | 允收標準 |
|:---------|:----------|:--------|:-----------|:--------|
| **M1** | 資料層完成 | 2025-10-11 | 資料庫 Schema, 基礎 API | 可執行 CRUD 操作,通過 Schema 驗證 |
| **M2** | 認證系統完成 | 2025-10-18 | 註冊/登入 API, OAuth 整合 | 可完成完整認證流程,JWT 有效運作 |
| **M3** | 資料管理完成 | 2025-10-25 | 個人檔案 API, 歷史報告 API | 可查詢/編輯檔案,可綁定評測結果 |
| **M4** | 前端整合完成 | 2025-11-01 | 前端頁面, 儀表板 | 使用者可透過 UI 完成所有核心功能 |
| **M5** | 安全合規完成 | 2025-11-08 | 安全加固, GDPR 合規 | 通過安全檢查,符合合規要求 |
| **M6** | 生產就緒 | 2025-11-15 | 測試完成, 文檔完整 | UAT 通過 100%,可正式上線 |

---

## Week 1: 基礎設施與資料層

**目標**: 建立會員系統的資料基礎與 API 骨架

### 任務清單

| Task ID | 任務描述 | 負責人 | 預估時間 | 優先級 | 依賴項 | 允收標準 |
|:--------|:--------|:------|:--------|:------|:------|:---------|
| **W1-T001** | 設計會員資料庫 Schema | Backend Dev | 0.5 天 | P0 | 無 | ERD 圖完成,包含 members, auth_tokens, oauth_providers 表 |
| **W1-T002** | 建立 SQLite 資料庫初始化腳本 | Backend Dev | 0.5 天 | P0 | W1-T001 | 執行腳本後資料庫正確建立 |
| **W1-T003** | 實作資料庫遷移機制 (Alembic) | Backend Dev | 1 天 | P0 | W1-T002 | 可執行 `upgrade`/`downgrade`,版本追蹤正常 |
| **W1-T004** | 建立 Member 資料模型 (SQLAlchemy ORM) | Backend Dev | 1 天 | P0 | W1-T003 | 模型可正確映射資料庫表結構 |
| **W1-T005** | 建立 FastAPI 路由架構 (`/api/members`) | Backend Dev | 0.5 天 | P0 | 無 | 路由群組註冊完成,健康檢查端點正常 |
| **W1-T006** | 實作基礎 CRUD 工具函式 | Backend Dev | 1 天 | P1 | W1-T004 | 可對會員資料執行增刪改查 |
| **W1-T007** | 實作 bcrypt 密碼雜湊工具 | Backend Dev | 0.5 天 | P0 | 無 | 可正確加密/驗證密碼,cost factor = 12 |
| **W1-T008** | 建立 JWT Token 產生/驗證工具 | Backend Dev | 1 天 | P0 | 無 | 可生成有效 JWT,可驗證 signature 與過期時間 |

**Week 1 交付物**:
- ✅ 資料庫 Schema 文檔 (ERD)
- ✅ Alembic 遷移腳本
- ✅ SQLAlchemy 資料模型
- ✅ 基礎 API 路由架構
- ✅ 密碼與 Token 工具模組

**驗證方式**:
```bash
# 執行資料庫初始化
alembic upgrade head

# 執行基礎 API 測試
pytest src/test/unit/test_member_models.py -v
pytest src/test/unit/test_auth_utils.py -v

# 檢查 API 健康狀態
curl http://localhost:8000/api/members/health
```

---

## Week 2: 會員認證系統

**目標**: 實作完整的註冊/登入流程,支援 Email 與社交帳號

### 任務清單

| Task ID | 任務描述 | 負責人 | 預估時間 | 優先級 | 依賴項 | 允收標準 |
|:--------|:--------|:------|:--------|:------|:------|:---------|
| **W2-T001** | 實作 Email 註冊 API (`POST /api/members/register`) | Backend Dev | 1 天 | P0 | W1-T004, W1-T007 | 可成功建立帳號,密碼加密正確 |
| **W2-T002** | 實作 Email 驗證機制 (驗證碼/連結) | Backend Dev | 1.5 天 | P0 | W2-T001 | 可發送驗證郵件,點擊連結啟用帳號 |
| **W2-T003** | 實作 Email 登入 API (`POST /api/members/login`) | Backend Dev | 1 天 | P0 | W1-T007, W1-T008 | 正確帳密返回 JWT,錯誤帳密返回 401 |
| **W2-T004** | 實作 JWT 中間件 (Authentication Middleware) | Backend Dev | 1 天 | P0 | W1-T008 | 受保護端點需有效 JWT 才可存取 |
| **W2-T005** | 實作 Refresh Token 機制 | Backend Dev | 1 天 | P1 | W2-T003 | Access Token 過期後可用 Refresh Token 換新 |
| **W2-T006** | 整合 Google OAuth 2.0 | Backend Dev | 1.5 天 | P0 | W1-T004 | 可透過 Google 登入,首次自動建立會員 |
| **W2-T007** | 整合 Facebook Login | Backend Dev | 1.5 天 | P0 | W2-T006 | 可透過 Facebook 登入,首次自動建立會員 |
| **W2-T008** | 實作密碼找回 API (`POST /api/members/reset-password`) | Backend Dev | 1 天 | P0 | W1-T007 | 可發送重設連結,連結 1 小時有效 |
| **W2-T009** | 實作登出 API (`POST /api/members/logout`) | Backend Dev | 0.5 天 | P1 | W2-T004 | Token 失效,再次請求返回 401 |

**Week 2 交付物**:
- ✅ 完整認證 API 端點 (註冊/登入/登出/密碼找回)
- ✅ OAuth 整合 (Google + Facebook)
- ✅ JWT 認證中間件
- ✅ Email 驗證系統
- ✅ API 整合測試

**驗證方式**:
```bash
# 執行認證流程測試
pytest src/test/integration/test_member_auth.py -v

# 手動測試註冊流程
curl -X POST http://localhost:8000/api/members/register \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "SecurePass123"}'

# 測試 OAuth 流程 (需瀏覽器)
open http://localhost:8000/api/members/auth/google
```

**關鍵決策記錄**:
- JWT 有效期設為 7 天 (Access Token)
- Refresh Token 有效期 30 天
- 使用 HTTP-only Cookie 儲存 Token (防 XSS)
- OAuth 回調 URL: `/api/members/auth/{provider}/callback`

---

## Week 3: 會員資料與歷史管理

**目標**: 實作個人檔案管理與評測歷史綁定機制

### 任務清單

| Task ID | 任務描述 | 負責人 | 預估時間 | 優先級 | 依賴項 | 允收標準 |
|:--------|:--------|:------|:--------|:------|:------|:---------|
| **W3-T001** | 實作個人檔案 API (`GET/PUT /api/members/profile`) | Backend Dev | 1 天 | P0 | W2-T004 | 可查詢/更新姓名、職稱、產業等資料 |
| **W3-T002** | 實作 Email 變更機制 (需重新驗證) | Backend Dev | 1 天 | P1 | W3-T001 | 變更 Email 觸發驗證流程,舊 Email 同步失效 |
| **W3-T003** | 實作隱私設定 API (`GET/PUT /api/members/privacy`) | Backend Dev | 0.5 天 | P1 | W3-T001 | 可設定行銷郵件、資料研究同意選項 |
| **W3-T004** | 實作帳號刪除 API (`DELETE /api/members/account`) | Backend Dev | 1 天 | P0 | W3-T001 | 可刪除會員及所有相關資料 (GDPR) |
| **W3-T005** | 設計評測歷史資料關聯 Schema | Backend Dev | 0.5 天 | P0 | W1-T004 | 建立 member_assessments 關聯表 |
| **W3-T006** | 實作評測結果綁定 API | Backend Dev | 1 天 | P0 | W3-T005 | 匿名評測完成後可綁定至會員帳號 |
| **W3-T007** | 實作評測歷史列表 API (`GET /api/members/assessments`) | Backend Dev | 1 天 | P0 | W3-T006 | 返回時間軸排序的所有評測記錄 |
| **W3-T008** | 實作歷史報告下載 API (`GET /api/members/assessments/{id}/pdf`) | Backend Dev | 1 天 | P0 | W3-T007 | 可下載任意歷史報告的 PDF |
| **W3-T009** | 實作報告分享連結生成 API | Backend Dev | 1.5 天 | P0 | W3-T007 | 可生成有時效性的分享連結 (7/30/永久天) |
| **W3-T010** | 實作分享連結撤銷 API | Backend Dev | 0.5 天 | P1 | W3-T009 | 可撤銷已分享的連結 |

**Week 3 交付物**:
- ✅ 個人檔案管理 API
- ✅ 隱私設定與帳號刪除 API
- ✅ 評測歷史綁定機制
- ✅ 歷史報告下載與分享 API
- ✅ 整合測試

**驗證方式**:
```bash
# 執行資料管理測試
pytest src/test/integration/test_member_profile.py -v
pytest src/test/integration/test_assessment_history.py -v

# 測試評測綁定流程
curl -X POST http://localhost:8000/api/members/assessments/bind \
  -H "Authorization: Bearer {JWT}" \
  -H "Content-Type: application/json" \
  -d '{"assessment_id": "abc123"}'

# 測試歷史列表查詢
curl http://localhost:8000/api/members/assessments \
  -H "Authorization: Bearer {JWT}"
```

---

## Week 4: 儀表板與前端整合

**目標**: 建立會員儀表板後端邏輯與前端 UI 整合

### 任務清單

| Task ID | 任務描述 | 負責人 | 預估時間 | 優先級 | 依賴項 | 允收標準 |
|:--------|:--------|:------|:--------|:------|:------|:---------|
| **W4-T001** | 實作儀表板摘要 API (`GET /api/members/dashboard`) | Backend Dev | 1 天 | P0 | W3-T007 | 返回最新評測摘要、評測次數、主導才幹 |
| **W4-T002** | 實作才幹趨勢計算邏輯 | Backend Dev | 1.5 天 | P1 | W3-T007 | 可計算多次評測的才幹分數變化 |
| **W4-T003** | 實作個人化建議生成邏輯 | Backend Dev | 1 天 | P1 | W4-T001 | 基於最新評測生成職涯建議 |
| **W4-T004** | 整合 SendGrid Email 服務 | Backend Dev | 1 天 | P0 | W2-T002 | 可發送註冊驗證、密碼重設郵件 |
| **W4-T005** | 建立前端註冊/登入頁面 | Frontend Dev | 2 天 | P0 | W2-T003 | UI 完整,表單驗證正確,錯誤訊息友善 |
| **W4-T006** | 建立前端個人檔案管理頁面 | Frontend Dev | 1.5 天 | P0 | W3-T001 | 可編輯所有檔案欄位,即時更新 |
| **W4-T007** | 建立前端儀表板頁面 | Frontend Dev | 2 天 | P0 | W4-T001 | 顯示才幹摘要、評測統計、快速行動按鈕 |
| **W4-T008** | 建立前端評測歷史頁面 | Frontend Dev | 1.5 天 | P0 | W3-T007 | 顯示時間軸列表,可下載/分享報告 |
| **W4-T009** | 實作前端 OAuth 登入流程 | Frontend Dev | 1 天 | P0 | W2-T006, W2-T007 | Google/Facebook 登入按鈕運作正常 |
| **W4-T010** | 前後端整合測試 | Full Team | 1 天 | P0 | 全部 | 完整使用者流程可正常運作 |

**Week 4 交付物**:
- ✅ 儀表板 API 端點
- ✅ SendGrid Email 整合
- ✅ 前端會員管理介面 (所有頁面)
- ✅ 前後端整合測試通過
- ✅ 響應式設計 (手機/平板/桌面)

**驗證方式**:
```bash
# 啟動前端開發伺服器
npm run dev

# 執行端到端測試
npm run test:e2e

# 手動測試完整流程
1. 註冊新帳號 → 驗證 Email → 登入
2. 完成評測 → 查看儀表板
3. 編輯個人檔案 → 查看歷史記錄
4. 下載/分享報告 → 登出
```

---

## Week 5: 安全性與合規

**目標**: 強化系統安全性,確保符合 GDPR 與 OWASP 標準

### 任務清單

| Task ID | 任務描述 | 負責人 | 預估時間 | 優先級 | 依賴項 | 允收標準 |
|:--------|:--------|:------|:--------|:------|:------|:---------|
| **W5-T001** | 實作 API Rate Limiting 中間件 | Backend Dev | 1 天 | P0 | 無 | 防止暴力破解,限制同 IP 每分鐘請求數 |
| **W5-T002** | 實作 CORS 白名單機制 | Backend Dev | 0.5 天 | P0 | 無 | 僅允許信任來源的跨域請求 |
| **W5-T003** | 實作 SQL Injection 防護 | Backend Dev | 0.5 天 | P0 | W1-T004 | 使用參數化查詢,禁止字串拼接 SQL |
| **W5-T004** | 實作 XSS 防護 (輸入消毒) | Backend Dev | 0.5 天 | P0 | 無 | 所有使用者輸入經過 HTML escape |
| **W5-T005** | 實作 CSRF Token 機制 | Backend Dev | 1 天 | P0 | W2-T004 | 表單提交需攜帶有效 CSRF Token |
| **W5-T006** | 實作審計軌跡記錄 (Audit Log) | Backend Dev | 1 天 | P1 | 無 | 記錄敏感操作 (登入/登出/資料變更) |
| **W5-T007** | 實作 GDPR 資料匯出 API | Backend Dev | 1 天 | P0 | W3-T001 | 可匯出會員所有個人資料 (JSON) |
| **W5-T008** | 實作資料匿名化刪除邏輯 | Backend Dev | 1 天 | P0 | W3-T004 | 刪除帳號後評測資料匿名化保留 |
| **W5-T009** | 執行 OWASP Top 10 安全掃描 | Security Eng | 1 天 | P0 | 全部 | 無高風險漏洞 (High/Critical) |
| **W5-T010** | 執行滲透測試 (Penetration Testing) | Security Eng | 1.5 天 | P1 | W5-T009 | 無法繞過認證或存取他人資料 |

**Week 5 交付物**:
- ✅ Rate Limiting + CORS 中間件
- ✅ OWASP Top 10 防護措施
- ✅ GDPR 合規機制 (匯出/刪除)
- ✅ 審計軌跡系統
- ✅ 安全測試報告

**驗證方式**:
```bash
# 執行安全測試
pytest src/test/security/test_auth_security.py -v
pytest src/test/security/test_owasp_top10.py -v

# 執行自動化安全掃描
bandit -r src/main/python/api/
safety check

# 驗證 Rate Limiting
for i in {1..100}; do curl http://localhost:8000/api/members/login; done
# 預期: 第 61 次請求返回 429 Too Many Requests
```

---

## Week 6: 測試與部署準備

**目標**: 完善測試覆蓋率,撰寫文檔,準備正式部署

### 任務清單

| Task ID | 任務描述 | 負責人 | 預估時間 | 優先級 | 依賴項 | 允收標準 |
|:--------|:--------|:------|:--------|:------|:------|:---------|
| **W6-T001** | 補齊單元測試 (目標覆蓋率 ≥80%) | Backend Dev | 2 天 | P0 | 全部 | 所有核心模組有測試,覆蓋率達標 |
| **W6-T002** | 補齊整合測試 | Backend Dev | 1.5 天 | P0 | 全部 | 所有 API 端點有整合測試 |
| **W6-T003** | 執行端到端測試 (E2E) | QA | 1.5 天 | P0 | W4-T010 | 所有使用者故事有自動化 E2E 測試 |
| **W6-T004** | 執行 UAT (使用者驗收測試) | QA + PM | 1 天 | P0 | 全部 | PRD 中所有允收標準通過 |
| **W6-T005** | 執行性能測試 (P95 < 200ms) | QA | 1 天 | P0 | 全部 | 壓力測試 500 並發,P95 延遲達標 |
| **W6-T006** | 撰寫 API 文檔 (OpenAPI/Swagger) | Backend Dev | 1 天 | P0 | 全部 | 所有端點有完整說明與範例 |
| **W6-T007** | 撰寫部署文檔 | DevOps | 1 天 | P0 | 無 | 包含環境變數、啟動腳本、資料庫遷移步驟 |
| **W6-T008** | 建立 CI/CD Pipeline | DevOps | 1.5 天 | P1 | 無 | 推送到 main 自動執行測試與部署 |
| **W6-T009** | 準備生產環境配置 | DevOps | 1 天 | P0 | 無 | HTTPS 證書、環境變數、監控配置完成 |
| **W6-T010** | 執行災難恢復演練 | DevOps | 0.5 天 | P1 | W6-T009 | 可從備份恢復資料庫,RTO < 4 小時 |

**Week 6 交付物**:
- ✅ 完整測試套件 (單元 + 整合 + E2E)
- ✅ 測試覆蓋率報告 (≥80%)
- ✅ UAT 測試報告 (100% 通過)
- ✅ API 文檔 (Swagger UI)
- ✅ 部署文檔與腳本
- ✅ CI/CD Pipeline

**驗證方式**:
```bash
# 執行完整測試套件
pytest src/test/ --cov=src/main/python --cov-report=html -v

# 執行性能測試
locust -f tests/performance/locustfile.py --host=http://localhost:8000

# 檢查測試覆蓋率
open htmlcov/index.html

# 查看 API 文檔
open http://localhost:8000/docs
```

---

## 關鍵路徑與依賴關係

### 關鍵路徑 (Critical Path)
以下任務鏈構成專案的關鍵路徑,任何延遲將直接影響上線日期:

```
W1-T001 (Schema 設計)
  ↓
W1-T002 (資料庫初始化)
  ↓
W1-T004 (資料模型)
  ↓
W2-T001 (註冊 API)
  ↓
W2-T003 (登入 API)
  ↓
W2-T004 (JWT 中間件)
  ↓
W3-T006 (評測綁定)
  ↓
W3-T007 (歷史列表 API)
  ↓
W4-T001 (儀表板 API)
  ↓
W4-T005 (前端登入頁)
  ↓
W4-T010 (前後端整合)
  ↓
W6-T004 (UAT)
```

**總關鍵路徑時間**: 約 18.5 工作日 (留有緩衝)

### 可並行任務
以下任務可並行開發,減少總開發時間:
- **Week 2**: OAuth 整合 (W2-T006, W2-T007) 可與基礎認證並行
- **Week 3**: 個人檔案 API (W3-T001-T004) 與評測歷史 API (W3-T005-T010) 可並行
- **Week 4**: 前端開發 (W4-T005-T009) 與後端 API (W4-T001-T004) 可並行
- **Week 5**: 安全測試 (W5-T009-T010) 與合規實作 (W5-T007-T008) 可並行

---

## 風險管理計劃

### 高風險項目

| 風險 ID | 風險描述 | 機率 | 影響 | 緩解策略 | 應變計畫 |
|:-------|:--------|:-----|:-----|:--------|:---------|
| **R-001** | OAuth 整合失敗 (API 變更/憑證問題) | 中 | 高 | Week 2 初期驗證 OAuth 可行性,預留 2 天緩衝 | 降級至僅支援 Email 註冊 |
| **R-002** | SendGrid 服務中斷 | 低 | 中 | 準備備用 Email 服務商 (AWS SES) | 手動啟用會員,事後補發郵件 |
| **R-003** | 性能測試未達標 (P95 > 200ms) | 中 | 中 | Week 5 提前進行壓力測試,及早優化 | 加入快取層 (Redis),資料庫索引優化 |
| **R-004** | GDPR 合規不完整 | 低 | 高 | Week 5 請法務審核資料處理流程 | 延後上線,補齊合規要求 |
| **R-005** | 前後端整合問題 (API 契約不一致) | 中 | 中 | Week 1 定義 OpenAPI Spec,前後端共用 | 增加整合測試時間,快速迭代修復 |
| **R-006** | SQLite 效能瓶頸 | 低 | 中 | 定期監控查詢效能,優化 Schema | 提前遷移至 PostgreSQL |

### 風險監控
- **每週風險回顧**: 每週五檢視風險狀態,更新緩解進度
- **風險指標**: 關鍵路徑任務延遲 > 1 天觸發警報
- **快速升級機制**: 高影響風險立即通知 PM + TL

---

## 附錄 A: 資源分配

### 人力配置

| 角色 | 人數 | 週工作時間 | 主要任務 |
|:-----|:-----|:----------|:---------|
| Backend Developer | 2 | 40 hrs/週 | API 開發,資料庫設計,安全加固 |
| Frontend Developer | 1 | 40 hrs/週 | UI 實作,前端整合 |
| QA Engineer | 1 | 40 hrs/週 | 測試設計,自動化測試,UAT |
| DevOps Engineer | 0.5 | 20 hrs/週 | CI/CD,部署,監控 |
| Product Manager | 0.5 | 20 hrs/週 | 需求澄清,UAT 協調,上線規劃 |

**總人月**: 約 6 人月

---

## 附錄 B: 定義完成標準 (Definition of Done)

每個任務必須滿足以下標準才算完成:

### 程式碼標準
- ✅ 通過 CI 自動化測試 (單元 + 整合)
- ✅ 測試覆蓋率 ≥80% (針對新增程式碼)
- ✅ 通過程式碼審查 (Code Review)
- ✅ 符合專案 Coding Style (Linter 檢查通過)
- ✅ 無 Critical/High 等級安全漏洞

### 文檔標準
- ✅ API 端點有 OpenAPI 文檔
- ✅ 複雜邏輯有內聯註解
- ✅ 公開函式有 Docstring
- ✅ 資料庫變更有遷移腳本

### 提交標準
- ✅ 遵循 Conventional Commits 格式
- ✅ 提交訊息包含 Task ID
- ✅ 推送至 GitHub (備份)

---

## 附錄 C: 技術債務追蹤

| 債務 ID | 描述 | 類型 | 優先級 | 預估修復時間 | 計劃處理時間 |
|:-------|:-----|:-----|:------|:------------|:------------|
| **TD-001** | 資料庫索引優化 (members.email, assessments.created_at) | 性能 | P1 | 0.5 天 | Week 5 |
| **TD-002** | 評測對比分析功能 (Post-MVP) | 功能 | P2 | 3 天 | 下個迭代 |
| **TD-003** | 多語系支援 (i18n) | 功能 | P2 | 5 天 | 下個迭代 |
| **TD-004** | JWT Token 自動續期機制 | 功能 | P1 | 1 天 | Week 5 |

---

**專案狀態追蹤**: https://github.com/your-org/gallup-strengths/projects/member-system
**Slack 頻道**: #gallup-member-system
**每日站會**: 每天上午 10:00 (15 分鐘)
**週進度報告**: 每週五下午 5:00

---

*本 WBS 遵循 VibeCoding 開發流程,為會員系統建立了清晰的開發路徑與時程規劃。*
