from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # FastAPI
    APP_NAME: str = "GAS Gateway API v2"
    DEBUG: bool = False
    PORT: int = 8000

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # JWT Secret
    SUPABASE_JWT_SECRET: str
    
    # Gateway API Key (System-to-System)
    GATEWAY_API_KEY: str
    
    # Production Hardening
    ENABLE_DOCS: bool = True

    # ── VPS 1 - Core ────────────────────────────────────────────────────
    AUTH_SERVICE_URL: str
    USER_SERVICE_URL: str
    BILLING_SERVICE_URL: str
    TELEGRAM_BOT_URL: str
    WEB_BACKEND_URL: str

    # ── VPS 2 - Engine ─────────────────────────────────────────────────
    ENGINE_ORCHESTRATOR_URL: str
    SIGNAL_SERVICE_URL: str
    JOURNAL_SERVICE_URL: str
    ALERT_ENGINE_URL: str

    # ── VPS 3 - AI ─────────────────────────────────────────────────────
    RAG_TECHNICAL_URL: str
    RAG_MACRO_URL: str
    AI_ORCHESTRATOR_URL: str

    # ── VPS 4 - Market Data ────────────────────────────────────────────
    MT5_DATA_SERVICE_URL: str
    TV_TECHNICAL_URL: str
    TV_FUNDAMENTAL_URL: str
    NOTIFICATION_SERVICE_URL: str
    TCG_SERVICE_URL: str
    NFT_SERVICE_URL: str
    MARKETPLACE_SERVICE_URL: str

    # ── VPS 5 - Data & Analysis Services ───────────────────────────────
    SCREENER_SERVICE_URL: str = "http://gas-screener-service:9600"
    CALENDAR_NEWS_SERVICE_URL: str = "http://gas-calendar-news-service:9601"
    TRADINGPLAN_SERVICE_URL: str = "http://gas-tradingplan-service:9602"
    FUNDAMENTAL_DATA_SERVICE_URL: str = "http://gas-fundamental-data-service:9603"
    DATA_INGESTOR_URL: str = "http://gas-data-ingestor:9604"
    CHART_SERVICE_URL: str = "http://gas-chart-service:9700"

    # ── Engine Layer ────────────────────────────────────────────────────
    INDICATOR_ENGINE_URL: str = "http://gas-indicator-engine:8203"
    SMC_ENGINE_URL: str = "http://gas-smc-engine:8000"
    FEATURE_ENGINE_URL: str = "http://gas-feature-engine:9499"
    STRATEGY_CORE_URL: str = "http://gas-strategy-core:7003"

    # ── Social & Realtime ───────────────────────────────────────────────
    SOCIAL_SERVICE_URL: str = "http://gas-social-service:8500"
    REALTIME_HUB_URL: str = "http://gas-realtime-hub:8111"
    MT5_WEBSOCKET_URL: str = "http://gas-mt5-websocket:8110"
    VECTOR_DB_URL: str = "http://gas-vector-db:9004"

    # ── Quant Layer ─────────────────────────────────────────────────────
    QUANT_ORCH_URL: str = "http://gas-quant-orch:9500"
    PATTERN_DETECTOR_URL: str = "http://gas-pattern-detector:9501"
    STATARB_ENGINE_URL: str = "http://gas-statarb-engine:9502"
    REGIME_DETECTOR_URL: str = "http://gas-regime-detector:9503"
    QUANT_BACKTESTER_URL: str = "http://gas-quant-backtester:9504"

    # ── Edge / Legendary Layer ──────────────────────────────────────────
    MARKET_PHASE_URL: str = "http://gas-market-phase:9510"
    RISK_ENGINE_URL: str = "http://gas-risk-engine:9511"
    CORRELATION_URL: str = "http://gas-correlation:9512"
    TREND_ENGINE_URL: str = "http://gas-trend-engine:9513"
    ORDERFLOW_URL: str = "http://gas-orderflow:9514"

    # ── Client / Terminal ───────────────────────────────────────────────
    TERMINAL_BACKEND_URL: str = "http://gas-terminal-backend:8085"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
