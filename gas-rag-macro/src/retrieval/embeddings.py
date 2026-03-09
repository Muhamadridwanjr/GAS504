"""
Retrieval embeddings for gas-rag-macro.
Generates text embeddings using OpenAI or Vertex AI.
"""
from __future__ import annotations

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


async def embed_texts(texts: list[str], provider: str = "openai") -> list[list[float]]:
    """
    Generate embeddings for a list of texts.

    Args:
        texts: List of text strings to embed.
        provider: 'openai' or 'vertex'.

    Returns:
        List of embedding vectors.
    """
    if provider == "openai" and settings.OPENAI_API_KEY:
        return await _openai_embed(texts)
    logger.warning("embeddings.provider_unavailable", provider=provider)
    return []


async def _openai_embed(texts: list[str]) -> list[list[float]]:
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    try:
        response = await client.embeddings.create(
            model=settings.OPENAI_EMBEDDING_MODEL,
            input=texts,
        )
        return [item.embedding for item in response.data]
    except Exception as exc:
        logger.error("embeddings.openai.error", error=str(exc))
        return []
