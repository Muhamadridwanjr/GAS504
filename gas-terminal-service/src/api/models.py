from pydantic import BaseModel
from typing import Optional

class CommandRequest(BaseModel):
    user_id: str
    command: str
    panel: Optional[str] = "terminal"
