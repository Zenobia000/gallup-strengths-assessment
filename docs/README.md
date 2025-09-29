# 📚 Gallup 優勢測驗 - 文檔導覽

歡迎來到 Gallup 優勢測驗專案文檔中心。本目錄包含所有技術與產品文檔。

---

## 🗂️ 文檔索引

### 核心文檔 (必讀)

| 文檔 | 用途 | 目標讀者 | 狀態 |
|:-----|:-----|:---------|:-----|
| **[prd.md](prd.md)** | 產品需求文件 | PM, 全團隊 | ✅ 完整 |
| **[architecture.md](architecture.md)** | 系統架構設計 | 技術團隊 | ✅ 完整 |
| **[api_design.md](api_design.md)** | API 設計規範 | 前後端開發者 | ✅ 完整 |

### 開發指南

| 文檔 | 用途 | 目標讀者 | 狀態 |
|:-----|:-----|:---------|:-----|
| **[structure_guide.md](structure_guide.md)** | 專案結構指南 | 新成員, 開發者 | ✅ 完整 |
| **[module_specifications.md](module_specifications.md)** | 模組規格與測試 | 開發者, QA | ✅ 完整 |

### 安全與合規

| 文檔 | 用途 | 目標讀者 | 狀態 |
|:-----|:-----|:---------|:-----|
| **[security_checklist.md](security_checklist.md)** | 安全檢查清單 | 技術負責人, DevOps | ✅ 完整 |

---

## 📖 快速導覽

### 🎯 我想了解...

#### 「這個專案做什麼？」
→ 閱讀 **[prd.md](prd.md)** (15分鐘)
- 商業目標與使用者故事
- MVP 功能範圍
- 成功指標

#### 「系統如何運作？」
→ 閱讀 **[architecture.md](architecture.md)** (30分鐘)
- 系統架構與C4模型
- 技術選型與原因
- 資料流程與模組設計

#### 「如何呼叫 API？」
→ 閱讀 **[api_design.md](api_design.md)** (20分鐘)
- API 端點規格
- 請求/回應範例
- 錯誤處理

#### 「專案目錄結構？」
→ 閱讀 **[structure_guide.md](structure_guide.md)** (10分鐘)
- Clean Architecture 目錄結構
- 命名約定
- 常見問題

#### 「如何撰寫測試？」
→ 閱讀 **[module_specifications.md](module_specifications.md)** (25分鐘)
- 契約式設計 (DbC)
- TDD 測試案例
- 覆蓋率目標

#### 「安全性如何保證？」
→ 閱讀 **[security_checklist.md](security_checklist.md)** (20分鐘)
- GDPR 合規檢查
- OWASP API Security
- 生產準備就緒清單

---

## 🚀 新成員入門路徑

### Day 1: 理解業務
1. 📋 閱讀 [prd.md](prd.md) - 了解產品目標
2. 🏗️ 瀏覽 [architecture.md](architecture.md) 的「架構總覽」部分

### Day 2: 熟悉技術
3. 📁 閱讀 [structure_guide.md](structure_guide.md) - 掌握專案結構
4. 🌐 瀏覽 [api_design.md](api_design.md) - 了解 API 規格

### Day 3: 開始開發
5. 🧪 閱讀 [module_specifications.md](module_specifications.md) - 學習測試規範
6. 🔒 快速檢視 [security_checklist.md](security_checklist.md) - 安全注意事項

---

## 📊 文檔統計

```
總文檔數: 6 個核心文檔
總字數: ~15,000 字
預估閱讀時間: 2 小時
最後更新: 2025-09-30
```

---

## 🔄 文檔更新規範

### 更新頻率
- **prd.md** - 每個 Sprint 開始前更新
- **architecture.md** - 重大技術決策後更新
- **api_design.md** - API 變更時立即更新
- **其他文檔** - 按需更新，保持實時性

### 更新流程
1. 修改相關 Markdown 檔案
2. 更新「最後更新」日期
3. 提交 Git commit with prefix `docs:`
4. PR 審查（重大變更需要）

---

## 🗺️ 文檔關聯圖

```
prd.md (產品需求)
  ├─> architecture.md (系統架構)
  │     ├─> structure_guide.md (專案結構)
  │     ├─> api_design.md (API 規範)
  │     └─> security_checklist.md (安全檢查)
  └─> module_specifications.md (模組規格)
```

---

## 💡 文檔哲學

遵循 **Linus Torvalds "好品味"原則**:
- ✅ 簡潔直觀 - 扁平化結構，無過度嵌套
- ✅ 單一事實來源 - 每個概念只有一個權威文檔
- ✅ 實用主義 - 文檔為開發服務，不為完美而完美
- ✅ 持續演進 - 隨專案成長而更新，不僵化

---

## 🆘 需要幫助？

- 📧 技術問題: 聯絡技術負責人
- 💬 產品問題: 聯絡 PM
- 🐛 文檔問題: 在 GitHub 開 Issue

**Happy Coding! 🚀**