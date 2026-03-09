from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "GAS Journal Service"
    DEBUG: bool = False
    PORT: int = 8107
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Database & Redis
    DATABASE_URL: str
    REDIS_URL: str

    # Security
    INTERNAL_API_KEY: str
    JWT_SECRET_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
