"""GAS Terminal v3 — Module 2: Fundamental Analysis System"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "🌍", "Fundamental Analysis"),
    ("2", "📰", "Latest Market News"),
    ("3", "📅", "Economic Calendar"),
    ("4", "🏦", "Central Bank Tracker"),
    ("5", "📊", "COT Data (Commitment of Traders)"),
    ("6", "🌐", "Global Macro Briefing"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🌍 Fundamental Analysis System")
        if choice == "b":
            break
        elif choice == "1":
            symbol = D.ask("Symbol (e.g. XAUUSD, EURUSD)")
            D.info(f"Fetching fundamental analysis for {symbol}...")
            result = api.run(api.ai_feature("fundamental", {"symbol": symbol}))
            _display(result, f"Fundamental — {symbol}")
        elif choice == "2":
            limit = D.ask("Number of news items (default 10)")
            try:
                limit = int(limit)
            except ValueError:
                limit = 10
            news = api.run(api.terminal_news(limit=limit))
            if isinstance(news, list) and news:
                rows = []
                for item in news:
                    rows.append([
                        item.get("time", ""),
                        item.get("title", "")[:60],
                        item.get("source", ""),
                        item.get("impact", ""),
                    ])
                D.data_table(["Time", "Title", "Source", "Impact"], rows, title="Market News")
            else:
                D.info("No news available from terminal backend.")
        elif choice == "3":
            events = api.run(api.terminal_calendar())
            if isinstance(events, list) and events:
                rows = []
                for e in events:
                    rows.append([
                        e.get("time", ""),
                        e.get("currency", ""),
                        e.get("event", "")[:50],
                        e.get("impact", ""),
                        e.get("forecast", ""),
                        e.get("previous", ""),
                    ])
                D.data_table(["Time", "CCY", "Event", "Impact", "Forecast", "Previous"], rows, title="Economic Calendar")
            else:
                D.info("No calendar events available.")
        elif choice == "4":
            result = api.run(api.ai_feature("fundamental", {"mode": "central_bank"}))
            _display(result, "Central Bank Tracker")
        elif choice == "5":
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("fundamental", {"symbol": symbol, "mode": "cot"}))
            _display(result, f"COT Data — {symbol}")
        elif choice == "6":
            result = api.run(api.ai_feature("briefing", {"scope": "global", "type": "macro"}))
            _display(result, "Global Macro Briefing")
        D.press_enter()

def _display(result: dict, title: str):
    if not result or "error" in result:
        D.error(result.get("error", "No data") if isinstance(result, dict) else str(result))
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
