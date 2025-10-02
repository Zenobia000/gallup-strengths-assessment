# 文件存儲架構 - 快速開發版本

## 概述

為了支持快速 Try-and-Error 開發模式，系統已完全轉換為文件存儲架構，使用 CSV/JSON 文件替代 SQLite 數據庫。

## 架構變更總結

### 🔄 **變更前後對比**

| 層面 | 數據庫版本 | 文件存儲版本 |
|:-----|:-----------|:-------------|
| **存儲方式** | SQLite (.db) | CSV + JSON 文件 |
| **數據修改** | 需要 SQL 遷移 | 直接編輯文件 |
| **備份策略** | 數據庫備份 | 文件版本控制 |
| **開發速度** | 中等 | 極快 |
| **調試難度** | 需要 SQL 工具 | 文本編輯器即可 |
| **部署複雜度** | 中等 | 極簡 |

### 📁 **新的存儲結構**

```
data/file_storage/
├── v4_statements.json         # 評測語句數據
├── v4_statements.csv          # 同上，CSV 格式
├── v4_sessions.json           # 評測會話
├── v4_responses.json          # 用戶回應
├── v4_response_items.json     # 詳細回應項目
├── v4_scores.json             # 計分結果
├── export_summary.json        # 數據導出摘要
└── backups/                   # 自動備份
    └── 20251002_140000/
        ├── v4_statements.json
        └── ...
```

## 核心組件

### 1. FileStorageManager

**位置**: `src/main/python/core/file_storage.py`

**功能**:
- 提供類似數據庫的 CRUD 操作
- 自動 JSON/CSV 雙格式存儲
- 內存緩存機制提升性能
- 自動備份與版本控制

**主要方法**:
```python
# 基本操作
storage.select_all("table_name")
storage.select_by_id("table_name", "id_field", id_value)
storage.insert("table_name", record_dict)
storage.update("table_name", "id_field", id_value, updates_dict)

# 查詢操作
storage.select_where("table_name", field1="value1", field2="value2")
storage.count("table_name", **conditions)

# 系統操作
storage.health_check()
storage.backup_table("table_name")
```

### 2. 簡化的 API 層

**位置**: `src/main/python/api/main_files.py`

**新特性**:
- 專用於文件存儲的路由
- 簡化的錯誤處理
- 快速重啟和測試支持

**端點**:
- **端口**: 8005 (避免與數據庫版本衝突)
- **健康檢查**: `/api/system/health`
- **評測塊**: `/api/assessment/blocks`
- **提交評測**: `/api/assessment/submit`
- **獲取結果**: `/api/assessment/results/{session_id}`

### 3. 模塊化組件

#### 計分引擎 (`core/scoring/`)
- `quality_checker.py`: 簡化版本質量檢查
- `v4_scoring_engine.py`: 基於文件的計分邏輯

#### 題組生成 (`core/thurstonian/`)
- `block_generator.py`: 平衡題組生成算法

## 使用指南

### 🚀 **啟動系統**

```bash
# 停止原數據庫版本 (端口 8004)
# 啟動文件存儲版本 (端口 8005)
cd src/main/python
python3 -m uvicorn api.main_files:app --host 0.0.0.0 --port 8005 --reload
```

### 📊 **訪問端點**

```bash
# 系統健康檢查
curl http://localhost:8005/api/system/health

# 獲取評測題組
curl http://localhost:8005/api/assessment/blocks

# 前端頁面
http://localhost:8005/landing.html
http://localhost:8005/assessment.html
http://localhost:8005/results.html
```

### 🛠️ **快速數據修改**

#### 修改評測語句
```bash
# 直接編輯 JSON 文件
vim data/file_storage/v4_statements.json

# 或編輯 CSV 文件
vim data/file_storage/v4_statements.csv

# 系統會自動重新加載
```

#### 查看系統狀態
```python
# Python 檢查
from core.file_storage import get_file_storage
storage = get_file_storage()
print(storage.health_check())
```

### 🔄 **Try-and-Error 工作流程**

1. **修改數據**:
   ```bash
   # 編輯語句文件
   vim data/file_storage/v4_statements.json
   ```

2. **測試變更**:
   ```bash
   # 獲取新的評測塊測試
   curl http://localhost:8005/api/assessment/blocks
   ```

3. **版本控制**:
   ```bash
   # 提交變更
   git add data/file_storage/
   git commit -m "test: 修改語句配置進行測試"
   ```

4. **快速回滾**:
   ```bash
   # 如果測試失敗，快速回滾
   git checkout -- data/file_storage/
   ```

## 優勢

### ✅ **開發效率**
- **即時修改**: 編輯文件後立即生效
- **可視化**: JSON/CSV 格式人類可讀
- **版本控制**: Git 友好的文本格式
- **快速備份**: 簡單的文件復制

### ✅ **測試友好**
- **數據隔離**: 每個測試可使用獨立數據集
- **快速重置**: 删除文件即重置狀態
- **調試簡單**: 直接查看 JSON 數據

### ✅ **部署簡便**
- **無依賴**: 不需要數據庫服務
- **跨平台**: 純文件存儲
- **零配置**: 開箱即用

## 限制與注意事項

### ⚠️ **性能限制**
- 不適合大量並發用戶
- 內存使用隨數據量增長
- 文件 I/O 可能成為瓶頸

### ⚠️ **數據一致性**
- 無事務支持
- 並發寫入可能導致數據丟失
- 需要應用層鎖機制

### ⚠️ **適用場景**
- ✅ 原型開發
- ✅ 算法測試
- ✅ 小規模演示
- ❌ 生產環境
- ❌ 高並發場景

## 遷移指南

### 從數據庫版本遷移到文件存儲

1. **數據導出**:
   ```bash
   python3 scripts/export_db_to_files.py
   ```

2. **切換服務**:
   ```bash
   # 停止數據庫版本
   # 啟動文件存儲版本
   python3 -m uvicorn api.main_files:app --port 8005
   ```

### 從文件存儲回到數據庫

1. **數據導入** (待開發):
   ```bash
   python3 scripts/import_files_to_db.py
   ```

2. **切換服務**:
   ```bash
   # 停止文件存儲版本
   # 啟動數據庫版本
   python3 -m uvicorn api.main:app --port 8004
   ```

## 測試驗證

### 功能測試
- ✅ 評測塊生成
- ✅ 用戶響應存儲
- ✅ 計分算法運行
- ✅ 結果頁面顯示
- ✅ 導航流程完整

### 性能測試
- ✅ 單用戶流程 < 5秒
- ✅ 數據讀取 < 100ms
- ✅ 文件存儲 < 50ms

---

## 快速上手

1. **克隆項目** (如果需要)
2. **切換到文件存儲分支**:
   ```bash
   git checkout feature/file-storage
   ```
3. **啟動服務**:
   ```bash
   cd src/main/python
   python3 -m uvicorn api.main_files:app --port 8005 --reload
   ```
4. **開始測試**:
   ```bash
   open http://localhost:8005/landing.html
   ```

**享受快速 Try-and-Error 開發體驗！** 🚀