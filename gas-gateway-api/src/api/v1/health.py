from fastapi import APIRouter, Request, Response
from src.config import settings

router = APIRouter()

@router.get("/")
async def health_check():
    """
    Gateway health check
    """
    return {"status": "ok", "service": settings.APP_NAME}
