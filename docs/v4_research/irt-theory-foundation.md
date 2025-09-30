# Thurstonian IRT 理論基礎與實作指南

**文件版本**: 1.0
**日期**: 2025-09-30
**作者**: Claude Code (Task 8.1.1)
**狀態**: 研究完成

## 1. Thurstonian IRT 模型核心原理

### 1.1 理論基礎

Thurstonian IRT 模型結合了 Thurstone 的比較判斷法則與項目反應理論（IRT），專門用於分析強制選擇（forced-choice）數據。

#### 數學模型

對於四選二（quartet）區塊，模型假設每個語句 i 具有潛在效用：

```
U_i = λ_i * θ + ε_i
```

其中：
- `U_i`: 語句 i 的感知效用
- `λ_i`: 語句 i 在特定維度上的因子載荷（item factor loading）
- `θ`: 個體在該維度上的潛在特質水平
- `ε_i`: 隨機誤差項，通常假設服從標準常態分布

### 1.2 強制選擇概率模型

當使用者從四個語句中選擇「最像我」和「最不像我」時，選擇概率遵循：

```
P(選擇 A 為最像，C 為最不像) = P(U_A > U_B, U_A > U_D, U_C < U_B, U_C < U_D)
```

這可以透過多變量常態分布的累積分布函數計算。

### 1.3 參數估計方法

#### 最大似然估計（MLE）
```python
def log_likelihood(theta, responses, item_params):
    """
    計算給定 θ 值下的對數似然

    Args:
        theta: 12維潛在特質向量
        responses: 使用者回應資料
        item_params: 預校準的項目參數
    """
    ll = 0
    for block_response in responses:
        # 計算每個選擇的概率
        prob = compute_choice_probability(theta, block_response, item_params)
        ll += np.log(prob)
    return ll
```

#### 期望後驗估計（EAP）
```python
def eap_estimate(responses, item_params, prior_mean=0, prior_sd=1):
    """
    使用貝葉斯期望後驗估計 θ

    採用數值積分或 MCMC 方法
    """
    # 使用正態先驗
    posterior = lambda theta: (
        likelihood(theta, responses, item_params) *
        normal_prior(theta, prior_mean, prior_sd)
    )
    # 數值積分求期望值
    return integrate_posterior(posterior)
```

## 2. 解決 Ipsative 數據問題

### 2.1 問題本質

傳統強制選擇產生的 ipsative 數據有以下限制：
- 分數總和固定（如30題二選一，總和恆為30）
- 只能進行個體內比較
- 無法進行跨個體的有意義比較

### 2.2 Thurstonian IRT 解決方案

透過建模潛在連續特質，Thurstonian IRT 能夠：
1. **恢復絕對尺度**：估計的 θ 值是連續的，不受總和限制
2. **保留個體差異**：不同個體可以在所有維度上都高或都低
3. **提供標準誤**：每個估計都有相應的測量精度

## 3. 四選二區塊設計要求

### 3.1 平衡性準則

理想的區塊設計應滿足：

```python
class BlockDesignCriteria:
    """四選二區塊設計準則"""

    def __init__(self, n_traits=12, n_blocks=30):
        self.n_traits = n_traits
        self.n_blocks = n_blocks
        self.blocks_per_trait = (n_blocks * 4) // n_traits  # 每個特質出現次數

    def check_balance(self, block_design):
        """檢查設計平衡性"""
        trait_counts = defaultdict(int)
        pair_counts = defaultdict(int)

        for block in block_design:
            for trait in block:
                trait_counts[trait] += 1
            for pair in combinations(block, 2):
                pair_counts[tuple(sorted(pair))] += 1

        # 檢查每個特質出現次數是否均衡
        trait_variance = np.var(list(trait_counts.values()))

        # 檢查配對頻率是否均衡
        pair_variance = np.var(list(pair_counts.values()))

        return {
            'trait_balance': trait_variance < 0.5,
            'pair_balance': pair_variance < 1.0
        }
```

### 3.2 社會期望性匹配

每個區塊內的四個語句應該在社會期望性上相近：

```python
def match_social_desirability(statements, desirability_ratings):
    """匹配語句的社會期望性"""
    blocks = []

    # 按社會期望性分組
    sorted_statements = sorted(statements,
                              key=lambda x: desirability_ratings[x])

    # 從相近期望性的語句中選擇
    for i in range(0, len(sorted_statements), 4):
        block = sorted_statements[i:i+4]
        if len(block) == 4:
            blocks.append(block)

    return blocks
```

## 4. Python IRT 套件評估

### 4.1 可用套件比較

| 套件 | 優點 | 缺點 | 適用性 |
|------|------|------|--------|
| **py-irt** | 純Python實作，易於整合 | 功能有限，不支援Thurstonian | 低 |
| **pymc3** | 強大的貝葉斯推斷 | 學習曲線陡峭 | 中 |
| **scipy.optimize** | 穩定可靠 | 需要自行實作IRT邏輯 | 高 |
| **自定義實作** | 完全控制，最佳整合 | 開發時間長 | 高 |

### 4.2 建議方案：混合實作

```python
import numpy as np
from scipy import optimize, stats
from typing import List, Dict, Tuple

class ThurstonianIRT:
    """Thurstonian IRT 模型實作"""

    def __init__(self, n_traits: int = 12):
        self.n_traits = n_traits
        self.item_params = None
        self.norm_params = None

    def load_parameters(self, item_param_file: str, norm_param_file: str):
        """載入預校準參數"""
        import json
        with open(item_param_file, 'r') as f:
            self.item_params = json.load(f)
        with open(norm_param_file, 'r') as f:
            self.norm_params = json.load(f)

    def estimate_theta(self, responses: List[Dict]) -> np.ndarray:
        """估計潛在特質 θ"""

        # 初始值（使用簡單計數）
        initial_theta = self._get_initial_estimate(responses)

        # MLE 估計
        result = optimize.minimize(
            lambda theta: -self._log_likelihood(theta, responses),
            initial_theta,
            method='L-BFGS-B',
            options={'maxiter': 100}
        )

        return result.x

    def _log_likelihood(self, theta: np.ndarray, responses: List[Dict]) -> float:
        """計算對數似然函數"""
        ll = 0
        for response in responses:
            # 計算四個選項的效用
            utilities = self._compute_utilities(theta, response['block_id'])

            # 計算選擇概率
            prob = self._choice_probability(
                utilities,
                response['most_like'],
                response['least_like']
            )

            ll += np.log(prob + 1e-10)  # 避免 log(0)

        return ll

    def _choice_probability(self, utilities: np.ndarray,
                           most_idx: int, least_idx: int) -> float:
        """計算特定選擇的概率"""

        # 使用 Bradley-Terry-Luce 模型的擴展
        exp_utils = np.exp(utilities)

        # P(most) * P(least|most)
        p_most = exp_utils[most_idx] / np.sum(exp_utils)

        remaining = exp_utils.copy()
        remaining[most_idx] = 0
        p_least_given_most = (1 / exp_utils[least_idx]) / np.sum(1 / remaining[remaining > 0])

        return p_most * p_least_given_most
```

## 5. 常模分數轉換

### 5.1 標準化程序

```python
class NormativeScoring:
    """常模分數轉換"""

    def __init__(self, norm_data: Dict):
        self.means = np.array(norm_data['means'])
        self.sds = np.array(norm_data['sds'])
        self.n_sample = norm_data['sample_size']

    def to_percentile(self, theta: np.ndarray) -> np.ndarray:
        """將 θ 轉換為百分位數"""
        z_scores = (theta - self.means) / self.sds
        percentiles = stats.norm.cdf(z_scores) * 100
        return percentiles

    def to_t_score(self, theta: np.ndarray) -> np.ndarray:
        """轉換為 T 分數（平均50，標準差10）"""
        z_scores = (theta - self.means) / self.sds
        t_scores = 50 + 10 * z_scores
        return t_scores
```

## 6. 實作挑戰與解決方案

### 6.1 計算複雜度

**挑戰**：每次評估需要計算多維積分
**解決方案**：
- 使用近似方法（如 Gauss-Hermite 積分）
- 實作高效的矩陣運算
- 考慮使用 GPU 加速（如需要）

### 6.2 參數識別性

**挑戰**：模型參數可能無法唯一識別
**解決方案**：
- 固定某些參數（如第一個維度的平均值為0）
- 使用適當的先驗分布
- 進行參數約束

### 6.3 小樣本校準

**挑戰**：理想校準需要大樣本（n>500）
**解決方案**：
```python
class AdaptiveCalibration:
    """漸進式校準策略"""

    def __init__(self, min_sample=100):
        self.min_sample = min_sample
        self.calibration_data = []

    def add_response(self, response):
        """累積回應數據"""
        self.calibration_data.append(response)

        if len(self.calibration_data) >= self.min_sample:
            if len(self.calibration_data) % 50 == 0:  # 每50個樣本重新校準
                self.recalibrate()

    def recalibrate(self):
        """重新校準參數"""
        # 使用 EM 算法更新參數
        pass
```

## 7. 效能優化策略

### 7.1 快取機制

```python
from functools import lru_cache

class OptimizedIRT:

    @lru_cache(maxsize=1000)
    def _compute_block_matrix(self, block_id: int) -> np.ndarray:
        """快取區塊的參數矩陣"""
        return self._build_matrix(self.item_params[block_id])

    @lru_cache(maxsize=10000)
    def _mvn_cdf(self, *args) -> float:
        """快取多變量常態分布計算"""
        return stats.multivariate_normal.cdf(args)
```

### 7.2 向量化運算

```python
def batch_estimate(self, all_responses: List[List[Dict]]) -> np.ndarray:
    """批次估計多個使用者"""

    # 向量化運算
    n_users = len(all_responses)
    theta_matrix = np.zeros((n_users, self.n_traits))

    # 平行處理
    from multiprocessing import Pool

    with Pool() as pool:
        theta_matrix = pool.map(self.estimate_theta, all_responses)

    return np.array(theta_matrix)
```

## 8. 驗證與測試

### 8.1 模擬研究

```python
def simulation_study():
    """透過模擬資料驗證模型"""

    # 生成真實 θ 值
    true_theta = np.random.randn(12)

    # 模擬回應
    simulated_responses = simulate_responses(true_theta, item_params)

    # 估計 θ
    estimated_theta = irt_model.estimate_theta(simulated_responses)

    # 計算恢復準確度
    correlation = np.corrcoef(true_theta, estimated_theta)[0, 1]
    rmse = np.sqrt(np.mean((true_theta - estimated_theta)**2))

    return {
        'correlation': correlation,
        'rmse': rmse,
        'bias': np.mean(estimated_theta - true_theta)
    }
```

## 9. 實作路線圖

### Phase 1: 基礎架構（當前）
1. ✅ 理論研究完成
2. ⏳ 資料結構定義
3. ⏳ 核心算法實作

### Phase 2: 參數校準
1. 設計校準研究
2. 收集校準數據
3. 估計項目參數

### Phase 3: 生產部署
1. 效能優化
2. API 整合
3. A/B 測試

## 10. 參考文獻

1. Brown, A., & Maydeu-Olivares, A. (2011). Item response modeling of forced-choice questionnaires. *Educational and Psychological Measurement*, 71(3), 460-502.

2. Brown, A. (2016). Item response models for forced-choice questionnaires: A common framework. *Psychometrika*, 81(4), 1159-1189.

3. Thurstone, L. L. (1927). A law of comparative judgment. *Psychological Review*, 34(4), 273-286.

---

**研究結論**：Thurstonian IRT 模型為解決強制選擇測驗的 ipsative 問題提供了科學嚴謹的方案。建議採用自定義實作結合 scipy 優化的混合方案，以確保最佳的系統整合和效能表現。