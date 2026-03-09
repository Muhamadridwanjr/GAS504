from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "GAS Signal Service"
    DEBUG: bool = False
    PORT: int = 8106
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database & Redis
    DATABASE_URL: str
    REDIS_URL: str

    # External Services
    BILLING_SERVICE_URL: str
    BILLING_API_KEY: str = ""
    JWT_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
