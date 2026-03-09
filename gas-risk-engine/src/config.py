import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 9511
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str = "redis://localhost:6379"
    MAX_DAILY_DRAWDOWN: float = 5.0
    MAX_RISK_PER_TRADE: float = 2.0

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception as e:
    print(f"Error loading settings: {e}")
    # Fallback for unexpected missing vars during build
    os.environ.setdefault("PORT", "9511")
    settings = Settings()
