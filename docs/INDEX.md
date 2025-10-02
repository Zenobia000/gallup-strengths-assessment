# 📚 優勢天賦評測系統 - 文檔索引

> 最後更新：2025-10-02
> 版本：v4.0 動態評測系統 (完整實作)

## 📁 文檔結構

```
docs/
├── INDEX.md                    # 本文檔索引
├── README.md                    # 專案總覽說明
├── documentation-index.md      # 舊版索引（待更新）
├── user-manual-zh.md           # 用戶使用手冊
│
├── 📐 architecture/            # 架構與技術文檔
│   ├── ARCHITECTURE.md         # 系統架構總覽
│   ├── API_DESIGN.md          # API 設計規範
│   ├── CACHE_IMPLEMENTATION.md # 快取實作詳情
│   ├── module_specifications.md # 模組規格說明
│   ├── structure_guide.md      # 專案結構指南
│   ├── security_checklist.md   # 安全檢查清單
│   └── v3_service_architecture.md # v3 服務架構
│
├── 🎨 design/                  # 設計與規劃文檔
│   ├── PRD.md                  # 產品需求文檔
│   ├── ui_ux_specification.md  # UI/UX 設計規範
│   ├── sitemap.md              # 網站地圖
│   ├── system-design-and-scoring-mechanism.md # 系統設計與評分機制
│   ├── scoring-engine-design.md # 評分引擎設計
│   └── career-archetype-mapping.md # 職業原型映射
│
├── 📊 project/                 # 專案管理文檔
│   ├── project-wbs-development-plan.md # WBS 開發計劃
│   ├── project-v4-thurstonian-irt-wbs.md # v4.0 WBS
│   ├── implementation-status.md # 實作狀態
│   └── maintenance-manual.md   # 維護手冊
│
├── 📈 reports/                 # 測試與研究報告
│   ├── IMPLEMENTATION_REPORT.md # 實作報告
│   ├── testing-status-report.md # 測試狀態報告
│   ├── data_persistence_report.md # 資料持久化報告
│   ├── v4_test_report.md       # v4.0 測試報告
│   ├── v4_page_flow_logic.md   # v4.0 頁面流程邏輯
│   └── scoring-algorithm-research.md # 評分算法研究
│
├── 🔬 v4_research/             # v4.0 研究文檔
│   └── [研究文檔]
│
├── 🧪 testing/                 # 測試相關文檔
│   └── [測試文檔]
│
├── 🛠️ dev/                     # 開發指南
│   └── web_design_guide.md     # 網頁設計指南
│
├── 📡 api/                     # API 文檔
│   └── api_documentation_example.md # API 文檔範例
│
└── 👤 user/                    # 用戶相關文檔
    └── [用戶文檔]
```

## 🚀 快速導航

### 開發人員必讀
1. [系統架構](architecture/ARCHITECTURE.md) - 了解整體系統結構
2. [API 設計](architecture/API_DESIGN.md) - API 開發規範
3. [專案結構](architecture/structure_guide.md) - 程式碼組織方式
4. [UI/UX 規範](design/ui_ux_specification.md) - 前端開發指引

### 產品設計
1. [產品需求文檔](design/PRD.md) - 功能需求說明
2. [系統設計](design/system-design-and-scoring-mechanism.md) - 核心機制設計
3. [職業原型映射](design/career-archetype-mapping.md) - 評測結果映射邏輯
4. [網站地圖](design/sitemap.md) - 頁面結構規劃

### 專案管理
1. [WBS 開發計劃](project/project-wbs-development-plan.md) - 工作分解結構
2. [v4.0 專案計劃](project/project-v4-thurstonian-irt-wbs.md) - 當前版本計劃
3. [實作狀態](project/implementation-status.md) - 開發進度追蹤
4. [維護手冊](project/maintenance-manual.md) - 系統維護指南

### 測試與報告
1. [實作報告](reports/IMPLEMENTATION_REPORT.md) - 功能實作總結
2. [測試報告](reports/v4_test_report.md) - v4.0 測試結果
3. [評分算法研究](reports/scoring-algorithm-research.md) - 理論基礎研究

## 📌 重要連結

- **GitHub Repository**: https://github.com/Zenobia000/gallup-strengths-assessment
- **Branch**: feature/v4.0-thurstonian-irt
- **Live Demo**: http://localhost:3000

## 🎯 **當前系統狀態 (v4.0)**

### ✅ **完全動態化系統**
- **動態出題**: 30題組基於120語句庫的平衡區塊設計
- **專業報告**: McKinsey風格的DNA視覺化與三層分級
- **API串接**: 完整的前後端分離架構
- **職業原型**: 基於主導領域的智能職業建議

### 🔧 **技術棧**
- **後端**: FastAPI + File Storage (極速開發模式)
- **前端**: 原生 HTML5/CSS3/JavaScript (專業級UI)
- **評測模型**: Thurstonian IRT + 常模百分位
- **視覺化**: SVG DNA雙螺旋結構

### 📊 **系統指標**
- **評測時間**: 10-15分鐘 (30題組)
- **維度覆蓋**: T1-T12 100%完整覆蓋
- **平衡性**: 每維度精確10次曝光
- **動態性**: 即時生成個人化報告

## 🔄 版本歷史

| 版本 | 日期 | 主要更新 |
|------|------|---------|
| v4.0 | 2025-10-02 | **完整動態系統實作** - DNA視覺化、專業報告、API串接 |
| v3.0 | 2025-09-30 | Thurstonian IRT 基礎架構 |
| v2.0 | 2025-09-25 | API 架構重構 |
| v1.0 | 2025-09-20 | 初始版本 |

## 📝 文檔維護說明

- 新增文檔請按照分類放入對應資料夾
- 更新文檔時請同步更新本索引
- 重要變更請在版本歷史中記錄
- 所有設計文檔已同步至當前實作狀態

---

*最後更新：2025-10-02 by Claude Code - 動態評測系統完全實作*