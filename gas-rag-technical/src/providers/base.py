"""Abstract base class for AI providers."""
from abc import ABC, abstractmethod
from typing import Any


class BaseProvider(ABC):
    """
    All LLM providers must implement this interface.
    """

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        params: dict[str, Any] | None = None,
    ) -> str:
        """
        Generate a completion from the provider.

        Args:
            system_prompt: System-level instructions.
            user_prompt: User query / context payload.
            params: Optional override parameters (temperature, max_tokens, etc.)

        Returns:
            Raw text response from the model.
        """

    @abstractmethod
    async def get_embedding(self, text: str) -> list[float]:
        """Generate a text embedding vector."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier string."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the model name currently in use."""
