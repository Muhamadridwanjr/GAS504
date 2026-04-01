"""GAS Terminal v3 — Module 9: DevOps & Infrastructure"""
from __future__ import annotations
import subprocess
from gas_terminal.utils import display as D
from gas_terminal import api, config

MENU = [
    ("1", "🐳", "List All Containers"),
    ("2", "▶ ", "Start Container"),
    ("3", "⏹ ", "Stop Container"),
    ("4", "🔄", "Restart Container"),
    ("5", "📜", "Container Logs"),
    ("6", "🔧", "Docker Compose Up"),
    ("7", "🔧", "Docker Compose Down"),
    ("8", "📊", "Docker Stats"),
    ("9", "🛠", "System Info"),
    ("10", "🔧", "Fix Failed Containers"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🛠 DevOps & Infrastructure")
        if choice == "b":
            break
        elif choice == "1":
            containers = api.docker_containers()
            if containers and "error" not in containers[0]:
                rows = []
                for c in containers:
                    status_color = "green" if c.get("status") == "running" else "red"
                    rows.append([
                        c.get("name", ""),
                        f"[{status_color}]{c.get('status', '')}[/{status_color}]",
                        c.get("image", ""),
                        c.get("id", ""),
                    ])
                D.data_table(["Name", "Status", "Image", "ID"], rows, title="Docker Containers")
            else:
                D.error(f"Docker error: {containers[0].get('error', 'unknown') if containers else 'no data'}")
        elif choice == "2":
            name = D.ask("Container name")
            msg = api.docker_container_action(name, "start")
            D.success(msg) if "successfully" in msg else D.error(msg)
        elif choice == "3":
            name = D.ask("Container name")
            if D.confirm(f"Stop container '{name}'?"):
                msg = api.docker_container_action(name, "stop")
                D.success(msg) if "successfully" in msg else D.error(msg)
        elif choice == "4":
            name = D.ask("Container name")
            msg = api.docker_container_action(name, "restart")
            D.success(msg) if "successfully" in msg else D.error(msg)
        elif choice == "5":
            name = D.ask("Container name")
            tail = D.ask("Number of lines (default 50)")
            try:
                tail = int(tail)
            except ValueError:
                tail = 50
            try:
                import docker as dk
                client = dk.from_env()
                c = client.containers.get(name)
                logs = c.logs(tail=tail).decode(errors="replace")
                D.console.print(logs)
            except Exception as e:
                D.error(str(e))
        elif choice == "6":
            compose_path = D.ask(f"Compose file path (default: /root/gasstrategyai/docker-compose.yml)")
            compose_path = compose_path.strip() or "/root/gasstrategyai/docker-compose.yml"
            service = D.ask("Service name (leave blank for all)")
            cmd = ["docker", "compose", "-f", compose_path, "up", "-d"]
            if service.strip():
                cmd.append(service.strip())
            _run_cmd(cmd)
        elif choice == "7":
            compose_path = D.ask(f"Compose file path (default: /root/gasstrategyai/docker-compose.yml)")
            compose_path = compose_path.strip() or "/root/gasstrategyai/docker-compose.yml"
            if D.confirm("Bring down all services?"):
                _run_cmd(["docker", "compose", "-f", compose_path, "down"])
        elif choice == "8":
            stats = api.docker_stats()
            D.result_panel("Docker Stats",
                f"[bold]Total containers:[/bold]   {stats['total']}\n"
                f"[bold]Running:[/bold]            {stats['running']}\n"
                f"[bold]Stopped/Exited:[/bold]     {stats['stopped']}")
        elif choice == "9":
            _show_system_info()
        elif choice == "10":
            containers = api.docker_containers()
            fixed = 0
            for c in containers:
                if c.get("status") in ("exited", "dead"):
                    msg = api.docker_container_action(c["name"], "start")
                    D.info(f"Restarting {c['name']}: {msg}")
                    fixed += 1
            if fixed:
                D.success(f"Fixed {fixed} containers")
            else:
                D.info("All containers are running or no containers found.")
        D.press_enter()

def _run_cmd(cmd: list):
    D.info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        D.error(f"Command not found: {cmd[0]}")
    except KeyboardInterrupt:
        D.info("Interrupted.")

def _show_system_info():
    try:
        import platform
        import os
        uname = platform.uname()
        D.result_panel("System Info",
            f"[bold]OS:[/bold]       {uname.system} {uname.release}\n"
            f"[bold]Machine:[/bold]  {uname.machine}\n"
            f"[bold]Node:[/bold]     {uname.node}\n"
            f"[bold]CPU:[/bold]      {os.cpu_count()} cores\n"
            f"[bold]Python:[/bold]   {platform.python_version()}")
    except Exception as e:
        D.error(f"Could not get system info: {e}")
