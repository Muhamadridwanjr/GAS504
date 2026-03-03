from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9504
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "sqlite+aiosqlite:///./gas_backtest.db"
    market_data_url: str = "http://gas-feature-engine:9499"
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
