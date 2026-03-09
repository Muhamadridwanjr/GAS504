from fastapi import APIRouter, Header, HTTPException
from src.api.models import CommandRequest
from src.core.command_parser import parse_command
from src.core.router import dispatch
from src.lib.logger import logger

router = APIRouter()

@router.post("/command")
async def handle_command(
    request: CommandRequest,
    x_user_id: str = Header(None, alias="X-User-ID")
):
    user_id = x_user_id or request.user_id
    if not user_id:
        raise HTTPException(status_code=400, detail="X-User-ID required")

    logger.info(f"[{user_id}] Command: {request.command}")

    try:
        action = parse_command(request.command)
        result = await dispatch(user_id, action)
        return {
            "command": request.command,
            "action": action["type"],
            "result": result
        }
    except Exception as e:
        logger.error(f"Error handling command: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/panels/chart")
async def chart_proxy(symbol: str = "XAUUSD", tf: str = "H1"):
    from src.config import settings
    return {
        "panel": "chart",
        "symbol": symbol,
        "timeframe": tf,
        "data_source": settings.chart_service_url
    }

@router.get("/panels/news")
async def news_proxy(q: str = ""):
    import httpx
    from src.config import settings
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(f"{settings.news_service_url}/news", params={"q": q})
            return res.json()
    except Exception as e:
        return {"error": str(e)}

@router.get("/panels/portfolio")
async def portfolio_proxy(x_user_id: str = Header(None, alias="X-User-ID")):
    import httpx
    from src.config import settings
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            res = await client.get(
                f"{settings.journal_service_url}/trades",
                params={"user_id": x_user_id},
                headers={"X-API-Key": settings.internal_api_key}
            )
            return res.json()
    except Exception as e:
        return {"error": str(e)}
