"""
Configuration Management - Gallup Strengths Assessment

Implements configuration management following Linus Torvalds principles:
- Simple and pragmatic
- Environment-based configuration
- No hardcoded values
- Clear separation of concerns

This module centralizes all configuration in one place with proper defaults.
"""

import os
from functools import lru_cache
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.

    Follows the "configuration external to code" principle.
    All settings can be overridden via environment variables.
    """

    # Application Configuration
    app_name: str = Field(
        default="gallup-strengths-assessment",
        description="Application name for logging and identification"
    )

    app_version: str = Field(
        default="1.0.0",
        description="Application version"
    )

    debug_mode: bool = Field(
        default=True,
        description="Enable debug mode for development"
    )

    # API Configuration
    api_prefix: str = Field(
        default="/api/v1",
        description="API version prefix"
    )

    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS allowed origins"
    )

    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./data/gallup_assessment.db",
        description="Database connection URL"
    )

    database_echo: bool = Field(
        default=False,
        description="Enable SQLAlchemy SQL logging"
    )

    # Psychometric Configuration
    mini_ipip_version: str = Field(
        default="v1.0",
        description="Mini-IPIP instrument version"
    )

    weights_version: str = Field(
        default="v1.0.0",
        description="Strength scoring weights version"
    )

    algorithm_version: str = Field(
        default="v1.0.0",
        description="Scoring algorithm version"
    )

    # Session Configuration
    session_timeout_minutes: int = Field(
        default=60,
        description="Assessment session timeout in minutes"
    )

    max_concurrent_sessions: int = Field(
        default=100,
        description="Maximum concurrent assessment sessions"
    )

    # Privacy Configuration
    consent_retention_days: int = Field(
        default=365,
        description="Days to retain consent records"
    )

    response_retention_hours: int = Field(
        default=24,
        description="Hours to retain raw responses after scoring"
    )

    # Reporting Configuration
    pdf_generation_timeout: int = Field(
        default=30,
        description="PDF generation timeout in seconds"
    )

    share_link_expiry_hours: int = Field(
        default=24,
        description="Shared report link expiry in hours"
    )

    # Quality Control Configuration
    min_completion_time_seconds: int = Field(
        default=60,
        description="Minimum time to complete assessment (quality control)"
    )

    max_completion_time_minutes: int = Field(
        default=30,
        description="Maximum time to complete assessment"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_prefix = "GALLUP_"
        case_sensitive = False


class PsychometricSettings:
    """
    Psychometric-specific configuration constants.

    These values are based on Mini-IPIP psychometric properties
    and should not be changed without proper validation.
    """

    # Mini-IPIP Configuration
    TOTAL_ITEMS: int = 20
    LIKERT_SCALE_MIN: int = 1
    LIKERT_SCALE_MAX: int = 7
    LIKERT_SCALE_NEUTRAL: int = 4

    # Reverse-scored items (1-indexed)
    REVERSE_ITEMS: List[int] = [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]

    # Big Five Factor Mapping
    BIG_FIVE_FACTORS: List[str] = [
        "extraversion",
        "agreeableness",
        "conscientiousness",
        "neuroticism",
        "openness"
    ]

    # HEXACO Extension
    HEXACO_FACTORS: List[str] = BIG_FIVE_FACTORS + ["honesty_humility"]

    # 12 Strength Facets (Chinese names as per specifications)
    STRENGTH_FACETS: List[str] = [
        "結構化執行",
        "品質與完備",
        "探索與創新",
        "分析與洞察",
        "影響與倡議",
        "協作與共好",
        "客戶導向",
        "學習與成長",
        "紀律與信任",
        "壓力調節",
        "衝突整合",
        "責任與當責"
    ]

    # Score Ranges
    SCORE_MIN: int = 0
    SCORE_MAX: int = 100
    CONFIDENCE_THRESHOLD: float = 0.7


class DevelopmentSettings(Settings):
    """
    Development environment specific settings.

    Overrides base settings with development-friendly defaults.
    """
    debug_mode: bool = True
    database_echo: bool = True
    allowed_origins: List[str] = ["*"]  # Allow all origins in dev


class ProductionSettings(Settings):
    """
    Production environment specific settings.

    Security-focused configuration for production deployment.
    """
    debug_mode: bool = False
    database_echo: bool = False
    # allowed_origins will be set via environment variables


@lru_cache()
def get_settings() -> Settings:
    """
    Get application settings with caching.

    Uses LRU cache to avoid repeated environment variable parsing.
    The cache ensures settings are loaded once and reused.

    Returns:
        Settings: Application configuration object
    """
    environment = os.getenv("ENVIRONMENT", "development").lower()

    if environment == "production":
        return ProductionSettings()
    else:
        return DevelopmentSettings()


@lru_cache()
def get_psychometric_settings() -> PsychometricSettings:
    """
    Get psychometric configuration constants.

    These settings are constants based on Mini-IPIP specifications
    and should not change between environments.

    Returns:
        PsychometricSettings: Psychometric configuration constants
    """
    return PsychometricSettings()


# Convenience function for database URL
def get_database_url() -> str:
    """Get database URL from settings."""
    settings = get_settings()
    return settings.database_url


# Convenience function for API configuration
def get_api_config() -> dict:
    """Get API configuration dictionary."""
    settings = get_settings()
    return {
        "prefix": settings.api_prefix,
        "title": settings.app_name,
        "version": settings.app_version,
        "debug": settings.debug_mode
    }