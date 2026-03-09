from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9503
    environment: str = "development"
    log_level: str = "INFO"

    redis_url: str = "redis://localhost:6379"
    regime_method: str = "rule_based" # rule_based or ml
    model_path: str = "./src/models/regime_model.pkl"
    cache_ttl: int = 60

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
