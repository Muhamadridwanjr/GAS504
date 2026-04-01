"""
GAS Terminal Backend – Binance Service Proxy + Crypto Analysis Engine
Proxies crypto market data from gas-binance-service and provides
real technical + SMC analysis from live OHLCV data.
"""
import asyncio
import math
from fastapi import APIRouter, HTTPException, Query, WebSocket, WebSocketDisconnect
from typing import Optional
from src.config import settings
from src.services.client import get_client, fetch_json

router = APIRouter(tags=["Binance"])

# ── Timeframe mapping: frontend → Binance/CCXT ──────────────────────────────
_TF_MAP = {
    "M1": "1m", "M5": "5m", "M15": "15m", "M30": "30m",
    "H1": "1h", "H2": "2h", "H4": "4h", "H6": "6h",
    "H8": "8h", "H12": "12h", "D1": "1d", "W1": "1w",
    # direct pass-through
    "1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m",
    "1h": "1h", "4h": "4h", "1d": "1d",
}

# ── Pure-Python Indicator Engine ─────────────────────────────────────────────

def _ema(prices: list, period: int) -> list:
    if len(prices) < period:
        return []
    k = 2.0 / (period + 1)
    result = [sum(prices[:period]) / period]
    for p in prices[period:]:
        result.append(p * k + result[-1] * (1 - k))
    return result


def _rsi(closes: list, period: int = 14) -> float:
    if len(closes) < period + 2:
        return 50.0
    diffs = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
    gains = [max(d, 0.0) for d in diffs]
    losses = [max(-d, 0.0) for d in diffs]
    avg_g = sum(gains[:period]) / period
    avg_l = sum(losses[:period]) / period
    for i in range(period, len(diffs)):
        avg_g = (avg_g * (period - 1) + gains[i]) / period
        avg_l = (avg_l * (period - 1) + losses[i]) / period
    if avg_l == 0:
        return 100.0
    return round(100.0 - (100.0 / (1 + avg_g / avg_l)), 2)


def _macd(closes: list):
    ema12 = _ema(closes, 12)
    ema26 = _ema(closes, 26)
    if len(ema12) < 10 or len(ema26) < 2:
        return 0.0, 0.0, 0.0
    # ema12 is (26-12)=14 candles longer than ema26 given same input
    offset = len(ema12) - len(ema26)
    macd_line = [ema12[i + offset] - ema26[i] for i in range(len(ema26))]
    signal_line = _ema(macd_line, 9)
    if not signal_line:
        return macd_line[-1], 0.0, macd_line[-1]
    hist = macd_line[-1] - signal_line[-1]
    return macd_line[-1], signal_line[-1], hist


def _bollinger(closes: list, period: int = 20):
    if len(closes) < period:
        return 0.0, 0.0, 0.0
    window = closes[-period:]
    mid = sum(window) / period
    variance = sum((c - mid) ** 2 for c in window) / period
    std = math.sqrt(variance)
    return mid + 2 * std, mid, mid - 2 * std


def _atr(highs: list, lows: list, closes: list, period: int = 14) -> float:
    if len(closes) < period + 1:
        return 0.0
    trs = []
    for i in range(1, len(closes)):
        tr = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )
        trs.append(tr)
    return sum(trs[-period:]) / period


def _swing_points(highs: list, lows: list, lookback: int = 5):
    sh, sl = [], []
    for i in range(lookback, len(highs) - lookback):
        if highs[i] == max(highs[i - lookback: i + lookback + 1]):
            sh.append(highs[i])
        if lows[i] == min(lows[i - lookback: i + lookback + 1]):
            sl.append(lows[i])
    return sh, sl


def _market_structure(sh: list, sl: list) -> str:
    if len(sh) < 2 or len(sl) < 2:
        return "NEUTRAL"
    hh = sh[-1] > sh[-2]
    hl = sl[-1] > sl[-2]
    lh = sh[-1] < sh[-2]
    ll = sl[-1] < sl[-2]
    if hh and hl:
        return "BULLISH"
    if lh and ll:
        return "BEARISH"
    return "NEUTRAL"


def _fmt_price(n: float) -> str:
    if n is None:
        return "N/A"
    if n < 0.01:
        return f"{n:.8f}"
    if n < 1:
        return f"{n:.6f}"
    if n < 100:
        return f"{n:.4f}"
    if n < 10000:
        return f"{n:.2f}"
    return f"{n:,.2f}"


def _analyze_crypto(candles: list, symbol: str, timeframe: str) -> dict:
    """
    Full technical + SMC analysis from OHLCV candle dicts.
    candles: [{"time":…, "open":…, "high":…, "low":…, "close":…, "volume":…}, …]
    """
    if not candles or len(candles) < 50:
        return {"error": "Insufficient candle data", "symbol": symbol, "candles": len(candles) if candles else 0}

    opens  = [float(c["open"])   for c in candles]
    highs  = [float(c["high"])   for c in candles]
    lows   = [float(c["low"])    for c in candles]
    closes = [float(c["close"])  for c in candles]
    vols   = [float(c["volume"]) for c in candles]

    price = closes[-1]

    # ── Indicators ──────────────────────────────────────────────────────────
    rsi = _rsi(closes)
    ema20_list  = _ema(closes, 20)
    ema50_list  = _ema(closes, 50)
    ema200_list = _ema(closes, 200) if len(closes) >= 200 else []
    macd_val, macd_sig, macd_hist = _macd(closes)
    bb_up, bb_mid, bb_low = _bollinger(closes)
    atr = _atr(highs, lows, closes)

    e20  = ema20_list[-1]  if ema20_list  else price
    e50  = ema50_list[-1]  if ema50_list  else price
    e200 = ema200_list[-1] if ema200_list else None

    # Volume analysis
    avg_vol = sum(vols[-20:]) / min(len(vols), 20)
    vol_ratio = vols[-1] / avg_vol if avg_vol > 0 else 1.0

    # ── SMC Structure ────────────────────────────────────────────────────────
    sh, sl = _swing_points(highs, lows, lookback=5)
    structure = _market_structure(sh, sl)

    support_levels    = sorted([x for x in sl[-8:] if x < price], reverse=True)[:3]
    resistance_levels = sorted([x for x in sh[-8:] if x > price])[:3]

    nearest_sup = support_levels[0]    if support_levels    else price * 0.99
    nearest_res = resistance_levels[0] if resistance_levels else price * 1.01

    # ── Confluence Scoring ───────────────────────────────────────────────────
    score = 0.0
    max_score = 7.5

    # Market structure (weight 2)
    if structure == "BULLISH":
        score += 2.0
    elif structure == "BEARISH":
        score -= 2.0

    # EMA stack (weight 1.5)
    if price > e20 > e50:
        score += 1.5
    elif price < e20 < e50:
        score -= 1.5
    elif price > e20:
        score += 0.5
    elif price < e20:
        score -= 0.5

    # EMA200 (weight 1)
    if e200:
        max_score += 1.0
        if price > e200:
            score += 1.0
        else:
            score -= 1.0

    # RSI (weight 1)
    if rsi > 60:
        score += 1.0
    elif rsi < 40:
        score -= 1.0
    elif rsi > 55:
        score += 0.5
    elif rsi < 45:
        score -= 0.5

    # MACD (weight 1)
    if macd_val > macd_sig and macd_hist > 0:
        score += 1.0
    elif macd_val < macd_sig and macd_hist < 0:
        score -= 1.0

    # Bollinger position (weight 0.5)
    if bb_up > bb_low:
        bb_pct = (price - bb_low) / (bb_up - bb_low)
        if bb_pct > 0.5:
            score += 0.5
        else:
            score -= 0.5

    # Volume confirmation (weight 0.5)
    if vol_ratio > 1.3:
        score += 0.5 if score > 0 else -0.5

    # ── Signal Generation ────────────────────────────────────────────────────
    # Confidence = signal strength (absolute score / max), not directional
    strength = abs(score) / max_score  # 0..1
    confidence = int(min(max(strength * 100, 25), 93))

    if score >= 2.5:
        bias, signal = "BULLISH", "BUY"
    elif score <= -2.5:
        bias, signal = "BEARISH", "SELL"
    else:
        bias, signal = "NEUTRAL", "HOLD"
        confidence = int(min(max(confidence, 30), 50))  # HOLD: moderate confidence

    # ── Entry / SL / TP ──────────────────────────────────────────────────────
    entry = price
    if signal == "BUY":
        sl_price = max(nearest_sup - atr * 0.5, price - atr * 1.5)
        tp1 = nearest_res
        tp2 = nearest_res + (nearest_res - entry) * 0.8
    elif signal == "SELL":
        sl_price = min(nearest_res + atr * 0.5, price + atr * 1.5)
        tp1 = nearest_sup
        tp2 = nearest_sup - (entry - nearest_sup) * 0.8
    else:
        sl_price = price - atr * 1.5
        tp1 = price + atr * 2.0
        tp2 = price + atr * 3.5

    # ── Indicator Labels ─────────────────────────────────────────────────────
    rsi_state = "Overbought" if rsi > 70 else "Oversold" if rsi < 30 else "Bullish" if rsi > 55 else "Bearish" if rsi < 45 else "Neutral"
    ema_state = ("Bullish Stack" if price > e20 > e50 else
                 "Bearish Stack" if price < e20 < e50 else
                 f"Price {'above' if price > e20 else 'below'} EMA20")
    macd_state = f"{'Bullish' if macd_hist > 0 else 'Bearish'} (hist {macd_hist:+.4f})"
    bb_pct_val = (price - bb_low) / (bb_up - bb_low) * 100 if (bb_up - bb_low) > 0 else 50
    bb_state = f"{'Upper' if bb_pct_val > 80 else 'Lower' if bb_pct_val < 20 else 'Middle'} Band ({bb_pct_val:.0f}%)"
    vol_state = f"{'High' if vol_ratio > 1.5 else 'Normal' if vol_ratio > 0.7 else 'Low'} ({vol_ratio:.1f}x avg)"

    structure_map = {
        "BULLISH": "HH-HL (Uptrend)",
        "BEARISH": "LH-LL (Downtrend)",
        "NEUTRAL": "No clear structure",
    }

    # ── Reasoning Text ───────────────────────────────────────────────────────
    reasons = []
    if structure != "NEUTRAL":
        reasons.append(f"Struktur {structure.lower()} ({structure_map[structure]})")
    if price > e20 > e50:
        reasons.append(f"EMA bullish: price({_fmt_price(price)}) > EMA20({_fmt_price(e20)}) > EMA50({_fmt_price(e50)})")
    elif price < e20 < e50:
        reasons.append(f"EMA bearish: price({_fmt_price(price)}) < EMA20({_fmt_price(e20)}) < EMA50({_fmt_price(e50)})")
    if e200:
        reasons.append(f"Price {'di atas' if price > e200 else 'di bawah'} EMA200 ({_fmt_price(e200)})")
    if macd_hist > 0:
        reasons.append(f"MACD bullish crossover (hist +{macd_hist:.4f})")
    elif macd_hist < 0:
        reasons.append(f"MACD bearish (hist {macd_hist:.4f})")
    reasons.append(f"RSI {rsi} — {rsi_state}")
    if vol_ratio > 1.3:
        reasons.append(f"Volume tinggi {vol_ratio:.1f}x rata-rata mengkonfirmasi momentum")
    reasons.append(f"Support: {_fmt_price(nearest_sup)} | Resistance: {_fmt_price(nearest_res)}")
    if atr > 0:
        atr_pct = atr / price * 100
        reasons.append(f"ATR {_fmt_price(atr)} ({atr_pct:.2f}%) — {'high' if atr_pct > 2 else 'moderate'} volatility")

    indicators = {
        "RSI_14":   f"{rsi} ({rsi_state})",
        "EMA_Trend": ema_state,
        "MACD":     macd_state,
        "Bollinger": bb_state,
        "Volume":   vol_state,
    }
    if e200:
        indicators["EMA_200"] = f"{_fmt_price(e200)} ({'Above ✓' if price > e200 else 'Below ✗'})"

    return {
        "symbol": symbol,
        "timeframe": timeframe,
        "price": round(price, 8),
        "bias": bias,
        "signal": signal,
        "confidence": confidence,
        "score": round(score, 2),
        "indicators": indicators,
        "support": round(nearest_sup, 8),
        "resistance": round(nearest_res, 8),
        "entry": round(entry, 8),
        "sl": round(sl_price, 8),
        "tp1": round(tp1, 8),
        "tp2": round(tp2, 8),
        "atr": round(atr, 8),
        "smc": {
            "structure": structure_map.get(structure, structure),
            "trend": structure,
            "swing_highs": len(sh),
            "swing_lows": len(sl),
            "key_support_levels": [round(x, 8) for x in support_levels[:2]],
            "key_resistance_levels": [round(x, 8) for x in resistance_levels[:2]],
        },
        "candles_analyzed": len(candles),
        "reasoning": " | ".join(reasons),
        "source": "binance-ohlcv-realtime",
    }

# Default symbols for WebSocket feed
_WS_DEFAULT_SYMBOLS = "BTC/USDT,ETH/USDT,SOL/USDT,BNB/USDT,XRP/USDT,DOGE/USDT,ADA/USDT,AVAX/USDT,DOT/USDT,MATIC/USDT"


@router.get("/terminal/binance/health")
async def binance_health():
    client = await get_client()
    try:
        resp = await client.get(f"{settings.BINANCE_SERVICE_URL}/health")
        return resp.json()
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@router.get("/terminal/binance/markets")
async def binance_markets():
    """Return all supported Binance markets (spot + usdt_futures + coin_futures)."""
    client = await get_client()
    try:
        resp = await client.get(f"{settings.BINANCE_SERVICE_URL}/markets", timeout=15.0)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Binance service error")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/binance/ticker/{symbol:path}")
async def binance_ticker(symbol: str):
    """Real-time 24h ticker for a symbol (e.g. BTC/USDT or BTC/USDT:USDT)."""
    client = await get_client()
    try:
        resp = await client.get(f"{settings.BINANCE_SERVICE_URL}/ticker/{symbol}", timeout=10.0)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Ticker fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/binance/tickers")
async def binance_tickers(symbols: str = Query(..., description="Comma-separated symbols e.g. BTC/USDT,ETH/USDT")):
    """Fetch multiple tickers at once using the batch endpoint in binance-service."""
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.BINANCE_SERVICE_URL}/tickers",
            params={"symbols": symbols},
            timeout=30.0  # Increased timeout for large batches
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Batch tickers fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/terminal/binance/ohlcv")
async def binance_ohlcv(
    symbol: str = Query(...),
    timeframe: str = Query("1h"),
    limit: Optional[int] = Query(100, le=1000),
    since: Optional[int] = Query(None),
):
    """OHLCV candle data from Binance."""
    client = await get_client()
    try:
        params = {"symbol": symbol, "timeframe": timeframe, "limit": limit}
        if since:
            params["since"] = since
        resp = await client.get(f"{settings.BINANCE_SERVICE_URL}/ohlcv", params=params, timeout=15.0)
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="OHLCV fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@router.websocket("/terminal/ws/binance")
async def binance_tickers_ws(websocket: WebSocket):
    """WebSocket endpoint — pushes live Binance tickers every 2s."""
    await websocket.accept()
    try:
        # Receive optional symbols list from client on connect
        symbols = _WS_DEFAULT_SYMBOLS
        try:
            init = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
            import json as _json
            msg = _json.loads(init)
            if msg.get("symbols"):
                symbols = msg["symbols"]
        except Exception:
            pass

        while True:
            try:
                data = await fetch_json(
                    f"{settings.BINANCE_SERVICE_URL}/tickers",
                    timeout=8.0,
                    params={"symbols": symbols},
                )
                if data and not isinstance(data, dict) or (isinstance(data, dict) and "error" not in data):
                    await websocket.send_json({"type": "tickers", "data": data, "ts": __import__("time").time()})
            except Exception:
                pass
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    except Exception:
        pass


@router.get("/terminal/binance/analyze")
async def binance_analyze(
    symbol: str = Query(..., description="Symbol e.g. BTC/USDT"),
    timeframe: str = Query("H1", description="M15 | H1 | H4 | D1"),
    limit: int = Query(200, ge=50, le=500),
):
    """
    Fetch real OHLCV from Binance, compute RSI/EMA/MACD/BB/ATR + SMC analysis.
    Returns actionable BUY/SELL/HOLD signal with confluence scoring.
    """
    binance_tf = _TF_MAP.get(timeframe.upper(), "1h")
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.BINANCE_SERVICE_URL}/ohlcv",
            params={"symbol": symbol, "timeframe": binance_tf, "limit": limit},
            timeout=20.0,
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"Binance OHLCV error: {resp.text[:200]}")
        payload = resp.json()
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Binance service unavailable: {str(e)}")

    # gas-binance-service returns {"symbol":…, "timeframe":…, "data":[{time,open,high,low,close,volume},…]}
    candles = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(candles, list):
        raise HTTPException(status_code=422, detail="Format OHLCV tidak dikenal dari Binance service")
    if len(candles) < 50:
        raise HTTPException(status_code=422, detail=f"Data tidak cukup: {len(candles)} candles (min 50)")

    result = _analyze_crypto(candles, symbol, timeframe)
    if "error" in result:
        raise HTTPException(status_code=422, detail=result["error"])
    return result


@router.get("/terminal/binance/orderbook/{symbol:path}")
async def binance_orderbook(symbol: str, limit: int = Query(10, le=100)):
    """L2 order book for a symbol."""
    client = await get_client()
    try:
        resp = await client.get(
            f"{settings.BINANCE_SERVICE_URL}/orderbook/{symbol}",
            params={"limit": limit},
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        raise HTTPException(status_code=resp.status_code, detail="Orderbook fetch failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))
