"""Configuration for gas-calendar-news-service."""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore")
    SERVICE_NAME: str = "gas-calendar-news-service"
    PORT: int = 9601
    ENVIRONMENT: Literal["development","staging","production","testing"] = "development"
    LOG_LEVEL: str = "INFO"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:pass@localhost:5432/gas_calendar"
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL: int = 3600
    VECTOR_DB_URL: str = "http://gas-vector-db:9004"
    VECTOR_DB_COLLECTION: str = "economic_events"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: str = ""
    INGESTION_SCHEDULE: str = "0 * * * *"
    ECOCAL_THREADS: int = 20
    INTERNAL_API_KEY: str = "gas-internal-secret-key"

settings = Settings()
