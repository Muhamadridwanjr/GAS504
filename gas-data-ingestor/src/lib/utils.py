"""
Utility functions for gas-data-ingestor.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone


def unix_now() -> int:
    """Return current UNIX timestamp."""
    return int(datetime.now(timezone.utc).timestamp())


def hash_key(*parts: str) -> str:
    """Create a short hash key from parts."""
    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def safe_json_loads(raw: str, default=None):
    """Safely parse JSON string."""
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default
