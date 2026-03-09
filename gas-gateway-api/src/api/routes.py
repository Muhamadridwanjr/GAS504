from fastapi import APIRouter
from src.api.v1 import (
    # Core
    auth, users, billing, telegram, web,
    # Engine
    engine, signals, journal, alerts,
    # Market Data
    mt5_data, tv_technical, tv_fundamental,
    # AI
    rag_technical, rag_macro, ai_orchestrator,
    # Notifications & TCG
    notification, tcg, nft, marketplace,
    # Data & Analysis (new layer)
    screener, calendar, fundamental, tradingplan, chart, data_ingestor,
    # Internal Engines
    indicator, smc, feature_engine, strategy,
    # Social & Realtime
    social, realtime, mt5_ws, vector_db,
    # Quant Layer
    quant_orch, pattern, statarb, regime, backtester,
    # Edge Legendary Layer
    market_phase, risk_engine, correlation, trend_engine, orderflow,
    # Health
    health,
    # Client
    terminal,
    # GAS EA Endpoints
    gas,
)

api_router = APIRouter()

# ── Core ──────────────────────────────────────────────────────────────
api_router.include_router(auth.router,         prefix="/v1/auth",         tags=["Auth"])
api_router.include_router(users.router,        prefix="/v1/users",        tags=["Users"])
api_router.include_router(billing.router,      prefix="/v1/billing",      tags=["Billing"])
api_router.include_router(telegram.router,     prefix="/v1/telegram",     tags=["Telegram"])
api_router.include_router(web.router,          prefix="/v1/web",          tags=["Web"])

# ── Engine ────────────────────────────────────────────────────────────
api_router.include_router(engine.router,       prefix="/v1/engine",       tags=["Engine"])
api_router.include_router(signals.router,      prefix="/v1/signals",      tags=["Signals"])
api_router.include_router(signals.router,      prefix="/signal",          tags=["EA Signals"])
api_router.include_router(journal.router,      prefix="/v1/journal",      tags=["Journal"])
api_router.include_router(alerts.router,       prefix="/v1/alerts",       tags=["Alerts"])

# ── Market Data ───────────────────────────────────────────────────────
api_router.include_router(mt5_data.router,     prefix="/v1/mt5/data",     tags=["Market Data"])
api_router.include_router(mt5_ws.router,       prefix="/v1/mt5/ws",       tags=["Market Data"])
api_router.include_router(tv_technical.router, prefix="/v1/tv/technical", tags=["Analysis"])
api_router.include_router(tv_fundamental.router,prefix="/v1/tv/fundamental",tags=["Analysis"])

# ── AI Layer ─────────────────────────────────────────────────────────
api_router.include_router(rag_technical.router, prefix="/v1/ai/technical", tags=["AI"])
api_router.include_router(rag_macro.router,     prefix="/v1/ai/macro",     tags=["AI"])
api_router.include_router(ai_orchestrator.router,prefix="/v1/ai/orchestrator",tags=["AI"])

# ── Notifications & TCG ───────────────────────────────────────────────
api_router.include_router(notification.router, prefix="/v1/notification",  tags=["Utility"])
api_router.include_router(tcg.router,          prefix="/v1/tcg",           tags=["TCG"])
api_router.include_router(nft.router,          prefix="/v1/nft",           tags=["TCG"])
api_router.include_router(marketplace.router,  prefix="/v1/marketplace",   tags=["TCG"])

# ── Data & Analysis Services ──────────────────────────────────────────
api_router.include_router(screener.router,     prefix="/v1/screener",      tags=["Data & Analysis"])
api_router.include_router(calendar.router,     prefix="/v1/calendar",      tags=["Data & Analysis"])
api_router.include_router(fundamental.router,  prefix="/v1/fundamental",   tags=["Data & Analysis"])
api_router.include_router(tradingplan.router,  prefix="/v1/tradingplan",   tags=["Data & Analysis"])
api_router.include_router(chart.router,        prefix="/v1/chart",         tags=["Data & Analysis"])
api_router.include_router(data_ingestor.router,prefix="/v1/ingestor",      tags=["Data & Analysis"])

# ── Internal Engines ──────────────────────────────────────────────────
api_router.include_router(indicator.router,    prefix="/v1/indicator",     tags=["Engines"])
api_router.include_router(smc.router,          prefix="/v1/smc",           tags=["Engines"])
api_router.include_router(feature_engine.router,prefix="/v1/feature-engine",tags=["Engines"])
api_router.include_router(strategy.router,     prefix="/v1/strategy",      tags=["Engines"])

# ── Social & Realtime ─────────────────────────────────────────────────
api_router.include_router(social.router,       prefix="/v1/social",        tags=["Social"])
api_router.include_router(realtime.router,     prefix="/v1/realtime",      tags=["Realtime"])
api_router.include_router(vector_db.router,    prefix="/v1/vector-db",     tags=["AI"])

# ── Quant Layer ───────────────────────────────────────────────────────
api_router.include_router(quant_orch.router,   prefix="/v1/quant",         tags=["Quant"])
api_router.include_router(pattern.router,      prefix="/v1/pattern",       tags=["Quant"])
api_router.include_router(statarb.router,      prefix="/v1/statarb",       tags=["Quant"])
api_router.include_router(regime.router,       prefix="/v1/regime",        tags=["Quant"])
api_router.include_router(backtester.router,   prefix="/v1/backtester",    tags=["Quant"])

# ── Edge / Legendary Layer ────────────────────────────────────────────
api_router.include_router(market_phase.router, prefix="/v1/market-phase",  tags=["Edge"])
api_router.include_router(risk_engine.router,  prefix="/v1/risk",          tags=["Edge"])
api_router.include_router(correlation.router,  prefix="/v1/correlation",   tags=["Edge"])
api_router.include_router(trend_engine.router, prefix="/v1/trend",         tags=["Edge"])
api_router.include_router(orderflow.router,    prefix="/v1/orderflow",     tags=["Edge"])

# ── Health (gateway itself) ───────────────────────────────────────────
api_router.include_router(health.router, tags=["Health"])

# ── Client Terminal ───────────────────────────────────────────────────
api_router.include_router(terminal.router, prefix="/v1/terminal", tags=["Terminal"])

# ─────────────────────────────────────────────────────────────────────
# API v2 — Same services, future-proof /v2/ prefix
# ─────────────────────────────────────────────────────────────────────
api_router.include_router(auth.router,          prefix="/v2/auth",           tags=["v2 Core"])
api_router.include_router(users.router,         prefix="/v2/users",          tags=["v2 Core"])
api_router.include_router(billing.router,       prefix="/v2/billing",        tags=["v2 Core"])
api_router.include_router(engine.router,        prefix="/v2/engine",         tags=["v2 Engine"])
api_router.include_router(signals.router,       prefix="/v2/signals",        tags=["v2 Engine"])
api_router.include_router(journal.router,       prefix="/v2/journal",        tags=["v2 Engine"])
api_router.include_router(alerts.router,        prefix="/v2/alerts",         tags=["v2 Engine"])
api_router.include_router(mt5_data.router,      prefix="/v2/mt5/data",       tags=["v2 Market Data"])
api_router.include_router(rag_technical.router, prefix="/v2/ai/technical",   tags=["v2 AI"])
api_router.include_router(rag_macro.router,     prefix="/v2/ai/macro",       tags=["v2 AI"])
api_router.include_router(ai_orchestrator.router,prefix="/v2/ai/orchestrator",tags=["v2 AI"])
api_router.include_router(screener.router,      prefix="/v2/screener",       tags=["v2 Data & Analysis"])
api_router.include_router(calendar.router,      prefix="/v2/calendar",       tags=["v2 Data & Analysis"])
api_router.include_router(fundamental.router,   prefix="/v2/fundamental",    tags=["v2 Data & Analysis"])
api_router.include_router(tradingplan.router,   prefix="/v2/tradingplan",    tags=["v2 Data & Analysis"])
api_router.include_router(chart.router,         prefix="/v2/chart",          tags=["v2 Data & Analysis"])
api_router.include_router(data_ingestor.router, prefix="/v2/ingestor",       tags=["v2 Data & Analysis"])
api_router.include_router(indicator.router,     prefix="/v2/indicator",      tags=["v2 Engines"])
api_router.include_router(smc.router,           prefix="/v2/smc",            tags=["v2 Engines"])
api_router.include_router(feature_engine.router,prefix="/v2/feature-engine", tags=["v2 Engines"])
api_router.include_router(strategy.router,      prefix="/v2/strategy",       tags=["v2 Engines"])
api_router.include_router(social.router,        prefix="/v2/social",         tags=["v2 Social"])
api_router.include_router(realtime.router,      prefix="/v2/realtime",       tags=["v2 Realtime"])
api_router.include_router(vector_db.router,     prefix="/v2/vector-db",      tags=["v2 AI"])
api_router.include_router(quant_orch.router,    prefix="/v2/quant",          tags=["v2 Quant"])
api_router.include_router(pattern.router,       prefix="/v2/pattern",        tags=["v2 Quant"])
api_router.include_router(statarb.router,       prefix="/v2/statarb",        tags=["v2 Quant"])
api_router.include_router(regime.router,        prefix="/v2/regime",         tags=["v2 Quant"])
api_router.include_router(backtester.router,    prefix="/v2/backtester",     tags=["v2 Quant"])
api_router.include_router(market_phase.router,  prefix="/v2/market-phase",   tags=["v2 Edge"])
api_router.include_router(risk_engine.router,   prefix="/v2/risk",           tags=["v2 Edge"])
api_router.include_router(correlation.router,   prefix="/v2/correlation",    tags=["v2 Edge"])
api_router.include_router(trend_engine.router,  prefix="/v2/trend",          tags=["v2 Edge"])
api_router.include_router(orderflow.router,     prefix="/v2/orderflow",      tags=["v2 Edge"])
api_router.include_router(terminal.router,      prefix="/v2/terminal",       tags=["v2 Terminal"])

# ── GAS EA Endpoints (no version prefix – EA sends /api/gas/...) ──────
api_router.include_router(gas.router,           prefix="/gas",               tags=["GAS EA"])
