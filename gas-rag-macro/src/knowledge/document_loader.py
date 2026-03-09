"""
Document loader for gas-rag-macro knowledge base.
Loads .txt, .md, and .json files from the knowledge base directory,
chunking them into overlapping segments for indexing.
"""
from __future__ import annotations
import json
import os
from pathlib import Path

from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


def _chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split text into overlapping chunks by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def load_documents(base_path: str | None = None) -> list[dict]:
    """
    Load and chunk documents from the knowledge base directory.

    Args:
        base_path: Override the default knowledge base path from settings.

    Returns:
        List of dicts with 'content' and 'metadata' keys.
    """
    path = Path(base_path or settings.KNOWLEDGE_BASE_PATH)
    if not path.exists():
        logger.warning("document_loader.path_not_found", path=str(path))
        return []

    chunk_size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP
    documents: list[dict] = []

    for file_path in path.rglob("*"):
        if not file_path.is_file():
            continue

        suffix = file_path.suffix.lower()
        try:
            if suffix in (".txt", ".md"):
                text = file_path.read_text(encoding="utf-8")
            elif suffix == ".json":
                data = json.loads(file_path.read_text(encoding="utf-8"))
                text = json.dumps(data, ensure_ascii=False)
            else:
                continue  # skip unsupported file types

            chunks = _chunk_text(text, chunk_size, overlap)
            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    documents.append({
                        "content": chunk,
                        "metadata": {
                            "source": str(file_path),
                            "chunk": i,
                            "filename": file_path.name,
                        },
                    })

        except Exception as exc:
            logger.warning("document_loader.file_error", file=str(file_path), error=str(exc))

    logger.info("document_loader.loaded", doc_count=len(documents), path=str(path))
    return documents
