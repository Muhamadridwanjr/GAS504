from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class NotificationRequest(BaseModel):
    user_id: str
    channels: List[str] # e.g. ["telegram", "web", "email"]
    title: str
    message: str
    data: Optional[Dict[str, Any]] = None
    priority: Optional[str] = "medium"
    template: Optional[str] = None
