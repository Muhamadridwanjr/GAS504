"""
Configuration management for gas-rag-macro.
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
    SERVICE_NAME: str = "gas-rag-macro"
    PORT: int = 9002
    ENVIRONMENT: Literal["development", "staging", "production", "testing"] = "development"
    LOG_LEVEL: str = "INFO"

    # ── Provider ─────────────────────────────────────────────────────────
    DEFAULT_PROVIDER: Literal["vertex", "openai"] = "openai"
    ENABLE_PROVIDER_ROUTING: bool = True

    # ── Vertex AI ────────────────────────────────────────────────────────
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    VERTEX_PROJECT_ID: str = ""
    VERTEX_LOCATION: str = "us-central1"
    VERTEX_MODEL: str = "gemini-1.5-pro"
    VERTEX_EMBEDDING_MODEL: str = "text-embedding-004"

    # ── OpenAI ───────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── News API ─────────────────────────────────────────────────────────
    NEWS_API_KEY: str = ""
    NEWS_SOURCES: str = "bloomberg,reuters,cnbc,marketwatch"
    NEWS_FETCH_INTERVAL: int = 300  # seconds

    # ── Economic Calendar ────────────────────────────────────────────────
    CALENDAR_PROVIDER: str = "forexfactory"
    CALENDAR_API_KEY: str = ""

    # ── Vector Database ──────────────────────────────────────────────────
    VECTOR_DB_TYPE: Literal["chroma", "faiss", "pinecone"] = "chroma"
    VECTOR_DB_URL: str = "http://localhost:9102"
    VECTOR_DB_API_KEY: str = ""
    VECTOR_DB_COLLECTION: str = "macro_analysis"

    # ── Market Data Service ──────────────────────────────────────────────
    MARKET_DATA_SERVICE_URL: str = "http://gas-market-data-processor:8100"
    MARKET_DATA_API_KEY: str = ""

    # ── Knowledge Base ───────────────────────────────────────────────────
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    INDEXING_INTERVAL: int = 3600      # seconds
    CHUNK_SIZE: int = 1500             # tokens per chunk
    CHUNK_OVERLAP: int = 200           # overlap between chunks

    # ── Redis Cache ──────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600              # seconds

    # ── Internal Security ─────────────────────────────────────────────────
    INTERNAL_API_KEY: str = "gas-internal-secret-key"


settings = Settings()
