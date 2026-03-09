import httpx
from src.config import settings
from src.lib.logger import logger
from src.core.exceptions import QuotaExceededError

class BillingClient:
    async def check_and_deduct_quota(self, user_id: str, action: str = "trade") -> bool:
        if not settings.billing_service_url:
            return True
            
        url = f"{settings.billing_service_url}/quota/check"
        headers = {"X-API-Key": settings.billing_api_key}
        payload = {
            "user_id": user_id,
            "action": action
        }
        
        try:
            async with httpx.AsyncClient() as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    if data.get("allowed", False):
                        return True
                    else:
                        raise QuotaExceededError("Insufficient quota to place order")
                else:
                    logger.warning(f"Billing service returned {res.status_code}")
                    # fail-open or fail-closed based on policy. Assume fail-open for now if service error
                    return True
        except QuotaExceededError:
            raise
        except Exception as e:
            logger.error(f"Error checking billing quota: {e}")
            return True # fail-open

billing_client = BillingClient()
