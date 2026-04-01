from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "GAS Web Backend"
    DEBUG: bool = False
    PORT: int = 8005

    # Core URL
    GATEWAY_URL: str = "http://gas-gateway-api:8000"

    # Services URLs
    USER_SERVICE_URL: str = "http://gas-user-service:8002"
    BILLING_SERVICE_URL: str = "http://gas-billing-service:8004"
    JOURNAL_SERVICE_URL: str = "http://gas-journal-service:8107"
    SIGNAL_SERVICE_URL: str = "http://gas-signal-service:8106"
    TCG_SERVICE_URL: str = "http://gas-tcg-service:8300"
    NOTIFICATION_SERVICE_URL: str = "http://gas-notification-service:8112"
    STRATEGY_CORE_URL: str = "http://gas-strategy-core:7003"

    REDIS_URL: str = "redis://gas-redis:6379/0"
    LOG_LEVEL: str = "INFO"
    BOT_API_KEY: str = "gas-bot-key-2026-secret"

    class Config:
        env_file = ".env"

settings = Settings()
