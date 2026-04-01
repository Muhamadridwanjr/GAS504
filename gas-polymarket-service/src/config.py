from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "GAS Polymarket Service"
    PORT: int = 9613
    HOST: str = "0.0.0.0"
    REDIS_URL: str = "redis://gas-redis:6379/0"
    STRATEGY_CORE_URL: str = "http://gas-strategy-core:7003"
    GAMMA_API_BASE: str = "https://gamma-api.polymarket.com"
    CLOB_API_BASE: str = "https://clob.polymarket.com"
    DATA_API_BASE: str = "https://data-api.polymarket.com"
    CACHE_TTL: int = 120  # 2 min cache for markets
    PREDICT_CACHE_TTL: int = 60  # 1 min cache for predictions
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
