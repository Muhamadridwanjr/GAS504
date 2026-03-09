from typing import Optional, List, Dict, Any
import httpx
from src.config import settings
from src.lib.logger import logger


class SignalClient:
    """HTTP client for communicating with gas-signal-service."""

    BASE_URL: str = settings.SIGNAL_SERVICE_URL
    API_KEY: str = settings.SIGNAL_SERVICE_API_KEY

    async def create_insider_signal(self, user_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call gas-signal-service to create an insider signal.
        Returns the created signal data including its ID.
        """
        headers = {"X-API-Key": self.API_KEY, "X-User-ID": user_id}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.BASE_URL}/internal/signals",
                    json={**payload, "tier": "insider", "source": f"user:{user_id}"},
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Signal service HTTP error: {e.response.status_code} – {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Signal service request error: {e}")
            raise

    async def get_insider_signals(
        self,
        user_ids: List[str],
        limit: int = 20,
        offset: int = 0,
        from_ts: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Fetch insider signals from gas-signal-service for a list of user IDs.
        Used for building the social feed.
        """
        headers = {"X-API-Key": self.API_KEY}
        params: Dict[str, Any] = {
            "users": ",".join(user_ids),
            "tier": "insider",
            "limit": limit,
            "offset": offset,
        }
        if from_ts:
            params["from"] = from_ts
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.BASE_URL}/internal/signals",
                    params=params,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Signal service error: {e.response.status_code}")
            return {"total": 0, "data": []}
        except httpx.RequestError as e:
            logger.error(f"Signal service unavailable: {e}")
            return {"total": 0, "data": []}


signal_client = SignalClient()
