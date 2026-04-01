"""GAS Terminal v3 — Module 16: Automation & Scheduler"""
from __future__ import annotations
import subprocess
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "🔄", "Auto Analyze Market (headless)"),
    ("2", "🔭", "Auto Scan Watchlist"),
    ("3", "🔧", "Auto Fix Failed Services"),
    ("4", "🔍", "Auto Code Review"),
    ("5", "📋", "List Cron Jobs"),
    ("6", "➕", "Add Cron Job"),
    ("7", "🗑 ", "Remove Cron Job"),
    ("8", "📜", "View Cron Log"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "⚙  Automation & Scheduler")
        if choice == "b":
            break
        elif choice == "1":
            symbols_input = D.ask("Symbols (comma-separated, default: XAUUSD,EURUSD,BTCUSDT)")
            sym_list = [s.strip() for s in symbols_input.split(",") if s.strip()] or ["XAUUSD", "EURUSD", "BTCUSDT"]
            for sym in sym_list:
                D.info(f"Analyzing {sym}...")
                result = api.run(api.ai_feature("technical", {"symbol": sym}))
                summary = result.get("summary") or result.get("analysis") or str(result)[:200]
                D.console.print(f"  [green]{sym}[/green]: {summary}")
        elif choice == "2":
            D.info("Scanning all watchlist pairs...")
            pairs = api.run(api.terminal_pairs())
            symbols = [p.get("symbol") for p in (pairs if isinstance(pairs, list) else []) if p.get("symbol")]
            if not symbols:
                symbols = ["XAUUSD", "EURUSD", "BTCUSDT"]
            result = api.run(api.ai_feature("scanner", {"symbols": symbols}))
            _display(result, "Auto Scan Results")
        elif choice == "3":
            D.info("Checking for failed containers...")
            containers = api.docker_containers()
            fixed = 0
            for c in containers:
                if c.get("status") in ("exited", "dead"):
                    D.warning(f"Restarting {c['name']}...")
                    msg = api.docker_container_action(c["name"], "start")
                    D.info(f"  {msg}")
                    fixed += 1
            if fixed:
                D.success(f"Fixed {fixed} containers.")
            else:
                D.success("All containers are running. Nothing to fix.")
        elif choice == "4":
            path = D.ask("Path to review (default: /root/gasstrategyai)")
            path = path.strip() or "/root/gasstrategyai"
            subprocess.run(["claude", "-p",
                f"Do a comprehensive code review of {path}. List critical issues, security vulnerabilities, "
                f"and top 5 improvements. Be concise."])
        elif choice == "5":
            _list_cron()
        elif choice == "6":
            schedule = D.ask("Cron schedule (e.g. '0 8 * * *' for 8am daily)")
            command = D.ask("Command to run")
            _add_cron(schedule, command)
        elif choice == "7":
            pattern = D.ask("Pattern to match in cron job (e.g. 'gas auto')")
            _remove_cron(pattern)
        elif choice == "8":
            _view_cron_log()
        D.press_enter()

def _list_cron():
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            rows = [[str(i+1), line] for i, line in enumerate(lines) if line.strip() and not line.startswith("#")]
            D.data_table(["#", "Cron Job"], rows, title="Scheduled Jobs")
        else:
            D.info("No cron jobs configured.")
    except Exception as e:
        D.error(f"Could not list cron jobs: {e}")

def _add_cron(schedule: str, command: str):
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        existing = result.stdout if result.returncode == 0 else ""
        new_line = f"{schedule} {command}\n"
        new_cron = existing.rstrip() + "\n" + new_line
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
        proc.communicate(new_cron.encode())
        D.success(f"Cron job added: {schedule} {command}")
    except Exception as e:
        D.error(f"Could not add cron job: {e}")

def _remove_cron(pattern: str):
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        if result.returncode != 0:
            D.info("No cron jobs to remove.")
            return
        lines = result.stdout.split("\n")
        new_lines = [l for l in lines if pattern not in l]
        removed = len(lines) - len(new_lines)
        new_cron = "\n".join(new_lines)
        proc = subprocess.Popen(["crontab", "-"], stdin=subprocess.PIPE)
        proc.communicate(new_cron.encode())
        D.success(f"Removed {removed} cron job(s) matching '{pattern}'")
    except Exception as e:
        D.error(f"Could not remove cron job: {e}")

def _view_cron_log():
    try:
        paths = ["/var/log/syslog", "/var/log/cron", "/var/log/cron.log"]
        import os
        for path in paths:
            if os.path.exists(path):
                D.info(f"Showing last 50 lines of {path}")
                result = subprocess.run(["tail", "-50", path], capture_output=True, text=True)
                lines = [l for l in result.stdout.split("\n") if "CRON" in l or "cron" in l.lower()]
                D.console.print("\n".join(lines[-30:]) if lines else "No cron entries in log.")
                return
        D.info("Cron log file not found in standard locations.")
    except Exception as e:
        D.error(str(e))

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
