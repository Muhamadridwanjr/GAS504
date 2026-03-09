"""
Embedding generator – wraps provider embedding calls for the retrieval layer.
"""
from typing import Any
from src.providers.router import ProviderRouter
from src.lib.logger import get_logger

logger = get_logger(__name__)
_router = ProviderRouter()


async def get_embedding(
    text: str,
    provider_preference: str | None = None,
) -> list[float]:
    """Generate an embedding vector for the given text."""
    provider = _router.get_embedding_provider(provider_preference)  # type: ignore[arg-type]
    logger.debug("Embedding via %s", provider.provider_name)
    return await provider.get_embedding(text)
