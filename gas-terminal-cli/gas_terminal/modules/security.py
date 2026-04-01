"""GAS Terminal v3 — Module 17: Security & API Keys"""
from __future__ import annotations
import os
from pathlib import Path
from gas_terminal.utils import display as D
from gas_terminal import config

MENU = [
    ("1", "🔑", "View Current API Keys (masked)"),
    ("2", "✏ ", "Update API Key"),
    ("3", "🔐", "Rotate GAS JWT Token"),
    ("4", "🧹", "Clear Cached Tokens"),
    ("5", "🔍", "Scan for Exposed Secrets"),
    ("6", "🛡 ", "Security Audit"),
]

MASKED_VARS = [
    ("ANTHROPIC_API_KEY",   config.ANTHROPIC_API_KEY),
    ("GAS_TOKEN",           config.GAS_TOKEN),
    ("GAS_EMAIL",           config.GAS_EMAIL),
    ("TELEGRAM_BOT_TOKEN",  config.TELEGRAM_BOT_TOKEN),
    ("REDIS_URL",           config.REDIS_URL),
]

def _mask(value: str) -> str:
    if not value:
        return "[dim]not set[/dim]"
    if len(value) <= 8:
        return "*" * len(value)
    return value[:4] + "*" * (len(value) - 8) + value[-4:]

def run():
    while True:
        choice = D.sub_menu(MENU, "🔐 Security & API Keys")
        if choice == "b":
            break
        elif choice == "1":
            lines = []
            for name, value in MASKED_VARS:
                lines.append(f"[bold]{name}:[/bold] {_mask(value)}")
            D.result_panel("API Keys (Masked)", "\n".join(lines), style="yellow")
        elif choice == "2":
            var_name = D.ask("Variable name (e.g. ANTHROPIC_API_KEY)")
            new_value = D.ask(f"New value for {var_name}")
            if new_value.strip():
                _set_env_var(var_name.strip(), new_value.strip())
                D.success(f"{var_name} updated in .env")
            else:
                D.warning("No value entered, nothing changed.")
        elif choice == "3":
            from gas_terminal import api
            email = config.GAS_EMAIL
            if not email:
                email = D.ask("Email")
            password = D.ask("Password")
            if D.confirm(f"Re-login as {email} to rotate JWT token?"):
                result = api.run(api.login(email, password))
                token = result.get("access_token") or result.get("token")
                if token:
                    _set_env_var("GAS_TOKEN", token)
                    config.GAS_TOKEN = token
                    D.success("JWT token rotated and saved.")
                else:
                    D.error(f"Login failed: {result}")
        elif choice == "4":
            if D.confirm("Clear GAS_TOKEN from .env?"):
                _set_env_var("GAS_TOKEN", "")
                config.GAS_TOKEN = ""
                D.success("GAS_TOKEN cleared.")
        elif choice == "5":
            _scan_secrets()
        elif choice == "6":
            _security_audit()
        D.press_enter()

def _set_env_var(key: str, value: str):
    env_path = Path(config._env)
    try:
        if env_path.exists():
            lines = env_path.read_text().splitlines()
        else:
            lines = []
        new_lines = [l for l in lines if not l.startswith(f"{key}=")]
        if value:
            new_lines.append(f"{key}={value}")
        env_path.write_text("\n".join(new_lines) + "\n")
    except Exception as e:
        D.error(f"Could not update .env: {e}")

def _scan_secrets():
    D.info("Scanning for potentially exposed secrets in /root/gasstrategyai...")
    dangerous_patterns = [
        ("sk-ant-",         "Anthropic API key"),
        ("sk-",             "OpenAI API key"),
        ("AKIA",            "AWS Access Key"),
        ("ghp_",            "GitHub Personal Access Token"),
        ("AIza",            "Google API Key"),
        ("xoxb-",           "Slack Bot Token"),
        ("-----BEGIN RSA",  "RSA Private Key"),
    ]
    found = []
    base = Path("/root/gasstrategyai")
    skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv"}
    for path in base.rglob("*"):
        if any(skip in path.parts for skip in skip_dirs):
            continue
        if not path.is_file():
            continue
        if path.suffix in (".pyc", ".log", ".jpg", ".png", ".gif", ".ico", ".woff", ".ttf"):
            continue
        try:
            text = path.read_text(errors="ignore")
            for pattern, label in dangerous_patterns:
                if pattern in text:
                    found.append((str(path.relative_to(base)), label))
                    break
        except Exception:
            pass
    if found:
        D.warning(f"Found {len(found)} files with potential secrets:")
        rows = [[f, l] for f, l in found]
        D.data_table(["File", "Pattern"], rows, title="Potential Secret Exposure")
        D.warning("Add these files to .gitignore or rotate the keys.")
    else:
        D.success("No obvious secret exposures found.")

def _security_audit():
    lines = []
    # Check .env file permissions
    env_path = Path(config._env)
    if env_path.exists():
        mode = oct(env_path.stat().st_mode)[-3:]
        if mode in ("600", "400"):
            lines.append(f"[green]✓ .env permissions: {mode} (good)[/green]")
        else:
            lines.append(f"[red]✗ .env permissions: {mode} (should be 600)[/red]")
    else:
        lines.append("[yellow]⚠ .env file not found[/yellow]")
    # Check API keys set
    lines.append("")
    lines.append("[bold]API Keys:[/bold]")
    lines.append(f"  Anthropic: {'[green]set[/green]' if config.ANTHROPIC_API_KEY else '[red]not set[/red]'}")
    lines.append(f"  GAS Token: {'[green]set[/green]' if config.GAS_TOKEN else '[yellow]not set (login required)[/yellow]'}")
    lines.append(f"  Telegram:  {'[green]set[/green]' if config.TELEGRAM_BOT_TOKEN else '[dim]not set[/dim]'}")
    lines.append("")
    # Check .gitignore
    gitignore = Path("/root/gasstrategyai/.gitignore")
    if gitignore.exists():
        content = gitignore.read_text()
        if ".env" in content:
            lines.append("[green]✓ .env is in .gitignore[/green]")
        else:
            lines.append("[red]✗ .env is NOT in .gitignore — risk of credential exposure![/red]")
    D.result_panel("Security Audit", "\n".join(lines), style="yellow")
