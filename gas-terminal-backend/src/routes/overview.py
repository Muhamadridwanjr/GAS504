"""
GET /terminal/overview – Aggregated dashboard data.
Returns real-time prices from Redis/MT5 + Binance, with market session status.
NO mock data — shows actual market state (open/closed) with last close price.
"""
import json
import time
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Request
from src.config import settings
from src.services.client import fetch_json
from src.services.redis import redis_service

router = APIRouter()

# ── Pair metadata (static: symbols, names, types only — NO prices) ───────────
PAIR_META = [
    # Commodities
    {"symbol": "XAUUSD", "name": "Gold / USD",        "type": "Commodity", "decimals": 2},
    {"symbol": "XAGUSD", "name": "Silver / USD",       "type": "Commodity", "decimals": 3},
    {"symbol": "USOIL",  "name": "WTI Crude Oil",      "type": "Commodity", "decimals": 2},
    {"symbol": "UKOIL",  "name": "Brent Crude Oil",    "type": "Commodity", "decimals": 2},
    # Forex Major 10 (Exness)
    {"symbol": "EURUSD", "name": "Euro / USD",         "type": "Forex",     "decimals": 5},
    {"symbol": "GBPUSD", "name": "Pound / USD",        "type": "Forex",     "decimals": 5},
    {"symbol": "USDJPY", "name": "USD / Yen",          "type": "Forex",     "decimals": 3},
    {"symbol": "USDCHF", "name": "USD / Franc",        "type": "Forex",     "decimals": 5},
    {"symbol": "AUDUSD", "name": "AUD / USD",          "type": "Forex",     "decimals": 5},
    {"symbol": "NZDUSD", "name": "NZD / USD",          "type": "Forex",     "decimals": 5},
    {"symbol": "USDCAD", "name": "USD / CAD",          "type": "Forex",     "decimals": 5},
    {"symbol": "EURGBP", "name": "Euro / Pound",       "type": "Forex",     "decimals": 5},
    {"symbol": "EURJPY", "name": "Euro / Yen",         "type": "Forex",     "decimals": 3},
    {"symbol": "GBPJPY", "name": "Pound / Yen",        "type": "Forex",     "decimals": 3},
    # Crypto (MT5)
    {"symbol": "BTCUSD", "name": "Bitcoin / USD",      "type": "Crypto",    "decimals": 2},
    {"symbol": "ETHUSD", "name": "Ethereum / USD",     "type": "Crypto",    "decimals": 2},
    # Indices (Exness)
    {"symbol": "US30",   "name": "Dow Jones 30",       "type": "Index",     "decimals": 1},
    {"symbol": "US500",  "name": "S&P 500",            "type": "Index",     "decimals": 2},
    {"symbol": "USTEC",  "name": "Nasdaq 100",         "type": "Index",     "decimals": 2},
    {"symbol": "UK100",  "name": "FTSE 100",           "type": "Index",     "decimals": 1},
    {"symbol": "GER40",  "name": "DAX 40",             "type": "Index",     "decimals": 1},
    {"symbol": "DXY",    "name": "US Dollar Index",    "type": "Index",     "decimals": 3},
]

# ── Crypto symbol map: MT5 symbol → Binance pair (path param format) ─────────
CRYPTO_BINANCE = {
    "BTCUSD": "BTC%2FUSDT",
    "ETHUSD": "ETH%2FUSDT",
}


def _market_status(symbol: str, pair_type: str) -> dict:
    """
    Returns real market open/close status based on UTC time.
    Crypto is always open. Forex/Commodity closes Fri 22:00 UTC – Sun 22:00 UTC.
    US Indices (CME futures) close 22:00–23:00 UTC daily.
    """
    now = datetime.now(timezone.utc)
    weekday = now.weekday()  # 0=Mon … 6=Sun
    hour = now.hour
    minute = now.minute

    if pair_type == "Crypto":
        return {"open": True, "session": "24/7", "label": "CRYPTO · 24/7"}

    # ── Weekend check (Forex/Commodity/Index) ────────────────────────────────
    if weekday == 5:  # Saturday — all closed
        return {"open": False, "session": "Weekend", "label": "TUTUP · Weekend"}
    if weekday == 6:  # Sunday
        if hour < 22:
            return {"open": False, "session": "Weekend", "label": "TUTUP · Weekend"}
        else:
            return {"open": True, "session": "Sydney Open", "label": "BUKA · Sydney"}
    if weekday == 4 and hour >= 22:  # Friday ≥ 22:00 UTC
        return {"open": False, "session": "Weekend", "label": "TUTUP · Weekend"}

    # ── US Index daily CME break 22:00–23:00 UTC ─────────────────────────────
    if pair_type == "Index" and symbol in ("US30", "US500", "USTEC"):
        if hour == 22:
            return {"open": False, "session": "CME Break", "label": "TUTUP · CME Break"}
        # NYSE regular hours (informational only — CME futures nearly 24h)
        if 14 <= hour < 21 or (hour == 14 and minute >= 30):
            session = "NYSE Regular"
        elif hour < 14 or hour >= 21:
            session = "CME Extended"
        else:
            session = "CME Futures"
        return {"open": True, "session": session, "label": f"BUKA · {session}"}

    # ── Forex/Commodity session detection ────────────────────────────────────
    if hour >= 22 or hour < 7:
        session = "Sydney / Tokyo"
    elif 7 <= hour < 8:
        session = "Tokyo / London"
    elif 8 <= hour < 12:
        session = "London"
    elif 12 <= hour < 17:
        session = "London / New York"
    elif 17 <= hour < 21:
        session = "New York"
    else:
        session = "NY Close"

    return {"open": True, "session": session, "label": f"BUKA · {session}"}


async def _get_price_from_redis(symbol: str) -> dict | None:
    """Try to read live MT5 price from hot Redis (gas-redis-hot)."""
    try:
        d = await redis_service.get_market_price(symbol)
        if not d:
            return None
        bid = d.get("bid", 0)
        ask = d.get("ask", 0)
        price = (bid + ask) / 2 if bid and ask else bid or ask
        if not price:
            return None
        ts = d.get("time", 0)
        # MT5 timestamp is broker server time (may have UTC offset).
        # Use Redis TTL as freshness check instead of wall-clock diff.
        # market:{sym} is set with ex=60 by MT5 — if key exists it's fresh (<60s).
        age_s = int(time.time()) - int(ts) if ts else 9999
        # Treat as stale only if > 300s (some brokers report server time ±offset)
        is_stale = age_s > 300
        return {
            "price": price,
            "bid": bid,
            "ask": ask,
            "spread": d.get("spread", 0),
            "open": d.get("open", 0),
            "high": d.get("high", 0),
            "low": d.get("low", 0),
            "prev_close": d.get("prev_close", 0),
            "change": d.get("change", 0),
            "change_pct": d.get("change_pct", 0),
            "source": "mt5_live",
            "age_s": age_s,
            "stale": is_stale,
        }
    except Exception:
        return None


async def _get_crypto_from_binance(symbol: str) -> dict | None:
    """Fetch crypto price from Binance service via path param endpoint."""
    pair_encoded = CRYPTO_BINANCE.get(symbol)
    if not pair_encoded:
        return None
    try:
        data = await fetch_json(
            f"{settings.BINANCE_SERVICE_URL}/ticker/{pair_encoded}",
            timeout=8.0,
        )
        if "error" in data or "detail" in data:
            return None
        price = data.get("last") or data.get("price") or data.get("close")
        if not price:
            return None
        return {
            "price": float(price),
            "bid": data.get("bid", float(price)),
            "ask": data.get("ask", float(price)),
            "open": data.get("open", 0),
            "high": data.get("high", 0),
            "low": data.get("low", 0),
            "change": data.get("change", 0),
            "change_pct": data.get("changePercent", 0),
            "volume": data.get("volume", 0),
            "source": "binance_live",
            "age_s": 0,
            "stale": False,
        }
    except Exception:
        return None


async def _get_stale_price_from_redis(symbol: str) -> dict | None:
    """Get last known (possibly stale) price as fallback."""
    try:
        await redis_service.connect()
        raw = await redis_service.client.get(f"market:last:{symbol.upper()}")
        if not raw:
            return None
        d = json.loads(raw)
        return {**d, "source": "last_known", "stale": True}
    except Exception:
        return None


def _synthetic_cross(base_price: float, quote_price: float, op: str = "div") -> float | None:
    """Compute synthetic cross rate from major pairs."""
    try:
        if not base_price or not quote_price:
            return None
        return round(base_price / quote_price if op == "div" else base_price * quote_price, 5)
    except Exception:
        return None


# Cross rates that can be synthesized from major pairs
_CROSS_MAP = {
    # symbol: (numerator_symbol, denominator_symbol, operation)
    "EURGBP": ("EURUSD", "GBPUSD", "div"),
    "EURJPY": ("EURUSD", "USDJPY", "mul"),   # EUR/JPY = EUR/USD * USD/JPY
    "GBPJPY": ("GBPUSD", "USDJPY", "mul"),
    "AUDJPY": ("AUDUSD", "USDJPY", "mul"),
    "NZDJPY": ("NZDUSD", "USDJPY", "mul"),
    "CADJPY": ("USDCAD", "USDJPY", "rdiv"),  # 1/USDCAD * USDJPY
}


@router.get("/terminal/overview")
async def get_overview(request: Request):
    """
    Returns aggregated dashboard overview with REAL prices.
    Sources: MT5 Redis (hot) → Binance (crypto) → synthetic cross → last-known cache.
    """
    # Pre-fetch all live prices from hot Redis in one pass for synthetic crosses
    live_prices: dict[str, float] = {}
    for sym in ["EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "NZDUSD", "USDCAD"]:
        d = await redis_service.get_market_price(sym)
        if d:
            bid = d.get("bid", 0)
            ask = d.get("ask", 0)
            p = (bid + ask) / 2 if bid and ask else bid or ask
            if p:
                live_prices[sym] = p

    pairs = []
    for meta in PAIR_META:
        sym = meta["symbol"]
        ptype = meta["type"]
        status = _market_status(sym, ptype)

        price_data = None

        # ── 1. Try MT5 Redis (hot) ───────────────────────────────────────────
        price_data = await _get_price_from_redis(sym)

        # ── 2. Crypto fallback: Binance ─────────────────────────────────────
        if not price_data and ptype == "Crypto":
            price_data = await _get_crypto_from_binance(sym)

        # ── 3. Synthetic cross rate from major pairs ─────────────────────────
        if not price_data and sym in _CROSS_MAP:
            a_sym, b_sym, op = _CROSS_MAP[sym]
            a = live_prices.get(a_sym)
            b = live_prices.get(b_sym)
            if op == "rdiv":
                synthetic = _synthetic_cross(1.0 / b if b else None, b, "div") if a and b else None
                # Actually: e.g. CADJPY = USDJPY / USDCAD
                synthetic = round(b / a, 5) if a and b else None
            else:
                synthetic = _synthetic_cross(a, b, op)
            if synthetic:
                price_data = {
                    "price": synthetic,
                    "bid": synthetic,
                    "ask": synthetic,
                    "spread": 0,
                    "change": 0,
                    "change_pct": 0,
                    "source": "synthetic",
                    "stale": False,
                }

        # ── 3. Last-known stale cache ───────────────────────────────────────
        if not price_data:
            price_data = await _get_stale_price_from_redis(sym)

        if price_data:
            # Save to last-known cache (main Redis) for future fallback
            try:
                await redis_service.connect()
                await redis_service.client.set(
                    f"market:last:{sym}",
                    json.dumps({**price_data, "cached_at": int(time.time())}),
                    ex=86400,
                )
            except Exception:
                pass

            pairs.append({
                **meta,
                "price": price_data.get("price"),
                "bid": price_data.get("bid"),
                "ask": price_data.get("ask"),
                "spread": price_data.get("spread", 0),
                "open_price": price_data.get("open"),
                "high": price_data.get("high"),
                "low": price_data.get("low"),
                "prev_close": price_data.get("prev_close"),
                "change": price_data.get("change", 0),
                "change_pct": price_data.get("change_pct", 0),
                "volume": price_data.get("volume"),
                "source": price_data.get("source", "unknown"),
                "stale": price_data.get("stale", False),
                "market": status,
            })
        else:
            # No price available at all — still show correct market status
            pairs.append({
                **meta,
                "price": None,
                "source": "unavailable",
                "stale": True,
                "no_data": True,
                "market": status,
            })

    # ── Real news from calendar service ─────────────────────────────────────
    news_data = await fetch_json(f"{settings.CALENDAR_NEWS_URL}/news/latest", timeout=5.0)
    if "error" in news_data or not isinstance(news_data, list) or len(news_data) == 0:
        import os as _os, re as _re
        _md = _os.path.join(_os.path.dirname(__file__), "..", "..", "data", "livenews.md")
        news_data = []
        try:
            with open(_md, "r", encoding="utf-8") as _f:
                for _line in _f:
                    _l = _line.strip()
                    if not _l.startswith("- ") or _l.startswith("<!--"):
                        continue
                    _l = _l[2:].strip()
                    _m = _re.match(r"\[(\d{2}:\d{2})\]\s*(.*)", _l)
                    if _m:
                        _parts = [p.strip() for p in _m.group(2).split("|")]
                        news_data.append({"title": f"[{_m.group(1)}] {_parts[0]}", "source": _parts[1] if len(_parts) > 1 else "GAS"})
        except Exception:
            pass

    # ── Real macro from fundamental service ─────────────────────────────────
    macro_data = await fetch_json(
        f"{settings.FUNDAMENTAL_DATA_URL}/fundamental/macro", timeout=5.0
    )
    if "error" in macro_data or not isinstance(macro_data, list):
        macro_data = []

    # ── Real signal from signal service ─────────────────────────────────────
    signal_data = await fetch_json(
        f"{settings.SIGNAL_SERVICE_URL}/signal/latest?pair=XAUUSD", timeout=5.0
    )
    if "error" in signal_data:
        signal_data = None  # No fake signals

    # ── Real AI analysis from strategy-core ─────────────────────────────────
    ai_data = await fetch_json(
        f"{settings.STRATEGY_CORE_URL}/v1/analysis/briefing", timeout=8.0
    )
    if "error" in ai_data:
        ai_data = None

    now_utc = datetime.now(timezone.utc)
    return {
        "status": "ok",
        "timestamp": int(now_utc.timestamp()),
        "server_time_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
        "pairs": pairs,
        "signal": signal_data,
        "news": news_data if isinstance(news_data, list) else [],
        "macro": macro_data if isinstance(macro_data, list) else [],
        "ai": ai_data,
    }
