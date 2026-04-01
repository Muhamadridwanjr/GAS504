"""
GAS Agent Engine — Environment Configuration
Loads all service URLs, model names, and infrastructure settings from environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from agent-engine directory
_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=_env_path)

# ─── Redis ────────────────────────────────────────────────────────────────────
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
REDIS_MAX_CONNECTIONS: int = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
REDIS_SOCKET_TIMEOUT: float = float(os.getenv("REDIS_SOCKET_TIMEOUT", "5.0"))

# ─── Database ─────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://gas:gas@localhost:5432/gasstrategy"
)
DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))

# ─── AI Model Configuration ───────────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
ANTHROPIC_BASE_URL: str = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

# Model tiers
MODEL_COMPLEX: str = os.getenv("MODEL_COMPLEX", "claude-sonnet-4-6")
MODEL_FAST: str = os.getenv("MODEL_FAST", "claude-haiku-4-5-20251001")
MODEL_LOCAL: str = os.getenv("MODEL_LOCAL", "llama3.1:8b")

# Local Ollama endpoint
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Model routing thresholds
MODEL_COMPLEX_MAX_TOKENS: int = int(os.getenv("MODEL_COMPLEX_MAX_TOKENS", "4096"))
MODEL_FAST_MAX_TOKENS: int = int(os.getenv("MODEL_FAST_MAX_TOKENS", "2048"))
CONTEXT_TOKEN_BUDGET: int = int(os.getenv("CONTEXT_TOKEN_BUDGET", "8000"))

# ─── Service URLs ─────────────────────────────────────────────────────────────
# Market Domain
MT5_WEBSOCKET_URL: str = os.getenv("MT5_WEBSOCKET_URL", "http://gas-mt5-websocket:8001")
MT5_DATA_SERVICE_URL: str = os.getenv("MT5_DATA_SERVICE_URL", "http://gas-mt5-data-service:8002")
MARKET_DATA_PROCESSOR_URL: str = os.getenv("MARKET_DATA_PROCESSOR_URL", "http://gas-market-data-processor:8003")
REALTIME_HUB_URL: str = os.getenv("REALTIME_HUB_URL", "http://gas-realtime-hub:8004")
DATA_INGESTOR_URL: str = os.getenv("DATA_INGESTOR_URL", "http://gas-data-ingestor:8005")
BINANCE_SERVICE_URL: str = os.getenv("BINANCE_SERVICE_URL", "http://gas-binance-service:9612")

# Analysis Domain
INDICATOR_ENGINE_URL: str = os.getenv("INDICATOR_ENGINE_URL", "http://gas-indicator-engine:8010")
SMC_ENGINE_URL: str = os.getenv("SMC_ENGINE_URL", "http://gas-smc-engine:8011")
TREND_ENGINE_URL: str = os.getenv("TREND_ENGINE_URL", "http://gas-trend-engine:8012")
PATTERN_DETECTOR_URL: str = os.getenv("PATTERN_DETECTOR_URL", "http://gas-pattern-detector:8013")
CORRELATION_URL: str = os.getenv("CORRELATION_URL", "http://gas-correlation:8014")
MARKET_PHASE_URL: str = os.getenv("MARKET_PHASE_URL", "http://gas-market-phase:8015")
REGIME_DETECTOR_URL: str = os.getenv("REGIME_DETECTOR_URL", "http://gas-regime-detector:8016")
ORDERFLOW_URL: str = os.getenv("ORDERFLOW_URL", "http://gas-orderflow:8017")
FUNDAMENTAL_DATA_URL: str = os.getenv("FUNDAMENTAL_DATA_URL", "http://gas-fundamental-data-service:8018")
CALENDAR_NEWS_URL: str = os.getenv("CALENDAR_NEWS_URL", "http://gas-calendar-news-service:8019")
CHART_SERVICE_URL: str = os.getenv("CHART_SERVICE_URL", "http://gas-chart-service:8020")

# Trading Domain
SIGNAL_SERVICE_URL: str = os.getenv("SIGNAL_SERVICE_URL", "http://gas-signal-service:8106")
RISK_ENGINE_URL: str = os.getenv("RISK_ENGINE_URL", "http://gas-risk-engine:8021")
ALERT_ENGINE_URL: str = os.getenv("ALERT_ENGINE_URL", "http://gas-alert-engine:8022")
TRADINGPLAN_URL: str = os.getenv("TRADINGPLAN_URL", "http://gas-tradingplan-service:8023")
STATARB_ENGINE_URL: str = os.getenv("STATARB_ENGINE_URL", "http://gas-statarb-engine:8024")
SCREENER_SERVICE_URL: str = os.getenv("SCREENER_SERVICE_URL", "http://gas-screener-service:8025")
FEATURE_ENGINE_URL: str = os.getenv("FEATURE_ENGINE_URL", "http://gas-feature-engine:8026")

# Quant Domain
QUANT_BACKTESTER_URL: str = os.getenv("QUANT_BACKTESTER_URL", "http://gas-quant-backtester:8030")
QUANT_ORCH_URL: str = os.getenv("QUANT_ORCH_URL", "http://gas-quant-orch:8031")
STRATEGY_CORE_URL: str = os.getenv("STRATEGY_CORE_URL", "http://gas-strategy-core:8010")
ENGINE_ORCHESTRATOR_URL: str = os.getenv("ENGINE_ORCHESTRATOR_URL", "http://gas-engine-orchestrator:8032")

# AI Domain
RAG_MACRO_URL: str = os.getenv("RAG_MACRO_URL", "http://gas-rag-macro:8040")
RAG_TECHNICAL_URL: str = os.getenv("RAG_TECHNICAL_URL", "http://gas-rag-technical:8041")
VECTOR_DB_URL: str = os.getenv("VECTOR_DB_URL", "http://gas-vector-db:8042")
AI_ORCHESTRATOR_URL: str = os.getenv("AI_ORCHESTRATOR_URL", "http://gas-ai-orchestrator:8050")

# Platform Domain
GATEWAY_API_URL: str = os.getenv("GATEWAY_API_URL", "http://gas-gateway-api:8000")
WEB_BACKEND_URL: str = os.getenv("WEB_BACKEND_URL", "http://gas-web-backend:8005")
TERMINAL_BACKEND_URL: str = os.getenv("TERMINAL_BACKEND_URL", "http://gas-terminal-backend:8060")
AUTH_SERVICE_URL: str = os.getenv("AUTH_SERVICE_URL", "http://gas-auth-service:8070")
BILLING_SERVICE_URL: str = os.getenv("BILLING_SERVICE_URL", "http://gas-billing-service:8080")
USER_SERVICE_URL: str = os.getenv("USER_SERVICE_URL", "http://gas-user-service:8071")
NOTIFICATION_SERVICE_URL: str = os.getenv("NOTIFICATION_SERVICE_URL", "http://gas-notification-service:8090")
TELEGRAM_BOT_URL: str = os.getenv("TELEGRAM_BOT_URL", "http://gas-telegram-bot:8091")
OBSERVABILITY_URL: str = os.getenv("OBSERVABILITY_URL", "http://gas-observability:9090")

# ─── Agent Engine Settings ────────────────────────────────────────────────────
DOMAINS_BASE_PATH: str = os.getenv(
    "DOMAINS_BASE_PATH",
    str(Path(__file__).parent.parent / "domains")
)
AGENT_DEFAULT_TIMEOUT: float = float(os.getenv("AGENT_DEFAULT_TIMEOUT", "30.0"))
AGENT_MAX_RETRIES: int = int(os.getenv("AGENT_MAX_RETRIES", "3"))
AGENT_RETRY_BASE_DELAY: float = float(os.getenv("AGENT_RETRY_BASE_DELAY", "1.0"))

# ─── Event Bus ────────────────────────────────────────────────────────────────
EVENT_BUS_STREAM_PREFIX: str = os.getenv("EVENT_BUS_STREAM_PREFIX", "gas:events")
EVENT_BUS_CONSUMER_GROUP: str = os.getenv("EVENT_BUS_CONSUMER_GROUP", "agent-engine")
EVENT_BUS_MAX_STREAM_LEN: int = int(os.getenv("EVENT_BUS_MAX_STREAM_LEN", "10000"))
EVENT_BUS_BLOCK_MS: int = int(os.getenv("EVENT_BUS_BLOCK_MS", "1000"))

# ─── Telegram ─────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ALERT_CHAT_ID: str = os.getenv("TELEGRAM_ALERT_CHAT_ID", "")
TELEGRAM_SECURITY_CHAT_ID: str = os.getenv("TELEGRAM_SECURITY_CHAT_ID", "")

# ─── Embedding ────────────────────────────────────────────────────────────────
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
EMBEDDING_DIMENSIONS: int = int(os.getenv("EMBEDDING_DIMENSIONS", "1536"))

# ─── Logging ──────────────────────────────────────────────────────────────────
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text

# ─── Feature Flags ────────────────────────────────────────────────────────────
ENABLE_LOCAL_MODEL: bool = os.getenv("ENABLE_LOCAL_MODEL", "false").lower() == "true"
ENABLE_RESPONSE_CACHE: bool = os.getenv("ENABLE_RESPONSE_CACHE", "true").lower() == "true"
ENABLE_CIRCUIT_BREAKER: bool = os.getenv("ENABLE_CIRCUIT_BREAKER", "true").lower() == "true"
CIRCUIT_BREAKER_THRESHOLD: int = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
CIRCUIT_BREAKER_TIMEOUT: int = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "300"))
