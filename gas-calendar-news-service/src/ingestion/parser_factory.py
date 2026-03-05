"""Factory for different calendar data parsers."""
from src.ingestion.ecocal_worker import fetch_calendar_events

PARSERS = {"ecocal": fetch_calendar_events}

def get_parser(name: str = "ecocal"):
    return PARSERS.get(name, fetch_calendar_events)
