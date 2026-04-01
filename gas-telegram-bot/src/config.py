from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_WEBHOOK_URL: Optional[str] = None

    # Redis (shared with main stack)
    REDIS_URL: str = "redis://gas-redis:6379/0"

    # Web backend for analysis + billing
    WEB_BACKEND_URL: str = "http://gas-web-backend:8005"

    # Internal bot API key (must match web-backend BOT_API_KEY)
    BOT_API_KEY: str = "gas-bot-key-2026-secret"

    # Site URL for Telegram link flow
    SITE_URL: str = "https://www.gasstrategyai.xyz"

    # Logging
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()

# Plans allowed to use the bot (all plans have at least basic access)
BOT_ALLOWED_PLANS = {"ultimate", "ultra", "premium", "plus", "essential", "trial", "free"}

# ── Per-plan feature matrix ────────────────────────────────────────────────────
PLAN_CONFIG = {
    "free": {
        "flows":       {"signal"},
        "cats":        {"FOREX", "CRYPTO"},
        "limit_pairs": {"XAUUSD", "EURUSD", "BTCUSD"},   # only these 3
        "styles":      {"scalping", "intraday"},
        "ai_tier":     "basic",
        "cache_ttl":   60,
        "label":       "🆓 Free",
        "upgrade_to":  "essential",
    },
    "trial": {
        "flows":       {"signal"},
        "cats":        {"FOREX", "CRYPTO"},
        "limit_pairs": {"XAUUSD", "EURUSD", "BTCUSD"},
        "styles":      {"scalping", "intraday"},
        "ai_tier":     "basic",
        "cache_ttl":   60,
        "label":       "🎁 Trial",
        "upgrade_to":  "essential",
    },
    "essential": {
        "flows":       {"signal"},
        "cats":        {"FOREX", "CRYPTO"},
        "limit_pairs": None,                               # all pairs in cat
        "styles":      {"scalping", "intraday", "swing", "position"},
        "ai_tier":     "basic",
        "cache_ttl":   30,
        "label":       "🔵 Essential",
        "upgrade_to":  "plus",
    },
    "plus": {
        "flows":       {"signal", "analysis"},
        "cats":        {"FOREX", "CRYPTO", "COMMODITY", "INDEX"},
        "limit_pairs": None,
        "styles":      {"scalping", "intraday", "swing", "position"},
        "ai_tier":     "advanced",
        "cache_ttl":   15,
        "label":       "➕ Plus",
        "upgrade_to":  "premium",
    },
    "premium": {
        "flows":       {"signal", "analysis", "analyst"},
        "cats":        {"FOREX", "CRYPTO", "COMMODITY", "INDEX", "MEME", "STOCK"},
        "limit_pairs": None,
        "styles":      {"scalping", "intraday", "swing", "position"},
        "ai_tier":     "pro",
        "cache_ttl":   5,
        "label":       "💎 Premium",
        "upgrade_to":  "ultimate",
    },
    "ultimate": {
        "flows":       {"signal", "analysis", "analyst", "scanner"},
        "cats":        {"FOREX", "CRYPTO", "COMMODITY", "INDEX", "MEME", "STOCK"},
        "limit_pairs": None,
        "styles":      {"scalping", "intraday", "swing", "position"},
        "ai_tier":     "ultra",
        "cache_ttl":   0,    # no cache — always fresh
        "label":       "👑 Ultimate",
        "upgrade_to":  None,
    },
    "ultra": {
        "flows":       {"signal", "analysis", "analyst", "scanner"},
        "cats":        {"FOREX", "CRYPTO", "COMMODITY", "INDEX", "MEME", "STOCK"},
        "limit_pairs": None,
        "styles":      {"scalping", "intraday", "swing", "position"},
        "ai_tier":     "ultra",
        "cache_ttl":   0,
        "label":       "⚡ Ultra",
        "upgrade_to":  None,
    },
}

def get_plan_cfg(plan: str) -> dict:
    """Return config for plan, fallback to free."""
    return PLAN_CONFIG.get(plan, PLAN_CONFIG["free"])
