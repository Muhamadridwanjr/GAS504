from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "GAS Memecoin Service"
    PORT: int = 9614
    HOST: str = "0.0.0.0"
    REDIS_URL: str = "redis://gas-redis:6379/0"
    STRATEGY_CORE_URL: str = "http://gas-strategy-core:7003"
    DEXSCREENER_BASE: str = "https://api.dexscreener.com"
    CACHE_TTL: int = 30         # 30s for trending
    SIGNAL_CACHE_TTL: int = 60  # 1min for signals
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
