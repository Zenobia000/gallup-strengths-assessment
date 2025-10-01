# V5.0 系統重構總體開發計畫

> **版本目標**: V4.0 → V5.0 (H-MIRT 均衡版全面升級)
> **制定日期**: 2025-10-01
> **預計週期**: 6週
> **核心理念**: 強項為刃，均衡為盾

---

## 🎯 **重構願景與目標**

### 當前 V4.0 系統現狀分析
- ✅ **已完成**: 基礎 Thurstonian IRT、動態職業原型、完整 T1-T12 覆蓋
- ❌ **缺少**: 領域層評估、均衡指標、H-MIRT 模型、30題組最優設計

### V5.0 目標系統願景
- 🎯 **階層式評估**: 12個才幹θ + 4個領域η 雙層科學評估
- 🎯 **均衡指標**: DBI/熵/Gini 三維均衡度量化
- 🎯 **最優題組**: 30題組×120陳述庫，ILP最優化設計
- 🎯 **可視化升級**: 四域均衡雷達 + 12才幹條形圖
- 🎯 **科學驗證**: 基於常模的跨人比較，心理測量學標準

---

## 📋 **重構架構對比分析**

| 組件 | V4.0 現狀 | V5.0 目標 | 改進程度 |
|------|-----------|-----------|----------|
| **評分模型** | 單層 Thurstonian IRT | 階層式 H-MIRT (θ+η) | 🚀 科學躍升 |
| **題組設計** | 9題組 (3次曝光) | 30題組 (10次曝光) | 📊 精度提升3倍 |
| **陳述庫** | 85個混合陳述 | 120個優化陳述 (12×10) | 🎯 質量標準化 |
| **結果呈現** | 單一才幹排序 | 雙層結構+均衡指標 | 🏗️ 多維洞察 |
| **職業原型** | 靜態映射 | 動態+均衡考量 | 🎨 個人化增強 |
| **API架構** | V4 單一端點 | V5 分層回應格式 | 🔗 擴展性提升 |

---

## 🗓️ **6週重構時程規劃**

### **第1週：基礎架構升級**
**目標**: 建立 H-MIRT 核心框架和資料結構

#### Week 1.1: 資料結構重構 (1-2天)
- [ ] 實作新的 `TieredTalentProfile` 資料結構
- [ ] 更新 `Talent`, `Domain`, `BalanceMetrics` 模型
- [ ] 建立 facets + domains 的分層 JSON schema
- [ ] 更新資料庫 schema 支援新結構

#### Week 1.2: H-MIRT 評分引擎骨架 (3-5天)
- [ ] 實作 `HMIRTScorer` 核心類別
- [ ] 建立 Lambda 載入矩陣系統
- [ ] 實作 `BalanceCalculator` (DBI/熵/Gini)
- [ ] 建立常模轉換器 (theta/eta → percentiles)

**本週交付物**:
- ✅ 新的分層資料結構
- ✅ H-MIRT 評分引擎框架
- ✅ 均衡指標計算器

### **第2週：題組設計系統重建**
**目標**: 實現 30題組×120陳述的 ILP 最優化設計

#### Week 2.1: 陳述庫標準化 (1-3天)
- [ ] 建立 120個標準化陳述 (12×10 結構)
- [ ] 實作陳述品質評估 (社會期望性、可讀性)
- [ ] 建立多語言支援框架
- [ ] 陳述資料庫版本管理

#### Week 2.2: ILP 題組優化器 (4-5天)
- [ ] 研究並實作 ILP 題組生成算法
- [ ] 建立均衡性約束 (r=10, λ≈2.73)
- [ ] 實作跨領域分布優化 (每題3-4領域)
- [ ] 題組品質驗證和平衡性測試

**本週交付物**:
- ✅ 120個高品質標準化陳述
- ✅ ILP 題組優化系統
- ✅ 30題組平衡驗證

### **第3週：H-MIRT 模型實作**
**目標**: 實現真實的階層式 IRT 計算

#### Week 3.1: 離線校準系統 (1-3天)
- [ ] 設計 800人規模的校準研究框架
- [ ] 實作資料收集 API (v4_data_collection 擴展)
- [ ] 建立校準資料管理系統
- [ ] 參數估計算法研究

#### Week 3.2: H-MIRT 計算核心 (3-5天)
- [ ] 整合專業 IRT 計算庫 (mirt, ltm, 或 Python 實作)
- [ ] 實作 12個θ + 4個η 同步估計
- [ ] 建立 Lambda 矩陣載入和驗證
- [ ] 常模轉換精確化

**本週交付物**:
- ✅ 離線校準研究系統
- ✅ H-MIRT 核心計算引擎
- ✅ 參數檔案管理系統

### **第4週：前端視覺化升級**
**目標**: 實現四域均衡儀表板和進階視覺化

#### Week 4.1: 四域均衡儀表板 (1-3天)
- [ ] 設計四域雷達圖組件
- [ ] 實作 DBI/熵/Gini 指標視覺化
- [ ] 建立均衡度燈號系統 (綠/黃/紅)
- [ ] 響應式設計適配

#### Week 4.2: 12才幹條形圖升級 (3-5天)
- [ ] 重新設計按領域分組的條形圖
- [ ] 實作互動式才幹詳情展示
- [ ] 建立才幹發展建議卡片
- [ ] 均衡發展策略視覺化

**本週交付物**:
- ✅ 四域均衡儀表板
- ✅ 互動式才幹視覺化
- ✅ 均衡發展建議系統

### **第5週：職業原型系統升級**
**目標**: 整合均衡考量的動態職業匹配

#### Week 5.1: 均衡考量原型分析 (1-3天)
- [ ] 更新職業原型映射考慮領域均衡
- [ ] 實作基於 η 分數的原型匹配
- [ ] 建立均衡風險評估和建議
- [ ] 職業發展路徑個人化

#### Week 5.2: 進階推薦引擎 (3-5天)
- [ ] 整合才幹×領域×均衡的三維匹配
- [ ] 實作團隊互補性分析
- [ ] 建立職涯發展階段匹配
- [ ] 個人化學習路徑生成

**本週交付物**:
- ✅ 均衡考量的職業原型系統
- ✅ 三維職業匹配引擎
- ✅ 個人化發展建議

### **第6週：整合測試與上線**
**目標**: 系統整合、全面測試、平滑遷移

#### Week 6.1: 系統整合測試 (1-3天)
- [ ] V4→V5 完整遷移測試
- [ ] 效能基準測試 (< 100ms 評分)
- [ ] 跨瀏覽器相容性測試
- [ ] 資料一致性驗證

#### Week 6.2: 上線與監控 (3-5天)
- [ ] 建立 V4/V5 並行運行機制
- [ ] 實作 A/B 測試框架
- [ ] 建立監控和警報系統
- [ ] 用戶體驗數據收集

**本週交付物**:
- ✅ V5.0 生產就緒系統
- ✅ 監控和維護工具
- ✅ 完整測試覆蓋

---

## 🏗️ **核心技術架構重構**

### 1. 評分引擎重構 (Critical Path)

```python
# V5.0 核心架構
class HMIRTScoringEngine:
    """階層式多維 IRT 評分引擎"""

    def __init__(self, item_params_path: str, lambda_matrix_path: str):
        self.item_params = self._load_calibrated_parameters(item_params_path)
        self.lambda_matrix = self._load_lambda_matrix(lambda_matrix_path)  # 12×4 載入矩陣
        self.norm_converter = NormativeConverter()
        self.balance_calculator = BalanceCalculator()

    def estimate_scores(self, responses: List[ForcedChoiceResponse]) -> HierarchicalResult:
        """
        H-MIRT 核心計算：同步估計 θ (才幹) 和 η (領域)

        Returns:
            facet_thetas: Dict[str, float]  # T1-T12 潛在分數
            domain_etas: Dict[str, float]   # 4領域潛在分數
            balance_metrics: BalanceMetrics # 均衡指標
        """
        # 1. 應用 H-MIRT 模型同步估計 θ 和 η
        facet_thetas, domain_etas = self._hmirt_estimation(responses)

        # 2. 轉換為常模百分位
        facet_percentiles = self.norm_converter.to_percentiles(facet_thetas, 'facets')
        domain_percentiles = self.norm_converter.to_percentiles(domain_etas, 'domains')

        # 3. 計算均衡指標
        balance_metrics = self.balance_calculator.calculate(domain_percentiles)

        return HierarchicalResult(
            facet_scores=facet_percentiles,
            domain_scores=domain_percentiles,
            balance_metrics=balance_metrics
        )
```

### 2. 題組設計系統重構

```python
# V5.0 ILP 最優化題組設計
class ILPBlockDesigner:
    """基於整數線性規劃的最優題組設計"""

    def create_optimal_blocks(self, statements: List[Statement]) -> List[QuartetBlock]:
        """
        生成 30個最優化題組

        約束條件:
        - 每個才幹出現 r=10 次
        - 配對出現次數 λ≈2.73
        - 每題包含 3-4 個不同領域
        """
        constraints = self._build_ilp_constraints()
        solution = self._solve_ilp_optimization(statements, constraints)
        return self._construct_blocks_from_solution(solution)
```

### 3. 前端視覺化重構

```javascript
// V5.0 前端架構
class TalentDashboard {
    // 四域均衡雷達圖
    renderBalanceDashboard(domainScores, balanceMetrics) {
        this.renderRadarChart(domainScores);
        this.renderBalanceIndicators(balanceMetrics);
    }

    // 12才幹分層條形圖
    renderTalentBars(talentsByDomain) {
        this.renderDomainGroupedBars(talentsByDomain);
        this.renderTierClassification();
    }

    // 均衡發展建議
    renderDevelopmentStrategy(balanceMetrics, dominantDomains) {
        this.renderCompensationStrategies();
        this.renderPartnershipSuggestions();
    }
}
```

---

## 🚀 **重構執行策略**

### Phase 1: 核心引擎重構 (週1-3)
**策略**: 採用「絞殺者模式」，新舊系統並行

1. **建立 V5 評分引擎** (週1)
   - 新增 `core/v5/` 目錄
   - 實作 H-MIRT 核心邏輯
   - 建立分層資料結構

2. **題組系統重建** (週2)
   - 升級陳述庫到 120個標準陳述
   - 實作 ILP 最優化題組生成
   - 建立題組品質驗證

3. **離線校準準備** (週3)
   - 建立校準研究資料收集系統
   - 實作參數估計工具
   - 準備模擬參數檔案

### Phase 2: 前端升級 (週4-5)
**策略**: 漸進式升級，保持向後相容

4. **四域均衡儀表板** (週4)
   - 新增雷達圖視覺化組件
   - 實作均衡指標顯示
   - 建立燈號系統

5. **職業原型升級** (週5)
   - 整合領域均衡考量
   - 實作三維職業匹配
   - 建立個人化建議系統

### Phase 3: 整合部署 (週6)
**策略**: A/B 測試平滑遷移

6. **系統整合** (週6)
   - V4/V5 並行運行
   - A/B 測試框架
   - 監控和回滾機制

---

## 🛠️ **關鍵技術決策**

### 1. H-MIRT 實作選擇
**決策**: 使用 Python mirt 庫 + 自訂包裝器
**理由**:
- 科學嚴謹的實作
- 支援階層式模型
- 社群驗證和維護

### 2. ILP 題組優化
**決策**: 使用 PuLP/OR-Tools 實作
**理由**:
- 數學最優解
- 約束條件靈活
- Python 生態整合

### 3. 前端架構升級
**決策**: 漸進式升級，保持現有框架
**理由**:
- 降低風險
- 用戶體驗連續性
- 開發效率

### 4. 資料庫遷移策略
**決策**: 新增表格，保留舊結構
**理由**:
- 向後相容性
- 資料安全性
- 平滑遷移

---

## 📊 **品質保證框架**

### 心理測量學驗證
- [ ] **測量等效性**: 跨群體 CFA/MIRT 驗證
- [ ] **項目功能差異 (DIF)**: 確保公平性
- [ ] **信度分析**: 邊際信度 (marginal reliability)
- [ ] **效度驗證**: 聚合效度、區別效度、效標效度

### 技術品質保證
- [ ] **單元測試覆蓋**: 核心算法 100% 覆蓋
- [ ] **整合測試**: API 端點完整測試
- [ ] **效能測試**: < 100ms 評分要求
- [ ] **壓力測試**: 併發用戶負載測試

### 用戶體驗驗證
- [ ] **A/B 測試**: V4 vs V5 用戶滿意度
- [ ] **可用性測試**: 評測完成率和時間
- [ ] **準確性驗證**: 結果與用戶自我認知對比

---

## ⚠️ **風險管理與緩解**

### 高風險項目
1. **H-MIRT 模型複雜性**
   - **風險**: 實作困難、計算複雜
   - **緩解**: 階段性實作，先用模擬參數

2. **ILP 題組優化計算複雜度**
   - **風險**: 計算時間過長
   - **緩解**: 啟發式算法備案，預計算結果

3. **用戶體驗差異**
   - **風險**: 新版本學習成本
   - **緩解**: 漸進式升級，保留熟悉元素

### 技術債管理
- **即時清理**: 每週重構時清理相關技術債
- **文檔同步**: 即時更新架構文檔
- **測試先行**: TDD 方式確保品質

---

## 🎉 **成功標準與驗收條件**

### 技術指標
- ✅ **評分精度**: H-MIRT 模型 fit indices > 0.95
- ✅ **系統效能**: 評分延遲 < 100ms
- ✅ **題組品質**: 平衡性指標 λ variance < 0.1
- ✅ **資料完整性**: 0% 資料遺失率

### 業務指標
- ✅ **用戶滿意度**: CSAT ≥ 4.5/5
- ✅ **評測準確性**: 與自我認知一致性 ≥ 85%
- ✅ **職業建議採納**: 7日內行動率 ≥ 70%
- ✅ **系統穩定性**: 99.9% 可用性

### 科學驗證
- ✅ **心理測量標準**: 符合 APA Standards
- ✅ **跨文化適用性**: 測量不變性驗證
- ✅ **預測效度**: 職業匹配準確性驗證

---

## 📝 **實作優先級與依賴關係**

### Critical Path (不可延遲)
1. **Week 1**: 資料結構 → H-MIRT 骨架
2. **Week 2**: 陳述庫 → ILP 題組設計
3. **Week 3**: H-MIRT 實作 → 校準系統

### Parallel Path (可並行)
- **前端升級** (Week 4-5): 與後端並行開發
- **職業原型升級** (Week 5): 與視覺化並行
- **測試和文檔** (Week 1-6): 持續進行

### Optional Enhancement (可選)
- GPT 整合深度分析
- 多語言支援
- 進階分析報告

---

## 🚀 **立即行動項目**

### 本週開始 (Week 1)
1. **建立 V5 開發分支**
2. **實作新資料結構**
3. **建立 H-MIRT 框架**
4. **更新專案文檔**

### 下週準備 (Week 2)
1. **收集120個標準陳述**
2. **研究 ILP 優化庫**
3. **設計前端升級方案**

這個 V5.0 重構計畫將把系統從「能工作」提升到「科學級工作」，實現真正的心理測量學標準和均衡發展理念。