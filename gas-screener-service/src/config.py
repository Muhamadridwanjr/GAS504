"""
Configuration management for gas-screener-service.
"""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore",
    )

    SERVICE_NAME: str = "gas-screener-service"
    PORT: int = 9600
    ENVIRONMENT: Literal["development", "staging", "production", "testing"] = "development"
    LOG_LEVEL: str = "INFO"

    # ── Engine URLs ──────────────────────────────────────────────────────
    INDICATOR_ENGINE_URL: str = "http://gas-indicator-engine:8203"
    INDICATOR_ENGINE_API_KEY: str = ""
    SMC_ENGINE_URL: str = "http://gas-smc-engine:8006"
    SMC_ENGINE_API_KEY: str = ""
    FEATURE_ENGINE_URL: str = ""

    # ── Screener ─────────────────────────────────────────────────────────
    DEFAULT_SYMBOLS: str = '["XAUUSD","BTCUSD","EURUSD","GBPUSD","US30"]'
    CONCURRENCY_LIMIT: int = 20
    REQUEST_TIMEOUT: float = 5.0

    # ── Redis Cache ──────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 60

    # ── Internal Security ─────────────────────────────────────────────
    INTERNAL_API_KEY: str = "gas-internal-secret-key"


settings = Settings()
