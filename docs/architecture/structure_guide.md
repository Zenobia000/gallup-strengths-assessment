# Gallup 優勢測驗 - 專案結構指南

---

**文件版本:** v1.0
**最後更新:** 2025-09-30
**主要作者:** 技術負責人
**狀態:** 活躍 (Active)

---

## 1. 指南目的

本指南定義 Gallup 優勢測驗專案的標準化目錄結構，確保：
- 團隊成員快速定位程式碼
- 清晰的關注點分離
- 符合 Clean Architecture 原則
- 易於測試與維護

---

## 2. 核心設計原則

1. **按功能組織 (Feature-based):** 相關功能集中管理
2. **Clean Architecture:** 依賴方向由外向內
3. **配置外部化:** 環境配置與程式碼分離
4. **根目錄簡潔:** 僅放置專案級檔案
5. **測試對應:** 測試結構鏡像原始碼結構

---

## 3. 專案結構總覽

```
gallup-strengths-assessment/
├── .claude/                    # TaskMaster & Claude Code 配置
│   ├── commands/               # 自訂指令
│   ├── agents/                 # 智能體配置
│   └── context/                # 跨智能體共享上下文
│       ├── decisions/          # ADR 決策記錄
│       ├── quality/            # 程式碼品質報告
│       ├── testing/            # 測試報告
│       └── security/           # 安全稽核報告
├── VibeCoding_Workflow_Templates/  # 企業級範本庫
├── docs/                       # 專案文檔
│   ├── architecture/           # 架構設計文件
│   ├── api/                    # API 規格
│   ├── testing/                # 測試規格
│   ├── security/               # 安全檢查清單
│   └── structure_guide.md      # 本檔案
├── src/                        # 原始碼根目錄
│   ├── main/                   # 主程式碼
│   │   ├── python/             # Python 程式碼
│   │   │   ├── core/           # 核心領域邏輯
│   │   │   │   ├── __init__.py
│   │   │   │   ├── config.py   # 配置管理
│   │   │   │   ├── scoring.py  # 計分引擎
│   │   │   │   └── strength_mapping.py  # 優勢映射
│   │   │   ├── models/         # 資料模型
│   │   │   │   ├── __init__.py
│   │   │   │   ├── database.py # ORM 模型
│   │   │   │   └── schemas.py  # Pydantic 驗證
│   │   │   ├── services/       # 業務邏輯服務
│   │   │   │   ├── __init__.py
│   │   │   │   ├── assessment.py
│   │   │   │   ├── recommendation.py
│   │   │   │   └── report_generator.py
│   │   │   ├── api/            # API 層
│   │   │   │   ├── __init__.py
│   │   │   │   ├── main.py     # FastAPI app
│   │   │   │   ├── dependencies.py
│   │   │   │   └── routes/
│   │   │   │       ├── __init__.py
│   │   │   │       ├── consent.py
│   │   │   │       ├── sessions.py
│   │   │   │       ├── questions.py
│   │   │   │       └── results.py
│   │   │   └── utils/          # 工具函式
│   │   │       ├── __init__.py
│   │   │       ├── database.py
│   │   │       └── logging.py
│   │   └── resources/          # 非程式碼資源
│   │       ├── config/         # 配置檔案
│   │       │   ├── settings.toml
│   │       │   └── weights.json  # 優勢權重矩陣
│   │       ├── data/           # 種子資料
│   │       │   ├── questions.json  # Mini-IPIP 題庫
│   │       │   └── strengths.json  # 優勢定義
│   │       └── templates/      # PDF 模板
│   │           └── report_template.rml
│   └── test/                   # 測試程式碼
│       ├── unit/               # 單元測試
│       │   ├── test_scoring.py
│       │   ├── test_mapping.py
│       │   └── test_assessment.py
│       ├── integration/        # 整合測試
│       │   ├── test_api.py
│       │   └── test_database.py
│       ├── fixtures/           # 測試資料
│       │   ├── sample_responses.json
│       │   └── expected_results.json
│       └── conftest.py         # Pytest 配置
├── data/                       # 執行時資料
│   ├── gallup_strengths.db     # SQLite 資料庫
│   ├── backups/                # 資料庫備份
│   └── exports/                # 匯出資料
├── output/                     # 產生的輸出
│   ├── pdfs/                   # 生成的 PDF 報告
│   └── logs/                   # 應用程式日誌
├── scripts/                    # 自動化腳本
│   ├── init_db.py              # 資料庫初始化
│   ├── seed_data.py            # 種子資料載入
│   ├── backup_db.sh            # 備份腳本
│   └── run_tests.sh            # 測試執行腳本
├── tools/                      # 開發工具
│   └── weight_calculator.py    # 權重矩陣計算器
├── .env.example                # 環境變數範例
├── .gitignore                  # Git 忽略配置
├── CLAUDE.md                   # Claude Code 指引
├── Dockerfile                  # 容器化配置
├── docker-compose.yml          # 本地開發環境
├── pyproject.toml              # Python 專案配置
├── requirements.txt            # 依賴套件
├── README.md                   # 專案說明
└── run_dev.py                  # 開發伺服器啟動腳本
```

---

## 4. 目錄職責詳解

### 4.1 `src/main/python/` - 應用程式原始碼

#### 🧠 `core/` - 領域層 (Domain Layer)
**職責:** 核心業務規則與領域邏輯
- `scoring.py`: Mini-IPIP 五大人格計分演算法
- `strength_mapping.py`: 人格向度 → Gallup 優勢映射
- `config.py`: 應用程式配置管理

**原則:**
- 無外部依賴（不依賴 API/DB）
- 純函式設計
- 高測試覆蓋率

#### 📊 `models/` - 資料模型層
**職責:** 資料結構定義
- `database.py`: SQLAlchemy ORM 模型
- `schemas.py`: Pydantic 驗證模型（DTO）

**原則:**
- ORM 模型僅用於持久化
- Pydantic 模型用於 API I/O

#### ⚙️ `services/` - 應用服務層
**職責:** 業務流程編排
- `assessment.py`: 測驗會話管理
- `recommendation.py`: 職缺推薦引擎
- `report_generator.py`: PDF 報告生成

**原則:**
- 協調領域邏輯與基礎設施
- 事務邊界管理

#### 🌐 `api/` - API 層 (Infrastructure)
**職責:** HTTP 接口暴露
- `main.py`: FastAPI 應用程式入口
- `routes/`: API 端點定義

**原則:**
- 僅處理 HTTP 請求/回應
- 委派業務邏輯給 services 層

---

### 4.2 `src/main/resources/` - 資源檔案

#### 📁 `data/` - 種子資料
- `questions.json`: 20 題 Mini-IPIP 問卷
  ```json
  {
    "questions": [
      {
        "id": 1,
        "text": "我經常感到充滿活力",
        "dimension": "extraversion",
        "reverse_scored": false
      }
    ]
  }
  ```

- `strengths.json`: 12 個 Gallup 優勢定義
  ```json
  {
    "strengths": [
      {
        "name": "achiever",
        "display_name": "成就",
        "description": "...",
        "job_recommendations": ["專案經理", "業務代表"]
      }
    ]
  }
  ```

#### ⚖️ `config/weights.json` - 權重矩陣
定義人格向度 → 優勢面向的映射權重：
```json
{
  "version": "1.0",
  "last_updated": "2025-09-30",
  "mapping": {
    "achiever": {
      "conscientiousness": 0.7,
      "extraversion": 0.3
    }
  }
}
```

---

### 4.3 `src/test/` - 測試程式碼

#### 單元測試結構
```
test/unit/
├── test_scoring.py           # 計分引擎測試
│   ├── test_calculate_dimension_scores()
│   ├── test_reverse_scoring()
│   └── test_score_range_validation()
├── test_mapping.py           # 優勢映射測試
│   ├── test_map_to_strengths()
│   └── test_provenance_tracking()
└── test_assessment.py        # 測驗服務測試
    ├── test_create_session()
    └── test_submit_responses()
```

#### 整合測試結構
```
test/integration/
├── test_api.py               # API 端對端測試
│   ├── test_complete_assessment_flow()
│   └── test_pdf_generation()
└── test_database.py          # 資料庫整合測試
    ├── test_transaction_rollback()
    └── test_concurrent_writes()
```

---

## 5. 文件命名約定

| 類型 | 約定 | 範例 |
|:-----|:-----|:-----|
| Python 模組 | `snake_case.py` | `strength_mapping.py` |
| Python 類別 | `PascalCase` | `AssessmentService` |
| Python 函式 | `snake_case()` | `calculate_scores()` |
| 測試檔案 | `test_*.py` | `test_scoring.py` |
| 配置檔案 | `lowercase.ext` | `settings.toml` |
| Markdown | `kebab-case.md` | `architecture-design.md` |

---

## 6. 資料流向

```
用戶請求
    ↓
API Layer (routes/)
    ↓
Application Layer (services/)
    ↓
Domain Layer (core/)
    ↓
Infrastructure (models/database.py)
    ↓
SQLite Database
```

**依賴方向:** 由外向內
**核心原則:** Domain Layer 不依賴任何外層

---

## 7. 配置管理策略

### 開發環境
```bash
# .env.dev
DATABASE_URL=sqlite:///data/dev.db
LOG_LEVEL=DEBUG
PDF_OUTPUT_DIR=output/pdfs
```

### 生產環境
```bash
# .env.prod
DATABASE_URL=sqlite:///data/prod.db
LOG_LEVEL=INFO
ENABLE_METRICS=true
```

---

## 8. 演進原則

1. **保持扁平化:** 避免過深的目錄嵌套（最多 3 層）
2. **模組化拆分:** 當檔案超過 500 行時考慮拆分
3. **測試對應:** 每個 `src/` 檔案應有對應 `test/` 檔案
4. **文檔同步:** 結構變更時更新本文件

---

## 9. 常見問題

### Q: 為何使用 `src/main/python` 而非直接 `src/`?
A: 遵循標準 Maven 目錄結構，支援多語言專案擴展（如未來加入 TypeScript 前端）。

### Q: `core/` 與 `services/` 的區別?
A: `core/` 是純領域邏輯（可獨立測試），`services/` 編排流程並處理外部依賴。

### Q: 測試檔案要放在 `src/` 內還是分離?
A: 分離至 `src/test/`，避免打包時包含測試程式碼。

---

**相關文檔:**
- [架構設計](architecture/architecture_design.md)
- [API 規格](api/api_specification.md)
- [測試策略](testing/module_specifications.md)