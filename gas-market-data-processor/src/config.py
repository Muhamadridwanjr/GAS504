import os
import json
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = ""
    REDIS_DB: int = 0
    
    DEFAULT_TIMEFRAMES_RAW: str = Field('["M1","M5","M15","H1","H4","D1"]', validation_alias="DEFAULT_TIMEFRAMES")
    MAX_CANDLES_PER_KEY: int = 1000
    
    LOG_LEVEL: str = "INFO"
    PORT: int = 8010
    
    @property
    def TIMEFRAMES(self) -> list[str]:
        try:
            return json.loads(self.DEFAULT_TIMEFRAMES_RAW)
        except Exception:
            return ["M1","M5","M15","H1","H4","D1"]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
