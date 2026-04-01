from .fetcher import IDX_SYMBOLS, get_multi_quote
from typing import List, Dict
import time

def get_top_gainer(n: int = 10) -> List[Dict]:
    quotes = get_multi_quote(IDX_SYMBOLS[:30])
    valid = [q for q in quotes if q.get("change_pct") is not None and q.get("price")]
    return sorted(valid, key=lambda x: x["change_pct"], reverse=True)[:n]

def get_top_loser(n: int = 10) -> List[Dict]:
    quotes = get_multi_quote(IDX_SYMBOLS[:30])
    valid = [q for q in quotes if q.get("change_pct") is not None and q.get("price")]
    return sorted(valid, key=lambda x: x["change_pct"])[:n]

def get_most_active(n: int = 10) -> List[Dict]:
    quotes = get_multi_quote(IDX_SYMBOLS[:30])
    valid = [q for q in quotes if q.get("volume") is not None and q.get("price")]
    return sorted(valid, key=lambda x: x.get("volume", 0), reverse=True)[:n]

def get_watchlist(symbols: List[str]) -> List[Dict]:
    return get_multi_quote(symbols)
