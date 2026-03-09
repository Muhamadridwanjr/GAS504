"""
Provider router for gas-rag-macro.
Selects between OpenAI and Vertex AI providers; falls back on error.
"""
from __future__ import annotations

from src.providers.base import BaseProvider
from src.providers.openai import OpenAIProvider
from src.providers.vertex import VertexProvider
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class ProviderRouter:
    """
    Routes generation requests to the appropriate AI provider.
    Falls back to the secondary provider if the preferred one fails.
    """

    def __init__(self):
        self._providers: dict[str, BaseProvider] = {
            "openai": OpenAIProvider(),
            "vertex": VertexProvider(),
        }

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        provider_preference: str = "openai",
        temperature: float = 0.3,
        max_tokens: int = 1200,
    ) -> tuple[str, str, str]:
        """
        Generate text using the preferred provider, with automatic fallback.

        Returns:
            Tuple of (generated_text, provider_name, model_name).
        """
        order = [provider_preference] + [p for p in self._providers if p != provider_preference]

        last_error: Exception | None = None
        for provider_name in order:
            provider = self._providers.get(provider_name)
            if not provider:
                continue
            try:
                logger.info("router.generate.attempt", provider=provider_name)
                text = await provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
                return text, provider.name, provider.model
            except Exception as exc:
                logger.warning("router.generate.failed", provider=provider_name, error=str(exc))
                last_error = exc

        raise RuntimeError(f"All providers failed. Last error: {last_error}")
