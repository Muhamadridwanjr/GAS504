import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 9510
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str = "redis://localhost:6379"
    FEATURE_ENGINE_URL: str = "http://gas-feature-engine:9499"
    CACHE_TTL: int = 60

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    # Fallback for unexpected missing vars during build
    os.environ.setdefault("PORT", "9510")
    settings = Settings()
