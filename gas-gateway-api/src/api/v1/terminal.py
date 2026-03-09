from fastapi import APIRouter, Request, WebSocket
from src.core.proxy_handler import forward_request
from src.config import settings

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_terminal(request: Request, path: str):
    target_url = f"{settings.TERMINAL_BACKEND_URL}/terminal/{path}"
    return await forward_request(request, target_url)
