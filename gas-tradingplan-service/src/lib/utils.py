import hashlib
def hash_key(*parts): return hashlib.sha256(":".join(parts).encode()).hexdigest()[:16]
