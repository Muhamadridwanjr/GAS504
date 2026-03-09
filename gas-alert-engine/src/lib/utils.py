from datetime import datetime
from uuid import UUID

def default_json_serializer(obj):
    """Custom serializer for objects not serializable by default json encoder"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not serializable")
