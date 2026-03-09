"""
Abstract base class for AI providers in gas-rag-macro.
"""
from __future__ import annotations
from abc import ABC, abstractmethod


class BaseProvider(ABC):
    """Abstract AI provider interface."""

    @abstractmethod
    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> str:
        """
        Generate text from the AI model.

        Args:
            system_prompt: System instruction.
            user_prompt: User content / context.
            temperature: Sampling temperature.
            max_tokens: Maximum tokens in response.

        Returns:
            Generated text string.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name identifier."""

    @property
    @abstractmethod
    def model(self) -> str:
        """Model identifier used by this provider."""
