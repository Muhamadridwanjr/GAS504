from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8111
    redis_url: str = "redis://localhost:6379"
    jwt_secret: str = "default_secret_for_dev_only"
    auth_service_url: str = ""
    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
