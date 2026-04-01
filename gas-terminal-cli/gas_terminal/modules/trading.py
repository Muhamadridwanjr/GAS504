"""GAS Terminal v3 — Module 8: Trading & Market Engine"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "📡", "Live Market Overview"),
    ("2", "💱", "Forex Pairs"),
    ("3", "🪙", "Crypto (Binance)"),
    ("4", "🥇", "Commodities"),
    ("5", "🔔", "Signal Feed"),
    ("6", "🔭", "Multi-Symbol Scanner"),
    ("7", "📋", "Watchlist"),
    ("8", "💹", "Order Flow (if available)"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "📡 Trading & Market Engine")
        if choice == "b":
            break
        elif choice == "1":
            overview = api.run(api.terminal_overview())
            if overview and "error" not in overview:
                lines = []
                for k, v in overview.items():
                    if isinstance(v, dict):
                        lines.append(f"[bold]{k}:[/bold]")
                        for kk, vv in v.items():
                            lines.append(f"  {kk}: {vv}")
                    else:
                        lines.append(f"[bold]{k}:[/bold] {v}")
                D.result_panel("Live Market Overview", "\n".join(lines), style="cyan")
            else:
                D.info("Terminal backend not available. Showing Binance fallback.")
                tickers = api.run(api.binance_tickers())
                if isinstance(tickers, list) and tickers:
                    rows = []
                    for t in tickers[:20]:
                        rows.append([
                            t.get("symbol", ""),
                            t.get("last", t.get("price", "")),
                            t.get("change_pct", t.get("percentage", "")),
                            t.get("volume", ""),
                        ])
                    D.data_table(["Symbol", "Price", "Change%", "Volume"], rows, title="Binance Live Tickers")
        elif choice == "2":
            pairs = api.run(api.terminal_pairs())
            forex = [p for p in (pairs if isinstance(pairs, list) else [])
                     if not any(c in p.get("symbol", "") for c in ["BTC", "ETH", "USDT", "XAU", "XAG"])]
            if forex:
                rows = [[p.get("symbol",""), p.get("price",""), p.get("change_pct",""), p.get("trend","")] for p in forex]
                D.data_table(["Symbol", "Price", "Change%", "Trend"], rows, title="Forex Pairs")
            else:
                D.info("No forex data available.")
        elif choice == "3":
            tickers = api.run(api.binance_tickers())
            if isinstance(tickers, list) and tickers:
                rows = []
                for t in tickers[:25]:
                    rows.append([
                        t.get("symbol", ""),
                        t.get("last", t.get("price", "")),
                        t.get("change_pct", t.get("percentage", "")),
                        t.get("volume", ""),
                    ])
                D.data_table(["Symbol", "Price", "Change%", "Volume"], rows, title="Crypto — Binance")
            else:
                D.info("Binance service not available.")
        elif choice == "4":
            pairs = api.run(api.terminal_pairs())
            commodities = [p for p in (pairs if isinstance(pairs, list) else [])
                           if any(c in p.get("symbol", "") for c in ["XAU", "XAG", "OIL", "USOIL", "WTI"])]
            if commodities:
                rows = [[p.get("symbol",""), p.get("price",""), p.get("change_pct",""), p.get("trend","")] for p in commodities]
                D.data_table(["Symbol", "Price", "Change%", "Trend"], rows, title="Commodities")
            else:
                D.info("No commodity data available from terminal backend.")
        elif choice == "5":
            symbol = D.ask("Symbol (default XAUUSD)")
            symbol = symbol.strip() or "XAUUSD"
            result = api.run(api.terminal_signals(symbol))
            if isinstance(result, list):
                rows = [[s.get("symbol",""), s.get("direction",""), s.get("confidence",""),
                         s.get("entry",""), s.get("tp",""), s.get("sl","")] for s in result]
            elif isinstance(result, dict) and "error" not in result:
                rows = [[result.get("symbol",""), result.get("direction",""), result.get("confidence",""),
                         result.get("entry",""), result.get("tp",""), result.get("sl","")]]
            else:
                rows = []
            if rows:
                D.data_table(["Symbol", "Direction", "Confidence", "Entry", "TP", "SL"], rows, title="Signal Feed")
            else:
                D.info("No signals available.")
        elif choice == "6":
            symbols_input = D.ask("Symbols (comma-separated, e.g. XAUUSD,EURUSD,BTCUSDT)")
            symbols = [s.strip() for s in symbols_input.split(",") if s.strip()] or ["XAUUSD", "EURUSD", "BTCUSDT"]
            result = api.run(api.ai_feature("scanner", {"symbols": symbols}))
            _display(result, "Scanner Results")
        elif choice == "7":
            pairs = api.run(api.terminal_pairs())
            if isinstance(pairs, list) and pairs:
                rows = []
                for p in pairs:
                    trend = p.get("trend", "→")
                    icon = "📈" if trend == "bullish" else "📉" if trend == "bearish" else "➡"
                    rows.append([p.get("symbol",""), icon, str(p.get("price","")), str(p.get("change_pct",""))])
                D.data_table(["Symbol", "", "Price", "Change%"], rows, title="Watchlist")
            else:
                D.info("Watchlist not available.")
        elif choice == "8":
            result = api.run(api.ai_feature("technical", {"mode": "orderflow"}))
            _display(result, "Order Flow Analysis")
        D.press_enter()

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
