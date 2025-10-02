# 🚀 優勢評測系統 - 快速訪問指南

## 📍 **正確的訪問地址（文件存儲版本 - 端口 8005）**

### 🌐 **前端頁面訪問**
```
主入口頁面: http://localhost:8005/static/index.html
營銷首頁:   http://localhost:8005/static/landing.html
評測準備:   http://localhost:8005/static/assessment-intro.html
開始評測:   http://localhost:8005/static/assessment.html
結果頁面:   http://localhost:8005/static/results.html
詳細報告:   http://localhost:8005/static/report-detail.html
```

### 🔧 **API 端點訪問**
```
API 文檔:    http://localhost:8005/api/docs
系統健康:    http://localhost:8005/api/system/health
評測題組:    http://localhost:8005/api/assessment/blocks
```

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

### 🎯 **推薦訪問流程**
1. **入口頁面**: http://localhost:8005/static/index.html
2. **點擊「核心營銷首頁」** → Landing Page
3. **點擊「開始專業評測」** → Assessment Intro
4. **確認準備事項後開始評測** → Assessment
5. **完成評測查看結果** → Results → Report Detail

---

**技術支援**: 文件存儲版本 V4.0-FileStorage | API 端點: localhost:8005