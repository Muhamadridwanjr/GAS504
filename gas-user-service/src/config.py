from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "GAS User Service"
    DEBUG: bool = False
    PORT: int = 8002
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/gas_user_db"
    DATABASE_POOL_SIZE: int = 20
    DATABASE_MAX_OVERFLOW: int = 10
    
    # Service URLs
    AUTH_SERVICE_URL: str = "http://gas-auth-service:8001"
    BILLING_SERVICE_URL: str = "http://gas-billing-service:8004"
    
    # Redis (Optional)
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"

settings = Settings()
