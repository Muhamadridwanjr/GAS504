"""GAS Terminal v3 — Configuration"""
import os
from pathlib import Path
from dotenv import load_dotenv

_env = Path(__file__).parent.parent / ".env"
load_dotenv(_env)

# ── Auth GAS Platform ─────────────────────────────────────────────────
# GAS_EMAIL / GAS_PASSWORD = akun login gasstrategyai.xyz
# Dipakai oleh `gas login` untuk ambil JWT token otomatis
GAS_TOKEN: str    = os.getenv("GAS_TOKEN",    "")
GAS_EMAIL: str    = os.getenv("GAS_EMAIL",    "")
GAS_PASSWORD: str = os.getenv("GAS_PASSWORD", "")

# ── Core Service URLs ─────────────────────────────────────────────────
GATEWAY_URL: str          = os.getenv("GATEWAY_URL",          "http://localhost:8000")
WEB_BACKEND_URL: str      = os.getenv("WEB_BACKEND_URL",      "http://localhost:8005")
TERMINAL_BACKEND_URL: str = os.getenv("TERMINAL_BACKEND_URL", "http://localhost:8060")
AUTH_URL: str             = os.getenv("AUTH_URL",             "http://localhost:8001")
AGENT_ENGINE_URL: str     = os.getenv("AGENT_ENGINE_URL",     "http://localhost:9000")

MT5_WEBSOCKET_URL: str    = os.getenv("MT5_WEBSOCKET_URL",    "http://localhost:8001")
BINANCE_SERVICE_URL: str  = os.getenv("BINANCE_SERVICE_URL",  "http://localhost:9612")
SIGNAL_SERVICE_URL: str   = os.getenv("SIGNAL_SERVICE_URL",   "http://localhost:8106")
SMC_ENGINE_URL: str       = os.getenv("SMC_ENGINE_URL",       "http://localhost:8011")
RISK_ENGINE_URL: str      = os.getenv("RISK_ENGINE_URL",      "http://localhost:8021")
QUANT_BACKTESTER_URL: str = os.getenv("QUANT_BACKTESTER_URL", "http://localhost:8030")
SCREENER_SERVICE_URL: str = os.getenv("SCREENER_SERVICE_URL", "http://localhost:8025")
CALENDAR_NEWS_URL: str    = os.getenv("CALENDAR_NEWS_URL",    "http://localhost:8019")
OBSERVABILITY_URL: str    = os.getenv("OBSERVABILITY_URL",    "http://localhost:9090")

# ══════════════════════════════════════════════════════════════════════
# AI MODEL KEYS — semua provider yang dipakai di GAS
# ══════════════════════════════════════════════════════════════════════

# ── 1. Anthropic / Claude ─────────────────────────────────────────────
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
MODEL_COMPLEX: str     = os.getenv("MODEL_COMPLEX", "claude-sonnet-4-6")
MODEL_FAST: str        = os.getenv("MODEL_FAST",    "claude-haiku-4-5-20251001")

# ── 2. OpenRouter (DeepSeek, Llama, Mistral, dll via 1 key) ──────────
OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
# Model default via OpenRouter (bisa ganti di .env)
OPENROUTER_MODEL: str   = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-chat")

# Semua model yang tersedia via OpenRouter:
OPENROUTER_MODELS: dict = {
    "deepseek-chat":    "deepseek/deepseek-chat",
    "deepseek-r1":      "deepseek/deepseek-r1",
    "deepseek-r1-free": "deepseek/deepseek-r1:free",
    "claude-sonnet":    "anthropic/claude-sonnet-4-6",
    "claude-haiku":     "anthropic/claude-haiku-4-5",
    "gemini-flash":     "google/gemini-2.0-flash-001",
    "gemini-pro":       "google/gemini-pro",
    "llama-70b":        "meta-llama/llama-3.1-70b-instruct",
    "llama-405b":       "meta-llama/llama-3.1-405b-instruct",
    "mistral-large":    "mistralai/mistral-large",
    "qwen-72b":         "qwen/qwen-2.5-72b-instruct",
}

# ── 3. Kimi AI / Moonshot ─────────────────────────────────────────────
KIMI_API_KEY: str      = os.getenv("KIMI_API_KEY",      "")
KIMI_BASE_URL: str     = "https://api.moonshot.cn/v1"
KIMI_MODEL: str        = os.getenv("KIMI_MODEL",        "moonshot-v1-32k")

KIMI_MODELS: dict = {
    "moonshot-v1-8k":   "moonshot-v1-8k",    # cepat, hemat
    "moonshot-v1-32k":  "moonshot-v1-32k",   # default, balanced
    "moonshot-v1-128k": "moonshot-v1-128k",  # context panjang
}

# ── 4. Google Gemini AI Studio ────────────────────────────────────────
GEMINI_API_KEY: str    = os.getenv("GEMINI_API_KEY",    "")
GEMINI_MODEL: str      = os.getenv("GEMINI_MODEL",      "gemini-2.0-flash")

GEMINI_MODELS: dict = {
    "gemini-2.0-flash":  "gemini-2.0-flash",
    "gemini-1.5-pro":    "gemini-1.5-pro",
    "gemini-1.5-flash":  "gemini-1.5-flash",
}

# ── 5. Vertex AI (Google Cloud) ───────────────────────────────────────
VERTEX_PROJECT_ID: str      = os.getenv("VERTEX_PROJECT_ID",      "gen-lang-client-0060492434")
VERTEX_LOCATION: str        = os.getenv("VERTEX_LOCATION",        "us-central1")
VERTEX_CREDENTIALS: str     = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "")
VERTEX_MODEL: str           = os.getenv("VERTEX_MODEL",           "gemini-2.0-flash")

# ── Default AI Provider (pilih salah satu: claude/openrouter/kimi/gemini/vertex)
DEFAULT_AI_PROVIDER: str    = os.getenv("DEFAULT_AI_PROVIDER",    "openrouter")

# ── Redis ─────────────────────────────────────────────────────────────
REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# ── Telegram ──────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID: str   = os.getenv("TELEGRAM_CHAT_ID",   "")

# ── Terminal Meta ─────────────────────────────────────────────────────
WEBSITE_URL: str      = os.getenv("WEBSITE_URL",    "gasstrategyai.xyz")
SERVER_NAME: str      = os.getenv("SERVER_NAME",    "VPS Trading Node")
DOMAINS_BASE: str     = os.getenv("DOMAINS_BASE",   str(Path(__file__).parent.parent.parent / "domains"))
AGENT_ENGINE_DIR: str = os.getenv("AGENT_ENGINE_DIR", str(Path(__file__).parent.parent.parent / "agent-engine"))
