from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8205
    environment: str = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://postgres:pass@localhost:5432/gas_terminal"
    redis_url: str = "redis://localhost:6379/0"

    billing_service_url: str = "http://gas-billing-service:8004"
    billing_api_key: str = ""

    risk_engine_url: str = "http://gas-risk-engine:9511"
    risk_api_key: str = ""

    journal_service_url: str = "http://gas-journal-service:8107"
    journal_api_key: str = ""

    order_queue_key: str = "execution:orders"
    status_channel: str = "execution:status"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
