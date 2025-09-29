# Gallup 優勢測驗 - 前端文檔

## 📁 目錄結構

```
static/
├── css/                      # 樣式檔案
│   ├── variables.css         # 設計系統變數 (顏色、字型、間距等)
│   ├── reset.css             # CSS Reset 與基礎樣式
│   ├── components.css        # 可重用元件樣式
│   ├── animations.css        # 動畫與微互動
│   └── responsive.css        # 響應式設計 (Mobile-first)
├── js/                       # JavaScript 模組
│   ├── api.js                # API 服務層 (與 FastAPI 通訊)
│   └── storage.js            # 本地儲存服務 (localStorage)
├── assets/                   # 靜態資源
│   └── images/               # 圖片資源
├── pages/                    # 應用頁面
│   ├── consent.html          # 同意條款頁面
│   ├── assessment.html       # 測驗作答頁面
│   └── results.html          # 結果展示頁面
├── index.html                # 首頁 (Landing Page)
└── README.md                 # 本文件
```

## 🎨 設計系統

### 色彩心理學

| 顏色 | 用途 | 心理效應 | 科學依據 |
|------|------|----------|----------|
| **寧靜藍** `#4A90E2` | 主要品牌色、CTA | 信任、專業、冷靜思考 | Küller et al., 2009 |
| **活力綠** `#52C41A` | 成功狀態、進度完成 | 成長、正向、完成感 | Elliot & Maier, 2014 |
| **溫暖橙** `#FA8C16` | 強調、行動呼籲 | 能量、創造力、行動 | Gorn et al., 2004 |

### 字型系統

- **主字型**: `Noto Sans TC` (中文), `-apple-system` (英文)
- **尺寸範圍**: 12px - 60px (使用 CSS Variables)
- **行高**: 1.25 (緊密) - 2.0 (寬鬆)

### 間距系統

- **xs**: 4px
- **sm**: 8px
- **md**: 16px (基準)
- **lg**: 24px
- **xl**: 32px
- **2xl**: 48px
- **3xl**: 64px
- **4xl**: 96px

### 響應式斷點

- **xs**: < 480px (手機直立)
- **sm**: 480px (手機橫向)
- **md**: 768px (平板)
- **lg**: 1024px (桌面)
- **xl**: 1280px (大螢幕)

## 🚀 頁面說明

### 1. Landing Page (`index.html`)

**目標**: 建立信任 → 引發興趣 → 促成行動

**關鍵元素**:
- Hero 區塊: 大標題 + 主要 CTA
- Trust Bar: 3 個信任指標 (GDPR、科學驗證、快速完成)
- Social Proof: 統計數據 (12,450+ 完成數、4.8/5 滿意度)
- Process: 4 步驟流程說明

**行為心理學應用**:
- **Social Proof** (社會證明): 顯示完成人數建立信任
- **Loss Aversion** (損失規避): "僅需 5 分鐘" 降低時間損失感

### 2. Consent Page (`pages/consent.html`)

**目標**: GDPR 合規 + 建立透明度

**關鍵元素**:
- 資料收集說明 (最小化原則)
- 資料使用與保護 (加密、不共享)
- 保存期限 (30 天)
- 用戶權利 (查看、更正、刪除、撤銷)

**互動設計**:
- 大型勾選框 (24px) + 動畫反饋
- 同意後才啟用「繼續」按鈕
- 勾選時卡片脈動動畫

### 3. Assessment Page (`pages/assessment.html`)

**目標**: 維持專注 → 鼓勵完成

**關鍵元素**:
- 固定頂部進度條 (Sticky Header)
- 20 題 Likert 5 點量表
- 里程碑慶祝 (25%, 50%, 75%)
- 上一題/下一題導航

**行為心理學應用**:
- **Zeigarnik Effect** (蔡格尼克效應): 進度條激發完成動機
- **Flow Theory** (心流理論): 即時反饋、平衡難度
- **Peak-End Rule** (峰終定律): 里程碑慶祝創造記憶點

**Flow 設計**:
1. 載入問題 (從 API)
2. 用戶選擇答案
3. 自動儲存到 localStorage (防止資料遺失)
4. 里程碑檢查與彈窗慶祝
5. 最後一題自動提交

### 4. Results Page (`pages/results.html`)

**目標**: 驚喜揭曉 → 價值體現 → 促成下載

**關鍵元素**:
- Loading 動畫 (營造期待)
- 前三大優勢卡片 (漸入動畫)
- 完整 12 項排名 (進度條動畫)
- 行動區 (下載 PDF、分享、重測)

**行為心理學應用**:
- **Peak-End Rule**: 結果揭曉是「Peak Moment」
- **Endowment Effect** (稟賦效應): 已完成測驗,更願意下載報告

**動畫時序**:
1. 0.2s: 第一張優勢卡片
2. 0.4s: 第二張優勢卡片
3. 0.6s: 第三張優勢卡片
4. 0.8s: 完整排名進度條依序填充 (每個間隔 100ms)

## 📡 API 整合

### API 服務 (`js/api.js`)

```javascript
import { api } from '/js/api.js';

// 範例: 提交同意
const response = await api.submitConsent({
  consent_given: true,
  consent_timestamp: new Date().toISOString()
});

// 範例: 取得問題
const questions = await api.getQuestions();

// 範例: 提交答案
await api.submitAllAnswers(sessionId, answers);

// 範例: 取得結果
const results = await api.getResults(sessionId);
```

### 本地儲存 (`js/storage.js`)

```javascript
import { storage } from '/js/storage.js';

// Session 管理
storage.saveSession(sessionId);
const sessionId = storage.getSession();

// 答案儲存
storage.saveAnswer(questionId, score);
const answers = storage.getAnswers();

// 進度儲存
storage.saveProgress({ currentIndex: 5, total: 20 });
const progress = storage.getProgress();

// 清除資料
storage.clearSession();
storage.clear(); // 清除所有
```

## 🎯 關鍵互動設計

### 1. 進度條動畫

```css
.progress-bar {
  background: linear-gradient(90deg, #4A90E2, #52C41A, #FA8C16);
  transition: width 0.5s ease-out;
}
```

### 2. 里程碑彈窗

觸發時機:
- 25% (5/20): 🎉 "很好!已完成 1/4"
- 50% (10/20): ⭐ "太棒了!已過半!"
- 75% (15/20): 🚀 "快完成了!加油!"

### 3. Likert 選項選中效果

```css
.likert-option.selected {
  border-color: var(--color-primary);
  background: var(--color-primary-light);
  box-shadow: 0 0 0 3px rgba(74, 144, 226, 0.1);
}
```

### 4. 優勢卡片漸入

```css
@keyframes revealStrength {
  from {
    opacity: 0;
    transform: translateY(30px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}
```

## ♿ 無障礙設計 (WCAG 2.1 AA)

### 實作項目

- ✅ **鍵盤導航**: 所有互動元素可用 Tab 鍵存取
- ✅ **焦點指示器**: `:focus-visible` 2px 藍色外框
- ✅ **色彩對比**: 文字對比度 ≥ 4.5:1
- ✅ **Skip Link**: "跳到主要內容" 連結
- ✅ **ARIA 標籤**: `aria-label` 用於互動元素
- ✅ **Reduced Motion**: `prefers-reduced-motion` 媒體查詢支援

### 測試工具

- Chrome DevTools Lighthouse (目標 > 90 分)
- axe DevTools
- NVDA / JAWS 螢幕閱讀器

## 📱 響應式設計

### Mobile-First 策略

所有樣式從手機版開始設計,再往上擴展至桌面版。

### 關鍵適配

| 元素 | 手機 (< 768px) | 桌面 (≥ 768px) |
|------|----------------|----------------|
| 標題 | 30px | 60px |
| 卡片間距 | 16px | 24px |
| Grid 欄數 | 1 欄 | 3 欄 |
| 按鈕排列 | 垂直堆疊 | 水平排列 |

## 🔧 開發與測試

### 本地開發

```bash
# 啟動後端 API
python run_dev.py

# 使用 Python HTTP Server 測試前端
cd src/main/resources/static
python -m http.server 8000

# 或使用 Live Server (VS Code 擴充套件)
```

存取: `http://localhost:8000`

### 測試清單

- [ ] **功能測試**
  - [ ] 首頁載入正常
  - [ ] 同意條款勾選啟用按鈕
  - [ ] API 同意提交成功並取得 session_id
  - [ ] 測驗頁面載入 20 題問題
  - [ ] 選擇答案後啟用「下一題」
  - [ ] 進度條正確更新
  - [ ] 里程碑彈窗在 25%/50%/75% 出現
  - [ ] 提交測驗跳轉到結果頁
  - [ ] 結果頁顯示前 3 大優勢
  - [ ] PDF 下載功能正常

- [ ] **響應式測試**
  - [ ] iPhone SE (375px)
  - [ ] iPad (768px)
  - [ ] Desktop (1920px)

- [ ] **瀏覽器相容**
  - [ ] Chrome (Latest)
  - [ ] Firefox (Latest)
  - [ ] Safari (Latest)
  - [ ] Edge (Latest)

- [ ] **無障礙測試**
  - [ ] Lighthouse Accessibility > 90
  - [ ] 鍵盤完整導航
  - [ ] 螢幕閱讀器測試

- [ ] **效能測試**
  - [ ] Lighthouse Performance > 90
  - [ ] First Contentful Paint < 1.5s
  - [ ] Time to Interactive < 3s

## 🐛 已知問題與改善

### 當前限制

1. **無 Dark Mode**: 未來可根據 `prefers-color-scheme` 實作
2. **無國際化**: 僅支援繁體中文,未來可加入 i18n
3. **無離線支援**: 未實作 Service Worker / PWA
4. **無圖表視覺化**: Results 頁面可加入 Chart.js 雷達圖

### 效能優化建議

1. **CSS 分割**: 將頁面特定樣式拆分至獨立檔案
2. **圖片優化**: 使用 WebP 格式 + lazy loading
3. **JavaScript 模組化**: 按頁面動態載入模組
4. **CDN 部署**: 靜態資源透過 CDN 加速

## 📚 參考資源

### 設計理論

- [Peak-End Rule - Daniel Kahneman](https://www.nobelprize.org/prizes/economic-sciences/2002/kahneman/facts/)
- [Flow Theory - Mihaly Csikszentmihalyi](https://www.researchgate.net/publication/224927532_Flow_The_Psychology_of_Optimal_Experience)
- [Color Psychology - Küller et al., 2009](https://journals.sagepub.com/doi/10.1177/0013916509340991)

### 技術文檔

- [MDN Web Docs](https://developer.mozilla.org/)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [CSS Tricks](https://css-tricks.com/)

---

**版本**: 1.0
**最後更新**: 2025-09-30
**維護者**: Frontend Team