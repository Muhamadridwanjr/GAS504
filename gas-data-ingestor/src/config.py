"""
Configuration management for gas-data-ingestor.
Uses Pydantic settings for type-safe environment variable loading.
"""
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Service ─────────────────────────────────────────────────────────
    SERVICE_NAME: str = "gas-data-ingestor"
    PORT: int = 9604
    ENVIRONMENT: Literal["development", "staging", "production", "testing"] = "development"
    LOG_LEVEL: str = "INFO"

    # ── Storage ─────────────────────────────────────────────────────────
    STORAGE_TYPE: Literal["minio", "s3"] = "minio"
    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET: str = "gas-data"
    S3_REGION: str = "us-east-1"

    # ── Source ──────────────────────────────────────────────────────────
    SOURCE_TYPE: Literal["excel", "csv", "api"] = "csv"
    SOURCE_PATH: str = "/data/gold.csv"
    SOURCE_API_URL: str = ""
    SOURCE_API_KEY: str = ""

    # ── Processing ──────────────────────────────────────────────────────
    CHUNK_SIZE: int = 100000
    PARTITION_BY: str = '["year","month"]'
    DEFAULT_SYMBOL: str = "XAUUSD"

    # ── Summary ─────────────────────────────────────────────────────────
    GENERATE_SUMMARY: bool = True
    SUMMARY_PERIOD: Literal["day", "week", "month", "year"] = "month"

    # ── Vector DB ───────────────────────────────────────────────────────
    VECTOR_DB_URL: str = "http://gas-vector-db:9004"
    VECTOR_DB_COLLECTION: str = "market_summaries"

    # ── Embedding ───────────────────────────────────────────────────────
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_API_KEY: str = ""

    # ── Scheduling ──────────────────────────────────────────────────────
    SCHEDULE_ENABLED: bool = False
    SCHEDULE_CRON: str = "0 2 * * *"

    # ── Internal Security ─────────────────────────────────────────────
    INTERNAL_API_KEY: str = "gas-internal-secret-key"


settings = Settings()
