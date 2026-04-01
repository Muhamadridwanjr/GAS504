"""GAS Terminal v3 — Module 15: Quant Research Lab"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "🧪", "Run Backtest"),
    ("2", "📊", "Strategy Performance Report"),
    ("3", "📈", "Walk-Forward Analysis"),
    ("4", "🔗", "Correlation Analysis"),
    ("5", "📉", "Drawdown Analysis"),
    ("6", "🔭", "Multi-Symbol Screener"),
    ("7", "📋", "PropFirm Challenge Tracker"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🧪 Quant Research Lab")
        if choice == "b":
            break
        elif choice == "1":
            strategy = D.ask("Strategy name (e.g. smc_v1, breakout_v2)")
            symbol = D.ask("Symbol (e.g. XAUUSD)")
            from_date = D.ask("From date (YYYY-MM-DD, e.g. 2024-01-01)")
            to_date = D.ask("To date (YYYY-MM-DD, e.g. 2024-12-31)")
            tf = D.ask("Timeframe (e.g. H1, M15)")
            D.info(f"Running backtest: {strategy} on {symbol} {from_date} → {to_date}")
            result = api.run(api.ai_feature("backtesting", {
                "strategy": strategy or "smc_v1",
                "symbol": symbol or "XAUUSD",
                "from_date": from_date or "2024-01-01",
                "to_date": to_date or "2024-12-31",
                "timeframe": tf or "H1",
            }))
            _display(result, f"Backtest — {strategy} on {symbol}")
        elif choice == "2":
            strategy = D.ask("Strategy name")
            result = api.run(api.ai_feature("backtesting", {
                "strategy": strategy or "smc_v1",
                "mode": "performance_report"
            }))
            _display(result, f"Performance Report — {strategy}")
        elif choice == "3":
            strategy = D.ask("Strategy name")
            symbol = D.ask("Symbol")
            result = api.run(api.ai_feature("backtesting", {
                "strategy": strategy or "smc_v1",
                "symbol": symbol or "XAUUSD",
                "mode": "walk_forward"
            }))
            _display(result, f"Walk-Forward — {strategy}")
        elif choice == "4":
            result = api.run(api.ai_feature("correlation", {}))
            _display(result, "Correlation Analysis")
        elif choice == "5":
            result = api.run(api.ai_feature("drawdown", {}))
            _display(result, "Drawdown Analysis")
        elif choice == "6":
            symbols_input = D.ask("Symbols (comma-separated)")
            symbols = [s.strip() for s in symbols_input.split(",") if s.strip()] or ["XAUUSD", "EURUSD", "BTCUSDT"]
            result = api.run(api.ai_feature("scanner", {"symbols": symbols}))
            _display(result, "Screener Results")
        elif choice == "7":
            result = api.run(api.ai_feature("propfirm", {}))
            _display(result, "PropFirm Challenge Tracker")
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
