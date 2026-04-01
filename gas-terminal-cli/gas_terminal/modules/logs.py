"""GAS Terminal v3 — Module 11: Logs & Debugger"""
from __future__ import annotations
import subprocess
from gas_terminal.utils import display as D
from gas_terminal import api

MENU = [
    ("1", "📜", "Container Logs (Docker)"),
    ("2", "🔴", "Live Log Stream (tail -f)"),
    ("3", "📡", "Redis Stream Viewer"),
    ("4", "🐛", "Recent Error Logs"),
    ("5", "📂", "View Log File"),
    ("6", "🧹", "Clear Redis Stream"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "📜 Logs & Debugger")
        if choice == "b":
            break
        elif choice == "1":
            name = D.ask("Container name")
            tail = D.ask("Lines to show (default 100)")
            try:
                tail = int(tail)
            except ValueError:
                tail = 100
            try:
                import docker as dk
                client = dk.from_env()
                c = client.containers.get(name)
                logs = c.logs(tail=tail).decode(errors="replace")
                D.console.print(logs)
            except Exception as e:
                D.error(str(e))
        elif choice == "2":
            name = D.ask("Container name")
            D.info(f"Streaming logs for '{name}' (Ctrl+C to stop)...")
            try:
                subprocess.run(["docker", "logs", "-f", "--tail", "50", name])
            except KeyboardInterrupt:
                D.info("Stopped log stream.")
            except Exception as e:
                D.error(str(e))
        elif choice == "3":
            stream = D.ask("Stream key (e.g. gas:events:agent:market_analyst)")
            count = D.ask("Number of messages (default 20)")
            try:
                count = int(count)
            except ValueError:
                count = 20
            msgs = api.redis_stream_read(stream, count=count)
            if msgs:
                for msg_id, fields in msgs:
                    mid = msg_id.decode() if isinstance(msg_id, bytes) else str(msg_id)
                    decoded = {}
                    for k, v in fields.items():
                        dk2 = k.decode() if isinstance(k, bytes) else str(k)
                        dv = v.decode() if isinstance(v, bytes) else str(v)
                        decoded[dk2] = dv
                    D.console.print(f"[dim]{mid}[/dim] {decoded}")
            else:
                D.info(f"No messages found in stream: {stream}")
        elif choice == "4":
            D.info("Checking all containers for recent errors...")
            containers = api.docker_containers()
            for c in containers:
                if c.get("status") == "running":
                    try:
                        import docker as dk
                        client = dk.from_env()
                        container = client.containers.get(c["name"])
                        logs = container.logs(tail=20).decode(errors="replace")
                        errors = [line for line in logs.split("\n")
                                  if any(kw in line.lower() for kw in ["error", "exception", "traceback", "critical"])]
                        if errors:
                            D.warning(f"Errors in [{c['name']}]:")
                            for line in errors[:5]:
                                D.console.print(f"  [red]{line}[/red]")
                    except Exception:
                        pass
        elif choice == "5":
            path = D.ask("Log file path")
            tail = D.ask("Lines (default 50)")
            try:
                tail = int(tail)
            except ValueError:
                tail = 50
            try:
                with open(path, "r", errors="replace") as f:
                    lines = f.readlines()
                tail_lines = lines[-tail:] if len(lines) > tail else lines
                D.console.print("".join(tail_lines))
            except FileNotFoundError:
                D.error(f"File not found: {path}")
            except Exception as e:
                D.error(str(e))
        elif choice == "6":
            stream = D.ask("Stream key to clear")
            if D.confirm(f"Delete all messages from stream '{stream}'?"):
                try:
                    import redis as r
                    from gas_terminal import config
                    client = r.from_url(config.REDIS_URL)
                    client.delete(stream)
                    D.success(f"Stream '{stream}' cleared.")
                except Exception as e:
                    D.error(str(e))
        D.press_enter()
