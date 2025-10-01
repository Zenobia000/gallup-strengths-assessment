# Gallup 優勢評測系統 V4.0 → V5.0

**基於 Thurstonian IRT 的科學化優勢評測平台**

> **當前版本**: V4.0 (生產就緒) - 純淨架構，技術債已清理
> **開發中**: V5.0 (H-MIRT 均衡版) - 基於設計文檔的全面升級
> **更新日期**: 2025-10-01

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
- **題組設計**: 9題組完美平衡，T1-T12 完整覆蓋
- **隨機化**: 每次評測動態生成不同題組
- **計分模型**: Thurstonian IRT + 常模轉換

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

### 📈 **V4.0 系統指標**
- **評測效率**: 9題組 vs 原15題組 (-40%時間)
- **維度覆蓋**: 100% T1-T12 完整覆蓋
- **平衡性**: 完美平衡 (每維度恰好3次曝光)
- **隨機化**: 每次生成不同題組，避免記憶效應
- **架構品質**: 簡潔、專注、易維護

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

### 快速啟動
```bash
# 1. 設置環境
git clone https://github.com/Zenobia000/gallup-strengths-assessment.git
cd gallup-strengths-assessment
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# 2. 啟動後端 API (V4)
cd src/main/python
PYTHONPATH=. python main.py
# API: http://localhost:8002

# 3. 啟動前端服務 (另一終端)
cd src/main/resources/static
python -m http.server 3000
# 前端: http://localhost:3000
```

### 🌐 **系統訪問入口**

#### 用戶端
- **評測入口**: http://localhost:3000/
- **評測頁面**: http://localhost:3000/assessment.html
- **結果頁面**: http://localhost:3000/results.html?session={id}

#### 開發端
- **API 文檔**: http://localhost:8002/docs
- **系統狀態**: http://localhost:8002/api/health
- **系統資訊**: http://localhost:8002/api/system/info

### 📊 **V4.0 API 端點**
```
V4 核心端點:
├── GET  /api/v4/assessment/blocks     # 獲取平衡題組
├── POST /api/v4/assessment/submit     # 提交評測回答
├── GET  /api/v4/assessment/results/{id} # 獲取完整結果
├── GET  /api/v4/health               # 系統健康檢查
└── POST /api/v4/calibration/run      # IRT 參數校準

共用端點:
├── POST /consent                     # 隱私同意管理
├── GET  /reports/{id}/download       # 報告下載
└── GET  /api/system/info            # 系統資訊
```

---

## 🧪 **測試與驗證**

### 執行測試
```bash
# V4 系統完整測試
PYTHONPATH=src/main/python python -m pytest src/test/ -v

# 特定功能測試
python -m pytest src/test/unit/test_archetype_service.py -v
python -m pytest src/test/integration/test_v4_archetype_integration.py -v
```

### 系統驗證
```bash
# 檢查核心功能
curl -s http://localhost:8002/api/v4/assessment/blocks | jq '.total_blocks'
curl -s http://localhost:8002/api/health | jq '.status'

# 評測流程測試
# 1. 訪問 http://localhost:3000/assessment.html
# 2. 完成 9 個四選二題組
# 3. 查看 http://localhost:3000/results.html?session={id}
```

---

## 📈 **成功指標與品質保證**

### V4.0 達成指標
- ✅ **完整性**: T1-T12 維度 100% 覆蓋
- ✅ **平衡性**: 每維度 3次曝光，完美平衡
- ✅ **動態性**: 職業原型基於真實分數分析
- ✅ **客觀性**: 隨機化題組，避免記憶效應
- ✅ **穩定性**: 純淨架構，無技術債

### V5.0 目標指標
- 🎯 **科學性**: H-MIRT 模型，心理測量學標準
- 🎯 **精確性**: 30題組，每維度 10次曝光
- 🎯 **洞察性**: 四域均衡分析，DBI/熵/Gini 指標
- 🎯 **專業性**: 120標準陳述，ILP 數學最優化

---

## 🚀 **開始使用**

### 立即體驗 V4.0
1. 啟動系統: `PYTHONPATH=src/main/python python main.py`
2. 訪問: http://localhost:3000/
3. 體驗: 完整的 T1-T12 動態優勢評測

### 參與 V5.0 開發
1. 查看重構計畫: `docs/development/v5-refactoring-master-plan.md`
2. 了解設計理念: `docs/design/system-design-and-scoring-mechanism.md`
3. 建立開發分支: `git checkout -b feature/v5.0-h-mirt-balance`

---

## 📚 **技術文檔**

### 設計文檔
- `docs/design/system-design-and-scoring-mechanism.md` - 系統設計理念
- `docs/design/scoring-engine-design.md` - 評分引擎技術規範
- `docs/design/talent-domain-mapping.md` - 才幹領域映射

### 開發文檔
- `docs/development/v5-refactoring-master-plan.md` - V5.0 重構總體計畫
- `docs/architecture-refactoring-summary.md` - 架構重構總結
- `CLAUDE.md` - 開發協作規則

### API 文檔
- **自動生成**: http://localhost:8002/docs
- **OpenAPI**: http://localhost:8002/openapi.json

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

**💡 這是一個活躍開發的科學級心理測量系統，歡迎參與 V5.0 H-MIRT 均衡版的重構開發！**

---

*由 TaskMaster Hub 系統管理 | 人類駕駛，AI 協助* 🤖⚔️