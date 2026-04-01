#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║  GAS GOLDEN AI — Unified Control System v1.0                    ║
║  CLI · Telegram Bot · Agent Manager · Docker Manager            ║
║  by Muhamad Ridwanjr                                            ║
╚══════════════════════════════════════════════════════════════════╝

Modes:
  python3 gas-golden-ai.py           → Interactive CLI
  python3 gas-golden-ai.py --bot     → Telegram Bot (PM2 mode)
  python3 gas-golden-ai.py --manage  → Docker Service Manager
  python3 gas-golden-ai.py --health  → Quick health check + exit

PM2 setup:
  pm2 start gas-golden-ai.py --interpreter python3 --name gas-bot -- --bot
  pm2 save
"""

import os, sys, json, time, signal, socket, shutil, subprocess, threading
import urllib.request, urllib.error, urllib.parse
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
#  PATHS & CONFIG
# ═══════════════════════════════════════════════════════════════
BASE        = Path(__file__).resolve().parent
CONFIG_FILE = BASE / ".gas-agent-config"
AGENTS_FILE = BASE / "tasks" / "agents.json"
TODO_FILE   = BASE / "tasks" / "todo.md"
USAGE_FILE  = BASE / "tasks" / "token_usage.json"

BOT_TOKEN = "7996917251:AAHkNqnmReO-szmWTXnLYvpNLVfhO1rFt6k"
BOT_USERS = {
    "ridwan": {"password": "gas2026!",  "role": "ADMIN"},
    "admin":  {"password": "golden123", "role": "ADMIN"},
}

# ═══════════════════════════════════════════════════════════════
#  COLORS (CLI)
# ═══════════════════════════════════════════════════════════════
R      = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
CORAL  = "\033[38;2;205;95;70m"
AMBER  = "\033[38;2;245;185;85m"
CREAM  = "\033[38;2;245;235;215m"
CYAN   = "\033[38;2;80;220;220m"
GREEN  = "\033[38;2;80;200;120m"
RED    = "\033[38;2;220;80;80m"
YELLOW = "\033[38;2;255;215;0m"
BLUE   = "\033[38;2;100;180;255m"
PURPLE = "\033[38;2;180;120;255m"

# ═══════════════════════════════════════════════════════════════
#  SERVICE DEFINITIONS
# ═══════════════════════════════════════════════════════════════
PORTS = {
    "gas-gateway-api":8000, "gas-auth-service":8001, "gas-user-service":8002,
    "gas-billing-service":8004, "gas-web-backend":8005, "gas-smc-engine":8006,
    "gas-terminal-backend":8085, "gas-engine-orchestrator":8105, "gas-signal-service":8106,
    "gas-journal-service":8107, "gas-mt5-websocket":8110, "gas-realtime-hub":8111,
    "gas-mt5-data-service":8100, "gas-indicator-engine":8203, "gas-alert-engine":8400,
    "gas-strategy-core":7003, "gas-ai-orchestrator":9003, "gas-rag-technical":9001,
    "gas-rag-macro":9002, "gas-vector-db":9004, "gas-feature-engine":9499,
    "gas-quant-orch":9500, "gas-pattern-detector":9501, "gas-statarb-engine":9502,
    "gas-regime-detector":9503, "gas-quant-backtester":9504, "gas-market-phase":9510,
    "gas-risk-engine":9511, "gas-correlation":9512, "gas-trend-engine":9513,
    "gas-orderflow":9514, "gas-screener-service":9600, "gas-calendar-news-service":9601,
    "gas-tradingplan-service":9602, "gas-fundamental-data-service":9603,
    "gas-data-ingestor":9604, "gas-binance-service":9612, "gas-chart-service":9700,
    "gas-terminal-frontend":3000,
}

SERVICES_BY_CAT = {
    "core":     ["gas-gateway-api","gas-auth-service","gas-user-service","gas-billing-service","gas-web-backend"],
    "data":     ["gas-mt5-websocket","gas-mt5-data-service","gas-data-ingestor","gas-calendar-news-service","gas-fundamental-data-service","gas-binance-service"],
    "engine":   ["gas-signal-service","gas-engine-orchestrator","gas-indicator-engine","gas-smc-engine","gas-strategy-core","gas-alert-engine"],
    "ai":       ["gas-ai-orchestrator","gas-rag-technical","gas-rag-macro","gas-vector-db"],
    "quant":    ["gas-quant-orch","gas-feature-engine","gas-regime-detector","gas-pattern-detector","gas-risk-engine","gas-correlation","gas-trend-engine"],
    "realtime": ["gas-realtime-hub","gas-terminal-backend","gas-terminal-frontend"],
    "infra":    ["gas-chart-service","gas-screener-service","gas-tradingplan-service"],
}

ALL_DOCKER_SERVICES = [
    "gas-ai-orchestrator","gas-alert-engine","gas-auth-service","gas-billing-service",
    "gas-binance-service","gas-calendar-news-service","gas-chart-service","gas-correlation",
    "gas-data-ingestor","gas-engine-orchestrator","gas-feature-engine","gas-fundamental-data-service",
    "gas-gateway-api","gas-indicator-engine","gas-journal-service","gas-market-phase",
    "gas-mt5-data-service","gas-mt5-websocket","gas-notification-service","gas-orderflow",
    "gas-pattern-detector","gas-quant-backtester","gas-quant-orch","gas-rag-macro",
    "gas-rag-technical","gas-realtime-hub","gas-regime-detector","gas-risk-engine",
    "gas-screener-service","gas-signal-service","gas-smc-engine","gas-statarb-engine",
    "gas-strategy-core","gas-term-service","gas-terminal-backend","gas-terminal-service",
    "gas-tradingplan-service","gas-trend-engine","gas-user-service","gas-vector-db","gas-web-backend",
]

AGENT_ROLES = {
    "1": ("ORCHESTRATOR", "ORCHESTRATOR.md",             "scan · decide · assign"),
    "2": ("ENGINEERING",  "divisions/ENGINEERING_MANAGER.md", "gateway · terminal · frontend"),
    "3": ("DATA",         "divisions/DATA_MANAGER.md",    "mt5 · scrapers · rag · realtime"),
    "4": ("TRADING",      "divisions/TRADING_MANAGER.md", "signal · quant · strategy · risk"),
    "5": ("PLATFORM",     "divisions/PLATFORM_MANAGER.md","auth · billing · telegram"),
    "6": ("DEVOPS",       "divisions/DEVOPS_MANAGER.md",  "docker · nginx · monitoring"),
    "7": ("SECURITY",     "divisions/SECURITY_MANAGER.md","firewall · audit · rate-limit"),
}

AI_MODELS = {
    # key: (label, provider, model_id, key_var, base_url)
    "1":  ("Claude Code [Primary]",             "claude_cli",   "",                                  "",                       ""),
    "2":  ("Kimi k2.5 [Moonshot Direct]",       "openai_compat","kimi-k2.5",                         "KIMI_API_KEY",           "https://api.moonshot.ai/v1"),
    "3":  ("Gemini 2.5 Flash [AI Studio]",      "gemini_studio","gemini-2.5-flash",                  "GEMINI_API_KEY",         ""),
    "4":  ("Gemini 2.5 Flash [Vertex AI]",      "vertex_ai",    "gemini-2.5-flash",                  "VERTEX_API_KEY",         ""),
    "5":  ("Kimi K2.5 [OpenRouter]",            "openrouter",   "moonshotai/kimi-k2.5",              "OPENROUTER_API_KEY",     ""),
    "6":  ("DeepSeek V3.2 [OpenRouter]",        "openrouter",   "deepseek/deepseek-v3.2",            "OPENROUTER_API_KEY",     ""),
    "7":  ("DeepSeek R1 [OpenRouter]",          "openrouter",   "deepseek/deepseek-r1-0528",         "OPENROUTER_API_KEY",     ""),
    "8":  ("Grok 4.20 Multi-Agent [OpenRouter]","openrouter",   "x-ai/grok-4.20-multi-agent-beta",   "OPENROUTER_API_KEY",     ""),
    "9":  ("Gemini 3.1 Flash Lite [OpenRouter]","openrouter",   "google/gemini-3.1-flash-lite-preview","OPENROUTER_API_KEY",   ""),
    "a":  ("Gemini 2.5 Flash [OpenRouter]",     "openrouter",   "google/gemini-2.5-flash",           "OPENROUTER_API_KEY",     ""),
    "b":  ("Gemini 2.5 Pro [OpenRouter]",       "openrouter",   "google/gemini-2.5-pro",             "OPENROUTER_API_KEY",     ""),
    "c":  ("DeepSeek V3 [Direct]",              "deepseek_api", "deepseek-chat",                     "DEEPSEEK_API_KEY",       ""),
    "d":  ("DeepSeek R1 [Direct]",              "deepseek_api", "deepseek-reasoner",                 "DEEPSEEK_API_KEY",       ""),
    "e":  ("Claude Haiku 4.5 [OpenRouter]",     "openrouter",   "anthropic/claude-haiku-4.5",        "OPENROUTER_API_KEY",     ""),
    "f":  ("Claude Sonnet 4.5 [OpenRouter]",    "openrouter",   "anthropic/claude-sonnet-4.5",       "OPENROUTER_API_KEY",     ""),
    "g":  ("Qwen3-Coder FREE [OpenRouter]",     "openrouter",   "qwen/qwen3-coder:free",             "OPENROUTER_API_KEY",     ""),
}

# ═══════════════════════════════════════════════════════════════
#  UTILITIES
# ═══════════════════════════════════════════════════════════════
def sh(cmd: str, timeout: int = 10) -> str:
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return r.stdout.strip()
    except Exception:
        return ""

def clear():
    os.system("clear")

def load_cfg() -> dict:
    cfg = {}
    if CONFIG_FILE.exists():
        for line in CONFIG_FILE.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                cfg[k.strip()] = v.strip()
    return cfg

def save_cfg_key(key: str, value: str):
    text = CONFIG_FILE.read_text() if CONFIG_FILE.exists() else ""
    lines = text.splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith(f"{key}="):
            lines[i] = f"{key}={value}"
            found = True
            break
    if not found:
        lines.append(f"{key}={value}")
    CONFIG_FILE.write_text("\n".join(lines) + "\n")

def ping_port(port: int, host: str = "localhost", timeout: float = 1.0) -> bool:
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except Exception:
        return False

def docker_status(name: str) -> str:
    out = sh(f"docker inspect --format='{{{{.State.Status}}}}' {name} 2>/dev/null")
    return out.strip("'") or "not found"

def fmt_status(s: str) -> str:
    c = {
        "running": GREEN, "exited": RED,
        "restarting": YELLOW, "not found": DIM,
    }.get(s, AMBER)
    return f"{c}{s}{R}"

# ═══════════════════════════════════════════════════════════════
#  AGENT PID MANAGER
# ═══════════════════════════════════════════════════════════════
def load_agents() -> dict:
    AGENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if AGENTS_FILE.exists():
        try:
            return json.loads(AGENTS_FILE.read_text())
        except Exception:
            pass
    return {}

def save_agents(data: dict):
    AGENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    AGENTS_FILE.write_text(json.dumps(data, indent=2))

def register_agent(role: str, pid: int, model: str = "claude"):
    agents = load_agents()
    agents[role] = {
        "pid":     pid,
        "model":   model,
        "started": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status":  "running",
    }
    save_agents(agents)

def unregister_agent(role: str):
    agents = load_agents()
    agents.pop(role, None)
    save_agents(agents)

def is_pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except (OSError, ProcessLookupError):
        return False

def get_live_agents() -> dict:
    agents = load_agents()
    live   = {}
    for role, info in agents.items():
        if is_pid_alive(info["pid"]):
            live[role] = info
        # else: stale entry, ignore
    return live

def kill_agent(role: str) -> str:
    agents = load_agents()
    info   = agents.get(role)
    if not info:
        return f"Agent {role} not found"
    pid = info["pid"]
    if is_pid_alive(pid):
        try:
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
            if is_pid_alive(pid):
                os.kill(pid, signal.SIGKILL)
            unregister_agent(role)
            return f"✅ Agent {role} (PID {pid}) killed"
        except Exception as e:
            return f"❌ Kill failed: {e}"
    unregister_agent(role)
    return f"Agent {role} was not alive (PID {pid} cleaned up)"

# ═══════════════════════════════════════════════════════════════
#  LAUNCH AGENTS
# ═══════════════════════════════════════════════════════════════
def launch_claude_agent(role_key: str):
    if role_key not in AGENT_ROLES:
        return
    role, md_file, desc = AGENT_ROLES[role_key]
    ctx_path = BASE / md_file

    cmd = ["claude", "--permission-mode", "dontAsk", "--name", f"GAS-{role}"]
    if ctx_path.exists():
        cmd += ["--append-system-prompt", ctx_path.read_text()]

    print(f"\n{CORAL}  ══════════════════════════════════════════{R}")
    print(f"  {BOLD}{CREAM}GAS-{role}{R}  {DIM}{desc}{R}")
    print(f"  {DIM}PID will be tracked in tasks/agents.json{R}")
    print(f"{CORAL}  ══════════════════════════════════════════{R}\n")
    time.sleep(0.3)

    try:
        proc = subprocess.Popen(cmd)
        register_agent(role, proc.pid, "claude")
        proc.wait()
    except KeyboardInterrupt:
        if proc.poll() is None:
            proc.terminate()
    finally:
        unregister_agent(role)


def launch_aider_model(model_key: str):
    cfg = load_cfg()
    if model_key not in AI_MODELS:
        print(f"{RED}Unknown model key{R}")
        return

    label, provider, model_id, key_var, base_url = AI_MODELS[model_key]
    api_key = cfg.get(key_var, "") if key_var else ""

    if provider != "claude_cli" and not api_key:
        print(f"{RED}  ⚠ {key_var} not set. Edit .gas-agent-config (press o){R}")
        time.sleep(2)
        return

    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)

    print(f"\n{CYAN}  Launching Aider → {label}{R}\n")
    time.sleep(0.3)

    if provider == "claude_cli":
        try:
            proc = subprocess.Popen(["claude", "--permission-mode", "dontAsk"])
            proc.wait()
        except KeyboardInterrupt:
            proc.terminate()
        return

    base_cmd = ["aider", "--no-auto-commits", "--dirty-commits"]

    if provider == "openrouter":
        env["OPENROUTER_API_KEY"] = api_key
        cmd = base_cmd + ["--model", f"openrouter/{model_id}"]

    elif provider == "openai_compat":
        env["OPENAI_API_BASE"] = base_url
        env["OPENAI_API_KEY"]  = api_key
        cmd = base_cmd + ["--model", f"openai/{model_id}"]

    elif provider == "gemini_studio":
        env["GEMINI_API_KEY"] = api_key
        cmd = base_cmd + ["--model", f"gemini/{model_id}"]

    elif provider == "vertex_ai":
        env["VERTEXAI_API_KEY"]  = api_key
        env["VERTEXAI_PROJECT"]  = cfg.get("VERTEX_PROJECT", "gen-lang-client-0060492434")
        env["VERTEXAI_LOCATION"] = "us-central1"
        cmd = base_cmd + ["--model", f"vertex_ai/{model_id}"]

    elif provider == "deepseek_api":
        env["DEEPSEEK_API_KEY"] = api_key
        cmd = base_cmd + ["--model", f"deepseek/{model_id}"]

    else:
        print(f"{RED}Unknown provider: {provider}{R}")
        return

    try:
        proc = subprocess.Popen(cmd, env=env, cwd=str(BASE))
        proc.wait()
    except FileNotFoundError:
        print(f"{RED}  ⚠ aider not found. Install: pip install aider-chat{R}")
        time.sleep(2)
    except KeyboardInterrupt:
        proc.terminate()

# ═══════════════════════════════════════════════════════════════
#  HEALTH CHECK
# ═══════════════════════════════════════════════════════════════
def check_health(verbose: bool = True) -> dict:
    results = {}
    for name, port in PORTS.items():
        ok = ping_port(port)
        results[name] = ok
        if verbose:
            icon = f"{GREEN}✅{R}" if ok else f"{RED}❌{R}"
            print(f"  {icon} {DIM}{name:<40}{R} :{port}")
    return results

# ═══════════════════════════════════════════════════════════════
#  TOKEN USAGE (delegates to gas_token_test.py)
# ═══════════════════════════════════════════════════════════════
def run_token_test(stats_only: bool = False):
    script = BASE / "scripts" / "gas_token_test.py"
    if not script.exists():
        print(f"{RED}  scripts/gas_token_test.py not found{R}")
        input(f"\n{DIM}[Enter]{R}")
        return
    flag = "--stats" if stats_only else ""
    subprocess.run(f"python3 {script} {flag}", shell=True, cwd=str(BASE))
    input(f"\n{DIM}[Enter to return]{R}")

# ═══════════════════════════════════════════════════════════════
#  DOCKER SERVICE MANAGER (from manage.py)
# ═══════════════════════════════════════════════════════════════
def parse_sel(raw: str, total: int) -> list:
    if raw.lower() == "all":
        return list(range(total))
    result = []
    for part in raw.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            try: result.extend(range(int(a)-1, int(b)))
            except ValueError: pass
        else:
            try: result.append(int(part)-1)
            except ValueError: pass
    return [i for i in result if 0 <= i < total]

def show_docker_list():
    print(f"\n  {BOLD}{'#':<4} {'SERVICE':<40} {'STATUS'}{R}")
    print(f"  {CORAL}{'─'*65}{R}")
    for i, svc in enumerate(ALL_DOCKER_SERVICES, 1):
        st = docker_status(svc)
        print(f"  {DIM}{i:>2}.{R}  {svc:<40} {fmt_status(st)}")
    print()

def docker_action(svc: str, action: str):
    svc_dir = BASE / svc
    if not (svc_dir / "docker-compose.yml").exists():
        print(f"{AMBER}  [SKIP]{R} {svc} — no docker-compose.yml")
        return
    cmds = {
        "start":   "docker compose up -d --remove-orphans",
        "stop":    "docker compose stop",
        "delete":  "docker compose down --remove-orphans",
        "rebuild": "docker compose build --no-cache && docker compose up -d",
    }
    cmd = cmds.get(action, "")
    if cmd:
        print(f"  {CYAN}[{action.upper()}]{R} {svc}...")
        subprocess.run(cmd, shell=True, cwd=str(svc_dir))

def docker_manager_menu():
    while True:
        clear()
        print(f"\n{CORAL}  ╔══════════════════════════════════════════╗{R}")
        print(f"{CORAL}  ║{R}  {BOLD}{CREAM}GAS DOCKER MANAGER{R}                      {CORAL}║{R}")
        print(f"{CORAL}  ╚══════════════════════════════════════════╝{R}\n")
        print(f"  {GREEN}1{R}  Start services")
        print(f"  {AMBER}2{R}  Stop services")
        print(f"  {RED}3{R}  Delete containers")
        print(f"  {CYAN}4{R}  Rebuild service")
        print(f"  {BLUE}5{R}  View logs")
        print(f"  {YELLOW}6{R}  Status all")
        print(f"  {DIM}q  Back{R}")
        ch = input(f"\n{CORAL}  > {R}").strip().lower()

        if ch == "q":
            break

        elif ch in ("1","2","3","4"):
            action_map = {"1":"start","2":"stop","3":"delete","4":"rebuild"}
            action = action_map[ch]

            clear()
            show_docker_list()

            if ch == "3":
                confirm = input(f"  {RED}Confirm delete? (yes/no): {R}").strip()
                if confirm.lower() != "yes":
                    continue

            raw = input(f"  {CYAN}Select (1,3,5 or 1-10 or all): {R}").strip()
            if not raw or raw == "0":
                continue
            selected = parse_sel(raw, len(ALL_DOCKER_SERVICES))
            print()
            for i in selected:
                docker_action(ALL_DOCKER_SERVICES[i], action)
            input(f"\n{DIM}[Enter]{R}")

        elif ch == "5":
            clear()
            show_docker_list()
            raw = input(f"  {CYAN}Service number: {R}").strip()
            try:
                idx  = int(raw) - 1
                name = ALL_DOCKER_SERVICES[idx]
                print(f"\n{CYAN}  Logs: {name}  (Ctrl+C to exit){R}\n")
                subprocess.run(f"docker logs --tail=80 --follow {name}", shell=True)
            except (ValueError, IndexError):
                print(f"{RED}Invalid{R}")
            input(f"\n{DIM}[Enter]{R}")

        elif ch == "6":
            clear()
            print(f"\n{BOLD}{CREAM}  DOCKER STATUS{R}\n")
            show_docker_list()
            running = sum(1 for s in ALL_DOCKER_SERVICES if docker_status(s) == "running")
            print(f"  {GREEN}Running: {running}{R}  {DIM}/ {len(ALL_DOCKER_SERVICES)} total{R}")
            input(f"\n{DIM}[Enter]{R}")

# ═══════════════════════════════════════════════════════════════
#  MODEL SWITCHER (CLI)
# ═══════════════════════════════════════════════════════════════
def model_switcher_menu() -> str:
    cfg          = load_cfg()
    current      = cfg.get("CURRENT_MODEL", "1")
    current_label= AI_MODELS.get(current, AI_MODELS["1"])[0]

    clear()
    print(f"\n{BOLD}{CREAM}  MODEL SWITCHER{R}")
    print(f"{CORAL}  ────────────────────────────────────────────{R}")
    print(f"  Current: {AMBER}{current_label}{R}\n")

    print(f"  {BOLD}{GREEN}── PRIMARY{R}")
    print(f"  {BOLD}1{R}  {GREEN}Claude Code (browser auth){R}  {DIM}primary · best overall{R}")

    print(f"\n  {BOLD}{CYAN}── DIRECT API{R}")
    print(f"  {BOLD}2{R}  {CYAN}Kimi k2.5{R}              {DIM}[Moonshot] KIMI_API_KEY{R}")
    print(f"  {BOLD}3{R}  {CYAN}Gemini 2.5 Flash{R}       {DIM}[AI Studio] GEMINI_API_KEY{R}")
    print(f"  {BOLD}4{R}  {CYAN}Gemini 2.5 Flash{R}       {DIM}[Vertex AI] VERTEX_API_KEY{R}")

    print(f"\n  {BOLD}{YELLOW}── VIA OPENROUTER{R}")
    print(f"  {BOLD}5{R}  {YELLOW}Kimi K2.5{R}              {DIM}$0.45/$2.20/1M · 262k ctx{R}")
    print(f"  {BOLD}6{R}  {YELLOW}DeepSeek V3.2{R}          {DIM}$0.26/$0.38/1M · fastest{R}")
    print(f"  {BOLD}7{R}  {YELLOW}DeepSeek R1{R}            {DIM}$0.45/$2.15/1M · reasoning{R}")
    print(f"  {BOLD}8{R}  {YELLOW}Grok 4.20 Multi-Agent{R}  {DIM}x-ai · multi-agent-beta{R}")
    print(f"  {BOLD}9{R}  {YELLOW}Gemini 3.1 Flash Lite{R}  {DIM}OR preview · free{R}")
    print(f"  {BOLD}a{R}  {YELLOW}Gemini 2.5 Flash{R}       {DIM}[OR] $0.30/$2.50/1M{R}")
    print(f"  {BOLD}b{R}  {YELLOW}Gemini 2.5 Pro{R}         {DIM}[OR] $1.25/$10/1M{R}")
    print(f"  {BOLD}e{R}  {YELLOW}Claude Haiku 4.5{R}       {DIM}[OR] $1.00/$5.00/1M{R}")
    print(f"  {BOLD}f{R}  {YELLOW}Claude Sonnet 4.5{R}      {DIM}[OR] $3.00/$15/1M{R}")
    print(f"  {BOLD}g{R}  {YELLOW}Qwen3-Coder FREE{R}       {DIM}[OR] $0.00 FREE · 262k{R}")

    print(f"\n  {BOLD}{DIM}── DEEPSEEK DIRECT{R}")
    print(f"  {BOLD}c{R}  {DIM}DeepSeek V3 (direct){R}   {DIM}DEEPSEEK_API_KEY required{R}")
    print(f"  {BOLD}d{R}  {DIM}DeepSeek R1 (direct){R}   {DIM}DEEPSEEK_API_KEY required{R}")

    print(f"\n  {DIM}q  Cancel{R}")
    print(f"{CORAL}  ────────────────────────────────────────────{R}")

    ch = input(f"  {BOLD}Pick: {R}").strip().lower()
    if ch in AI_MODELS:
        save_cfg_key("CURRENT_MODEL", ch)
        label = AI_MODELS[ch][0]
        print(f"\n  {GREEN}✅ Model set: {label}{R}")
        time.sleep(0.8)
        return ch
    return current

# ═══════════════════════════════════════════════════════════════
#  AGENTS STATUS (CLI)
# ═══════════════════════════════════════════════════════════════
def show_agents_status():
    live = get_live_agents()
    print(f"\n{BOLD}{CREAM}  RUNNING AGENTS{R}")
    print(f"{CORAL}  ────────────────────────────────────────────{R}")
    if not live:
        print(f"  {DIM}No agents currently running{R}")
    for role, info in live.items():
        print(f"  {GREEN}●{R} {BOLD}GAS-{role:<15}{R} PID:{CYAN}{info['pid']}{R}  model:{DIM}{info['model']}{R}  started:{DIM}{info['started']}{R}")

    print(f"\n  {BOLD}{AMBER}ALL DIVISION STATUS{R}")
    print(f"{CORAL}  ────────────────────────────────────────────{R}")
    for key, (role, _, desc) in AGENT_ROLES.items():
        info = live.get(role)
        if info:
            print(f"  {GREEN}●{R} {key}  {BOLD}{role:<15}{R} {DIM}{desc}{R}  {GREEN}PID {info['pid']}{R}")
        else:
            print(f"  {DIM}○{R} {key}  {role:<15} {DIM}{desc}{R}")
    print()

# ═══════════════════════════════════════════════════════════════
#  GIT + TODO (CLI)
# ═══════════════════════════════════════════════════════════════
def show_git():
    print(f"\n{BOLD}{CREAM}  GIT STATUS{R}")
    print(f"{CORAL}  ──────────────────────────────────────{R}")
    subprocess.run("git status --short | head -20", shell=True, cwd=str(BASE))
    print(f"\n{DIM}Last 5 commits:{R}")
    subprocess.run("git log --oneline -5", shell=True, cwd=str(BASE))
    print(f"{CORAL}  ──────────────────────────────────────{R}")
    input(f"\n{DIM}[Enter]{R}")

def show_todo():
    if not TODO_FILE.exists():
        print(f"{RED}tasks/todo.md not found{R}")
        input(f"\n{DIM}[Enter]{R}")
        return
    print(f"\n{BOLD}{CREAM}  TASK BOARD{R}")
    print(f"{CORAL}  ──────────────────────────────────────{R}")
    for line in TODO_FILE.read_text().splitlines():
        if line.startswith("## "):
            print(f"  {BOLD}{AMBER}{line}{R}")
        elif "❌" in line or "DOWN" in line:
            print(f"  {RED}{line}{R}")
        elif "✅" in line or "healthy" in line:
            print(f"  {GREEN}{line}{R}")
        elif "- [ ]" in line:
            print(f"  {YELLOW}{line}{R}")
        else:
            print(f"  {DIM}{line}{R}")
    print(f"{CORAL}  ──────────────────────────────────────{R}")
    input(f"\n{DIM}[Enter]{R}")

# ═══════════════════════════════════════════════════════════════
#  CLI HEADER + STATUS BAR
# ═══════════════════════════════════════════════════════════════
def cli_header():
    cfg    = load_cfg()
    model  = cfg.get("CURRENT_MODEL", "1")
    mlabel = AI_MODELS.get(model, AI_MODELS["1"])[0]
    live   = get_live_agents()

    clear()
    print()
    print(f"{CORAL}  ╔═══════════════════════════════════════════════════════╗{R}")
    print(f"{CORAL}  ║{R}  {BOLD}{AMBER} ██████╗  █████╗ ███████╗{R}                        {CORAL}║{R}")
    print(f"{CORAL}  ║{R}  {BOLD}{AMBER}██╔════╝ ██╔══██╗██╔════╝{R}  {CREAM}Golden AI Strategy{R}    {CORAL}║{R}")
    print(f"{CORAL}  ║{R}  {BOLD}{AMBER}██║  ███╗███████║███████╗{R}  {DIM}gas-golden-ai v1.0{R}    {CORAL}║{R}")
    print(f"{CORAL}  ║{R}  {BOLD}{AMBER}╚██████╔╝██║  ██║███████║{R}  {DIM}by Muhamad Ridwanjr{R}   {CORAL}║{R}")
    print(f"{CORAL}  ╚═══════════════════════════════════════════════════════╝{R}")
    print()

    # Status bar
    claude_ok = bool(sh("claude --version 2>/dev/null | head -1"))
    aider_ok  = bool(sh("aider --version 2>/dev/null | head -1"))
    dc_up     = sh("docker compose ps --filter status=running -q 2>/dev/null | wc -l").strip() or "0"
    live_count= len(live)

    print(f"{CORAL}  ─────────────────────────────────────────────────────────{R}")
    print(f"  {DIM}STATUS{R}  ", end="")
    print(f"{GREEN if claude_ok else RED}Claude {'✅' if claude_ok else '❌'}{R}  ", end="")
    print(f"{GREEN if aider_ok else DIM}Aider {'✅' if aider_ok else '─'}{R}  ", end="")
    print(f"{GREEN}Docker {dc_up} up{R}  ", end="")
    print(f"{AMBER}Model: {mlabel[:30]}{R}  ", end="")
    print(f"{CYAN if live_count else DIM}Agents: {live_count} live{R}")
    print(f"{CORAL}  ─────────────────────────────────────────────────────────{R}")
    print()

# ═══════════════════════════════════════════════════════════════
#  MAIN CLI LOOP
# ═══════════════════════════════════════════════════════════════
def cli_main():
    while True:
        cfg = load_cfg()
        cli_header()

        print(f"  {BOLD}AGENTS {DIM}(Claude Code + role context){R}")
        for key, (role, _, desc) in AGENT_ROLES.items():
            live  = get_live_agents()
            badge = f" {GREEN}●{R}" if role in live else ""
            print(f"  {CORAL}{key}{R}  {BOLD}{role:<15}{R}{badge} {DIM}{desc}{R}")

        print(f"\n  {BOLD}AI TOOLS{R}")
        print(f"  {CYAN}m{R}  Model switcher      {DIM}[current: {AI_MODELS.get(cfg.get('CURRENT_MODEL','1'), AI_MODELS['1'])[0][:25]}]{R}")
        print(f"  {CYAN}i{R}  Launch Aider        {DIM}[with current model]{R}")
        print(f"  {CYAN}u{R}  Token usage test    {DIM}[test all models]{R}")
        print(f"  {CYAN}U{R}  Token stats only    {DIM}[show saved]{R}")

        print(f"\n  {BOLD}SYSTEM{R}")
        print(f"  {CYAN}p{R}  Agent PIDs status   {DIM}[show running agents]{R}")
        print(f"  {CYAN}s{R}  Service health      {DIM}[ping all ports]{R}")
        print(f"  {CYAN}k{R}  Docker manager      {DIM}[start/stop/logs]{R}")
        print(f"  {CYAN}t{R}  Task board          {DIM}[tasks/todo.md]{R}")
        print(f"  {CYAN}g{R}  Git status{R}")
        print(f"  {CYAN}o{R}  Edit .gas-agent-config{R}")
        print(f"  {CYAN}h{R}  Refresh menu{R}")
        print(f"  {DIM}q  Quit{R}")
        print()
        print(f"{CORAL}  ─────────────────────────────────────────────────────────{R}")

        ch = input(f"  {BOLD}Pick: {R}").strip().lower()

        if ch in AGENT_ROLES:
            launch_claude_agent(ch)

        elif ch == "m":
            model_switcher_menu()

        elif ch == "i":
            model_key = cfg.get("CURRENT_MODEL", "1")
            launch_aider_model(model_key)

        elif ch == "u":
            run_token_test(stats_only=False)

        elif ch == "U":
            run_token_test(stats_only=True)

        elif ch == "p":
            show_agents_status()
            input(f"{DIM}[Enter]{R}")

        elif ch == "s":
            clear()
            print(f"\n{BOLD}{CREAM}  SERVICE HEALTH CHECK{R}\n")
            check_health()
            input(f"\n{DIM}[Enter]{R}")

        elif ch == "k":
            docker_manager_menu()

        elif ch == "t":
            show_todo()

        elif ch == "g":
            show_git()

        elif ch == "o":
            subprocess.run([os.environ.get("EDITOR", "nano"), str(CONFIG_FILE)])

        elif ch in ("h", ""):
            pass  # just refresh

        elif ch == "q":
            print(f"\n{DIM}  Bye bro. Keep building.\n{R}")
            sys.exit(0)

        else:
            print(f"  {DIM}Unknown option{R}")
            time.sleep(0.4)

# ═══════════════════════════════════════════════════════════════
#  TELEGRAM BOT
# ═══════════════════════════════════════════════════════════════
API_URL   = f"https://api.telegram.org/bot{BOT_TOKEN}"
tg_sessions     = {}   # chat_id → {user, role, time}
tg_pending      = {}   # chat_id → pending action

def tg(method: str, data: dict) -> dict:
    url  = f"{API_URL}/{method}"
    body = json.dumps(data).encode()
    req  = urllib.request.Request(url, body, {"Content-Type": "application/json"})
    tout = 35 if method == "getUpdates" else 15
    try:
        resp = urllib.request.urlopen(req, timeout=tout)
        return json.loads(resp.read())
    except Exception:
        return {}

def send(chat_id, text: str, buttons=None, parse="HTML"):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    tg("sendMessage", data)

def edit(chat_id, msg_id, text: str, buttons=None):
    data = {"chat_id": chat_id, "message_id": msg_id, "text": text, "parse_mode": "HTML"}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    tg("editMessageText", data)

def btn(text: str, data: str) -> dict:
    return {"text": text, "callback_data": data}

def is_auth(chat_id) -> bool:
    s = tg_sessions.get(chat_id)
    if not s:
        return False
    if time.time() - s["time"] > 43200:
        tg_sessions.pop(chat_id, None)
        return False
    return True

# ── VPS Data ──────────────────────────────────────────────────
def vps_quick() -> str:
    cpu  = sh("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'") or "N/A"
    ram  = sh("free -m | awk 'NR==2{printf \"%.1f/%.1f GB (%.0f%%)\", $3/1024, $2/1024, $3*100/$2}'")
    disk = sh("df -h / | awk 'NR==2{printf \"%s/%s (%s)\", $3, $2, $5}'")
    up   = sh("uptime -p").replace("up ","") or "N/A"
    load = sh("cat /proc/loadavg | awk '{print $1,$2,$3}'") or "N/A"
    dc   = sh("docker ps -q 2>/dev/null | wc -l") or "0"
    live = get_live_agents()
    agents_line = ", ".join([f"GAS-{r}" for r in live]) if live else "none"

    def emoji(val_str):
        try:
            v = float(val_str.replace("%","").strip())
            return "🔴" if v>85 else "🟡" if v>70 else "🟢"
        except Exception:
            return "🟢"

    cpu_pct = sh("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | tr -d '%us,'") or "0"
    ram_pct = sh("free | awk 'NR==2{printf \"%.0f\", $3*100/$2}'") or "0"
    dsk_pct = sh("df / | awk 'NR==2{print $5}' | tr -d '%'") or "0"

    return (
        f"🧠 <b>GOLDEN AI STRATEGY — VPS STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🔥 CPU    : {cpu}%  {emoji(cpu_pct)}\n"
        f"💾 RAM    : {ram}  {emoji(ram_pct)}\n"
        f"📀 Disk   : {disk}  {emoji(dsk_pct)}\n"
        f"📈 Load   : {load}\n"
        f"⏱ Uptime : {up}\n"
        f"🐳 Docker : {dc} containers up\n"
        f"🤖 Agents : {agents_line}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"by Muhamad Ridwanjr"
    )

def tg_health_text() -> str:
    lines = ["🔌 <b>SERVICE HEALTH</b>\n━━━━━━━━━━━━━━━━━━━━"]
    ok = err = 0
    for name, port in list(PORTS.items())[:24]:
        up = ping_port(port)
        lines.append(f"{'🟢' if up else '🔴'} {name}")
        if up: ok += 1
        else:  err += 1
    lines.append(f"━━━━━━━━━━━━━━━━━━━━\n✅ OK:{ok}  ❌ Down:{err}")
    return "\n".join(lines)

def tg_docker_text() -> str:
    all_c = {}
    raw = sh("docker ps -a --format '{{.Names}}|{{.Status}}'")
    for line in raw.splitlines():
        if "|" in line:
            n, s = line.split("|", 1)
            all_c[n.strip()] = s.strip()
    gas = {k:v for k,v in all_c.items() if k.startswith("gas-")}
    up  = sum(1 for v in gas.values() if "Up" in v)
    dn  = len(gas) - up
    lines = [
        f"🐳 <b>DOCKER STATUS</b>\n━━━━━━━━━━━━━━━━━━━━",
        f"Total: {len(gas)}  🟢 Up: {up}  🔴 Down: {dn}\n━━━━━━━━━━━━━━━━━━━━",
    ]
    for svc, st in list(gas.items())[:20]:
        icon = "🟢" if "Up" in st else "🔴"
        lines.append(f"{icon} {svc}")
    return "\n".join(lines)

def tg_agents_text() -> str:
    live = get_live_agents()
    lines = ["🤖 <b>RUNNING AGENTS</b>\n━━━━━━━━━━━━━━━━━━━━"]
    if not live:
        lines.append("No agents currently running.\nLaunch from CLI: python3 gas-golden-ai.py")
    for role, info in live.items():
        lines.append(f"🟢 GAS-{role}  PID:{info['pid']}  [{info['model']}]  {info['started']}")
    lines.append("━━━━━━━━━━━━━━━━━━━━")
    for key, (role, _, desc) in AGENT_ROLES.items():
        is_live = role in live
        lines.append(f"{'🟢' if is_live else '⚫'} {key}. {role} — {desc}")
    return "\n".join(lines)

def tg_todo_text() -> str:
    if not TODO_FILE.exists():
        return "📋 tasks/todo.md not found"
    content = TODO_FILE.read_text()[:3000]
    return f"📋 <b>TASK BOARD</b>\n<code>{content}</code>"

# ── Main Menu ─────────────────────────────────────────────────
def main_menu_btns():
    return [
        [btn("🖥 VPS STATUS",    "vps"),      btn("🔌 HEALTH",     "health")],
        [btn("🐳 DOCKER",        "docker"),   btn("🤖 AGENTS",     "agents")],
        [btn("📋 TODO BOARD",    "todo"),     btn("📊 TOKEN USAGE","tokens")],
        [btn("⚙️ DOCKER MGR",    "dockmgr"), btn("🔒 LOGOUT",      "logout")],
    ]

def main_menu_text(chat_id) -> str:
    user = tg_sessions.get(chat_id, {}).get("user", "?")
    live = get_live_agents()
    return (
        f"🧠 <b>GOLDEN AI CONTROL PANEL</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"👤 User    : {user}\n"
        f"🤖 Agents  : {len(live)} running\n"
        f"⏰ Time    : {datetime.now().strftime('%H:%M:%S')}\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Select module 👇"
    )

# ── Callback Handler ──────────────────────────────────────────
def handle_callback(chat_id, msg_id, data: str):
    if not is_auth(chat_id):
        tg("answerCallbackQuery", {"callback_query_id": msg_id, "text": "Please login first"})
        return
    tg("answerCallbackQuery", {"callback_query_id": msg_id, "text": ""})

    back = [[btn("⬅️ Back", "main")]]

    if data == "main":
        edit(chat_id, msg_id, main_menu_text(chat_id), main_menu_btns())

    elif data == "vps":
        edit(chat_id, msg_id, vps_quick(), back)

    elif data == "health":
        edit(chat_id, msg_id, tg_health_text(), back)

    elif data == "docker":
        edit(chat_id, msg_id, tg_docker_text(),
             [[btn("🔄 Restart svc", "restart_pick")], [btn("⬅️ Back","main")]])

    elif data == "agents":
        edit(chat_id, msg_id, tg_agents_text(),
             [[btn("☠️ Kill agent","kill_pick")], [btn("⬅️ Back","main")]])

    elif data == "todo":
        text = tg_todo_text()
        # Telegram limit 4096 chars
        if len(text) > 4000:
            text = text[:4000] + "\n..."
        edit(chat_id, msg_id, text, back)

    elif data == "tokens":
        usage = {}
        if USAGE_FILE.exists():
            try:
                usage = json.loads(USAGE_FILE.read_text())
            except Exception:
                pass
        lines = ["📊 <b>TOKEN USAGE (saved)</b>\n━━━━━━━━━━━━━━━━━━━━"]
        total_in = total_out = total_all = 0
        for mid, m in usage.get("models", {}).items():
            ti  = m.get("input_total", 0)
            to  = m.get("output_total", 0)
            tt  = m.get("token_total", 0)
            runs= m.get("runs", 0)
            lines.append(f"<b>{mid}</b>\n  in:{ti:,} out:{to:,} tot:{tt:,} runs:{runs}")
            total_in  += ti
            total_out += to
            total_all += tt
        lines.append(f"━━━━━━━━━━━━━━━━━━━━\n<b>TOTAL in:{total_in:,} out:{total_out:,} all:{total_all:,}</b>")
        edit(chat_id, msg_id, "\n".join(lines), back)

    elif data == "dockmgr":
        btns = [
            [btn("▶ Start service","dock_start"), btn("■ Stop service","dock_stop")],
            [btn("🔄 Restart svc",  "dock_restart"), btn("📋 Logs","dock_logs")],
            [btn("⬅️ Back","main")],
        ]
        edit(chat_id, msg_id, "🐳 <b>DOCKER MANAGER</b>\nSelect action:", btns)

    elif data.startswith("dock_"):
        action = data.replace("dock_","")
        lines  = ["🐳 <b>QUICK DOCKER ACTIONS</b>\n\nSend service name as text:"]
        lines.append(f"\nPending action: <code>{action}</code>")
        lines.append("\nExamples:\n<code>gas-gateway-api</code>\n<code>gas-signal-service</code>")
        tg_pending[chat_id] = f"dock_{action}"
        edit(chat_id, msg_id, "\n".join(lines), back)

    elif data == "kill_pick":
        live  = get_live_agents()
        lines = ["☠️ <b>KILL AGENT</b>\n\nSend agent name as text:"]
        if live:
            lines.append("\nRunning: " + ", ".join(live.keys()))
        else:
            lines.append("\nNo agents running")
        tg_pending[chat_id] = "kill_agent"
        edit(chat_id, msg_id, "\n".join(lines), back)

    elif data == "restart_pick":
        tg_pending[chat_id] = "dock_restart"
        edit(chat_id, msg_id, "🔄 <b>RESTART SERVICE</b>\n\nSend service name:", back)

    elif data == "logout":
        tg_sessions.pop(chat_id, None)
        edit(chat_id, msg_id, "🔒 Session ended. Send /start to login again.", None)

# ── Message Handler ───────────────────────────────────────────
def handle_message(chat_id, text: str):
    text = text.strip()

    # ── Login flow ──────────────────────────────────────────
    if text == "/start":
        if is_auth(chat_id):
            send(chat_id, main_menu_text(chat_id), main_menu_btns())
        else:
            send(chat_id,
                "🔐 <b>GOLDEN AI CONTROL PANEL</b>\n\nSend: <code>username password</code>\n\nExample:\n<code>ridwan gas2026!</code>")
        return

    # ── Auth ────────────────────────────────────────────────
    if not is_auth(chat_id):
        parts = text.split()
        if len(parts) == 2:
            uname, pwd = parts
            user_cfg = BOT_USERS.get(uname)
            if user_cfg and user_cfg["password"] == pwd:
                tg_sessions[chat_id] = {"user": uname, "role": user_cfg["role"], "time": time.time()}
                send(chat_id,
                    f"✅ <b>Login successful!</b>\nWelcome, {uname} ({user_cfg['role']})",
                    main_menu_btns())
            else:
                send(chat_id, "❌ Wrong credentials. Try again.")
        else:
            send(chat_id, "Send /start to begin login.")
        return

    # ── Pending action ──────────────────────────────────────
    pending = tg_pending.pop(chat_id, None)
    if pending:
        if pending.startswith("dock_"):
            action  = pending.replace("dock_","")
            svc     = text.strip()
            svc_dir = BASE / svc
            cmd_map = {
                "start":   f"cd {svc_dir} && docker compose up -d",
                "stop":    f"cd {svc_dir} && docker compose stop",
                "restart": f"docker compose -f {BASE}/docker-compose.yml restart {svc} 2>/dev/null || cd {svc_dir} && docker compose restart",
                "logs":    f"docker logs --tail=30 {svc} 2>&1",
            }
            cmd = cmd_map.get(action, f"docker ps -a --filter name={svc}")
            out = sh(cmd, timeout=30)
            send(chat_id, f"🐳 <b>{action.upper()}</b> <code>{svc}</code>\n\n<code>{out[:2000] if out else 'done'}</code>",
                 [[btn("⬅️ Back","main")]])
            return

        if pending == "kill_agent":
            result = kill_agent(text.strip().upper())
            send(chat_id, result, [[btn("⬅️ Back","main")]])
            return

    # ── Commands ────────────────────────────────────────────
    cmd = text.lower()

    if cmd in ("/menu", "/main", "/home"):
        send(chat_id, main_menu_text(chat_id), main_menu_btns())

    elif cmd in ("/status", "/vps"):
        send(chat_id, vps_quick(), [[btn("⬅️ Back","main")]])

    elif cmd in ("/health", "/ports"):
        send(chat_id, tg_health_text(), [[btn("⬅️ Back","main")]])

    elif cmd in ("/docker", "/dc"):
        send(chat_id, tg_docker_text(), [[btn("⬅️ Back","main")]])

    elif cmd in ("/agents", "/agent"):
        send(chat_id, tg_agents_text(), [[btn("⬅️ Back","main")]])

    elif cmd in ("/todo", "/tasks"):
        t = tg_todo_text()
        if len(t) > 4000: t = t[:4000] + "\n..."
        send(chat_id, t, [[btn("⬅️ Back","main")]])

    elif cmd.startswith("/restart "):
        svc = cmd.replace("/restart ","").strip()
        out = sh(f"docker compose -f {BASE}/docker-compose.yml restart {svc}", timeout=30)
        send(chat_id, f"🔄 restart <code>{svc}</code>\n<code>{out[:500] if out else 'done'}</code>")

    elif cmd.startswith("/logs "):
        svc = cmd.replace("/logs ","").strip()
        out = sh(f"docker logs --tail=40 {svc} 2>&1", timeout=15)
        send(chat_id, f"📋 logs <code>{svc}</code>\n<code>{out[:3000] if out else 'empty'}</code>")

    elif cmd.startswith("/kill "):
        role   = cmd.replace("/kill ","").strip().upper()
        result = kill_agent(role)
        send(chat_id, result)

    elif cmd == "/help":
        send(chat_id,
            "📖 <b>COMMANDS</b>\n\n"
            "/status — VPS stats\n"
            "/health — Port health check\n"
            "/docker — Docker containers\n"
            "/agents — AI agent PIDs\n"
            "/todo — Task board\n"
            "/restart &lt;svc&gt; — Restart container\n"
            "/logs &lt;svc&gt; — Container logs\n"
            "/kill &lt;ROLE&gt; — Kill agent by role\n"
            "/menu — Main menu\n"
            "/logout — End session\n\n"
            "Agents launched from CLI:\n"
            "<code>python3 gas-golden-ai.py</code>")

    elif cmd == "/logout":
        tg_sessions.pop(chat_id, None)
        send(chat_id, "🔒 Logged out. Send /start to re-login.")

    else:
        send(chat_id, "❓ Unknown command. Send /help or /menu")

# ── Bot polling loop ──────────────────────────────────────────
def bot_main():
    print(f"[GAS BOT] Starting Telegram bot...")
    print(f"[GAS BOT] Token: {BOT_TOKEN[:20]}...")
    print(f"[GAS BOT] Send /start to your bot to begin")

    offset = 0
    while True:
        try:
            resp = tg("getUpdates", {"timeout": 30, "offset": offset,
                                     "allowed_updates": ["message","callback_query"]})
            for upd in resp.get("result", []):
                offset = upd["update_id"] + 1

                if "callback_query" in upd:
                    cb      = upd["callback_query"]
                    chat_id = cb["message"]["chat"]["id"]
                    msg_id  = cb["message"]["message_id"]
                    data    = cb.get("data","")
                    tg("answerCallbackQuery", {"callback_query_id": cb["id"]})
                    handle_callback(chat_id, msg_id, data)

                elif "message" in upd:
                    msg     = upd["message"]
                    chat_id = msg["chat"]["id"]
                    text    = msg.get("text","")
                    if text:
                        handle_message(chat_id, text)

        except KeyboardInterrupt:
            print("\n[GAS BOT] Stopped.")
            break
        except Exception as e:
            print(f"[GAS BOT] Error: {e}")
            time.sleep(3)

# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    args = set(sys.argv[1:])

    if "--bot" in args:
        # PM2 mode — run Telegram bot
        bot_main()

    elif "--manage" in args:
        # Docker service manager only
        docker_manager_menu()

    elif "--health" in args:
        # Quick health check and exit
        print(f"\n{BOLD}{CREAM}GAS SERVICE HEALTH CHECK{R}\n")
        r = check_health()
        ok  = sum(1 for v in r.values() if v)
        err = len(r) - ok
        print(f"\n{GREEN}OK: {ok}{R}  {RED}Down: {err}{R}\n")
        sys.exit(0 if err == 0 else 1)

    elif "--kill" in args:
        # Kill agent: python3 gas-golden-ai.py --kill ORCHESTRATOR
        try:
            role = sys.argv[sys.argv.index("--kill") + 1].upper()
            print(kill_agent(role))
        except (IndexError, ValueError):
            print("Usage: python3 gas-golden-ai.py --kill ROLE_NAME")
        sys.exit(0)

    elif "--agents" in args:
        # Show running agents and exit
        show_agents_status()
        sys.exit(0)

    else:
        # Default: interactive CLI
        try:
            cli_main()
        except KeyboardInterrupt:
            print(f"\n{DIM}  Bye bro.\n{R}")
            sys.exit(0)
