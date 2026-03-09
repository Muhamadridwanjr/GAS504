import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 9513
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str = "redis://localhost:6379"
    FEATURE_ENGINE_URL: str = "http://gas-feature-engine:9499"
    DEFAULT_BREAKOUT_PERIOD: int = 20
    DEFAULT_MA_FAST: int = 10
    DEFAULT_MA_SLOW: int = 30
    ADX_THRESHOLD: int = 25
    CACHE_TTL: int = 60

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception:
    os.environ.setdefault("PORT", "9513")
    settings = Settings()
