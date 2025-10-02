# 優勢評測系統 UI/UX 設計規範

**版本**: 4.1
**更新日期**: 2025-10-01
**狀態**: 實現完整動態結果系統與V4.0整合

## 1. 品牌定位與使命

### 核心價值主張
「發現你獨特的優勢組合，開啟專屬成功路徑」

### 認知心理學基礎

#### Hick's Law 應用
- **首頁**: 單一明確 CTA，降低決策摩擦
- **評測頁**: 每次只顯示一個區塊，避免選擇過載
- **結果頁**: 分層展示，先總覽後細節

#### 認知負荷理論
- **分塊處理**: 15個區塊分次展示，每次專注一個決策
- **視覺分組**: 相關資訊群組化，減少工作記憶負擔
- **漸進揭露**: 複雜資訊逐步展開，避免資訊過載

#### 峰終定律 (Peak-End Rule)
- **峰值體驗**: 發現優勢時的動畫慶祝
- **終值優化**: 完成評測後的個人化報告是高潮結尾

## 2. 信任架構體系

### 三層信任建立
1. **即時可見層**: SSL加密、用戶數量、評價星級
2. **權威專業層**: 科學方法、專家背書、數據支撐
3. **社會認同層**: 成功案例、用戶見證、即時動態

## 3. 用戶旅程設計

### 3.1 完整用戶流程圖

```
[首頁] → [評測說明] → [評測進行] → [結果展示] → [深度報告] → [行動方案]
   ↓           ↓            ↓            ↓            ↓           ↓
[信任建立] [期待設定] [進度反饋] [價值確認] [付費轉換] [持續互動]
```

### 3.2 頁面導航架構

#### 主要頁面
1. **index.html** - 主要入口點（V3.0/V4.0選擇）
2. **landing.html** - 轉換導向首頁
3. **assessment-intro.html** - 評測說明頁
4. **assessment.html** - V3.0評測執行頁（點選式介面）
5. **v4_pilot_test.html** - V4.0測試頁（Thurstonian IRT）
6. **results.html** - 動態結果頁（DNA視覺化）
7. **report-detail.html** - 深度報告頁
8. **action-plan.html** - 行動方案頁
9. **profile.html** - 個人檔案頁

#### 導航邏輯
- **前進路徑**: 線性引導，每步都有明確下一步
- **返回機制**: 麵包屑導航 + 進度儲存
- **跳出預防**: 離開提醒 + 進度自動儲存

### 3.3 AIDA 轉換漏斗

| 階段 | 頁面 | 設計重點 | 轉換目標 |
|:-----|:-----|:---------|:---------|
| **Attention** | landing.html | 強視覺衝擊、清晰標題 | 100% → 85% |
| **Interest** | assessment-intro.html | 價值展示、流程說明 | 85% → 70% |
| **Desire** | results.html | 部分揭露、價值證明 | 70% → 40% |
| **Action** | report-detail.html | 深度價值、付費轉換 | 40% → 10% |

## 4. 核心頁面設計

### 4.1 首頁（Landing Page）

#### 設計原則
- **F-Pattern 佈局**: 左上角 logo，右上角 CTA
- **視覺階層**: 標題 > 副標題 > 正文 > 細節
- **對比原則**: CTA 按鈕使用高對比色

#### 必要元素
```html
<!-- 頂部導航 -->
<nav>
  - Logo (點擊返回首頁)
  - 關於我們
  - 如何運作
  - 科學依據
  - 登入/註冊
</nav>

<!-- 英雄區塊 -->
<section class="hero">
  - 主標題：發現你的優勢DNA
  - 副標題：3分鐘科學評測，解鎖專屬成功密碼
  - CTA按鈕：立即開始免費測評
  - 信任標誌：100萬+用戶 | 科學驗證 | 3分鐘完成
</section>

<!-- 價值說明 -->
<section class="value-props">
  - 圖標化三大價值
  - 互動式優勢展示
  - 用戶見證輪播
</section>
```

### 4.2 評測說明頁（Assessment Intro）【新增】

#### 設計目的
- 設定正確期待
- 降低評測焦慮
- 提高完成率

#### 頁面內容
```html
<!-- 評測預覽 -->
<section class="assessment-preview">
  - 評測時長：約3-5分鐘
  - 題目數量：15個選擇題
  - 評測方式：選出最像和最不像你的描述
  - 視覺化流程圖
</section>

<!-- 注意事項 -->
<section class="guidelines">
  - 沒有對錯答案
  - 憑直覺選擇
  - 確保環境安靜
  - 進度會自動保存
</section>

<!-- 開始按鈕 -->
<button class="start-assessment">
  我準備好了，開始評測
</button>
```

### 4.3 評測執行頁（Assessment）

#### 設計要點
- **專注設計**: 一次一個區塊，減少干擾
- **進度可視化**: 進度條 + 數字指示（3/15）
- **即時反饋**: 選擇後的視覺確認
- **時間壓力平衡**: 顯示預估剩餘時間，但不倒數計時

#### 交互細節
```javascript
// 選擇反饋
function handleSelection(type, index) {
  // 視覺反饋
  element.classList.add('selected');
  // 觸覺反饋（移動端）
  navigator.vibrate(50);
  // 聲音反饋（可選）
  playSound('select');
  // 自動進入下一題（延遲800ms）
  if (bothSelected()) {
    setTimeout(nextBlock, 800);
  }
}

// 返回處理
function handleBack() {
  if (confirm('確定要離開嗎？您的進度會被保存')) {
    saveProgress();
    navigateBack();
  }
}
```

### 4.4 動態結果頁（Strengths Report UI v4.1）

#### 設計原則
- **科學導向**: 基於Thurstonian IRT與常模百分位的專業展示
- **三層分級**: 主導才幹(>75%) / 支援才幹(25-75%) / 待管理領域(<25%)
- **DNA雙軌視覺化**: 雙軌色帶展示12維度強度排序
- **職業原型映射**: 基於優勢組合的智能職業建議
- **行動導向**: 即時生成個人化30/60/90天行動計劃

#### 核心設計系統

##### 領域色彩編碼
```javascript
const DOMAIN_META = {
  executing: { zh: "執行力", en: "EXECUTING", color: "#7C3AED" },
  influencing: { zh: "影響力", en: "INFLUENCING", color: "#F59E0B" },
  relationship: { zh: "關係建立", en: "RELATIONSHIP", color: "#0EA5E9" },
  strategic: { zh: "戰略思維", en: "STRATEGIC", color: "#10B981" }
};
```

##### 三層分級演算法
```javascript
function useTiered(dimensions) {
  return useMemo(() => {
    const byTier = { dominant: [], supporting: [], lesser: [] };
    const sorted = [...dimensions].sort((a, b) => b.percentile - a.percentile);
    for (const d of sorted) {
      if (d.percentile > 75) byTier.dominant.push(d);
      else if (d.percentile < 25) byTier.lesser.push(d);
      else byTier.supporting.push(d);
    }
    return { byTier, sorted };
  }, [dimensions]);
}
```

#### 頁面架構

##### 1. 頂部標題區
```html
<header class="border-b bg-white">
  <div class="flex items-center justify-between">
    <!-- 品牌標識 -->
    <div class="flex items-center gap-3">
      <div class="w-9 h-9 rounded-xl bg-strategic-color"></div>
      <div>
        <div class="text-sm font-semibold">優勢評測系統 v4.1</div>
        <div class="text-xs text-neutral-500">Thurstonian IRT • 常模化百分位</div>
      </div>
    </div>

    <!-- 行動按鈕 -->
    <div class="flex gap-2">
      <button class="rounded-xl border">分享</button>
      <button class="rounded-xl bg-black text-white">下載報告 PDF</button>
    </div>
  </div>
</header>
```

##### 2. 會話資訊條
```html
<div class="rounded-2xl bg-white border p-4 flex items-center gap-4">
  <div class="text-sm">Session：<span class="font-mono">{sessionId}</span></div>
  <div class="text-sm text-neutral-600">測試時間：{testedAt}</div>
  <div class="flex items-center gap-2">
    置信度
    <div class="w-32 h-2 bg-neutral-100 rounded-full">
      <div class="h-2 rounded-full bg-emerald-500" style="width: {confidence*100}%"></div>
    </div>
    <span class="text-neutral-600">{Math.round(confidence*100)}%</span>
  </div>
</div>
```

##### 3. KPI 摘要卡片
```html
<section class="grid md:grid-cols-3 gap-4">
  <div class="rounded-2xl bg-white border p-4">
    <div class="text-neutral-500 text-xs">主導才幹</div>
    <div class="text-2xl font-semibold">{dominant.length}</div>
    <div class="text-xs text-neutral-500">>75 百分位</div>
  </div>
  <!-- 重複支援才幹和待管理領域 -->
</section>
```

##### 4. DNA雙軌色帶視覺化
```javascript
function Helix({ dimensions }) {
  const width = 960, height = 180, padding = 24;
  const laneY1 = 60, laneY2 = 120;
  const len = Math.max(2, dimensions.length);
  const step = (width - padding * 2) / (len - 1);

  return (
    <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
      {/* 雙軌線 */}
      <path d={`M ${padding} ${laneY1} L ${width-padding} ${laneY1}`} stroke="#E5E7EB" strokeWidth="2"/>
      <path d={`M ${padding} ${laneY2} L ${width-padding} ${laneY2}`} stroke="#E5E7EB" strokeWidth="2"/>

      {/* 才幹節點 */}
      {dimensions.map((d, i) => {
        const x = padding + i * step;
        const y = i % 2 === 0 ? laneY1 : laneY2;
        const color = DOMAIN_META[d.domain].color;
        const radius = 7 + (d.percentile / 100) * 6; // 大小編碼強度

        return (
          <g key={d.id}>
            <circle cx={x} cy={y} r={radius} fill={color} fillOpacity="0.9"/>
            <line x1={x} y1={y} x2={x} y2={y === laneY1 ? laneY2 : laneY1}
                  stroke={color} strokeOpacity="0.25"/>
          </g>
        );
      })}
    </svg>
  );
}
```

##### 5. 三層才幹列表
```html
<section class="grid md:grid-cols-3 gap-4">
  <!-- 主導才幹 -->
  <div class="rounded-2xl bg-white border p-4">
    <div class="text-sm font-semibold">主導才幹 (Dominant)</div>
    <ul class="mt-3 space-y-2">
      {dominant.map(d => (
        <li class="flex items-center justify-between">
          <div class="flex items-center gap-2">
            <span class="w-2.5 h-2.5 rounded-full" style="background: {domain.color}"></span>
            <span class="text-sm">{d.name}</span>
            <badge color="{domain.color}" label="{domain.zh}"/>
          </div>
          <span class="text-xs text-neutral-500">PR {d.percentile}</span>
        </li>
      ))}
    </ul>
  </div>
  <!-- 重複支援才幹和待管理領域 -->
</section>
```

##### 6. 職業原型面板
```html
<div class="rounded-2xl bg-white border p-4">
  <div class="text-sm font-semibold">職業原型參考（Beta）</div>
  <div class="mt-2 text-lg font-semibold">{persona.name}</div>
  <div class="text-sm text-neutral-600">{persona.hint}</div>
  <ul class="mt-3 grid grid-cols-2 gap-2 text-sm text-neutral-700">
    <li>建議職位：產品經理、資料科學家、解決方案架構師</li>
    <li>關鍵情境：策略規劃、跨部門協作、決策支援</li>
    <li>盲點提醒：避免過度分析，設定決策截止點</li>
    <li>搭檔建議：配對強『影響力/關係』夥伴共同推進</li>
  </ul>
  <div class="mt-3 text-xs text-neutral-500">* 參考自你的主導才幹組合，作為探索線索，非定性標籤。</div>
</div>
```

##### 7. 行動計劃面板
```html
<div class="rounded-2xl bg-white border p-4">
  <div class="text-sm font-semibold">下一步行動</div>
  <ol class="mt-3 list-decimal pl-5 space-y-2 text-sm">
    <li>下載 PDF 報告（可加入履歷或個人頁）。</li>
    <li>建立 30/60/90 天行動計畫：選擇 1–2 個主導才幹，綁定情境與產出。</li>
    <li>邀請 1 名互補夥伴（影響力/關係）共同驗證一個 PoC。</li>
  </ol>
  <div class="mt-4 flex gap-2">
    <button class="rounded-xl bg-emerald-600 text-white">生成行動計畫</button>
    <button class="rounded-xl border">與主管分享</button>
  </div>
</div>
```

##### 8. 方法論說明
```html
<section class="rounded-2xl bg-white border p-4">
  <div class="text-sm font-semibold">方法論與解讀門檻</div>
  <ul class="mt-2 grid md:grid-cols-2 gap-2 text-sm text-neutral-700">
    <li>Thurstonian IRT：由強制選擇完整作答模式推估 12 維度潛在分數 θ。</li>
    <li>常模百分位：與代表性樣本對比，支持跨人比較（Normative）。</li>
    <li>分層規則：PR>75 主導；PR 25–75 支援；PR<25 較弱。</li>
    <li>置信度：基於題項資訊量與收斂準則計算（可見上方指示條）。</li>
  </ul>
</section>
```

#### 智能職業原型映射
```javascript
function PrototypePanel({ byTier }) {
  const top4 = byTier.dominant.slice(0, 4);
  const hasStrategic = top4.some(d => d.domain === "strategic");
  const hasExecuting = top4.some(d => d.domain === "executing");
  const hasInfluencing = top4.some(d => d.domain === "influencing");

  const persona = hasStrategic && hasExecuting
    ? { name: "系統建構者", hint: "把複雜轉為結構，可對應 INTJ/ISTJ 原型" }
    : hasInfluencing
    ? { name: "關係拓展者", hint: "擅長連結與倡議，可對應 ENFP/ENFJ 原型" }
    : { name: "均衡整合者", hint: "跨域協同，面向多職能場景" };

  return persona;
}
```

### 4.5 深度報告頁（Report Detail）【新增】

#### 設計目的
- 提供付費轉換價值
- 展示專業深度
- 個性化建議

#### 報告內容
1. **優勢組合分析**
   - 優勢間的協同效應
   - 獨特性指數
   - 同類型成功案例

2. **職業發展建議**
   - 適合的職業方向（具體職位）
   - 技能發展路徑圖
   - 學習資源推薦

3. **人際互動指南**
   - 溝通風格建議
   - 團隊協作模式
   - 領導力發展方向

4. **個人成長計劃**
   - 30/60/90天行動計劃
   - 優勢強化練習
   - 盲點改善建議

### 4.6 行動方案頁（Action Plan）【新增】

#### 智能化建議系統
```python
def generate_action_plan(profile):
    """
    基於用戶優勢組合生成個性化行動方案
    """
    plan = {
        "immediate_actions": [],  # 立即可做
        "short_term_goals": [],   # 1個月內
        "long_term_vision": [],   # 3-6個月
        "resources": [],          # 具體資源
        "milestones": []         # 檢查點
    }

    # 基於優勢類型匹配方案
    if "戰略思維" in profile.top_strengths:
        plan["immediate_actions"].append({
            "action": "開始寫策略分析日記",
            "how": "每天花10分鐘分析一個商業案例",
            "tool": "推薦應用：Notion策略模板"
        })

    return plan
```

## 5. 視覺設計系統

### 5.1 v4.1新增設計組件

#### Badge 標籤系統
```javascript
function Badge({ color, label }) {
  return (
    <span className="inline-flex items-center gap-1 rounded-full px-2 py-0.5 text-[10px] font-medium"
          style={{ background: `${color}1A`, color }}>
      <i className="w-2 h-2 rounded-full" style={{ background: color }} />
      {label}
    </span>
  );
}
```

#### KPI 卡片系統
```javascript
function KPI({ title, value, desc }) {
  return (
    <div className="rounded-2xl bg-white border border-neutral-200 p-4 shadow-sm">
      <div className="text-neutral-500 text-xs">{title}</div>
      <div className="text-2xl font-semibold mt-1">{value}</div>
      {desc && <div className="text-xs text-neutral-500 mt-1">{desc}</div>}
    </div>
  );
}
```

#### 分層列表組件
```javascript
function TierList({ title, items }) {
  return (
    <div className="rounded-2xl bg-white border border-neutral-200 p-4">
      <div className="text-sm font-semibold">{title}</div>
      <ul className="mt-3 space-y-2">
        {items.map((d) => (
          <li key={d.id} className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full"
                    style={{ background: DOMAIN_META[d.domain].color }} />
              <span className="text-sm">{d.name}</span>
              <Badge color={DOMAIN_META[d.domain].color}
                     label={DOMAIN_META[d.domain].zh} />
            </div>
            <span className="text-xs text-neutral-500">PR {d.percentile}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}
```

#### 數據品質檢驗
```javascript
// 輕量級開發測試（不影響現有行為）
function runDevTests() {
  try {
    // 測試1：分級邊界
    const sample = [
      { id: "A", percentile: 80 }, // dominant
      { id: "B", percentile: 50 }, // supporting
      { id: "C", percentile: 10 }  // lesser
    ];
    const { byTier } = useTieredShim(sample);
    console.assert(byTier.dominant.length === 1, "主導才幹數量應為1");
    console.assert(byTier.supporting.length === 1, "支援才幹數量應為1");
    console.assert(byTier.lesser.length === 1, "較弱才幹數量應為1");

    // 測試2：Helix步長保護（長度=1時）
    const stepOk = computeHelixStep(1) > 0 && isFinite(computeHelixStep(1));
    console.assert(stepOk, "Helix步長應為有限正數");
  } catch (e) {
    console.warn("開發測試警告:", e);
  }
}
```

### 5.2 統一設計系統（跨專案一致性）

#### 色彩系統
```css
:root {
  /* 領域色彩（主要） */
  --executing: #7C3AED;        /* 執行力 - 紫色 */
  --influencing: #F59E0B;      /* 影響力 - 橙色 */
  --relationship: #0EA5E9;     /* 關係建立 - 藍色 */
  --strategic: #10B981;        /* 戰略思維 - 綠色 */

  /* 中性色調 */
  --neutral-50: #F9FAFB;
  --neutral-100: #F3F4F6;
  --neutral-200: #E5E7EB;
  --neutral-500: #6B7280;
  --neutral-600: #4B5563;
  --neutral-700: #374151;
  --neutral-900: #111827;

  /* 功能色彩 */
  --emerald-500: #10B981;
  --emerald-600: #059669;
  --red-500: #EF4444;
  --amber-500: #F59E0B;

  /* 語義色彩 */
  --success: var(--emerald-500);
  --warning: var(--amber-500);
  --error: var(--red-500);
  --info: var(--relationship);
}
```

#### 字體系統
```css
/* 主要字體堆疊 */
.font-primary {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
               'Microsoft JhengHei', 'PingFang TC', sans-serif;
}

/* 等寬字體（代碼、會話ID） */
.font-mono {
  font-family: 'SF Mono', Monaco, Inconsolata, 'Roboto Mono', monospace;
}

/* 字體大小階層 */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
```

#### 形狀語言
```css
/* 圓角系統 */
.rounded-sm { border-radius: 0.125rem; }    /* 2px - 小元素 */
.rounded-md { border-radius: 0.375rem; }    /* 6px - 按鈕 */
.rounded-lg { border-radius: 0.5rem; }      /* 8px - 卡片 */
.rounded-xl { border-radius: 0.75rem; }     /* 12px - 面板 */
.rounded-2xl { border-radius: 1rem; }       /* 16px - 主要容器 */
.rounded-full { border-radius: 9999px; }    /* 圓形 - 徽章、頭像 */

/* 陰影系統 */
.shadow-sm { box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05); }
.shadow { box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1); }
```

#### 標準組件規範

##### 按鈕系統
```css
/* 主要按鈕 */
.btn-primary {
  background: var(--neutral-900);
  color: white;
  border-radius: 0.75rem; /* rounded-xl */
  padding: 0.375rem 0.75rem; /* py-1.5 px-3 */
  font-size: 0.875rem; /* text-sm */
  font-weight: 500;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--neutral-700);
  transform: translateY(-1px);
}

/* 次要按鈕 */
.btn-secondary {
  background: transparent;
  color: var(--neutral-700);
  border: 1px solid var(--neutral-200);
  border-radius: 0.75rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--neutral-50);
  border-color: var(--neutral-300);
}

/* 成功按鈕 */
.btn-success {
  background: var(--emerald-600);
  color: white;
  border-radius: 0.75rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}
```

##### 卡片系統
```css
.card {
  background: white;
  border: 1px solid var(--neutral-200);
  border-radius: 1rem; /* rounded-2xl */
  padding: 1rem; /* p-4 */
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05);
}

.card-elevated {
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
}
```

##### 輸入框系統
```css
.input {
  background: white;
  border: 1px solid var(--neutral-200);
  border-radius: 0.5rem; /* rounded-lg */
  padding: 0.5rem 0.75rem;
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: var(--strategic);
  box-shadow: 0 0 0 3px rgb(16 185 129 / 0.1);
}
```

#### 版面配置標準
```css
/* 主要容器 */
.container {
  max-width: 72rem; /* max-w-6xl - 1152px */
  margin: 0 auto;
  padding: 0 1.5rem; /* px-6 */
}

/* 間距系統 */
.space-y-2 > * + * { margin-top: 0.5rem; }
.space-y-3 > * + * { margin-top: 0.75rem; }
.space-y-4 > * + * { margin-top: 1rem; }
.space-y-6 > * + * { margin-top: 1.5rem; }

/* 網格系統 */
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.gap-2 { gap: 0.5rem; }
.gap-4 { gap: 1rem; }
```

### 5.3 格式塔原則應用

#### 鄰近性 (Proximity)
- 相關功能按鈕組合（flex gap-2）
- 優勢卡片分組展示（grid gap-4）
- 表單欄位邏輯分區（space-y-4）

#### 相似性 (Similarity)
- 統一的卡片樣式（rounded-2xl bg-white border）
- 一致的按鈕形狀（rounded-xl）
- 重複的圖標系統（w-2.5 h-2.5 rounded-full）

#### 連續性 (Continuity)
- 流暢的頁面過渡（transition-all duration-200）
- 進度條的視覺延續（DNA雙軌連接線）
- 步驟指示的連接線（SVG path連接）

#### 閉合性 (Closure)
- 進度環的完成感（圓形進度指示器）
- 評測完成的視覺閉環（從開始到結果的完整路徑）
- 優勢拼圖的完整性（12維度完整覆蓋）

### 5.4 跨頁面一致性實施

#### 全頁面設計系統應用
基於Strengths Report UI v4.1的成功設計，所有頁面都應採用相同的視覺語言：

```css
/* 全域基礎樣式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI',
               'Microsoft JhengHei', 'PingFang TC', sans-serif;
  background: #F9FAFB; /* neutral-50 */
  color: #111827; /* neutral-900 */
  line-height: 1.6;
}

/* 主要頁面容器 */
.page-container {
  min-height: 100vh;
  background: #F9FAFB;
}

/* 標準頁面標題 */
.page-header {
  background: white;
  border-bottom: 1px solid #E5E7EB;
  padding: 1.5rem 0;
}

/* 標準內容區域 */
.page-content {
  max-width: 72rem;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}
```

#### 頁面特定應用

##### index.html - 主要入口點
```css
.entry-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1);
  transition: all 0.2s ease;
}

.entry-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
}

.version-badge {
  background: #10B981; /* strategic color */
  color: white;
  border-radius: 9999px;
  padding: 0.25rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
}
```

##### landing.html - 轉換導向首頁
```css
.hero-section {
  background: linear-gradient(135deg, #10B981 0%, #0EA5E9 100%);
  color: white;
  border-radius: 1rem;
  padding: 3rem 2rem;
  text-align: center;
}

.cta-button {
  background: #111827;
  color: white;
  border-radius: 0.75rem;
  padding: 1rem 2rem;
  font-size: 1.125rem;
  font-weight: 600;
  transition: all 0.2s ease;
}

.cta-button:hover {
  background: #374151;
  transform: translateY(-1px);
}
```

##### assessment.html - 評測頁面
```css
.question-card {
  background: white;
  border: 1px solid #E5E7EB;
  border-radius: 1rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
}

.option-button {
  background: white;
  border: 2px solid #E5E7EB;
  border-radius: 0.75rem;
  padding: 1rem;
  width: 100%;
  text-align: left;
  transition: all 0.2s ease;
  cursor: pointer;
}

.option-button:hover {
  border-color: #10B981;
  background: #F0FDF4;
}

.option-button.selected {
  border-color: #10B981;
  background: #DCFCE7;
  color: #065F46;
}

.progress-bar {
  background: #E5E7EB;
  border-radius: 9999px;
  height: 0.5rem;
  overflow: hidden;
}

.progress-fill {
  background: #10B981;
  height: 100%;
  border-radius: 9999px;
  transition: width 0.3s ease;
}
```

##### 其他頁面統一標準
- **assessment-intro.html**: 使用相同的卡片系統和按鈕樣式
- **v4_pilot_test.html**: 統一的選項按鈕和進度指示器
- **report-detail.html**: 繼承results.html的設計語言
- **action-plan.html**: 使用相同的表單和按鈕組件
- **profile.html**: 統一的用戶界面元素

### 5.5 響應式設計策略

#### 移動優先原則
```css
/* 基礎移動端樣式 */
.container {
  width: 100%;
  padding: 16px;
}

/* 平板增強 */
@media (min-width: 768px) {
  .container {
    max-width: 750px;
    padding: 24px;
  }
}

/* 桌面優化 */
@media (min-width: 1024px) {
  .container {
    max-width: 1200px;
    padding: 32px;
  }
}
```

## 6. 交互設計規範

### 6.1 微交互設計

#### 按鈕狀態
```css
.btn {
  /* 默認 */
  transition: all 0.3s ease;

  /* 懸停 */
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  }

  /* 點擊 */
  &:active {
    transform: translateY(0);
  }

  /* 載入中 */
  &.loading {
    pointer-events: none;
    opacity: 0.7;
  }
}
```

#### 頁面過渡
```javascript
// 平滑過渡
function pageTransition(targetPage) {
  // 淡出當前頁面
  currentPage.style.opacity = '0';

  // 載入動畫
  showLoader();

  // 載入新頁面
  setTimeout(() => {
    window.location.href = targetPage;
  }, 300);
}
```

### 6.2 錯誤處理與反饋

#### 錯誤預防
- 實時驗證
- 智能提示
- 操作確認

#### 錯誤恢復
```javascript
function handleError(error) {
  // 保存當前狀態
  saveState();

  // 友好錯誤提示
  showToast({
    type: 'error',
    message: '哎呀，出了點問題',
    action: '重試',
    onAction: () => retry()
  });

  // 自動恢復機制
  setTimeout(() => {
    autoRecover();
  }, 3000);
}
```

## 7. 深度內容策略

### 7.1 個性化內容生成

#### 優勢解讀模板
```javascript
const strengthTemplates = {
  '戰略思維': {
    definition: '你擅長看到大局，理解複雜系統間的關聯',
    workplace: '在工作中，你能快速理解商業模式，預見潛在問題',
    examples: [
      '制定長期規劃',
      '分析市場趨勢',
      '優化業務流程'
    ],
    famousPeople: ['比爾·蓋茨', '馬雲'],
    developmentTips: [
      '練習系統思考：使用思維導圖工具',
      '案例分析：每週研究一個商業案例',
      '寫作輸出：記錄你的策略思考'
    ]
  },
  // ... 其他11個維度
};
```

#### 組合效應分析
```javascript
const synergyAnalysis = {
  ['戰略思維', '溝通']: {
    synergy: '策略傳播者',
    description: '你不僅能制定優秀策略，還能清晰傳達願景',
    careers: ['產品經理', '創業家', '管理顧問'],
    advice: '考慮需要同時運用分析和表達能力的角色'
  },
  // ... 其他組合
};
```

### 7.2 行動建議深化

#### 具體化建議框架
```python
class ActionRecommendation:
    def __init__(self, strength, context):
        self.strength = strength
        self.context = context  # 用戶背景

    def generate_actions(self):
        actions = {
            'daily_practice': self._get_daily_practice(),
            'skill_building': self._get_skills_to_learn(),
            'project_ideas': self._get_project_suggestions(),
            'reading_list': self._get_book_recommendations(),
            'online_courses': self._get_course_links(),
            'community': self._get_community_suggestions()
        }
        return actions

    def _get_daily_practice(self):
        # 每日可執行的小練習
        if self.strength == '學習力':
            return [
                '費曼技巧：向他人解釋今天學到的一個概念',
                '康奈爾筆記：用此方法記錄一次會議',
                '間隔重複：使用Anki復習重要知識點'
            ]
```

### 7.3 進度追蹤系統

#### 返回引導機制
```javascript
class ProgressTracker {
  constructor() {
    this.checkpoints = [
      'landing_viewed',
      'assessment_started',
      'assessment_50_complete',
      'assessment_completed',
      'results_viewed',
      'report_downloaded'
    ];
  }

  saveProgress(checkpoint, data) {
    localStorage.setItem('progress', JSON.stringify({
      checkpoint,
      data,
      timestamp: Date.now()
    }));
  }

  getReturnPath() {
    const progress = JSON.parse(localStorage.getItem('progress'));

    if (!progress) return '/landing.html';

    // 根據進度返回適當頁面
    switch(progress.checkpoint) {
      case 'assessment_started':
      case 'assessment_50_complete':
        return '/assessment.html?resume=true';
      case 'assessment_completed':
        return `/results.html?session=${progress.data.sessionId}`;
      default:
        return '/landing.html';
    }
  }

  showReturnPrompt() {
    const lastVisit = localStorage.getItem('lastVisit');
    if (lastVisit && Date.now() - lastVisit < 86400000) { // 24小時內
      showToast({
        message: '歡迎回來！要繼續上次的進度嗎？',
        actions: [
          { text: '繼續', onClick: () => this.resume() },
          { text: '重新開始', onClick: () => this.restart() }
        ]
      });
    }
  }
}
```

## 8. 技術規格

### 8.1 性能指標
- FCP (First Contentful Paint) < 1.0s
- LCP (Largest Contentful Paint) < 2.5s
- FID (First Input Delay) < 100ms
- CLS (Cumulative Layout Shift) < 0.1

### 8.2 瀏覽器支援
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### 8.3 響應式斷點
- Mobile: 320px - 767px
- Tablet: 768px - 1023px
- Desktop: 1024px - 1439px
- Wide: 1440px+

## 9. 性能優化

### 9.1 載入優化
- 關鍵 CSS 內聯
- JavaScript 延遲載入
- 圖片懶載入
- 預連接關鍵域名

### 9.2 運行時優化
- 虛擬滾動
- 防抖節流
- Web Workers
- 請求快取

## 10. 文案指南

### 10.1 語氣與風格
- **專業但親切**: 避免過於學術的表達
- **積極正向**: 強調優勢和可能性
- **行動導向**: 使用動詞開頭的句子

### 10.2 術語轉換
| 技術術語 | 用戶友好表達 |
|:---------|:------------|
| Thurstonian IRT | 智能優勢識別 |
| 四選二強迫選擇 | 優勢配對選擇 |
| 常模參照 | 同齡人對比 |

## 11. 實施檢查清單

### 11.1 頁面完整性檢查

- [x] **index.html** - 主要入口點
  - [x] V3.0/V4.0選擇介面
  - [x] 統一導航入口
  - [x] 版本說明清晰

- [x] **landing.html** - 首頁實現
  - [x] 信任標誌顯示
  - [x] CTA 按鈕醒目
  - [x] 價值主張清晰
  - [x] 響應式適配

- [x] **assessment-intro.html** - 評測說明頁
  - [x] 流程說明清楚
  - [x] 期待設定恰當
  - [x] 開始按鈕明確

- [x] **assessment.html** - V3.0評測頁
  - [x] 點選式介面（與V4.0統一）
  - [x] 進度保存功能
  - [x] 返回提醒機制
  - [x] 自動下一題

- [x] **v4_pilot_test.html** - V4.0測試頁
  - [x] Thurstonian IRT評測
  - [x] 防重複選擇邏輯
  - [x] 環境適配（雙埠支援）
  - [x] 與assessment.html統一設計

- [x] **results.html** - 動態結果頁（Strengths Report UI v4.1）
  - [x] DNA雙螺旋視覺化（SVG雙軌色帶）
  - [x] 三層分級系統（主導>75% / 支援25-75% / 待管理<25%）
  - [x] 智能職業原型映射
  - [x] KPI摘要卡片展示
  - [x] 會話資訊與置信度指示器
  - [x] 科學方法論說明
  - [x] 個人化行動計劃生成
  - [x] 統一設計系統（色彩/字體/形狀）

- [x] **report-detail.html** - 深度報告
  - [x] 基礎頁面架構
  - [ ] 內容個性化（待優化）
  - [ ] 建議具體化（待優化）
  - [ ] 下載功能（待實現）

- [x] **action-plan.html** - 行動方案
  - [x] 基礎頁面架構
  - [ ] 計劃個性化（待實現）
  - [ ] 資源連結整合（待實現）
  - [ ] 進度追蹤（待實現）

- [x] **profile.html** - 個人檔案
  - [x] 基礎頁面架構
  - [ ] 歷史記錄整合（待實現）
  - [ ] 進步追蹤（待實現）
  - [ ] 分享功能（待實現）

### 11.2 設計系統一致性檢查

- [x] **Strengths Report UI v4.1設計系統**已建立
  - [x] 統一色彩系統（4個領域色彩+中性色調）
  - [x] 標準字體堆疊（系統字體+等寬字體）
  - [x] 形狀語言（圓角系統+陰影階層）
  - [x] 組件規範（按鈕+卡片+輸入框）

- [ ] **跨頁面設計系統應用**（待實施）
  - [ ] index.html: 應用入口卡片和版本徽章樣式
  - [ ] landing.html: 更新英雄區塊和CTA按鈕
  - [ ] assessment.html: 統一問題卡片和選項按鈕
  - [ ] v4_pilot_test.html: 保持與assessment.html一致
  - [ ] assessment-intro.html: 應用統一卡片系統
  - [ ] report-detail.html: 繼承results.html設計語言
  - [ ] action-plan.html: 使用統一表單組件
  - [ ] profile.html: 統一用戶界面元素

### 11.3 用戶流程驗證

- [x] 新用戶完整流程順暢
- [x] 返回用戶恢復機制完善
- [x] 錯誤處理友好
- [x] 載入狀態明確
- [x] 離開確認提醒

## 12. 總結

本規範（v4.1）在v4.0基礎上完成了動態結果系統實現，深度整合認知心理學原理、格式塔設計原則、AIDA模型和Cialdini說服力原則，解決了以下關鍵問題：

### V4.1版本新增功能
1. ✅ **Strengths Report UI v4.1** - 完全重寫結果頁面，採用現代化設計語言
2. ✅ **DNA雙軌視覺化** - SVG實現的雙螺旋結構，色彩編碼領域分類
3. ✅ **三層分級系統** - 科學化分類（主導>75% / 支援25-75% / 待管理<25%）
4. ✅ **智能職業原型** - 基於優勢組合的MBTI關聯職業建議
5. ✅ **統一設計系統** - 建立跨頁面一致的色彩、字體、形狀語言
6. ✅ **科學方法論展示** - Thurstonian IRT與常模百分位的專業說明
7. ✅ **動態個人化** - session驅動的完全個人化結果展示
8. ✅ **行動導向設計** - 即時生成30/60/90天個人行動計劃

### 已解決技術問題
1. ✅ **IRT計分問題** - 修復DIMENSION_MAPPING，確保不同答案產生不同結果
2. ✅ **UI邏輯錯誤** - 防止同選項重複選擇為「最像」和「最不像」
3. ✅ **API路由問題** - 修復端點404錯誤，確保JSON回應格式
4. ✅ **靜態結果問題** - 從硬編碼靜態內容轉為動態session載入
5. ✅ **導航不一致** - 統一所有評測按鈕路由到正確頁面

### 核心技術架構改進
- **雙版本並行**: V3.0傳統評測 + V4.0 IRT前沿研究
- **動態個性化**: 從靜態展示轉為session驅動的個人化體驗
- **視覺創新**: DNA雙螺旋替代傳統圖表，提升峰值體驗
- **容錯設計**: 多層fallback確保任何情況下都有合適展示

### 系統完整性狀態
- **核心流程**: 完全實現並測試通過
- **前端介面**: 9個主要頁面全部到位
- **後端API**: 雙API架構支撐V3.0/V4.0評測
- **數據視覺化**: DNA結構創新呈現優勢組合

### 下一階段重點
1. **設計系統跨頁面實施** - 將Strengths Report UI v4.1設計語言應用到所有9個頁面
2. **深化個性化引擎** - 擴展職業原型映射和行動計劃生成算法
3. **PDF報告與分享功能** - 實現高質量報告下載和社交分享機制
4. **用戶歷史記錄系統** - 建立進度追蹤和多次測試比較功能
5. **性能與體驗優化** - 載入速度提升和微交互完善

### 設計系統實施路線圖
**第一波（核心頁面）**：index.html → landing.html → assessment.html
**第二波（功能頁面）**：assessment-intro.html → v4_pilot_test.html
**第三波（深度功能）**：report-detail.html → action-plan.html → profile.html

透過v4.1版本的完整實現，系統已經建立了從「科學評測 → 動態結果 → 個性化建議」的完整價值鏈，並確立了現代化的設計標準。下一階段將重點確保整個系統的視覺一致性，為後續的商業化和規模化奠定堅實基礎。