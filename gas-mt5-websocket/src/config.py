import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MODE: str = "socket"  # "local" or "socket"
    SOCKET_PORT: int = 8110
    REDIS_URL: str = "redis://gas-redis:6379/0"
    REDIS_TICK_CHANNEL: str = "market:ticks"
    REDIS_OHLC_CHANNEL_PREFIX: str = "market:ohlc"
    
    # MT5 Local Mode configs
    MT5_PATH: str = r"C:\Program Files\MetaTrader 5\terminal64.exe"
    MT5_ACCOUNT: Optional[int] = None
    MT5_PASSWORD: Optional[str] = None
    MT5_SERVER: Optional[str] = None
    
    # Default pairs to subscribe to in Local mode
    SYMBOLS: List[str] = ["XAUUSD", "BTCUSD"]
    TIMEFRAMES: List[str] = ["M1", "M5"]
    
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
