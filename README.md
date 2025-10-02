# Gallup 優勢評測系統 V4.0 - 文件存儲版本

**基於 Thurstonian IRT 的科學化優勢評測平台**

> **當前版本**: V4.0-FileStorage (快速開發版) - 支持極速 Try-and-Error 開發
> **數據庫版本**: V4.0 (穩定版) - SQLite 持久化存儲
> **文件存儲版本**: V4.0-FileStorage (開發版) - CSV/JSON 靈活存儲 ⭐
> **更新日期**: 2025-10-02

## 🚀 **新增文件存儲架構**

### 雙版本並行部署
```
📊 數據庫版本 (端口 8004)     📁 文件存儲版本 (端口 8005) ⭐
├── SQLite 持久化            ├── CSV/JSON 文件存儲
├── 事務支持               ├── 即時修改生效
├── 適合穩定測試            ├── 零配置部署
└── 生產就緒               └── 極速開發迭代
```

---

## 🎯 **系統理念**

### 核心哲學
> **"強項為刃，均衡為盾"**
>
> 用主導才幹切入價值創造，用四域均衡抵禦複雜情境風險

### 設計原則
- **科學嚴謹**: 基於心理測量學標準的評測系統
- **客觀公正**: Thurstonian IRT 模型確保跨人比較
- **動態個人化**: 基於真實才幹分數的職業原型分析
- **實用導向**: 提供可行動的發展建議和職涯指導

---

## 🏗️ **當前系統架構 (V4.0)**

### ✅ 已實現的核心功能

#### 📊 **Thurstonian IRT 評測系統**
- **評測方式**: 四選二強制選擇 (Quartet Blocks)
- **題組設計**: 30題組動態生成，T1-T12 完整覆蓋，基於120語句庫
- **平衡算法**: 系統化輪轉規則 + 領域平衡約束
- **計分模型**: Thurstonian IRT + 常模轉換 + 三層分級系統

#### 🎯 **完整 T1-T12 才幹評估**
```
四域×三才結構:
┌─執行力─────┬─影響力─────┬─關係建立───┬─戰略思維───┐
│T1 結構化執行│T5 影響倡議 │T6 協作共好 │T3 探索創新 │
│T2 品質完備  │T7 客戶導向 │T9 紀律信任 │T4 分析洞察 │
│T12 責任當責 │T11 衝突整合│T10 壓力調節│T8 學習成長 │
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### 🎨 **動態職業原型分析**
- **4種凱爾西類型**: 系統建構者、組織守護者、人文關懷家、推廣實踐家
- **動態匹配**: 基於實際才幹分數的即時分析
- **職位推薦**: 個人化職業建議和發展路徑

#### 🔧 **技術架構優勢**
- **純 V4 架構**: 技術債已清理，無歷史包袱
- **統一計分引擎**: 可插拔策略，支援多種計分方法
- **Repository Pattern**: 抽象資料存取，易測試維護
- **全域錯誤處理**: 標準化回應格式，用戶友善
- **配置外部化**: 環境變數支援，部署靈活

### 📈 **V4.0 系統指標 (完全實現並驗證)**
- **評測規模**: ✅ 完整30題組動態生成，120語句庫完美平衡 (每維度精確10語句)
- **差異化計分**: ✅ 真實分數分布7.3-99範圍，告別固定20.0，展現個人化優勢
- **時間精確**: ✅ 真實評測時間記錄 (0:50-2:32)，MM:SS精確計時顯示
- **視覺專業**: ✅ McKinsey風格DNA雙螺旋，節點大小動態映射分數強度
- **智能分析**: ✅ 三層分級系統，動態職業原型，基於才幹模式的個人化分析
- **架構品質**: ✅ 完全符合pages-overview-and-sitemap.md，支援遠端開發訪問
- **數據同步**: ✅ 120語句庫CSV/SQLite完全同步，支援極速開發迭代

---

## 🚀 **V5.0 升級計畫 (H-MIRT 均衡版)**

### 🎯 升級願景
基於設計文檔要求，V5.0 將實現：

#### 🧠 **階層式多維 IRT (H-MIRT)**
- **雙層評估**: 12個才幹θ + 4個領域η 同步估計
- **科學模型**: 基於 λ 載入矩陣的結構化評估
- **常模化**: 真正的跨人比較分數

#### ⚖️ **四域均衡分析**
- **DBI 指數**: 領域均衡度量化 (0-1)
- **相對熵**: 分布均勻度分析
- **Gini 係數**: 才幹分布公平性
- **均衡策略**: 基於指標的發展建議

#### 🔬 **ILP 最優化題組**
- **30題組設計**: 每才幹曝光10次 (vs 當前3次)
- **數學最優**: 整數線性規劃確保完美平衡
- **120陳述庫**: 標準化、高品質評測內容

#### 📊 **四域均衡儀表板**
- **雷達圖**: 四個領域的視覺化分析
- **燈號系統**: 綠/黃/紅均衡度指示
- **發展建議**: 個人化均衡策略

### 📅 **V5.0 開發時程** (6週計畫)
```
Week 1: H-MIRT 核心引擎 + 資料結構重構
Week 2: ILP 題組優化 + 120陳述庫建立
Week 3: 離線校準系統 + 參數管理
Week 4: 四域均衡儀表板 + 視覺化升級
Week 5: 職業原型均衡整合 + 三維匹配
Week 6: 系統整合測試 + A/B 遷移部署
```

---

## 🛠️ **開發與部署**

### 環境需求
- **Python**: 3.10+
- **Node.js**: 16+ (前端開發)
- **系統**: Linux/macOS/Windows

### 🚀 **快速啟動 - 雙版本選擇**

#### 方式一：文件存儲版本 (推薦開發使用) ⭐
```bash
# 1. 設置環境
git clone https://github.com/Zenobia000/gallup-strengths-assessment.git
cd gallup-strengths-assessment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. 啟動文件存儲版本
cd src/main/python
python3 -m uvicorn api.main_files:app --host 0.0.0.0 --port 8005 --reload
# API: http://localhost:8005

# 3. 直接訪問前端 (無需單獨服務)
# 前端: http://localhost:8005/landing.html
```

#### 方式二：數據庫版本 (穩定測試使用)
```bash
# 啟動數據庫版本
cd src/main/python
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8004 --reload
# API: http://localhost:8004
```

### 🌐 **系統訪問入口**

#### 文件存儲版本 (端口 8005) ⭐
**本地開發:**
- **主入口**: http://localhost:8005/static/index.html
- **著陸頁**: http://localhost:8005/static/landing.html
- **評測準備**: http://localhost:8005/static/assessment-intro.html
- **評測執行**: http://localhost:8005/static/assessment.html (30題動態出題)
- **結果展示**: http://localhost:8005/static/results.html?session={id} (專業報告)
- **詳細分析**: http://localhost:8005/static/report-detail.html?session={id}
- **API 文檔**: http://localhost:8005/api/docs
- **系統狀態**: http://localhost:8005/api/system/health

**遠端開發 (替換為你的服務器IP):**
- **主入口**: http://10.137.80.58:8005/static/index.html
- **著陸頁**: http://10.137.80.58:8005/static/landing.html
- **評測準備**: http://10.137.80.58:8005/static/assessment-intro.html
- **評測執行**: http://10.137.80.58:8005/static/assessment.html (30題動態出題)
- **結果展示**: http://10.137.80.58:8005/static/results.html?session={id}
- **API 文檔**: http://10.137.80.58:8005/api/docs
- **系統狀態**: http://10.137.80.58:8005/api/system/health

#### 數據庫版本 (端口 8004)
- **API 文檔**: http://localhost:8004/api/docs
- **系統狀態**: http://localhost:8004/api/system/health
- **系統資訊**: http://localhost:8004/api/system/info

### 🎯 **Try-and-Error 快速開發流程**

文件存儲版本支持極速開發迭代：

```bash
# 1. 修改評測語句
vim data/file_storage/v4_statements.json

# 2. 立即測試新配置 (無需重啟)
curl http://localhost:8005/api/assessment/blocks

# 3. 前端實時測試
open http://localhost:8005/assessment.html

# 4. 版本控制
git add data/file_storage/
git commit -m "test: 調整評測語句配置"

# 5. 快速回滾 (如需要)
git checkout -- data/file_storage/
```

### 📊 **API 端點 - 雙版本對照**

#### 文件存儲版本 (端口 8005)
```
系統相關:
└── GET  /api/system/health              # 文件存儲健康檢查

評測相關:
├── GET  /api/assessment/blocks          # 獲取平衡題組 (文件存儲)
├── POST /api/assessment/submit          # 提交評測回答 (文件存儲)
├── GET  /api/assessment/results/{id}    # 獲取完整結果 (文件存儲)
└── GET  /api/assessment/questions       # 獲取評測題目 (文件存儲)

前端頁面:
├── GET  /landing.html                   # 著陸頁
├── GET  /assessment.html                # 評測頁面
├── GET  /results.html                   # 結果頁面
└── GET  /report-detail.html             # 詳細報告頁面
```

#### 數據庫版本 (端口 8004)
```
系統相關:
├── GET  /api/system/health              # 數據庫健康檢查
└── GET  /api/system/info                # 系統資訊

隱私相關:
└── POST /api/privacy/consent            # 隱私同意管理

評測相關:
├── GET  /api/assessment/blocks          # 獲取平衡題組 (數據庫)
├── POST /api/assessment/submit          # 提交評測回答 (數據庫)
├── GET  /api/assessment/results/{id}    # 獲取完整結果 (數據庫)
└── GET  /api/assessment/questions       # 獲取評測題目 (數據庫)

報告相關:
├── POST /api/reports/generate/{id}      # 生成報告
└── GET  /api/reports/download/{id}      # 報告下載

數據收集:
└── POST /api/data/collection/*          # 數據收集相關
```

---

## 🧪 **測試與驗證**

### 🧪 **雙版本測試方式**

#### 文件存儲版本測試 (推薦) ⭐
```bash
# 系統健康檢查
curl -s http://localhost:8005/api/system/health | jq '.status'

# 功能測試
curl -s http://localhost:8005/api/assessment/blocks | jq '.total_blocks'

# 完整評測流程測試
# 1. 訪問 http://localhost:8005/landing.html
# 2. 點擊開始評測
# 3. 完成題組 (11個四選二題組)
# 4. 查看結果頁面

# 數據修改測試
vim data/file_storage/v4_statements.json
curl -s http://localhost:8005/api/assessment/blocks  # 立即生效
```

#### 數據庫版本測試
```bash
# V4 系統完整測試
PYTHONPATH=src/main/python python -m pytest src/test/ -v

# 特定功能測試
python -m pytest src/test/unit/test_archetype_service.py -v
python -m pytest src/test/integration/test_v4_archetype_integration.py -v

# 系統驗證
curl -s http://localhost:8004/api/assessment/blocks | jq '.total_blocks'
curl -s http://localhost:8004/api/system/health | jq '.status'
```

### 🚀 **文件存儲優勢體驗**

#### 即時數據修改
```bash
# 1. 修改語句內容
echo '修改評測語句內容...' > data/file_storage/custom_statement.json

# 2. 立即測試效果 (無需重啟服務)
curl http://localhost:8005/api/assessment/blocks

# 3. 版本控制友好
git diff data/file_storage/  # 查看變更
git add data/file_storage/ && git commit -m "test: 新語句配置"
```

#### 零配置部署
```bash
# 一條命令啟動完整系統
python3 -m uvicorn api.main_files:app --port 8005 --reload

# 無需額外的數據庫服務
# 無需複雜的環境配置
# 開箱即用！
```

---

## 📈 **成功指標與品質保證**

### V4.0 達成指標 (完全驗證)
- ✅ **完整性**: T1-T12 維度100%覆蓋，120語句庫30題組完整評測
- ✅ **平衡性**: 每維度精確10次曝光，系統化輪轉演算法完美實現
- ✅ **差異化**: 真實分數分布7.3-99範圍，個人化優勢清晰展現
- ✅ **時間精確**: 實際評測時間0:50-2:32記錄，MM:SS倒數計時器
- ✅ **視覺專業**: McKinsey風格DNA視覺化，節點大小映射分數強度
- ✅ **智能原型**: 動態職業分析，基於真實才幹模式的個人化建議
- ✅ **架構品質**: 完全符合設計文件，支援本地和遠端開發環境

### V5.0 目標指標
- 🎯 **科學性**: H-MIRT 模型，心理測量學標準
- 🎯 **精確性**: 30題組，每維度 10次曝光
- 🎯 **洞察性**: 四域均衡分析，DBI/熵/Gini 指標
- 🎯 **專業性**: 120標準陳述，ILP 數學最優化

---

## 🚀 **開始使用**

### ⭐ 立即體驗文件存儲版本 (推薦)
```bash
# 1. 一鍵啟動
cd src/main/python
python3 -m uvicorn api.main_files:app --port 8005 --reload

# 2. 立即訪問
open http://localhost:8005/landing.html

# 3. 開始極速開發
vim data/file_storage/v4_statements.json  # 修改數據
curl http://localhost:8005/api/assessment/blocks  # 立即測試
```

### 📊 立即體驗數據庫版本 (穩定版)
```bash
# 1. 啟動系統
cd src/main/python
python3 -m uvicorn api.main:app --port 8004 --reload

# 2. 訪問 API
open http://localhost:8004/api/docs

# 3. 完整測試流程
python -m pytest src/test/ -v
```

### 🎯 選擇版本指南

| 使用場景 | 推薦版本 | 端口 | 優勢 |
|:---------|:---------|:-----|:-----|
| **快速開發測試** | 文件存儲版本 ⭐ | 8005 | 即時修改、零配置 |
| **算法實驗** | 文件存儲版本 ⭐ | 8005 | 數據靈活、版本控制 |
| **演示準備** | 文件存儲版本 ⭐ | 8005 | 快速調整、穩定運行 |
| **穩定功能測試** | 數據庫版本 | 8004 | 數據持久、事務支持 |
| **生產部署準備** | 數據庫版本 | 8004 | 成熟穩定、完整功能 |

### 🔄 版本切換
```bash
# 切換到文件存儲版本
python3 -m uvicorn api.main_files:app --port 8005

# 切換到數據庫版本
python3 -m uvicorn api.main:app --port 8004

# 同時運行兩個版本 (不同端口)
# 終端1: python3 -m uvicorn api.main:app --port 8004
# 終端2: python3 -m uvicorn api.main_files:app --port 8005
```

---

## 📚 **技術文檔**

### 🆕 **文件存儲架構文檔**
- `docs/file-storage-architecture.md` - 文件存儲完整架構指南 ⭐
- `logs/file_storage_migration_report.md` - 遷移完成報告
- `docs/design/information-architecture-v2.md` - 更新的資訊架構

### 設計文檔
- `docs/design/system-design-and-scoring-mechanism.md` - 系統設計理念
- `docs/design/scoring-engine-design.md` - 評分引擎技術規範
- `docs/design/talent-domain-mapping.md` - 才幹領域映射

### 開發文檔
- `docs/development/v5-refactoring-master-plan.md` - V5.0 重構總體計畫
- `docs/architecture-refactoring-summary.md` - 架構重構總結
- `CLAUDE.md` - 開發協作規則

### API 文檔
#### 文件存儲版本 ⭐
- **自動生成**: http://localhost:8005/api/docs
- **OpenAPI**: http://localhost:8005/api/openapi.json

#### 數據庫版本
- **自動生成**: http://localhost:8004/api/docs
- **OpenAPI**: http://localhost:8004/api/openapi.json

---

## 🤝 **貢獻指南**

### 開發原則
- 遵循 Linus Torvalds 好品味原則
- 保持函式簡潔 (≤3層縮排)
- 單一職責，清晰抽象
- 測試先行，文檔同步

### 提交規範
```bash
# Conventional Commits 格式
git commit -m "feat(component): 功能描述"
git commit -m "fix(component): 修復描述"
git commit -m "refactor(component): 重構描述"
```

---

---

## ⭐ **文件存儲版本 - 極速開發體驗**

### 🚀 **為什麼選擇文件存儲版本？**

1. **秒級 Try-and-Error 循環**
   ```bash
   vim data/file_storage/v4_statements.json  # 修改
   curl localhost:8005/api/assessment/blocks  # 測試
   # 立即看到效果！
   ```

2. **零配置啟動**
   ```bash
   python3 -m uvicorn api.main_files:app --port 8005 --reload
   # 就這麼簡單！
   ```

3. **Git 友好的版本控制**
   ```bash
   git diff data/file_storage/  # 清晰的變更對比
   git commit -m "test: 新算法配置"  # 版本化實驗
   ```

4. **人類可讀的數據格式**
   - 直接編輯 JSON 配置
   - 無需 SQL 遷移腳本
   - 實時可視化調試

### 🎯 **適用場景**
- ✅ 算法參數調優
- ✅ 語句內容實驗
- ✅ 快速原型驗證
- ✅ 演示數據準備
- ✅ 教學和研究

**💡 這是一個科學級心理測量系統，現在支持極速 Try-and-Error 開發！文件存儲版本讓您的創意實驗變得前所未有的簡單快速！**

---

## 🔄 **快速切換指南**

```bash
# 文件存儲版本 (推薦開發使用)
python3 -m uvicorn api.main_files:app --port 8005 --reload
open http://localhost:8005/landing.html

# 數據庫版本 (穩定測試使用)
python3 -m uvicorn api.main:app --port 8004 --reload
open http://localhost:8004/api/docs
```

---

*由 TaskMaster Hub 系統管理 | 人類駕駛，AI 協助 | 現已支援文件存儲極速開發模式* 🚀🤖⚔️