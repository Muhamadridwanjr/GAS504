"""
Knowledge base document chunker.
Splits raw text into overlapping chunks suitable for embedding.
"""
from __future__ import annotations
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    """
    Split text into overlapping chunks by character count.

    Args:
        text: Input text.
        chunk_size: Max characters per chunk (defaults to CHUNK_SIZE setting × 4).
        overlap: Overlap characters (defaults to CHUNK_OVERLAP × 4).

    Returns:
        List of text chunks.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE * 4     # approx chars for token count
    overlap = overlap or settings.CHUNK_OVERLAP * 4

    if len(text) <= chunk_size:
        return [text.strip()]

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap

    return chunks
