"""
Centralized configuration management for the Gallup Strengths Assessment system.
Handles environment variables, database settings, JWT configuration, and psychology-specific compliance settings.
"""

from functools import lru_cache
from typing import Optional, List
from pydantic import validator, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with psychology-specific compliance configurations."""

    # Application
    app_name: str = "Gallup Strengths Assessment API"
    app_version: str = "1.0.0"
    debug: bool = False

    # Server
    host: str = "127.0.0.1"
    port: int = 8000

    # Database
    database_url: str = "sqlite+aiosqlite:///./gallup_strengths.db"
    database_sync_url: str = "sqlite:///./gallup_strengths.db"
    echo_sql: bool = False

    # JWT Security
    secret_key: str = Field(default="your-secret-key-here-change-in-production-minimum-32-chars", min_length=32)
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # CORS
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:8080"]

    # Psychology/Compliance Settings
    session_ttl_hours: int = Field(24, description="Session data TTL (24h for psychological assessments)")
    sensitive_data_ttl_hours: int = Field(24, description="Sensitive data retention period")
    audit_logging_enabled: bool = True
    data_anonymization_enabled: bool = True
    consent_required: bool = True

    # Privacy Protection
    anonymize_ip_addresses: bool = True
    log_personal_data: bool = False

    # Assessment Configuration
    max_assessment_attempts: int = 3
    question_time_limit_seconds: int = 300
    session_inactivity_timeout_minutes: int = 30

    # Data Retention (GDPR Compliance)
    data_retention_days: int = 365
    audit_log_retention_days: int = 2555  # 7 years for psychological data

    @validator('backend_cors_origins', pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v

    @validator('secret_key')
    def validate_secret_key(cls, v):
        if len(v) < 32:
            raise ValueError('SECRET_KEY must be at least 32 characters long')
        return v

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached application settings."""
    return Settings()


# Psychology-specific configuration constants
PSYCHOLOGICAL_ASSESSMENT_CONFIG = {
    "min_question_response_time_ms": 500,  # Prevent bot responses
    "max_session_duration_hours": 24,
    "required_consent_types": ["data_processing", "assessment_participation", "result_storage"],
    "data_classification_levels": ["public", "internal", "confidential", "restricted"],
    "audit_event_types": [
        "session_created", "consent_given", "assessment_started",
        "question_answered", "assessment_completed", "data_accessed",
        "data_deleted", "privacy_request"
    ]
}