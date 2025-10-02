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

### ✨ **系統特色 (V4.0 完整動態版)**
- **🎯 動態出題**: 基於120語句庫的平衡區塊設計
- **🧬 DNA視覺化**: SVG雙螺旋結構展示優勢分布
- **📊 三層分級**: 主導(>75%) / 支援(25-75%) / 待管理(<25%)
- **💼 職業原型**: 基於主導領域的動態職業建議
- **🔬 科學基礎**: Thurstonian IRT + 常模百分位系統

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

### 🎯 **推薦訪問流程（完整動態體驗）**
1. **主入口**: http://localhost:8005/static/index.html
2. **營銷首頁**: http://localhost:8005/static/landing.html
3. **評測準備**: http://localhost:8005/static/assessment-intro.html
4. **動態評測**: http://localhost:8005/static/assessment.html (🔄 即時生成30題組)
5. **專業報告**: http://localhost:8005/static/results.html (🧬 DNA視覺化 + 職業原型)
6. **深度分析**: http://localhost:8005/static/report-detail.html (📊 個人化詳細報告)

### 🎮 **快速測試**
```bash
# 測試動態題組生成
curl -s http://localhost:8005/api/assessment/blocks | head -c 300

# 測試API健康狀態
curl -s http://localhost:8005/api/system/health

# 測試評測結果 (使用現有session)
curl -s http://localhost:8005/api/assessment/results/v4_51891bd0dfab | head -c 300
```

---

**系統狀態**: 動態評測系統 V4.0 | 🧬 DNA視覺化 | 📊 McKinsey專業報告 | API 端點: localhost:8005