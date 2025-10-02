# V4.0 分支開發策略

**專案**: Gallup 優勢測驗 v4.0 Thurstonian IRT 升級
**分支**: `feature/v4.0-thurstonian-irt`
**建立日期**: 2025-09-30
**負責人**: Claude Code & Sunny

## 🎯 分支策略目標

1. **隔離開發**: v4.0 開發不影響 v3.0 生產環境
2. **平行維護**: 允許 main 分支的 bug 修復和小改進
3. **安全整合**: 完整測試後才合併回主分支
4. **回滾能力**: 保持隨時可回滾的能力

## 📋 分支結構

```
main (v3.0 生產版本)
  │
  └── feature/v4.0-thurstonian-irt (v4.0 開發分支)
      │
      ├── feature/v4.0-statements (語句池設計)
      ├── feature/v4.0-scoring (IRT 計分引擎)
      └── feature/v4.0-frontend (四選二介面)
```

## 🔄 開發流程

### 1. 功能開發
```bash
# 在 v4.0 分支上開發
git checkout feature/v4.0-thurstonian-irt
# 進行開發...
git add .
git commit -m "feat(v4.0): 功能描述"
git push origin feature/v4.0-thurstonian-irt
```

### 2. 同步主分支更新
```bash
# 定期從 main 分支合併更新
git checkout feature/v4.0-thurstonian-irt
git fetch origin
git merge origin/main --no-ff
# 解決衝突（如果有）
git push origin feature/v4.0-thurstonian-irt
```

### 3. 子功能分支
```bash
# 對於大功能，創建子分支
git checkout feature/v4.0-thurstonian-irt
git checkout -b feature/v4.0-statements
# 開發完成後合併回 v4.0 主分支
git checkout feature/v4.0-thurstonian-irt
git merge feature/v4.0-statements --no-ff
```

## 📊 合併策略

### Phase 1: 開發階段 (現在 - Week 6)
- 所有 v4.0 開發在 `feature/v4.0-thurstonian-irt` 分支
- 不影響 main 分支的 v3.0 功能

### Phase 2: 測試階段 (Week 6-7)
- A/B 測試框架部署
- 平行運行 v3.0 和 v4.0

### Phase 3: 合併準備 (Week 8)
- 代碼審查
- 完整測試套件通過
- 性能基準測試

### Phase 4: 合併到主分支
```bash
# 最終合併（使用 PR）
git checkout main
git merge feature/v4.0-thurstonian-irt --no-ff
git push origin main
```

## ✅ 合併檢查清單

在合併 v4.0 到 main 之前，必須滿足：

- [ ] 所有單元測試通過 (100%)
- [ ] 整合測試通過
- [ ] A/B 測試結果正面
- [ ] 性能測試達標 (<100ms 計分延遲)
- [ ] 向後相容性測試通過
- [ ] 文檔更新完成
- [ ] Code Review 通過
- [ ] 部署計劃準備就緒

## 🚨 回滾計劃

如果 v4.0 出現嚴重問題：

```bash
# 緊急回滾到 v3.0
git checkout main
git revert -m 1 <merge-commit-hash>
git push origin main

# 或使用標籤回滾
git checkout v3.0-stable
git checkout -b hotfix/rollback-v4
git push origin hotfix/rollback-v4
```

## 🏷️ 版本標籤策略

```bash
# v3.0 穩定版標籤
git tag -a v3.0-stable -m "Last stable v3.0 before v4.0 merge"

# v4.0 里程碑標籤
git tag -a v4.0-alpha -m "v4.0 Alpha: Core IRT implementation"
git tag -a v4.0-beta -m "v4.0 Beta: Complete feature set"
git tag -a v4.0-rc1 -m "v4.0 Release Candidate 1"
git tag -a v4.0 -m "v4.0 Production Release"
```

## 📝 提交訊息規範

v4.0 分支的提交訊息應包含版本標識：

```
feat(v4.0): 實作 Thurstonian IRT 計分引擎
fix(v4.0): 修復四選二區塊平衡性問題
docs(v4.0): 更新 IRT 模型技術文檔
test(v4.0): 新增 IRT scorer 單元測試
refactor(v4.0): 優化參數估計算法效能
```

## 🔐 分支保護規則

建議在 GitHub 設置以下保護規則：

### main 分支
- 需要 Pull Request 審查
- 需要狀態檢查通過
- 禁止強制推送
- 需要分支是最新的

### feature/v4.0-thurstonian-irt 分支
- 需要狀態檢查通過
- 建議 Pull Request 審查
- 允許管理員繞過

## 📅 分支生命週期

- **建立**: 2025-09-30
- **預計開發期**: 6 週
- **預計合併**: 2025-11-16 (v4.0 部署後)
- **分支保留**: 合併後保留 30 天供參考

---

**注意事項**：
1. 始終在 v4.0 分支開發，避免直接修改 main
2. 定期同步 main 的修復，避免合併衝突累積
3. 大功能使用子分支，保持 v4.0 分支的穩定性
4. 合併前進行完整的回歸測試