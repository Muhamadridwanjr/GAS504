from fastapi import APIRouter, Depends
from ...core.dependencies import get_current_user
from ...core.http_client import http_client
from ...config import settings
import asyncio

router = APIRouter(tags=["Dashboard"], dependencies=[Depends(get_current_user)])

@router.get("/summary")
async def get_dashboard_summary(user_id: str = Depends(get_current_user)):
    return {
        "summary": "This is the dashboard summary",
        "user_id": user_id
    }

@router.get("/full")
async def get_dashboard_full(user_id: str = Depends(get_current_user)):
    # Aggregating data from multiple services concurrently
    headers = {"X-User-ID": user_id}
    
    # We will simulate the HTTP calls to internal services
    async def fetch_service_data(url: str, default: dict):
        try:
            # We would use http_client here:
            # return await http_client.get(url, headers=headers)
            return default
        except Exception:
            return default

    # Mocking concurrent calls for now (until actual services are guaranteed reachable during dev)
    user_task = fetch_service_data(f"{settings.USER_SERVICE_URL}/profiles/me", {"name": "User", "avatar": "placeholder.jpg"})
    billing_task = fetch_service_data(f"{settings.BILLING_SERVICE_URL}/billing/status", {"plan": "ULTIMATE", "quota": 5, "level": "VIP"})
    journal_task = fetch_service_data(f"{settings.JOURNAL_SERVICE_URL}/journal/stats", {"total_trades": 42, "winrate": 68.5, "profit": 1250.75})
    signal_task = fetch_service_data(f"{settings.SIGNAL_SERVICE_URL}/signals/latest?limit=5", [{"pair": "EURUSD", "action": "BUY"}])
    tcg_task = fetch_service_data(f"{settings.TCG_SERVICE_URL}/tcg/profile", {"cards_count": 12, "equipped": "Dragon Card"})
    notif_task = fetch_service_data(f"{settings.NOTIFICATION_SERVICE_URL}/notifications", [{"title": "Welcome", "read": False}])

    results = await asyncio.gather(
        user_task, billing_task, journal_task, signal_task, tcg_task, notif_task, return_exceptions=True
    )

    return {
        "user": results[0] if not isinstance(results[0], Exception) else {},
        "billing": results[1] if not isinstance(results[1], Exception) else {},
        "journal": dict(results[2]) if not isinstance(results[2], Exception) else {}, # explicit cast if mock dict
        "recent_signals": results[3] if not isinstance(results[3], Exception) else [],
        "tcg": results[4] if not isinstance(results[4], Exception) else {},
        "notifications": results[5] if not isinstance(results[5], Exception) else []
    }
