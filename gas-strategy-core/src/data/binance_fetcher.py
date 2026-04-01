"""
Fetch OHLCV data from gas-binance-service for crypto pairs.
Used as data source when the requested pair is a crypto symbol.
"""
import httpx
import os
import logging

log = logging.getLogger("gas.binance_fetcher")

BINANCE_SERVICE_URL = os.getenv("BINANCE_SERVICE_URL", "http://gas-binance-service:9612")

# MT5 timeframe format → CCXT/Binance format
TF_MAP = {
    "M1": "1m",  "M5": "5m",  "M15": "15m", "M30": "30m",
    "H1": "1h",  "H4": "4h",  "D1": "1d",   "W1": "1w",
    # passthrough if already in CCXT format
    "1m": "1m",  "5m": "5m",  "15m": "15m", "30m": "30m",
    "1h": "1h",  "4h": "4h",  "1d": "1d",   "1w": "1w",
}

# Known crypto base symbols
_CRYPTO_BASES = {
    "BTC", "ETH", "SOL", "XRP", "BNB", "ADA", "DOGE", "SHIB", "TRX",
    "MATIC", "DOT", "LINK", "UNI", "ATOM", "AVAX", "LTC", "ALGO",
    "NEAR", "FIL", "APE", "ICP", "APT", "ARB", "OP", "INJ", "STX",
    "RNDR", "FET", "GRT", "IMX", "SUI", "SEI", "TIA", "WIF", "PEPE",
    "FLOKI", "WLD", "BLUR", "BONK", "MEME", "BOME", "DEGEN", "TURBO",
    "NEIRO", "POPCAT", "MEW", "BRETT", "PONKE", "GIGA",
}


def is_crypto_pair(symbol: str) -> bool:
    """Return True if symbol is a crypto pair (BTC/USDT, ETH/USDT:USDT, BTCUSDT, etc.)."""
    if "/" in symbol:
        return True
    upper = symbol.upper()
    for base in _CRYPTO_BASES:
        if upper.startswith(base):
            return True
    return False


def normalize_crypto_symbol(symbol: str) -> str:
    """
    Normalize various crypto symbol formats to CCXT standard (BTC/USDT).
    Examples: BTCUSDT → BTC/USDT, ETHUSDT → ETH/USDT, PEPE → PEPE/USDT
    """
    if "/" in symbol:
        return symbol  # already in CCXT format
    upper = symbol.upper()
    for base in sorted(_CRYPTO_BASES, key=len, reverse=True):
        if upper.startswith(base):
            quote = upper[len(base):]
            if quote in ("USDT", "USDC", "BTC", "ETH", "BNB", "USD"):
                return f"{base}/{quote}"
            elif quote == "":
                # No quote suffix — default to /USDT
                return f"{base}/USDT"
    return symbol


async def get_ohlc_from_binance(symbol: str, timeframe: str, limit: int = 200) -> list:
    """
    Fetch OHLCV candles from gas-binance-service.
    Returns list of candle dicts in GAS standard format (same as MT5 Redis format).
    """
    ccxt_tf = TF_MAP.get(timeframe, timeframe.lower())
    normalized = normalize_crypto_symbol(symbol)

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(
                f"{BINANCE_SERVICE_URL}/ohlcv",
                params={"symbol": normalized, "timeframe": ccxt_tf, "limit": limit},
            )
            resp.raise_for_status()
            data = resp.json()
            candles = data.get("data", [])

            result = []
            for c in candles:
                t = c.get("time", 0)
                if t > 1_000_000_000_000:  # milliseconds → seconds
                    t = int(t / 1000)
                result.append({
                    "time": int(t),
                    "open":   float(c.get("open",   0)),
                    "high":   float(c.get("high",   0)),
                    "low":    float(c.get("low",    0)),
                    "close":  float(c.get("close",  0)),
                    "volume": float(c.get("volume", 0)),
                })
            log.info(f"Binance OHLCV fetched: {normalized}/{ccxt_tf} — {len(result)} candles")
            return result

    except Exception as e:
        log.error(f"Binance OHLCV fetch failed for {normalized}/{ccxt_tf}: {e}")
        return []


async def get_latest_price_binance(symbol: str) -> float:
    """Get latest price for a crypto pair from binance-service ticker."""
    normalized = normalize_crypto_symbol(symbol)
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            from urllib.parse import quote
            resp = await client.get(
                f"{BINANCE_SERVICE_URL}/ticker/{quote(normalized, safe='')}",
            )
            resp.raise_for_status()
            data = resp.json()
            return float(data.get("last", 0))
    except Exception as e:
        log.error(f"Binance ticker fetch failed for {normalized}: {e}")
        return 0.0
