# 優勢天賦評測系統 - 網站地圖 (Sitemap)

**更新時間**: 2025-09-30
**版本**: v4.0

## 🗺️ 頁面架構總覽

```
首頁 (/)
├── 評測流程
│   ├── 評測介紹 → 評測執行 → 結果展示
│   └── 深度報告 → 行動方案
├── 用戶中心
│   ├── 個人檔案
│   └── 歷史記錄
└── 其他頁面
    ├── 關於我們
    └── 科學依據
```

## 📄 核心頁面清單

### 1. 公開頁面（無需登入）

| 頁面名稱 | 檔案名稱 | URL路徑 | 主要功能 | 狀態 |
|:---------|:---------|:--------|:---------|:-----|
| **商業首頁** | landing.html | / | 價值主張、轉換導向 | ✅ 已完成 |
| **評測介紹** | assessment-intro.html | /assessment-intro | 設定期待、流程說明 | ✅ 已完成 |
| **評測執行** | assessment.html | /assessment | 實際評測進行 | ✅ 已完成 |
| **V4評測頁** | v4_assessment.html | /v4-assessment | V4.0版本評測（備用） | ✅ 已完成 |

### 2. 結果相關頁面

| 頁面名稱 | 檔案名稱 | URL路徑 | 主要功能 | 狀態 |
|:---------|:---------|:--------|:---------|:-----|
| **基礎結果** | results.html | /results?session={id} | 免費版結果展示 | ✅ 已完成 |
| **深度報告** | report-detail.html | /report/{session_id} | 付費版詳細分析 | ✅ 已完成 |
| **行動方案** | action-plan.html | /action-plan/{session_id} | 個性化發展計劃 | ✅ 已完成 |

### 3. 用戶中心頁面

| 頁面名稱 | 檔案名稱 | URL路徑 | 主要功能 | 狀態 |
|:---------|:---------|:--------|:---------|:-----|
| **個人檔案** | profile.html | /profile | 用戶資料、設定 | ⏳ 待開發 |
| **評測歷史** | history.html | /history | 歷史記錄、進度追蹤 | ❌ 未開發 |
| **升級方案** | pricing.html | /pricing | 付費方案選擇 | ❌ 未開發 |

### 4. 支援頁面

| 頁面名稱 | 檔案名稱 | URL路徑 | 主要功能 | 狀態 |
|:---------|:---------|:--------|:---------|:-----|
| **關於我們** | about.html | /about | 團隊介紹、使命願景 | ❌ 未開發 |
| **科學依據** | science.html | /science | IRT模型說明 | ❌ 未開發 |
| **隱私政策** | privacy.html | /privacy | 隱私保護說明 | ❌ 未開發 |
| **服務條款** | terms.html | /terms | 使用條款 | ❌ 未開發 |

## 🔄 用戶流程路徑

### 主要流程：新用戶完整評測
```
1. landing.html (首頁)
   ↓ 點擊「開始測評」
2. assessment-intro.html (評測介紹)
   ↓ 點擊「開始評測」
3. assessment.html (評測執行)
   ↓ 完成15個區塊
4. results.html (基礎結果)
   ↓ 點擊「查看深度分析」
5. report-detail.html (深度報告) [付費牆]
   ↓ 點擊「生成行動方案」
6. action-plan.html (行動方案)
   ↓ 點擊「追蹤進度」
7. profile.html (個人檔案)
```

### 返回用戶流程
```
1. landing.html 或 profile.html
   ↓ 檢測到未完成評測
2. assessment.html?resume=true (繼續評測)
   ↓ 或查看歷史結果
3. history.html → results.html
```

## 🎯 頁面功能對比

### assessment-intro.html vs assessment.html 差異

| 特性 | assessment-intro.html | assessment.html |
|:-----|:---------------------|:----------------|
| **主要目的** | 評測前的準備和說明 | 實際執行評測 |
| **內容** | 流程介紹、注意事項、時間預估 | 評測題目、選項 |
| **用戶行為** | 閱讀、理解、準備 | 選擇、回答 |
| **必要性** | 可選（但建議保留） | 必要 |
| **時長** | 30秒-1分鐘 | 3-5分鐘 |

**建議保留兩個頁面的理由**：
1. **降低焦慮**：assessment-intro 讓用戶有心理準備
2. **設定期待**：明確告知評測方式和時長
3. **提高完成率**：準備充分的用戶更容易完成評測
4. **專注體驗**：assessment.html 可以純粹專注於評測本身

## 🔗 頁面連結關係

### 導航連結矩陣

| 從/到 | landing | assessment-intro | assessment | results | report | action | profile |
|:------|:--------|:----------------|:-----------|:--------|:-------|:-------|:--------|
| **landing** | - | ✓ | ✓ | - | - | - | ✓ |
| **assessment-intro** | ✓ | - | ✓ | - | - | - | - |
| **assessment** | ✓ | ✓ | - | ✓ | - | - | - |
| **results** | ✓ | - | ✓ | - | ✓ | ✓ | ✓ |
| **report** | ✓ | - | - | ✓ | - | ✓ | ✓ |
| **action** | ✓ | - | - | ✓ | ✓ | - | ✓ |
| **profile** | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | - |

## 📱 響應式設計要求

### 斷點設計
- **Mobile**: 320px - 767px
- **Tablet**: 768px - 1023px
- **Desktop**: 1024px - 1439px
- **Wide**: 1440px+

### 關鍵頁面移動端優化
1. **assessment.html**: 垂直排列選項，大按鈕易點擊
2. **results.html**: 圖表自適應，可橫向滾動
3. **action-plan.html**: 卡片堆疊顯示

## 🔐 訪問權限設計

### 公開訪問
- landing.html
- assessment-intro.html
- assessment.html
- results.html (基礎部分)
- about.html
- science.html
- privacy.html
- terms.html

### 需要Session ID
- results.html (完整功能)
- report-detail.html
- action-plan.html

### 需要用戶登入
- profile.html
- history.html
- pricing.html (購買功能)

## 🚀 開發優先級

### P0 - 核心功能（已完成）
- [x] landing.html
- [x] assessment.html
- [x] results.html

### P1 - 增值功能（進行中）
- [x] assessment-intro.html
- [x] report-detail.html
- [x] action-plan.html
- [ ] profile.html

### P2 - 支援功能
- [ ] history.html
- [ ] pricing.html
- [ ] about.html
- [ ] science.html

### P3 - 合規功能
- [ ] privacy.html
- [ ] terms.html

## 📊 頁面性能目標

| 頁面類型 | FCP | LCP | CLS | 總大小 |
|:---------|:----|:----|:----|:-------|
| 靜態頁面 | <0.8s | <2.0s | <0.05 | <500KB |
| 互動頁面 | <1.0s | <2.5s | <0.1 | <1MB |
| 結果頁面 | <1.2s | <3.0s | <0.1 | <1.5MB |

## 🎨 設計一致性檢查

### 必要元素
- [ ] 統一導航欄
- [ ] 品牌標識
- [ ] 頁腳資訊
- [ ] 響應式適配
- [ ] 返回/前進邏輯
- [ ] 錯誤處理
- [ ] 載入狀態

## 📝 備註

1. **關於 assessment-intro.html**：
   - 可考慮整合到 assessment.html 作為第一個步驟
   - 或保留作為獨立頁面，提供更好的用戶體驗

2. **版本管理**：
   - v4_assessment.html 作為實驗版本
   - assessment.html 作為穩定版本

3. **SEO 優化**：
   - landing.html 需要meta標籤優化
   - 結果頁面應設為 noindex

4. **分析追蹤**：
   - 每個頁面需要埋點追蹤
   - 重點關注轉換漏斗

---

**更新紀錄**：
- 2025-09-30: 初版建立，整理現有頁面結構