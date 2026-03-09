import httpx
from src.config import settings
from src.lib.logger import logger

class BillingClient:
    def __init__(self):
        self.base_url = settings.BILLING_SERVICE_URL
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=5.0)

    async def get_user_allowed_tiers(self, user_id: str, token: str) -> list[str]:
        # Implementation assumes the token is passed and we can fetch user profile or billing info.
        # This is a mock assuming it interacts with `gas-billing-service` directly to determine level.
        try:
            headers = {"Authorization": f"Bearer {token}"}
            # For simplicity, we assume an endpoint exists in billing to check access level, e.g. /levels
            # In a real scenario, this matches gas-billing-service API.
            # Example response mock: {"level": "PREMIUM", "allowed_features": ["signals.premium", "signals.insider"]}
            response = await self.client.get("/levels/me", headers=headers)
            if response.status_code == 200:
                data = response.json()
                level = data.get("level", "FREE")
                
                # Logic map to determine allowed tiers
                allowed = ["insider"]
                if level in ["PREMIUM", "ULTIMATE", "VIP_ELITE"]:
                    allowed.append("premium")
                if level in ["ULTIMATE", "VIP_ELITE"]:
                    allowed.append("ultimate")
                return allowed
            else:
                logger.warning(f"Billing request failed with {response.status_code}. Defaulting to FREE.")
                return ["insider"]
        except Exception as e:
            logger.error(f"Error accessing billing service: {e}")
            return ["insider"] # Fallback

    async def close(self):
        await self.client.aclose()

billing_client = BillingClient()
