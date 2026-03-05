"""Configuration for gas-fundamental-data-service."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    SERVICE_NAME: str = "gas-fundamental-data-service"
    PORT: int = 9603
    ENVIRONMENT: Literal["development","staging","production","testing"] = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pass@localhost:5432/gas_fundamental"
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    FRED_API_KEY: str = ""
    WORLD_BANK_API_KEY: str = ""
    INGESTION_SCHEDULE: str = "0 2 * * *"
    INTERNAL_API_KEY: str = "gas-internal-secret-key"

settings = Settings()
