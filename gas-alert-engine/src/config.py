from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "GAS Alert Engine"
    DEBUG: bool = False
    PORT: int = 8400
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database & Redis
    DATABASE_URL: str
    REDIS_URL: str

    # Redis Channels & Queues
    MARKET_DATA_CHANNEL: str = "market:data"
    NOTIFICATION_QUEUE: str = "notifications"
    ALERT_CACHE_PREFIX: str = "alert"

    # Worker
    WORKER_CONCURRENCY: int = 10

    # Auth
    JWT_SECRET_KEY: str = ""

    # External Services
    NOTIFICATION_SERVICE_URL: str = ""
    GATEWAY_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
