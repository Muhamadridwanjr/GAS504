from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PORT: int = 8100
    REDIS_URL: str = "redis://localhost:6379/1"
    MT5_MODE: str = "socket"  # local or socket
    MT5_PATH: str = "C:\\Program Files\\MetaTrader 5\\terminal64.exe"
    MT5_EA_HOST: str = "localhost"
    MT5_EA_PORT: int = 8080
    MT5_ACCOUNT: str | None = None
    MT5_PASSWORD: str | None = None
    MT5_SERVER: str | None = None
    CACHE_TTL: int = 3600
    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "development"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
