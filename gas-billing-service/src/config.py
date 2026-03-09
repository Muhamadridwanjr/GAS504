from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "GAS Billing Service"
    DEBUG: bool = False
    PORT: int = 8004
    
    # Database
    DATABASE_URL: Optional[str] = None
    SUPABASE_URL: Optional[str] = None
    SUPABASE_ANON_KEY: Optional[str] = None
    SUPABASE_SERVICE_ROLE_KEY: Optional[str] = None
    
    # Service URLs
    USER_SERVICE_URL: str = "http://gas-user-service:8002"
    AUTH_SERVICE_URL: str = "http://gas-auth-service:8001"
    
    # Redis
    REDIS_URL: Optional[str] = None
    
    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"

settings = Settings()
