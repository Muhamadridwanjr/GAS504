"""
GAS Terminal Backend – Configuration
All service URLs and settings for the terminal aggregator.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── App ────────────────────────────────────────────────────────────
    APP_NAME: str = "GAS Terminal Backend"
    DEBUG: bool = False
    PORT: int = 8085
    HOST: str = "0.0.0.0"

    # ── Redis ──────────────────────────────────────────────────────────
    REDIS_HOST: str = "gas-redis"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 1
    CACHE_TTL_SECONDS: int = 30

    # ── Internal gateway key (for service-to-service) ─────────────────
    GATEWAY_API_KEY: str = ""

    # ── Upstream Service URLs ──────────────────────────────────────────
    SIGNAL_SERVICE_URL: str = "http://gas-signal-service:8106"
    CALENDAR_NEWS_URL: str = "http://gas-calendar-news-service:9601"
    FUNDAMENTAL_DATA_URL: str = "http://gas-fundamental-data-service:9603"
    CHART_SERVICE_URL: str = "http://gas-chart-service:9700"
    USER_SERVICE_URL: str = "http://gas-user-service:8002"
    TRADINGPLAN_URL: str = "http://gas-tradingplan-service:9602"
    JOURNAL_URL: str = "http://gas-journal-service:8107"
    MT5_DATA_URL: str = "http://gas-mt5-data-service:8100"
    SMC_ENGINE_URL: str = "http://gas-smc-engine:8000"
    INDICATOR_ENGINE_URL: str = "http://gas-indicator-engine:8203"
    REALTIME_HUB_URL: str = "http://gas-realtime-hub:8111"
    SCREENER_URL: str = "http://gas-screener-service:9600"

    # ── CORS ───────────────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
