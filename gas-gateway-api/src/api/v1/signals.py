from fastapi import APIRouter, Request
from src.core.proxy_handler import forward_request
from src.config import settings

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_signals(request: Request, path: str):
    # If path is empty (e.g. EA calling /api/signal), default to /signals
    target_path = path if path else "signals"
    target_url = f"{settings.SIGNAL_SERVICE_URL}/{target_path}"
    return await forward_request(request, target_url)
