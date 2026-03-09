from fastapi import APIRouter, HTTPException
from src.api.models import EvaluateRequest, EvaluateResponse
from src.core.evaluator import evaluate_condition
from src.redis.cache import alert_cache
from src.lib.logger import logger

router = APIRouter(prefix="/internal", tags=["Internal"])


@router.post("/evaluate", response_model=EvaluateResponse)
async def manual_evaluate(body: EvaluateRequest):
    """
    Manual evaluation endpoint (internal use).
    Evaluates an alert condition against provided market data.
    """
    alert_def = await alert_cache.get_cached_alert(str(body.alert_id))
    if not alert_def:
        raise HTTPException(status_code=404, detail="Alert not found in cache")

    condition = alert_def.get("condition", {})
    triggered = evaluate_condition(condition, body.market_data)

    logger.info(f"Manual evaluate alert {body.alert_id}: triggered={triggered}")

    return EvaluateResponse(
        alert_id=body.alert_id,
        triggered=triggered,
        condition=condition,
        market_data=body.market_data,
    )
