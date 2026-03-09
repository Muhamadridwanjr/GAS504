import uuid


def generate_uuid() -> str:
    """Generate a new UUIDv4 string."""
    return str(uuid.uuid4())


def paginate(total: int, limit: int, offset: int) -> dict:
    """Build pagination metadata dict."""
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total,
    }
