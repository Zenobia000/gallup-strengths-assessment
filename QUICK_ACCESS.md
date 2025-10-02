# 🚀 優勢評測系統 - 快速訪問指南

## 📍 **正確的訪問地址（動態評測系統 - 端口 8005）**

### 🌐 **完整評測流程**
```
主入口頁面: http://localhost:8005/static/index.html
營銷首頁:   http://localhost:8005/static/landing.html
評測準備:   http://localhost:8005/static/assessment-intro.html
動態評測:   http://localhost:8005/static/assessment.html (🔄 30題組動態生成)
專業報告:   http://localhost:8005/static/results.html?session={id} (🧬 DNA視覺化)
深度分析:   http://localhost:8005/static/report-detail.html?session={id}
```

### 🔧 **API 服務端點**
```
API 文檔:    http://localhost:8005/api/docs
系統健康:    http://localhost:8005/api/system/health
動態題組:    http://localhost:8005/api/assessment/blocks (⚡ 即時生成)
評測結果:    http://localhost:8005/api/assessment/results/{session_id}
提交評測:    http://localhost:8005/api/assessment/submit
```

### ✨ **系統特色 (V4.0 完全動態版 - 已清空舊資料)**
- **🎯 智能出題**: 基於120語句庫的輪轉平衡算法，30題組動態生成
- **🧬 DNA視覺化**: SVG雙螺旋結構，節點大小映射真實分數強度
- **📊 差異化計分**: 15-95分數範圍，告別固定20.0，展現真實優勢分布
- **⏱️ 真實計時**: 基於實際評測時間的MM:SS精確顯示
- **💼 職業原型**: 基於主導領域的動態職業建議與發展策略
- **🔬 科學基礎**: Thurstonian IRT + 改進的theta估計算法

### 🛠️ **如果端口被轉發到其他地址**

您的開發環境可能將端口轉發到了 `http://localhost:53274`，這通常發生在：
- VS Code Remote Development
- PyCharm Remote Interpreter
- Docker 容器端口映射
- SSH 隧道或代理設置

**解決方案：**
1. 直接使用原始端口：`http://localhost:8005`
2. 查看開發環境的 Port Forwarding 設置
3. 清除瀏覽器快取（Ctrl+Shift+R）

### ✅ **驗證服務狀態**
```bash
# 檢查服務是否正常運行
curl -s http://localhost:8005/api/system/health

# 測試前端頁面
curl -s -I http://localhost:8005/static/index.html
```

### 🎯 **推薦訪問流程（完全動態版本 - 清空後首次測試）**

**本地開發：**
1. **主入口**: http://localhost:8005/static/index.html
2. **營銷首頁**: http://localhost:8005/static/landing.html
3. **評測準備**: http://localhost:8005/static/assessment-intro.html
4. **動態評測**: http://localhost:8005/static/assessment.html (🔄 智能30題組生成)
5. **差異化報告**: http://localhost:8005/static/results.html?session={新session} (🧬 真實分數DNA)
6. **深度分析**: http://localhost:8005/static/report-detail.html?session={新session}

**遠端開發（替換為您的服務器IP）：**
1. **主入口**: http://10.137.80.58:8005/static/index.html
2. **營銷首頁**: http://10.137.80.58:8005/static/landing.html
3. **評測準備**: http://10.137.80.58:8005/static/assessment-intro.html
4. **動態評測**: http://10.137.80.58:8005/static/assessment.html
5. **差異化報告**: http://10.137.80.58:8005/static/results.html?session={新session}
6. **深度分析**: http://10.137.80.58:8005/static/report-detail.html?session={新session}

### 🎮 **快速測試**
```bash
# 測試動態題組生成
curl -s http://localhost:8005/api/assessment/blocks | head -c 300

# 測試API健康狀態
curl -s http://localhost:8005/api/system/health

# 測試新的動態題組 (舊session已清空)
curl -s http://localhost:8005/api/assessment/blocks | head -c 300
```

### 🔄 **重要更新 (2025-10-02)**
**資料庫已完全清空，準備測試差異化計分：**

✅ **舊資料清理**: 移除所有含固定20.0分數的session資料
✅ **新計分邏輯**: 15-95分數範圍的真實差異化分布
✅ **真實時間**: 基於實際評測完成時間的精確顯示
✅ **McKinsey升級**: 專業版本的才幹卡片與分級視覺化

**⚠️ 注意**: 舊的 session ID 將無法使用，請進行新的評測來體驗改進功能

### 🎯 **新評測測試流程（體驗完全動態功能）**
1. **開始評測**: http://10.137.80.58:8005/static/assessment.html
   - ⚡ 智能題組生成：基於120語句庫的輪轉平衡算法
   - ⏱️ 實時計時：MM:SS精確倒數計時器
   - 🎮 互動體驗：McKinsey風格的評測介面

2. **完成評測** (預計10-15分鐘)
   - 📊 30題組平衡覆蓋T1-T12全維度
   - 🧠 四選二強制選擇，降低社會讚許性偏誤
   - 💾 自動保存進度，支援返回修改

3. **查看專業報告**: http://10.137.80.58:8005/static/results.html?session={新session}
   - 🧬 **DNA雙螺旋視覺化**: 節點大小動態映射真實分數
   - 📈 **差異化分數**: 15-95範圍的真實優勢分布（告別20.0）
   - 🏆 **三層分級**: 主導(綠) / 支援(藍) / 待管理(橙)
   - 💼 **智能職業原型**: 基於才幹模式的動態分析

4. **深入分析**: http://10.137.80.58:8005/static/report-detail.html?session={新session}
   - 📝 個人化詳細報告與發展建議

---

**系統狀態**: ✨ V4.0 完全動態版 | 🧬 DNA視覺化 | 📊 差異化計分 | 🚀 已清空測試就緒