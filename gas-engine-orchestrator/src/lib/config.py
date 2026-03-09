from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    host: str = "0.0.0.0"
    port: int = 8105
    environment: str = "development"
    
    # Redis
    redis_host: str = "gas-redis"
    redis_port: int = 6379
    redis_password: str = ""
    
    # Security
    jwt_secret_key: str = "super-secret-key-change-me-in-production"
    jwt_algorithm: str = "HS256"
    
    # Engine URLs
    indicator_engine_grpc_url: str = "gas-indicator-engine:8201"
    smc_engine_grpc_url: str = "gas-smc-engine:8202"
    ai_orchestrator_url: str = "http://gas-ai-orchestrator:9003"
    
    # Other
    strategy_path: str = "./strategies"
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
