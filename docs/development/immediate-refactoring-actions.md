# V5.0 重構立即行動計畫

> **基於設計文檔分析的緊急重構藍圖**
> **目標**: 將 V4.0 升級為符合設計理念的 V5.0 H-MIRT 均衡版

---

## 🔍 **設計文檔 vs 現狀分析**

### 設計理念要求 (來自4個文檔)
- **H-MIRT 模型**: 階層式多維 IRT (12個θ + 4個η 同步估計)
- **均衡框架**: DBI/熵/Gini 三維均衡指標
- **30題組設計**: 每才幹曝光10次，ILP最優化平衡
- **四域×三才結構**: 執行力、影響力、關係建立、戰略思維各3個才幹
- **120陳述庫**: 標準化、高品質、社會期望性平衡
- **四域均衡儀表板**: 雷達圖 + 燈號系統

### 當前 V4.0 實作現狀
- ✅ **基礎 IRT**: 單層 Thurstonian IRT
- ✅ **動態原型**: 4種凱爾西職業原型
- ✅ **完整覆蓋**: T1-T12 平衡評測
- ❌ **領域層評估**: 缺少 4個η分數
- ❌ **均衡指標**: 無 DBI/熵/Gini 計算
- ❌ **題組優化**: 9題組 vs 設計要求30題組
- ❌ **視覺化**: 缺少四域均衡儀表板

---

## 🚨 **關鍵差距與重構優先級**

### Priority 1: 評分引擎升級 (Critical)
**差距**: 單層 IRT → 階層式 H-MIRT
**影響**: 無法提供領域層洞察和均衡分析
**重構行動**:
1. 建立 H-MIRT 評分引擎框架
2. 實作 12θ + 4η 雙層估計
3. 整合均衡指標計算

### Priority 2: 題組設計優化 (High)
**差距**: 9題組簡單平衡 → 30題組 ILP 最優化
**影響**: 評測精度不足，不符合科學標準
**重構行動**:
1. 研究並實作 ILP 題組優化
2. 升級陳述庫到 120個標準陳述
3. 建立題組品質驗證系統

### Priority 3: 前端視覺化升級 (Medium)
**差距**: 單一才幹視圖 → 四域均衡儀表板
**影響**: 缺少均衡洞察，用戶價值受限
**重構行動**:
1. 建立四域雷達圖組件
2. 實作均衡指標視覺化
3. 設計均衡發展建議系統

---

## 📋 **立即執行的重構任務**

### Task 1: 建立 V5 開發環境 (今天)
```bash
# 建立 V5 分支和目錄結構
git checkout -b feature/v5.0-h-mirt-balance
mkdir -p src/main/python/core/v5/{scoring,balance,optimization}
mkdir -p src/main/python/api/routes/v5
mkdir -p src/main/resources/static/v5/components
```

### Task 2: 實作核心資料結構 (明天)
```python
# 新增 V5 資料模型
@dataclass
class HierarchicalResult:
    facet_scores: Dict[str, float]      # T1-T12 θ分數
    domain_scores: Dict[str, float]     # 4領域 η分數
    balance_metrics: BalanceMetrics     # DBI/熵/Gini
    confidence_intervals: Dict[str, Tuple[float, float]]

@dataclass
class BalanceMetrics:
    dbi: float              # Domain Balance Index
    relative_entropy: float # 分布均勻度
    gini_coefficient: float # 資源公平性
    balance_grade: str      # 'excellent'/'good'/'needs_improvement'
```

### Task 3: H-MIRT 評分引擎骨架 (本週)
```python
# 核心評分引擎
class HMIRTScoringEngine:
    def __init__(self):
        self.lambda_matrix = self._load_lambda_matrix()  # 12×4 載入矩陣
        self.item_params = self._load_item_parameters()   # IRT 參數

    def estimate_hierarchical_scores(self, responses):
        # 1. 同步估計 12個θ + 4個η
        facet_thetas, domain_etas = self._hmirt_estimation(responses)

        # 2. 轉換為常模百分位
        facet_percentiles = self._to_percentiles(facet_thetas, 'facets')
        domain_percentiles = self._to_percentiles(domain_etas, 'domains')

        # 3. 計算均衡指標
        balance_metrics = self._calculate_balance_metrics(domain_percentiles)

        return HierarchicalResult(...)
```

### Task 4: API 端點升級 (本週)
```python
# V5 API 端點
@router.get("/api/v5/assessment/results/{session_id}")
async def get_v5_results(session_id: str):
    return {
        "facet_scores": {...},      # T1-T12 θ分數
        "domain_scores": {...},     # 4領域 η分數
        "balance_metrics": {...},   # DBI/熵/Gini指標
        "talent_classification": {...}, # 分層分類
        "career_prototype": {...},  # 職業原型 (考慮均衡)
        "development_strategy": {...}, # 均衡發展建議
        "visualization_data": {...} # 視覺化資料
    }
```

---

## 🎯 **本週實作重點**

### 今日任務 (Priority 1)
1. ✅ 已完成設計文檔分析和重構計畫
2. 🔄 建立 V5 開發分支
3. 🔄 實作基礎資料結構
4. 🔄 建立 H-MIRT 引擎骨架

### 明日任務 (Priority 2)
1. 實作 BalanceCalculator (DBI/熵/Gini)
2. 建立 Lambda 載入矩陣系統
3. 設計 V5 API 端點結構
4. 準備 ILP 題組優化研究

### 本週目標
- ✅ V5 核心框架建立
- ✅ 均衡指標計算實作
- ✅ API 端點升級
- ✅ 基礎測試覆蓋

---

## 💡 **重構設計原則**

### Linus 好品味原則
- **消除複雜性**: H-MIRT 複雜度隱藏在抽象層後
- **單一真實來源**: 評分邏輯統一到 V5 引擎
- **漸進式升級**: 不破壞現有功能，添加新能力

### 心理測量學原則
- **科學嚴謹**: 每個算法都有理論基礎
- **統計有效**: 所有指標都可驗證
- **跨人比較**: 常模化分數確保公平性

### 實用主義原則
- **用戶價值**: 均衡洞察提供實際指導
- **開發效率**: 重用現有架構，漸進升級
- **維護性**: 清晰的抽象層和文檔

---

## 🚀 **開始重構**

基於深度設計文檔分析，V5.0 重構將實現：

**科學升級**:
- 從簡單 IRT → 階層式 H-MIRT
- 從個人排序 → 個人+均衡雙重洞察
- 從啟發式 → 數學最優化

**用戶價值**:
- 更準確的才幹評估
- 科學的均衡分析
- 個人化發展策略

**系統品質**:
- 心理測量學標準
- 可擴展的架構
- 優雅的用戶體驗

重構開始！🚀