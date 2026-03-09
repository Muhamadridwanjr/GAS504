from fastapi import APIRouter
from typing import Dict, Any, List
from src.api.models import SignalRequest, SignalResponse, PairConfig
from src.core.engine import engine
from src.core.pair_manager import pair_manager

router = APIRouter()

@router.get("/pairs")
async def get_pairs():
    # Helper to return state of default pairs
    res = []
    for pair_symbols in pair_manager.pairs:
        pair_name = f"{pair_symbols[0]}_{pair_symbols[1]}"
        params = await pair_manager.get_pair_params(pair_name)
        if params:
            res.append(params)
    return res

@router.post("/signal", response_model=SignalResponse)
async def get_signal(req: SignalRequest):
    result = await engine.generate_signal(req.pair, req.lookback, req.threshold)
    return SignalResponse(**result)

@router.post("/signal/batch", response_model=Dict[str, Any])
async def get_signal_batch(req: Dict[str, List[str]]):
    pairs = req.get("pairs", [])
    results = {}
    for p in pairs:
        try:
            res = await engine.generate_signal(p)
            results[p] = res
        except Exception as e:
            results[p] = {"error": str(e)}
    return results

@router.post("/pairs/add")
async def add_pair(req: PairConfig):
    # Update cache explicitly
    params = await pair_manager.update_pair(req.pair, req.symbol_x, req.symbol_y)
    return {"status": "success", "params": params}
