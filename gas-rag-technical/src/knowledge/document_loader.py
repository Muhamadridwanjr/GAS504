"""
Document loader – loads text from Markdown, TXT, and JSON files
in the knowledge base directory.
"""
from __future__ import annotations
import os
import json
from typing import Any
from src.config import settings
from src.lib.logger import get_logger

logger = get_logger(__name__)


class Document:
    """Represents a loaded document with content and metadata."""

    def __init__(self, text: str, metadata: dict[str, Any] | None = None) -> None:
        self.text = text
        self.metadata = metadata or {}


def load_documents(base_path: str | None = None) -> list[Document]:
    """
    Recursively load all .txt, .md, and .json documents from the knowledge base.

    Returns:
        List of Document objects.
    """
    base_path = base_path or settings.KNOWLEDGE_BASE_PATH
    documents: list[Document] = []

    if not os.path.exists(base_path):
        logger.warning("Knowledge base path does not exist: %s", base_path)
        return documents

    for root, _, files in os.walk(base_path):
        for fname in files:
            fpath = os.path.join(root, fname)
            ext = os.path.splitext(fname)[1].lower()

            try:
                if ext in (".txt", ".md"):
                    with open(fpath, "r", encoding="utf-8") as f:
                        text = f.read()
                    documents.append(
                        Document(
                            text=text,
                            metadata={
                                "source": fpath,
                                "title": fname,
                                "type": "text",
                            },
                        )
                    )
                elif ext == ".json":
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    # Expect either {"text": "..."} or list of {"text": "...", ...}
                    if isinstance(data, dict):
                        text = data.get("text", data.get("content", json.dumps(data)))
                        documents.append(
                            Document(
                                text=text,
                                metadata={**data.get("metadata", {}), "source": fpath, "title": fname},
                            )
                        )
                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                text = item.get("text", item.get("content", ""))
                                if text:
                                    documents.append(
                                        Document(
                                            text=text,
                                            metadata={**item, "source": fpath},
                                        )
                                    )
            except Exception as exc:  # noqa: BLE001
                logger.warning("Failed to load %s: %s", fpath, exc)

    logger.info("Loaded %d documents from %s", len(documents), base_path)
    return documents
