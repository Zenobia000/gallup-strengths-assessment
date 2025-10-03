"""
IRT 參數校準與估計模組
實作 Thurstonian IRT 模型的參數估計演算法
Task 8.2.1-8.2.3
"""

import numpy as np
from scipy import optimize, stats, special
from typing import List, Dict, Tuple, Optional, Any
import json
import logging
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import warnings

from models.v4.forced_choice import (
    ForcedChoiceBlockResponse,
    QuartetBlock,
    IRTParameters
)

logger = logging.getLogger(__name__)


@dataclass
class CalibrationResult:
    """校準結果"""
    item_parameters: Dict[str, Dict]  # 題目參數
    dimension_parameters: Dict[str, Dict]  # 維度參數
    model_fit: Dict[str, float]  # 模型擬合指標
    sample_size: int
    convergence: bool
    iterations: int
    calibration_date: datetime


@dataclass
class PersonParameter:
    """個人潛在特質參數"""
    theta: np.ndarray  # 12維度的潛在特質值
    se: np.ndarray  # 標準誤
    response_pattern: List[Dict]  # 回應模式
    fit_statistics: Dict[str, float]  # 擬合統計


class ThurstonianIRTCalibrator:
    """
    Thurstonian IRT 模型校準器

    實作參數估計的核心演算法：
    1. 邊際最大似然估計 (MMLE)
    2. 期望最大化算法 (EM)
    3. 馬可夫鏈蒙特卡洛 (MCMC) - 選用
    """

    def __init__(self,
                 n_dimensions: int = 12,
                 estimation_method: str = 'MMLE'):
        """
        初始化校準器

        Args:
            n_dimensions: 維度數量
            estimation_method: 估計方法 ('MMLE', 'EM', 'MCMC')
        """
        self.n_dimensions = n_dimensions
        self.estimation_method = estimation_method
        self.item_parameters = {}
        self.person_parameters = []

    def calibrate(self,
                  responses: List[ForcedChoiceBlockResponse],
                  blocks: List[QuartetBlock],
                  max_iter: int = 100,
                  tol: float = 1e-5) -> CalibrationResult:
        """
        校準 IRT 模型參數

        Args:
            responses: 受試者回應資料
            blocks: 題目區塊
            max_iter: 最大迭代次數
            tol: 收斂閾值

        Returns:
            CalibrationResult 校準結果
        """
        logger.info(f"開始 IRT 參數校準 (方法: {self.estimation_method})")
        logger.info(f"樣本數: {len(responses)}, 區塊數: {len(blocks)}")

        if self.estimation_method == 'MMLE':
            result = self._mmle_calibration(responses, blocks, max_iter, tol)
        elif self.estimation_method == 'EM':
            result = self._em_calibration(responses, blocks, max_iter, tol)
        else:
            raise ValueError(f"不支援的估計方法: {self.estimation_method}")

        return result

    def _mmle_calibration(self,
                         responses: List[ForcedChoiceBlockResponse],
                         blocks: List[QuartetBlock],
                         max_iter: int,
                         tol: float) -> CalibrationResult:
        """
        邊際最大似然估計 (Marginal Maximum Likelihood Estimation)
        """
        n_items = len(blocks) * 4
        n_persons = len(responses)

        # 初始化參數
        item_params = self._initialize_item_parameters(blocks)
        person_thetas = self._initialize_person_parameters(n_persons)

        # EM 算法主循環
        converged = False
        iteration = 0
        prev_ll = -np.inf

        while not converged and iteration < max_iter:
            iteration += 1

            # E-step: 估計潛在變數的期望值
            expected_thetas, expected_cov = self._e_step(
                responses, blocks, item_params, person_thetas
            )

            # M-step: 最大化參數
            item_params = self._m_step_items(
                responses, blocks, expected_thetas, item_params
            )
            person_thetas = expected_thetas

            # 計算對數似然
            current_ll = self._compute_log_likelihood(
                responses, blocks, item_params, person_thetas
            )

            # 檢查收斂
            if abs(current_ll - prev_ll) < tol:
                converged = True
                logger.info(f"MMLE 在第 {iteration} 次迭代收斂")

            prev_ll = current_ll

            if iteration % 10 == 0:
                logger.debug(f"迭代 {iteration}: LL = {current_ll:.4f}")

        # 計算模型擬合指標
        model_fit = self._compute_model_fit(
            responses, blocks, item_params, person_thetas
        )

        # 整理參數
        dimension_params = self._extract_dimension_parameters(
            item_params, blocks
        )

        return CalibrationResult(
            item_parameters=item_params,
            dimension_parameters=dimension_params,
            model_fit=model_fit,
            sample_size=n_persons,
            convergence=converged,
            iterations=iteration,
            calibration_date=datetime.now()
        )

    def _em_calibration(self,
                       responses: List[ForcedChoiceBlockResponse],
                       blocks: List[QuartetBlock],
                       max_iter: int,
                       tol: float) -> CalibrationResult:
        """
        期望最大化算法 (Expectation-Maximization)

        更精確但計算成本較高的方法
        """
        # 簡化版本，實際上與 MMLE 類似但有細節差異
        return self._mmle_calibration(responses, blocks, max_iter, tol)

    def _initialize_item_parameters(self, blocks: List[QuartetBlock]) -> Dict:
        """初始化題目參數"""
        params = {}

        for block in blocks:
            for stmt in block.statements:
                if stmt.statement_id not in params:
                    params[stmt.statement_id] = {
                        'discrimination': np.random.uniform(0.5, 1.5),  # a 參數
                        'difficulty': np.random.normal(0, 1),  # b 參數
                        'guessing': 0,  # c 參數 (強制選擇中通常為0)
                        'dimension': stmt.dimension,
                        'factor_loading': stmt.factor_loading
                    }

        return params

    def _initialize_person_parameters(self, n_persons: int) -> np.ndarray:
        """初始化個人參數"""
        # 使用標準常態分佈作為初始值
        return np.random.randn(n_persons, self.n_dimensions) * 0.5

    def _e_step(self,
                responses: List[ForcedChoiceBlockResponse],
                blocks: List[QuartetBlock],
                item_params: Dict,
                person_thetas: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        E-step: 計算潛在變數的條件期望
        """
        n_persons = len(responses)
        expected_thetas = np.zeros((n_persons, self.n_dimensions))
        expected_cov = np.zeros((n_persons, self.n_dimensions, self.n_dimensions))

        for i, response in enumerate(responses):
            # 使用數值積分或近似方法計算後驗分佈
            posterior_mean, posterior_cov = self._compute_posterior(
                response, blocks, item_params, person_thetas[i]
            )
            expected_thetas[i] = posterior_mean
            expected_cov[i] = posterior_cov

        return expected_thetas, expected_cov

    def _m_step_items(self,
                      responses: List[ForcedChoiceBlockResponse],
                      blocks: List[QuartetBlock],
                      expected_thetas: np.ndarray,
                      current_params: Dict) -> Dict:
        """
        M-step: 最大化題目參數
        """
        updated_params = {}

        # 對每個題目估計參數
        for stmt_id, params in current_params.items():
            # 使用牛頓-拉夫遜或其他優化方法
            def objective(x):
                params_copy = params.copy()
                params_copy['discrimination'] = x[0]
                params_copy['difficulty'] = x[1]
                return -self._item_log_likelihood(
                    stmt_id, params_copy, responses, blocks, expected_thetas
                )

            x0 = [params['discrimination'], params['difficulty']]
            bounds = [(0.1, 3.0), (-3.0, 3.0)]

            result = optimize.minimize(
                objective, x0,
                method='L-BFGS-B',
                bounds=bounds
            )

            if result.success:
                updated_params[stmt_id] = params.copy()
                updated_params[stmt_id]['discrimination'] = result.x[0]
                updated_params[stmt_id]['difficulty'] = result.x[1]
            else:
                updated_params[stmt_id] = params

        return updated_params

    def _compute_posterior(self,
                          response: ForcedChoiceBlockResponse,
                          blocks: List[QuartetBlock],
                          item_params: Dict,
                          prior_theta: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        計算個人參數的後驗分佈

        使用拉普拉斯近似或變分推斷
        """
        # 簡化版：使用 MAP 估計
        def neg_log_posterior(theta):
            # 先驗：標準常態
            prior_ll = -0.5 * np.sum(theta ** 2)

            # 似然
            likelihood_ll = 0
            for resp in response.responses:
                block = next(b for b in blocks if b.block_id == resp.block_id)
                prob = self._compute_response_probability(
                    theta, resp, block, item_params
                )
                likelihood_ll += np.log(prob + 1e-10)

            return -(prior_ll + likelihood_ll)

        # 優化找到 MAP 估計
        result = optimize.minimize(
            neg_log_posterior,
            prior_theta,
            method='L-BFGS-B'
        )

        posterior_mean = result.x

        # 使用 Hessian 近似協方差
        eps = 1e-5
        hessian = np.zeros((self.n_dimensions, self.n_dimensions))
        for i in range(self.n_dimensions):
            for j in range(self.n_dimensions):
                theta_pp = posterior_mean.copy()
                theta_pp[i] += eps
                theta_pp[j] += eps

                theta_pm = posterior_mean.copy()
                theta_pm[i] += eps
                theta_pm[j] -= eps

                theta_mp = posterior_mean.copy()
                theta_mp[i] -= eps
                theta_mp[j] += eps

                theta_mm = posterior_mean.copy()
                theta_mm[i] -= eps
                theta_mm[j] -= eps

                hessian[i, j] = (
                    neg_log_posterior(theta_pp) -
                    neg_log_posterior(theta_pm) -
                    neg_log_posterior(theta_mp) +
                    neg_log_posterior(theta_mm)
                ) / (4 * eps * eps)

        # 協方差是 Hessian 的逆
        try:
            posterior_cov = np.linalg.inv(hessian)
        except np.linalg.LinAlgError:
            posterior_cov = np.eye(self.n_dimensions) * 0.5

        return posterior_mean, posterior_cov

    def _compute_response_probability(self,
                                     theta: np.ndarray,
                                     response: Any,
                                     block: QuartetBlock,
                                     item_params: Dict) -> float:
        """
        計算給定參數下的回應概率
        """
        # 計算每個選項的效用
        utilities = np.zeros(4)

        for i, stmt in enumerate(block.statements):
            params = item_params.get(stmt.statement_id, {})
            dim_idx = self._get_dimension_index(stmt.dimension)

            # IRT 模型: P = 1 / (1 + exp(-a*(theta - b)))
            # 但在 Thurstonian 模型中，我們使用效用差異
            utilities[i] = (
                params.get('discrimination', 1.0) *
                (theta[dim_idx] - params.get('difficulty', 0))
            )

        # 計算選擇概率 (Bradley-Terry-Luce 模型)
        exp_utils = np.exp(utilities - np.max(utilities))

        # 最喜歡的概率
        p_most = exp_utils[response.most_like_index] / np.sum(exp_utils)

        # 最不喜歡的概率 (從剩餘選項中)
        remaining = exp_utils.copy()
        remaining[response.most_like_index] = 0

        if np.sum(remaining) > 0:
            p_least = (1 / exp_utils[response.least_like_index]) / np.sum(1 / remaining[remaining > 0])
        else:
            p_least = 1/3

        return p_most * p_least

    def _item_log_likelihood(self,
                            stmt_id: str,
                            params: Dict,
                            responses: List[ForcedChoiceBlockResponse],
                            blocks: List[QuartetBlock],
                            thetas: np.ndarray) -> float:
        """計算單個題目的對數似然"""
        ll = 0

        for i, response in enumerate(responses):
            for resp in response.responses:
                block = next(b for b in blocks if b.block_id == resp.block_id)

                # 檢查此題目是否在這個區塊中
                stmt_indices = [
                    j for j, s in enumerate(block.statements)
                    if s.statement_id == stmt_id
                ]

                if stmt_indices:
                    prob = self._compute_response_probability(
                        thetas[i], resp, block, {stmt_id: params}
                    )
                    ll += np.log(prob + 1e-10)

        return ll

    def _compute_log_likelihood(self,
                               responses: List[ForcedChoiceBlockResponse],
                               blocks: List[QuartetBlock],
                               item_params: Dict,
                               person_thetas: np.ndarray) -> float:
        """計算完整模型的對數似然"""
        total_ll = 0

        for i, response in enumerate(responses):
            for resp in response.responses:
                block = next(b for b in blocks if b.block_id == resp.block_id)
                prob = self._compute_response_probability(
                    person_thetas[i], resp, block, item_params
                )
                total_ll += np.log(prob + 1e-10)

        return total_ll

    def _compute_model_fit(self,
                          responses: List[ForcedChoiceBlockResponse],
                          blocks: List[QuartetBlock],
                          item_params: Dict,
                          person_thetas: np.ndarray) -> Dict[str, float]:
        """
        計算模型擬合指標
        """
        n_persons = len(responses)
        n_items = len(item_params)
        n_params = n_items * 2 + n_persons * self.n_dimensions  # 簡化計算

        # 對數似然
        log_likelihood = self._compute_log_likelihood(
            responses, blocks, item_params, person_thetas
        )

        # AIC (Akaike Information Criterion)
        aic = 2 * n_params - 2 * log_likelihood

        # BIC (Bayesian Information Criterion)
        bic = n_params * np.log(n_persons) - 2 * log_likelihood

        # RMSEA (Root Mean Square Error of Approximation) - 簡化版
        chi_square = -2 * log_likelihood
        df = n_persons * len(blocks) * 6 - n_params  # 6 = C(4,2) 可能的選擇組合

        if df > 0:
            rmsea = np.sqrt(max(0, (chi_square - df) / (df * n_persons)))
        else:
            rmsea = 0

        # CFI (Comparative Fit Index) - 簡化版
        # 需要基準模型，這裡使用隨機猜測模型
        null_ll = n_persons * len(blocks) * np.log(1/6)  # 隨機選擇的概率
        null_chi_square = -2 * null_ll

        if null_chi_square > chi_square:
            cfi = (null_chi_square - chi_square) / null_chi_square
        else:
            cfi = 0

        return {
            'log_likelihood': log_likelihood,
            'aic': aic,
            'bic': bic,
            'rmsea': rmsea,
            'cfi': cfi,
            'n_parameters': n_params
        }

    def _extract_dimension_parameters(self,
                                     item_params: Dict,
                                     blocks: List[QuartetBlock]) -> Dict[str, Dict]:
        """
        從題目參數中提取維度層級的參數
        """
        dimension_params = {}

        # 收集每個維度的題目參數
        for block in blocks:
            for stmt in block.statements:
                dim = stmt.dimension
                if dim not in dimension_params:
                    dimension_params[dim] = {
                        'items': [],
                        'mean_discrimination': 0,
                        'mean_difficulty': 0,
                        'reliability': 0
                    }

                if stmt.statement_id in item_params:
                    dimension_params[dim]['items'].append(
                        item_params[stmt.statement_id]
                    )

        # 計算維度層級統計
        for dim, data in dimension_params.items():
            if data['items']:
                data['mean_discrimination'] = np.mean([
                    item['discrimination'] for item in data['items']
                ])
                data['mean_difficulty'] = np.mean([
                    item['difficulty'] for item in data['items']
                ])

                # 計算內部一致性信度 (簡化版)
                # 使用 discrimination 參數作為因子載荷的近似
                loadings = [item['discrimination'] for item in data['items']]
                if len(loadings) > 1:
                    # Cronbach's alpha 近似
                    k = len(loadings)
                    var_sum = sum(l**2 for l in loadings)
                    total_var = var_sum + k  # 假設誤差變異數為1
                    data['reliability'] = k / (k - 1) * (1 - k / total_var)
                else:
                    data['reliability'] = 0.7  # 預設值

        return dimension_params

    def _get_dimension_index(self, dimension: str) -> int:
        """獲取維度的索引"""
        dimensions = [
            'Achiever', 'Activator', 'Adaptability',
            'Analytical', 'Arranger', 'Belief',
            'Command', 'Communication', 'Competition',
            'Connectedness', 'Consistency', 'Context'
        ]
        return dimensions.index(dimension)

    def save_parameters(self,
                       result: CalibrationResult,
                       filepath: Path):
        """
        儲存校準參數
        """
        save_data = {
            'item_parameters': result.item_parameters,
            'dimension_parameters': result.dimension_parameters,
            'model_fit': result.model_fit,
            'sample_size': result.sample_size,
            'calibration_date': result.calibration_date.isoformat(),
            'convergence': result.convergence,
            'iterations': result.iterations,
            'model_version': '4.0-calibrated'
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        logger.info(f"參數已儲存至 {filepath}")

    def load_parameters(self, filepath: Path) -> CalibrationResult:
        """
        載入校準參數
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return CalibrationResult(
            item_parameters=data['item_parameters'],
            dimension_parameters=data['dimension_parameters'],
            model_fit=data['model_fit'],
            sample_size=data['sample_size'],
            convergence=data['convergence'],
            iterations=data['iterations'],
            calibration_date=datetime.fromisoformat(data['calibration_date'])
        )