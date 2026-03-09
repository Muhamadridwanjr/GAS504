from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "GAS Social Service"
    DEBUG: bool = False
    PORT: int = 8500
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database & Redis
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@gas-user-db:5432/gas_social"
    REDIS_URL: str = "redis://gas-redis:6379/3"

    # Internal API Key (for inter-service communication)
    INTERNAL_API_KEY: str = "internal_secret_key"

    # External Services
    SIGNAL_SERVICE_URL: str = "http://gas-signal-service:8106"
    SIGNAL_SERVICE_API_KEY: str = ""

    NOTIFICATION_SERVICE_URL: str = "http://gas-notification-service:8112"
    NOTIFICATION_SERVICE_API_KEY: str = ""

    GATEWAY_URL: str = "http://gas-gateway-api:8000"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
