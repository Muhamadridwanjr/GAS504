from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8112
    redis_url: str = "redis://localhost:6379"
    internal_api_key: str = "your_internal_api_key_here"
    
    telegram_bot_token: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "noreply@gasstrategy.io"
    
    user_service_url: str = "http://gas-user-service:8002"
    realtime_hub_url: str = "http://gas-realtime-hub:8111"
    
    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
