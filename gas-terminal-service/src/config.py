from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    port: int = 8206
    environment: str = "development"
    log_level: str = "INFO"

    # Execution
    term_service_url: str = "http://gas-term-service:8205"
    billing_service_url: str = "http://gas-billing-service:8004"

    # Charts & Realtime
    chart_service_url: str = "http://gas-chart-service:8101"
    realtime_hub_url: str = "http://gas-realtime-hub:8111"
    indicator_engine_url: str = "http://gas-indicator-engine:9510"
    smc_engine_url: str = "http://gas-smc-engine:9505"

    # News & Macro
    news_service_url: str = "http://gas-calendar-news-service:8103"
    rag_macro_url: str = "http://gas-rag-macro:9002"

    # Research & AI
    rag_technical_url: str = "http://gas-rag-technical:9001"
    ai_orchestrator_url: str = "http://gas-ai-orchestrator:8100"
    fundamental_data_url: str = "http://gas-fundamental-data-service:8104"
    vector_db_url: str = "http://gas-vector-db:9004"
    pattern_detector_url: str = "http://gas-pattern-detector:9501"
    quant_orchestrator_url: str = "http://gas-quant-orch:9500"
    quant_backtester_url: str = "http://gas-quant-backtester:9512"

    # Portfolio & Risk
    journal_service_url: str = "http://gas-journal-service:8107"
    risk_engine_url: str = "http://gas-risk-engine:9511"

    # Social & Collaboration
    social_service_url: str = "http://gas-social-service:8106"
    tradingplan_service_url: str = "http://gas-tradingplan-service:8108"
    notification_service_url: str = "http://gas-notification-service:8112"

    internal_api_key: str = "your_internal_api_key_here"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
