import os
import json
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PORT: int = 9514
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str = "redis://localhost:6379"
    TICK_CHANNEL: str = "market:ticks"
    SYMBOLS: str = '["XAUUSD","BTCUSD","EURUSD"]'
    DELTA_THRESHOLD: int = 100
    IMBALANCE_THRESHOLD: float = 0.3
    CACHE_TTL: int = 60

    @property
    def symbol_list(self) -> List[str]:
        return json.loads(self.SYMBOLS)

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception:
    os.environ.setdefault("PORT", "9514")
    settings = Settings()
