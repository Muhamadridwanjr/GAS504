"""Configuration for gas-tradingplan-service."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    SERVICE_NAME: str = "gas-tradingplan-service"
    PORT: int = 9602
    ENVIRONMENT: Literal["development","staging","production","testing"] = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pass@localhost:5432/gas_tradingplan"
    REDIS_URL: str = ""
    CACHE_TTL: int = 300
    SOFT_DELETE: bool = True
    INTERNAL_API_KEY: str = "gas-internal-secret-key"
settings = Settings()
