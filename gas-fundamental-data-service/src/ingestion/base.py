"""Base class for external data sources."""
from abc import ABC, abstractmethod

class BaseSource(ABC):
    @abstractmethod
    async def fetch(self, indicator: str, from_time: int, to_time: int) -> list[dict]:
        ...
