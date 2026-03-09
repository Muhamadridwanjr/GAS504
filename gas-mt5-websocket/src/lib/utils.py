import asyncio
from datetime import datetime

def get_now_timestamp() -> int:
    """Returns current UTC timestamp as integer"""
    return int(datetime.utcnow().timestamp())

def format_timestamp(ts: int) -> str:
    """Formats timestamp to readable string"""
    return datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
