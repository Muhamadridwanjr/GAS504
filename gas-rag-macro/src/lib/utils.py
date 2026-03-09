"""
Shared utilities for gas-rag-macro.
"""
from __future__ import annotations
import json
import time


def now_ts() -> int:
    """Return current UTC unix timestamp (seconds)."""
    return int(time.time())


def safe_json_parse(text: str) -> dict | None:
    """Attempt to parse JSON from a string; returns None on failure."""
    try:
        # Try direct parse first
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to extract JSON block from markdown
    import re
    block = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if block:
        try:
            return json.loads(block.group(1))
        except json.JSONDecodeError:
            pass
    return None


def truncate_text(text: str, max_chars: int = 2000) -> str:
    """Truncate text to max_chars, appending ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "…"


def build_cache_key(*parts: str) -> str:
    """Build a Redis cache key from string parts."""
    return ":".join(["gas-rag-macro"] + list(parts))
