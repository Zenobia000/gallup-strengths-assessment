# V4.0 Thurstonian IRT 研究與開發

## 📋 專案概覽

本目錄包含 Gallup 優勢測驗 v4.0 升級的所有研究文檔、技術規範和開發資源。

### 🎯 核心目標
- 從簡單計數模型升級至 Thurstonian IRT 統計模型
- 解決強制選擇產生的 ipsative 數據限制
- 實現跨人群可比較的常模分數

## 📁 文檔結構

```
v4_research/
├── README.md                       # 本文件
├── irt-theory-foundation.md        # ✅ IRT 理論基礎與數學模型
├── branch-strategy.md               # ✅ 分支開發策略
├── statement-pool-design.md         # ⏳ 語句池設計 (待完成)
├── block-balance-algorithm.md      # ⏳ 區塊平衡演算法 (待完成)
├── calibration-study-plan.md       # ⏳ 校準研究計劃 (待完成)
└── performance-benchmarks.md        # ⏳ 性能基準測試 (待完成)
```

## 🚀 開發進度

### ✅ 已完成 (28h)
- [x] IRT 理論研究與文獻調研 (Task 8.1.1)
- [x] v4.0 原型架構設計 (Task 8.3.1)
- [x] 新資料結構定義 (Task 8.3.2)
- [x] IRTScorer 類別原型 (Task 8.3.3)
- [x] 原型驗證測試 (Task 8.3.4)
- [x] 分支開發策略制定

### 🔄 進行中
- [ ] 48+ 語句池設計 (Task 8.1.2)

### ⏳ 待開始 (74h)
- [ ] 平衡四選二區塊設計 (Task 8.1.3)
- [ ] 小規模預測試設計 (Task 8.1.4)
- [ ] 初步參數估計分析 (Task 8.1.5)
- [ ] Thurstonian IRT 演算法研究 (Task 8.2.1)
- [ ] Python IRT 套件評估 (Task 8.2.2)
- [ ] 統計計算原型實作 (Task 8.2.3)
- [ ] 常模轉換邏輯設計 (Task 8.2.4)

## 🛠️ 技術架構

### 核心模組
```python
src/main/python/
├── models/v4/               # v4.0 資料模型
│   ├── forced_choice.py     # 強制選擇資料結構
│   └── __init__.py
├── core/v4/                 # v4.0 核心邏輯
│   ├── irt_scorer.py        # IRT 計分引擎
│   ├── block_designer.py    # 區塊設計器
│   └── __init__.py
└── test/unit/v4/            # v4.0 單元測試
    └── test_irt_prototype.py
```

### 關鍵類別
- `ThurstonianIRTScorer`: IRT 模型計分器
- `QuartetBlockDesigner`: 四選二區塊設計器
- `ForcedChoiceBlockResponse`: 區塊回應資料結構
- `Statement`: 語句定義
- `QuartetBlock`: 四語句區塊

## 📊 技術規格

### IRT 模型參數
- **維度數**: 12 (Gallup 優勢主題)
- **語句數**: 48+ (每維度 4+)
- **區塊數**: 28-30
- **選擇模式**: 四選二 (最像/最不像)
- **估計方法**: MLE with Bayesian prior

### 性能目標
- **計分延遲**: < 100ms
- **記憶體使用**: < 100MB
- **準確度**: 重測相關 > 0.90

## 🔬 研究方法

### Phase 1: 理論研究 ✅
- Thurstonian IRT 數學基礎
- Python 實作策略
- 參數估計方法

### Phase 2: 語句開發 🔄
- 內容效度審查
- 社會期望性評定
- 語句池平衡

### Phase 3: 統計校準 ⏳
- 小樣本預測試
- 參數估計
- 模型擬合度檢驗

### Phase 4: 系統實作 ⏳
- 生產級代碼
- 效能優化
- 整合測試

## 📚 參考資源

### 學術文獻
- Brown & Maydeu-Olivares (2011) - IRT for forced-choice
- Brown (2016) - Common framework for FC questionnaires
- Thurstone (1927) - Law of comparative judgment

### Python 套件
- `scipy.optimize`: 優化演算法
- `numpy`: 數值計算
- `statsmodels`: 統計模型 (評估中)
- `pymc3`: 貝葉斯推斷 (評估中)

## 🤝 貢獻指南

### 開發流程
1. 在 `feature/v4.0-thurstonian-irt` 分支開發
2. 遵循提交訊息規範 (feat/fix/docs/test + v4.0 標識)
3. 確保測試通過再提交
4. 定期同步 main 分支更新

### 程式碼標準
- Python 3.10+
- Type hints 必須
- Docstrings 必須
- 單元測試覆蓋率 > 80%

## 📈 里程碑

| 日期 | 里程碑 | 狀態 |
|------|--------|------|
| 2025-09-30 | 原型實作完成 | ✅ |
| 2025-10-16 | 語句池設計完成 | ⏳ |
| 2025-10-25 | 統計校準完成 | ⏳ |
| 2025-11-07 | 系統重構完成 | ⏳ |
| 2025-11-16 | v4.0 生產部署 | ⏳ |

## 📞 聯絡資訊

**技術負責人**: Claude Code
**專案經理**: TaskMaster Hub
**人類駕駛員**: Sunny

---

最後更新: 2025-09-30 23:45