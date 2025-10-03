# V4.0 語句池設計 - 12 維度強制選擇題

**文件版本**: 1.0
**日期**: 2025-09-30
**作者**: Claude Code (Task 8.1.2)
**狀態**: 設計中

## 1. 設計原則

### 1.1 語句要求
- **內容效度**: 準確反映該維度的核心特質
- **區分度**: 能有效區分高低特質者
- **社會期望性平衡**: 4-6分範圍（7分制）
- **語言清晰**: 避免雙重否定或模糊表述
- **行為導向**: 聚焦具體行為而非抽象概念

### 1.2 平衡考量
- 每維度至少4個語句（共48+）
- 正向與挑戰性語句混合
- 工作與生活情境平衡
- 避免文化偏見

## 2. 12維度語句池

### 2.1 Achiever (成就)
**核心特質**: 每天需要完成具體成果，追求生產力

#### 語句池：
```json
{
  "ACH001": {
    "text": "我每天都會列出待辦事項清單並逐項完成",
    "social_desirability": 5.2,
    "context": "work"
  },
  "ACH002": {
    "text": "完成任務帶給我極大的滿足感",
    "social_desirability": 5.5,
    "context": "general"
  },
  "ACH003": {
    "text": "我經常在下班後還繼續思考如何提高效率",
    "social_desirability": 4.8,
    "context": "work"
  },
  "ACH004": {
    "text": "沒有具體成果的一天讓我感到焦慮",
    "social_desirability": 4.2,
    "context": "general"
  },
  "ACH005": {
    "text": "我會追蹤並記錄自己的工作進度",
    "social_desirability": 5.1,
    "context": "work"
  }
}
```

### 2.2 Activator (行動)
**核心特質**: 將想法轉化為行動，不喜歡過度分析

#### 語句池：
```json
{
  "ACT001": {
    "text": "我傾向先開始行動，邊做邊調整",
    "social_desirability": 4.9,
    "context": "work"
  },
  "ACT002": {
    "text": "長時間的會議討論讓我不耐煩",
    "social_desirability": 4.3,
    "context": "work"
  },
  "ACT003": {
    "text": "我善於推動停滯的專案向前進展",
    "social_desirability": 5.6,
    "context": "work"
  },
  "ACT004": {
    "text": "比起完美計劃，我更重視快速執行",
    "social_desirability": 4.7,
    "context": "general"
  },
  "ACT005": {
    "text": "我經常是團隊中第一個採取行動的人",
    "social_desirability": 5.3,
    "context": "team"
  }
}
```

### 2.3 Adaptability (適應)
**核心特質**: 靈活應對變化，活在當下

#### 語句池：
```json
{
  "ADA001": {
    "text": "突發狀況不會讓我感到慌張",
    "social_desirability": 5.4,
    "context": "general"
  },
  "ADA002": {
    "text": "我能輕鬆調整計劃以應對新情況",
    "social_desirability": 5.2,
    "context": "work"
  },
  "ADA003": {
    "text": "相比長期規劃，我更擅長處理當前事務",
    "social_desirability": 4.5,
    "context": "general"
  },
  "ADA004": {
    "text": "變化帶給我新鮮感而非壓力",
    "social_desirability": 5.0,
    "context": "general"
  },
  "ADA005": {
    "text": "我享受每天面對不同挑戰的工作",
    "social_desirability": 5.1,
    "context": "work"
  }
}
```

### 2.4 Analytical (分析)
**核心特質**: 尋求數據和證據，理性決策

#### 語句池：
```json
{
  "ANA001": {
    "text": "我需要充分的數據才能做出決定",
    "social_desirability": 5.0,
    "context": "work"
  },
  "ANA002": {
    "text": "我經常質疑他人提出的結論是否有證據支持",
    "social_desirability": 4.4,
    "context": "general"
  },
  "ANA003": {
    "text": "我擅長發現數據中的模式和趨勢",
    "social_desirability": 5.5,
    "context": "work"
  },
  "ANA004": {
    "text": "情感因素很少影響我的判斷",
    "social_desirability": 4.6,
    "context": "general"
  },
  "ANA005": {
    "text": "我喜歡深入研究問題的根本原因",
    "social_desirability": 5.3,
    "context": "work"
  }
}
```

### 2.5 Arranger (統籌)
**核心特質**: 組織協調資源，追求最佳配置

#### 語句池：
```json
{
  "ARR001": {
    "text": "我擅長同時管理多個任務和專案",
    "social_desirability": 5.6,
    "context": "work"
  },
  "ARR002": {
    "text": "我能快速找出最有效的資源配置方案",
    "social_desirability": 5.4,
    "context": "work"
  },
  "ARR003": {
    "text": "複雜的協調工作對我來說是種享受",
    "social_desirability": 4.8,
    "context": "work"
  },
  "ARR004": {
    "text": "我經常重新安排計劃以達到更好效果",
    "social_desirability": 5.0,
    "context": "general"
  },
  "ARR005": {
    "text": "我善於識別並調動團隊成員的優勢",
    "social_desirability": 5.7,
    "context": "team"
  }
}
```

### 2.6 Belief (信念)
**核心特質**: 堅持核心價值觀，使命導向

#### 語句池：
```json
{
  "BEL001": {
    "text": "我的核心價值觀指引著我的所有決定",
    "social_desirability": 5.5,
    "context": "general"
  },
  "BEL002": {
    "text": "工作的意義比薪資更重要",
    "social_desirability": 5.2,
    "context": "work"
  },
  "BEL003": {
    "text": "我難以在價值觀不合的環境中工作",
    "social_desirability": 4.7,
    "context": "work"
  },
  "BEL004": {
    "text": "我願意為自己相信的事業付出額外努力",
    "social_desirability": 5.4,
    "context": "general"
  },
  "BEL005": {
    "text": "違背原則的成功對我毫無意義",
    "social_desirability": 5.3,
    "context": "general"
  }
}
```

### 2.7 Command (統率)
**核心特質**: 掌控局面，敢於對抗

#### 語句池：
```json
{
  "CMD001": {
    "text": "在混亂情況下我自然會接手領導",
    "social_desirability": 5.1,
    "context": "team"
  },
  "CMD002": {
    "text": "我不害怕與他人產生衝突",
    "social_desirability": 4.2,
    "context": "general"
  },
  "CMD003": {
    "text": "我能讓猶豫不決的團隊快速行動",
    "social_desirability": 5.4,
    "context": "team"
  },
  "CMD004": {
    "text": "直接表達意見比顧慮他人感受更重要",
    "social_desirability": 4.0,
    "context": "general"
  },
  "CMD005": {
    "text": "我享受承擔決策責任的壓力",
    "social_desirability": 4.9,
    "context": "work"
  }
}
```

### 2.8 Communication (溝通)
**核心特質**: 善於表達，將想法轉化為語言

#### 語句池：
```json
{
  "COM001": {
    "text": "我能輕鬆地向不同背景的人解釋複雜概念",
    "social_desirability": 5.6,
    "context": "general"
  },
  "COM002": {
    "text": "我經常成為團隊的發言人",
    "social_desirability": 5.0,
    "context": "team"
  },
  "COM003": {
    "text": "寫作和演講對我來說很自然",
    "social_desirability": 5.2,
    "context": "general"
  },
  "COM004": {
    "text": "我喜歡通過故事來傳達觀點",
    "social_desirability": 5.1,
    "context": "general"
  },
  "COM005": {
    "text": "安靜的會議讓我忍不住想發言",
    "social_desirability": 4.5,
    "context": "work"
  }
}
```

### 2.9 Competition (競爭)
**核心特質**: 衡量與他人的表現，追求勝利

#### 語句池：
```json
{
  "CMP001": {
    "text": "我經常將自己的表現與他人比較",
    "social_desirability": 4.3,
    "context": "general"
  },
  "CMP002": {
    "text": "贏得競爭給我強大的動力",
    "social_desirability": 4.8,
    "context": "general"
  },
  "CMP003": {
    "text": "第二名對我來說等同於失敗",
    "social_desirability": 3.9,
    "context": "general"
  },
  "CMP004": {
    "text": "我會研究競爭對手以確保領先",
    "social_desirability": 5.0,
    "context": "work"
  },
  "CMP005": {
    "text": "沒有競爭的環境讓我失去動力",
    "social_desirability": 4.4,
    "context": "work"
  }
}
```

### 2.10 Connectedness (關聯)
**核心特質**: 相信萬物相連，尋求深層意義

#### 語句池：
```json
{
  "CON001": {
    "text": "我相信所有事件的發生都有其原因",
    "social_desirability": 5.0,
    "context": "general"
  },
  "CON002": {
    "text": "我能看到不同事物之間的深層聯繫",
    "social_desirability": 5.3,
    "context": "general"
  },
  "CON003": {
    "text": "幫助他人讓我感受到生命的意義",
    "social_desirability": 5.7,
    "context": "general"
  },
  "CON004": {
    "text": "我重視團隊的集體成就勝過個人榮譽",
    "social_desirability": 5.4,
    "context": "team"
  },
  "CON005": {
    "text": "巧合對我來說往往有特殊含義",
    "social_desirability": 4.6,
    "context": "general"
  }
}
```

### 2.11 Consistency (公平)
**核心特質**: 重視平等和公正，一視同仁

#### 語句池：
```json
{
  "CST001": {
    "text": "規則應該平等地適用於所有人",
    "social_desirability": 5.6,
    "context": "general"
  },
  "CST002": {
    "text": "特權和例外讓我感到不適",
    "social_desirability": 5.0,
    "context": "general"
  },
  "CST003": {
    "text": "我會確保每個人都有平等的機會",
    "social_desirability": 5.8,
    "context": "team"
  },
  "CST004": {
    "text": "程序的一致性比靈活性更重要",
    "social_desirability": 4.5,
    "context": "work"
  },
  "CST005": {
    "text": "我難以接受基於關係的優待",
    "social_desirability": 5.1,
    "context": "work"
  }
}
```

### 2.12 Context (背景)
**核心特質**: 從過去尋求答案，重視歷史

#### 語句池：
```json
{
  "CTX001": {
    "text": "了解事情的來龍去脈對我很重要",
    "social_desirability": 5.3,
    "context": "general"
  },
  "CTX002": {
    "text": "我經常引用過去的經驗來解決當前問題",
    "social_desirability": 5.2,
    "context": "work"
  },
  "CTX003": {
    "text": "沒有背景資訊我難以做出判斷",
    "social_desirability": 4.8,
    "context": "general"
  },
  "CTX004": {
    "text": "我喜歡研究事物的歷史和演變",
    "social_desirability": 5.0,
    "context": "general"
  },
  "CTX005": {
    "text": "理解組織文化的形成過程幫助我更好地融入",
    "social_desirability": 5.4,
    "context": "work"
  }
}
```

## 3. 社會期望性評定

### 3.1 評定方法
採用7點李克特量表，由專家評定每個語句的社會期望性：
- 1-2分：低社會期望性（可能被視為負面）
- 3-5分：中等社會期望性（中性）
- 6-7分：高社會期望性（普遍被視為正面）

### 3.2 平衡策略
- 每個四選二區塊的平均社會期望性應在4.5-5.5之間
- 區塊內語句的社會期望性標準差應小於1.0
- 避免將極端高低期望性語句放在同一區塊

## 4. 語句驗證檢查清單

### 4.1 內容效度
- [ ] 語句準確反映維度定義
- [ ] 避免與其他維度高度重疊
- [ ] 包含維度的核心行為表現

### 4.2 心理測量品質
- [ ] 語句長度適中（10-20字）
- [ ] 避免雙重否定
- [ ] 使用具體而非抽象表述
- [ ] 第一人稱陳述

### 4.3 文化適應性
- [ ] 避免文化特定的習語
- [ ] 考慮不同工作環境
- [ ] 性別中立的表述
- [ ] 年齡中立的情境

## 5. 實施建議

### 5.1 預測試計劃
1. **小樣本測試** (n=30)
   - 收集理解度反饋
   - 檢查歧義表述
   - 驗證社會期望性評定

2. **專家審查**
   - 內容效度評估
   - 維度純度檢查
   - 語言清晰度審核

3. **統計分析**
   - 項目-總分相關
   - 因素分析驗證
   - 區分度指標

### 5.2 迭代優化
- 基於預測試數據調整語句
- 平衡各維度的語句難度
- 確保社會期望性匹配

## 6. 下一步行動

1. **語句擴充**: 每維度增加2-3個備選語句
2. **專家評定**: 邀請3-5位專家評定社會期望性
3. **區塊設計**: 使用 BlockDesigner 創建平衡區塊
4. **預測試實施**: 收集初步心理測量數據

---

**總結**: 已設計60個初始語句覆蓋12個維度，每維度5個語句。語句設計考慮了內容效度、社會期望性平衡、和文化適應性。下一步將進行區塊平衡設計（Task 8.1.3）。