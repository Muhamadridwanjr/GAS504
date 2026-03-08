from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from src.config import settings
from src.services.client import fetch_json, get_client
import structlog

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/terminal/ai", tags=["AI Chat"])

class ChatRequest(BaseModel):
    prompt: str
    type: str = "general"
    model_id: Optional[str] = None

@router.post("/chat")
async def ai_chat(request: ChatRequest):
    """Proxy chat request to AI Orchestrator"""
    url = f"{settings.AI_ORCHESTRATOR_URL}/analyze"

    # We pass a default system user id since the terminal backend might not have user auth overhead yet
    headers = {
        "X-User-ID": "terminal-user",
        "Content-Type": "application/json"
    }

    payload = {
        "type": request.type,
        "prompt": request.prompt,
        "context": {"source": "web-terminal"},
        "model_params": {"model_id": request.model_id} if request.model_id else {},
    }
    
    try:
        client = await get_client()
        response = await client.post(url, json=payload, headers=headers, timeout=30.0)
        
        if response.status_code != 200:
            logger.error(f"AI Orchestrator returned status {response.status_code}", response=response.text)
            raise HTTPException(status_code=response.status_code, detail="Failed to communicate with AI Orchestrator")
            
        data = response.json()
        return {"status": "ok", "result": data.get("result", {})}
        
    except Exception as e:
        logger.error("error_calling_ai_orchestrator", error=str(e))
        raise HTTPException(status_code=500, detail="Internal Server Error: AI Service Unavailable")
