from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from src.api.models import BacktestRequest, BacktestResponse
from src.core.backtest_engine import engine
from src.lib.logger import logger

router = APIRouter()

@router.post("/backtest", response_model=BacktestResponse)
async def run_backtest(req: BacktestRequest):
    try:
        res = await engine.run_backtest(req)
        return res
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Error during backtest: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/backtest/{bt_id}", response_model=Dict[str, Any])
async def get_backtest(bt_id: str):
    # Stub: would normally query DB
    return {"status": "not_implemented"}

@router.delete("/backtest/{bt_id}")
async def delete_backtest(bt_id: str):
    return {"status": "not_implemented"}
