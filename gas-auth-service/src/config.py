from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    # ===== FastAPI =====
    APP_NAME: str = "GAS Auth Service"
    DEBUG: bool = False
    PORT: int = 8001

    # ===== Google OAuth2 =====
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    GOOGLE_REDIRECT_URI: str = "http://localhost:8001/v1/auth/google/callback"

    # ===== Frontend =====
    FRONTEND_URL: str = "http://localhost:5173"

    # ===== JWT =====
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_HOURS: int = 24

    # ===== Database (shared gas-user-db) =====
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@gas-user-db:5432/gas_user_db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10

    # ===== Logging =====
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
