"""GAS Terminal v3 — Module 14: Services Manager"""
from __future__ import annotations
import subprocess
from gas_terminal.utils import display as D
from gas_terminal import api, config

COMPOSE_FILE = "/root/gasstrategyai/docker-compose.yml"

MENU = [
    ("1", "📋", "List All Services"),
    ("2", "▶ ", "Start Service"),
    ("3", "⏹ ", "Stop Service"),
    ("4", "🔄", "Restart Service"),
    ("5", "🚀", "Start All (docker-compose up)"),
    ("6", "⏹ ", "Stop All (docker-compose down)"),
    ("7", "🔃", "Pull Latest Images"),
    ("8", "📊", "Service Health Overview"),
    ("9", "🔧", "Rebuild & Restart Service"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "📡 Services Manager")
        if choice == "b":
            break
        elif choice == "1":
            containers = api.docker_containers()
            rows = []
            for c in containers:
                status = c.get("status", "")
                color = "green" if status == "running" else "red" if status in ("exited","dead") else "yellow"
                rows.append([c.get("name",""), f"[{color}]{status}[/{color}]",
                             c.get("image",""), c.get("id","")])
            D.data_table(["Service", "Status", "Image", "ID"], rows, title="All Services")
        elif choice == "2":
            name = D.ask("Service/container name")
            msg = api.docker_container_action(name, "start")
            D.success(msg) if "successfully" in msg else D.error(msg)
        elif choice == "3":
            name = D.ask("Service/container name")
            if D.confirm(f"Stop '{name}'?"):
                msg = api.docker_container_action(name, "stop")
                D.success(msg) if "successfully" in msg else D.error(msg)
        elif choice == "4":
            name = D.ask("Service/container name")
            msg = api.docker_container_action(name, "restart")
            D.success(msg) if "successfully" in msg else D.error(msg)
        elif choice == "5":
            compose_path = D.ask(f"Compose file (default: {COMPOSE_FILE})")
            compose_path = compose_path.strip() or COMPOSE_FILE
            D.info(f"Starting all services from {compose_path}...")
            _run_cmd(["docker", "compose", "-f", compose_path, "up", "-d"])
        elif choice == "6":
            compose_path = D.ask(f"Compose file (default: {COMPOSE_FILE})")
            compose_path = compose_path.strip() or COMPOSE_FILE
            if D.confirm("Stop all services?"):
                _run_cmd(["docker", "compose", "-f", compose_path, "down"])
        elif choice == "7":
            compose_path = D.ask(f"Compose file (default: {COMPOSE_FILE})")
            compose_path = compose_path.strip() or COMPOSE_FILE
            D.info("Pulling latest images...")
            _run_cmd(["docker", "compose", "-f", compose_path, "pull"])
        elif choice == "8":
            from gas_terminal.modules.monitoring import check_all_health
            check_all_health()
        elif choice == "9":
            name = D.ask("Service name (docker-compose service name)")
            compose_path = D.ask(f"Compose file (default: {COMPOSE_FILE})")
            compose_path = compose_path.strip() or COMPOSE_FILE
            D.info(f"Rebuilding and restarting {name}...")
            _run_cmd(["docker", "compose", "-f", compose_path, "up", "-d", "--build", name])
        D.press_enter()

def _run_cmd(cmd: list):
    D.info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd)
    except FileNotFoundError:
        D.error(f"Command not found: {cmd[0]}")
    except KeyboardInterrupt:
        D.info("Interrupted.")
