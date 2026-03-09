"""
Provider router – selects and returns the appropriate AI provider
based on model_preference and routing logic.
"""
from typing import Literal
from functools import lru_cache
from src.config import settings
from src.providers.base import BaseProvider
from src.lib.logger import get_logger

logger = get_logger(__name__)

ProviderName = Literal["vertex", "openai"]


@lru_cache(maxsize=1)
def _get_openai_provider() -> BaseProvider:
    from src.providers.openai import OpenAIProvider
    return OpenAIProvider()


@lru_cache(maxsize=1)
def _get_vertex_provider() -> BaseProvider:
    from src.providers.vertex import VertexProvider
    return VertexProvider()


class ProviderRouter:
    """
    Selects appropriate LLM provider based on:
    1. Explicit model_preference in request
    2. Default provider from config
    3. Availability of API keys
    """

    def get_provider(self, preference: ProviderName | None = None) -> BaseProvider:
        """Return a provider instance for the given preference."""
        chosen = preference or settings.DEFAULT_PROVIDER

        if chosen == "vertex":
            if not settings.VERTEX_PROJECT_ID:
                logger.warning("Vertex AI credentials missing – falling back to OpenAI")
                return _get_openai_provider()
            return _get_vertex_provider()

        if chosen == "openai":
            if not settings.OPENAI_API_KEY:
                logger.warning("OpenAI API key missing")
            return _get_openai_provider()

        # Unknown preference – use default
        logger.warning("Unknown provider preference '%s', using default.", chosen)
        return _get_openai_provider()

    def get_embedding_provider(self, preference: ProviderName | None = None) -> BaseProvider:
        """Return a provider suitable for embedding generation."""
        return self.get_provider(preference)


# Module-level singleton
router = ProviderRouter()
