# 系統導航流程圖

## 頁面導航關係

```
landing.html (首頁)
    ↓
assessment-intro.html (評測說明)
    ↓
assessment.html (評測問卷)
    ↓
results.html (個人優勢報告)
    ↓ 【查看團隊協作報告】
report-detail.html (團隊協作潛力報告)
    ↓ 【返回】
results.html (個人優勢報告)
```

---

## 詳細導航矩陣

### 1. landing.html (首頁)
**出口:**
- `開始評測` → assessment-intro.html

**頂部導航:**
- Logo → landing.html (刷新)

---

### 2. assessment-intro.html (評測說明)
**出口:**
- `開始評測` → assessment.html
- `返回首頁` → landing.html

**頂部導航:**
- Logo → landing.html

---

### 3. assessment.html (評測問卷)
**出口:**
- `提交評測` → results.html?session={session_id}
- 進度條完成 → 自動跳轉 results.html

**頂部導航:**
- Logo → landing.html (可能需要確認)
- 進度顯示: X/30

**注意事項:**
- ⚠️ 避免意外離開導致進度丟失

---

### 4. results.html (個人優勢報告) ⭐ 核心頁面
**出口:**
- `查看團隊協作報告` → report-detail.html?session={session_id}
- `下載 PDF` → window.print()
- `分享報告` → 複製連結或原生分享
- `重新評測` → assessment-intro.html

**頂部導航:**
- Logo → landing.html
- 右上角按鈕: 下載PDF、分享、重新評測

**功能區塊:**
1. KPI 卡片 (3 個主要指標)
2. 優勢 DNA 視覺化
3. 12 維度分析
4. 職業原型分類
5. 行動按鈕

---

### 5. report-detail.html (團隊協作潛力報告) 🆕
**出口:**
- `← 返回個人優勢報告` (導航欄 Logo) → results.html?session={session_id}
- `← 查看完整個人報告` (側邊欄按鈕) → results.html?session={session_id}
- `🏠 返回首頁` → landing.html
- `🔄 重新評測` → assessment-intro.html
- `📄 下載PDF` → window.print()
- `📤 分享` → 複製連結或原生分享

**頂部導航:**
- Logo (返回按鈕): `← 返回個人優勢報告`
- 右上角: 下載PDF、分享

**側邊欄:**
- 四大才幹領域貢獻度
- 下一步行動 (3 個按鈕)

**功能區塊:**
1. 團隊角色羅盤 (雷達圖)
2. 原型儀表板 (子原型 + 職業建議)
3. 理想團隊組合

---

## 按鈕功能去重分析

### ❌ 修復前的問題 (report-detail.html)

**重複按鈕:**
1. 導航欄: `📄 下載PDF` + `📤 分享報告` + `重新評測`
2. 側邊欄: `下載完整報告` + `分享給您的團隊` + `返回個人優勢報告`

**問題:**
- ❌ 下載 PDF 出現 2 次
- ❌ 分享功能出現 2 次
- ❌ 缺少「返回」功能

---

### ✅ 修復後的配置

#### 導航欄 (頂部)
```
[← 返回個人優勢報告]  |  [📄 下載PDF]  [📤 分享]
```

**用途:**
- 快速返回上一頁
- 快速導出/分享

#### 側邊欄 (下一步行動)
```
[← 查看完整個人報告] (primary)
[🏠 返回首頁]         (secondary)
[🔄 重新評測]         (secondary)
```

**用途:**
- 引導下一步動作
- 提供其他導航選項

**邏輯分工:**
- **導航欄**: 快速操作 (下載、分享)
- **側邊欄**: 導航選項 (返回、首頁、重測)

---

## Session ID 傳遞流程

### URL 參數傳遞
```
assessment.html
  → 生成 session_id
  → 提交評測

results.html?session={session_id}
  → 載入分數數據
  → 點擊「查看團隊協作報告」

report-detail.html?session={session_id}
  → 載入相同分數數據
  → 計算團隊原型
  → 點擊「返回」

results.html?session={session_id}
  → 返回原始報告
```

### JavaScript 函數
```javascript
// report-detail.html
function backToResults() {
    const sessionId = new URLSearchParams(window.location.search).get('session');
    if (sessionId) {
        window.location.href = `results.html?session=${sessionId}`;
    } else {
        window.location.href = 'results.html';
    }
}
```

```javascript
// results.html
document.getElementById('detailReportLink').onclick = () => {
    window.location.href = `report-detail.html?session=${sessionId}`;
};
```

---

## 用戶旅程範例

### 標準流程
```
1. 用戶訪問首頁
   landing.html

2. 點擊「開始評測」
   → assessment-intro.html

3. 閱讀說明，點擊「開始評測」
   → assessment.html

4. 完成 30 題評測
   → results.html?session=v4_abc123

5. 查看個人優勢報告
   - 看到主導才幹、領域分布、原型分類

6. 點擊「查看團隊協作報告」
   → report-detail.html?session=v4_abc123

7. 查看團隊角色定位、職業建議

8. 點擊「← 返回個人優勢報告」
   → results.html?session=v4_abc123

9. 下載 PDF 或分享報告
```

### 快速重測流程
```
results.html
  → 點擊「重新評測」
  → assessment-intro.html
  → assessment.html
  → results.html?session=v4_xyz789 (新 session)
```

---

## 設計原則

### 1. 無阻斷返回
- ✅ 所有深層頁面都有明確的返回路徑
- ✅ Logo 點擊行為一致 (返回上層或首頁)
- ✅ 避免用戶迷路

### 2. Session 持久性
- ✅ Session ID 通過 URL 參數傳遞
- ✅ 所有報告頁面共享同一 session
- ✅ 支援書籤和分享連結

### 3. 功能分層
- **頂部導航**: 快速操作 (下載、分享)
- **主要內容**: 資訊展示
- **側邊欄/底部**: 下一步動作引導

### 4. 一致性
- ✅ 所有頁面使用相同的設計語言
- ✅ 按鈕文案清晰 (動詞 + 目標)
- ✅ Icon 使用一致

---

## 下一步優化建議

### 1. 添加麵包屑導航 (可選)
```html
<div class="breadcrumb">
    首頁 > 評測結果 > 團隊協作報告
</div>
```

### 2. 添加「上一頁/下一頁」導航 (可選)
```html
<div class="page-nav">
    <button onclick="backToResults()">← 上一頁: 個人優勢報告</button>
    <button disabled>下一頁 →</button>
</div>
```

### 3. 添加「返回頂部」按鈕
```javascript
window.addEventListener('scroll', () => {
    const scrollTop = document.getElementById('scroll-top');
    if (window.scrollY > 300) {
        scrollTop.style.display = 'block';
    } else {
        scrollTop.style.display = 'none';
    }
});
```

---

**版本**: 1.0
**最後更新**: 2025-10-03
**狀態**: ✅ 已完成優化
