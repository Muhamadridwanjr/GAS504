from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9501
    environment: str = "development"
    log_level: str = "INFO"

    redis_url: str = "redis://localhost:6379"
    vector_db_url: str = "http://gas-vector-db:9004"
    vector_db_collection: str = "market_patterns"
    cache_ttl: int = 300
    default_top_k: int = 10
    min_confidence: float = 0.6

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
