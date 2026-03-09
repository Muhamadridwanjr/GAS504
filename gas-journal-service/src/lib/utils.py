from datetime import datetime
from uuid import UUID
from decimal import Decimal

def default_json_serializer(obj):
    """Custom serializer for objects not serializable by default json encoder"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")
