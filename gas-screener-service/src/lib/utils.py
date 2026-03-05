"""Utility functions for gas-screener-service."""
from __future__ import annotations
import hashlib, json


def hash_key(*parts: str) -> str:
    raw = ":".join(parts)
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def safe_json_loads(raw: str, default=None):
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return default
