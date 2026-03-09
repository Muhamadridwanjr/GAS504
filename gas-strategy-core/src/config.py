import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    STRATEGY_PATH: str = os.getenv("STRATEGY_PATH", "./strategies")
    STRATEGY_DB_URL: str = os.getenv("STRATEGY_DB_URL", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
settings = Settings()
