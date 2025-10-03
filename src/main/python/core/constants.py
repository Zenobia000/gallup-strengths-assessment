"""
System Constants and Configuration

統一的系統常數管理，消除硬編碼：
- 心理測量參數
- API 配置
- 資料庫配置
- 前端配置

Linus 原則：所有魔術數字都應該有名稱和意義
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum


# 心理測量常數
class PsychometricConstants:
    """心理測量學相關常數"""

    # Mini-IPIP 評測參數
    MINI_IPIP_QUESTION_COUNT = 20
    MINI_IPIP_LIKERT_MIN = 1
    MINI_IPIP_LIKERT_MAX = 7
    MINI_IPIP_DIMENSIONS = 5

    # V4 強制選擇評測參數
    V4_DIMENSIONS_COUNT = 12
    V4_QUARTET_SIZE = 4
    V4_MIN_BLOCKS_FOR_COVERAGE = 9
    V4_OPTIMAL_BLOCKS = 12
    V4_MAX_BLOCKS = 18

    # IRT 模型參數
    IRT_THETA_MIN = -3.0
    IRT_THETA_MAX = 3.0
    IRT_THETA_DEFAULT = 0.0
    IRT_SE_THRESHOLD = 0.3

    # 才幹階層閾值
    DOMINANT_THRESHOLD = 75  # PR > 75%
    LESSER_THRESHOLD = 25    # PR < 25%

    # 信心分數閾值
    HIGH_CONFIDENCE = 0.8
    MEDIUM_CONFIDENCE = 0.6
    LOW_CONFIDENCE = 0.4

    # 職業原型匹配權重
    PRIMARY_TALENT_WEIGHT = 3.0
    SECONDARY_TALENT_WEIGHT = 1.0
    ARCHETYPE_CONFIDENCE_MIN = 0.7


# API 配置常數
class APIConstants:
    """API 相關常數"""

    # 端點配置
    V1_PREFIX = "/api/v1"
    V4_PREFIX = "/api/v4"

    # 預設埠號
    DEFAULT_API_PORT = 8004
    DEFAULT_FRONTEND_PORT = 3000

    # 超時配置
    REQUEST_TIMEOUT_SECONDS = 30
    SCORING_TIMEOUT_SECONDS = 60
    REPORT_GENERATION_TIMEOUT_SECONDS = 120

    # 分頁配置
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100

    # 快取配置
    CACHE_TTL_SHORT = 300    # 5分鐘
    CACHE_TTL_MEDIUM = 3600  # 1小時
    CACHE_TTL_LONG = 86400   # 24小時


# 資料庫配置常數
class DatabaseConstants:
    """資料庫相關常數"""

    # 連接配置
    CONNECTION_TIMEOUT = 30.0
    CONNECTION_POOL_SIZE = 10
    MAX_OVERFLOW = 20

    # SQLite 配置
    SQLITE_CACHE_SIZE = 10000  # 10MB
    SQLITE_WAL_MODE = "WAL"

    # 事務配置
    TRANSACTION_RETRY_COUNT = 3
    DEADLOCK_RETRY_DELAY = 0.1

    # 清理配置
    SESSION_EXPIRY_DAYS = 30
    LOG_RETENTION_DAYS = 90


# 業務邏輯常數
class BusinessConstants:
    """業務邏輯相關常數"""

    # 評測品質控制
    MIN_COMPLETION_TIME_SECONDS = 60    # 最短完成時間
    MAX_COMPLETION_TIME_SECONDS = 1800  # 最長完成時間
    SUSPICIOUS_FAST_TIME = 120          # 可疑的快速完成

    # 職業原型分析
    MIN_DOMINANT_TALENTS_FOR_ARCHETYPE = 2
    MAX_JOB_RECOMMENDATIONS = 10
    FEATURED_RECOMMENDATIONS_COUNT = 3

    # 報告生成
    PDF_GENERATION_TIMEOUT = 30
    REPORT_CACHE_HOURS = 24
    MAX_REPORT_SIZE_MB = 10

    # 分享設定
    SHARE_LINK_EXPIRY_DAYS = 7
    MAX_SHARE_ACCESS_COUNT = 5


# 前端配置常數
class FrontendConstants:
    """前端相關常數"""

    # 視覺配置
    DNA_HELIX_WIDTH = 960
    DNA_HELIX_HEIGHT = 180
    CONFIDENCE_BAR_WIDTH = 128  # 8rem in pixels

    # 動畫配置
    LOADING_SPINNER_DURATION = 1000  # 1秒
    FADE_TRANSITION_DURATION = 200   # 0.2秒

    # 響應式斷點
    MOBILE_BREAKPOINT = 768
    TABLET_BREAKPOINT = 1024
    DESKTOP_BREAKPOINT = 1200


@dataclass
class SystemConfiguration:
    """系統配置整合"""

    # 從環境變數讀取，使用常數作為預設值
    api_port: int = APIConstants.DEFAULT_API_PORT
    frontend_port: int = APIConstants.DEFAULT_FRONTEND_PORT
    db_timeout: float = DatabaseConstants.CONNECTION_TIMEOUT
    cache_ttl: int = APIConstants.CACHE_TTL_MEDIUM

    # 心理測量配置
    dominant_threshold: float = PsychometricConstants.DOMINANT_THRESHOLD
    lesser_threshold: float = PsychometricConstants.LESSER_THRESHOLD
    min_confidence: float = PsychometricConstants.LOW_CONFIDENCE

    # 業務配置
    min_completion_time: int = BusinessConstants.MIN_COMPLETION_TIME_SECONDS
    max_completion_time: int = BusinessConstants.MAX_COMPLETION_TIME_SECONDS
    max_recommendations: int = BusinessConstants.MAX_JOB_RECOMMENDATIONS

    @classmethod
    def from_environment(cls) -> 'SystemConfiguration':
        """從環境變數建立配置"""
        import os

        return cls(
            api_port=int(os.getenv('API_PORT', cls.api_port)),
            frontend_port=int(os.getenv('FRONTEND_PORT', cls.frontend_port)),
            db_timeout=float(os.getenv('DB_TIMEOUT', cls.db_timeout)),
            cache_ttl=int(os.getenv('CACHE_TTL', cls.cache_ttl)),

            dominant_threshold=float(os.getenv('DOMINANT_THRESHOLD', cls.dominant_threshold)),
            lesser_threshold=float(os.getenv('LESSER_THRESHOLD', cls.lesser_threshold)),
            min_confidence=float(os.getenv('MIN_CONFIDENCE', cls.min_confidence)),

            min_completion_time=int(os.getenv('MIN_COMPLETION_TIME', cls.min_completion_time)),
            max_completion_time=int(os.getenv('MAX_COMPLETION_TIME', cls.max_completion_time)),
            max_recommendations=int(os.getenv('MAX_RECOMMENDATIONS', cls.max_recommendations))
        )

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            'api_port': self.api_port,
            'frontend_port': self.frontend_port,
            'db_timeout': self.db_timeout,
            'cache_ttl': self.cache_ttl,
            'dominant_threshold': self.dominant_threshold,
            'lesser_threshold': self.lesser_threshold,
            'min_confidence': self.min_confidence,
            'min_completion_time': self.min_completion_time,
            'max_completion_time': self.max_completion_time,
            'max_recommendations': self.max_recommendations
        }


# 維度映射常數
class DimensionMapping:
    """T1-T12 維度映射常數"""

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

    DOMAIN_MAPPING = {
        'T1': 'executing', 'T2': 'executing', 'T9': 'executing', 'T12': 'executing',
        'T3': 'strategic', 'T4': 'strategic', 'T8': 'strategic',
        'T5': 'influencing',
        'T6': 'relationship', 'T7': 'relationship', 'T10': 'relationship', 'T11': 'relationship'
    }

    DOMAIN_COLORS = {
        'executing': '#7C3AED',     # 紫色
        'influencing': '#F59E0B',   # 橙色
        'relationship': '#0EA5E9',  # 藍色
        'strategic': '#10B981'      # 綠色
    }


# 全域配置實例
_system_config: Optional[SystemConfiguration] = None


def get_system_config() -> SystemConfiguration:
    """獲取系統配置實例"""
    global _system_config
    if _system_config is None:
        _system_config = SystemConfiguration.from_environment()
    return _system_config


# 便利函式
def get_api_config() -> Dict[str, Any]:
    """獲取 API 配置"""
    config = get_system_config()
    return {
        'v1_prefix': APIConstants.V1_PREFIX,
        'v4_prefix': APIConstants.V4_PREFIX,
        'api_port': config.api_port,
        'frontend_port': config.frontend_port,
        'request_timeout': APIConstants.REQUEST_TIMEOUT_SECONDS
    }


def get_psychometric_config() -> Dict[str, Any]:
    """獲取心理測量配置"""
    config = get_system_config()
    return {
        'dominant_threshold': config.dominant_threshold,
        'lesser_threshold': config.lesser_threshold,
        'min_confidence': config.min_confidence,
        'v4_optimal_blocks': PsychometricConstants.V4_OPTIMAL_BLOCKS,
        'primary_talent_weight': PsychometricConstants.PRIMARY_TALENT_WEIGHT
    }


def get_frontend_config() -> Dict[str, Any]:
    """獲取前端配置 (供 JavaScript 使用)"""
    config = get_system_config()
    return {
        'api_port': config.api_port,
        'frontend_port': config.frontend_port,
        'dominant_threshold': config.dominant_threshold,
        'lesser_threshold': config.lesser_threshold,
        'domain_colors': DimensionMapping.DOMAIN_COLORS,
        'dimension_names': DimensionMapping.T_DIMENSION_NAMES
    }