"""GAS Terminal v3 — Module 18: Help & Documentation"""
from __future__ import annotations
from gas_terminal.utils import display as D
from gas_terminal import config

MENU = [
    ("1", "📖", "Quick Start Guide"),
    ("2", "🗺 ", "Full Feature Map"),
    ("3", "⌨ ", "CLI Commands Reference"),
    ("4", "🔗", "Service URLs"),
    ("5", "💡", "Tips & Tricks"),
    ("6", "📋", "About GAS Terminal"),
]

def run():
    while True:
        choice = D.sub_menu(MENU, "🧭 Help & Documentation")
        if choice == "b":
            break
        elif choice == "1":
            _quick_start()
        elif choice == "2":
            _feature_map()
        elif choice == "3":
            _cli_reference()
        elif choice == "4":
            _service_urls()
        elif choice == "5":
            _tips()
        elif choice == "6":
            _about()
        D.press_enter()

def _quick_start():
    D.result_panel("Quick Start Guide", """
[bold cyan]1. Setup[/bold cyan]
   cp .env.example .env
   nano .env   # fill in your credentials
   pip install -r requirements.txt
   pip install -e .

[bold cyan]2. Login[/bold cyan]
   gas login --email you@example.com

[bold cyan]3. Launch TUI[/bold cyan]
   gas            # opens interactive terminal
   gas terminal   # same

[bold cyan]4. CLI Commands[/bold cyan]
   gas ta analyze XAUUSD --tf H1
   gas signal generate EURUSD
   gas docker ps
   gas agent list
   gas status

[bold cyan]5. AI Command Mode[/bold cyan]
   gas ai analyze gold market
   gas ai what is the trend on EURUSD?
""", style="cyan")

def _feature_map():
    D.result_panel("GAS Feature Map (18 AI Features)", """
[bold yellow]Essential Plan ($2.99):[/bold yellow]
  1.  Technical Analysis    — SMC, indicators, patterns
  2.  Signal Generation     — Buy/sell signals with TP/SL
  3.  Session Analysis      — London/NY/Asia session context
  4.  Alert System          — Price & signal alerts

[bold yellow]Plus Plan ($5.99):[/bold yellow]
  5.  Correlation Matrix    — Asset correlation analysis
  6.  Fundamental Analysis  — Macro & fundamental data
  7.  Economic Calendar     — High-impact events AI
  8.  Market Sentiment      — Retail vs institutional sentiment
  9.  Risk Manager          — Position sizing & risk calc

[bold yellow]Premium Plan ($11.99):[/bold yellow]
  10. Hybrid Confluence     — TA + FA + Sentiment merged
  11. Drawdown Recovery     — Recovery planning AI
  12. Market Briefing       — AI daily/weekly briefing
  13. Psychology Coach      — Emotion & discipline AI
  14. Trade Journal AI      — Journal analysis & insights
  15. PropFirm Tracker      — Challenge rules & compliance

[bold yellow]Ultimate Plan ($19.99):[/bold yellow]
  16. Scanner (15cr)        — Multi-symbol opportunity scanner
  17. Backtesting (20cr)    — AI strategy backtesting engine
  18. Mentor Mode (10cr)    — AI mentor trade review
""", style="yellow")

def _cli_reference():
    D.result_panel("CLI Commands Reference", """
[bold]Auth:[/bold]
  gas login                       Login & save token
  gas status                      System overview

[bold]Analysis:[/bold]
  gas ta analyze XAUUSD --tf H1   Technical analysis
  gas ta signal EURUSD            Signal generation
  gas macro analyze XAUUSD        Fundamental analysis
  gas hybrid score XAUUSD         Hybrid confluence score
  gas sentiment check XAUUSD      Sentiment check
  gas sentiment market            Global sentiment

[bold]Calendar & Alerts:[/bold]
  gas calendar events --impact high
  gas calendar today

[bold]Risk & Backtest:[/bold]
  gas risk calculate --account 10000 --risk-pct 1.0
  gas backtest run --strategy smc_v1 --symbol XAUUSD

[bold]Psychology & Journal:[/bold]
  gas psychology check
  gas journal analyze
  gas journal review
  gas mentor review
  gas mentor trade

[bold]Charts:[/bold]
  gas chart show XAUUSD --tf M15 --type line
  gas chart candle XAUUSD --tf H1

[bold]Scanner:[/bold]
  gas scanner run --symbols XAUUSD,EURUSD,BTCUSDT
  gas scanner watchlist

[bold]Agents:[/bold]
  gas agent list
  gas agent status
  gas agent start market_analyst
  gas agent stop signal_bot
  gas agent logs market_analyst

[bold]Docker:[/bold]
  gas docker ps
  gas docker start <name>
  gas docker stop <name>
  gas docker restart <name>
  gas docker logs <name> --tail 100

[bold]Dev Tools:[/bold]
  gas dev claude "fix the login bug"
  gas dev review /path/to/code
  gas dev fix-bug "TypeError on line 42"
  gas dev refactor /path/to/file.py

[bold]Monitoring:[/bold]
  gas monitor health
  gas monitor metrics

[bold]Automation:[/bold]
  gas auto analyze-market --symbols XAUUSD,EURUSD
  gas auto scan-watchlist
  gas auto fix-services
  gas auto code-review /root/gasstrategyai

[bold]AI Mode:[/bold]
  gas ai analyze gold for next week
  gas ai what are key risks today?
""")

def _service_urls():
    D.data_table(
        ["Service", "URL"],
        [
            ["Gateway",           config.GATEWAY_URL],
            ["Web Backend",       config.WEB_BACKEND_URL],
            ["Terminal Backend",  config.TERMINAL_BACKEND_URL],
            ["Auth Service",      config.AUTH_URL],
            ["Agent Engine",      config.AGENT_ENGINE_URL],
            ["MT5 WebSocket",     config.MT5_WEBSOCKET_URL],
            ["Binance Service",   config.BINANCE_SERVICE_URL],
            ["Signal Service",    config.SIGNAL_SERVICE_URL],
            ["SMC Engine",        config.SMC_ENGINE_URL],
            ["Risk Engine",       config.RISK_ENGINE_URL],
            ["Quant Backtester",  config.QUANT_BACKTESTER_URL],
            ["Screener",          config.SCREENER_SERVICE_URL],
            ["Calendar/News",     config.CALENDAR_NEWS_URL],
            ["Redis",             config.REDIS_URL],
        ],
        title="Service URLs"
    )

def _tips():
    D.result_panel("Tips & Tricks", """
[bold cyan]• Headless automation:[/bold cyan]
  Use 'gas auto *' commands in cron jobs for scheduled analysis.

[bold cyan]• Quick AI commands:[/bold cyan]
  'gas ai <natural language>' — describe what you want in plain English.

[bold cyan]• Token saving:[/bold cyan]
  Run 'gas login' once — token is saved to .env and reused.

[bold cyan]• Docker shortcuts:[/bold cyan]
  'gas docker ps' shows all containers with color-coded status.
  'gas auto fix-services' auto-restarts any stopped containers.

[bold cyan]• AI Code Tools:[/bold cyan]
  'gas dev claude' launches interactive Claude Code.
  'gas dev review .' reviews entire current directory.

[bold cyan]• Keyboard shortcuts in TUI:[/bold cyan]
  Press 'b' at any submenu to go back.
  Press Ctrl+C at any time to interrupt.
  Press '0' or 'q' at main menu to exit.

[bold cyan]• Redis inspection:[/bold cyan]
  Use module 11 (Logs) → Redis Stream Viewer to inspect live data.
""")

def _about():
    D.result_panel("About GAS Terminal v3", f"""
[bold cyan]GAS Terminal v3 — Golden AI Strategy[/bold cyan]
[dim]AI Trading & DevOps Command Center[/dim]

Version:      3.0.0
Website:      {config.WEBSITE_URL}
Server:       {config.SERVER_NAME}

[bold]Stack:[/bold]
  • Python 3.11+ / Click / Rich
  • FastAPI microservices backend
  • Anthropic Claude AI models
  • Docker / Redis / PostgreSQL

[bold]AI Models:[/bold]
  Complex:  {config.MODEL_COMPLEX}
  Fast:     {config.MODEL_FAST}

[bold]Features:[/bold]
  • 18 AI trading analysis features
  • 20 interactive TUI modules
  • 50+ CLI subcommands
  • Headless automation support
  • Docker DevOps management
  • Natural language AI mode
""", style="cyan")
