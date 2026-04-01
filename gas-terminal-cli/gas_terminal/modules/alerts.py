"""GAS Terminal v3 — Module 12: Alerts & Notification"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api, config

MENU = [
    ("1", "🔔", "View Active Alerts"),
    ("2", "➕", "Create New Alert"),
    ("3", "📱", "Send Telegram Test Message"),
    ("4", "📊", "Signal Alerts"),
    ("5", "💎", "Price Level Alerts"),
    ("6", "⚙ ", "Notification Settings"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🔔 Alerts & Notification")
        if choice == "b":
            break
        elif choice == "1":
            result = api.run(api.ai_feature("signal", {"mode": "alerts"}))
            _display(result, "Active Alerts")
        elif choice == "2":
            symbol = D.ask("Symbol")
            alert_type = D.ask("Alert type (price/signal/news)")
            condition = D.ask("Condition (e.g. price > 2050, bullish signal)")
            D.info(f"Alert created: {alert_type} on {symbol} — {condition}")
            D.info("(Alert persistence requires backend integration)")
        elif choice == "3":
            if not config.TELEGRAM_BOT_TOKEN or not config.TELEGRAM_CHAT_ID:
                D.error("Telegram not configured. Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env")
            else:
                msg = D.ask("Test message text")
                _send_telegram(msg or "GAS Terminal v3 — test notification!")
        elif choice == "4":
            symbol = D.ask("Symbol for signal alerts")
            result = api.run(api.ai_feature("signal", {"symbol": symbol}))
            _display(result, f"Signal Alerts — {symbol}")
        elif choice == "5":
            symbol = D.ask("Symbol")
            price = D.ask("Price level")
            direction = D.ask("Direction (above/below)")
            D.info(f"Price alert queued: {symbol} {direction} {price}")
            D.info("(Persistent alerts require backend integration)")
        elif choice == "6":
            D.result_panel("Notification Settings",
                f"[bold]Telegram Token:[/bold] {'set' if config.TELEGRAM_BOT_TOKEN else 'not set'}\n"
                f"[bold]Telegram Chat ID:[/bold] {'set' if config.TELEGRAM_CHAT_ID else 'not set'}\n\n"
                f"[dim]Edit .env to configure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID[/dim]")
        D.press_enter()

def _send_telegram(text: str):
    try:
        import httpx
        url = f"https://api.telegram.org/bot{config.TELEGRAM_BOT_TOKEN}/sendMessage"
        r = httpx.post(url, json={"chat_id": config.TELEGRAM_CHAT_ID, "text": text})
        if r.status_code == 200:
            D.success("Telegram message sent successfully!")
        else:
            D.error(f"Telegram API error: {r.text}")
    except Exception as e:
        D.error(f"Telegram send failed: {e}")

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
