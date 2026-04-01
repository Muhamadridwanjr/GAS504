"""GAS Terminal v3 — Module 5: AI Agents Control"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "📋", "List All Agents"),
    ("2", "📊", "Orchestrator Status"),
    ("3", "▶ ", "Start / Dispatch Agent"),
    ("4", "⏸ ", "Pause Agent"),
    ("5", "▶ ", "Resume Agent"),
    ("6", "📜", "View Agent Logs (Redis Stream)"),
    ("7", "🔄", "Restart All Agents"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🤖 AI Agents Control")
        if choice == "b":
            break
        elif choice == "1":
            domain = D.ask("Filter by domain (leave blank for all)")
            data = api.run(api.agents_list(domain or None))
            agents = data.get("agents", [])
            domains = data.get("domains", [])
            D.info(f"Domains: {', '.join(domains) if domains else 'none'}")
            if agents:
                rows = [[a if isinstance(a, str) else a.get("name", str(a)),
                         a.get("status", "") if isinstance(a, dict) else "",
                         a.get("domain", "") if isinstance(a, dict) else ""]
                        for a in agents]
                D.data_table(["Agent", "Status", "Domain"], rows, title="Registered Agents")
            else:
                D.info("No agents found or agent engine unreachable.")
        elif choice == "2":
            data = api.run(api.agents_status())
            if data and "error" not in data:
                lines = []
                for k, v in data.items():
                    lines.append(f"[bold]{k}:[/bold] {v}")
                D.result_panel("Orchestrator Status", "\n".join(lines), style="cyan")
            else:
                D.error(f"Agent engine unreachable: {data.get('error', 'unknown')}")
        elif choice == "3":
            name = D.ask("Agent name")
            task = D.ask("Task description (optional)")
            result = api.run(api.agent_dispatch(name, task=task))
            if result.get("success"):
                D.success(f"Agent '{name}' executed in {result.get('duration_ms', 0):.0f}ms")
            else:
                D.error(f"Dispatch failed: {result.get('error', str(result))}")
        elif choice == "4":
            name = D.ask("Agent name to pause")
            result = api.run(api.agent_pause(name))
            if "paused" in str(result).lower() or result.get("status") == "paused":
                D.success(f"Agent '{name}' paused.")
            else:
                D.error(f"Could not pause: {result}")
        elif choice == "5":
            name = D.ask("Agent name to resume")
            result = api.run(api.agent_resume(name))
            if "resumed" in str(result).lower() or result.get("status") == "running":
                D.success(f"Agent '{name}' resumed.")
            else:
                D.error(f"Could not resume: {result}")
        elif choice == "6":
            name = D.ask("Agent name")
            msgs = api.redis_stream_read(f"gas:events:agent:{name}", count=20)
            if msgs:
                for msg_id, fields in msgs:
                    mid = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                    D.console.print(f"[dim]{mid}[/dim] {fields}")
            else:
                D.info(f"No Redis stream logs found for agent '{name}'")
        elif choice == "7":
            if D.confirm("Restart all agents?"):
                D.info("Restarting all agents...")
                result = api.run(api.agent_dispatch("orchestrator", task="restart_all"))
                D.success(f"Restart dispatched: {result}")
        D.press_enter()
