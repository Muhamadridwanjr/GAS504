"""
Command parser: converts raw text command strings into structured action dictionaries.

Supported commands:
  TRADING:
    /buy SYMBOL LOT [sl:X] [tp:Y]
    /sell SYMBOL LOT [sl:X] [tp:Y]
    /close ORDER_ID
    /portfolio
    /risk

  CHARTS:
    /chart SYMBOL [TIMEFRAME]
    @smc SYMBOL

  NEWS & MACRO:
    @news [keyword]
    @macro [query]

  RESEARCH & AI:
    @research [query]
    @fundamental [query]
    @pattern SYMBOL
    @quant SYMBOL
    @backtest SYMBOL [strategy]
    @ai "question"

  COLLABORATION:
    /share MESSAGE

  EDUCATION:
    @learn [topic]

  META:
    /help
"""

def parse_command(raw: str) -> dict:
    raw = raw.strip()
    result = {"type": "unknown", "args": {}, "raw": raw}
    lower = raw.lower()

    # ─── TRADING ──────────────────────────────────────────────────────────────
    if lower.startswith("/buy ") or lower.startswith("/sell "):
        parts = raw.split()
        side = parts[0][1:].lower()    # buy / sell
        symbol = parts[1] if len(parts) > 1 else None
        volume = float(parts[2]) if len(parts) > 2 else 0.1
        kwargs = {}
        for p in parts[3:]:
            if ":" in p:
                k, v = p.split(":", 1)
                kwargs[k.strip().lower()] = float(v)
        result["type"] = side
        result["args"] = {
            "symbol": symbol,
            "volume": volume,
            "stop_loss": kwargs.get("sl", 0),
            "take_profit": kwargs.get("tp", 0),
        }

    elif lower.startswith("/close "):
        parts = raw.split()
        result["type"] = "close"
        result["args"] = {"order_id": parts[1] if len(parts) > 1 else None}

    elif lower.startswith("/portfolio"):
        result["type"] = "portfolio"

    elif lower.startswith("/risk"):
        result["type"] = "risk"

    # ─── CHARTS ───────────────────────────────────────────────────────────────
    elif lower.startswith("/chart "):
        parts = raw.split()
        result["type"] = "chart"
        result["args"] = {
            "symbol": parts[1] if len(parts) > 1 else "XAUUSD",
            "timeframe": parts[2] if len(parts) > 2 else "H1",
        }

    elif lower.startswith("@smc"):
        parts = raw.split()
        result["type"] = "smc"
        result["args"] = {"symbol": parts[1] if len(parts) > 1 else "XAUUSD"}

    # ─── NEWS & MACRO ──────────────────────────────────────────────────────────
    elif lower.startswith("@news"):
        result["type"] = "news"
        result["args"] = {"query": raw[5:].strip()}

    elif lower.startswith("@macro"):
        result["type"] = "macro"
        result["args"] = {"query": raw[6:].strip()}

    # ─── RESEARCH & AI ─────────────────────────────────────────────────────────
    elif lower.startswith("@research"):
        result["type"] = "research"
        result["args"] = {"query": raw[9:].strip()}

    elif lower.startswith("@fundamental"):
        result["type"] = "fundamental"
        result["args"] = {"query": raw[12:].strip()}

    elif lower.startswith("@pattern"):
        parts = raw.split()
        result["type"] = "pattern"
        result["args"] = {"symbol": parts[1] if len(parts) > 1 else "XAUUSD"}

    elif lower.startswith("@quant"):
        parts = raw.split()
        result["type"] = "quant"
        result["args"] = {"symbol": parts[1] if len(parts) > 1 else "XAUUSD"}

    elif lower.startswith("@backtest"):
        parts = raw.split()
        result["type"] = "backtest"
        result["args"] = {
            "symbol": parts[1] if len(parts) > 1 else "XAUUSD",
            "strategy": parts[2] if len(parts) > 2 else "default"
        }

    elif lower.startswith("@ai"):
        result["type"] = "ai"
        result["args"] = {"query": raw[3:].strip().strip('"')}

    # ─── COLLABORATION ─────────────────────────────────────────────────────────
    elif lower.startswith("/share "):
        result["type"] = "share"
        result["args"] = {"message": raw[len("/share "):].strip()}

    # ─── EDUCATION ─────────────────────────────────────────────────────────────
    elif lower.startswith("@learn"):
        result["type"] = "learn"
        result["args"] = {"query": raw[6:].strip()}

    # ─── META ──────────────────────────────────────────────────────────────────
    elif lower.startswith("/help"):
        result["type"] = "help"

    return result
