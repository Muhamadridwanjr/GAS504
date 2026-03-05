import hashlib, json
def hash_key(*parts): return hashlib.sha256(":".join(str(p) for p in parts).encode()).hexdigest()[:16]
