import os
import json
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PORT: int = 9512
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str = "redis://localhost:6379"
    FEATURE_ENGINE_URL: str = "http://gas-feature-engine:9499"
    ASSET_LIST: str = '["XAUUSD","DXY","EURUSD","GBPUSD","BTCUSD","ETHUSD","US30","SPX500"]'
    CORRELATION_WINDOWS: str = '[20,50,100]'
    DEFAULT_THRESHOLD: float = 0.7
    CACHE_TTL: int = 60

    @property
    def assets(self) -> List[str]:
        return json.loads(self.ASSET_LIST)

    @property
    def windows(self) -> List[int]:
        return json.loads(self.CORRELATION_WINDOWS)

    class Config:
        env_file = ".env"

try:
    settings = Settings()
except Exception:
    os.environ.setdefault("PORT", "9512")
    settings = Settings()
