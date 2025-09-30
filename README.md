# Gallup 優勢測驗

**透過 Gallup 認證課程的問卷協助用戶分析**

> **專案目標**: 4週內建立「同意→作答→計分→決策建議→PDF報告」的端到端 MVP

## 🎯 專案特色

- **📊 公領域人格量表** - 基於 Big Five/HEXACO + Mini-IPIP (20題)
- **🧠 自有優勢本體** - 12個優勢面向權重系統
- **⚙️ 規則引擎** - 職缺推薦與改善建議系統
- **📄 PDF 報告** - 一鍵生成個人化分析報告
- **🔒 隱私合規** - 完整同意流程與審計軌跡
- **⚡ 高效MVP** - SQLite + FastAPI，4週交付

## 🚀 技術架構

### 後端技術棧
- **FastAPI** (Python 3.11+) - 高效API框架
- **SQLite** - 輕量級資料庫 (WAL模式)
- **Pydantic** - 資料驗證與序列化
- **ReportLab** - PDF報告生成

### 核心模組
```
src/main/python/
├── core/          # 心理測量核心演算法
├── models/        # 資料模型與Schema
├── services/      # 業務邏輯服務層
├── api/           # FastAPI路由與端點
└── utils/         # 工具函式與共用邏輯
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

## 📋 開發計劃 (4週)

### Week 1: 基礎架構 (40h) ✅ 已完成
- [x] 專案結構建立
- [x] SQLite 資料庫設計與初始化
- [x] FastAPI 專案架構
- [x] Mini-IPIP 題庫建立 (20題中文版)
- [x] 基礎 API 端點 (同意、會話、問題、提交)
- [x] 用戶同意與隱私合規
- [x] 前端評估介面
- [x] 結果顯示頁面
- [x] 基本計分系統

### Week 2: 計分引擎 (45h)
- [ ] 人格向度計分演算法
- [ ] 12個優勢面向權重系統
- [ ] 可解釋性追蹤 (provenance)
- [ ] 決策推理鏈實作
- [ ] 單元測試完善

### Week 3: 推薦系統 (38h)
- [ ] 職缺規則引擎
- [ ] 改善建議系統
- [ ] PDF 報告模板
- [ ] 一次性分享連結
- [ ] 整合測試

### Week 4: 品質保證 (33h)
- [ ] 端到端測試
- [ ] 錯誤處理與監控
- [ ] 審計軌跡完善
- [ ] 文檔與部署準備

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

#### 前端界面 (使用者介面)
- **主頁**: http://localhost:3000
- **測驗界面**: http://localhost:3000/pages/assessment.html
- **結果展示**: http://localhost:3000/pages/results.html

#### 後端 API (開發/測試)
- **健康檢查**: http://localhost:8004/api/v1/health
- **API 文檔**: http://localhost:8004/api/v1/docs
- **測驗問題**: http://localhost:8004/api/v1/questions

#### 🛠️ 除錯工具 (Debug Tools)
- **清除會話工具**: http://localhost:3000/clear_session.html
- **提交測試工具**: http://localhost:3000/test_submit.html

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