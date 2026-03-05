"""Configuration for gas-chart-service."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    SERVICE_NAME: str = "gas-chart-service"
    PORT: int = 9700
    ENVIRONMENT: Literal["development","staging","production","testing"] = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pass@localhost:5432/gas_chart"
    REDIS_URL: str = "redis://localhost:6379"
    MT5_DATA_URL: str = "http://gas-mt5-data-service:8100"
    INDICATOR_ENGINE_URL: str = "http://gas-indicator-engine:8203"
    SMC_ENGINE_URL: str = "http://gas-smc-engine:8006"
    REQUEST_TIMEOUT: float = 5.0
    CACHE_TTL: int = 5
    INTERNAL_API_KEY: str = "gas-internal-secret-key"
settings = Settings()
