"""
AI Chat endpoint — routes to gas-strategy-core (OpenRouter/DeepSeek).
Supports mentor mode, general chat, and all feature types.
"""
import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/terminal/ai", tags=["AI Chat"])

STRATEGY_CORE_URL = os.getenv("STRATEGY_CORE_URL", "http://gas-strategy-core:7003")


class ChatRequest(BaseModel):
    prompt: str
    type: str = "general"
    model_id: Optional[str] = None
    context: Optional[dict] = None


@router.post("/chat")
async def ai_chat(request: ChatRequest):
    """
    AI chat endpoint. Routes to gas-strategy-core → OpenRouter → DeepSeek.
    Supports types: mentor, general, psychology, strategy, review
    """
    try:
        async with httpx.AsyncClient(timeout=45.0) as client:
            res = await client.post(
                f"{STRATEGY_CORE_URL}/v1/ai/chat",
                json={
                    "prompt": request.prompt,
                    "type": request.type,
                    "context": request.context or {},
                },
            )
            if res.status_code == 200:
                data = res.json()
                return {"status": "ok", "result": data.get("response", data)}
            else:
                logger.error("strategy_core_chat_error", status=res.status_code, body=res.text[:200])
                raise HTTPException(status_code=res.status_code, detail="AI service error")

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI response timeout — coba lagi")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("ai_chat_error", error=str(e))
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {str(e)}")
