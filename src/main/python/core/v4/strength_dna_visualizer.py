"""
Strength DNA 雙軌色帶視覺化模組
創建精美的 T1-T12 才幹強度排序視覺效果
"""

import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
import json
import time


@dataclass
class StrengthDNA:
    """才幹 DNA 數據結構"""
    dimension: str
    name: str
    strength_score: float
    percentile: float
    rank: int
    color_primary: str
    color_secondary: str
    category: str
    interpretation: str


class StrengthDNAVisualizer:
    """
    Strength DNA 雙軌色帶視覺化器

    創建基於 T1-T12 才幹強度排序的精美視覺效果
    """

    # T1-T12 維度定義
    T_DIMENSION_NAMES = {
        'T1': '結構化執行',
        'T2': '品質與完備',
        'T3': '探索與創新',
        'T4': '分析與洞察',
        'T5': '影響與倡議',
        'T6': '協作與共好',
        'T7': '客戶導向',
        'T8': '學習與成長',
        'T9': '紀律與信任',
        'T10': '壓力調節',
        'T11': '衝突整合',
        'T12': '責任與當責'
    }

    # 才幹類別與顏色主題
    CATEGORY_THEMES = {
        'execution': {
            'name': '執行力',
            'dimensions': ['T1', 'T2', 'T9', 'T12'],
            'color_gradient': ['#2563eb', '#3b82f6', '#60a5fa', '#93c5fd'],  # 藍色系
            'icon': '⚡',
            'description': '將想法轉化為現實的能力'
        },
        'influencing': {
            'name': '影響力',
            'dimensions': ['T5', 'T7'],
            'color_gradient': ['#dc2626', '#ef4444', '#f87171', '#fca5a5'],  # 紅色系
            'icon': '🎯',
            'description': '影響他人並推動變革的能力'
        },
        'relationship': {
            'name': '關係建立',
            'dimensions': ['T6', 'T10', 'T11'],
            'color_gradient': ['#059669', '#10b981', '#34d399', '#6ee7b7'],  # 綠色系
            'icon': '🤝',
            'description': '建立連結並促進合作的能力'
        },
        'thinking': {
            'name': '戰略思考',
            'dimensions': ['T3', 'T4', 'T8'],
            'color_gradient': ['#7c3aed', '#8b5cf6', '#a78bfa', '#c4b5fd'],  # 紫色系
            'icon': '🧠',
            'description': '分析資訊並制定策略的能力'
        }
    }

    def __init__(self):
        """初始化視覺化器"""
        self._setup_color_mappings()

    def _setup_color_mappings(self):
        """設定維度到顏色的映射"""
        self.dimension_colors = {}

        for category, theme in self.CATEGORY_THEMES.items():
            dimensions = theme['dimensions']
            gradient = theme['color_gradient']

            for i, dim in enumerate(dimensions):
                color_index = min(i, len(gradient) - 1)
                self.dimension_colors[dim] = {
                    'primary': gradient[color_index],
                    'secondary': self._lighten_color(gradient[color_index]),
                    'category': category
                }

    def _lighten_color(self, hex_color: str, factor: float = 0.3) -> str:
        """將顏色變淺"""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        # 向白色混合
        lightened = tuple(int(c + (255 - c) * factor) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"

    def create_strength_dna(self, norm_scores: Dict) -> List[StrengthDNA]:
        """
        創建 Strength DNA 數據

        Args:
            norm_scores: 常模分數字典 {dimension: NormScore}

        Returns:
            按強度排序的 StrengthDNA 列表
        """
        dna_items = []

        # 按百分位數排序
        sorted_scores = sorted(
            norm_scores.items(),
            key=lambda x: x[1].percentile,
            reverse=True
        )

        for rank, (dimension, score) in enumerate(sorted_scores, 1):
            color_info = self.dimension_colors.get(dimension, {
                'primary': '#6b7280',
                'secondary': '#d1d5db',
                'category': 'other'
            })

            dna_item = StrengthDNA(
                dimension=dimension,
                name=self.T_DIMENSION_NAMES.get(dimension, dimension),
                strength_score=score.raw_theta,
                percentile=score.percentile,
                rank=rank,
                color_primary=color_info['primary'],
                color_secondary=color_info['secondary'],
                category=color_info['category'],
                interpretation=score.interpretation
            )
            dna_items.append(dna_item)

        return dna_items

    def generate_dna_visualization(self, dna_items: List[StrengthDNA]) -> Dict:
        """
        生成雙軌色帶視覺化數據

        Args:
            dna_items: StrengthDNA 列表

        Returns:
            視覺化配置字典
        """
        # 計算色帶段落
        dna_segments = []
        total_length = 100  # 總長度百分比

        for i, item in enumerate(dna_items):
            # 計算每個段落的長度（基於強度權重）
            if len(dna_items) > 0:
                base_width = total_length / len(dna_items)
                # 根據百分位數調整寬度
                strength_factor = (item.percentile / 100) * 0.5 + 0.75  # 0.75-1.25倍
                segment_width = base_width * strength_factor
            else:
                segment_width = total_length

            # 計算漸層效果
            gradient_stops = self._create_gradient_stops(
                item.color_primary,
                item.color_secondary,
                item.percentile
            )

            segment = {
                'dimension': item.dimension,
                'name': item.name,
                'rank': item.rank,
                'width_percent': segment_width,
                'percentile': item.percentile,
                'category': item.category,
                'gradient_primary': gradient_stops['primary'],
                'gradient_secondary': gradient_stops['secondary'],
                'intensity': self._calculate_intensity(item.percentile),
                'glow_effect': self._calculate_glow(item.percentile),
                'pattern_overlay': self._get_pattern_overlay(item.category, item.percentile)
            }
            dna_segments.append(segment)

        # 歸一化寬度
        total_width = sum(seg['width_percent'] for seg in dna_segments)
        if total_width > 0:
            for segment in dna_segments:
                segment['width_percent'] = (segment['width_percent'] / total_width) * 100

        return {
            'dna_segments': dna_segments,
            'category_summary': self._generate_category_summary(dna_items),
            'visualization_config': self._get_visualization_config(),
            'strength_narrative': self._generate_strength_narrative(dna_items)
        }

    def _create_gradient_stops(self, primary: str, secondary: str, percentile: float) -> Dict:
        """創建漸層色階"""
        intensity = percentile / 100

        return {
            'primary': {
                'start': primary,
                'middle': self._blend_colors(primary, secondary, 0.3),
                'end': secondary,
                'opacity_start': min(1.0, 0.6 + intensity * 0.4),
                'opacity_end': min(1.0, 0.3 + intensity * 0.3)
            },
            'secondary': {
                'start': secondary,
                'middle': self._blend_colors(secondary, '#ffffff', 0.4),
                'end': self._blend_colors(secondary, '#ffffff', 0.7),
                'opacity_start': min(0.8, 0.4 + intensity * 0.4),
                'opacity_end': min(0.6, 0.2 + intensity * 0.2)
            }
        }

    def _blend_colors(self, color1: str, color2: str, ratio: float) -> str:
        """混合兩個顏色"""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)

        blended = tuple(int(c1 * (1 - ratio) + c2 * ratio) for c1, c2 in zip(rgb1, rgb2))
        return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"

    def _calculate_intensity(self, percentile: float) -> str:
        """計算強度等級"""
        if percentile >= 85:
            return 'exceptional'  # 卓越
        elif percentile >= 70:
            return 'strong'       # 強勢
        elif percentile >= 50:
            return 'moderate'     # 中等
        elif percentile >= 30:
            return 'developing'   # 發展中
        else:
            return 'emerging'     # 新興

    def _calculate_glow(self, percentile: float) -> Dict:
        """計算發光效果"""
        intensity = percentile / 100

        return {
            'enabled': bool(percentile >= 70),
            'radius': int(5 + intensity * 10),
            'opacity': float(min(0.8, intensity * 0.6)),
            'color': '#fbbf24' if percentile >= 85 else '#60a5fa'
        }

    def _get_pattern_overlay(self, category: str, percentile: float) -> Dict:
        """獲取圖案覆蓋效果"""
        patterns = {
            'execution': {
                'type': 'diagonal-lines',
                'spacing': 8,
                'angle': 45
            },
            'influencing': {
                'type': 'dots',
                'size': 3,
                'spacing': 10
            },
            'relationship': {
                'type': 'waves',
                'amplitude': 4,
                'frequency': 0.5
            },
            'thinking': {
                'type': 'hexagons',
                'size': 6,
                'spacing': 12
            }
        }

        pattern = patterns.get(category, {'type': 'none'})
        pattern['opacity'] = float(min(0.3, (percentile / 100) * 0.2))
        pattern['enabled'] = bool(percentile >= 60)

        return pattern

    def _generate_category_summary(self, dna_items: List[StrengthDNA]) -> Dict:
        """生成類別摘要"""
        category_stats = {}

        for category, theme in self.CATEGORY_THEMES.items():
            category_items = [item for item in dna_items if item.category == category]

            if category_items:
                avg_percentile = sum(item.percentile for item in category_items) / len(category_items)
                top_talent = max(category_items, key=lambda x: x.percentile)

                category_stats[category] = {
                    'name': theme['name'],
                    'icon': theme['icon'],
                    'description': theme['description'],
                    'average_percentile': avg_percentile,
                    'talent_count': len(category_items),
                    'top_talent': {
                        'dimension': top_talent.dimension,
                        'name': top_talent.name,
                        'percentile': top_talent.percentile,
                        'rank': top_talent.rank
                    },
                    'strength_level': self._get_category_strength_level(avg_percentile)
                }

        return category_stats

    def _get_category_strength_level(self, avg_percentile: float) -> str:
        """獲取類別強度等級"""
        if avg_percentile >= 80:
            return '主導優勢'
        elif avg_percentile >= 65:
            return '核心強項'
        elif avg_percentile >= 50:
            return '均衡發展'
        elif avg_percentile >= 35:
            return '成長潛力'
        else:
            return '待開發領域'

    def _get_visualization_config(self) -> Dict:
        """獲取視覺化配置"""
        return {
            'canvas': {
                'width': 800,
                'height': 120,
                'margin': {'top': 20, 'right': 20, 'bottom': 40, 'left': 20}
            },
            'dna_track': {
                'primary_height': 40,
                'secondary_height': 25,
                'gap': 5,
                'border_radius': 8
            },
            'labels': {
                'font_family': "'Inter', 'Segoe UI', sans-serif",
                'font_size': {
                    'rank': 14,
                    'name': 11,
                    'category': 10
                },
                'font_weight': {
                    'rank': 600,
                    'name': 500,
                    'category': 400
                }
            },
            'animation': {
                'enabled': True,
                'duration': 1200,
                'easing': 'cubic-bezier(0.4, 0, 0.2, 1)',
                'delay_increment': 100
            },
            'interactive': {
                'hover_effects': True,
                'click_details': True,
                'tooltip_enabled': True
            }
        }

    def _generate_strength_narrative(self, dna_items: List[StrengthDNA]) -> Dict:
        """生成才幹敘事"""
        if not dna_items:
            return {'summary': '無才幹數據', 'details': []}

        top_3 = dna_items[:3]
        bottom_3 = dna_items[-3:]

        # 分析才幹分布
        category_distribution = {}
        for item in dna_items:
            category = item.category
            if category not in category_distribution:
                category_distribution[category] = []
            category_distribution[category].append(item)

        # 找出主導類別
        dominant_category = max(
            category_distribution.items(),
            key=lambda x: (len(x[1]), sum(item.percentile for item in x[1]) / len(x[1]))
        )[0]

        dominant_theme = self.CATEGORY_THEMES[dominant_category]

        narrative = {
            'summary': f"您的才幹以「{dominant_theme['name']}」為主導特質，展現出{dominant_theme['description']}的天賦。",
            'dominant_category': {
                'name': dominant_theme['name'],
                'icon': dominant_theme['icon'],
                'description': dominant_theme['description']
            },
            'top_strengths': [
                {
                    'rank': item.rank,
                    'name': item.name,
                    'percentile': item.percentile,
                    'interpretation': item.interpretation,
                    'category': self.CATEGORY_THEMES[item.category]['name']
                }
                for item in top_3
            ],
            'development_opportunities': [
                {
                    'rank': item.rank,
                    'name': item.name,
                    'percentile': item.percentile,
                    'growth_potential': self._calculate_growth_potential(item.percentile),
                    'category': self.CATEGORY_THEMES[item.category]['name']
                }
                for item in bottom_3
            ],
            'balance_analysis': self._analyze_talent_balance(dna_items)
        }

        return narrative

    def _calculate_growth_potential(self, percentile: float) -> str:
        """計算成長潛力"""
        if percentile < 25:
            return '高成長潛力 - 透過刻意練習可顯著提升'
        elif percentile < 50:
            return '中等成長潛力 - 穩定發展可帶來進步'
        elif percentile < 75:
            return '精進空間 - 深化應用可達到更高水準'
        else:
            return '維持優勢 - 持續發揮並尋求創新應用'

    def _analyze_talent_balance(self, dna_items: List[StrengthDNA]) -> Dict:
        """分析才幹平衡性"""
        percentiles = [item.percentile for item in dna_items]

        if not percentiles:
            return {'type': '無數據', 'description': ''}

        range_span = max(percentiles) - min(percentiles)
        avg_percentile = sum(percentiles) / len(percentiles)
        std_dev = np.std(percentiles)

        if range_span < 30 and std_dev < 15:
            balance_type = '均衡型'
            description = '您的才幹發展相對均衡，各項能力都有穩定的表現。'
        elif range_span > 60 or std_dev > 25:
            balance_type = '分化型'
            description = '您有明確的才幹優勢領域，建議專注發展強項並適度補強弱項。'
        else:
            balance_type = '混合型'
            description = '您的才幹呈現多元發展，有潛力在多個領域發揮影響力。'

        return {
            'type': balance_type,
            'description': description,
            'range_span': range_span,
            'average_percentile': avg_percentile,
            'variability': std_dev,
            'recommendations': self._get_balance_recommendations(balance_type)
        }

    def _get_balance_recommendations(self, balance_type: str) -> List[str]:
        """獲取平衡性建議"""
        recommendations = {
            '均衡型': [
                '尋找能整合多項才幹的角色和專案',
                '發展跨領域的專業技能',
                '培養團隊協作和溝通能力'
            ],
            '分化型': [
                '深度發展您的頂尖才幹',
                '尋求能發揮優勢的專業領域',
                '建立互補的團隊夥伴關係'
            ],
            '混合型': [
                '探索多元發展的職涯路徑',
                '培養整合不同才幹的創新能力',
                '保持學習的開放心態'
            ]
        }

        return recommendations.get(balance_type, [])


def create_fancy_dna_visualization(norm_scores: Dict) -> Dict:
    """
    創建精美的 Strength DNA 視覺化

    Args:
        norm_scores: 常模分數字典

    Returns:
        完整的視覺化數據包
    """
    visualizer = StrengthDNAVisualizer()

    # 創建 DNA 數據
    dna_items = visualizer.create_strength_dna(norm_scores)

    # 生成視覺化
    visualization = visualizer.generate_dna_visualization(dna_items)

    return {
        'dna_data': [item.__dict__ for item in dna_items],
        'visualization': visualization,
        'metadata': {
            'total_dimensions': len(dna_items),
            'generation_timestamp': int(time.time()),
            'version': '1.0.0'
        }
    }