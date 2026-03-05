"""Generate embeddings for event summaries."""
from src.lib.logger import get_logger
logger = get_logger(__name__)

async def embed_text(text: str) -> list[float]:
    """Placeholder: return dummy embedding."""
    logger.debug("Embedding text of length %d", len(text))
    return [0.0] * 384
