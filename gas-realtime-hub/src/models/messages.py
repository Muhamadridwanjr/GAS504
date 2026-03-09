from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class IncomingMessage(BaseModel):
    type: str # 'subscribe', 'unsubscribe', 'ping'
    channels: Optional[List[str]] = None

class OutgoingMessage(BaseModel):
    type: str # 'data', 'error', 'pong'
    channel: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    message: Optional[str] = None
