"""GAS Terminal v3 — HTTP API Client"""
from __future__ import annotations
import asyncio
import json
import httpx
from typing import Any, Optional
from gas_terminal import config
from gas_terminal.utils.display import console

_client: Optional[httpx.AsyncClient] = None

def _headers() -> dict:
    h = {"Content-Type": "application/json"}
    if config.GAS_TOKEN:
        h["Authorization"] = f"Bearer {config.GAS_TOKEN}"
    return h

async def _get_client() -> httpx.AsyncClient:
    global _client
    if _client is None or _client.is_closed:
        _client = httpx.AsyncClient(timeout=30.0)
    return _client

def run(coro):
    """Run async coroutine synchronously (for click commands)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(asyncio.run, coro)
                return future.result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)

# ── Auth ──────────────────────────────────────────────────────────────

async def login(email: str, password: str) -> dict:
    c = await _get_client()
    r = await c.post(f"{config.AUTH_URL}/auth/v1/login",
                     json={"email": email, "password": password})
    r.raise_for_status()
    return r.json()

# ── Web Backend — 18 AI Features ─────────────────────────────────────

async def ai_feature(feature: str, payload: dict) -> dict:
    """Call any of the 18 AI analysis features."""
    c = await _get_client()
    r = await c.post(f"{config.WEB_BACKEND_URL}/api/v1/analysis/{feature}",
                     json=payload, headers=_headers())
    if r.status_code == 200:
        return r.json()
    return {"error": r.text, "status": r.status_code}

async def web_health() -> dict:
    c = await _get_client()
    try:
        r = await c.get(f"{config.WEB_BACKEND_URL}/api/v1/health")
        return r.json()
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}

async def user_level() -> dict:
    c = await _get_client()
    r = await c.get(f"{config.WEB_BACKEND_URL}/api/v1/user/level", headers=_headers())
    return r.json() if r.status_code == 200 else {}

async def plan_features() -> dict:
    c = await _get_client()
    r = await c.get(f"{config.WEB_BACKEND_URL}/api/v1/plan/features", headers=_headers())
    return r.json() if r.status_code == 200 else {}

async def dashboard_data() -> dict:
    c = await _get_client()
    r = await c.get(f"{config.WEB_BACKEND_URL}/api/v1/dashboard", headers=_headers())
    return r.json() if r.status_code == 200 else {}

async def user_stats() -> dict:
    """Admin user statistics."""
    c = await _get_client()
    r = await c.get(f"{config.WEB_BACKEND_URL}/api/v1/admin/users", headers=_headers())
    return r.json() if r.status_code == 200 else {}

async def leaderboard() -> list:
    c = await _get_client()
    r = await c.get(f"{config.WEB_BACKEND_URL}/api/v1/leaderboard", headers=_headers())
    return r.json() if r.status_code == 200 else []

# ── Terminal Backend ──────────────────────────────────────────────────

async def terminal_signals(symbol: str = "XAUUSD") -> dict:
    c = await _get_client()
    try:
        r = await c.get(f"{config.TERMINAL_BACKEND_URL}/api/signals",
                        params={"symbol": symbol}, headers=_headers())
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        return {"error": str(e)}

async def terminal_overview() -> dict:
    c = await _get_client()
    try:
        r = await c.get(f"{config.TERMINAL_BACKEND_URL}/api/overview", headers=_headers())
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        return {"error": str(e)}

async def terminal_news(limit: int = 10) -> list:
    c = await _get_client()
    try:
        r = await c.get(f"{config.TERMINAL_BACKEND_URL}/api/news",
                        params={"limit": limit}, headers=_headers())
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        return []

async def terminal_calendar() -> list:
    c = await _get_client()
    try:
        r = await c.get(f"{config.TERMINAL_BACKEND_URL}/api/calendar", headers=_headers())
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        return []

async def terminal_ohlcv(symbol: str, timeframe: str = "M15", limit: int = 100) -> list:
    """Fetch OHLCV from terminal backend for chart rendering."""
    c = await _get_client()
    try:
        r = await c.get(f"{config.TERMINAL_BACKEND_URL}/api/chart/{symbol}",
                        params={"timeframe": timeframe, "limit": limit},
                        headers=_headers())
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        return []

async def terminal_pairs() -> list:
    c = await _get_client()
    try:
        r = await c.get(f"{config.TERMINAL_BACKEND_URL}/api/pairs", headers=_headers())
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        return []

# ── Binance ────────────────────────────────────────────────────────────

async def binance_tickers() -> list:
    c = await _get_client()
    try:
        r = await c.get(f"{config.BINANCE_SERVICE_URL}/tickers")
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        return []

async def binance_ticker(symbol: str) -> dict:
    c = await _get_client()
    try:
        r = await c.get(f"{config.BINANCE_SERVICE_URL}/ticker/{symbol}")
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        return {"error": str(e)}

# ── Agent Engine ───────────────────────────────────────────────────────

async def agents_status() -> dict:
    c = await _get_client()
    try:
        r = await c.get(f"{config.AGENT_ENGINE_URL}/status")
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        return {"error": str(e)}

async def agents_list(domain: Optional[str] = None) -> dict:
    c = await _get_client()
    try:
        params = {"domain": domain} if domain else {}
        r = await c.get(f"{config.AGENT_ENGINE_URL}/agents", params=params)
        return r.json() if r.status_code == 200 else {}
    except Exception as e:
        return {"agents": [], "domains": []}

async def agent_dispatch(agent_name: str, task: str = "", payload: dict = None) -> dict:
    c = await _get_client()
    try:
        r = await c.post(
            f"{config.AGENT_ENGINE_URL}/dispatch/{agent_name}",
            json={"task": task, "payload": payload or {}}
        )
        return r.json() if r.status_code == 200 else {"error": r.text}
    except Exception as e:
        return {"error": str(e)}

async def agent_pause(name: str) -> dict:
    c = await _get_client()
    r = await c.post(f"{config.AGENT_ENGINE_URL}/agents/{name}/pause")
    return r.json() if r.status_code == 200 else {"error": r.text}

async def agent_resume(name: str) -> dict:
    c = await _get_client()
    r = await c.post(f"{config.AGENT_ENGINE_URL}/agents/{name}/resume")
    return r.json() if r.status_code == 200 else {"error": r.text}

# ── Docker ─────────────────────────────────────────────────────────────

def docker_containers() -> list:
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list(all=True)
        return [
            {
                "name": c.name,
                "status": c.status,
                "image": c.image.tags[0] if c.image.tags else "unknown",
                "id": c.short_id,
            }
            for c in containers
        ]
    except Exception as e:
        return [{"error": str(e)}]

def docker_container_action(name: str, action: str) -> str:
    """action: start | stop | restart"""
    try:
        import docker
        client = docker.from_env()
        container = client.containers.get(name)
        getattr(container, action)()
        return f"Container '{name}' {action}ed successfully"
    except Exception as e:
        return f"Error: {e}"

def docker_stats() -> dict:
    try:
        import docker
        client = docker.from_env()
        all_c = client.containers.list(all=True)
        running = [c for c in all_c if c.status == "running"]
        return {"total": len(all_c), "running": len(running), "stopped": len(all_c) - len(running)}
    except Exception:
        return {"total": 0, "running": 0, "stopped": 0}

# ── Redis ──────────────────────────────────────────────────────────────

def redis_get(key: str) -> Any:
    try:
        import redis as r
        client = r.from_url(config.REDIS_URL)
        val = client.get(key)
        return val.decode() if val else None
    except Exception:
        return None

def redis_stream_read(stream: str, count: int = 10) -> list:
    try:
        import redis as r
        client = r.from_url(config.REDIS_URL)
        msgs = client.xrevrange(stream, count=count)
        return msgs
    except Exception:
        return []
