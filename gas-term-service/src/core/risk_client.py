import httpx
from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import RiskValidationError

class RiskClient:
    async def validate_order(self, user_id: str, order_data: dict) -> dict:
        if not settings.risk_engine_url:
            return {"allowed": True, "recommended_lot": order_data.get("volume")}
            
        url = f"{settings.risk_engine_url}/validate"
        headers = {"X-API-Key": settings.risk_api_key}
        payload = {
            "user_id": user_id,
            "order": order_data
        }
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if not data.get("allowed", False):
                        reason = data.get("reason", "Risk validation failed")
                        raise RiskValidationError(reason)
                    return data
                else:
                    logger.warning(f"Risk engine returned {res.status_code}")
                    return {"allowed": True}
        except RiskValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating risk: {e}")
            return {"allowed": True}

risk_client = RiskClient()
