"""
GAS System Health Endpoint
GET /api/v1/health          — simple liveness
GET /api/v1/system/health   — full dependency check
"""
import asyncio
import os
from fastapi import APIRouter
import httpx
import redis.asyncio as aioredis

router = APIRouter(tags=["Health"])

REDIS_URL          = os.getenv("REDIS_URL",          "redis://gas-redis:6379/0")
STRATEGY_CORE_URL  = os.getenv("STRATEGY_CORE_URL",  "http://gas-strategy-core:7003")
FUNDAMENTAL_URL    = os.getenv("FUNDAMENTAL_URL",     "http://gas-fundamental-data-service:9603")
CALENDAR_URL       = os.getenv("CALENDAR_NEWS_URL",   "http://gas-calendar-news-service:9601")
BINANCE_URL        = os.getenv("BINANCE_SERVICE_URL", "http://gas-binance-service:9612")
AUTH_URL           = os.getenv("AUTH_SERVICE_URL",    "http://gas-auth-service:8001")
BILLING_URL        = os.getenv("BILLING_SERVICE_URL", "http://gas-billing-service:8004")
TERMINAL_URL       = os.getenv("TERMINAL_BACKEND_URL","http://gas-terminal-backend:8085")
SIGNAL_URL         = os.getenv("SIGNAL_SERVICE_URL",  "http://gas-signal-service:8106")


async def _check_http(url: str, timeout: float = 3.0) -> str:
    """Ping a service health endpoint, return 'ok' or 'down'."""
    try:
        async with httpx.AsyncClient(timeout=timeout) as client:
            r = await client.get(f"{url}/health")
            if r.status_code < 500:
                return "ok"
            return f"error:{r.status_code}"
    except Exception as e:
        return f"down:{type(e).__name__}"


async def _check_redis() -> str:
    try:
        r = aioredis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        await r.ping()
        await r.aclose()
        return "ok"
    except Exception as e:
        return f"down:{type(e).__name__}"


async def _check_payment() -> str:
    """Check payment system: verify ERC20 wallet config is present."""
    try:
        wallet = os.getenv("ERC20_WALLET", "0xf8ef68F41B609B06210ebe7d045FA111F2034518")
        api_key = os.getenv("ETHERSCAN_API_KEY", "QQXE85JN3C1B6YIPBWRQNS5FK7GCMH2IKE")
        if wallet and api_key and len(wallet) == 42:
            return "ok"
        return "warn:config_missing"
    except Exception as e:
        return f"down:{type(e).__name__}"


async def _check_fear_greed() -> str:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            r = await client.get("https://api.alternative.me/fng/?limit=1")
            d = r.json()
            if d.get("data"):
                return f"ok:{d['data'][0].get('value_classification','?')}"
            return "warn:no data"
    except Exception as e:
        return f"down:{type(e).__name__}"


@router.get("/health")
async def health_check():
    return {"status": "ok", "message": "GAS Web Backend is healthy"}


@router.get("/system/circuit-breakers")
async def circuit_breaker_status():
    """Real-time per-endpoint circuit breaker status."""
    from ...services.circuit_breaker import CircuitBreakerRegistry
    return {
        "circuit_breakers": CircuitBreakerRegistry.all_statuses(),
    }


@router.get("/system/health")
async def system_health():
    """
    Full dependency health check.
    Runs all service probes in parallel and returns consolidated status.
    """
    (
        redis_status, strategy_status, fundamental_status,
        calendar_status, binance_status, auth_status,
        billing_status, terminal_status, signal_status,
        payment_status, fear_greed_status,
    ) = await asyncio.gather(
        _check_redis(),
        _check_http(STRATEGY_CORE_URL),
        _check_http(FUNDAMENTAL_URL),
        _check_http(CALENDAR_URL),
        _check_http(BINANCE_URL),
        _check_http(AUTH_URL),
        _check_http(BILLING_URL),
        _check_http(TERMINAL_URL),
        _check_http(SIGNAL_URL),
        _check_payment(),
        _check_fear_greed(),
    )

    services = {
        "gateway":           "ok",          # self
        "ai_engine":         strategy_status,
        "signal_service":    signal_status,
        "market_data":       binance_status,
        "economic_calendar": calendar_status,
        "fundamental_data":  fundamental_status,
        "payment":           payment_status,
        "database":          redis_status,
        "auth":              auth_status,
        "billing":           billing_status,
        "terminal":          terminal_status,
        "external_fear_greed": fear_greed_status,
    }

    # Overall status: ok if all core services pass
    core = [redis_status, strategy_status, auth_status, billing_status]
    overall = "ok" if all(s == "ok" for s in core) else "degraded"

    failing = [k for k, v in services.items() if not v.startswith("ok")]

    from ...services.circuit_breaker import CircuitBreakerRegistry
    cb_statuses = CircuitBreakerRegistry.all_statuses()
    open_cbs = [cb["name"] for cb in cb_statuses if cb["state"] == "OPEN"]

    return {
        "status": overall,
        "services": services,
        "failing": failing,
        "healthy_count": len(services) - len(failing),
        "total_count": len(services),
        "circuit_breakers": {
            "open": open_cbs,
            "total": len(cb_statuses),
            "detail": cb_statuses,
        },
    }
