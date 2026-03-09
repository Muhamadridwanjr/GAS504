# Utility functions can be added here as needed.
from datetime import datetime, timezone

def get_current_utc_time() -> str:
    """Returns the current UTC time as an ISO formatted string."""
    return datetime.now(tz=timezone.utc).isoformat()
