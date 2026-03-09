from fastapi import APIRouter, Request
from src.core.proxy_handler import forward_request
from src.config import settings

router = APIRouter()

@router.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_risk_engine(request: Request, path: str):
    target_url = f"{settings.RISK_ENGINE_URL}/{path}"
    return await forward_request(request, target_url)
