from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9499
    environment: str = "development"
    log_level: str = "INFO"

    redis_url: str = "redis://localhost:6379"
    market_data_url: str = "http://gas-market-data-processor:8100"
    cache_ttl: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
