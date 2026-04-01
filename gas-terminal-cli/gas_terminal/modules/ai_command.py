"""GAS Terminal v3 — Module 20: AI Command Mode (Natural Language)"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api, config

MENU = [
    ("1", "💬", "Natural Language Command"),
    ("2", "🤖", "Interactive AI Chat"),
    ("3", "📊", "Market Analysis (AI Prompt)"),
    ("4", "🎯", "Trade Idea Generator"),
    ("5", "📰", "Summarize Market News"),
]

_SYSTEM_PROMPT = """You are GAS Terminal AI — an expert AI trading assistant embedded in the
GAS Terminal v3 trading platform. You have access to market analysis, signals, and trading data.

You help traders with:
- Technical and fundamental market analysis
- Trading signals and setup identification
- Risk management and position sizing
- Market sentiment and momentum assessment
- Trade psychology and discipline

Keep responses concise, actionable, and professional. Use bullet points for clarity.
Always include specific price levels, key observations, and risk considerations when relevant.
"""

def run():
    while True:
        choice = D.sub_menu(MENU, "🎮 AI Command Mode")
        if choice == "b":
            break
        elif choice == "1":
            query = D.ask("Enter your command (e.g. 'analyze gold for a long setup')")
            if query.strip():
                run_nl_command(query.strip())
        elif choice == "2":
            run_interactive_mode()
        elif choice == "3":
            symbol = D.ask("Symbol")
            run_nl_command(f"Give me a comprehensive market analysis for {symbol} including trend, key levels, and best trade setup right now.")
        elif choice == "4":
            symbol = D.ask("Symbol")
            run_nl_command(f"Generate 3 high-probability trade ideas for {symbol} with specific entry, TP, and SL levels. Include confluence factors.")
        elif choice == "5":
            run_nl_command("Summarize the most important market news and economic events happening today that could impact forex and gold prices. List the top 5 market-moving events.")
        D.press_enter()

def run_nl_command(query: str, provider: str = None):
    """
    Execute a single natural language command.
    Uses multi-provider router: OpenRouter → Kimi → Gemini → Claude (fallback chain).
    """
    from gas_terminal.modules.models import ask_ai
    full_prompt = f"{_SYSTEM_PROMPT}\n\nUser: {query}"
    D.info(f"Processing [{config.DEFAULT_AI_PROVIDER}]: {query}")
    try:
        reply = ask_ai(full_prompt, provider=provider, max_tokens=1024)
        D.result_panel("GAS AI Response", reply, style="cyan")
    except Exception as e:
        D.warning(f"AI provider failed: {e}. Fallback ke API feature...")
        _fallback_nl_command(query)

def run_interactive_mode():
    """
    Interactive multi-turn AI chat. Pakai provider yang aktif di config.
    Ketik 'model' untuk ganti provider di sesi ini.
    """
    from gas_terminal.modules.models import ask_ai, _build_fallback_chain
    available = _build_fallback_chain(config.DEFAULT_AI_PROVIDER)
    provider  = available[0] if available else None

    if not provider:
        D.error("Tidak ada AI provider yang dikonfigurasi. Set salah satu key di .env:\n"
                "  OPENROUTER_API_KEY / KIMI_API_KEY / GEMINI_API_KEY / ANTHROPIC_API_KEY")
        return

    D.info(f"AI Chat Mode — Provider: [bold cyan]{provider}[/bold cyan]")
    D.info("Ketik [bold]'model'[/bold] ganti provider, [bold]'exit'[/bold] keluar.\n")
    history: list[str] = []

    while True:
        try:
            user_input = D.ask("Kamu")
        except (EOFError, KeyboardInterrupt):
            break
        cmd = user_input.lower().strip()
        if cmd in ("exit", "quit", "q", "b", "back"):
            break
        if cmd == "model":
            from gas_terminal.modules.models import _change_provider
            _change_provider()
            available = _build_fallback_chain(config.DEFAULT_AI_PROVIDER)
            provider  = available[0] if available else provider
            D.success(f"Provider ganti ke: {provider}")
            continue
        if not user_input.strip():
            continue

        history.append(f"User: {user_input}")
        ctx = "\n".join(history[-6:])  # keep last 3 turns as context
        full_prompt = f"{_SYSTEM_PROMPT}\n\n{ctx}\nAssistant:"
        try:
            reply = ask_ai(full_prompt, provider=provider, max_tokens=1500)
            history.append(f"Assistant: {reply}")
            D.result_panel(f"GAS AI [{provider}]", reply, style="cyan")
        except Exception as e:
            D.error(f"AI error: {e}")

def _fallback_nl_command(query: str):
    """Fallback: try to route NL command to a known API feature."""
    query_lower = query.lower()
    routed = False

    if any(kw in query_lower for kw in ["analyze", "technical", "trend", "structure"]):
        symbols = _extract_symbols(query)
        sym = symbols[0] if symbols else "XAUUSD"
        result = api.run(api.ai_feature("technical", {"symbol": sym}))
        _display(result, f"Technical Analysis — {sym}")
        routed = True

    if any(kw in query_lower for kw in ["signal", "buy", "sell", "entry"]):
        symbols = _extract_symbols(query)
        sym = symbols[0] if symbols else "XAUUSD"
        result = api.run(api.ai_feature("signal", {"symbol": sym}))
        _display(result, f"Signal — {sym}")
        routed = True

    if any(kw in query_lower for kw in ["sentiment", "feeling", "retail", "institutional"]):
        symbols = _extract_symbols(query)
        sym = symbols[0] if symbols else "XAUUSD"
        result = api.run(api.ai_feature("sentiment", {"symbol": sym}))
        _display(result, f"Sentiment — {sym}")
        routed = True

    if any(kw in query_lower for kw in ["fundamental", "macro", "economy", "news"]):
        symbols = _extract_symbols(query)
        sym = symbols[0] if symbols else "XAUUSD"
        result = api.run(api.ai_feature("fundamental", {"symbol": sym}))
        _display(result, f"Fundamental — {sym}")
        routed = True

    if not routed:
        D.warning("Could not interpret command. Set ANTHROPIC_API_KEY for full AI mode.")
        D.info(f"Query: '{query}'")
        D.info("Try commands like: 'analyze XAUUSD', 'signal for EURUSD', 'market sentiment'")

def _extract_symbols(query: str) -> list[str]:
    """Extract known trading symbols from a query string."""
    known = [
        "XAUUSD", "XAGUSD", "EURUSD", "GBPUSD", "USDJPY", "USDCHF",
        "AUDUSD", "NZDUSD", "USDCAD", "BTCUSDT", "ETHUSDT", "BNBUSDT",
        "SOLUSDT", "GOLD", "SILVER", "OIL", "USOIL",
    ]
    aliases = {
        "gold": "XAUUSD",
        "silver": "XAGUSD",
        "bitcoin": "BTCUSDT",
        "btc": "BTCUSDT",
        "ethereum": "ETHUSDT",
        "eth": "ETHUSDT",
        "euro": "EURUSD",
        "pound": "GBPUSD",
        "yen": "USDJPY",
    }
    found = []
    query_upper = query.upper()
    for sym in known:
        if sym in query_upper:
            found.append(sym)
    for alias, sym in aliases.items():
        if alias.lower() in query.lower() and sym not in found:
            found.append(sym)
    return found

def _display(result, title):
    if not result or (isinstance(result, dict) and "error" in result):
        D.error(result.get("error", "No data") if isinstance(result, dict) else str(result))
        return
    lines = []
    data = result if isinstance(result, dict) else {}
    for k, v in data.items():
        if isinstance(v, dict):
            lines.append(f"[bold]{k}:[/bold]")
            for kk, vv in v.items():
                lines.append(f"  {kk}: {vv}")
        elif isinstance(v, list):
            lines.append(f"[bold]{k}:[/bold] {', '.join(str(i) for i in v[:5])}")
        else:
            lines.append(f"[bold]{k}:[/bold] {v}")
    D.result_panel(title, "\n".join(lines) if lines else str(result))
