"""GAS Terminal v3 — Display utilities using Rich"""
from __future__ import annotations
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.columns import Columns
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax
from rich import box
from rich.live import Live
from rich.layout import Layout
import time

console = Console()

BRAND   = "GAS TERMINAL v3"
TAGLINE = "Golden AI Strategy · AI Trading OS"

THEME = {
    "primary":   "bold cyan",
    "secondary": "bold yellow",
    "success":   "bold green",
    "error":     "bold red",
    "warning":   "bold orange1",
    "dim":       "dim white",
    "header":    "bold white on dark_blue",
    "market_up": "bold bright_green",
    "market_dn": "bold bright_red",
}

def banner(containers: int = 0, agents: int = 0, models: str = "Claude / GPT / DeepSeek") -> None:
    """Print the GAS Terminal header banner."""
    console.print()
    console.print(Panel(
        f"[bold cyan]{BRAND}[/bold cyan]\n[dim]{TAGLINE}[/dim]",
        border_style="cyan",
        padding=(0, 4),
    ))

def status_bar(containers: int, agents: int, feed: str = "MT5 + Binance") -> None:
    """Print live system status bar."""
    from gas_terminal import config
    grid = Table.grid(expand=True, padding=(0, 2))
    grid.add_column()
    grid.add_column()
    grid.add_row("[dim]🌐 Website[/dim]",       f"[cyan]{config.WEBSITE_URL}[/cyan]")
    grid.add_row("[dim]🖥  Server[/dim]",        f"[white]{config.SERVER_NAME}[/white]")
    grid.add_row("[dim]🐳 Containers[/dim]",    f"[green]{containers} running[/green]")
    grid.add_row("[dim]🤖 AI Agents[/dim]",     f"[yellow]{agents} active[/yellow]")
    grid.add_row("[dim]🧠 AI Models[/dim]",     f"[magenta]{feed}[/magenta]")
    grid.add_row("[dim]📡 Market Feed[/dim]",   f"[cyan]{feed}[/cyan]")
    console.print(Panel(grid, border_style="dim", title="[dim]System Status[/dim]", title_align="left"))

def main_menu() -> None:
    """Print the 20-module main menu."""
    console.print()
    console.rule("[bold cyan]SELECT MODULE[/bold cyan]")
    console.print()

    items = [
        (" 1", "📊", "Technical Analysis System"),
        (" 2", "🌍", "Fundamental Analysis System"),
        (" 3", "⚡", "Hybrid & Risk System"),
        (" 4", "🧠", "Psychology & Growth"),
        (" 5", "🤖", "AI Agents Control"),
        (" 6", "🧠", "AI Models & Token Usage"),
        (" 7", "🧰", "AI Coding Tools"),
        (" 8", "📡", "Trading & Market Engine"),
        (" 9", "🛠", "DevOps & Infrastructure"),
        ("10", "📊", "Monitoring & Metrics"),
        ("11", "📜", "Logs & Debugger"),
        ("12", "🔔", "Alerts & Notification"),
        ("13", "🌐", "Website Control"),
        ("14", "📡", "Services Manager"),
        ("15", "🧪", "Quant Research Lab"),
        ("16", "⚙ ", "Automation & Scheduler"),
        ("17", "🔐", "Security & API Keys"),
        ("18", "🧭", "Help & Documentation"),
        ("19", "📈", "Live Chart Terminal"),
        ("20", "🎮", "AI Command Mode"),
        (" 0", "🚪", "Exit Terminal"),
    ]

    left  = items[:11]
    right = items[11:]

    left_col  = Table(show_header=False, box=None, padding=(0,1))
    right_col = Table(show_header=False, box=None, padding=(0,1))

    for num, icon, label in left:
        left_col.add_row(f"[cyan]{num}[/cyan]", icon, f"[white]{label}[/white]")
    for num, icon, label in right:
        right_col.add_row(f"[cyan]{num}[/cyan]", icon, f"[white]{label}[/white]")

    console.print(Columns([left_col, right_col], equal=True, expand=True))
    console.print()

def section_header(title: str, subtitle: str = "") -> None:
    """Print a section header panel."""
    content = f"[bold white]{title}[/bold white]"
    if subtitle:
        content += f"\n[dim]{subtitle}[/dim]"
    console.print(Panel(content, border_style="cyan", padding=(0,2)))
    console.print()

def sub_menu(items: list[tuple[str, str, str]], title: str) -> str:
    """
    Display a numbered sub-menu and return the user's choice.
    items: list of (num, icon, label)
    Returns chosen number string.
    """
    section_header(title)
    t = Table(show_header=False, box=None, padding=(0,1))
    for num, icon, label in items:
        t.add_row(f"[cyan]{num}[/cyan]", icon, f"[white]{label}[/white]")
    t.add_row("[dim]b[/dim]", "◀", "[dim]Back to Main Menu[/dim]")
    console.print(t)
    console.print()
    return Prompt.ask("[cyan]Select[/cyan]")

def result_panel(title: str, content: str, style: str = "green") -> None:
    console.print(Panel(content, title=f"[bold]{title}[/bold]", border_style=style))

def error(msg: str) -> None:
    console.print(f"[bold red]✗ {msg}[/bold red]")

def success(msg: str) -> None:
    console.print(f"[bold green]✓ {msg}[/bold green]")

def info(msg: str) -> None:
    console.print(f"[cyan]ℹ {msg}[/cyan]")

def warning(msg: str) -> None:
    console.print(f"[orange1]⚠ {msg}[/orange1]")

def spinner(label: str):
    """Context manager: show spinner while working."""
    return Progress(
        SpinnerColumn(),
        TextColumn(f"[cyan]{label}...[/cyan]"),
        transient=True,
    )

def press_enter() -> None:
    Prompt.ask("\n[dim]Press Enter to continue[/dim]", default="")

def ask(prompt: str) -> str:
    return Prompt.ask(f"[cyan]{prompt}[/cyan]")

def confirm(prompt: str) -> bool:
    return Confirm.ask(f"[yellow]{prompt}[/yellow]")

def data_table(headers: list[str], rows: list[list], title: str = "") -> None:
    """Generic data table."""
    t = Table(title=title, box=box.SIMPLE_HEAD, header_style="bold cyan")
    for h in headers:
        t.add_column(h)
    for row in rows:
        t.add_row(*[str(c) for c in row])
    console.print(t)
