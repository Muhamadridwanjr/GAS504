from fastapi import APIRouter, Header, HTTPException, Depends
from src.api.models import NotificationRequest
from src.config import settings
from src.lib.logger import logger
from src.workers.tasks import send_notification_task

router = APIRouter()

def verify_api_key(x_api_key: str = Header(None)):
    if settings.internal_api_key and x_api_key != settings.internal_api_key:
        logger.warning(f"Unauthorized API request with key: {x_api_key}")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return x_api_key

@router.post("/notify", status_code=202)
def add_notification(req: NotificationRequest, api_key: str = Depends(verify_api_key)):
    try:
        # Enqueue the Celery task
        # Serialize Pydantic model to dictionary
        task = send_notification_task.delay(req.model_dump())
        return {
            "task_id": task.id,
            "status": "queued"
        }
    except Exception as e:
        logger.error(f"Failed to enqueue notification task: {e}")
        raise HTTPException(status_code=500, detail="Failed to enqueue task")
