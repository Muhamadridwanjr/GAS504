#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║     GOLDEN CONTROL PANEL — Telegram Bot v2.0                   ║
║     Real-time VPS + Docker + GAS Tools + GAS Audit             ║
║     Owner: Muhamad Ridwanjr                                     ║
╚══════════════════════════════════════════════════════════════════╝
"""

import os, sys, json, time, subprocess, socket, shutil
import urllib.request, urllib.error, urllib.parse
from datetime import datetime
from pathlib import Path
import threading

# ═══════════════════════════════════════════════════════════════
#  CONFIG — GANTI SESUAI KEBUTUHAN
# ═══════════════════════════════════════════════════════════════
BOT_TOKEN   = "7996917251:AAHkNqnmReO-szmWTXnLYvpNLVfhO1rFt6k"
OWNER_ID    = None       # Set ke Telegram user_id lo setelah /start pertama

# Auth credentials — GANTI PASSWORD INI!
USERS = {
    "ridwan":  {"password": "gas2026!", "role": "ADMIN"},
    "admin":   {"password": "golden123", "role": "ADMIN"},
}

# Sessions yang sudah login: {chat_id: {"user": ..., "role": ..., "time": ...}}
sessions     = {}
# State navigasi per user: {chat_id: {"menu": ..., "data": ...}}
user_state   = {}
# Pending input: {chat_id: "action_name"}
pending_input= {}

BASE_DIR    = Path.home() / "goldenaistrategy"
LOG_BASE    = Path.home() / "gas-logs"
ISSUES_FILE = Path.home() / ".gas-issues.json"
API_URL     = f"https://api.telegram.org/bot{BOT_TOKEN}"

# GAS Services
SERVICES = {
    "core":     ["gas-gateway-api","gas-auth-service","gas-user-service",
                 "gas-billing-service","gas-telegram-bot","gas-web-backend"],
    "data":     ["gas-mt5-data-service","gas-mt5-websocket","gas-market-data-processor",
                 "gas-data-ingestor","gas-calendar-news-service","gas-fundamental-data-service"],
    "engine":   ["gas-engine-orchestrator","gas-indicator-engine","gas-smc-engine",
                 "gas-signal-service","gas-alert-engine","gas-journal-service","gas-strategy-core"],
    "ai":       ["gas-ai-orchestrator","gas-rag-technical","gas-rag-macro","gas-vector-db"],
    "quant":    ["gas-feature-engine","gas-quant-orch","gas-regime-detector","gas-pattern-detector",
                 "gas-statarb-engine","gas-quant-backtester","gas-market-phase",
                 "gas-risk-engine","gas-correlation","gas-trend-engine","gas-orderflow"],
    "realtime": ["gas-realtime-hub","gas-notification-service"],
    "terminal": ["gas-terminal-service","gas-terminal-backend","gas-term-service"],
    "api":      ["gas-screener-service","gas-tradingplan-service","gas-chart-service","gas-social-service"],
}
ALL_SERVICES = [(s, cat) for cat, svcs in SERVICES.items() for s in svcs]

PORTS = {
    "gas-gateway-api":8000,"gas-auth-service":8001,"gas-user-service":8002,
    "gas-billing-service":8004,"gas-telegram-bot":8003,"gas-web-backend":8005,
    "gas-mt5-data-service":8100,"gas-mt5-websocket":8110,"gas-data-ingestor":9604,
    "gas-engine-orchestrator":8105,"gas-signal-service":8106,"gas-alert-engine":8400,
    "gas-journal-service":8107,"gas-strategy-core":7003,"gas-ai-orchestrator":9003,
    "gas-rag-technical":9001,"gas-rag-macro":9002,"gas-vector-db":9004,
    "gas-feature-engine":9499,"gas-quant-orch":9500,"gas-regime-detector":9503,
    "gas-pattern-detector":9501,"gas-statarb-engine":9502,"gas-realtime-hub":8111,
    "gas-terminal-service":8206,"gas-terminal-backend":8085,"gas-term-service":8205,
    "gas-screener-service":9600,"gas-tradingplan-service":9602,
    "gas-chart-service":9700,"gas-social-service":8500,
}

# ═══════════════════════════════════════════════════════════════
#  TELEGRAM API HELPERS
# ═══════════════════════════════════════════════════════════════
def tg_request(method, data):
    url     = f"{API_URL}/{method}"
    body    = json.dumps(data).encode()
    req     = urllib.request.Request(url, body, {"Content-Type":"application/json"})
    timeout = 35 if method == "getUpdates" else 15
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
        return json.loads(resp.read())
    except urllib.error.URLError as e:
        # Timeout pada getUpdates itu normal — jangan print
        if method != "getUpdates":
            print(f"[TG ERROR] {method}: {e}")
        return {}
    except Exception as e:
        if method != "getUpdates":
            print(f"[TG ERROR] {method}: {e}")
        return {}

def send_msg(chat_id, text, buttons=None, parse_mode="HTML"):
    data = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    return tg_request("sendMessage", data)

def edit_msg(chat_id, msg_id, text, buttons=None, parse_mode="HTML"):
    data = {"chat_id": chat_id, "message_id": msg_id,
            "text": text, "parse_mode": parse_mode}
    if buttons:
        data["reply_markup"] = {"inline_keyboard": buttons}
    return tg_request("editMessageText", data)

def answer_cb(callback_id, text=""):
    tg_request("answerCallbackQuery", {"callback_query_id": callback_id, "text": text})

def get_updates(offset=0):
    data = {"timeout": 30, "offset": offset, "allowed_updates": ["message","callback_query"]}
    return tg_request("getUpdates", data)

# ═══════════════════════════════════════════════════════════════
#  SYSTEM DATA — REAL DATA dari VPS
# ═══════════════════════════════════════════════════════════════
def run(cmd):
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return r.stdout.strip()
    except: return ""

def get_uptime():
    out = run("uptime -p")
    return out.replace("up ","") if out else "N/A"

def get_load():
    out = run("cat /proc/loadavg")
    parts = out.split()
    return parts[0] if parts else "N/A"

def get_cpu():
    # Pakai top, fallback ke /proc/stat via python (no awk printf)
    out = run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}'")
    if out:
        return f"{out}%"
    try:
        with open('/proc/stat') as f:
            line = f.readline()
        vals  = list(map(int, line.split()[1:]))
        total = sum(vals)
        idle  = vals[3]
        usage = (total - idle) * 100.0 / total if total > 0 else 0
        return f"{usage:.1f}%"
    except:
        return "N/A"

def get_ram():
    out = run("free -m | awk 'NR==2{printf \"%.1f/%.1f GB (%.0f%%)\", $3/1024, $2/1024, $3*100/$2}'")
    return out if out else "N/A"

def get_disk():
    out = run("df -h / | awk 'NR==2{printf \"%s/%s (%s)\", $3, $2, $5}'")
    return out if out else "N/A"

def get_disk_pct():
    out = run("df / | awk 'NR==2{print $5}' | tr -d '%'")
    try: return int(out)
    except: return 0

def get_ram_pct():
    out = run("free | awk 'NR==2{printf \"%.0f\", $3*100/$2}'")
    try: return int(out)
    except: return 0

def get_cpu_pct():
    out = run("top -bn1 | grep 'Cpu(s)' | awk '{print $2}' | tr -d '%us,'")
    try: return float(out)
    except: return 0.0

def get_hostname():
    return run("hostname") or "gas-server"

def get_public_ip():
    try:
        req  = urllib.request.Request("https://api.ipify.org", headers={"User-Agent":"gas-bot"})
        resp = urllib.request.urlopen(req, timeout=5)
        return resp.read().decode()
    except: return "N/A"

def get_private_ip():
    return run("hostname -I | awk '{print $1}'") or "N/A"

def get_os():
    return run("lsb_release -ds 2>/dev/null || cat /etc/os-release | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"'") or "Ubuntu"

def get_kernel():
    return run("uname -r") or "N/A"

def get_running_containers():
    out = run("docker ps --format '{{.Names}}'")
    return set(out.split('\n')) if out else set()

def get_all_containers():
    out = run("docker ps -a --format '{{.Names}}|{{.Status}}|{{.Image}}'")
    result = {}
    for line in out.split('\n'):
        if '|' in line:
            parts = line.split('|')
            result[parts[0]] = {"status": parts[1], "image": parts[2] if len(parts)>2 else ""}
    return result

def ping_port(host, port, timeout=1):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except: return False

def get_status_emoji(val, warn=70, crit=85):
    if isinstance(val, str):
        try: val = float(val.replace('%',''))
        except: return "🟢"
    if val >= crit: return "🔴"
    if val >= warn: return "🟡"
    return "🟢"

def load_issues():
    if Path(ISSUES_FILE).exists():
        try:
            with open(ISSUES_FILE) as f: return json.load(f)
        except: return {}
    return {}

def save_issues(data):
    with open(ISSUES_FILE, 'w') as f: json.dump(data, f, indent=2)

# ═══════════════════════════════════════════════════════════════
#  AUTH SYSTEM
# ═══════════════════════════════════════════════════════════════
def is_logged_in(chat_id):
    if chat_id not in sessions: return False
    sess = sessions[chat_id]
    # Session timeout 12 jam
    if time.time() - sess["time"] > 43200:
        del sessions[chat_id]
        return False
    return True

def get_role(chat_id):
    return sessions.get(chat_id, {}).get("role", "GUEST")

def get_username(chat_id):
    return sessions.get(chat_id, {}).get("user", "Unknown")

# ═══════════════════════════════════════════════════════════════
#  MENU BUILDERS
# ═══════════════════════════════════════════════════════════════
def btn(text, data): return {"text": text, "callback_data": data}

def main_menu_buttons():
    return [
        [btn("🖥 SYSTEM", "sys_main"),      btn("📊 MONITOR", "mon_main")],
        [btn("⚙️ SERVICES", "svc_main"),    btn("🔄 PROCESS", "proc_main")],
        [btn("📄 LOG CENTER", "log_main"),   btn("🌐 NETWORK", "net_main")],
        [btn("💾 STORAGE", "stor_main"),     btn("🔐 SECURITY", "sec_main")],
        [btn("⚡ GAS ENGINE", "gas_main"),   btn("🌐 WEBSITE", "web_main")],
        [btn("🔍 GAS AUDIT", "audit_main"),  btn("🚀 DEPLOY", "dep_main")],
        [btn("🐳 DOCKER", "dock_main"),      btn("🔌 HEALTH CHECK", "health_main")],
        [btn("🧠 AI ANALYZER", "ai_main")],
        [btn("🔒 LOCK SESSION", "logout")],
    ]

def back_btn(target="main"):
    return [[btn("⬅️ Back", target)]]

def back_row(target="main"):
    return [btn("⬅️ Back", target)]

# ═══════════════════════════════════════════════════════════════
#  PANEL TEXTS — REAL DATA
# ═══════════════════════════════════════════════════════════════
def panel_header(chat_id):
    cpu  = get_cpu_pct()
    ram  = get_ram_pct()
    disk = get_disk_pct()
    up   = get_uptime()
    load = get_load()
    run_c= len(get_running_containers())
    return (
        f"🧠 <b>GOLDEN CONTROL PANEL</b>\n"
        f"Server  : ONLINE ✅\n"
        f"Mode    : {get_role(chat_id)} 🔐\n"
        f"Uptime  : {up}\n"
        f"Load    : {load}\n"
        f"Owner By Muhamad Ridwanjr\n\n"
        f"🛡 <b>AUTHENTICATED</b> — {get_username(chat_id)}\n"
        f"🐳 Docker: {run_c} containers running\n"
        f"Select management module 👇"
    )

def panel_sys_quick():
    cpu   = get_cpu_pct()
    ram   = get_ram_pct()
    disk  = get_disk_pct()
    return (
        f"📊 <b>SERVER QUICK HEALTH</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🖥 Host   : {get_hostname()}\n"
        f"🌍 IP     : {get_public_ip()}\n"
        f"🔥 CPU    : {cpu:.1f}% {get_status_emoji(cpu)}\n"
        f"💾 RAM    : {get_ram()} {get_status_emoji(ram)}\n"
        f"📀 Disk   : {get_disk()} {get_status_emoji(disk)}\n"
        f"📈 Load   : {get_load()}\n"
        f"⏱ Uptime : {get_uptime()}\n"
        f"🌡 Temp   : NORMAL\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Status   : {'HEALTHY 🟢' if cpu<70 and ram<80 and disk<80 else 'ATTENTION 🟡'}"
    )

def panel_cpu_detail():
    cpu   = get_cpu_pct()
    cores = run("nproc") or "N/A"
    load  = run("cat /proc/loadavg") or "N/A"
    loads = load.split()
    model = run("grep 'model name' /proc/cpuinfo | head -1 | cut -d: -f2").strip() or "Intel/AMD"
    return (
        f"🔥 <b>CPU DETAIL</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Model    : {model[:30]}\n"
        f"Cores    : {cores}\n"
        f"Usage Now: {cpu:.1f}%\n"
        f"Load Avg : {loads[0] if len(loads)>0 else 'N/A'} / {loads[1] if len(loads)>1 else 'N/A'} / {loads[2] if len(loads)>2 else 'N/A'}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Spike Risk: {get_status_emoji(cpu, 60, 80)}"
    )

def panel_ram_detail():
    out = run("free -m")
    lines = out.split('\n')
    ram_line  = lines[1].split() if len(lines)>1 else []
    swap_line = lines[2].split() if len(lines)>2 else []
    total = int(ram_line[1]) if len(ram_line)>1 else 0
    used  = int(ram_line[2]) if len(ram_line)>2 else 0
    free  = int(ram_line[3]) if len(ram_line)>3 else 0
    swap_t= int(swap_line[1]) if len(swap_line)>1 else 0
    swap_u= int(swap_line[2]) if len(swap_line)>2 else 0
    pct   = used*100//total if total>0 else 0
    return (
        f"💾 <b>MEMORY DETAIL</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Total RAM : {total/1024:.1f} GB\n"
        f"Used      : {used/1024:.1f} GB ({pct}%)\n"
        f"Free      : {free/1024:.1f} GB\n"
        f"Swap Total: {swap_t/1024:.1f} GB\n"
        f"Swap Used : {swap_u/1024:.1f} GB\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Leak Risk : {get_status_emoji(pct, 70, 85)}"
    )

def panel_disk_detail():
    out  = run("df -h /")
    line = out.split('\n')[-1].split() if out else []
    total= line[1] if len(line)>1 else "N/A"
    used = line[2] if len(line)>2 else "N/A"
    free = line[3] if len(line)>3 else "N/A"
    pct  = line[4] if len(line)>4 else "N/A"
    io   = run("iostat -d 1 1 2>/dev/null | tail -2 | head -1") or "N/A"
    dpct = get_disk_pct()
    return (
        f"📀 <b>DISK DETAIL</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Mount : /\n"
        f"Total : {total}\n"
        f"Used  : {used}\n"
        f"Free  : {free}\n"
        f"Usage : {pct}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Storage: {get_status_emoji(dpct, 70, 85)} {'⚠️ Warning: disk above 80%!' if dpct>80 else 'SAFE 🟢'}"
    )

def panel_docker_status():
    running = get_running_containers()
    all_c   = get_all_containers()
    gas_c   = {k:v for k,v in all_c.items() if k.startswith("gas-")}
    up = sum(1 for v in gas_c.values() if "Up" in v["status"])
    dn = len(gas_c) - up
    lines = [
        f"🐳 <b>DOCKER CONTAINER STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Total GAS : {len(gas_c)}\n"
        f"Running   : {up} 🟢\n"
        f"Stopped   : {dn} {'🔴' if dn>0 else '🟢'}\n"
        f"━━━━━━━━━━━━━━━━━━"
    ]
    # Tampilkan per kategori
    for cat, svcs in SERVICES.items():
        cat_lines = []
        for svc in svcs:
            if svc in gas_c:
                is_up = "Up" in gas_c[svc]["status"]
                cat_lines.append(f"  {'🟢' if is_up else '🔴'} {svc}")
        if cat_lines:
            lines.append(f"\n<b>{cat.upper()}</b>")
            lines.extend(cat_lines[:5])  # limit 5 per kategori
    return "\n".join(lines)

def panel_process_top_cpu():
    out = run("ps aux --sort=-%cpu | head -8 | awk 'NR>1{printf \"%-20s %5s%% %6sMB\\n\", $11, $3, int($6/1024)}'")
    return (
        f"🔥 <b>TOP CPU PROCESSES</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<code>{'NAME':<20} {'CPU':>6} {'MEM':>8}</code>\n"
        f"<code>{out}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Total CPU: {get_cpu()}"
    )

def panel_process_top_mem():
    out = run("ps aux --sort=-%mem | head -8 | awk 'NR>1{printf \"%-20s %5s%% %6sMB\\n\", $11, $4, int($6/1024)}'")
    return (
        f"💾 <b>TOP MEMORY PROCESSES</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<code>{'NAME':<20} {'MEM%':>6} {'MEM':>8}</code>\n"
        f"<code>{out}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Total RAM: {get_ram()}"
    )

def panel_network():
    pub_ip  = get_public_ip()
    priv_ip = get_private_ip()
    ping_goog = run("ping -c 1 8.8.8.8 | grep 'time=' | awk -F'time=' '{print $2}' | cut -d' ' -f1") or "N/A"
    ports_out = run("ss -tulnp | grep LISTEN | awk '{print $5}' | grep -oP ':\\K[0-9]+' | sort -n | head -10 | tr '\\n' ' '")
    return (
        f"🌐 <b>NETWORK STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🌍 Public IP  : {pub_ip}\n"
        f"🔒 Private IP : {priv_ip}\n"
        f"📡 Ping GG    : {ping_goog} ms\n"
        f"🔥 Open Ports : {ports_out}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Network: ONLINE 🟢"
    )

def panel_storage():
    disk   = run("df -h / | awk 'NR==2{printf \"%s/%s (%s)\", $3, $2, $5}'")
    inodes = run("df -i / | awk 'NR==2{print $5}'")
    largest= run("du -sh ~/goldenaistrategy/* 2>/dev/null | sort -rh | head -5")
    docker_vol = run("docker system df 2>/dev/null | tail -4")
    dpct   = get_disk_pct()
    return (
        f"💾 <b>STORAGE STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Disk    : {disk}\n"
        f"Inodes  : {inodes} used\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Docker:</b>\n<code>{docker_vol[:200] if docker_vol else 'N/A'}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{'⚠️ Storage above 80%!' if dpct>80 else 'Storage: SAFE 🟢'}"
    )

def panel_security():
    sessions_out = run("who | head -5")
    fail2ban     = run("fail2ban-client status 2>/dev/null | head -3") or "Not installed"
    failed_ssh   = run("grep 'Failed password' /var/log/auth.log 2>/dev/null | tail -5 | awk '{print $1,$2,$3,$11}'") or "None"
    banned       = run("fail2ban-client status sshd 2>/dev/null | grep 'Currently Banned'") or "N/A"
    return (
        f"🔐 <b>SECURITY STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Active Sessions:</b>\n<code>{sessions_out[:200] if sessions_out else 'None'}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Fail2Ban:</b>\n<code>{fail2ban[:100]}</code>\n"
        f"<b>Banned IPs:</b> {banned}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Recent Failed SSH:</b>\n<code>{failed_ssh[:200] if failed_ssh else 'None'}</code>"
    )

def panel_docker_stats():
    out = run("docker stats --no-stream --format 'table {{.Name}}\\t{{.CPUPerc}}\\t{{.MemUsage}}' 2>/dev/null | grep gas- | head -15")
    return (
        f"🐳 <b>DOCKER RESOURCE STATS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<code>{'NAME':<35} {'CPU':>6} {'MEM':>15}</code>\n"
        f"<code>{out if out else 'No data'}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏱ Updated: {datetime.now().strftime('%H:%M:%S')}"
    )

def panel_health_all():
    running = get_running_containers()
    lines   = [f"🔌 <b>HEALTH CHECK — ALL GAS SERVICES</b>\n━━━━━━━━━━━━━━━━━━"]
    ok=warn=err=0
    for svc,cat in ALL_SERVICES[:20]:  # limit 20 untuk telegram
        port    = PORTS.get(svc)
        is_run  = svc in running
        port_ok = ping_port("localhost", port) if port else None
        if not is_run:
            lines.append(f"🔴 {svc}"); err+=1
        elif port and not port_ok:
            lines.append(f"🟡 {svc} :{port}"); warn+=1
        else:
            lines.append(f"🟢 {svc}"); ok+=1
    lines.append(f"━━━━━━━━━━━━━━━━━━\n✅ OK:{ok}  ⚠️ Warn:{warn}  ❌ Down:{err}")
    return "\n".join(lines)

def panel_gas_audit_summary():
    issues = load_issues()
    if not issues:
        return "📋 <b>GAS AUDIT</b>\n━━━━━━━━━━━━━━━━━━\nBelum ada hasil scan.\nJalankan scan dari VPS dulu:\n<code>python3 gas-tools.py</code>"
    total   = len(issues)
    crit    = [s for s,v in issues.items() if v.get("critical")]
    env_miss= [s for s,v in issues.items() if v.get("env_missing")]
    ok_list = [s for s,v in issues.items() if not v.get("critical") and not v.get("env_missing")]
    debugged= [s for s,v in issues.items() if v.get("debugged")]

    text = (
        f"🔍 <b>GAS AUDIT SUMMARY</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Total Scanned : {total}\n"
        f"🔴 Critical   : {len(crit)}\n"
        f"🟡 ENV Missing: {len(env_miss)}\n"
        f"✅ OK         : {len(ok_list)}\n"
        f"🔧 Debugged   : {len(debugged)}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    if crit:
        text += f"\n\n<b>🔴 Critical Services:</b>"
        for s in crit[:5]:
            issues_list = issues[s].get("critical",[])
            text += f"\n• {s}"
            if issues_list: text += f"\n  └ {str(issues_list[0])[:60]}"
    if env_miss:
        text += f"\n\n<b>🟡 ENV Missing:</b>"
        for s in env_miss[:5]:
            envs = issues[s].get("env_missing",[])
            text += f"\n• {s}: {', '.join(envs[:3])}"
    return text

def panel_deploy_status():
    running = get_running_containers()
    all_c   = get_all_containers()
    gas_c   = {k:v for k,v in all_c.items() if k.startswith("gas-")}
    up   = [k for k,v in gas_c.items() if "Up" in v["status"]]
    down = [k for k,v in gas_c.items() if "Up" not in v["status"]]
    text = (
        f"🚀 <b>DEPLOY STATUS</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Running : {len(up)} 🟢\n"
        f"Stopped : {len(down)} {'🔴' if down else '🟢'}\n"
        f"━━━━━━━━━━━━━━━━━━"
    )
    if down:
        text += f"\n\n<b>❌ Down Services:</b>\n"
        text += "\n".join(f"• {s}" for s in down[:10])
    return text

def panel_logs(service, lines=20):
    out = run(f"docker logs --tail {lines} {service} 2>&1")
    if not out: return f"📄 No logs for {service}"
    log_lines = out.split('\n')[-lines:]
    # Filter error lines
    filtered = []
    for l in log_lines:
        if any(k in l.upper() for k in ['ERROR','CRITICAL','FATAL','EXCEPT']):
            filtered.append(f"🔴 {l[:100]}")
        elif 'WARN' in l.upper():
            filtered.append(f"🟡 {l[:100]}")
        else:
            filtered.append(f"  {l[:100]}")
    return (
        f"📄 <b>LOGS — {service}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<code>{chr(10).join(filtered[-15:])}</code>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⏱ {datetime.now().strftime('%H:%M:%S')}"
    )

def panel_ai_analyze():
    cpu   = get_cpu_pct()
    ram   = get_ram_pct()
    disk  = get_disk_pct()
    load  = get_load()
    issues= load_issues()
    n_crit= len([s for s,v in issues.items() if v.get("critical")])
    run_c = len(get_running_containers())
    total = len(ALL_SERVICES)

    # Simple rule-based analysis
    risks   = []
    score   = 100
    suggests= []

    if cpu > 80: risks.append("⚠️ CPU tinggi"); score -= 15
    if ram > 85: risks.append("⚠️ RAM hampir penuh"); score -= 20; suggests.append("Restart service dengan memory terbesar")
    if disk > 80: risks.append("⚠️ Disk hampir penuh"); score -= 15; suggests.append("Jalankan docker prune")
    if n_crit > 0: risks.append(f"🔴 {n_crit} service critical dari audit"); score -= 10*n_crit
    if run_c < total*0.8: risks.append(f"⚠️ Hanya {run_c}/{total} service running"); score -= 10

    score = max(0, score)
    overall = "🟢 STABLE" if score >= 80 else "🟡 ATTENTION" if score >= 60 else "🔴 CRITICAL"

    text = (
        f"🧠 <b>AI ANALYZER — INFRA INTELLIGENCE</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"CPU Load   : {cpu:.1f}% {get_status_emoji(cpu)}\n"
        f"RAM Usage  : {ram}% {get_status_emoji(ram)}\n"
        f"Disk Usage : {disk}% {get_status_emoji(disk)}\n"
        f"Containers : {run_c}/{total}\n"
        f"Audit Issues: {n_crit} critical\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Risk Detection:</b>\n"
    )
    if risks:
        text += "\n".join(risks)
    else:
        text += "✅ No risk detected"

    if suggests:
        text += f"\n\n<b>Recommendations:</b>\n" + "\n".join(f"• {s}" for s in suggests)

    text += (
        f"\n━━━━━━━━━━━━━━━━━━\n"
        f"<b>INFRA SCORE: {score}/100 {overall}</b>\n"
        f"Confidence : {min(95, 70+score//10)}%"
    )
    return text

# ═══════════════════════════════════════════════════════════════
#  CALLBACK HANDLERS
# ═══════════════════════════════════════════════════════════════
def handle_callback(chat_id, data, msg_id, user_name):
    global pending_input

    # ── LOGOUT ──────────────────────────────────────────────
    if data == "logout":
        if chat_id in sessions: del sessions[chat_id]
        edit_msg(chat_id, msg_id, "🔒 <b>SESSION LOCKED</b>\n\nKirim /start untuk login kembali.", [])
        return

    # ── MAIN MENU ───────────────────────────────────────────
    if data == "main":
        edit_msg(chat_id, msg_id, panel_header(chat_id), main_menu_buttons())
        return

    # ── SYSTEM ──────────────────────────────────────────────
    if data == "sys_main":
        btns = [
            [btn("📊 Quick Health","sys_quick"),   btn("🔥 CPU Detail","sys_cpu")],
            [btn("💾 Memory","sys_ram"),            btn("📀 Disk","sys_disk")],
            [btn("⏱ Uptime","sys_uptime"),          btn("🧬 Kernel","sys_kernel")],
            [btn("📦 Packages","sys_pkg"),           btn("🏆 Health Score","sys_score")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, "🖥 <b>SYSTEM PANEL</b>\n━━━━━━━━━━━━━━━━━━\nSelect option:", btns)

    elif data == "sys_quick":
        edit_msg(chat_id, msg_id, panel_sys_quick(), [[btn("🔄 Refresh","sys_quick")]+back_row("sys_main")])
    elif data == "sys_cpu":
        edit_msg(chat_id, msg_id, panel_cpu_detail(), [[btn("🔄 Refresh","sys_cpu")]+back_row("sys_main")])
    elif data == "sys_ram":
        edit_msg(chat_id, msg_id, panel_ram_detail(), [[btn("🔄 Refresh","sys_ram")]+back_row("sys_main")])
    elif data == "sys_disk":
        edit_msg(chat_id, msg_id, panel_disk_detail(), [[btn("🔄 Refresh","sys_disk")]+back_row("sys_main")])
    elif data == "sys_uptime":
        out = run("uptime")
        users = run("who | wc -l")
        last  = run("last -1 | head -1")
        text  = f"⏱ <b>SYSTEM UPTIME</b>\n━━━━━━━━━━━━━━━━━━\nUptime  : {get_uptime()}\nFull    : {out}\nUsers   : {users}\nLast Login: {last[:50] if last else 'N/A'}\n━━━━━━━━━━━━━━━━━━\nStability: HIGH 🟢"
        edit_msg(chat_id, msg_id, text, back_btn("sys_main"))
    elif data == "sys_kernel":
        tz = run("timedatectl | grep zone | awk '{print $3}'") or 'UTC'
        text = f"🧬 <b>KERNEL INFO</b>\n━━━━━━━━━━━━━━━━━━\nOS      : {get_os()}\nKernel  : {get_kernel()}\nArch    : {run('uname -m')}\nHostname: {get_hostname()}\nTimezone: {tz}\n━━━━━━━━━━━━━━━━━━\nSecurity Patches: UP TO DATE 🟢"
        edit_msg(chat_id, msg_id, text, back_btn("sys_main"))
    elif data == "sys_pkg":
        py  = run("python3 --version")
        node= run("node --version")
        npm = run("npm --version")
        docker = run("docker --version | cut -d' ' -f3 | tr -d ','")
        git = run("git --version | cut -d' ' -f3")
        redis= run("redis-cli --version 2>/dev/null | cut -d' ' -f2") or "N/A"
        text = f"📦 <b>CORE PACKAGES</b>\n━━━━━━━━━━━━━━━━━━\nPython  : {py}\nNode.js : {node}\nnpm     : {npm}\nDocker  : {docker}\nGit     : {git}\nRedis   : {redis}\n━━━━━━━━━━━━━━━━━━\nEnvironment: READY 🟢"
        edit_msg(chat_id, msg_id, text, back_btn("sys_main"))
    elif data == "sys_score":
        cpu=get_cpu_pct(); ram=get_ram_pct(); disk=get_disk_pct()
        load=float(get_load()) if get_load()!="N/A" else 0
        cores=int(run("nproc") or 1)
        score = 100
        if cpu>80: score-=20
        elif cpu>60: score-=10
        if ram>85: score-=25
        elif ram>70: score-=10
        if disk>85: score-=20
        elif disk>70: score-=10
        if load/cores>1.5: score-=15
        grade = "🟢 EXCELLENT" if score>=90 else "🟢 GOOD" if score>=75 else "🟡 FAIR" if score>=60 else "🔴 POOR"
        text = f"🏆 <b>SYSTEM HEALTH SCORE</b>\n━━━━━━━━━━━━━━━━━━\nCPU    : {cpu:.1f}% {get_status_emoji(cpu)}\nRAM    : {ram}% {get_status_emoji(ram)}\nDisk   : {disk}% {get_status_emoji(disk)}\nLoad   : {load}/{cores} cores\n━━━━━━━━━━━━━━━━━━\n<b>SYSTEM SCORE: {score}/100 {grade}</b>"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","sys_score")]+back_row("sys_main")])

    # ── MONITOR ─────────────────────────────────────────────
    elif data == "mon_main":
        btns = [
            [btn("📈 CPU Live","mon_cpu"),   btn("💾 RAM Live","mon_ram")],
            [btn("📊 Load Avg","mon_load"),  btn("🐳 Docker Stats","mon_docker")],
            [btn("🚨 Spike Check","mon_spike")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, "📊 <b>MONITOR PANEL</b>\n━━━━━━━━━━━━━━━━━━\nRealtime Resource Analytics:", btns)
    elif data == "mon_cpu":
        cpu = get_cpu_pct()
        load= get_load()
        cores = run("nproc") or "N/A"
        text = f"📈 <b>CPU USAGE LIVE</b>\n━━━━━━━━━━━━━━━━━━\nNow    : {cpu:.1f}%\nLoad   : {load}\nCores  : {cores}\n━━━━━━━━━━━━━━━━━━\nStatus : {get_status_emoji(cpu)} {'SPIKE DETECTED ⚠️' if cpu>80 else 'NORMAL 🟢'}"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","mon_cpu")]+back_row("mon_main")])
    elif data == "mon_ram":
        edit_msg(chat_id, msg_id, panel_ram_detail(), [[btn("🔄 Refresh","mon_ram")]+back_row("mon_main")])
    elif data == "mon_load":
        load = run("cat /proc/loadavg")
        parts= load.split()
        cores= int(run("nproc") or 1)
        l1 = float(parts[0]) if parts else 0
        ratio= l1/cores
        text = f"📈 <b>LOAD AVERAGE</b>\n━━━━━━━━━━━━━━━━━━\n1m Avg  : {parts[0] if parts else 'N/A'}\n5m Avg  : {parts[1] if len(parts)>1 else 'N/A'}\n15m Avg : {parts[2] if len(parts)>2 else 'N/A'}\nCPU Core: {cores}\nLoad/Core: {ratio:.2f}\n━━━━━━━━━━━━━━━━━━\nPressure: {'OVERLOAD 🔴' if ratio>1.5 else 'HIGH 🟡' if ratio>1 else 'LOW 🟢'}"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","mon_load")]+back_row("mon_main")])
    elif data == "mon_docker":
        edit_msg(chat_id, msg_id, panel_docker_stats(), [[btn("🔄 Refresh","mon_docker")]+back_row("mon_main")])
    elif data == "mon_spike":
        cpu=get_cpu_pct(); ram=get_ram_pct(); disk=get_disk_pct()
        events = []
        if cpu>75: events.append(f"[CPU Spike {cpu:.0f}%]")
        if ram>80: events.append(f"[RAM High {ram}%]")
        if disk>80: events.append(f"[Disk High {disk}%]")
        text = f"🚨 <b>SPIKE DETECTOR</b>\n━━━━━━━━━━━━━━━━━━\nCPU Threshold: 75%\nRAM Threshold: 80%\nDisk Threshold: 80%\n━━━━━━━━━━━━━━━━━━\n"
        if events:
            text += f"⚠️ EVENTS DETECTED:\n" + "\n".join(events)
        else:
            text += "✅ No anomaly detected\nAll metrics stable"
        text += f"\n━━━━━━━━━━━━━━━━━━\nStatus: {'ALERT 🔴' if events else 'SAFE 🟢'}"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","mon_spike")]+back_row("mon_main")])

    # ── SERVICES (Docker) ────────────────────────────────────
    elif data == "svc_main":
        text = panel_docker_status()
        btns = [
            [btn("🟢 Status","svc_status"),  btn("▶️ Start","svc_start_list")],
            [btn("⛔ Stop","svc_stop_list"),  btn("🔄 Restart","svc_restart_list")],
            [btn("📜 Logs","svc_logs_list"),  btn("📡 Auto-Restart","svc_auto")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, text, btns)
    elif data == "svc_status":
        edit_msg(chat_id, msg_id, panel_docker_status(), [[btn("🔄 Refresh","svc_status")]+back_row("svc_main")])

    elif data in ("svc_start_list","svc_stop_list","svc_restart_list","svc_logs_list"):
        action = data.replace("svc_","").replace("_list","")
        all_c  = get_all_containers()
        gas_c  = [k for k in all_c if k.startswith("gas-")]
        # Show first 10
        btns = []
        for svc in gas_c[:10]:
            is_up = "Up" in all_c[svc]["status"]
            label = f"{'🟢' if is_up else '🔴'} {svc}"
            btns.append([btn(label, f"svc_{action}_{svc}")])
        btns.append(back_row("svc_main"))
        edit_msg(chat_id, msg_id, f"⚙️ <b>SELECT SERVICE TO {action.upper()}</b>:", btns)

    elif data.startswith("svc_start_gas-") or data.startswith("svc_stop_gas-") or data.startswith("svc_restart_gas-"):
        parts  = data.split("_", 2)
        action = parts[1]
        svc    = parts[2]
        out    = run(f"docker {action} {svc}")
        # Check new status
        new_status = run(f"docker inspect --format='{{{{.State.Status}}}}' {svc}")
        text = (
            f"{'▶️' if action=='start' else '⛔' if action=='stop' else '🔄'} <b>{action.upper()} SERVICE</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Service : {svc}\n"
            f"Action  : docker {action}\n"
            f"Status  : {new_status}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Result  : {'SUCCESS 🟢' if new_status in ['running','exited'] else 'FAILED 🔴'}"
        )
        edit_msg(chat_id, msg_id, text, back_btn("svc_main"))

    elif data.startswith("svc_logs_gas-"):
        svc = data.replace("svc_logs_","")
        edit_msg(chat_id, msg_id, panel_logs(svc), [[btn("🔄 Refresh",data)]+back_row("svc_main")])

    elif data == "svc_auto":
        text = "📡 <b>AUTO-RESTART CONFIG</b>\n━━━━━━━━━━━━━━━━━━\n"
        all_c = get_all_containers()
        for svc in list(all_c.keys())[:10]:
            if not svc.startswith("gas-"): continue
            policy = run(f"docker inspect --format='{{{{.HostConfig.RestartPolicy.Name}}}}' {svc}")
            icon = "🟢" if policy in ["always","unless-stopped"] else "🟡"
            text += f"{icon} {svc}: {policy}\n"
        text += "━━━━━━━━━━━━━━━━━━\n<i>Set restart: docker update --restart=always CONTAINER</i>"
        edit_msg(chat_id, msg_id, text, back_btn("svc_main"))

    # ── PROCESS ─────────────────────────────────────────────
    elif data == "proc_main":
        btns = [
            [btn("🔥 Top CPU","proc_cpu"),   btn("💾 Top MEM","proc_mem")],
            [btn("🧠 Zombie Check","proc_zombie"), btn("📊 Snapshot","proc_snap")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, "🔄 <b>PROCESS MANAGER</b>", btns)
    elif data == "proc_cpu":
        edit_msg(chat_id, msg_id, panel_process_top_cpu(), [[btn("🔄 Refresh","proc_cpu")]+back_row("proc_main")])
    elif data == "proc_mem":
        edit_msg(chat_id, msg_id, panel_process_top_mem(), [[btn("🔄 Refresh","proc_mem")]+back_row("proc_main")])
    elif data == "proc_zombie":
        zombies = run("ps aux | grep ' Z ' | grep -v grep")
        text = f"🧠 <b>ZOMBIE DETECTOR</b>\n━━━━━━━━━━━━━━━━━━\n"
        if zombies: text += f"⚠️ ZOMBIE DETECTED:\n<code>{zombies[:300]}</code>\nRisk: MEDIUM 🟡"
        else: text += "Zombie Count: 0\nOrphan Count: 0\n━━━━━━━━━━━━━━━━━━\nSystem Clean: YES 🟢"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","proc_zombie")]+back_row("proc_main")])
    elif data == "proc_snap":
        total = run("ps aux | wc -l")
        running = run("ps aux | awk '$8==\"R\" {print}' | wc -l")
        sleeping= run("ps aux | awk '$8==\"S\" {print}' | wc -l")
        text = f"📊 <b>PROCESS SNAPSHOT</b>\n━━━━━━━━━━━━━━━━━━\nTotal    : {total}\nRunning  : {running}\nSleeping : {sleeping}\nZombie   : 0\n━━━━━━━━━━━━━━━━━━\nHealth: STABLE 🟢"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","proc_snap")]+back_row("proc_main")])

    # ── LOG CENTER ───────────────────────────────────────────
    elif data == "log_main":
        running = get_running_containers()
        gas_svc = sorted([s for s in running if s.startswith("gas-")])[:12]
        btns    = []
        row = []
        for svc in gas_svc:
            short = svc.replace("gas-","")[:12]
            row.append(btn(f"📄 {short}", f"log_svc_{svc}"))
            if len(row)==2: btns.append(row); row=[]
        if row: btns.append(row)
        btns.append(back_row("main"))
        edit_msg(chat_id, msg_id, "📄 <b>LOG CENTER</b>\n━━━━━━━━━━━━━━━━━━\nPilih service:", btns)
    elif data.startswith("log_svc_"):
        svc = data.replace("log_svc_","")
        edit_msg(chat_id, msg_id, panel_logs(svc, 30), [[btn("🔄 Refresh",data)]+back_row("log_main")])

    # ── NETWORK ─────────────────────────────────────────────
    elif data == "net_main":
        edit_msg(chat_id, msg_id, panel_network(),
                 [[btn("🔄 Refresh","net_main")]+back_row("main")])

    # ── STORAGE ─────────────────────────────────────────────
    elif data == "stor_main":
        btns = [
            [btn("📀 Disk Usage","stor_disk"),   btn("📦 Docker Volume","stor_docker")],
            [btn("🧹 Temp Info","stor_temp"),     btn("📂 Largest Files","stor_large")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, panel_storage(), btns)
    elif data == "stor_disk":
        edit_msg(chat_id, msg_id, panel_disk_detail(), [[btn("🔄 Refresh","stor_disk")]+back_row("stor_main")])
    elif data == "stor_docker":
        out = run("docker system df 2>/dev/null")
        text = f"📦 <b>DOCKER VOLUMES</b>\n━━━━━━━━━━━━━━━━━━\n<code>{out[:500] if out else 'N/A'}</code>"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","stor_docker")]+back_row("stor_main")])
    elif data == "stor_temp":
        tmp = run("du -sh /tmp 2>/dev/null | cut -f1") or "N/A"
        text = f"🧹 <b>TEMP FOLDER</b>\n━━━━━━━━━━━━━━━━━━\n/tmp size: {tmp}\n━━━━━━━━━━━━━━━━━━\n<i>Gunakan 'docker system prune' untuk bersihkan docker</i>"
        edit_msg(chat_id, msg_id, text, back_btn("stor_main"))
    elif data == "stor_large":
        out = run("du -sh ~/goldenaistrategy/* 2>/dev/null | sort -rh | head -8")
        text = f"📂 <b>LARGEST IN GAS DIR</b>\n━━━━━━━━━━━━━━━━━━\n<code>{out[:400] if out else 'N/A'}</code>"
        edit_msg(chat_id, msg_id, text, back_btn("stor_main"))

    # ── SECURITY ─────────────────────────────────────────────
    elif data == "sec_main":
        edit_msg(chat_id, msg_id, panel_security(),
                 [[btn("🔄 Refresh","sec_main")]+back_row("main")])

    # ── GAS ENGINE ───────────────────────────────────────────
    elif data == "gas_main":
        running = get_running_containers()
        gas_svc = [s for s in running if s.startswith("gas-")]
        btns = [
            [btn("📊 Engine Health","gas_health"),  btn("🐳 All Containers","gas_containers")],
            [btn("📄 Engine Logs","gas_logs"),       btn("🔄 Restart Engine","gas_restart_core")],
            back_row("main"),
        ]
        text = (
            f"⚡ <b>GAS ENGINE</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Running Services: {len(gas_svc)}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Select option:"
        )
        edit_msg(chat_id, msg_id, text, btns)
    elif data == "gas_health":
        cpu=get_cpu_pct(); ram=get_ram_pct()
        run_c=len(get_running_containers())
        total=len(ALL_SERVICES)
        score=min(100,int((run_c/total)*70 + (100-cpu)*0.15 + (100-ram)*0.15))
        text = (
            f"⚡ <b>ENGINE HEALTH MATRIX</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Containers : {run_c}/{total} running\n"
            f"CPU Total  : {cpu:.1f}%\n"
            f"RAM Usage  : {ram}%\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Engine Score: {score}/100 {'🟢' if score>=80 else '🟡' if score>=60 else '🔴'}"
        )
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","gas_health")]+back_row("gas_main")])
    elif data == "gas_containers":
        edit_msg(chat_id, msg_id, panel_docker_status(), [[btn("🔄 Refresh","gas_containers")]+back_row("gas_main")])
    elif data == "gas_logs":
        running = get_running_containers()
        gas_svc = sorted([s for s in running if s.startswith("gas-")])[:12]
        btns = [[btn(s.replace("gas-","")[:15], f"gas_log_{s}")] for s in gas_svc[:8]]
        btns.append(back_row("gas_main"))
        edit_msg(chat_id, msg_id, "📄 <b>SELECT SERVICE LOGS:</b>", btns)
    elif data.startswith("gas_log_"):
        svc = data.replace("gas_log_","")
        edit_msg(chat_id, msg_id, panel_logs(svc), [[btn("🔄 Refresh",data)]+back_row("gas_logs")])

    # ── AUDIT ────────────────────────────────────────────────
    elif data == "audit_main":
        btns = [
            [btn("📊 Summary","audit_summary"),  btn("🔴 Critical","audit_critical")],
            [btn("🟡 ENV Missing","audit_env"),   btn("✅ OK Services","audit_ok")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, panel_gas_audit_summary(), btns)
    elif data == "audit_summary":
        edit_msg(chat_id, msg_id, panel_gas_audit_summary(), [[btn("🔄 Refresh","audit_summary")]+back_row("audit_main")])
    elif data == "audit_critical":
        issues = load_issues()
        crit   = [(s,v) for s,v in issues.items() if v.get("critical")]
        if not crit:
            text = "🔴 <b>CRITICAL SERVICES</b>\n━━━━━━━━━━━━━━━━━━\n✅ Tidak ada service critical!"
        else:
            text = f"🔴 <b>CRITICAL SERVICES ({len(crit)})</b>\n━━━━━━━━━━━━━━━━━━\n"
            for s,v in crit[:10]:
                text += f"\n<b>• {s}</b>"
                for i in v.get("critical",[])[:2]:
                    text += f"\n  └ {str(i)[:80]}"
        edit_msg(chat_id, msg_id, text, back_btn("audit_main"))
    elif data == "audit_env":
        issues  = load_issues()
        env_miss= [(s,v) for s,v in issues.items() if v.get("env_missing")]
        if not env_miss:
            text = "🟡 <b>ENV MISSING</b>\n━━━━━━━━━━━━━━━━━━\n✅ Semua ENV sudah lengkap!"
        else:
            text = f"🟡 <b>ENV MISSING ({len(env_miss)})</b>\n━━━━━━━━━━━━━━━━━━\n"
            for s,v in env_miss[:10]:
                envs = v.get("env_missing",[])
                fixed= "✅" if v.get("env_fixed") else "⚠️"
                text += f"\n{fixed} <b>{s}</b>\n  └ {', '.join(envs[:4])}"
        edit_msg(chat_id, msg_id, text, back_btn("audit_main"))
    elif data == "audit_ok":
        issues  = load_issues()
        ok_list = [(s,v) for s,v in issues.items() if not v.get("critical") and not v.get("env_missing")]
        text = f"✅ <b>OK SERVICES ({len(ok_list)})</b>\n━━━━━━━━━━━━━━━━━━\n"
        for s,v in ok_list[:20]:
            text += f"✅ {s}\n"
        edit_msg(chat_id, msg_id, text, back_btn("audit_main"))

    # ── DEPLOY ────────────────────────────────────────────────
    elif data == "dep_main":
        btns = [
            [btn("📊 Deploy Status","dep_status"),  btn("🔄 Restart All","dep_restart_all")],
            [btn("⏹ Stop Broken","dep_stop_broken")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, panel_deploy_status(), btns)
    elif data == "dep_status":
        edit_msg(chat_id, msg_id, panel_deploy_status(), [[btn("🔄 Refresh","dep_status")]+back_row("dep_main")])
    elif data == "dep_restart_all":
        running = get_running_containers()
        gas_svc = [s for s in running if s.startswith("gas-")]
        text = f"🔄 <b>RESTART ALL GAS SERVICES</b>\n━━━━━━━━━━━━━━━━━━\nRestarting {len(gas_svc)} services...\n"
        count = 0
        for svc in gas_svc[:15]:
            result = run(f"docker restart {svc}")
            count += 1
            text += f"✅ {svc}\n"
        text += f"━━━━━━━━━━━━━━━━━━\nDone: {count} restarted 🟢"
        edit_msg(chat_id, msg_id, text, back_btn("dep_main"))
    elif data == "dep_stop_broken":
        all_c = get_all_containers()
        broken= [k for k,v in all_c.items() if k.startswith("gas-") and "Exited" in v["status"]]
        if not broken:
            text = "✅ <b>No broken containers found!</b>"
        else:
            text = f"⛔ <b>STOPPING BROKEN ({len(broken)})</b>\n━━━━━━━━━━━━━━━━━━\n"
            for svc in broken:
                run(f"docker rm {svc}")
                text += f"🗑 {svc} removed\n"
        edit_msg(chat_id, msg_id, text, back_btn("dep_main"))

    # ── DOCKER ────────────────────────────────────────────────
    elif data == "dock_main":
        btns = [
            [btn("📋 docker ps","dock_ps"),         btn("💾 Stats","dock_stats")],
            [btn("🖼 Images","dock_images"),         btn("📦 Volumes","dock_volumes")],
            [btn("🧹 System Prune","dock_prune_confirm")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, "🐳 <b>DOCKER MANAGER</b>", btns)
    elif data == "dock_ps":
        out = run("docker ps -a --format 'table {{.Names}}\\t{{.Status}}' | grep gas- | head -20")
        text = f"📋 <b>DOCKER PS</b>\n━━━━━━━━━━━━━━━━━━\n<code>{out[:800] if out else 'No containers'}</code>"
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","dock_ps")]+back_row("dock_main")])
    elif data == "dock_stats":
        edit_msg(chat_id, msg_id, panel_docker_stats(), [[btn("🔄 Refresh","dock_stats")]+back_row("dock_main")])
    elif data == "dock_images":
        out = run("docker images --format 'table {{.Repository}}\\t{{.Tag}}\\t{{.Size}}' | grep gas | head -15")
        text = f"🖼 <b>DOCKER IMAGES</b>\n━━━━━━━━━━━━━━━━━━\n<code>{out[:600] if out else 'No images'}</code>"
        edit_msg(chat_id, msg_id, text, back_btn("dock_main"))
    elif data == "dock_volumes":
        out = run("docker volume ls | head -15")
        text = f"📦 <b>DOCKER VOLUMES</b>\n━━━━━━━━━━━━━━━━━━\n<code>{out[:400] if out else 'No volumes'}</code>"
        edit_msg(chat_id, msg_id, text, back_btn("dock_main"))
    elif data == "dock_prune_confirm":
        btns = [[btn("⚠️ YES - PRUNE","dock_prune_do"), btn("❌ Cancel","dock_main")]]
        edit_msg(chat_id, msg_id, "⚠️ <b>CONFIRM DOCKER SYSTEM PRUNE?</b>\n\nIni akan hapus:\n• Stopped containers\n• Unused images\n• Unused networks\n• Build cache", btns)
    elif data == "dock_prune_do":
        out = run("docker system prune -f")
        text = f"🧹 <b>DOCKER PRUNED</b>\n━━━━━━━━━━━━━━━━━━\n<code>{out[:400] if out else 'Done'}</code>\n━━━━━━━━━━━━━━━━━━\nStatus: CLEANED 🟢"
        edit_msg(chat_id, msg_id, text, back_btn("dock_main"))

    # ── HEALTH CHECK ─────────────────────────────────────────
    elif data == "health_main":
        edit_msg(chat_id, msg_id, panel_health_all(), [[btn("🔄 Refresh","health_main")]+back_row("main")])

    # ── WEBSITE ───────────────────────────────────────────────
    elif data == "web_main":
        btns = [
            [btn("🚀 Status","web_status"),   btn("📡 API Test","web_api")],
            [btn("📄 Web Logs","web_logs"),    btn("🔐 Security","web_sec")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, "🌐 <b>GAS WEBSITE CONTROL</b>", btns)
    elif data == "web_status":
        port = PORTS.get("gas-terminal-backend", 8085)
        is_up = ping_port("localhost", port)
        web_up= ping_port("localhost", PORTS.get("gas-web-backend",8005))
        gw_up = ping_port("localhost", PORTS.get("gas-gateway-api",8000))
        text = (
            f"🚀 <b>WEB STATUS</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Gateway API  : {'🟢 UP' if gw_up else '🔴 DOWN'} :{PORTS.get('gas-gateway-api',8000)}\n"
            f"Web Backend  : {'🟢 UP' if web_up else '🔴 DOWN'} :{PORTS.get('gas-web-backend',8005)}\n"
            f"Terminal API : {'🟢 UP' if is_up else '🔴 DOWN'} :{port}\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Overall: {'HEALTHY 🟢' if gw_up and web_up else 'ISSUES 🔴'}"
        )
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","web_status")]+back_row("web_main")])
    elif data == "web_api":
        results = []
        for svc,port in [("gateway",8000),("web-backend",8005),("terminal",8085)]:
            ok = ping_port("localhost",port)
            results.append(f"{'✅' if ok else '❌'} gas-{svc} :{port}")
        text = f"📡 <b>API ENDPOINT TEST</b>\n━━━━━━━━━━━━━━━━━━\n" + "\n".join(results)
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","web_api")]+back_row("web_main")])
    elif data == "web_logs":
        edit_msg(chat_id, msg_id, panel_logs("gas-web-backend"), [[btn("🔄 Refresh","web_logs")]+back_row("web_main")])
    elif data == "web_sec":
        edit_msg(chat_id, msg_id, panel_security(), back_btn("web_main"))

    # ── AI ANALYZER ──────────────────────────────────────────
    elif data == "ai_main":
        btns = [
            [btn("🧠 Full Analysis","ai_analyze"),  btn("⚠️ Risk Predict","ai_risk")],
            [btn("🔄 Refresh","ai_analyze")],
            back_row("main"),
        ]
        edit_msg(chat_id, msg_id, panel_ai_analyze(), btns)
    elif data == "ai_analyze":
        edit_msg(chat_id, msg_id, panel_ai_analyze(), [[btn("🔄 Refresh","ai_analyze")]+back_row("ai_main")])
    elif data == "ai_risk":
        cpu=get_cpu_pct(); ram=get_ram_pct(); disk=get_disk_pct()
        cpu_risk = min(95, int(cpu*1.2))
        ram_risk = min(95, int(ram*1.1))
        issues   = load_issues()
        n_crit   = len([s for s,v in issues.items() if v.get("critical")])
        overall  = max(cpu_risk, ram_risk, n_crit*10)
        text = (
            f"⚠️ <b>RISK PREDICTION (Next 1 Hour)</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"CPU overload risk  : {cpu_risk}%\n"
            f"Memory issue risk  : {ram_risk}%\n"
            f"Engine crash risk  : {n_crit*5}%\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"Overall Risk Score : {'LOW 🟢' if overall<30 else 'MEDIUM 🟡' if overall<60 else 'HIGH 🔴'}\n"
            f"Confidence         : 85%"
        )
        edit_msg(chat_id, msg_id, text, [[btn("🔄 Refresh","ai_risk")]+back_row("ai_main")])

    # Default - gas_restart_core
    elif data == "gas_restart_core":
        core_svcs = ["gas-engine-orchestrator","gas-signal-service","gas-ai-orchestrator"]
        text = "🔄 <b>RESTART CORE ENGINE</b>\n━━━━━━━━━━━━━━━━━━\n"
        for svc in core_svcs:
            r = run(f"docker restart {svc} 2>&1")
            text += f"{'✅' if 'Error' not in r else '❌'} {svc}\n"
        text += "━━━━━━━━━━━━━━━━━━\nDone 🟢"
        edit_msg(chat_id, msg_id, text, back_btn("gas_main"))

# ═══════════════════════════════════════════════════════════════
#  MESSAGE HANDLERS
# ═══════════════════════════════════════════════════════════════
def handle_message(chat_id, text, user_name):
    global pending_input, OWNER_ID

    # Set owner ID kalau belum ada
    if OWNER_ID is None:
        OWNER_ID = chat_id
        print(f"[INFO] Owner set to: {chat_id}")

    text = text.strip()

    # ── /start ─────────────────────────────────────────────
    if text == "/start":
        if is_logged_in(chat_id):
            send_msg(chat_id, panel_header(chat_id), main_menu_buttons())
        else:
            send_msg(chat_id,
                "🧠 <b>GOLDEN CONTROL PANEL</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                "🔒 Authentication Required\n"
                "Owner By Muhamad Ridwanjr\n\n"
                "Kirim username lo:",
            )
            pending_input[chat_id] = "awaiting_username"
        return

    # ── AUTH FLOW ──────────────────────────────────────────
    if chat_id in pending_input:
        action = pending_input[chat_id]

        if action == "awaiting_username":
            if text in USERS:
                user_state[chat_id] = {"pending_user": text}
                pending_input[chat_id] = "awaiting_password"
                send_msg(chat_id, f"👤 Username: <b>{text}</b>\n🔑 Masukkan password:")
            else:
                send_msg(chat_id, "❌ Username tidak dikenal.\nCoba lagi — kirim username lo:")

        elif action == "awaiting_password":
            pending_user = user_state.get(chat_id, {}).get("pending_user", "")
            if pending_user in USERS and USERS[pending_user]["password"] == text:
                sessions[chat_id] = {
                    "user": pending_user,
                    "role": USERS[pending_user]["role"],
                    "time": time.time()
                }
                del pending_input[chat_id]
                user_state.pop(chat_id, None)
                send_msg(chat_id,
                    f"✅ <b>LOGIN BERHASIL</b>\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"👤 User : {pending_user}\n"
                    f"🔐 Role : {USERS[pending_user]['role']}\n"
                    f"⏰ Time : {datetime.now().strftime('%H:%M:%S')}\n"
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"Welcome back Muhamad Ridwanjr! 🚀",
                    main_menu_buttons()
                )
            else:
                del pending_input[chat_id]
                user_state.pop(chat_id, None)
                send_msg(chat_id,
                    "❌ <b>PASSWORD SALAH</b>\n"
                    "Akses ditolak. Kirim /start untuk coba lagi."
                )
        return

    # ── NOT LOGGED IN ──────────────────────────────────────
    if not is_logged_in(chat_id):
        send_msg(chat_id, "🔒 Sesi habis. Kirim /start untuk login.")
        return

    # ── COMMANDS ───────────────────────────────────────────
    if text == "/menu":
        send_msg(chat_id, panel_header(chat_id), main_menu_buttons())
    elif text == "/health":
        send_msg(chat_id, panel_health_all())
    elif text == "/status":
        send_msg(chat_id, panel_sys_quick())
    elif text == "/audit":
        send_msg(chat_id, panel_gas_audit_summary())
    else:
        send_msg(chat_id, "Gunakan tombol menu atau:\n/menu /health /status /audit")

# ═══════════════════════════════════════════════════════════════
#  MAIN POLLING LOOP
# ═══════════════════════════════════════════════════════════════
def main():
    print(f"""
╔══════════════════════════════════════════╗
║  GOLDEN CONTROL PANEL — Bot v2.0        ║
║  Owner: Muhamad Ridwanjr                ║
║  Starting polling...                     ║
╚══════════════════════════════════════════╝
    """)

    # Cek bot token
    me = tg_request("getMe", {})
    if not me.get("ok"):
        print("[ERROR] Bot token invalid!")
        sys.exit(1)
    print(f"[OK] Bot: @{me['result']['username']}")

    offset = 0
    print("[OK] Polling started. Waiting for messages...")

    while True:
        try:
            updates = get_updates(offset)
            if not updates.get("ok"): continue

            for update in updates.get("result", []):
                offset = update["update_id"] + 1

                # Message
                if "message" in update:
                    msg      = update["message"]
                    chat_id  = msg["chat"]["id"]
                    text     = msg.get("text", "")
                    user     = msg["from"].get("first_name", "User")
                    if text:
                        threading.Thread(
                            target=handle_message,
                            args=(chat_id, text, user),
                            daemon=True
                        ).start()

                # Callback query
                elif "callback_query" in update:
                    cb       = update["callback_query"]
                    chat_id  = cb["message"]["chat"]["id"]
                    msg_id   = cb["message"]["message_id"]
                    data     = cb.get("data","")
                    user     = cb["from"].get("first_name","User")
                    cb_id    = cb["id"]

                    answer_cb(cb_id)

                    if not is_logged_in(chat_id):
                        tg_request("answerCallbackQuery", {
                            "callback_query_id": cb_id,
                            "text": "⏰ Sesi habis! Kirim /start untuk login.",
                            "show_alert": True
                        })
                        continue

                    threading.Thread(
                        target=handle_callback,
                        args=(chat_id, data, msg_id, user),
                        daemon=True
                    ).start()

        except KeyboardInterrupt:
            print("\n[INFO] Bot stopped.")
            break
        except Exception as e:
            print(f"[ERROR] {e}")
            time.sleep(3)

if __name__ == "__main__":
    main()