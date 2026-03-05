"""Utility functions."""
import hashlib, json
def hash_key(*parts: str) -> str:
    return hashlib.sha256(":".join(parts).encode()).hexdigest()[:16]
def safe_json_loads(raw, default=None):
    try: return json.loads(raw)
    except: return default
