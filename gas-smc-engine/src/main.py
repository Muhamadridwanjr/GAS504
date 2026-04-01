"""
gas-smc-engine — Smart Money Concept (SMC) Analysis Engine
Accepts raw OHLCV candles, returns full SMC analysis:
  Market Structure, Order Blocks, FVGs, Liquidity, Entry Triggers, Time Context.
"""
from fastapi import FastAPI, HTTPException
from src.models.schemas  import DetectRequest, DetectResponse
from src.mtf.orchestrator import Orchestrator

app = FastAPI(
    title="GAS SMC Engine",
    version="2.0.0",
    description="Real SMC analysis: BOS/CHoCH, Order Blocks, FVG, Liquidity, OTE, Kill Zones",
)

orchestrator = Orchestrator()


@app.get("/health")
def health_check():
    return {
        "status":  "ok",
        "service": "gas-smc-engine",
        "version": "2.0.0",
        "features": ["market_structure", "order_blocks", "fvg", "liquidity", "ote", "kill_zones", "amd"],
    }


@app.post("/detect", response_model=DetectResponse)
def detect_smc(request: DetectRequest):
    """
    Run full SMC analysis on provided OHLCV candles.

    Request body:
      - symbol    : e.g. "XAUUSD", "BTC/USDT", "EURUSD"
      - timeframe : e.g. "H1", "H4", "M15"
      - candles   : list of {time, open, high, low, close, volume}
      - options   : {trading_style: scalping|intraday|swing}

    Returns: full SMC analysis including BOS, CHoCH, OBs, FVGs, liquidity pools,
             OTE zone, kill zone status, AMD phase, and confluence signal.
    """
    if not request.candles or len(request.candles) < 20:
        raise HTTPException(
            status_code=422,
            detail=f"Need at least 20 candles for SMC analysis. Got {len(request.candles)}."
        )

    try:
        result = orchestrator.analyze(request.dict())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SMC analysis failed: {str(e)}")
