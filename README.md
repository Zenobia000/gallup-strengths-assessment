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

### Week 1: 基礎架構 (40h)
- [x] 專案結構建立
- [ ] SQLite 資料庫設計與初始化
- [ ] FastAPI 專案架構
- [ ] Mini-IPIP 題庫建立
- [ ] 基礎 API 端點
- [ ] 用戶同意與隱私合規

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
pip install fastapi uvicorn sqlite3 pydantic reportlab
```

### 資料庫初始化
```bash
# 初始化 SQLite 資料庫
python scripts/init_database.py

# 載入種子資料
python scripts/load_seed_data.py
```

### 啟動開發服務器
```bash
uvicorn src.main.python.api.main:app --reload
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

## 📚 相關資源

- **CLAUDE.md** - 開發規則與協作指南
- **docs/api/** - API文檔
- **examples/** - 使用範例
- **VibeCoding_Workflow_Templates/** - 開發流程範本

---

**由 TaskMaster 系統管理 | 人類駕駛，AI協助** 🤖⚔️