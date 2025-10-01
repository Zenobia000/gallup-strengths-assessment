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

## 2. 均衡版映射（四域 × 三才）

> 依據組織行為、社會資本、情緒調節與策略認知等學理調整，使四域各含 3 個才幹，避免某域過重。

| 領域 | 才幹代碼 | 才幹名稱 | 學理錨點（精要） |
| :--- | :--- | :--- | :--- |
| **執行力 Executing** | **T1** | 結構化執行 | Locke & Latham 目標設定理論：將目標轉為步驟可顯著提升績效。 |
| | **T2** | 品質與完備 | TQM/Kaizen：持續改善、第一次就把事情做對。 |
| | **T12** | 責任與當責 | Accountability/Ownership：結果導向的行為承諾。 |
| **影響力 Influencing** | **T5** | 影響與倡議 | 轉換型領導：願景陳述、說服與動員。 |
| | **T7** | 客戶導向 | 服務主導邏輯（SDL）：價值共創與外部影響。 |
| | **T11** | 衝突整合 | 衝突管理（協作式）：議題框定與形成共識。 |
| **關係建立 Relationship**| **T6** | 協作與共好 | 團隊動力學/高互信文化。 |
| | **T9** | 紀律與信任 | 社會資本（Coleman）：可靠性提升關係資產存量。 |
| | **T10** | 壓力調節 | 情緒調節理論/情緒穩定性支撐關係品質。 |
| **戰略思維 Strategic** | **T3** | 探索與創新 | 開放性/探索式學習（Exploration）。 |
| | **T4** | 分析與洞察 | 認知─決策研究：訊號抽取、因果推理。 |
| | **T8** | 學習與成長 | 成長心態（Dweck）：能力可塑，長期優勢來源。 |

---

## 3. 開發用數據 (Data for Implementation)

為了方便開發，以下是均衡版映射關係的 JSON 格式表示。

```json
{
  "T1": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" },
  "T2": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" },
  "T12": { "domain_id": "EXECUTING", "domain_name": "執行力", "color": "purple" },
  "T5": { "domain_id": "INFLUENCING", "domain_name": "影響力", "color": "orange" },
  "T7": { "domain_id": "INFLUENCING", "domain_name": "影響力", "color": "orange" },
  "T11": { "domain_id": "INFLUENCING", "domain_name": "影響力", "color": "orange" },
  "T6": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T9": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T10": { "domain_id": "RELATIONSHIP_BUILDING", "domain_name": "關係建立", "color": "blue" },
  "T3": { "domain_id": "STRATEGIC_THINKING", "domain_name": "戰略思維", "color": "green" },
  "T4": { "domain_id": "STRATEGIC_THINKING", "domain_name": "戰略思維", "color": "green" },
  "T8": { "domain_id": "STRATEGIC_THINKING", "domain_name": "戰略思維", "color": "green" }
}
```
*註：`color` 欄位是基於蓋洛普官方配色給出的建議，可供前端UI設計參考。*
