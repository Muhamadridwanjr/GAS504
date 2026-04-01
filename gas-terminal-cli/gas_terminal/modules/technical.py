"""GAS Terminal v3 — Module 1: Technical Analysis System"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "📊", "Analyze Symbol (Technical AI)"),
    ("2", "⚡", "Generate Trading Signal"),
    ("3", "🔍", "Multi-Timeframe Analysis"),
    ("4", "📈", "SMC Structure & Zones"),
    ("5", "🧮", "Indicator Confluence"),
    ("6", "🌊", "Liquidity Map"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "📊 Technical Analysis System")
        if choice == "b":
            break
        elif choice == "1":
            symbol = D.ask("Symbol (e.g. XAUUSD)")
            tf = D.ask("Timeframe (e.g. H1, M15, H4)")
            D.info(f"Fetching technical analysis for {symbol} {tf}...")
            result = api.run(api.ai_feature("technical", {"symbol": symbol, "timeframe": tf}))
            _display(result, f"Technical Analysis — {symbol} {tf}")
        elif choice == "2":
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("signal", {"symbol": symbol}))
            _display(result, f"Signal — {symbol}")
        elif choice == "3":
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("technical", {
                "symbol": symbol,
                "mode": "mtf",
                "timeframes": ["M15", "H1", "H4", "D1"]
            }))
            _display(result, f"Multi-Timeframe — {symbol}")
        elif choice == "4":
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("technical", {
                "symbol": symbol,
                "mode": "smc"
            }))
            _display(result, f"SMC Structure — {symbol}")
        elif choice == "5":
            symbol = D.ask("Symbol")
            tf = D.ask("Timeframe")
            result = api.run(api.ai_feature("technical", {
                "symbol": symbol,
                "timeframe": tf,
                "mode": "confluence"
            }))
            _display(result, f"Indicator Confluence — {symbol} {tf}")
        elif choice == "6":
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("technical", {
                "symbol": symbol,
                "mode": "liquidity"
            }))
            _display(result, f"Liquidity Map — {symbol}")
        D.press_enter()

def _display(result: dict, title: str):
    if not result or "error" in result:
        D.error(result.get("error", "No data returned") if isinstance(result, dict) else str(result))
        return
    lines = []
    for k, v in result.items():
        if isinstance(v, dict):
            lines.append(f"[bold]{k}:[/bold]")
            for kk, vv in v.items():
                lines.append(f"  {kk}: {vv}")
        elif isinstance(v, list):
            lines.append(f"[bold]{k}:[/bold] {', '.join(str(i) for i in v[:5])}")
        else:
            lines.append(f"[bold]{k}:[/bold] {v}")
    D.result_panel(title, "\n".join(lines) if lines else str(result))
