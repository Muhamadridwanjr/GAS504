"""GAS Terminal v3 — Module 10: Monitoring & Metrics"""
from __future__ import annotations
import httpx
from gas_terminal.utils import display as D
from gas_terminal import api, config

MENU = [
    ("1", "❤ ", "Health Check — All Services"),
    ("2", "📊", "System Metrics Dashboard"),
    ("3", "🐳", "Docker Container Status"),
    ("4", "🤖", "Agent Engine Status"),
    ("5", "🗄 ", "Redis Status"),
    ("6", "🌐", "Web Backend Health"),
]

# All services to health-check
SERVICES = [
    ("Gateway",           config.GATEWAY_URL,          "/health"),
    ("Web Backend",       config.WEB_BACKEND_URL,       "/api/v1/health"),
    ("Terminal Backend",  config.TERMINAL_BACKEND_URL,  "/health"),
    ("Auth Service",      config.AUTH_URL,              "/health"),
    ("Agent Engine",      config.AGENT_ENGINE_URL,      "/health"),
    ("MT5 WebSocket",     config.MT5_WEBSOCKET_URL,     "/health"),
    ("Binance Service",   config.BINANCE_SERVICE_URL,   "/health"),
    ("Signal Service",    config.SIGNAL_SERVICE_URL,    "/health"),
    ("SMC Engine",        config.SMC_ENGINE_URL,        "/health"),
    ("Risk Engine",       config.RISK_ENGINE_URL,       "/health"),
    ("Quant Backtester",  config.QUANT_BACKTESTER_URL,  "/health"),
    ("Screener Service",  config.SCREENER_SERVICE_URL,  "/health"),
    ("Calendar/News",     config.CALENDAR_NEWS_URL,     "/health"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "📊 Monitoring & Metrics")
        if choice == "b":
            break
        elif choice == "1":
            check_all_health()
        elif choice == "2":
            show_metrics()
        elif choice == "3":
            containers = api.docker_containers()
            rows = []
            for c in containers:
                status = c.get("status", "")
                color = "green" if status == "running" else "red"
                rows.append([c.get("name",""), f"[{color}]{status}[/{color}]",
                             c.get("image",""), c.get("id","")])
            D.data_table(["Name", "Status", "Image", "ID"], rows, title="Container Status")
        elif choice == "4":
            data = api.run(api.agents_status())
            if data and "error" not in data:
                lines = [f"[bold]{k}:[/bold] {v}" for k, v in data.items()]
                D.result_panel("Agent Engine Status", "\n".join(lines), style="cyan")
            else:
                D.error(f"Agent engine unreachable: {data.get('error','unknown') if isinstance(data,dict) else data}")
        elif choice == "5":
            _check_redis()
        elif choice == "6":
            result = api.run(api.web_health())
            if result.get("status") == "unreachable":
                D.error(f"Web backend unreachable: {result.get('error','')}")
            else:
                lines = [f"[bold]{k}:[/bold] {v}" for k, v in result.items()]
                D.result_panel("Web Backend Health", "\n".join(lines), style="green")
        D.press_enter()

def check_all_health():
    """Check all services and print status table."""
    rows = []
    with httpx.Client(timeout=5.0) as client:
        for name, base_url, path in SERVICES:
            try:
                r = client.get(f"{base_url}{path}")
                status = "OK" if r.status_code < 400 else f"HTTP {r.status_code}"
                color = "green" if r.status_code < 400 else "red"
            except httpx.ConnectError:
                status = "DOWN"
                color = "red"
            except httpx.TimeoutException:
                status = "TIMEOUT"
                color = "yellow"
            except Exception as e:
                status = f"ERR: {str(e)[:30]}"
                color = "red"
            rows.append([name, base_url, f"[{color}]{status}[/{color}]"])
    D.data_table(["Service", "URL", "Status"], rows, title="Service Health Check")

def show_metrics():
    """Show system metrics from Docker + Redis."""
    docker_stats = api.docker_stats()
    agent_data = api.run(api.agents_status())
    web_health = api.run(api.web_health())

    lines = [
        "[bold cyan]── Docker ─────────────────[/bold cyan]",
        f"  Total containers:  {docker_stats.get('total', 0)}",
        f"  Running:           {docker_stats.get('running', 0)}",
        f"  Stopped:           {docker_stats.get('stopped', 0)}",
        "",
        "[bold cyan]── Agent Engine ───────────[/bold cyan]",
        f"  Total agents:      {agent_data.get('total_agents', 'N/A')}",
        f"  Running:           {agent_data.get('running', 'N/A')}",
        f"  Errors:            {agent_data.get('errors', 'N/A')}",
        "",
        "[bold cyan]── Web Backend ────────────[/bold cyan]",
        f"  Status:            {web_health.get('status', 'unknown')}",
    ]
    D.result_panel("System Metrics Dashboard", "\n".join(lines), style="cyan")

def _check_redis():
    try:
        import redis as r
        client = r.from_url(config.REDIS_URL)
        client.ping()
        info = client.info()
        D.result_panel("Redis Status",
            f"[bold]Status:[/bold]        Connected\n"
            f"[bold]Version:[/bold]       {info.get('redis_version','')}\n"
            f"[bold]Memory used:[/bold]   {info.get('used_memory_human','')}\n"
            f"[bold]Keys:[/bold]          {info.get('db0','N/A')}\n"
            f"[bold]Clients:[/bold]       {info.get('connected_clients','')}\n"
            f"[bold]Uptime (days):[/bold] {info.get('uptime_in_days','')}",
            style="green")
    except ImportError:
        D.error("redis package not installed. Run: pip install redis")
    except Exception as e:
        D.error(f"Redis unreachable: {e}")
