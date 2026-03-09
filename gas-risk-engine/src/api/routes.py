from fastapi import APIRouter, HTTPException
from src.api.models import RiskEvaluateRequest, RiskEvaluateResponse
from src.core.evaluator import RiskEvaluator
from src.core.exceptions import RiskEngineException
from src.lib.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()
evaluator = RiskEvaluator()

@router.post("/risk/evaluate", response_model=RiskEvaluateResponse)
async def evaluate_risk(request: RiskEvaluateRequest):
    try:
        response = await evaluator.evaluate(request)
        return response
    except RiskEngineException as e:
        logger.error(f"Risk evaluation error: {e.message}")
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "gas-risk-engine"}
