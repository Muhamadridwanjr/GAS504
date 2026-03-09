from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModelClient(ABC):
    """Abstract base class untuk semua model AI."""
    
    @abstractmethod
    async def generate(self, prompt: str, params: Dict[str, Any] = None) -> str:
        """
        Menjalankan prompt ke model dan mengembalikan hasil dalam bentuk string.
        """
        pass
