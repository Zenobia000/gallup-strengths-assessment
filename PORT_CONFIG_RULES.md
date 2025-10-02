# 端口配置統一規則

## 🚨 重要：所有端口配置必須統一

### 標準端口配置
- **前端服務器**: `http://localhost:3000`
- **後端API服務器**: `http://localhost:8004`
- **API路徑**: 功能性API結構:
  - `/api/system/health` (系統健康檢查)
  - `/api/privacy/consent` (隱私同意)
  - `/api/assessment/*` (評測相關)
  - `/api/reports/*` (報告相關)
  - `/api/data/collection/*` (數據收集)

### 禁止使用的端口
- ❌ `8002` - 已棄用，改用8004
- ❌ `8000` - 避免衝突
- ❌ `5000` - 避免衝突

### 所有前端文件必須使用的配置
```javascript
// 正確配置
const apiBase = window.location.port === '3000' ? 'http://localhost:8004' : '';
const apiUrl = `${apiBase}/api/assessment/start`;

// 錯誤配置 (禁止使用)
const apiBase = 'http://localhost:8002'; // ❌ 錯誤
```

### 需要檢查和修正的文件
- [ ] `/src/main/resources/static/results.html` ✅ 已修正
- [ ] `/src/main/resources/static/assessment.html`
- [ ] `/src/main/resources/static/report-detail.html`
- [ ] `/src/main/resources/static/v4_pilot_test.html`
- [ ] `/src/main/resources/static/js/config.js` ✅ 已修正

### 啟動命令
```bash
# 後端服務器 (端口 8004)
PYTHONPATH=src/main/python python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8004 --reload

# 前端服務器 (端口 3000)
cd src/main/resources/static && python3 -m http.server 3000
```

### 規則執行
任何時候修改端口配置時，必須：
1. 檢查所有前端文件
2. 統一修改為 8004
3. 測試所有頁面
4. 更新此文檔

**最後更新**: 2025-10-02