# UAT 測試快速啟動指南

## 🚀 5 分鐘快速開始

### 步驟 1：啟動 API 伺服器

```bash
cd /mnt/d/python_workspace/github/gallup-strengths-assessment

# 啟動伺服器
PYTHONPATH=src/main/python python3 -m uvicorn api.main_files:app --host 0.0.0.0 --port 8005 --reload
```

### 步驟 2：打開測試輔助工具

在**另一個終端**執行：

```bash
# 顯示維度摘要（建議先看這個）
python3 scripts/uat_helper.py SUMMARY

# 或啟動互動模式
python3 scripts/uat_helper.py
```

### 步驟 3：開始測試

1. **瀏覽器訪問**: http://localhost:8005/static/landing.html
2. **選擇測試組**: 決定要測試哪個領域（執行力/戰略思維/影響力/關係建立）
3. **查看測試策略**:
   ```bash
   python3 scripts/uat_helper.py EXECUTING          # 執行力
   python3 scripts/uat_helper.py STRATEGIC_THINKING # 戰略思維
   python3 scripts/uat_helper.py INFLUENCING        # 影響力
   python3 scripts/uat_helper.py RELATIONSHIP_BUILDING # 關係建立
   ```

---

## 📋 測試執行流程

### 對每個測試組（共 4 組）：

1. **準備階段**
   - [ ] 查看測試策略（使用 uat_helper.py）
   - [ ] 記下目標維度代碼（例如：T1, T2, T12）
   - [ ] 準備計時器

2. **執行階段**
   - [ ] 點擊「開始評測」
   - [ ] 對每個題組（共 30 個）：
     - 閱讀 4 個語句
     - 識別哪些屬於目標領域
     - **最符合**：選擇目標領域的語句
     - **最不符合**：選擇其他領域的語句
   - [ ] 提交答案

3. **記錄階段**
   - [ ] 複製 Session ID
   - [ ] 截圖或記錄結果
   - [ ] 填寫 `docs/UAT_TEST_RESULTS.md`

---

## 🎯 測試策略速查表

### 測試組 1：執行力主導 (EXECUTING)
- **目標維度**: T1, T2, T12
- **關鍵詞**: 結構、品質、責任、執行、完成
- **選擇策略**: 優先選有「計畫」「標準」「負責」等關鍵詞的語句

### 測試組 2：戰略思維主導 (STRATEGIC_THINKING)
- **目標維度**: T3, T4, T8
- **關鍵詞**: 創新、分析、學習、未來、思考
- **選擇策略**: 優先選有「想法」「數據」「知識」等關鍵詞的語句

### 測試組 3：影響力主導 (INFLUENCING)
- **目標維度**: T5, T7, T11
- **關鍵詞**: 影響、說服、客戶、溝通、整合
- **選擇策略**: 優先選有「影響力」「服務」「整合」等關鍵詞的語句

### 測試組 4：關係建立主導 (RELATIONSHIP_BUILDING)
- **目標維度**: T6, T9, T10
- **關鍵詞**: 協作、信任、團隊、穩定、關係
- **選擇策略**: 優先選有「合作」「信賴」「冷靜」等關鍵詞的語句

---

## ✅ 驗證檢查清單

測試完成後，對每個測試組檢查：

- [ ] **主導才幹覆蓋率**: Top 4 中至少有 2/3 個來自目標領域
- [ ] **百分位範圍**: 主導才幹在 75-95 之間
- [ ] **鑑別度**: 主導才幹與待管理領域差距 > 40 百分位
- [ ] **一致性**: 同領域的 3 個維度應該都在 Top 6-7 內

---

## 🔧 常用命令

### 查看維度摘要
```bash
python3 scripts/uat_helper.py SUMMARY
```

### 查看特定測試策略
```bash
python3 scripts/uat_helper.py EXECUTING
python3 scripts/uat_helper.py STRATEGIC_THINKING
python3 scripts/uat_helper.py INFLUENCING
python3 scripts/uat_helper.py RELATIONSHIP_BUILDING
```

### 查看完整語句指南
```bash
python3 scripts/uat_helper.py GUIDE
```

### 啟動互動模式
```bash
python3 scripts/uat_helper.py
```

---

## 📊 預期測試結果示例

### 成功案例：執行力主導

```
主導才幹 (Top 4):
1. T12 - 責任當責 - 93.5
2. T1 - 結構化執行 - 89.2
3. T2 - 品質完美主義 - 84.7
4. T6 - 協作和諧 - 78.3

✅ 通過：3/3 個目標維度都在 Top 4
```

### 失敗案例：戰略思維主導

```
主導才幹 (Top 4):
1. T1 - 結構化執行 - 91.2
2. T6 - 協作和諧 - 87.5
3. T3 - 探索創新 - 83.1
4. T12 - 責任當責 - 79.8

❌ 失敗：只有 1/3 個目標維度在 Top 4
→ 可能原因：選擇策略不一致或評分邏輯有問題
```

---

## 📁 測試文檔位置

- **測試計劃**: `docs/UAT_TEST_PLAN.md`
- **結果記錄**: `docs/UAT_TEST_RESULTS.md`
- **本指南**: `docs/UAT_QUICK_START.md`
- **輔助工具**: `scripts/uat_helper.py`

---

## 🆘 故障排除

### 問題 1: 無法訪問測試頁面
```bash
# 檢查伺服器是否運行
curl http://localhost:8005/static/landing.html

# 重啟伺服器
pkill -f uvicorn
PYTHONPATH=src/main/python python3 -m uvicorn api.main_files:app --host 0.0.0.0 --port 8005 --reload
```

### 問題 2: 輔助工具無法執行
```bash
# 確認在專案根目錄
pwd
# 應該顯示: /mnt/d/python_workspace/github/gallup-strengths-assessment

# 檢查檔案權限
chmod +x scripts/uat_helper.py
```

### 問題 3: 測試結果不符預期
1. 檢查是否一致性地遵循測試策略
2. 查看伺服器日誌中的調試輸出
3. 驗證語句是否正確對應到維度
4. 記錄問題並報告

---

## ⏱️ 預估時間

- **單個測試組**: 15-20 分鐘
- **四組測試總計**: 60-80 分鐘
- **結果記錄**: 20-30 分鐘
- **總計**: 約 2 小時

---

**準備好了嗎？開始測試吧！** 🚀

有任何問題，請參考 `docs/UAT_TEST_PLAN.md` 的詳細說明。
