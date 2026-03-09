from typing import Dict, Any
from src.models.base import BaseModelClient
from src.models.technical import TechnicalModelClient
from src.models.macro import MacroModelClient
from src.models.general import GeneralModelClient
from src.core.exceptions import ModelNotFoundError
from src.lib.logger import setup_logger

logger = setup_logger(__name__)

class ModelRouter:
    """Manajer klien model untuk mendistribusikan request ke module AI yang tepat."""
    
    def __init__(self):
        self.clients: Dict[str, BaseModelClient] = {
            "technical": TechnicalModelClient(),
            "macro": MacroModelClient(),
            "general": GeneralModelClient(),
        }

    def get_client(self, model_type: str) -> BaseModelClient:
        client = self.clients.get(model_type.lower())
        if not client:
            error_msg = f"Model type '{model_type}' not found or unsupported."
            logger.error(error_msg)
            raise ModelNotFoundError(error_msg)
        return client

router = ModelRouter()
