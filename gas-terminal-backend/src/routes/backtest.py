"""
/terminal/backtest – Proxy for gas-quant-backtester.
POST /terminal/backtest        – Run a new backtest
GET  /terminal/backtest/{id}   – Get backtest result
DELETE /terminal/backtest/{id} – Delete backtest
"""
from fastapi import APIRouter
from src.config import settings
from src.services.client import fetch_json

router = APIRouter()


@router.post("/terminal/backtest")
async def run_backtest(body: dict):
    """
    Submit a backtest job.
    body: {symbol, timeframe, strategy, start_date, end_date, ...}
    """
    data = await fetch_json(
        f"{settings.BACKTESTER_URL}/backtest",
        method="POST",
        json_body=body,
        timeout=60.0,
    )
    if "error" in data:
        return {"status": "unavailable", "message": "Backtester sedang tidak tersedia."}
    return data


@router.get("/terminal/backtest/{bt_id}")
async def get_backtest(bt_id: str):
    data = await fetch_json(f"{settings.BACKTESTER_URL}/backtest/{bt_id}", timeout=30.0)
    return data


@router.delete("/terminal/backtest/{bt_id}")
async def delete_backtest(bt_id: str):
    data = await fetch_json(
        f"{settings.BACKTESTER_URL}/backtest/{bt_id}",
        method="DELETE",
        timeout=8.0,
    )
    return data
