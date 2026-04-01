"""GAS Terminal v3 — Interactive TUI App"""
from __future__ import annotations
import sys
import subprocess
from rich.prompt import Prompt
from rich.console import Console
from gas_terminal.utils import display as D
from gas_terminal import api, config

console = Console()

# ── Module imports (lazy to keep startup fast) ─────────────────────────

def _mod(name: str):
    import importlib
    return importlib.import_module(f"gas_terminal.modules.{name}")


class GASTerminal:
    def __init__(self):
        self._running = True

    def _system_stats(self) -> tuple[int, int]:
        """Quick system snapshot: (containers_running, agents_active)"""
        try:
            stats = api.docker_stats()
            containers = stats.get("running", 0)
        except Exception:
            containers = 0
        try:
            agent_data = api.run(api.agents_status())
            agents = agent_data.get("total_agents", 0)
        except Exception:
            agents = 0
        return containers, agents

    def run(self):
        """Main interactive loop."""
        D.banner()
        containers, agents = self._system_stats()
        D.status_bar(containers, agents)

        while self._running:
            D.main_menu()
            choice = Prompt.ask("[bold cyan]GAS >[/bold cyan]").strip()
            self._route(choice)

    def _route(self, choice: str):
        handlers = {
            "1":  lambda: _mod("technical").run(),
            "2":  lambda: _mod("fundamental").run(),
            "3":  lambda: _mod("hybrid").run(),
            "4":  lambda: _mod("psychology").run(),
            "5":  lambda: _mod("agents").run(),
            "6":  lambda: _mod("models").run(),
            "7":  lambda: _mod("devtools").run(),
            "8":  lambda: _mod("trading").run(),
            "9":  lambda: _mod("devops").run(),
            "10": lambda: _mod("monitoring").run(),
            "11": lambda: _mod("logs").run(),
            "12": lambda: _mod("alerts").run(),
            "13": lambda: _mod("website").run(),
            "14": lambda: _mod("services").run(),
            "15": lambda: _mod("quant").run(),
            "16": lambda: _mod("automation").run(),
            "17": lambda: _mod("security").run(),
            "18": lambda: _mod("help").run(),
            "19": lambda: _mod("charts").run(),
            "20": lambda: _mod("ai_command").run(),
            "0":  self._exit,
            "q":  self._exit,
            "exit": self._exit,
        }
        fn = handlers.get(choice.lower())
        if fn:
            try:
                fn()
            except KeyboardInterrupt:
                console.print("\n[dim]Interrupted — back to main menu[/dim]")
            except Exception as e:
                D.error(f"Module error: {e}")
                D.press_enter()
        else:
            D.warning(f"Unknown option: '{choice}'")

    def _exit(self):
        console.print("\n[bold cyan]Goodbye from GAS Terminal v3 👋[/bold cyan]\n")
        self._running = False


def run_app():
    GASTerminal().run()
