"""
Router: dispatches parsed commands to the appropriate backend panel/service proxy.
Services that are 'planned' (not yet deployed) return a graceful stub message.
"""

import httpx
from src.config import settings
from src.lib.logger import logger

HELP_TEXT = """
📋 GAS Terminal – Available Commands:

🔴 TRADING (Execution)
  /buy SYMBOL VOLUME [sl:X] [tp:Y]  – Place BUY order
  /sell SYMBOL VOLUME [sl:X] [tp:Y] – Place SELL order
  /close ORDER_ID                    – Close a position
  /portfolio                         – Open positions & P&L
  /risk                              – Drawdown & risk metrics

📊 CHARTS & REALTIME
  /chart SYMBOL [TIMEFRAME]          – Load chart panel
  @smc SYMBOL                        – Smart Money Concept analysis (planned)

📰 NEWS & MACRO
  @news [keyword]                    – Latest market news
  @macro [query]                     – Macro & sentiment analysis

🔬 RESEARCH & AI
  @research [query]                  – Technical RAG analysis
  @fundamental [query]               – Fundamental data (gold, rates)
  @pattern SYMBOL                    – Pattern detection (planned)
  @quant SYMBOL                      – Quant signals (planned)
  @backtest SYMBOL [strategy]        – Backtesting (planned)
  @ai "QUESTION"                     – Ask the AI orchestrator

🤝 COLLABORATION
  /share MESSAGE                     – Share signal to followers

🎓 EDUCATION
  @learn [topic]                     – Education panel / AI tutor (planned)

  /help                              – Show this help
"""

PLANNED_STUB = lambda cmd: {
    "status": "planned",
    "message": f"⏳ Command `{cmd}` akan tersedia segera. Service terkait sedang dalam tahap pengembangan."
}

async def _call(client, method, url, **kwargs):
    """Wrapper untuk memanggil service dengan catch graceful."""
    try:
        if method == "GET":
            res = await client.get(url, **kwargs)
        else:
            res = await client.post(url, **kwargs)
        return res.json() if res.status_code < 300 else {"error": res.text}
    except httpx.ConnectError:
        service_name = url.split("/")[2]
        logger.warning(f"Service not reachable: {service_name}")
        return {"error": f"Service `{service_name}` tidak tersedia saat ini."}
    except Exception as e:
        logger.error(f"Error calling {url}: {e}")
        return {"error": str(e)}

async def dispatch(user_id: str, action: dict) -> dict:
    cmd_type = action.get("type", "unknown")
    args = action.get("args", {})
    headers = {"X-API-Key": settings.internal_api_key, "X-User-ID": user_id}

    async with httpx.AsyncClient(timeout=15) as client:

        # ─── TRADING ────────────────────────────────────────────────────────────
        if cmd_type in ("buy", "sell"):
            payload = {
                "symbol": args.get("symbol"),
                "action": cmd_type.upper(),
                "order_type": "MARKET",
                "volume": args.get("volume", 0.1),
                "price": 0,
                "stop_loss": args.get("stop_loss", 0),
                "take_profit": args.get("take_profit", 0),
            }
            return await _call(client, "POST", f"{settings.term_service_url}/trade", json=payload, headers=headers)

        elif cmd_type == "close":
            order_id = args.get("order_id")
            try:
                res = await client.delete(f"{settings.term_service_url}/orders/{order_id}", headers=headers)
                return res.json() if res.status_code < 300 else {"error": res.text}
            except httpx.ConnectError:
                return {"error": "gas-term-service tidak tersedia."}

        elif cmd_type == "portfolio":
            return await _call(client, "GET", f"{settings.journal_service_url}/trades",
                               params={"user_id": user_id}, headers=headers)

        elif cmd_type == "risk":
            return await _call(client, "GET", f"{settings.risk_engine_url}/metrics",
                               params={"user_id": user_id}, headers=headers)

        # ─── CHARTS ─────────────────────────────────────────────────────────────
        elif cmd_type == "chart":
            return {
                "panel": "chart",
                "symbol": args.get("symbol"),
                "timeframe": args.get("timeframe"),
                "data_source": settings.chart_service_url
            }

        elif cmd_type == "smc":
            return PLANNED_STUB("@smc")

        # ─── NEWS & MACRO ────────────────────────────────────────────────────────
        elif cmd_type == "news":
            return await _call(client, "GET", f"{settings.news_service_url}/news",
                               params={"q": args.get("query", "")}, headers=headers)

        elif cmd_type == "macro":
            return await _call(client, "POST", f"{settings.rag_macro_url}/query",
                               json={"query": args.get("query")}, headers=headers)

        # ─── RESEARCH & AI ───────────────────────────────────────────────────────
        elif cmd_type == "research":
            return await _call(client, "POST", f"{settings.rag_technical_url}/query",
                               json={"query": args.get("query")}, headers=headers)

        elif cmd_type == "fundamental":
            return await _call(client, "POST", f"{settings.fundamental_data_url}/query",
                               json={"query": args.get("query")}, headers=headers)

        elif cmd_type == "pattern":
            return PLANNED_STUB("@pattern")

        elif cmd_type == "quant":
            return PLANNED_STUB("@quant")

        elif cmd_type == "backtest":
            return PLANNED_STUB("@backtest")

        elif cmd_type == "ai":
            return await _call(client, "POST", f"{settings.ai_orchestrator_url}/analyze",
                               json={"query": args.get("query"), "user_id": user_id}, headers=headers)

        # ─── COLLABORATION ───────────────────────────────────────────────────────
        elif cmd_type == "share":
            return await _call(client, "POST", f"{settings.social_service_url}/signals",
                               json={"user_id": user_id, "message": args.get("message")}, headers=headers)

        # ─── EDUCATION ───────────────────────────────────────────────────────────
        elif cmd_type == "learn":
            return PLANNED_STUB("@learn")

        # ─── META ────────────────────────────────────────────────────────────────
        elif cmd_type == "help":
            return {"help": HELP_TEXT}

        else:
            return {"error": "Unknown command. Type /help for the full command list."}
