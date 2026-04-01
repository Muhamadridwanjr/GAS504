"""GAS Terminal v3 — Module 3: Hybrid & Risk System"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "⚡", "Hybrid Confluence Score"),
    ("2", "📊", "Sentiment Analysis"),
    ("3", "🛡", "Risk Calculator"),
    ("4", "📉", "Drawdown Recovery Planner"),
    ("5", "🔗", "Correlation Matrix"),
    ("6", "🤖", "AI Market Briefing"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "⚡ Hybrid & Risk System")
        if choice == "b":
            break
        elif choice == "1":
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("hybrid", {"symbol": symbol}))
            _display(result, f"Hybrid Confluence — {symbol}")
        elif choice == "2":
            symbol = D.ask("Symbol (or 'global' for market-wide)")
            payload = {"symbol": symbol} if symbol.lower() != "global" else {"scope": "global"}
            result = api.run(api.ai_feature("sentiment", payload))
            _display(result, f"Sentiment — {symbol}")
        elif choice == "3":
            account = D.ask("Account Balance (USD)")
            risk_pct = D.ask("Risk % per trade (e.g. 1.0)")
            symbol = D.ask("Symbol")
            try:
                result = api.run(api.ai_feature("risk", {
                    "account_balance": float(account),
                    "risk_percentage": float(risk_pct),
                    "symbol": symbol
                }))
                _display(result, "Risk Calculation")
            except ValueError:
                D.error("Invalid number input.")
        elif choice == "4":
            result = api.run(api.ai_feature("drawdown", {}))
            _display(result, "Drawdown Recovery Planner")
        elif choice == "5":
            result = api.run(api.ai_feature("correlation", {}))
            _display(result, "Correlation Matrix")
        elif choice == "6":
            period = D.ask("Period (daily/weekly)")
            result = api.run(api.ai_feature("briefing", {"period": period or "daily"}))
            _display(result, f"AI Market Briefing — {period or 'daily'}")
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
