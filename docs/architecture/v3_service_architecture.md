# V3.0 優勢天賦評測系統 - 服務架構規範

---

**文件版本:** v3.0
**最後更新:** 2025-09-30
**狀態:** 生產環境配置

---

## 系統架構概覽

```
┌─────────────────────────────────────────────────────────────┐
│                         用戶瀏覽器                           │
└─────────────────┬───────────────────────┬───────────────────┘
                  │                       │
                  ▼                       ▼
        ┌─────────────────┐     ┌─────────────────┐
        │   前端服務      │     │   API 網關      │
        │   Port: 3000    │     │   Port: 8004    │
        └─────────────────┘     └─────────────────┘
                  │                       │
                  │                       ▼
                  │             ┌─────────────────┐
                  │             │   核心 API      │
                  │             │ (FastAPI)       │
                  └─────────────┤                 │
                                └─────────────────┘
                                         │
                                         ▼
                              ┌──────────────────┐
                              │   數據庫層      │
                              │  (SQLite)       │
                              └──────────────────┘
```

## 端口分配規範

### 生產環境端口

| 服務名稱 | 端口 | 用途 | 狀態 | 訪問地址 |
|:---------|:-----|:-----|:-----|:---------|
| **前端服務** | 3000 | 靜態文件服務器 | ✅ 運行中 | http://localhost:3000 |
| **API 主服務** | 8004 | FastAPI 主要 API 端點 | ✅ 運行中 | http://localhost:8004/api |

### 開發環境預留端口

| 端口範圍 | 用途 |
|:---------|:-----|
| 8001 | 開發測試 API |
| 8002-8003 | 臨時測試服務 |
| 8005-8010 | 微服務擴展預留 |

## 服務啟動腳本

### 1. 清理所有服務

```bash
#!/bin/bash
# cleanup_services.sh

echo "🧹 清理所有運行中的服務..."

# 停止前端服務
pkill -f "python.*3000" 2>/dev/null

# 停止所有 API 服務
for port in 8001 8002 8003 8004 8005; do
    lsof -ti:$port | xargs kill -9 2>/dev/null
done

echo "✅ 清理完成"
```

### 2. 啟動生產環境

```bash
#!/bin/bash
# start_production.sh

echo "🚀 啟動 V3.0 生產環境..."

# 啟動前端服務 (Port 3000)
cd /home/os-sunnie.gd.weng/python_workstation/side-project/strength-system
python3 -m http.server 3000 --directory src/main/resources/static &

# 啟動 API 服務 (Port 8004)
cd src/main/python
PYTHONPATH=. python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8004 --reload &

echo "✅ 服務啟動完成"
echo "📱 前端: http://localhost:3000"
echo "🔌 API: http://localhost:8004/docs"
```

## API 端點規範

### V3.0 核心端點

| 端點 | 方法 | 功能 | 版本 |
|:-----|:-----|:-----|:-----|
| `/api/system/health` | GET | 健康檢查 | 現行 |
| `/api/assessment/questions` | GET | 獲取題目 | 現行 |
| `/api/privacy/consent` | POST | 用戶同意 | 現行 |
| `/api/assessment/start` | POST | 開始測評 | 現行 |
| `/api/assessment/submit` | POST | 提交答案 | 現行 |
| `/api/assessment/scoring/calculate` | POST | 計算分數 | 現行 |
| `/api/reports/generate` | POST | 生成報告 | 現行 |

## 前端路由規範

| 路由 | 頁面 | 功能 | 狀態 |
|:-----|:-----|:-----|:-----|
| `/` | 目錄列表 | 開發導航 | ✅ |
| `/landing.html` | 登陸頁面 | 商業轉換優化版 | ✅ |
| `/v4_assessment.html` | V4 測評 | Thurstonian IRT 測評 | ✅ |
| `/test_submit.html` | 測試頁面 | API 測試工具 | ✅ |
| `/results.html` | 結果展示 | 測評結果展示 | 🚧 開發中 |

## 數據流架構

```
用戶訪問流程:
1. 用戶訪問 http://localhost:3000/landing.html
2. 點擊 "開始測評"
3. 前端調用 POST /api/assessment/start
4. 跳轉到 /v4_assessment.html
5. 用戶完成測評
6. 前端調用 POST /api/assessment/submit
7. 後端處理並返回結果
8. 跳轉到 /results.html 展示結果
```

## 環境變量配置

```bash
# .env 文件配置
DATABASE_URL=sqlite:///./gallup_assessment.db
SECRET_KEY=your-secret-key-here
ALLOWED_ORIGINS=["http://localhost:3000", "http://localhost:8004"]
API_VERSION=v3.0
ENVIRONMENT=production
```

## 監控與日誌

### 服務健康檢查

```bash
# 檢查服務狀態
curl http://localhost:8004/api/system/health
curl http://localhost:3000/landing.html -I
```

### 日誌位置

- API 日誌: `/var/log/strength-system/api.log`
- 前端訪問日誌: `/var/log/strength-system/access.log`
- 錯誤日誌: `/var/log/strength-system/error.log`

## 故障排除

### 常見問題

1. **端口佔用**
   ```bash
   # 查找佔用端口的進程
   lsof -i :3000
   lsof -i :8004
   ```

2. **API 無響應**
   ```bash
   # 重啟 API 服務
   pkill -f "uvicorn.*8004"
   cd src/main/python && python3 -m uvicorn api.main:app --port 8004 --reload
   ```

3. **前端頁面 404**
   ```bash
   # 檢查靜態文件路徑
   ls -la src/main/resources/static/
   ```

## 部署檢查清單

- [ ] 清理所有測試端口
- [ ] 確認數據庫連接
- [ ] 啟動前端服務 (3000)
- [ ] 啟動 API 服務 (8004)
- [ ] 測試健康檢查端點
- [ ] 驗證前端頁面加載
- [ ] 測試完整用戶流程
- [ ] 檢查日誌輸出
- [ ] 設置監控告警

## 安全注意事項

1. 生產環境必須使用 HTTPS
2. 實施 CORS 策略
3. API 速率限制
4. SQL 注入防護
5. XSS 防護
6. CSRF Token 驗證

---

**維護聯繫**: DevOps Team
**更新週期**: 每月檢查
**下次審查**: 2025-10-30