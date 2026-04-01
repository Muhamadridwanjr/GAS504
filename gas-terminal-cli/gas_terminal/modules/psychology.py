"""GAS Terminal v3 — Module 4: Psychology & Growth"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "🧠", "Psychology Coach Check-In"),
    ("2", "📔", "Trade Journal AI Analysis"),
    ("3", "📖", "Journal Review (Recent Entries)"),
    ("4", "🎓", "Mentor Mode — Review Last Trade"),
    ("5", "🎯", "Mentor — Live Setup Guidance"),
    ("6", "🏆", "View XP Level & Progress"),
    ("7", "🏅", "Leaderboard"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🧠 Psychology & Growth")
        if choice == "b":
            break
        elif choice == "1":
            result = api.run(api.ai_feature("psychology", {}))
            _display(result, "Psychology Coach")
        elif choice == "2":
            result = api.run(api.ai_feature("journal", {}))
            _display(result, "Journal AI Analysis")
        elif choice == "3":
            result = api.run(api.ai_feature("journal", {"action": "review"}))
            _display(result, "Journal Review")
        elif choice == "4":
            trade_id = D.ask("Trade ID (leave blank for last trade)")
            payload = {"trade_id": trade_id} if trade_id.strip() else {}
            result = api.run(api.ai_feature("mentor", payload))
            _display(result, "Mentor — Trade Review")
        elif choice == "5":
            result = api.run(api.ai_feature("mentor", {"mode": "live"}))
            _display(result, "Mentor — Live Setup")
        elif choice == "6":
            level_data = api.run(api.user_level())
            if level_data:
                lines = []
                for k, v in level_data.items():
                    lines.append(f"[bold]{k}:[/bold] {v}")
                D.result_panel("XP Level & Progress", "\n".join(lines), style="yellow")
            else:
                D.info("Level data not available (not logged in?)")
        elif choice == "7":
            lb = api.run(api.leaderboard())
            if isinstance(lb, list) and lb:
                rows = []
                for i, entry in enumerate(lb[:10], 1):
                    rows.append([
                        str(i),
                        entry.get("username", ""),
                        str(entry.get("level", "")),
                        str(entry.get("xp", "")),
                        str(entry.get("plan", "")),
                    ])
                D.data_table(["#", "Username", "Level", "XP", "Plan"], rows, title="Leaderboard Top 10")
            else:
                D.info("Leaderboard not available.")
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
