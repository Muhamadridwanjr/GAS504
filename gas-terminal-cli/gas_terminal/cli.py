"""
GAS Terminal v3 — CLI Entry Point
Invoke with: gas [command] [subcommand] [args]
             gas terminal    → interactive TUI
"""
from __future__ import annotations
import os
import sys
import subprocess
import asyncio
import click
from rich.console import Console
from gas_terminal.utils import display as D
from gas_terminal import api, config

console = Console()


@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """GAS Terminal v3 — AI Trading & DevOps Command Center"""
    if ctx.invoked_subcommand is None:
        # Default: open interactive TUI
        from gas_terminal.app import run_app
        run_app()


# ── Interactive terminal ──────────────────────────────────────────────

@main.command()
def terminal():
    """Launch the interactive GAS Terminal TUI."""
    from gas_terminal.app import run_app
    run_app()


# ── Auth ──────────────────────────────────────────────────────────────

@main.command()
@click.option("--email",    prompt="Email",    default=config.GAS_EMAIL)
@click.option("--password", prompt="Password", hide_input=True, default=config.GAS_PASSWORD)
def login(email, password):
    """Login to GAS platform and save JWT token."""
    with D.spinner("Logging in"):
        result = api.run(api.login(email, password))
    token = result.get("access_token") or result.get("token")
    if token:
        # Write to .env
        env_path = os.path.join(os.path.dirname(__file__), "..", ".env")
        _set_env(env_path, "GAS_TOKEN", token)
        config.GAS_TOKEN = token
        D.success(f"Logged in. Token saved to .env")
    else:
        D.error(f"Login failed: {result}")


def _set_env(path: str, key: str, value: str):
    try:
        with open(path, "a+") as f:
            f.seek(0)
            lines = f.readlines()
        new_lines = [l for l in lines if not l.startswith(f"{key}=")]
        new_lines.append(f"{key}={value}\n")
        with open(path, "w") as f:
            f.writelines(new_lines)
    except Exception:
        pass


# ── Technical Analysis ─────────────────────────────────────────────────

@main.group("ta")
def ta():
    """Technical Analysis commands."""
    pass

@ta.command("analyze")
@click.argument("symbol", default="XAUUSD")
@click.option("--tf", default="H1", help="Timeframe")
def ta_analyze(symbol, tf):
    """Run Technical Analysis AI on a symbol."""
    D.info(f"Analyzing {symbol} on {tf}...")
    result = api.run(api.ai_feature("technical", {"symbol": symbol, "timeframe": tf}))
    if "error" in result:
        D.error(result["error"])
    else:
        _print_analysis(result, f"Technical Analysis — {symbol} {tf}")

@ta.command("signal")
@click.argument("symbol", default="XAUUSD")
def ta_signal(symbol):
    """Generate trading signal for a symbol."""
    result = api.run(api.ai_feature("signal", {"symbol": symbol}))
    _print_analysis(result, f"Signal — {symbol}")


# ── Signal ─────────────────────────────────────────────────────────────

@main.group()
def signal():
    """Signal system commands."""
    pass

@signal.command("generate")
@click.argument("symbol", default="XAUUSD")
def signal_generate(symbol):
    """Generate AI signal for symbol."""
    result = api.run(api.ai_feature("signal", {"symbol": symbol}))
    _print_analysis(result, f"Signal — {symbol}")

@signal.command("feed")
def signal_feed():
    """Show live signal feed from terminal backend."""
    result = api.run(api.terminal_signals())
    D.data_table(
        ["Symbol", "Direction", "Confidence", "Entry", "TP", "SL"],
        [[s.get("symbol"), s.get("direction"), s.get("confidence"),
          s.get("entry"), s.get("tp"), s.get("sl")] for s in (result if isinstance(result, list) else [result])],
        title="Signal Feed"
    )


# ── Scanner ────────────────────────────────────────────────────────────

@main.group()
def scanner():
    """Multi-symbol scanner commands."""
    pass

@scanner.command("run")
@click.option("--symbols", default="XAUUSD,EURUSD,BTCUSDT", help="Comma-separated symbols")
def scanner_run(symbols):
    """Run multi-symbol AI scanner."""
    sym_list = symbols.split(",")
    result = api.run(api.ai_feature("scanner", {"symbols": sym_list}))
    _print_analysis(result, "Scanner Results")

@scanner.command("watchlist")
def scanner_watchlist():
    """Show watchlist with market direction."""
    pairs = api.run(api.terminal_pairs())
    rows = []
    for p in (pairs if isinstance(pairs, list) else []):
        trend = p.get("trend", "→")
        emoji = "📈" if trend == "bullish" else "📉" if trend == "bearish" else "➡"
        rows.append([p.get("symbol", ""), emoji, p.get("price", ""), p.get("change_pct", "")])
    D.data_table(["Symbol", "", "Price", "Change%"], rows, title="Watchlist")


# ── Macro / Fundamental ───────────────────────────────────────────────

@main.group()
def macro():
    """Fundamental analysis commands."""
    pass

@macro.command("analyze")
@click.argument("symbol", default="XAUUSD")
def macro_analyze(symbol):
    """Run Fundamental Analysis AI."""
    result = api.run(api.ai_feature("fundamental", {"symbol": symbol}))
    _print_analysis(result, f"Fundamental — {symbol}")


# ── Calendar ────────────────────────────────────────────────────────────

@main.group()
def calendar():
    """Economic calendar commands."""
    pass

@calendar.command("events")
@click.option("--impact", default="high", type=click.Choice(["all", "low", "medium", "high"]))
def calendar_events(impact):
    """Show economic calendar events."""
    events = api.run(api.terminal_calendar())
    rows = []
    for e in (events if isinstance(events, list) else []):
        if impact != "all" and e.get("impact", "").lower() != impact:
            continue
        rows.append([e.get("time", ""), e.get("currency", ""), e.get("event", ""), e.get("impact", ""), e.get("forecast", ""), e.get("previous", "")])
    D.data_table(["Time", "CCY", "Event", "Impact", "Forecast", "Previous"], rows, title="Economic Calendar")

@calendar.command("today")
def calendar_today():
    """Show today's high-impact events."""
    from datetime import date
    result = api.run(api.ai_feature("calendar", {"date": str(date.today())}))
    _print_analysis(result, "Calendar AI — Today")


# ── Sentiment ─────────────────────────────────────────────────────────

@main.group()
def sentiment():
    """Sentiment analysis commands."""
    pass

@sentiment.command("check")
@click.argument("symbol", default="XAUUSD")
def sentiment_check(symbol):
    """Check market sentiment for a symbol."""
    result = api.run(api.ai_feature("sentiment", {"symbol": symbol}))
    _print_analysis(result, f"Sentiment — {symbol}")

@sentiment.command("market")
def sentiment_market():
    """Overall market sentiment."""
    result = api.run(api.ai_feature("sentiment", {"scope": "global"}))
    _print_analysis(result, "Global Sentiment")


# ── Hybrid ────────────────────────────────────────────────────────────

@main.group()
def hybrid():
    """Hybrid AI system (TA + FA + Sentiment)."""
    pass

@hybrid.command("score")
@click.argument("symbol", default="XAUUSD")
def hybrid_score(symbol):
    """Get hybrid confluence score."""
    result = api.run(api.ai_feature("hybrid", {"symbol": symbol}))
    _print_analysis(result, f"Hybrid Score — {symbol}")


# ── Risk ──────────────────────────────────────────────────────────────

@main.group()
def risk():
    """Risk management commands."""
    pass

@risk.command("calculate")
@click.option("--account", default=10000.0, help="Account balance")
@click.option("--risk-pct", default=1.0, help="Risk percentage")
@click.option("--symbol", default="XAUUSD")
def risk_calculate(account, risk_pct, symbol):
    """Calculate position size and risk."""
    result = api.run(api.ai_feature("risk", {
        "account_balance": account,
        "risk_percentage": risk_pct,
        "symbol": symbol
    }))
    _print_analysis(result, "Risk Calculation")


# ── Backtest ──────────────────────────────────────────────────────────

@main.group()
def backtest():
    """Backtesting commands."""
    pass

@backtest.command("run")
@click.option("--strategy", default="smc_v1")
@click.option("--symbol", default="XAUUSD")
@click.option("--from-date", default="2024-01-01")
@click.option("--to-date", default="2024-12-31")
def backtest_run(strategy, symbol, from_date, to_date):
    """Run AI backtesting engine."""
    result = api.run(api.ai_feature("backtesting", {
        "strategy": strategy,
        "symbol": symbol,
        "from_date": from_date,
        "to_date": to_date
    }))
    _print_analysis(result, f"Backtest — {strategy} on {symbol}")


# ── Psychology ────────────────────────────────────────────────────────

@main.group()
def psychology():
    """Psychology coach commands."""
    pass

@psychology.command("check")
def psychology_check():
    """Check trader psychology state."""
    result = api.run(api.ai_feature("psychology", {}))
    _print_analysis(result, "Psychology Coach")


# ── Journal ───────────────────────────────────────────────────────────

@main.group()
def journal():
    """Trade journal commands."""
    pass

@journal.command("analyze")
def journal_analyze():
    """AI analysis of trade journal."""
    result = api.run(api.ai_feature("journal", {}))
    _print_analysis(result, "Journal AI")

@journal.command("review")
def journal_review():
    """Review recent journal entries."""
    result = api.run(api.ai_feature("journal", {"action": "review"}))
    _print_analysis(result, "Journal Review")


# ── Mentor ────────────────────────────────────────────────────────────

@main.group()
def mentor():
    """AI Mentor Mode commands."""
    pass

@mentor.command("review")
@click.argument("trade_id", required=False)
def mentor_review(trade_id):
    """AI mentor reviews your last trade."""
    result = api.run(api.ai_feature("mentor", {"trade_id": trade_id}))
    _print_analysis(result, "Mentor AI")

@mentor.command("trade")
def mentor_trade():
    """Get mentoring on current market setup."""
    result = api.run(api.ai_feature("mentor", {"mode": "live"}))
    _print_analysis(result, "Mentor — Live Setup")


# ── Chart ─────────────────────────────────────────────────────────────

@main.group()
def chart():
    """Live chart commands."""
    pass

@chart.command("show")
@click.argument("symbol", default="XAUUSD")
@click.option("--tf", default="M15")
@click.option("--type", "chart_type", default="line", type=click.Choice(["line", "candle"]))
def chart_show(symbol, tf, chart_type):
    """Show live chart in terminal."""
    from gas_terminal.modules import charts
    charts.show_chart(symbol, tf, chart_type)

@chart.command("candle")
@click.argument("symbol", default="XAUUSD")
@click.option("--tf", default="M15")
def chart_candle(symbol, tf):
    """Show candlestick chart."""
    from gas_terminal.modules import charts
    charts.show_chart(symbol, tf, "candle")


# ── Agents ────────────────────────────────────────────────────────────

@main.group()
def agent():
    """AI Agent control commands."""
    pass

@agent.command("list")
@click.option("--domain", default=None)
def agent_list(domain):
    """List all registered AI agents."""
    data = api.run(api.agents_list(domain))
    agents = data.get("agents", [])
    domains = data.get("domains", [])
    D.info(f"Domains: {', '.join(domains)}")
    console.print("\n".join(f"  [cyan]•[/cyan] {a}" for a in agents))

@agent.command("status")
def agent_status():
    """Show orchestrator status."""
    data = api.run(api.agents_status())
    D.result_panel("Agent Status",
        f"Total: {data.get('total_agents',0)}  Running: {data.get('running',0)}  Errors: {data.get('errors',0)}")

@agent.command("start")
@click.argument("name")
def agent_start(name):
    """Dispatch/start a specific agent."""
    result = api.run(api.agent_dispatch(name))
    if result.get("success"):
        D.success(f"Agent '{name}' executed — {result.get('duration_ms',0):.0f}ms")
    else:
        D.error(f"Agent failed: {result.get('error', 'unknown')}")

@agent.command("stop")
@click.argument("name")
def agent_stop(name):
    """Pause an agent."""
    result = api.run(api.agent_pause(name))
    D.success(f"Agent '{name}' paused") if "paused" in str(result) else D.error(str(result))

@agent.command("logs")
@click.argument("name")
def agent_logs(name):
    """Show agent run logs from Redis."""
    msgs = api.redis_stream_read(f"gas:events:agent:{name}", count=20)
    if not msgs:
        D.info(f"No logs found for agent '{name}'")
        return
    for msg_id, fields in msgs:
        console.print(f"[dim]{msg_id.decode() if isinstance(msg_id, bytes) else msg_id}[/dim] {fields}")


# ── DevOps / Docker ──────────────────────────────────────────────────

@main.group()
def docker():
    """Docker container management."""
    pass

@docker.command("ps")
def docker_ps():
    """List all containers."""
    containers = api.docker_containers()
    rows = [[c.get("name",""), c.get("status",""), c.get("image",""), c.get("id","")] for c in containers]
    D.data_table(["Name", "Status", "Image", "ID"], rows, title="Docker Containers")

@docker.command("start")
@click.argument("name")
def docker_start(name):
    """Start a container."""
    msg = api.docker_container_action(name, "start")
    D.success(msg) if "successfully" in msg else D.error(msg)

@docker.command("stop")
@click.argument("name")
def docker_stop(name):
    """Stop a container."""
    msg = api.docker_container_action(name, "stop")
    D.success(msg) if "successfully" in msg else D.error(msg)

@docker.command("restart")
@click.argument("name")
def docker_restart(name):
    """Restart a container."""
    msg = api.docker_container_action(name, "restart")
    D.success(msg) if "successfully" in msg else D.error(msg)

@docker.command("logs")
@click.argument("name")
@click.option("--tail", default=50)
def docker_logs(name, tail):
    """Tail container logs."""
    try:
        import docker as dk
        client = dk.from_env()
        c = client.containers.get(name)
        logs = c.logs(tail=tail).decode(errors="replace")
        console.print(logs)
    except Exception as e:
        D.error(str(e))


# ── Dev Tools ─────────────────────────────────────────────────────────

@main.group("dev")
def dev():
    """AI coding tools (Claude Code, Aider)."""
    pass

@dev.command("claude")
@click.argument("prompt", required=False)
def dev_claude(prompt):
    """Launch Claude Code CLI."""
    cmd = ["claude"]
    if prompt:
        cmd.extend(["-p", prompt])
    subprocess.run(cmd)

@dev.command("aider")
@click.argument("files", nargs=-1)
def dev_aider(files):
    """Launch Aider AI coding agent."""
    cmd = ["aider"] + list(files)
    subprocess.run(cmd)

@dev.command("review")
@click.argument("path", default=".")
def dev_review(path):
    """AI code review via Claude Code."""
    subprocess.run(["claude", "-p", f"Review the code in {path} and identify issues, bugs, and improvements"])

@dev.command("fix-bug")
@click.argument("description")
def dev_fix_bug(description):
    """Ask Claude Code to fix a bug."""
    subprocess.run(["claude", "-p", f"Fix this bug: {description}"])

@dev.command("refactor")
@click.argument("path")
def dev_refactor(path):
    """Auto-refactor code with AI."""
    subprocess.run(["aider", "--message", f"Refactor {path} for better readability and performance", path])


# ── Monitoring ─────────────────────────────────────────────────────────

@main.group()
def monitor():
    """Monitoring and metrics commands."""
    pass

@monitor.command("health")
def monitor_health():
    """Check health of all services."""
    from gas_terminal.modules import monitoring
    monitoring.check_all_health()

@monitor.command("metrics")
def monitor_metrics():
    """Show system metrics dashboard."""
    from gas_terminal.modules import monitoring
    monitoring.show_metrics()


# ── Automation ─────────────────────────────────────────────────────────

@main.group("auto")
def auto():
    """Headless automation commands."""
    pass

@auto.command("analyze-market")
@click.option("--symbols", default="XAUUSD,EURUSD,BTCUSDT")
def auto_analyze_market(symbols):
    """Auto analyze multiple symbols headlessly."""
    sym_list = symbols.split(",")
    for sym in sym_list:
        D.info(f"Analyzing {sym}...")
        result = api.run(api.ai_feature("technical", {"symbol": sym}))
        summary = result.get("summary") or result.get("analysis") or str(result)[:200]
        console.print(f"  [green]{sym}[/green]: {summary}")

@auto.command("scan-watchlist")
def auto_scan_watchlist():
    """Auto scan all watchlist symbols."""
    pairs = api.run(api.terminal_pairs())
    symbols = [p.get("symbol") for p in (pairs if isinstance(pairs, list) else []) if p.get("symbol")]
    if not symbols:
        symbols = ["XAUUSD", "EURUSD", "BTCUSDT"]
    result = api.run(api.ai_feature("scanner", {"symbols": symbols}))
    _print_analysis(result, "Auto Scan Results")

@auto.command("fix-services")
def auto_fix_services():
    """Auto restart failed/stopped containers."""
    containers = api.docker_containers()
    fixed = 0
    for c in containers:
        if c.get("status") in ("exited", "dead"):
            msg = api.docker_container_action(c["name"], "start")
            D.info(f"Restarting {c['name']}: {msg}")
            fixed += 1
    D.success(f"Fixed {fixed} containers") if fixed else D.info("All containers running")

@auto.command("code-review")
@click.argument("path", default=".")
def auto_code_review(path):
    """AI automatic code review."""
    subprocess.run(["claude", "-p",
        f"Do a comprehensive code review of {path}. List critical issues, security vulnerabilities, and top 5 improvements."])


# ── AI Command Mode ────────────────────────────────────────────────────

@main.command("ai")
@click.argument("prompt", nargs=-1, required=False)
def ai_command(prompt):
    """
    Natural language AI command mode.
    Example: gas ai analyze gold market
    """
    if prompt:
        query = " ".join(prompt)
        from gas_terminal.modules.ai_command import run_nl_command
        run_nl_command(query)
    else:
        from gas_terminal.modules.ai_command import run_interactive_mode
        run_interactive_mode()


# ── Status / Health ───────────────────────────────────────────────────

@main.command("status")
def status():
    """Quick system status overview."""
    D.banner()
    stats = api.docker_stats()
    agent_data = api.run(api.agents_status())
    web_h = api.run(api.web_health())
    D.result_panel("System Status",
        f"🐳 Containers: {stats['running']}/{stats['total']} running\n"
        f"🤖 Agents: {agent_data.get('total_agents',0)} registered, {agent_data.get('running',0)} running\n"
        f"🌐 Web Backend: {web_h.get('status','unknown')}\n"
        f"📡 Market Feed: {'OK' if api.run(api.terminal_overview()) else 'N/A'}")


# ── Helpers ────────────────────────────────────────────────────────────

def _print_analysis(result: dict, title: str) -> None:
    if isinstance(result, str):
        D.result_panel(title, result)
        return
    if "error" in result:
        D.error(f"{title}: {result['error']}")
        return
    lines = []
    for k, v in result.items():
        if isinstance(v, dict):
            lines.append(f"[bold]{k}:[/bold]")
            for kk, vv in v.items():
                lines.append(f"  {kk}: {vv}")
        elif isinstance(v, list):
            lines.append(f"[bold]{k}:[/bold] {', '.join(str(i) for i in v[:5])}")
        else:
            lines.append(f"[bold]{k}:[/bold] {v}")
    D.result_panel(title, "\n".join(lines))


if __name__ == "__main__":
    main()
