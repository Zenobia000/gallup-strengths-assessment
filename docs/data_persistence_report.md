# 資料留存與分析報告

**更新時間**: 2025-09-30 23:15

## 📊 資料留存狀況

### 資料庫概況
- **資料庫位置**: `/src/main/python/data/gallup_assessment.db`
- **資料庫大小**: 217 KB
- **資料庫類型**: SQLite3

### 資料表結構與內容

| 資料表 | 用途 | 目前筆數 | 留存狀態 |
|--------|------|----------|----------|
| **v4_sessions** | V4.0 評測會話記錄 | 6 | ✅ 有資料 |
| **v4_assessment_results** | V4.0 評測結果 | 0 | ⚠️ 無資料 |
| **v4_calibration_data** | V4.0 IRT 校準資料 | - | 📋 待確認 |
| **v4_parameters** | V4.0 模型參數 | - | 📋 待確認 |
| **sessions** | 一般會話記錄 | 5 | ✅ 有資料 |
| **responses** | 用戶回應記錄 | 0 | ⚠️ 無資料 |
| **scores** | 評分記錄 | 1 | ✅ 有資料 |
| **assessment_items** | 評測題目 | - | 📋 待確認 |
| **assessment_responses** | 評測回應 | - | 📋 待確認 |
| **assessment_sessions** | 評測會話 | - | 📋 待確認 |

## 🔍 詳細資料結構

### V4.0 相關資料表

#### 1. v4_sessions
存儲評測會話的基本資訊和區塊配置
```sql
- session_id: 會話識別碼
- blocks_data: JSON 格式的區塊資料
- created_at: 建立時間
```

#### 2. v4_assessment_results
存儲完整的評測結果（目前無資料，需要完成評測才會產生）
```sql
- session_id: 會話識別碼
- responses: JSON 格式的回應資料
- theta_scores: IRT 模型計算的能力值
- norm_scores: 常模分數
- profile: 個人檔案分析
- completed_at: 完成時間
```

## 🛠️ 資料留存機制

### 自動留存點
1. **會話建立時**（GET /api/v4/assessment/blocks）
   - 自動存儲 session_id 和 blocks_data 到 v4_sessions

2. **評測提交時**（POST /api/v4/assessment/submit）
   - 存儲完整回應到 v4_assessment_results
   - 包含原始回應、IRT 分數、常模分數

3. **校準執行時**（POST /api/v4/calibration/run）
   - 存儲校準後的參數到 v4_parameters
   - 用於優化 IRT 模型

## 📈 後續分析用途

### 1. 個人層級分析
- **優勢識別**: 基於 theta_scores 識別前 5 大優勢
- **發展建議**: 基於低分維度提供發展方向
- **成長追蹤**: 多次評測比較進步狀況

### 2. 群體層級分析
- **常模建立**: 累積足夠資料後建立本地常模
- **維度相關性**: 分析不同優勢之間的關聯
- **類型分群**: 識別典型的優勢組合模式

### 3. 模型優化
- **IRT 參數校準**: 使用累積資料優化題目參數
- **區塊設計優化**: 分析哪些配對最有區分度
- **信度效度分析**: 評估測驗品質

## 🔐 資料安全與隱私

### 現有保護措施
1. **本地存儲**: 資料存在本地 SQLite，不外傳
2. **Session 隔離**: 每個用戶有獨立 session_id
3. **無個資欄位**: 不收集姓名、email 等個資

### 建議加強措施
1. 加密敏感資料欄位
2. 定期備份資料庫
3. 實施資料保留政策（如 90 天後自動清理）

## 📝 資料查詢範例

### 查看最近的評測會話
```sql
SELECT session_id, created_at, json_extract(blocks_data, '$.length') as block_count
FROM v4_sessions
ORDER BY created_at DESC
LIMIT 5;
```

### 統計維度分布
```sql
SELECT
  json_extract(value, '$.dimension') as dimension,
  COUNT(*) as count
FROM v4_assessment_results, json_each(responses)
GROUP BY dimension;
```

### 計算平均完成時間
```sql
SELECT
  AVG(json_extract(value, '$.response_time_ms')) as avg_response_time
FROM v4_assessment_results, json_each(responses);
```

## 🚀 後續行動建議

### 立即行動
1. ✅ 資料庫結構已建立完善
2. ✅ 資料自動留存機制運作正常
3. ⚠️ 需要累積實際評測資料

### 短期目標（1-2 週）
1. 累積至少 100 筆完整評測資料
2. 執行第一次 IRT 參數校準
3. 建立基礎分析報表

### 中期目標（1-3 月）
1. 建立本地化常模（需要 500+ 樣本）
2. 開發進階分析功能
3. 實施資料品質監控

## 📊 目前可用於分析的資料

### 可立即分析
- 6 個會話的區塊配置
- 1 筆評分記錄
- 系統運作日誌

### 需要更多資料
- IRT 參數校準（建議 100+ 完整回應）
- 常模建立（建議 500+ 樣本）
- 信效度分析（建議 200+ 樣本）

## 結論

目前系統的資料留存機制已經完善建立，所有評測資料都會自動存儲在本地資料庫中，可供後續分析使用。主要限制是實際評測資料量還不足，需要累積更多用戶完成評測才能進行深入的統計分析和模型優化。

---

*資料庫路徑: `/home/os-sunnie.gd.weng/python_workstation/side-project/strength-system/src/main/python/data/gallup_assessment.db`*