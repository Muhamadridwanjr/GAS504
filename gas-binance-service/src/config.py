from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    port: int = 9612
    redis_url: str = "redis://gas-redis:6379/0"
    binance_api_key: str = ""
    binance_secret_key: str = ""
    market_data_processor_url: str = "http://gas-market-data-processor:8010"
    realtime_hub_url: str = "http://gas-realtime-hub:8111"
    cache_ttl: int = 60
    default_limit: int = 100
    environment: str = "development"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
