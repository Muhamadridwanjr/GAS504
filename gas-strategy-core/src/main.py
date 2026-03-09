from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.core.engine import evaluate

app = FastAPI(title="gas-strategy-core API")

class EvaluationRequest(BaseModel):
    strategy_name: str
    data: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None

@app.get("/health")
def health_check():
    """Healthcheck endpoint for Docker & gas-gateway-api"""
    return {"status": "ok", "message": "gas-strategy-core is running"}

@app.post("/v1/strategy/evaluate")
def evaluate_strategy_endpoint(req: EvaluationRequest):
    """Evaluate a strategy via REST API (optional entrypoint)"""
    try:
        signal = evaluate(req.strategy_name, req.data, req.context)
        return signal
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
