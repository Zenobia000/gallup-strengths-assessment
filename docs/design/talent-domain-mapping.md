# 天賦才幹領域映射 (Talent Domain Mapping)

> **文件版本**: 1.0
> **日期**: 2025-09-30
> **目的**: 本文件定義了12個核心才幹維度如何歸類到四大才幹領域，並闡述其背後的理論依據。

---

## 1. 理論基礎：蓋洛普四大領導力領域

我們的分類框架，是將蓋洛普(Gallup)公司在其 CliftonStrengths 理論中提出的「四大領導力領域」(Four Domains of Leadership Strength)應用於我們的12個才幹維度。這四大領域並非定義「你是哪一類領導」，而是回答「你如何做出貢獻」。

這四大領域分別是：

1.  **執行力 (Executing)**: 擅長將想法付諸實行，讓事情發生。
2.  **影響力 (Influencing)**: 擅長說服他人，掌控局面並確保團隊的聲音被聽見。
3.  **關係建立 (Relationship Building)**: 擅長建立穩固的關係，能將團隊凝聚在一起。
4.  **戰略思維 (Strategic Thinking)**: 擅長吸收和分析資訊，幫助團隊做出更明智的決策。

## 2. 完整映射關係與對應邏輯

下表詳細列出了我們的12個才幹維度與四大領域的對應關係及其理由。

| 才幹維度 | 領域 | 對應邏輯 (Mapping Rationale) |
| :--- | :--- | :--- |
| **T1: 結構化執行** | **執行力** | 核心在於將抽象計畫轉化為具體的、可執行的步驟，是「讓事情發生」的基礎。 |
| **T2: 品質與完備** | **執行力** | 關注任務的完成度與品質，確保事情不僅被完成，而且被「做對」。 |
| **T9: 紀律與信任** | **執行力** | 透過建立秩序和流程來確保執行的穩定性與可預測性。 |
| **T12: 責任與當責** | **執行力** | 強調對結果的承諾與擁有感，是驅動執行到底的內在力量。 |
| **T5: 影響與倡議** | **影響力** | 其核心是說服、溝通與激勵他人，是影響力領域最直接的體現。 |
| **T6: 協作與共好** | **關係建立** | 專注於團隊的和諧與共識，是凝聚團隊、建立內部信任的關鍵。 |
| **T7: 客戶導向** | **關係建立** | 透過理解與滿足外部人員（客戶）的需求來建立和維護關係。 |
| **T10: 壓力調節** | **關係建立** | 在壓力下保持情緒穩定，能有效防止關係的破裂，是維持健康人際關係的基石。 |
| **T11: 衝突整合** | **關係建立** | 透過調解分歧來修復和加強關係，將潛在的衝突轉化為更深的連結。 |
| **T3: 探索與創新** | **戰略思維** | 專注於發掘新觀點和可能性，為戰略決策提供創新的輸入。 |
| **T4: 分析與洞察** | **戰略思維** | 透過深度分析數據與資訊來理解現狀、預測未來，是所有戰略思考的核心。 |
| **T8: 學習與成長** | **戰略思維** | 不斷吸收新知，為制定更優越的長期戰略提供源源不斷的養分。 |

---

## 3. 開發用數據 (Data for Implementation)

為了方便開發，以下是上述映射關係的 JSON 格式表示。

```json
{
  "T1": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" },
  "T2": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" },
  "T3": { "domain_id": "STRATEGIC_THINKING", "domain_name": "戰略思維", "color": "green" },
  "T4": { "domain_id": "STRATEGIC_THINKING", "domain_name": "戰略思維", "color": "green" },
  "T5": { "domain_id": "INFLUENCING", "domain_name": "影響力", "color": "orange" },
  "T6": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T7": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T8": { "domain_id": "STRATEGIC_THINKING", "domain_name": "戰略思維", "color": "green" },
  "T9": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" },
  "T10": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T11": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T12": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" }
}
```
*註：`color` 欄位是基於蓋洛普官方配色給出的建議，可供前端UI設計參考。*
