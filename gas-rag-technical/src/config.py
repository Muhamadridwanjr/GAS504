"""
Configuration management for gas-rag-technical.
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
    SERVICE_NAME: str = "gas-rag-technical"
    PORT: int = 9001
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: str = "INFO"

    # ── Provider ─────────────────────────────────────────────────────────
    DEFAULT_PROVIDER: Literal["vertex", "openai"] = "openai"
    ENABLE_PROVIDER_ROUTING: bool = True

    # ── Vertex AI ────────────────────────────────────────────────────────
    GOOGLE_APPLICATION_CREDENTIALS: str = ""
    VERTEX_PROJECT_ID: str = ""
    VERTEX_LOCATION: str = "us-central1"
    VERTEX_AGENT_ID: str = ""
    VERTEX_MODEL: str = "gemini-1.5-pro"
    VERTEX_EMBEDDING_MODEL: str = "text-embedding-004"

    # ── OpenAI ───────────────────────────────────────────────────────────
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # ── Vector Database ──────────────────────────────────────────────────
    VECTOR_DB_TYPE: Literal["chroma", "faiss", "pinecone"] = "chroma"
    VECTOR_DB_URL: str = "http://localhost:8001"
    VECTOR_DB_API_KEY: str = ""
    VECTOR_DB_COLLECTION: str = "technical_analysis"

    # ── Market Data Service ──────────────────────────────────────────────
    MARKET_DATA_SERVICE_URL: str = "http://gas-market-data-processor:8100"
    MARKET_DATA_API_KEY: str = ""

    # ── Knowledge Base ───────────────────────────────────────────────────
    KNOWLEDGE_BASE_PATH: str = "./data/knowledge_base"
    INDEXING_INTERVAL: int = 3600          # seconds
    CHUNK_SIZE: int = 1500                 # tokens per chunk
    CHUNK_OVERLAP: int = 200               # overlap between chunks

    # ── Redis Cache ──────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600                  # seconds

    # ── Internal Security ─────────────────────────────────────────────────
    INTERNAL_API_KEY: str = "gas-internal-secret-key"


settings = Settings()
