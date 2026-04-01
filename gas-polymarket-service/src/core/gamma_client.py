"""
GAS Polymarket — Market Fetcher + GAS Event Generator.
Combines filtered Polymarket events with GAS-generated trading events.
"""
import httpx
import logging
import re
import hashlib
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from ..config import settings

logger = logging.getLogger("gamma_client")

# ── Pair config ──────────────────────────────────────────────────────────────
PAIRS = {
    "BTC":    {"pair": "BTC/USDT", "category": "crypto",  "name": "Bitcoin"},
    "ETH":    {"pair": "ETH/USDT", "category": "crypto",  "name": "Ethereum"},
    "SOL":    {"pair": "SOL/USDT", "category": "crypto",  "name": "Solana"},
    "BNB":    {"pair": "BNB/USDT", "category": "crypto",  "name": "BNB"},
    "XAUUSD": {"pair": "XAUUSD",   "category": "forex",   "name": "Gold"},
    "EURUSD": {"pair": "EURUSD",   "category": "forex",   "name": "EUR/USD"},
    "GBPUSD": {"pair": "GBPUSD",   "category": "forex",   "name": "GBP/USD"},
    "USDJPY": {"pair": "USDJPY",   "category": "forex",   "name": "USD/JPY"},
    "DXY":    {"pair": "DXY",      "category": "macro",   "name": "DXY Index"},
    "SPX":    {"pair": "SPX500",   "category": "macro",   "name": "S&P 500"},
}

# Reference price levels for GAS-generated events
PAIR_LEVELS = {
    "BTC":    [60000, 65000, 68000, 70000, 72000, 75000, 80000],
    "ETH":    [2800,  3000,  3200,  3500,  4000],
    "SOL":    [120,   140,   160,   180,   200],
    "BNB":    [400,   450,   500,   550,   600],
    "XAUUSD": [2300,  2350,  2400,  2450,  2500, 2550],
    "EURUSD": [1.05,  1.06,  1.07,  1.08,  1.10],
    "GBPUSD": [1.25,  1.26,  1.27,  1.28,  1.30],
    "USDJPY": [148,   150,   152,   154,   156],
    "DXY":    [100,   102,   104,   106,   108],
    "SPX":    [4800,  5000,  5200,  5400,  5600],
}

# ── Trading-relevance filter ──────────────────────────────────────────────────
TRADING_PAIRS_KEYWORDS = [
    "btc", "bitcoin", "eth", "ethereum", "sol", "solana", "bnb", "binance",
    "xrp", "ripple", "gold", "xauusd", "eurusd", "gbpusd", "usdjpy", "dxy",
    "s&p", "spx", "nasdaq", "dow", "crude", "oil", "silver", "forex",
]

PRICE_PATTERN = re.compile(r'\$?\d[\d,]*\.?\d*[kK]?')
PERCENT_PATTERN = re.compile(r'\d+\.?\d*\s*%')

NON_TRADING_KEYWORDS = [
    "election", "president", "congress", "senate", "vote", "trump", "biden",
    "harris", "republican", "democrat", "war", "nato", "invasion", "arrest",
    "nba", "nfl", "soccer", "fifa", "world cup", "oscar", "grammy", "celebrity",
    "marriage", "divorce", "born", "die", "death", "murder", "trial",
    "vaccine", "pandemic", "covid", "cancer", "surgery",
]

def is_trading_relevant(question: str) -> bool:
    """Return True only for trading-relevant prediction events."""
    q = question.lower()
    # Hard reject: non-trading keywords
    for kw in NON_TRADING_KEYWORDS:
        if kw in q:
            return False
    # Accept: has a tradeable pair keyword
    has_pair = any(kw in q for kw in TRADING_PAIRS_KEYWORDS)
    # Accept: has a price level or % movement
    has_number = bool(PRICE_PATTERN.search(question)) or bool(PERCENT_PATTERN.search(question))
    return has_pair and has_number

def detect_category(question: str) -> str:
    q = question.lower()
    if any(k in q for k in ["btc","bitcoin","eth","ethereum","sol","bnb","crypto","altcoin"]):
        return "crypto"
    if any(k in q for k in ["gold","xauusd","eurusd","gbpusd","usdjpy","forex","fx"]):
        return "forex"
    if any(k in q for k in ["dxy","s&p","spx","nasdaq","interest rate","inflation","cpi","fed","fomc"]):
        return "macro"
    if any(k in q for k in ["today","4h","24h","intraday","breakout","move","pump","dump"]):
        return "intraday"
    if any(k in q for k in ["bos","break of structure","liquidity","sweep","fvg","support","resistance"]):
        return "technical"
    return "crypto"

def map_to_pair(question: str) -> Optional[str]:
    q = question.lower()
    for key, cfg in PAIRS.items():
        if key.lower() in q or cfg["name"].lower() in q:
            return cfg["pair"]
    return None

# ── GAS Event Generator ──────────────────────────────────────────────────────
EVENT_TEMPLATES = [
    # Price Target events
    ("{name} above {level} by end of day?",         "price_target",  "intraday"),
    ("{name} reaches {level} this week?",            "price_target",  "crypto"),
    ("Will {name} break {level} today?",             "price_target",  "intraday"),
    ("{name} holding above {level} at NY close?",    "price_target",  "technical"),
    # % Movement events
    ("{name} up +1.5% in next 4 hours?",             "pct_move",     "intraday"),
    ("{name} up +2% today?",                         "pct_move",     "intraday"),
    ("{name} down -1.5% in next 4 hours?",           "pct_move",     "intraday"),
    ("{name} moves +3% this week?",                  "pct_move",     "crypto"),
    # Structure events
    ("{name} breaks key resistance today?",          "structure",    "technical"),
    ("{name} liquidity sweep before NY session?",    "structure",    "technical"),
    ("{name} BOS confirmed on H4?",                  "structure",    "technical"),
    ("{name} in bullish trend on daily?",            "structure",    "technical"),
    # Time-based events
    ("{name} bullish before London open?",           "time_based",   "intraday"),
    ("{name} closes green today?",                   "time_based",   "intraday"),
    ("{name} pumps during Asian session today?",     "time_based",   "intraday"),
    ("{name} holds weekly open level?",              "time_based",   "technical"),
]

def _stable_yes_price(pair_key: str, template: str, level: str = "") -> float:
    """Generate a deterministic but realistic YES price per event."""
    seed = hashlib.md5(f"{pair_key}{template}{level}{datetime.now().strftime('%Y%m%d')}".encode()).hexdigest()
    n = int(seed[:8], 16) / 0xFFFFFFFF  # 0..1
    # Most prices near 0.45-0.70 (slight bullish bias)
    return round(0.38 + n * 0.40, 4)

def generate_gas_events(
    category_filter: Optional[str] = None,
    max_per_pair: int = 3,
) -> List[Dict[str, Any]]:
    """Generate GAS-native prediction events for all trading pairs."""
    events = []
    now = datetime.now(timezone.utc)
    end_of_day = (now + timedelta(hours=24)).isoformat()
    end_of_week = (now + timedelta(days=7)).isoformat()

    for pair_key, cfg in PAIRS.items():
        cat = cfg["category"]
        if category_filter and category_filter != "all" and cat != category_filter:
            continue

        levels = PAIR_LEVELS.get(pair_key, [])
        count = 0

        for tmpl, event_type, preferred_cat in EVENT_TEMPLATES:
            if count >= max_per_pair:
                break
            # Pick a nearby level if template uses it
            if "{level}" in tmpl:
                if not levels:
                    continue
                # Pick level near middle
                level = levels[len(levels) // 2]
                # Format level: crypto large numbers → k suffix
                if level >= 1000 and cfg["category"] == "crypto":
                    level_str = f"${level // 1000}k" if level % 1000 == 0 else f"${level:,}"
                elif level >= 1000:
                    level_str = f"{level:,}"
                else:
                    level_str = str(level)
                question = tmpl.format(name=cfg["name"], level=level_str)
            else:
                question = tmpl.format(name=cfg["name"], level="")

            yes_price = _stable_yes_price(pair_key, tmpl)
            no_price = round(1.0 - yes_price, 4)
            end = end_of_day if preferred_cat in ("intraday",) else end_of_week

            event_id = f"gas_{pair_key}_{hashlib.md5(question.encode()).hexdigest()[:8]}"
            events.append({
                "event_id": event_id,
                "question": question,
                "category": preferred_cat if not category_filter or category_filter == "all" else cat,
                "yes_price": yes_price,
                "no_price": no_price,
                "volume": 0.0,
                "end_date": end,
                "active": True,
                "pair": cfg["pair"],
                "source": "gas",
                "event_type": event_type,
            })
            count += 1

    return events


async def fetch_markets(
    limit: int = 40,
    category: Optional[str] = None,
    active_only: bool = True,
    search: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Fetch and merge Polymarket (filtered) + GAS-generated events."""

    # 1. Fetch from Gamma API
    params: Dict[str, Any] = {
        "limit": min(limit * 3, 150),  # fetch extra to survive filtering
        "active": "true" if active_only else "false",
        "closed": "false",
        "order": "volume24hr",
        "ascending": "false",
    }
    if search:
        params["search"] = search

    poly_markets: List[Dict[str, Any]] = []
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            resp = await client.get(f"{settings.GAMMA_API_BASE}/markets", params=params)
            resp.raise_for_status()
            data = resp.json()
            raw = data if isinstance(data, list) else data.get("data", data.get("markets", []))

            for m in raw:
                question = m.get("question", m.get("title", ""))
                if not question:
                    continue
                if not is_trading_relevant(question):
                    continue
                cat = detect_category(question)
                if category and category != "all" and cat != category:
                    continue
                yes_price = float(m.get("bestBid",
                    m.get("outcomePrices", [0.5])[0]
                    if isinstance(m.get("outcomePrices"), list) else 0.5) or 0.5)
                poly_markets.append({
                    "event_id": str(m.get("conditionId", m.get("id", ""))),
                    "question": question,
                    "category": cat,
                    "yes_price": round(yes_price, 4),
                    "no_price": round(1.0 - yes_price, 4),
                    "volume": float(m.get("volume24hr", m.get("volume", 0)) or 0),
                    "end_date": m.get("endDate", m.get("endDateIso")),
                    "active": True,
                    "pair": map_to_pair(question),
                    "source": "polymarket",
                    "event_type": "price_target",
                })
        except Exception as e:
            logger.warning(f"Gamma API error: {e}")

    # 2. GAS-generated events
    gas_events = generate_gas_events(
        category_filter=category if category != "all" else None,
        max_per_pair=4,
    )

    # 3. Search filter on GAS events too
    if search:
        q = search.lower()
        gas_events = [e for e in gas_events if q in e["question"].lower() or q in e["pair"].lower()]

    # 4. Merge: Polymarket first, then GAS
    combined = poly_markets + gas_events

    # 5. Cap total
    return combined[:limit]
