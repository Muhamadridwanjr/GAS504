from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 9003
    vector_db_type: str = "chroma"
    vector_db_url: str = "http://localhost:8001"
    vector_db_api_key: str | None = None
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    moonshot_api_key: str | None = None
    technical_model_url: str = "http://localhost:8501"
    macro_model_url: str = "http://localhost:8502"
    chart_service_url: str = "http://gas-chart-service:9700"
    mt5_data_service_url: str = "http://gas-mt5-data-service:8100"
    redis_url: str = "redis://localhost:6379/0"
    google_application_credentials: str = "/app/credentials/google_credentials.json"
    log_level: str = "INFO"
    environment: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()
