# Gallup 優勢測驗系統 v4.0

**企業級心理測量與優勢分析平台**

> **專案狀態**: v4.0 Thurstonian IRT 模型升級中 (2025-09-30)
> **核心目標**: 提供科學化、可解釋的優勢分析與職涯發展建議

## 🎯 產品特色

### 核心功能
- **📊 雙軌評估系統**
  - v3.0: Mini-IPIP 傳統李克特量表 (20題 + 情境題)
  - v4.0: Thurstonian IRT 迫選式問卷 (60題四選二)
- **🧠 統一知識庫** - CareerKnowledgeBase 單一資料來源
- **🎯 12維度優勢模型** - 完整心理測量映射系統
- **📈 常模化分數** - 百分位、T分數、九分量表
- **💼 職涯匹配引擎** - 智能職位推薦與發展建議
- **📄 即時報告生成** - PDF/HTML 多格式輸出
- **🔒 企業級安全** - GDPR 合規、完整審計軌跡
- **⚡ 高效能架構** - FastAPI + SQLite WAL 模式

## 🚀 技術架構

### 核心技術
- **FastAPI** (Python 3.11+) - 非同步高效能 API 框架
- **SQLite** (WAL 模式) - 生產級輕量資料庫
- **NumPy/SciPy** - 科學計算與 IRT 模型
- **Pydantic** - 強型別資料驗證
- **ReportLab** - 專業 PDF 報告生成

### 心理測量模型
- **v3.0**: Classical Test Theory (CTT)
- **v4.0**: Thurstonian Item Response Theory (IRT)
  - 最大似然估計 (MLE)
  - 期望後驗估計 (EAP)
  - 邊際最大似然校準 (MMLE)

### 專案結構
```
src/main/python/
├── core/
│   ├── scoring/           # v3.0 CTT 計分引擎
│   ├── v4/                # v4.0 IRT 模型
│   │   ├── irt_scorer.py      # Thurstonian IRT 計分
│   │   ├── block_designer.py  # 區組設計演算法
│   │   ├── irt_calibration.py # 參數校準 EM 演算法
│   │   └── normative_scoring.py # 常模轉換
│   ├── recommendation/    # 推薦引擎
│   └── knowledge/         # 統一知識庫
├── models/                # 資料模型
│   ├── schemas.py         # Pydantic schemas
│   └── v4/                # v4.0 迫選模型
├── api/                   # REST API
│   ├── routes/
│   │   ├── v4_assessment.py  # v4.0 端點
│   │   └── recommendations.py # 推薦端點
│   └── main.py           # FastAPI 應用
├── services/              # 業務服務層
├── data/                  # 資料檔案
│   ├── v4_statements.py   # 60 題陳述句庫
│   └── v4_normative_data.json # 常模資料
└── utils/                 # 工具函式
    └── migrations/        # 資料庫遷移
```

## 📊 12個優勢面向系統

### 面向定義 (自有命名)
1. **結構化執行** (+C, −N) - 系統性任務處理能力
2. **品質與完備** (+C, +A, −N) - 細節注重與完整性
3. **探索與創新** (+O, +E) - 新想法發掘能力
4. **分析與洞察** (+O, −N) - 資訊分析判斷力
5. **影響與倡議** (+E, −N) - 領導影響他人
6. **協作與共好** (+A, +H) - 團隊合作精神
7. **客戶導向** (+A, +E) - 服務他人意識
8. **學習與成長** (+O, +C) - 持續學習動機
9. **紀律與信任** (+H, +C) - 可靠性與誠信
10. **壓力調節** (−N, +C) - 壓力管理能力
11. **衝突整合** (+A, +E, −N) - 衝突處理技巧
12. **責任與當責** (+H, +C, −N) - 承擔責任意識

### 計分公式
```
S_k = Σ(w_k,d * z_d) + b_k  → [0-100]

其中：
- z_d: 人格向度標準化分數 (E/A/C/N/O/H)
- w_k,d: 面向k對向度d的權重
- b_k: 基準偏移值
```

## 📋 版本路線圖

### v3.0 (已完成) - 傳統 CTT 模型
- ✅ Mini-IPIP 李克特量表 (20題)
- ✅ Big Five 人格維度計分
- ✅ 12 維度優勢映射
- ✅ 情境問題增強
- ✅ 統一知識庫 CareerKnowledgeBase
- ✅ 職涯推薦與發展建議

### v4.0 (開發中) - Thurstonian IRT 模型
- 🔄 迫選式問卷設計 (60題四選二)
- 🔄 區組設計演算法 (BIBD)
- 🔄 IRT 參數校準 (EM 演算法)
- 🔄 常模化分數轉換
- 🔄 API v4 端點整合
- ⬜ A/B 測試框架
- ⬜ 小規模預測試

### v5.0 (規劃中) - 企業版
- ⬜ 多租戶支援
- ⬜ 團隊分析儀表板
- ⬜ API 商業授權
- ⬜ 雲端部署

## 🔧 開發指南

### 環境設置
```bash
# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 快速啟動系統

#### 方式一：使用啟動腳本 (推薦)
```bash
# 啟動後端 API 服務
python3 scripts/utilities/run_dev.py

# 啟動前端服務器
cd src/main/resources/static
python3 -m http.server 3000
```

#### 方式二：直接使用 uvicorn
```bash
# 啟動後端 API 服務
cd src/main/python
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8004 --reload

# 啟動前端服務器
cd src/main/resources/static
python3 -m http.server 3000
```

### 🌐 系統訪問地址

#### 前端服務器 (Port 3000)
- **主頁**: http://localhost:3000
- **v3.0 測驗界面**: http://localhost:3000/assessment.html
- **v4.0 先導測試**: http://localhost:3000/v4_pilot_test.html
- **結果展示**: http://localhost:3000/results.html

#### 後端 API 服務 (Port 8004)
- **FastAPI 應用根目錄**: http://localhost:8004/
- **v3.0 測驗頁面**: http://localhost:8004/assessment
- **v4.0 先導測試頁面**: http://localhost:8004/v4-pilot
- **健康檢查**: http://localhost:8004/api/v1/health
- **API 文檔**: http://localhost:8004/api/v1/docs
- **OpenAPI Schema**: http://localhost:8004/api/v1/openapi.json

#### API 端點總覽
- **v3.0 評估系統**
  - `GET /api/v1/questions` - 獲取測驗題目
  - `POST /api/v1/consent` - 記錄用戶同意
  - `POST /api/v1/sessions/start` - 開始測驗會話
  - `POST /api/v1/scoring/submit` - 提交答案計分
  - `GET /api/v1/results/{session_id}` - 獲取測驗結果

- **v4.0 Thurstonian IRT 系統**
  - `GET /api/v4/blocks` - 獲取迫選題組
  - `POST /api/v4/sessions` - 創建 v4 會話
  - `POST /api/v4/submit` - 提交 v4 答案
  - `POST /api/v4/data-collection/participants/register` - 註冊參與者
  - `POST /api/v4/data-collection/sessions/start` - 開始資料收集
  - `GET /api/v4/data-collection/stats` - 獲取收集統計

### 📝 使用操作說明

#### 完整測驗流程
1. **開始測驗**
   - 訪問 http://localhost:3000
   - 點擊「開始測驗」按鈕

2. **同意條款**
   - 閱讀隱私政策和使用條款
   - 填寫基本資訊（姓名、年齡、性別）
   - 點擊「同意並繼續」

3. **完成評估**
   - 誠實回答 20 道問題
   - 每題選擇 1-5 分 (1=非常不同意, 5=非常同意)
   - 建議在 15-20 分鐘內完成

4. **查看結果**
   - 系統自動計算 Big Five 人格特質分數
   - 顯示 Gallup 優勢主題推薦
   - 提供詳細的職涯發展建議

5. **下載報告**
   - 點擊「下載 PDF 報告」
   - 獲得專業的個人化分析報告

### 🔧 開發與測試

#### 運行測試套件
```bash
# 運行所有測試
python scripts/run_tests.py all

# 僅運行端到端測試
python scripts/run_tests.py e2e

# 僅運行效能測試
python scripts/run_tests.py performance

# 僅運行單元測試
python scripts/run_tests.py unit

# 檢查測試依賴
python scripts/run_tests.py --check-deps

# 生成覆蓋率報告
python scripts/run_tests.py coverage
```

#### API 測試
```bash
# 健康檢查
curl http://localhost:8004/api/v1/health

# 獲取問題
curl http://localhost:8004/api/v1/questions

# 檢視 API 文檔
# 瀏覽器訪問: http://localhost:8004/api/v1/docs
```

### 🛠️ 故障排除

#### 常見問題

1. **提交失敗，請稍後再試**
   ```bash
   # 使用清除工具重置會話
   # 瀏覽器訪問: http://localhost:3000/clear_session.html
   # 點擊 "Clear All Storage" 然後 "Test New Flow"
   ```

2. **端口被占用**
   ```bash
   # 檢查端口使用情況
   netstat -tulpn | grep :8004
   netstat -tulpn | grep :3000

   # 終止占用的進程
   pkill -f "uvicorn.*api.main"
   pkill -f "http.server"
   ```

2. **無法載入問題**
   - 確認後端 API 服務正在運行
   - 檢查前端 API 配置 (src/main/resources/static/js/api.js)
   - 確認網路連接正常

3. **資料庫錯誤**
   ```bash
   # 檢查資料庫文件
   ls -la *.db

   # 重新初始化資料庫
   python3 -c "from utils.database import init_db; init_db()"
   ```

### 📊 系統監控

#### 檢查服務狀態
```bash
# 檢查所有服務
curl -s http://localhost:8004/api/v1/health | python3 -m json.tool

# 檢查快取狀態
curl -s http://localhost:8004/api/v1/cache/health | python3 -m json.tool

# 檢查快取統計
curl -s http://localhost:8004/api/v1/cache/stats | python3 -m json.tool
```

## 📊 API 端點設計

### 核心流程端點
- `POST /consent` - 記錄用戶同意
- `POST /session/start` - 建立作答Session
- `GET /instrument/{name}/items` - 獲取題目
- `POST /session/submit` - 提交答案並計分
- `POST /decision/{session_id}` - 生成決策建議
- `GET /report/{session_id}.pdf` - 下載PDF報告

## 🛡️ 隱私與合規

### 資料保護措施
- **最小化原則** - 僅收集必要資料
- **同意記錄** - 完整同意流程與時間戳記
- **審計軌跡** - 所有操作可追溯
- **資料加密** - 敏感資料加密存儲
- **限時分享** - 一次性/時效性分享連結

## 📈 成功指標

### 技術指標
- 可用性: >90% 用戶 ≤5分鐘完成並獲取報告
- 錯誤率: <1%
- 效能: PDF生成 <1秒

### 業務指標
- 決策價值: 管理者/教練滿意度 ≥4.5/5
- 採納率: 建議被採納 ≥70% (7日內)
- 可解釋性: 所有建議可回溯到分數、權重、規則ID

## 🔄 最新實作狀態 (2025-09-30)

### ✅ 已完成功能
- **完整測驗流程** - 同意→問題→提交→結果 端到端運作
- **前端介面** - 響應式設計，支援中文
- **API 系統** - FastAPI + SQLite，完整 CRUD 操作
- **會話管理** - 防止重複提交，錯誤恢復機制
- **結果展示** - 10項優勢分析與中文描述
- **除錯工具** - 清除會話、測試提交工具

### 🛠️ 最新修復
- **修復提交錯誤** - 解決 `DatabaseManager` 缺少方法問題
- **防止重複提交** - 添加提交狀態管理，避免 409 衝突
- **結果頁面** - 提供正確格式的優勢資料
- **編碼問題** - 修復中文顯示亂碼

### 🚧 開發中功能
- 實際計分演算法 (目前使用模擬資料)
- PDF 報告生成
- 職涯建議系統
- 進階優勢分析

## 📚 相關資源

- **CLAUDE.md** - 開發規則與協作指南
- **docs/** - 技術文檔與實作報告
- **examples/** - 使用範例
- **VibeCoding_Workflow_Templates/** - 開發流程範本

---

**由 TaskMaster 系統管理 | 人類駕駛，AI協助** 🤖⚔️