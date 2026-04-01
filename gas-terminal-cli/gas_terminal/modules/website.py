"""GAS Terminal v3 — Module 13: Website Control"""
from __future__ import annotations
import subprocess
from gas_terminal.utils import display as D
from gas_terminal import config

MENU = [
    ("1", "🌐", "Check Website Status"),
    ("2", "🔄", "Reload Nginx"),
    ("3", "🔐", "Renew SSL Certificate"),
    ("4", "📋", "View Nginx Config"),
    ("5", "🛠", "Test Nginx Config"),
    ("6", "📊", "Website Access Logs"),
    ("7", "🚀", "Deploy Frontend (npm build)"),
    ("8", "📁", "List Domains"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🌐 Website Control")
        if choice == "b":
            break
        elif choice == "1":
            _check_website()
        elif choice == "2":
            if D.confirm("Reload Nginx configuration?"):
                _run_cmd(["nginx", "-s", "reload"])
        elif choice == "3":
            domain = D.ask(f"Domain (default: {config.WEBSITE_URL})")
            domain = domain.strip() or config.WEBSITE_URL
            if D.confirm(f"Renew SSL certificate for {domain}?"):
                _run_cmd(["certbot", "renew", "--nginx", "-d", domain])
        elif choice == "4":
            nginx_conf = D.ask("Nginx config path (default: /etc/nginx/nginx.conf)")
            nginx_conf = nginx_conf.strip() or "/etc/nginx/nginx.conf"
            try:
                with open(nginx_conf, "r") as f:
                    content = f.read()
                from rich.syntax import Syntax
                D.console.print(Syntax(content, "nginx", theme="monokai", line_numbers=True))
            except FileNotFoundError:
                D.error(f"File not found: {nginx_conf}")
            except Exception as e:
                D.error(str(e))
        elif choice == "5":
            _run_cmd(["nginx", "-t"])
        elif choice == "6":
            log_path = D.ask("Access log path (default: /var/log/nginx/access.log)")
            log_path = log_path.strip() or "/var/log/nginx/access.log"
            tail = D.ask("Lines (default 50)")
            try:
                tail = int(tail)
            except ValueError:
                tail = 50
            try:
                with open(log_path, "r") as f:
                    lines = f.readlines()
                D.console.print("".join(lines[-tail:]))
            except Exception as e:
                D.error(str(e))
        elif choice == "7":
            frontend_path = D.ask("Frontend path (default: /root/gasstrategyai/gas-terminal-frontend)")
            frontend_path = frontend_path.strip() or "/root/gasstrategyai/gas-terminal-frontend"
            D.info(f"Building frontend at {frontend_path}...")
            _run_cmd(["npm", "run", "build"], cwd=frontend_path)
        elif choice == "8":
            import os
            domains_path = config.DOMAINS_BASE
            D.info(f"Domains directory: {domains_path}")
            try:
                entries = os.listdir(domains_path)
                rows = [[e] for e in sorted(entries)]
                D.data_table(["Domain / Config"], rows, title="Domains")
            except FileNotFoundError:
                D.error(f"Domains directory not found: {domains_path}")
            except Exception as e:
                D.error(str(e))
        D.press_enter()

def _check_website():
    try:
        import httpx
        url = f"https://{config.WEBSITE_URL}"
        D.info(f"Checking {url}...")
        r = httpx.get(url, timeout=10.0, follow_redirects=True)
        if r.status_code < 400:
            D.success(f"Website is UP — HTTP {r.status_code}")
        else:
            D.warning(f"Website returned HTTP {r.status_code}")
    except Exception as e:
        D.error(f"Website check failed: {e}")

def _run_cmd(cmd: list, cwd: str = None):
    D.info(f"Running: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, cwd=cwd)
    except FileNotFoundError:
        D.error(f"Command not found: {cmd[0]}")
    except KeyboardInterrupt:
        D.info("Interrupted.")
