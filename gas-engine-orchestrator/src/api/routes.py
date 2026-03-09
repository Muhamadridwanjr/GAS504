from fastapi import APIRouter
import time
import random
from typing import List
from .models import AnalyzeRequest, AnalyzeResponse, SignalRequest, SignalResponse, StrategyDetail, HealthResponse
from src.lib.logger import log
from src.lib.config import settings
import httpx

router = APIRouter()

@router.get("/health", response_model=HealthResponse)
async def health_check():
    return {"status": "ok"}

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_market(request: AnalyzeRequest):
    log.info(f"Received logic execution for testing symbol {request.symbol} on {request.timeframe}")
    current_time = int(time.time())
    result = {
        "symbol": request.symbol,
        "timeframe": request.timeframe,
        "timestamp": current_time,
        "indicators": {
            "RSI": 45.2,
            "MA": [{"period": 20, "value": 2000.5}],
            "Requested": request.indicators
        },
        "smc": {
            "order_blocks": [{"type": "bullish", "time": current_time - 100, "price": 1995.0}],
            "fvgs": [{"direction": "bullish", "start": 1995.5, "end": 1997.2}],
            "Requested": request.smc
        },
        "signal": "NEUTRAL"
    }
    log.info(f"Analysis complete for {request.symbol}")
    return result

async def _simulate_gas_ecosystem(pair: str) -> dict:
    """Simulates the 30+ microservices orchestration pipeline with AI validation."""
    # Market Phase & Regime Simulator
    is_volatile = random.random() > 0.7
    phase = "EXPANSION" if random.random() > 0.5 else "ACCUMULATION"
    
    # Fundamental & Macro Integration
    macro_bias = "STAGFLASI / RISK-OFF"
    
    # Technical & SMC
    sig_type = "BUY" if random.random() > 0.45 else "SELL"
    
    # Risk Engine Validator
    confidence_score = random.randint(60, 95)
    
    # --- REAL AI INTEGRATION ---
    ai_level = None
    try:
        async with httpx.AsyncClient() as client:
            ai_resp = await client.post(
                f"{settings.ai_orchestrator_url}/analyze",
                json={
                    "type": "technical",
                    "prompt": f"Analisa setup {sig_type} untuk {pair}. Berikan keputusan WAIT atau ACTION.",
                    "context": {"pair": pair, "source": "engine-orchestrator"}
                },
                headers={"X-User-ID": "engine-system"},
                timeout=15.0
            )
            if ai_resp.status_code == 200:
                ai_data = ai_resp.json()
                ai_text = ai_data.get("result", {}).get("summary", "").upper()
                if "WAIT" in ai_text: ai_level = "WAIT"
                elif "HOT" in ai_text or "ACTION" in ai_text: ai_level = "HOT"
                elif "VALID" in ai_text: ai_level = "VALID"
    except Exception as e:
        log.error(f"Falled to reach AI Orchestrator: {e}")

    # Determine the Level based on AI or Fallback
    if ai_level:
        level = ai_level
    else:
        # Fallback simulation
        if confidence_score < 75 or is_volatile:
            level = "WAIT"
        elif confidence_score > 88:
            level = "HOT"
        else:
            level = "VALID"

    base_prices = {
        "XAUUSD": (2034.50, 2), "BTCUSD": (64230.15, 2), "NVDA": (176.32, 2),
        "EURUSD": (1.0854, 4), "TSLA": (247.10, 2), "USDJPY": (149.85, 2),
    }
    base, prec = base_prices.get(pair, (100.0, 2))
    entry = round(base + (random.random() - 0.5) * base * 0.005, prec)

    return {
        "id": f"orchestrated-sig-{random.randint(1000, 9999)}",
        "pair": pair,
        "type": sig_type,
        "grade": "A+" if confidence_score > 90 else "A" if confidence_score > 80 else "B",
        "level": level,
        "entry": str(entry),
        "sl": str(round(entry * (0.985 if sig_type == "BUY" else 1.015), prec)),
        "tp1": str(round(entry * (1.015 if sig_type == "BUY" else 0.985), prec)),
        "tp2": str(round(entry * (1.030 if sig_type == "BUY" else 0.970), prec)),
        "confidence": confidence_score // 10,  # Convert to 1-10 scale for UI
        "rr": "1:3",
        "orchestration_metadata": {
            "phase": phase,
            "macro_bias": macro_bias,
            "risk_approved": not is_volatile,
            "ai_validated": ai_level is not None
        }
    }

@router.get("/signal/orchestrated")
async def get_orchestrated_signal(pair: str):
    """Specific endpoint for Terminal Proxy to get a full ecosystem simulated signal"""
    log.info(f"Orchestrating full ecosystem pipeline for {pair}")
    data = await _simulate_gas_ecosystem(pair)
    return {"status": "ok", "signal": data}

@router.post("/signal", response_model=SignalResponse)
async def request_signal(request: SignalRequest):
    data = await _simulate_gas_ecosystem(request.symbol)
    return {
        "symbol": request.symbol,
        "signal": data["type"],
        "metadata": data["orchestration_metadata"]
    }

@router.get("/strategies", response_model=List[StrategyDetail])
async def list_strategies():
    return [
        {"name": "gas-smc-engine-v1", "version": "1.0"},
        {"name": "gas-quant-backtester-opt", "version": "1.1"}
    ]
