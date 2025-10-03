"""
常模分數轉換模組
將 IRT θ 分數轉換為可解釋的常模分數
Task 8.2.4
"""

import numpy as np
from scipy import stats
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class NormativeData:
    """常模資料"""
    dimension: str
    mean: float
    sd: float
    sample_size: int
    percentiles: Dict[int, float]  # 1, 5, 10, 25, 50, 75, 90, 95, 99
    skewness: float
    kurtosis: float
    min_value: float
    max_value: float


@dataclass
class NormScore:
    """常模分數"""
    dimension: str
    raw_theta: float
    percentile: float
    t_score: float
    stanine: int
    sten: int
    z_score: float
    interpretation: str


class NormativeScorer:
    """
    常模分數轉換器

    支援多種常模分數類型：
    - 百分位數
    - T分數 (M=50, SD=10)
    - 九分制 (Stanine, 1-9)
    - 十分制 (Sten, 1-10)
    - Z分數
    """

    def __init__(self, norm_data_path: Optional[Path] = None):
        """
        初始化常模計分器

        Args:
            norm_data_path: 常模資料檔案路徑
        """
        self.norm_data = {}
        if norm_data_path and norm_data_path.exists():
            self.load_norm_data(norm_data_path)
        else:
            self._initialize_default_norms()

    def _initialize_default_norms(self):
        """初始化預設常模（標準常態分佈）- T1-T12 框架"""
        dimensions = [
            'T1', 'T2', 'T3', 'T4', 'T5', 'T6',
            'T7', 'T8', 'T9', 'T10', 'T11', 'T12'
        ]

        for dim in dimensions:
            self.norm_data[dim] = NormativeData(
                dimension=dim,
                mean=0.0,
                sd=1.0,
                sample_size=1000,  # 假設值
                percentiles={
                    1: -2.33, 5: -1.64, 10: -1.28,
                    25: -0.67, 50: 0.0, 75: 0.67,
                    90: 1.28, 95: 1.64, 99: 2.33
                },
                skewness=0.0,
                kurtosis=0.0,
                min_value=-3.0,
                max_value=3.0
            )

    def compute_norm_scores(self,
                           theta_scores: Dict[str, float]) -> Dict[str, NormScore]:
        """
        計算所有維度的常模分數

        Args:
            theta_scores: 各維度的 θ 分數

        Returns:
            各維度的常模分數
        """
        norm_scores = {}

        for dimension, theta in theta_scores.items():
            if dimension in self.norm_data:
                norm_scores[dimension] = self._compute_single_norm(
                    dimension, theta
                )
            else:
                logger.warning(f"維度 {dimension} 沒有常模資料")

        return norm_scores

    def _compute_single_norm(self,
                            dimension: str,
                            theta: float) -> NormScore:
        """計算單一維度的常模分數"""
        norm = self.norm_data[dimension]

        # Z分數
        z_score = (theta - norm.mean) / norm.sd

        # 百分位數（使用常態分佈近似）
        percentile = stats.norm.cdf(z_score) * 100

        # T分數
        t_score = 50 + 10 * z_score
        t_score = np.clip(t_score, 20, 80)  # 限制在合理範圍

        # 九分制 (Stanine)
        stanine = self._compute_stanine(percentile)

        # 十分制 (Sten)
        sten = self._compute_sten(percentile)

        # 解釋
        interpretation = self._get_interpretation(percentile)

        return NormScore(
            dimension=dimension,
            raw_theta=theta,
            percentile=round(percentile, 1),
            t_score=round(t_score, 1),
            stanine=stanine,
            sten=sten,
            z_score=round(z_score, 2),
            interpretation=interpretation
        )

    @staticmethod
    def _compute_stanine(percentile: float) -> int:
        """
        計算九分制分數

        Stanine 分布：
        1: 0-4%     (4%)
        2: 4-11%    (7%)
        3: 11-23%   (12%)
        4: 23-40%   (17%)
        5: 40-60%   (20%)
        6: 60-77%   (17%)
        7: 77-89%   (12%)
        8: 89-96%   (7%)
        9: 96-100%  (4%)
        """
        if percentile < 4:
            return 1
        elif percentile < 11:
            return 2
        elif percentile < 23:
            return 3
        elif percentile < 40:
            return 4
        elif percentile < 60:
            return 5
        elif percentile < 77:
            return 6
        elif percentile < 89:
            return 7
        elif percentile < 96:
            return 8
        else:
            return 9

    @staticmethod
    def _compute_sten(percentile: float) -> int:
        """
        計算十分制分數

        Sten 分布（標準十分）：
        1: 0-2.3%
        2: 2.3-6.7%
        3: 6.7-15.9%
        4: 15.9-30.9%
        5: 30.9-50%
        6: 50-69.1%
        7: 69.1-84.1%
        8: 84.1-93.3%
        9: 93.3-97.7%
        10: 97.7-100%
        """
        if percentile < 2.3:
            return 1
        elif percentile < 6.7:
            return 2
        elif percentile < 15.9:
            return 3
        elif percentile < 30.9:
            return 4
        elif percentile < 50:
            return 5
        elif percentile < 69.1:
            return 6
        elif percentile < 84.1:
            return 7
        elif percentile < 93.3:
            return 8
        elif percentile < 97.7:
            return 9
        else:
            return 10

    @staticmethod
    def _get_interpretation(percentile: float) -> str:
        """獲取分數解釋"""
        if percentile >= 95:
            return "極高（前5%）"
        elif percentile >= 85:
            return "很高（前15%）"
        elif percentile >= 70:
            return "高於平均（前30%）"
        elif percentile >= 30:
            return "平均範圍"
        elif percentile >= 15:
            return "低於平均（後30%）"
        elif percentile >= 5:
            return "很低（後15%）"
        else:
            return "極低（後5%）"

    def calibrate_norms(self,
                        theta_samples: Dict[str, List[float]],
                        save_path: Optional[Path] = None) -> Dict[str, NormativeData]:
        """
        從樣本資料校準常模

        Args:
            theta_samples: 各維度的 θ 分數樣本
            save_path: 儲存路徑

        Returns:
            校準後的常模資料
        """
        calibrated_norms = {}

        for dimension, samples in theta_samples.items():
            if len(samples) < 30:
                logger.warning(f"維度 {dimension} 樣本太少 ({len(samples)})")
                continue

            samples = np.array(samples)

            # 計算統計量
            norm_data = NormativeData(
                dimension=dimension,
                mean=float(np.mean(samples)),
                sd=float(np.std(samples, ddof=1)),
                sample_size=len(samples),
                percentiles={
                    p: float(np.percentile(samples, p))
                    for p in [1, 5, 10, 25, 50, 75, 90, 95, 99]
                },
                skewness=float(stats.skew(samples)),
                kurtosis=float(stats.kurtosis(samples)),
                min_value=float(np.min(samples)),
                max_value=float(np.max(samples))
            )

            calibrated_norms[dimension] = norm_data
            self.norm_data[dimension] = norm_data

        if save_path:
            self.save_norm_data(save_path)

        return calibrated_norms

    def save_norm_data(self, filepath: Path):
        """儲存常模資料"""
        save_data = {}
        for dim, norm in self.norm_data.items():
            save_data[dim] = {
                'mean': norm.mean,
                'sd': norm.sd,
                'sample_size': norm.sample_size,
                'percentiles': norm.percentiles,
                'skewness': norm.skewness,
                'kurtosis': norm.kurtosis,
                'min_value': norm.min_value,
                'max_value': norm.max_value
            }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)

        logger.info(f"常模資料已儲存至 {filepath}")

    def load_norm_data(self, filepath: Path):
        """載入常模資料"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.norm_data = {}
        for dim, norm_dict in data.items():
            self.norm_data[dim] = NormativeData(
                dimension=dim,
                mean=norm_dict['mean'],
                sd=norm_dict['sd'],
                sample_size=norm_dict['sample_size'],
                percentiles=norm_dict['percentiles'],
                skewness=norm_dict['skewness'],
                kurtosis=norm_dict['kurtosis'],
                min_value=norm_dict['min_value'],
                max_value=norm_dict['max_value']
            )

        logger.info(f"已載入 {len(self.norm_data)} 個維度的常模資料")

    def get_strength_profile(self,
                            norm_scores: Dict[str, NormScore],
                            top_n: int = 5) -> Dict:
        """
        生成優勢概況

        Args:
            norm_scores: 各維度的常模分數
            top_n: 返回前幾個優勢

        Returns:
            優勢概況報告
        """
        # 按百分位數排序
        sorted_dims = sorted(
            norm_scores.items(),
            key=lambda x: x[1].percentile,
            reverse=True
        )

        # 前五優勢
        top_strengths = [
            {
                'dimension': dim,
                'percentile': score.percentile,
                'interpretation': score.interpretation,
                't_score': score.t_score
            }
            for dim, score in sorted_dims[:top_n]
        ]

        # 發展領域（後五個）
        development_areas = [
            {
                'dimension': dim,
                'percentile': score.percentile,
                'interpretation': score.interpretation,
                't_score': score.t_score
            }
            for dim, score in sorted_dims[-5:]
        ]

        # 整體統計
        all_percentiles = [score.percentile for _, score in norm_scores.items()]

        # 防護：如果沒有分數，使用預設值
        if not all_percentiles:
            profile_stats = {
                'mean_percentile': 50.0,
                'sd_percentile': 0.0,
                'min_percentile': 50.0,
                'max_percentile': 50.0,
                'range': 0.0
            }
        else:
            profile_stats = {
                'mean_percentile': np.mean(all_percentiles),
                'sd_percentile': np.std(all_percentiles),
                'min_percentile': np.min(all_percentiles),
                'max_percentile': np.max(all_percentiles),
                'range': np.max(all_percentiles) - np.min(all_percentiles)
            }

        # 優勢類別分布
        category_distribution = self._analyze_categories(norm_scores)

        return {
            'top_strengths': top_strengths,
            'development_areas': development_areas,
            'profile_statistics': profile_stats,
            'category_distribution': category_distribution,
            'profile_type': self._determine_profile_type(profile_stats)
        }

    def _analyze_categories(self,
                          norm_scores: Dict[str, NormScore]) -> Dict[str, Dict]:
        """分析優勢類別分布 - T1-T12 框架"""
        categories = {
            'execution': ['T1', 'T2', 'T9', 'T12'],  # 執行力類別：結構化執行、品質與完備、紀律與信任、責任與當責
            'influencing': ['T5', 'T7'],             # 影響力類別：影響與倡議、客戶導向
            'relationship': ['T6', 'T10', 'T11'],    # 關係類別：協作與共好、壓力調節、衝突整合
            'thinking': ['T3', 'T4', 'T8']           # 思考類別：探索與創新、分析與洞察、學習與成長
        }

        category_stats = {}
        for cat_name, dimensions in categories.items():
            cat_scores = [
                norm_scores[dim].percentile
                for dim in dimensions
                if dim in norm_scores
            ]

            if cat_scores:
                category_stats[cat_name] = {
                    'mean_percentile': np.mean(cat_scores),
                    'max_percentile': np.max(cat_scores) if cat_scores else 0.0,
                    'count_top5': sum(1 for s in cat_scores if s >= 85)
                }

        return category_stats

    @staticmethod
    def _determine_profile_type(profile_stats: Dict) -> str:
        """判斷概況類型"""
        range_val = profile_stats['range']

        if range_val < 30:
            return "均衡型"
        elif range_val < 50:
            return "中度分化型"
        elif range_val < 70:
            return "高度分化型"
        else:
            return "極端分化型"


def create_sample_norms():
    """創建範例常模資料 - T1-T12 框架"""
    np.random.seed(42)

    # 模擬12個T維度的樣本資料
    dimensions = [
        'T1', 'T2', 'T3', 'T4', 'T5', 'T6',
        'T7', 'T8', 'T9', 'T10', 'T11', 'T12'
    ]

    theta_samples = {}
    for dim in dimensions:
        # 生成略有偏態的分佈
        samples = np.random.normal(0, 1, 1000)
        if dim in ['T1', 'T5']:  # 結構化執行、影響與倡議
            samples += 0.2  # 輕微正偏
        elif dim in ['T12', 'T9']:  # 責任與當責、紀律與信任
            samples -= 0.1  # 輕微負偏

        theta_samples[dim] = samples.tolist()

    # 校準常模
    scorer = NormativeScorer()
    norm_data = scorer.calibrate_norms(
        theta_samples,
        Path('data/v4_normative_data.json')
    )

    return norm_data