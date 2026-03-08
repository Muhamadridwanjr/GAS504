#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════╗
║          GAS TOOLS — GoldenAI Strategy Management Tool          ║
║          Version 1.0 | by mridwan3101                           ║
║          Supports: VPS SSH + Docker                             ║
╚══════════════════════════════════════════════════════════════════╝

MENU:
  1. 🔍 Audit & Debug      — Scan, debug, rescan semua service
  2. 🚀 Deploy & Restart   — Build, deploy, restart, rollback
  3. 📊 Monitor & Log      — Status, log realtime, health check
  4. 🔑 ENV Manager        — List, edit, validasi env
  5. 🖥️  Terminal UI        — Test endpoint, cek frontend, debug BE+FE+koneksi+laporan
  6. 📈 Grafana & Observ.  — Prometheus, Loki, Grafana guide
  7. 🐳 Docker Manager     — PS, stats, prune, inspect
  8. 🔌 Health Check       — Ping semua endpoint GAS
  9. 📋 Laporan            — Generate report lengkap
  0. ❌ Keluar
"""

import os, sys, time, subprocess, json, shutil, socket
import urllib.request, urllib.error
from datetime import datetime
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
#  WARNA & UI
# ═══════════════════════════════════════════════════════════════
class C:
    RED='\033[0;31m';     GREEN='\033[0;32m';   YELLOW='\033[1;33m'
    BLUE='\033[0;34m';    CYAN='\033[0;36m';    MAGENTA='\033[0;35m'
    WHITE='\033[1;37m';   BOLD='\033[1m';       DIM='\033[2m'
    BG_RED='\033[41m';    BG_GREEN='\033[42m';  BG_BLUE='\033[44m'
    NC='\033[0m'

def c(color, text):  return f"{color}{text}{C.NC}"
def clear():         os.system('clear')
def pause():         input(c(C.DIM, "\n  Tekan Enter untuk kembali..."))

def divider(title="", color=C.BLUE, width=60):
    if title:
        pad = (width - len(title) - 2) // 2
        print(c(color, "─"*pad + f" {title} " + "─"*pad))
    else:
        print(c(color, "─"*width))

def banner():
    print(c(C.YELLOW, """
   ██████╗  █████╗ ███████╗    ████████╗ ██████╗  ██████╗ ██╗     ███████╗
  ██╔════╝ ██╔══██╗██╔════╝       ██╔══╝██╔═══██╗██╔═══██╗██║     ██╔════╝
  ██║  ███╗███████║███████╗        ██║  ██║   ██║██║   ██║██║     ███████╗
  ██║   ██║██╔══██║╚════██║        ██║  ██║   ██║██║   ██║██║     ╚════██║
  ╚██████╔╝██║  ██║███████║        ██║  ╚██████╔╝╚██████╔╝███████╗███████║
   ╚═════╝ ╚═╝  ╚═╝╚══════╝        ╚═╝   ╚═════╝  ╚═════╝ ╚══════╝╚══════╝"""))
    print(c(C.WHITE,  "  GoldenAI Strategy — Management Tool v1.0"))
    print(c(C.DIM,    f"  {datetime.now().strftime('%A, %d %B %Y — %H:%M:%S')}"))
    _status_bar()
    print()

def _status_bar():
    tmux_s   = c(C.GREEN,  "tmux ✓") if in_tmux()      else c(C.YELLOW, "tmux ✗")
    claude_s = c(C.GREEN,  "claude ✓") if check_claude() else c(C.RED,   "claude ✗")
    docker_s = c(C.GREEN,  "docker ✓") if check_docker() else c(C.RED,   "docker ✗")
    apikey_s = c(C.RED,    " ⚠ API_KEY aktif!") if check_api_key_conflict() else ""
    running  = len(get_running())
    total    = len(ALL_SERVICES)
    print(c(C.DIM, f"  [{tmux_s}{C.DIM}] [{claude_s}{C.DIM}] [{docker_s}{C.DIM}] "
                   f"[{c(C.CYAN, str(running))}{C.DIM}/{c(C.WHITE,str(total))}{C.DIM} containers]{apikey_s}"))

# ═══════════════════════════════════════════════════════════════
#  CONFIG & DATA
# ═══════════════════════════════════════════════════════════════
BASE_DIR      = Path.home() / "goldenaistrategy"
LOG_BASE      = Path.home() / "gas-logs"
ISSUES_FILE   = Path.home() / ".gas-issues.json"
REPORT_DIR    = Path.home() / "gas-reports"
SLEEP_NORMAL  = 40
SLEEP_LONG    = 90

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
    "obs":      ["gas-grafana","gas-prometheus","gas-loki","gas-promtail"],
    "infra":    ["gas-redis","gas-minio"],
}

ICONS = {
    "core":"🔷","data":"📊","engine":"⚙️ ","ai":"🤖","quant":"📈",
    "realtime":"⚡","terminal":"💻","api":"🔌","obs":"📈","infra":"🗄️ "
}

# Port mapping semua service
PORTS = {
    "gas-gateway-api":8000,"gas-auth-service":8001,"gas-user-service":8002,
    "gas-billing-service":8004,"gas-telegram-bot":8003,"gas-web-backend":8005,
    "gas-mt5-data-service":8100,"gas-mt5-websocket":8110,"gas-data-ingestor":9604,
    "gas-calendar-news-service":9601,"gas-fundamental-data-service":9603,
    "gas-engine-orchestrator":8105,"gas-indicator-engine":8203,"gas-smc-engine":8006,
    "gas-signal-service":8106,"gas-alert-engine":8400,"gas-journal-service":8107,
    "gas-strategy-core":7003,"gas-ai-orchestrator":9003,"gas-rag-technical":9001,
    "gas-rag-macro":9002,"gas-vector-db":9004,"gas-feature-engine":9499,
    "gas-quant-orch":9500,"gas-regime-detector":9503,"gas-pattern-detector":9501,
    "gas-statarb-engine":9502,"gas-quant-backtester":9504,"gas-market-phase":9510,
    "gas-risk-engine":9511,"gas-correlation":9512,"gas-trend-engine":9513,
    "gas-orderflow":9514,"gas-realtime-hub":8111,"gas-notification-service":8112,
    "gas-terminal-service":8206,"gas-terminal-backend":8085,"gas-term-service":8205,
    "gas-screener-service":9600,"gas-tradingplan-service":9602,
    "gas-chart-service":9700,"gas-social-service":8500,
    "gas-grafana":3000,"gas-prometheus":9090,"gas-loki":3100,
    "gas-redis":6379,"gas-minio":9000,
}

ALL_SERVICES = [(s, cat) for cat, svcs in SERVICES.items() for s in svcs]

# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def _find_claude():
    """Cari claude binary di beberapa lokasi umum Ubuntu"""
    candidates = [
        "claude",                                    # kalau sudah di PATH
        os.path.expanduser("~/.npm-global/bin/claude"),
        os.path.expanduser("~/.local/bin/claude"),
        "/usr/local/bin/claude",
        "/usr/bin/claude",
    ]
    for path in candidates:
        try:
            r = subprocess.run([path, "--version"], capture_output=True)
            if r.returncode == 0:
                return path
        except FileNotFoundError:
            continue
    return None

def check_claude():
    return _find_claude() is not None

def check_docker():
    return subprocess.run(["which","docker"],capture_output=True).returncode==0

def in_tmux():
    return os.environ.get("TMUX") is not None

def check_api_key_conflict():
    """Peringatkan kalau ANTHROPIC_API_KEY aktif — akan pakai billing API bukan Pro quota"""
    return os.environ.get("ANTHROPIC_API_KEY") is not None

def get_running():
    r = subprocess.run(["docker","ps","--format","{{.Names}}"],capture_output=True,text=True)
    return set(r.stdout.strip().split('\n')) if r.returncode==0 else set()

def get_all_containers():
    r = subprocess.run(["docker","ps","-a","--format","{{.Names}}\t{{.Status}}\t{{.Image}}"],
                       capture_output=True,text=True)
    result = {}
    for line in r.stdout.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 2:
            result[parts[0]] = {"status":parts[1],"image":parts[2] if len(parts)>2 else ""}
    return result

def load_json(path):
    if Path(path).exists():
        try:
            with open(path) as f: return json.load(f)
        except: return {}
    return {}

def save_json(path, data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,'w') as f: json.dump(data,f,indent=2)

def run_cmd(cmd, cwd=None, capture=True):
    try:
        r = subprocess.run(cmd, shell=isinstance(cmd,str),
                          capture_output=capture, text=True, cwd=cwd)
        return r.stdout, r.stderr, r.returncode
    except Exception as e:
        return "", str(e), 1

def run_claude(prompt, cwd, timeout=300):
    claude_bin = _find_claude()
    if not claude_bin:
        return "[ERROR] Claude CLI tidak ditemukan. Jalankan setup-claude.sh dulu!", False
    # Hapus API key dari env supaya pakai quota Pro $20, bukan API billing
    env = os.environ.copy()
    env.pop("ANTHROPIC_API_KEY", None)
    try:
        r = subprocess.run(
            [claude_bin, "--print", prompt],
            capture_output=True, text=True,
            cwd=str(cwd), timeout=timeout, env=env
        )
        return r.stdout, r.returncode==0
    except subprocess.TimeoutExpired:
        return "[TIMEOUT] Claude tidak merespons dalam 5 menit", False
    except Exception as e:
        return f"[ERROR] {e}", False

def ping_port(host, port, timeout=2):
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((host, port))
        s.close()
        return True
    except: return False

def save_log(path, content, header=""):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,'w') as f:
        if header: f.write(header + "\n" + "="*54 + "\n\n")
        f.write(content)

def parse_scan(output):
    issues = {"env_missing":[],"critical":[],"warning":[],"status":"OK"}
    for line in output.split('\n'):
        line = line.strip()
        if line.startswith("ENV_MISSING:"):
            val = line.replace("ENV_MISSING:","").strip()
            if val and val.upper()!="NONE":
                issues["env_missing"]=[e.strip() for e in val.split(',') if e.strip()]
        elif line.startswith("CRITICAL:"):
            val = line.replace("CRITICAL:","").strip()
            if val and val.upper()!="NONE": issues["critical"].append(val)
        elif line.startswith("WARNING:"):
            val = line.replace("WARNING:","").strip()
            if val and val.upper()!="NONE": issues["warning"].append(val)
        elif line.startswith("STATUS:"):
            issues["status"] = line.replace("STATUS:","").strip()
    return issues

# ═══════════════════════════════════════════════════════════════
#  PROMPTS CLAUDE
# ═══════════════════════════════════════════════════════════════
PROMPT_SCAN = lambda s: f"""Scan cepat service '{s}'. Cari:
1. ENV variable WAJIB yang mungkin missing
2. Bug kritis yang bikin crash
3. Koneksi ke service lain bermasalah

Format WAJIB (max 20 baris):
ENV_MISSING: [list env, pisah koma, atau NONE]
CRITICAL: [masalah fatal atau NONE]
WARNING: [masalah sedang atau NONE]
STATUS: [OK atau PERLU_PERHATIAN]"""

PROMPT_DEBUG = lambda s, issue: f"""Debug mendalam service '{s}'.
ISSUE DARI SCAN:
{issue}
Berikan:
1. Root cause tiap issue
2. Fix konkret + kode jika perlu
3. Langkah step by step

Format: ISSUE → ROOT CAUSE → FIX → LANGKAH"""

PROMPT_ENV = lambda s: f"""List SEMUA env variable yang dibutuhkan service '{s}'.
Format per baris: NAMA_VAR | fungsi | contoh_value | WAJIB/OPSIONAL"""

PROMPT_REVIEW_FRONTEND = lambda s: f"""Review UI/UX dan kode frontend service '{s}'.
Cek: komponen broken, API call salah, responsive issues, error handling UI.
Format: ISSUE | SEVERITY | FIX"""

PROMPT_DEBUG_TERMINAL_BE = """Debug mendalam gas-terminal-backend service.
Cek secara menyeluruh:
1. Semua route/endpoint yang ada (routes/ folder) dan apakah sudah terhubung ke GAS service lain
2. Koneksi ke: gas-chart-service:9700, gas-signal-service:8106, gas-mt5-data-service:8100,
   gas-gateway-api:8000, gas-auth-service:8001, gas-redis:6379, gas-realtime-hub:8111
3. Konfigurasi CORS — apakah frontend bisa connect?
4. WebSocket handler di ws/ folder
5. Config .env — apakah semua URL service sudah diset?
6. Import error, circular dependency, missing module
Format tiap issue: ISSUE | SEVERITY(CRITICAL/WARNING/INFO) | ROOT CAUSE | FIX KONKRET"""

PROMPT_DEBUG_TERMINAL_FE = """Debug mendalam gas-terminal-frontend React/Vite app.
Cek secara menyeluruh:
1. File .env/.env.local — VITE_API_URL sudah pointing ke gas-terminal-backend:8085?
2. services/api.js — base URL dan endpoint path sudah benar?
3. Komponen utama: MarketsView, SignalView, TradingViewChart, StaticChart — ada error?
4. WebSocket connection — sudah handle reconnect dan error?
5. constants.js — URL/port hardcoded yang salah?
6. Import yang missing, package.json dependencies
7. CORS error saat fetch ke backend
Format tiap issue: ISSUE | SEVERITY(CRITICAL/WARNING/INFO) | ROOT CAUSE | FIX KONKRET"""

PROMPT_GRAFANA_EXPLAIN = """Jelaskan dashboard Grafana untuk monitoring microservices:
1. Metric penting yang harus dipantau (CPU, RAM, request rate, error rate)
2. Alert yang sebaiknya dibuat
3. Query Prometheus yang berguna
4. Cara baca Loki logs
Buat penjelasan mudah dipahami developer yang baru pakai Grafana."""

# ═══════════════════════════════════════════════════════════════
#  MENU 1: AUDIT & DEBUG
# ═══════════════════════════════════════════════════════════════
def menu_audit():
    while True:
        clear(); banner()
        divider("🔍 AUDIT & DEBUG", C.CYAN)

        issues   = load_json(ISSUES_FILE)
        n_crit   = len([s for s,v in issues.items() if v.get("critical")])
        n_env    = len([s for s,v in issues.items() if v.get("env_missing")])
        n_debug  = len([s for s,v in issues.items() if v.get("debugged")])

        print(f"""
  {c(C.CYAN,'1.')} 🔍 Scan Semua Service
     {c(C.DIM,'Scan ringan, temukan service bermasalah.')}

  {c(C.CYAN,'2.')} 🔧 Debug Per Service
     {c(C.DIM,f'Debug mendalam — {n_crit} critical, {n_env} env missing')}

  {c(C.CYAN,'3.')} 🔄 Rescan Setelah Fix
     {c(C.DIM,'Verifikasi service yang sudah difix.')}

  {c(C.CYAN,'4.')} 📊 Ringkasan Hasil Scan
     {c(C.DIM,f'Total scanned: {len(issues)} | Debug done: {n_debug}')}

  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': audit_scan_all()
        elif ch=='2': audit_debug_menu()
        elif ch=='3': audit_rescan()
        elif ch=='4': audit_summary(); pause()
        elif ch=='0': break

def audit_scan_all():
    clear(); banner()
    divider("SCAN SEMUA SERVICE", C.CYAN)
    total = len(ALL_SERVICES)
    print(f"\n  Total   : {c(C.WHITE,str(total))} service")
    print(f"  Estimasi: ~{total} menit")
    print(f"  Jeda    : {SLEEP_NORMAL}s antar service\n")

    if not in_tmux():
        print(c(C.YELLOW,"  ⚠️  Belum di tmux! Jalankan: tmux new -s gas-audit\n"))

    if input(c(C.WHITE,"  Mulai scan? (y/n): ")).strip().lower() != 'y': return

    session = datetime.now().strftime("%Y%m%d-%H%M")+"-scan"
    log_dir = LOG_BASE / session
    log_dir.mkdir(parents=True, exist_ok=True)
    issues  = load_json(ISSUES_FILE)
    print()

    for count,(svc,cat) in enumerate(ALL_SERVICES,1):
        icon     = ICONS.get(cat,"📦")
        svc_path = BASE_DIR / svc
        print(f"  {c(C.DIM,f'[{count}/{total}]')} {icon} {c(C.CYAN,svc):<46}",end="",flush=True)

        if not svc_path.exists():
            print(c(C.DIM,"✗ folder")); continue

        output,ok = run_claude(PROMPT_SCAN(svc), svc_path)
        save_log(log_dir/f"{svc}.txt", output, f"SCAN: {svc}")
        parsed = parse_scan(output)

        issues[svc] = {
            "category":svc,"cat":cat,"scan_time":datetime.now().isoformat(),
            "log":str(log_dir/f"{svc}.txt"),"env_missing":parsed["env_missing"],
            "critical":parsed["critical"],"warning":parsed["warning"],
            "status":parsed["status"],"debugged":False,"env_fixed":False,
        }
        save_json(ISSUES_FILE, issues)

        if parsed["critical"]:   print(c(C.RED,   f" 🔴 {len(parsed['critical'])} critical"))
        elif parsed["env_missing"]: print(c(C.YELLOW," 🟡 env missing"))
        else:                    print(c(C.GREEN,  " ✅ OK"))

        if count < total:
            if count%10==0:
                print(c(C.YELLOW,f"\n  ⏸️  Istirahat 90 detik...\n"))
                time.sleep(SLEEP_LONG)
            else:
                time.sleep(SLEEP_NORMAL)

    print(); audit_summary(); pause()

def audit_debug_menu():
    clear(); banner()
    issues = load_json(ISSUES_FILE)
    if not issues:
        print(c(C.YELLOW,"\n  Belum ada hasil scan!")); pause(); return

    problem = [(s,v) for s,v in issues.items() if v.get("critical") or v.get("env_missing")]
    if not problem:
        print(c(C.GREEN,"\n  ✅ Semua service OK!")); pause(); return

    divider("DEBUG PER SERVICE", C.CYAN)
    print()
    for i,(svc,data) in enumerate(problem,1):
        done = c(C.GREEN,"✅") if data.get("debugged") else c(C.DIM,"  ")
        icon = ICONS.get(data.get("cat",""),"📦")
        tags = []
        if data.get("critical"):   tags.append(c(C.RED,   f"🔴{len(data['critical'])}"))
        if data.get("env_missing"):tags.append(c(C.YELLOW, "🟡env"))
        print(f"  {done} {c(C.CYAN,str(i)+'.')} {icon} {svc:<44} {' '.join(tags)}")

    print(f"\n  {c(C.CYAN,'A.')} Debug SEMUA sekaligus")
    print(f"  {c(C.CYAN,'0.')} ← Kembali\n")
    ch = input(c(C.WHITE,"  Pilih: ")).strip().upper()

    if ch=='0': return
    elif ch=='A':
        for i,(svc,data) in enumerate(problem):
            if not data.get("debugged"):
                _do_debug(svc,data,issues)
                if i<len(problem)-1: time.sleep(SLEEP_NORMAL)
    else:
        try:
            idx=int(ch)-1
            if 0<=idx<len(problem): _do_debug(problem[idx][0],problem[idx][1],issues)
        except ValueError: pass
    pause()

def _do_debug(service, data, issues):
    svc_path = BASE_DIR / service
    if not svc_path.exists():
        print(c(C.RED,f"\n  ❌ Folder {service} tidak ditemukan")); return

    print(f"\n  {c(C.CYAN,f'🔧 Debugging: {service}')}")
    issue_text = ""
    if data.get("critical"):   issue_text += "CRITICAL:\n"  +"\n".join(f"- {i}" for i in data["critical"])+"\n"
    if data.get("env_missing"):issue_text += "ENV MISSING:\n"+"\n".join(f"- {e}" for e in data["env_missing"])+"\n"
    if data.get("warning"):    issue_text += "WARNING:\n"   +"\n".join(f"- {w}" for w in data["warning"][:3])+"\n"

    print(c(C.DIM,"  Menjalankan debug Claude..."),flush=True)
    output,ok = run_claude(PROMPT_DEBUG(service,issue_text), svc_path)

    debug_file = LOG_BASE/f"debug-{service}-{datetime.now().strftime('%Y%m%d-%H%M')}.txt"
    save_log(debug_file, output, f"DEBUG: {service}\n\nISSUES:\n{issue_text}\n\nHASIL:")
    issues[service].update({"debugged":True,"debug_log":str(debug_file),
                            "debug_time":datetime.now().isoformat()})
    save_json(ISSUES_FILE, issues)

    print(c(C.GREEN if ok else C.RED, f"  {'✅ Selesai' if ok else '❌ Gagal'} → {debug_file}"))
    print(f"\n{c(C.WHITE,'  Preview hasil:')}")
    for line in output[:600].split('\n'): print(f"    {line}")
    if len(output)>600: print(c(C.DIM,f"  ... (lihat: {debug_file})"))

def audit_rescan():
    clear(); banner()
    issues    = load_json(ISSUES_FILE)
    to_rescan = [(s,v) for s,v in issues.items() if v.get("env_fixed") or v.get("debugged")]
    if not to_rescan:
        print(c(C.YELLOW,"\n  Belum ada service yang di-fix.")); pause(); return

    divider("RESCAN SETELAH FIX", C.CYAN)
    print(f"\n  {c(C.WHITE,f'{len(to_rescan)} service akan di-rescan:')}\n")
    for svc,data in to_rescan:
        print(f"  {ICONS.get(data.get('cat',''),'📦')} {svc}")

    if input(c(C.WHITE,"\n  Mulai rescan? (y/n): ")).strip().lower() != 'y': return

    log_dir = LOG_BASE/( datetime.now().strftime("%Y%m%d-%H%M")+"-rescan")
    log_dir.mkdir(parents=True, exist_ok=True)
    print()

    for i,(svc,data) in enumerate(to_rescan,1):
        svc_path = BASE_DIR/svc
        print(f"  [{i}/{len(to_rescan)}] {ICONS.get(data.get('cat',''),'📦')} {c(C.CYAN,svc):<46}",end="",flush=True)
        if not svc_path.exists(): print(c(C.DIM,"✗ folder")); continue

        output,_ = run_claude(PROMPT_SCAN(svc), svc_path)
        parsed   = parse_scan(output)
        save_log(log_dir/f"{svc}.txt", output, f"RESCAN: {svc}")
        issues[svc].update({"rescan_time":datetime.now().isoformat(),
                            "rescan_critical":parsed["critical"],
                            "rescan_env":parsed["env_missing"]})
        save_json(ISSUES_FILE, issues)

        bad = parsed["critical"] or parsed["env_missing"]
        print(c(C.RED," 🔴 masih ada issue") if bad else c(C.GREEN," ✅ clean!"))
        if i<len(to_rescan): time.sleep(SLEEP_NORMAL)

    pause()

def audit_summary():
    issues = load_json(ISSUES_FILE)
    if not issues: print(c(C.YELLOW,"\n  Belum ada hasil scan.")); return

    total    = len(issues)
    critical = [s for s,v in issues.items() if v.get("critical")]
    env_miss = [s for s,v in issues.items() if v.get("env_missing")]
    ok_list  = [s for s,v in issues.items() if not v.get("critical") and not v.get("env_missing")]
    debugged = [s for s,v in issues.items() if v.get("debugged")]

    print(); divider("RINGKASAN SCAN", C.WHITE)
    print(f"  Total service  : {c(C.WHITE, str(total))}")
    print(f"  🔴 Critical    : {c(C.RED,    str(len(critical)))}")
    print(f"  🟡 ENV Missing : {c(C.YELLOW, str(len(env_miss)))}")
    print(f"  ✅ OK          : {c(C.GREEN,  str(len(ok_list)))}")
    print(f"  🔧 Sudah debug : {c(C.CYAN,   str(len(debugged)))}")

    if critical:
        print(f"\n  {c(C.RED,'🔴 Critical:')}")
        for s in critical:
            print(f"    → {c(C.CYAN,s)}")
            for i in issues[s].get("critical",[])[:2]:
                print(f"      {c(C.DIM,'• '+str(i)[:65])}")
    if env_miss:
        print(f"\n  {c(C.YELLOW,'🟡 ENV Missing:')}")
        for s in env_miss:
            fixed  = issues[s].get("env_fixed",False)
            status = c(C.GREEN,"✅") if fixed else c(C.YELLOW,"⚠️ ")
            envs   = issues[s].get("env_missing",[])
            print(f"    {status} {s}: {c(C.DIM,', '.join(envs[:4]))}")

# ═══════════════════════════════════════════════════════════════
#  MENU 2: DEPLOY & RESTART
# ═══════════════════════════════════════════════════════════════
def menu_deploy():
    while True:
        clear(); banner()
        divider("🚀 DEPLOY & RESTART", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} ▶️  Start Service
  {c(C.CYAN,'2.')} ⏹️  Stop Service
  {c(C.CYAN,'3.')} 🔄 Restart Service
  {c(C.CYAN,'4.')} 🏗️  Build & Deploy Ulang
  {c(C.CYAN,'5.')} 🔄 Restart SEMUA Service
  {c(C.CYAN,'6.')} ⏹️  Stop SEMUA Service
  {c(C.CYAN,'7.')} 📋 Lihat docker-compose.yml
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': deploy_action("start")
        elif ch=='2': deploy_action("stop")
        elif ch=='3': deploy_action("restart")
        elif ch=='4': deploy_build()
        elif ch=='5': deploy_restart_all()
        elif ch=='6': deploy_stop_all()
        elif ch=='7': deploy_show_compose()
        elif ch=='0': break

def _pick_service(prompt="Pilih service"):
    running = get_running()
    all_c   = get_all_containers()
    gas_c   = {k:v for k,v in all_c.items() if k.startswith("gas-")}

    if not gas_c:
        print(c(C.YELLOW,"\n  Tidak ada container GAS ditemukan.")); return None

    items = list(gas_c.items())
    for i,(name,data) in enumerate(items,1):
        up   = "Up" in data["status"]
        stat = c(C.GREEN,"● running") if up else c(C.RED,"○ stopped")
        print(f"  {c(C.CYAN,str(i)+'.')} {name:<50} {stat}")

    print(f"  {c(C.CYAN,'0.')} ← Batal\n")
    ch = input(c(C.WHITE,f"  {prompt}: ")).strip()
    try:
        idx = int(ch)-1
        if 0<=idx<len(items): return items[idx][0]
    except ValueError: pass
    return None

def deploy_action(action):
    clear(); banner()
    divider(f"{action.upper()} SERVICE", C.CYAN)
    print()
    svc = _pick_service(f"Pilih service untuk di-{action}")
    if not svc: return

    print(f"\n  {action.capitalize()} {c(C.CYAN,svc)}...")
    stdout,stderr,code = run_cmd(f"docker {action} {svc}")
    if code==0: print(c(C.GREEN,f"  ✅ {svc} berhasil di-{action}"))
    else:       print(c(C.RED,  f"  ❌ Gagal: {stderr[:200]}"))
    pause()

def deploy_build():
    clear(); banner()
    divider("BUILD & DEPLOY", C.CYAN)
    print()
    svc = _pick_service("Pilih service untuk di-build ulang")
    if not svc: return

    svc_path = BASE_DIR / svc
    if not svc_path.exists():
        print(c(C.RED,f"\n  ❌ Folder {svc} tidak ditemukan")); pause(); return

    print(f"\n  Building {c(C.CYAN,svc)}...")
    print(c(C.DIM,"  Menjalankan docker compose up --build -d ...\n"))

    proc = subprocess.Popen(
        ["docker","compose","up","--build","-d"],
        cwd=str(svc_path), stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, text=True
    )
    for line in proc.stdout:
        print(f"  {c(C.DIM,line.rstrip())}")
    proc.wait()

    if proc.returncode==0: print(c(C.GREEN,f"\n  ✅ {svc} berhasil di-build dan deploy!"))
    else:                  print(c(C.RED,  f"\n  ❌ Build gagal (code {proc.returncode})"))
    pause()

def deploy_restart_all():
    clear(); banner()
    divider("RESTART SEMUA SERVICE", C.YELLOW)
    print(c(C.YELLOW,"\n  ⚠️  Ini akan restart SEMUA container GAS!\n"))
    if input(c(C.WHITE,"  Yakin? (ketik YES): ")).strip() != "YES": return

    running = get_running()
    gas_svc = [s for s in running if s.startswith("gas-")]
    print(f"\n  Restart {len(gas_svc)} service...\n")
    for svc in gas_svc:
        print(f"  🔄 {svc}...",end="",flush=True)
        _,_,code = run_cmd(f"docker restart {svc}")
        print(c(C.GREEN," ✅") if code==0 else c(C.RED," ❌"))
        time.sleep(1)
    print(c(C.GREEN,"\n  ✅ Semua service sudah di-restart!")); pause()

def deploy_stop_all():
    clear(); banner()
    divider("STOP SEMUA SERVICE", C.RED)
    print(c(C.RED,"\n  ⚠️  Ini akan STOP SEMUA container GAS!\n"))
    if input(c(C.WHITE,"  Yakin? (ketik YES): ")).strip() != "YES": return

    running = get_running()
    gas_svc = [s for s in running if s.startswith("gas-")]
    for svc in gas_svc:
        print(f"  ⏹️  {svc}...",end="",flush=True)
        _,_,code = run_cmd(f"docker stop {svc}")
        print(c(C.GREEN," ✅") if code==0 else c(C.RED," ❌"))
    pause()

def deploy_show_compose():
    clear(); banner()
    divider("DOCKER COMPOSE FILES", C.CYAN)
    print()
    composes = list(BASE_DIR.glob("*/docker-compose.yml"))
    for i,f in enumerate(composes,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {f.parent.name}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")
    ch = input(c(C.WHITE,"  Pilih untuk lihat isinya: ")).strip()
    try:
        idx = int(ch)-1
        if 0<=idx<len(composes):
            content = composes[idx].read_text()
            print(f"\n{c(C.WHITE,str(composes[idx]))}")
            print(c(C.DIM,"─"*60))
            for line in content.split('\n')[:50]:
                print(f"  {line}")
            if content.count('\n')>50: print(c(C.DIM,"  ... (file terpotong)"))
    except ValueError: pass
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 3: MONITOR & LOG
# ═══════════════════════════════════════════════════════════════
def menu_monitor():
    while True:
        clear(); banner()
        divider("📊 MONITOR & LOG", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} 🐳 Status Semua Container
  {c(C.CYAN,'2.')} 📋 Log Realtime (docker logs -f)
  {c(C.CYAN,'3.')} ❤️  Health Check Semua Service
  {c(C.CYAN,'4.')} 💾 Resource Usage (CPU & RAM)
  {c(C.CYAN,'5.')} 🔴 Tampilkan Container yang Error/Down
  {c(C.CYAN,'6.')} 🔍 Cari Error di Log Service
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': monitor_status()
        elif ch=='2': monitor_logs()
        elif ch=='3': monitor_health()
        elif ch=='4': monitor_resources()
        elif ch=='5': monitor_errors()
        elif ch=='6': monitor_search_log()
        elif ch=='0': break

def monitor_status():
    clear(); banner()
    divider("STATUS SEMUA CONTAINER", C.CYAN)
    stdout,_,_ = run_cmd("docker ps -a --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'")
    gas_lines  = [l for l in stdout.split('\n') if 'gas-' in l or 'NAMES' in l]
    print()
    for line in gas_lines:
        if "Up" in line:    print(f"  {c(C.GREEN, line)}")
        elif "Exited" in line: print(f"  {c(C.RED, line)}")
        else:               print(f"  {c(C.DIM, line)}")
    pause()

def monitor_logs():
    clear(); banner()
    divider("LOG REALTIME", C.CYAN)
    print()
    running = get_running()
    gas_svc = sorted([s for s in running if s.startswith("gas-")])
    for i,svc in enumerate(gas_svc,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {svc}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")

    ch = input(c(C.WHITE,"  Pilih service: ")).strip()
    try:
        idx = int(ch)-1
        if 0<=idx<len(gas_svc):
            svc = gas_svc[idx]
            lines = input(c(C.DIM,"  Berapa baris terakhir? (default 50): ")).strip() or "50"
            print(c(C.DIM,f"\n  Tekan Ctrl+C untuk berhenti...\n"))
            time.sleep(1)
            subprocess.run(["docker","logs","-f","--tail",lines,svc])
    except (ValueError, KeyboardInterrupt):
        pass
    pause()

def monitor_health():
    clear(); banner()
    divider("HEALTH CHECK SEMUA SERVICE", C.CYAN)
    running = get_running()
    print()

    ok_count = err_count = 0
    for svc,cat in ALL_SERVICES:
        icon = ICONS.get(cat,"📦")
        port = PORTS.get(svc)
        running_now = svc in running

        print(f"  {icon} {c(C.CYAN,svc):<46}",end="",flush=True)

        if not running_now:
            print(c(C.RED," ○ stopped"))
            err_count+=1; continue

        if port and ping_port("localhost",port):
            print(c(C.GREEN," ● healthy"))
            ok_count+=1
        elif port:
            print(c(C.YELLOW," ⚠ running tapi port tidak respond"))
            err_count+=1
        else:
            print(c(C.GREEN," ● running (no port check)"))
            ok_count+=1

    print(f"\n  {c(C.GREEN,f'✅ OK: {ok_count}')}  {c(C.RED,f'❌ Issue: {err_count}')}")
    pause()

def monitor_resources():
    clear(); banner()
    divider("RESOURCE USAGE (CPU & RAM)", C.CYAN)
    print(c(C.DIM,"\n  Loading docker stats...\n"))
    stdout,_,_ = run_cmd("docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}'")
    gas_lines  = [l for l in stdout.split('\n') if 'gas-' in l or 'NAME' in l]
    for line in gas_lines:
        if any(x in line for x in ['9','8','7'] if line.split('\t')[1:2] and '%' in line.split('\t')[1]):
            print(f"  {c(C.YELLOW,line)}")
        else:
            print(f"  {line}")
    pause()

def monitor_errors():
    clear(); banner()
    divider("CONTAINER ERROR / DOWN", C.RED)
    all_c = get_all_containers()
    gas_c = {k:v for k,v in all_c.items() if k.startswith("gas-")}

    down = [(k,v) for k,v in gas_c.items() if "Up" not in v["status"]]
    print()
    if not down:
        print(c(C.GREEN,"  ✅ Semua container GAS sedang berjalan!"))
    else:
        print(c(C.RED,f"  ❌ {len(down)} container bermasalah:\n"))
        for name,data in down:
            print(f"  🔴 {c(C.CYAN,name)}")
            print(f"     Status: {c(C.RED,data['status'])}")
            # Ambil 5 baris log terakhir
            stdout,_,_ = run_cmd(f"docker logs --tail 5 {name}")
            for line in stdout.split('\n')[-5:]:
                if line: print(f"     {c(C.DIM,line)}")
    pause()

def monitor_search_log():
    clear(); banner()
    divider("CARI ERROR DI LOG", C.CYAN)
    running = get_running()
    gas_svc = sorted([s for s in running if s.startswith("gas-")])

    for i,svc in enumerate(gas_svc,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {svc}")
    print(f"  {c(C.CYAN,'A.')} Cari di SEMUA service\n")

    ch    = input(c(C.WHITE,"  Pilih service: ")).strip().upper()
    kw    = input(c(C.WHITE,"  Kata kunci (contoh: ERROR, Exception): ")).strip()
    if not kw: return

    if ch == 'A':
        targets = gas_svc
    else:
        try:
            idx = int(ch)-1
            targets = [gas_svc[idx]] if 0<=idx<len(gas_svc) else []
        except ValueError: return

    print(f"\n  Mencari '{c(C.YELLOW,kw)}' di log...\n")
    for svc in targets:
        stdout,_,_ = run_cmd(f"docker logs --tail 200 {svc}")
        matches    = [l for l in stdout.split('\n') if kw.lower() in l.lower()]
        if matches:
            print(f"  {c(C.RED,'🔴')} {c(C.CYAN,svc)} — {len(matches)} match:")
            for m in matches[:5]:
                print(f"    {c(C.DIM,m[:100])}")
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 4: ENV MANAGER
# ═══════════════════════════════════════════════════════════════
def menu_env():
    while True:
        clear(); banner()
        divider("🔑 ENV MANAGER", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} 📋 List ENV yang Dibutuhkan (Claude analisis)
  {c(C.CYAN,'2.')} 🔍 Tampilkan .env yang Ada
  {c(C.CYAN,'3.')} ✏️  Edit .env Service
  {c(C.CYAN,'4.')} ✅ Validasi ENV (cek yang missing)
  {c(C.CYAN,'5.')} 📊 Status ENV Semua Service (dari scan)
  {c(C.CYAN,'6.')} 🏷️  Tandai Service Sudah Fix ENV
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': env_list_claude()
        elif ch=='2': env_show_file()
        elif ch=='3': env_edit()
        elif ch=='4': env_validate()
        elif ch=='5': env_status_all()
        elif ch=='6': env_mark_fixed()
        elif ch=='0': break

def env_list_claude():
    clear(); banner()
    divider("LIST ENV (CLAUDE ANALISIS)", C.CYAN)
    svc = input(c(C.WHITE,"\n  Nama service (contoh: gas-signal-service): ")).strip()
    if not svc: return

    svc_path = BASE_DIR/svc
    if not svc_path.exists():
        print(c(C.RED,f"  ❌ Folder {svc} tidak ditemukan")); pause(); return

    print(c(C.DIM,f"\n  Menganalisis ENV untuk {svc}..."))
    output,_ = run_claude(PROMPT_ENV(svc), svc_path)

    log_file = LOG_BASE/f"env-{svc}.txt"
    save_log(log_file, output, f"ENV LIST: {svc}")

    print(f"\n{c(C.WHITE,'  ENV yang dibutuhkan:')}\n")
    for line in output.split('\n'):
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts)>=4:
                name   = c(C.CYAN, parts[0])
                fungsi = parts[1][:30]
                contoh = c(C.DIM, parts[2][:25])
                wajib  = c(C.RED,"WAJIB") if "WAJIB" in parts[3] else c(C.DIM,"opsional")
                print(f"  {name:<35} {fungsi:<32} {contoh:<27} {wajib}")
        else:
            if line.strip(): print(f"  {c(C.DIM,line)}")
    print(f"\n  {c(C.DIM,f'Disimpan: {log_file}')}")
    pause()

def env_show_file():
    clear(); banner()
    divider("TAMPILKAN .env", C.CYAN)
    env_files = list(BASE_DIR.glob("*/.env"))
    if not env_files:
        print(c(C.YELLOW,"\n  Tidak ada .env file ditemukan.")); pause(); return

    for i,f in enumerate(env_files,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {f.parent.name}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")

    ch = input(c(C.WHITE,"  Pilih: ")).strip()
    try:
        idx = int(ch)-1
        if 0<=idx<len(env_files):
            content = env_files[idx].read_text()
            print(f"\n{c(C.WHITE,str(env_files[idx]))}")
            print(c(C.DIM,"─"*60))
            for line in content.split('\n'):
                if line.startswith('#'):  print(c(C.DIM,f"  {line}"))
                elif '=' in line:
                    k,_,v = line.partition('=')
                    masked = "****" if any(x in k.upper() for x in ['KEY','SECRET','PASS','TOKEN']) else v
                    print(f"  {c(C.CYAN,k)}={c(C.DIM,masked)}")
                else: print(f"  {line}")
    except ValueError: pass
    pause()

def env_edit():
    clear(); banner()
    divider("EDIT .env SERVICE", C.CYAN)
    env_files = list(BASE_DIR.glob("*/.env"))
    if not env_files:
        print(c(C.YELLOW,"\n  Tidak ada .env file. Buat dulu dari .env.example"))
        pause(); return

    for i,f in enumerate(env_files,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {f.parent.name}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")

    ch = input(c(C.WHITE,"  Pilih service: ")).strip()
    try:
        idx = int(ch)-1
        if 0<=idx<len(env_files):
            editor = os.environ.get("EDITOR","nano")
            subprocess.run([editor, str(env_files[idx])])
    except ValueError: pass

def env_validate():
    clear(); banner()
    divider("VALIDASI ENV", C.CYAN)
    print(c(C.DIM,"\n  Mengecek .env.example vs .env di semua service...\n"))

    results = []
    for svc_dir in sorted(BASE_DIR.iterdir()):
        if not svc_dir.is_dir() or not svc_dir.name.startswith("gas-"): continue
        example = svc_dir/".env.example"
        env     = svc_dir/".env"
        if not example.exists(): continue

        example_keys = set()
        for line in example.read_text().split('\n'):
            if '=' in line and not line.startswith('#'):
                example_keys.add(line.split('=')[0].strip())

        env_keys = set()
        if env.exists():
            for line in env.read_text().split('\n'):
                if '=' in line and not line.startswith('#'):
                    env_keys.add(line.split('=')[0].strip())

        missing = example_keys - env_keys
        results.append((svc_dir.name, missing, env.exists()))

    for svc,missing,has_env in results:
        if not has_env:
            print(f"  {c(C.RED,'❌')} {svc:<48} {c(C.RED,'no .env file')}")
        elif missing:
            print(f"  {c(C.YELLOW,'⚠️ ')} {svc:<48} {c(C.YELLOW,f'missing: {len(missing)} vars')}")
            for m in list(missing)[:3]: print(f"     {c(C.DIM,'→ '+m)}")
        else:
            print(f"  {c(C.GREEN,'✅')} {svc}")
    pause()

def env_status_all():
    clear(); banner()
    issues = load_json(ISSUES_FILE)
    missing = {s:v for s,v in issues.items() if v.get("env_missing")}
    divider("STATUS ENV DARI SCAN", C.CYAN)
    print()
    if not missing:
        print(c(C.GREEN,"  ✅ Tidak ada ENV missing dari hasil scan!"))
    else:
        for svc,data in missing.items():
            fixed  = data.get("env_fixed",False)
            status = c(C.GREEN,"✅ fixed") if fixed else c(C.YELLOW,"⚠️  belum")
            print(f"  {status} {c(C.CYAN,svc)}")
            for e in data.get("env_missing",[]):
                print(f"    {c(C.DIM,'→ '+e)}")
    pause()

def env_mark_fixed():
    clear(); banner()
    issues  = load_json(ISSUES_FILE)
    missing = [(s,v) for s,v in issues.items() if v.get("env_missing") and not v.get("env_fixed")]
    if not missing:
        print(c(C.GREEN,"\n  ✅ Semua ENV sudah di-fix!")); pause(); return

    divider("TANDAI ENV SUDAH FIX", C.CYAN)
    print()
    for i,(svc,_) in enumerate(missing,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {svc}")
    print(f"  {c(C.CYAN,'A.')} Tandai semua\n")

    ch = input(c(C.WHITE,"  Pilih: ")).strip().upper()
    if ch=='A':
        for svc,_ in missing: issues[svc]["env_fixed"]=True
        save_json(ISSUES_FILE,issues)
        print(c(C.GREEN,f"\n  ✅ Semua {len(missing)} service ditandai!"))
    else:
        try:
            idx=int(ch)-1
            if 0<=idx<len(missing):
                issues[missing[idx][0]]["env_fixed"]=True
                save_json(ISSUES_FILE,issues)
                print(c(C.GREEN,f"\n  ✅ {missing[idx][0]} ditandai!"))
        except ValueError: pass
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 5: TERMINAL UI
# ═══════════════════════════════════════════════════════════════
def menu_terminal_ui():
    while True:
        clear(); banner()
        divider("🖥️  TERMINAL UI & FRONTEND", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} 🔌 Test Semua Endpoint API
  {c(C.CYAN,'2.')} 🌐 Cek Koneksi Web Backend
  {c(C.CYAN,'3.')} 🤖 Claude Review Frontend (AI)
  {c(C.CYAN,'4.')} 📡 Test WebSocket Connection
  {c(C.CYAN,'5.')} 🔐 Test Auth Flow (Login/Token)
  {c(C.CYAN,'6.')} 🐛 Debug Terminal (BE + FE + Koneksi + Laporan)
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': ui_test_endpoints()
        elif ch=='2': ui_check_web()
        elif ch=='3': ui_claude_review()
        elif ch=='4': ui_test_websocket()
        elif ch=='5': ui_test_auth()
        elif ch=='6': menu_debug_terminal()
        elif ch=='0': break

def ui_test_endpoints():
    clear(); banner()
    divider("TEST SEMUA ENDPOINT", C.CYAN)
    print(c(C.DIM,"\n  Ping semua port service GAS...\n"))

    ok=err=0
    for svc,cat in ALL_SERVICES:
        port = PORTS.get(svc)
        if not port: continue
        icon = ICONS.get(cat,"📦")
        print(f"  {icon} {c(C.CYAN,svc):<46} :{port} ",end="",flush=True)
        if ping_port("localhost",port):
            print(c(C.GREEN,"● online")); ok+=1
        else:
            print(c(C.RED,"○ offline")); err+=1

    print(f"\n  {c(C.GREEN,f'✅ Online: {ok}')}  {c(C.RED,f'❌ Offline: {err}')}")
    pause()

def ui_check_web():
    clear(); banner()
    divider("CEK WEB BACKEND", C.CYAN)
    endpoints = [
        ("gas-web-backend",   "http://localhost:8005/health"),
        ("gas-gateway-api",   "http://localhost:8000/health"),
        ("gas-terminal-backend","http://localhost:8085/health"),
    ]
    print()
    for name,url in endpoints:
        print(f"  {c(C.CYAN,name)}")
        print(f"  {c(C.DIM,'→ '+url)} ",end="",flush=True)
        try:
            req  = urllib.request.Request(url,headers={"User-Agent":"gas-tools"})
            resp = urllib.request.urlopen(req,timeout=3)
            print(c(C.GREEN,f" ✅ {resp.status}"))
        except urllib.error.HTTPError as e:
            print(c(C.YELLOW,f" ⚠️  HTTP {e.code}"))
        except Exception as e:
            print(c(C.RED,f" ❌ {str(e)[:50]}"))
    pause()

def ui_claude_review():
    clear(); banner()
    divider("CLAUDE REVIEW FRONTEND", C.CYAN)
    frontend_services = ["gas-terminal-frontend","gas-web-backend","gas-terminal-backend"]
    for i,svc in enumerate(frontend_services,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {svc}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")

    ch = input(c(C.WHITE,"  Pilih service frontend: ")).strip()
    try:
        idx=int(ch)-1
        if 0<=idx<len(frontend_services):
            svc      = frontend_services[idx]
            svc_path = BASE_DIR/svc
            if not svc_path.exists():
                print(c(C.RED,f"  ❌ Folder {svc} tidak ditemukan")); pause(); return
            print(c(C.DIM,f"\n  Claude mereview {svc}..."))
            output,_ = run_claude(PROMPT_REVIEW_FRONTEND(svc), svc_path)
            log_file  = LOG_BASE/f"ui-review-{svc}.txt"
            save_log(log_file, output, f"UI REVIEW: {svc}")
            print(f"\n{c(C.WHITE,'  Hasil Review:')}\n")
            for line in output.split('\n'): print(f"  {line}")
    except ValueError: pass
    pause()

def ui_test_websocket():
    clear(); banner()
    divider("TEST WEBSOCKET", C.CYAN)
    print(f"\n  WebSocket endpoints:\n")
    ws_services = [("gas-realtime-hub",8111),("gas-mt5-websocket",8110)]
    for svc,port in ws_services:
        print(f"  {c(C.CYAN,svc):<46} :{port} ",end="",flush=True)
        if ping_port("localhost",port):
            print(c(C.GREEN,"● port open"))
        else:
            print(c(C.RED,"○ port closed"))
    print(c(C.DIM,"\n  Note: Port open ≠ WS handshake sukses."))
    print(c(C.DIM,"  Untuk full WS test, gunakan wscat atau Postman."))
    pause()

def ui_test_auth():
    clear(); banner()
    divider("TEST AUTH FLOW", C.CYAN)
    print(c(C.DIM,"\n  Test koneksi ke gas-auth-service:8001\n"))
    auth_port = PORTS.get("gas-auth-service",8001)

    if ping_port("localhost",auth_port):
        print(c(C.GREEN,f"  ✅ Auth service online di port {auth_port}"))
        print(c(C.DIM,"  Endpoint tersedia:"))
        endpoints = ["/health","/api/v1/auth/login","/api/v1/auth/register","/api/v1/auth/refresh"]
        for ep in endpoints:
            url = f"http://localhost:{auth_port}{ep}"
            try:
                req  = urllib.request.Request(url,headers={"User-Agent":"gas-tools"})
                resp = urllib.request.urlopen(req,timeout=2)
                print(f"  {c(C.GREEN,'✅')} {ep}")
            except urllib.error.HTTPError as e:
                print(f"  {c(C.YELLOW,'⚠️ ')} {ep} → HTTP {e.code}")
            except:
                print(f"  {c(C.DIM,'○')} {ep} → tidak respond")
    else:
        print(c(C.RED,f"  ❌ Auth service tidak online di port {auth_port}"))
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 5.6: DEBUG TERMINAL (BE + FE + KONEKSI)
# ═══════════════════════════════════════════════════════════════

# Service dependencies dari gas-terminal-backend
TERMINAL_DEPS = [
    ("gas-chart-service",    9700, "Charts/OHLCV data"),
    ("gas-signal-service",   8106, "Trading signals"),
    ("gas-mt5-data-service", 8100, "MT5 market data"),
    ("gas-mt5-websocket",    8110, "MT5 realtime WS"),
    ("gas-gateway-api",      8000, "API Gateway"),
    ("gas-auth-service",     8001, "Auth/JWT"),
    ("gas-redis",            6379, "Cache/session"),
    ("gas-realtime-hub",     8111, "Realtime events"),
    ("gas-indicator-engine", 8203, "Indicators"),
]

# Endpoint BE terminal yang diuji
TERMINAL_BE_ENDPOINTS = [
    ("GET",  "/health",                   "Health check"),
    ("GET",  "/api/v1/overview",          "Overview data"),
    ("GET",  "/api/v1/chart",             "Chart data"),
    ("GET",  "/api/v1/signals",           "Signals"),
    ("GET",  "/api/v1/markets",           "Markets data"),
    ("GET",  "/terminal",                 "Terminal route"),
]

DEBUG_REPORT_FILE = Path.home() / "gas-reports" / "debug-terminal-latest.txt"

def menu_debug_terminal():
    while True:
        clear(); banner()
        divider("🐛 DEBUG TERMINAL (BE + FE + KONEKSI)", C.MAGENTA)

        be_ok   = ping_port("localhost", 8085)
        fe_path = BASE_DIR / "gas-terminal-frontend"
        be_path = BASE_DIR / "gas-terminal-backend"
        be_s = c(C.GREEN, "● :8085") if be_ok else c(C.RED, "○ :8085")
        fe_s = c(C.GREEN, "✓ ada") if fe_path.exists() else c(C.RED, "✗ tidak ada")

        print(f"""
  Status:  BE {be_s}   FE folder {fe_s}

  {c(C.CYAN,'1.')} 🔌 Test Endpoint BE Terminal     — Ping semua route gas-terminal-backend
  {c(C.CYAN,'2.')} 🌐 Cek Koneksi Terminal → GAS    — Semua service yg dipakai terminal
  {c(C.CYAN,'3.')} 📁 Cek FE Terminal               — .env, constants, build status
  {c(C.CYAN,'4.')} 🤖 Claude Debug BE Terminal      — AI analisis kode BE + fix
  {c(C.CYAN,'5.')} 🤖 Claude Debug FE Terminal      — AI analisis kode FE + fix
  {c(C.CYAN,'6.')} 📋 Laporan Debug Lengkap         — Generate & simpan laporan
  {c(C.CYAN,'7.')} 🔴 Lihat Error Log Terminal      — docker logs gas-terminal-backend
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': debug_test_be_endpoints()
        elif ch=='2': debug_check_connections()
        elif ch=='3': debug_check_fe()
        elif ch=='4': debug_claude_be()
        elif ch=='5': debug_claude_fe()
        elif ch=='6': debug_report_terminal()
        elif ch=='7': debug_show_be_logs()
        elif ch=='0': break


def debug_test_be_endpoints():
    clear(); banner()
    divider("TEST ENDPOINT BE TERMINAL (:8085)", C.MAGENTA)
    be_port = 8085

    if not ping_port("localhost", be_port):
        print(c(C.RED, f"\n  ❌ gas-terminal-backend TIDAK running di port {be_port}"))
        print(c(C.DIM,  "  Jalankan: docker start gas-terminal-backend"))
        pause(); return

    print(f"\n  BE online di :{be_port}. Mengetes semua endpoint...\n")
    results = []

    for method, path, desc in TERMINAL_BE_ENDPOINTS:
        url = f"http://localhost:{be_port}{path}"
        print(f"  {method:<4} {c(C.CYAN, path):<40} {c(C.DIM, desc):<30} ",end="",flush=True)
        try:
            req  = urllib.request.Request(url, headers={"User-Agent":"gas-tools"}, method=method)
            resp = urllib.request.urlopen(req, timeout=3)
            body = resp.read(200).decode(errors='replace')
            print(c(C.GREEN, f"✅ {resp.status}"))
            results.append((path, resp.status, "OK", ""))
        except urllib.error.HTTPError as e:
            body = e.read(200).decode(errors='replace') if hasattr(e,'read') else ""
            color = C.YELLOW if e.code < 500 else C.RED
            print(c(color, f"⚠️  HTTP {e.code}"))
            results.append((path, e.code, "HTTP_ERROR", body[:80]))
        except Exception as e:
            print(c(C.RED, f"❌ {str(e)[:50]}"))
            results.append((path, 0, "CONN_ERROR", str(e)[:80]))

    ok   = sum(1 for _,code,s,_ in results if s=="OK")
    warn = sum(1 for _,code,s,_ in results if s=="HTTP_ERROR")
    err  = sum(1 for _,code,s,_ in results if s=="CONN_ERROR")

    print(f"\n  {c(C.GREEN,f'✅ OK: {ok}')}  {c(C.YELLOW,f'⚠️  HTTP err: {warn}')}  {c(C.RED,f'❌ Conn err: {err}')}")

    # Simpan ke file untuk laporan
    _save_debug_partial("be_endpoints", results)
    pause()


def debug_check_connections():
    clear(); banner()
    divider("KONEKSI TERMINAL → GAS SERVICES", C.MAGENTA)
    print(c(C.DIM, "\n  Mengecek semua service yang dibutuhkan gas-terminal-backend...\n"))

    running = get_running()
    results = []

    for svc, port, desc in TERMINAL_DEPS:
        is_running = svc in running
        port_ok    = ping_port("localhost", port)
        icon       = "✅" if (is_running and port_ok) else ("⚠️ " if is_running else "❌")

        run_s = c(C.GREEN,"running") if is_running else c(C.RED,"stopped")
        port_s = c(C.GREEN,f":{port} ✓") if port_ok else c(C.RED,f":{port} ✗")

        print(f"  {icon} {c(C.CYAN,svc):<46} {run_s}  {port_s}  {c(C.DIM,desc)}")

        status = "OK" if (is_running and port_ok) else ("STOPPED" if not is_running else "PORT_FAIL")
        results.append((svc, port, status, desc))

    ok   = sum(1 for _,_,s,_ in results if s=="OK")
    bad  = len(results) - ok
    print(f"\n  {c(C.GREEN,f'✅ Terhubung: {ok}')}  {c(C.RED,f'❌ Bermasalah: {bad}')}")

    if bad:
        print(c(C.YELLOW, "\n  Service bermasalah akan menyebabkan fitur terminal tidak berfungsi!"))
        print(c(C.DIM,    "  Fix: Deploy & Restart → Start Service\n"))

    _save_debug_partial("connections", results)
    pause()


def debug_check_fe():
    clear(); banner()
    divider("CEK FE TERMINAL (gas-terminal-frontend)", C.MAGENTA)
    fe_path = BASE_DIR / "gas-terminal-frontend"

    if not fe_path.exists():
        print(c(C.RED, "\n  ❌ Folder gas-terminal-frontend tidak ditemukan!")); pause(); return

    print()
    results = []

    # Cek file-file penting
    important_files = [
        (".env",                      "Konfigurasi environment"),
        ("src/constants.js",          "URL/port constants"),
        ("src/services/api.js",       "API client"),
        ("src/App.jsx",               "App utama"),
        ("src/components/MarketsView.jsx",   "MarketsView component"),
        ("src/components/SignalView.jsx",     "SignalView component"),
        ("src/components/TradingViewChart.jsx","TradingView Chart"),
        ("package.json",              "Dependencies"),
        ("node_modules",              "Installed packages"),
        ("dist",                      "Build output"),
    ]

    divider("File & Folder", C.DIM)
    for fname, desc in important_files:
        fpath  = fe_path / fname
        exists = fpath.exists()
        icon   = c(C.GREEN,"✅") if exists else c(C.RED,"❌")
        print(f"  {icon} {fname:<45} {c(C.DIM,desc)}")
        results.append(("file", fname, "OK" if exists else "MISSING", desc))

    # Cek .env dan VITE vars
    print(); divider("ENV Variables", C.DIM)
    env_file = fe_path / ".env"
    if env_file.exists():
        env_content = env_file.read_text()
        vite_vars = [(line.split('=')[0].strip(), line.split('=',1)[1].strip() if '=' in line else "")
                     for line in env_content.split('\n')
                     if line.strip() and not line.startswith('#') and '=' in line]
        for key, val in vite_vars:
            masked = val if 'URL' in key or 'HOST' in key or 'PORT' in key else ("****" if val else "(kosong)")
            ok_s = c(C.GREEN,"✅") if val else c(C.RED,"❌ kosong!")
            print(f"  {ok_s} {c(C.CYAN,key):<40} = {c(C.DIM,masked)}")
            results.append(("env", key, "OK" if val else "EMPTY", val))

        # Cek apakah VITE_API_URL pointing ke BE
        api_url_line = [v for k,v in vite_vars if 'API' in k and 'URL' in k]
        if api_url_line:
            url = api_url_line[0]
            be_port_in_url = "8085" in url
            print(f"\n  {c(C.GREEN,'✅') if be_port_in_url else c(C.YELLOW,'⚠️ ')} "
                  f"API URL pointing ke BE:8085 → {'Ya' if be_port_in_url else 'Cek! port 8085 tidak ditemukan di URL'}")
    else:
        print(c(C.RED, "  ❌ .env tidak ada! FE tidak tahu alamat BE."))
        results.append(("env", ".env", "MISSING", ""))

    # Cek constants.js untuk URL hardcoded
    print(); divider("Constants.js check", C.DIM)
    const_file = fe_path / "src" / "constants.js"
    if const_file.exists():
        content = const_file.read_text()
        for line in content.split('\n'):
            if any(x in line for x in ['localhost','http','ws://']):
                print(f"  {c(C.YELLOW,'⚠️ ')} {c(C.DIM, line.strip()[:80])}")
    else:
        print(c(C.DIM,"  constants.js tidak ditemukan"))

    _save_debug_partial("fe_check", results)
    pause()


def debug_claude_be():
    clear(); banner()
    divider("CLAUDE DEBUG BE TERMINAL", C.MAGENTA)
    be_path = BASE_DIR / "gas-terminal-backend"
    if not be_path.exists():
        print(c(C.RED,"\n  ❌ Folder gas-terminal-backend tidak ditemukan!")); pause(); return

    print(c(C.DIM,"\n  Claude sedang menganalisis kode gas-terminal-backend..."))
    print(c(C.DIM,"  (ini bisa 2-3 menit)\n"))

    output, ok = run_claude(PROMPT_DEBUG_TERMINAL_BE, be_path)
    ts        = datetime.now().strftime("%Y%m%d-%H%M")
    log_file  = LOG_BASE / f"debug-terminal-be-{ts}.txt"
    save_log(log_file, output, "DEBUG BE TERMINAL: gas-terminal-backend")

    print(f"\n{c(C.WHITE,'  Hasil Analisis Claude:')}\n")
    for line in output.split('\n'):
        if 'CRITICAL' in line.upper(): print(f"  {c(C.RED, line)}")
        elif 'WARNING'  in line.upper(): print(f"  {c(C.YELLOW, line)}")
        elif '|' in line:               print(f"  {c(C.CYAN, line)}")
        else:                            print(f"  {c(C.DIM, line)}")

    print(f"\n  {c(C.DIM,f'Disimpan: {log_file}')}")
    _save_debug_partial("claude_be", output)
    pause()


def debug_claude_fe():
    clear(); banner()
    divider("CLAUDE DEBUG FE TERMINAL", C.MAGENTA)
    fe_path = BASE_DIR / "gas-terminal-frontend"
    if not fe_path.exists():
        print(c(C.RED,"\n  ❌ Folder gas-terminal-frontend tidak ditemukan!")); pause(); return

    print(c(C.DIM,"\n  Claude sedang menganalisis kode gas-terminal-frontend..."))
    print(c(C.DIM,"  (ini bisa 2-3 menit)\n"))

    output, ok = run_claude(PROMPT_DEBUG_TERMINAL_FE, fe_path)
    ts        = datetime.now().strftime("%Y%m%d-%H%M")
    log_file  = LOG_BASE / f"debug-terminal-fe-{ts}.txt"
    save_log(log_file, output, "DEBUG FE TERMINAL: gas-terminal-frontend")

    print(f"\n{c(C.WHITE,'  Hasil Analisis Claude:')}\n")
    for line in output.split('\n'):
        if 'CRITICAL' in line.upper(): print(f"  {c(C.RED, line)}")
        elif 'WARNING'  in line.upper(): print(f"  {c(C.YELLOW, line)}")
        elif '|' in line:               print(f"  {c(C.CYAN, line)}")
        else:                            print(f"  {c(C.DIM, line)}")

    print(f"\n  {c(C.DIM,f'Disimpan: {log_file}')}")
    _save_debug_partial("claude_fe", output)
    pause()


def debug_show_be_logs():
    clear(); banner()
    divider("ERROR LOG — gas-terminal-backend", C.MAGENTA)
    running = get_running()
    if "gas-terminal-backend" not in running:
        print(c(C.RED, "\n  ❌ gas-terminal-backend tidak running!"))
        print(c(C.DIM, "  Cek: docker ps -a | grep gas-terminal-backend")); pause(); return

    lines = input(c(C.DIM, "  Berapa baris terakhir? (default 100): ")).strip() or "100"
    stdout,_,_ = run_cmd(f"docker logs --tail {lines} gas-terminal-backend")

    errors = [l for l in stdout.split('\n') if any(x in l.lower() for x in ['error','exception','traceback','critical','failed'])]

    print(f"\n  Total log: {stdout.count(chr(10))} baris | {c(C.RED,f'Error/Exception: {len(errors)}')}\n")
    divider("Error lines", C.RED)
    if errors:
        for line in errors[:30]:
            print(f"  {c(C.RED,'→')} {c(C.DIM, line[:120])}")
        if len(errors) > 30:
            print(c(C.DIM, f"  ... ({len(errors)-30} error lainnya)"))
    else:
        print(c(C.GREEN, "  ✅ Tidak ada error/exception di log!"))

    print(); divider("Full log (50 baris terakhir)", C.DIM)
    for line in stdout.split('\n')[-50:]:
        print(f"  {c(C.DIM, line[:120])}")

    pause()


def _save_debug_partial(key, data):
    """Simpan hasil debug partial ke file sementara untuk laporan."""
    tmp_dir = Path.home() / ".gas-debug-tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    save_json(tmp_dir / f"{key}.json", {"data": data if isinstance(data, list) else str(data),
                                         "time": datetime.now().isoformat()})


def debug_report_terminal():
    clear(); banner()
    divider("LAPORAN DEBUG TERMINAL LENGKAP", C.MAGENTA)
    print(c(C.DIM, "\n  Mengumpulkan semua data debug terminal...\n"))

    ts       = datetime.now().strftime("%Y%m%d-%H%M%S")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    report_f = REPORT_DIR / f"debug-terminal-{ts}.txt"
    running  = get_running()
    lines    = []

    lines.append("=" * 70)
    lines.append("  GAS TERMINAL DEBUG REPORT")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("=" * 70)

    # 1. Status BE & FE
    lines.append("\n── STATUS TERMINAL SERVICES ──────────────────────────────────────────")
    be_running = "gas-terminal-backend"  in running
    fe_path    = BASE_DIR / "gas-terminal-frontend"
    be_port_ok = ping_port("localhost", 8085)

    lines.append(f"  gas-terminal-backend  : {'● UP' if be_running else '○ DOWN'}"
                 f"  port 8085: {'✓' if be_port_ok else '✗'}")
    lines.append(f"  gas-terminal-frontend : folder {'ada' if fe_path.exists() else 'TIDAK ADA'}")

    # 2. Test endpoints BE
    lines.append("\n── ENDPOINT TEST (BE :8085) ──────────────────────────────────────────")
    if be_port_ok:
        for method, path, desc in TERMINAL_BE_ENDPOINTS:
            url = f"http://localhost:8085{path}"
            try:
                req  = urllib.request.Request(url, headers={"User-Agent":"gas-tools"}, method=method)
                resp = urllib.request.urlopen(req, timeout=3)
                lines.append(f"  ✅ {method} {path:<40} {resp.status}")
            except urllib.error.HTTPError as e:
                lines.append(f"  ⚠️  {method} {path:<40} HTTP {e.code}")
            except Exception as e:
                lines.append(f"  ❌ {method} {path:<40} {str(e)[:50]}")
    else:
        lines.append("  ❌ BE tidak online — skip endpoint test")

    # 3. Koneksi ke GAS services
    lines.append("\n── KONEKSI TERMINAL → GAS SERVICES ──────────────────────────────────")
    for svc, port, desc in TERMINAL_DEPS:
        is_running = svc in running
        port_ok    = ping_port("localhost", port)
        status     = "✅ OK" if (is_running and port_ok) else ("⚠️  running tapi port ✗" if is_running else "❌ STOPPED")
        lines.append(f"  {status:<22} {svc:<46} :{port}  {desc}")

    # 4. FE ENV check
    lines.append("\n── FE ENV CHECK (.env) ───────────────────────────────────────────────")
    env_file = fe_path / ".env" if fe_path.exists() else None
    if env_file and env_file.exists():
        for line in env_file.read_text().split('\n'):
            if line.strip() and not line.startswith('#') and '=' in line:
                k,_,v = line.partition('=')
                lines.append(f"  {k.strip()} = {v.strip()[:60] if 'URL' in k or 'PORT' in k or 'HOST' in k else '****'}")
    else:
        lines.append("  ❌ .env tidak ditemukan di gas-terminal-frontend!")

    # 5. Error log dari BE
    lines.append("\n── RECENT ERRORS (gas-terminal-backend logs) ────────────────────────")
    if be_running:
        stdout,_,_ = run_cmd("docker logs --tail 50 gas-terminal-backend")
        errors = [l for l in stdout.split('\n')
                  if any(x in l.lower() for x in ['error','exception','traceback','critical'])]
        if errors:
            for e in errors[:20]:
                lines.append(f"  → {e[:110]}")
        else:
            lines.append("  ✅ Tidak ada error di 50 baris terakhir log BE")
    else:
        lines.append("  ⏭️  Skip — BE tidak running")

    # 6. Summary & rekomendasi
    lines.append("\n── SUMMARY & REKOMENDASI ─────────────────────────────────────────────")
    dep_ok  = sum(1 for svc,port,_ in TERMINAL_DEPS if svc in running and ping_port("localhost",port))
    dep_bad = len(TERMINAL_DEPS) - dep_ok

    lines.append(f"  Dependency services OK : {dep_ok}/{len(TERMINAL_DEPS)}")
    lines.append(f"  BE Terminal status     : {'✅ UP' if be_running else '❌ DOWN'}")
    lines.append(f"  FE folder exists       : {'✅' if fe_path.exists() else '❌'}")
    lines.append(f"  FE .env ada            : {'✅' if (env_file and env_file.exists()) else '❌'}")

    if not be_running:
        lines.append("\n  ⚡ AKSI: docker start gas-terminal-backend")
    if dep_bad > 0:
        lines.append(f"\n  ⚡ {dep_bad} dependency service tidak running.")
        lines.append("     → Pakai menu: Deploy & Restart → Start Service")
    if not (env_file and env_file.exists()):
        lines.append("\n  ⚡ Buat .env di gas-terminal-frontend:")
        lines.append("     cp gas-terminal-frontend/.env.example gas-terminal-frontend/.env")
        lines.append("     Edit VITE_API_URL=http://YOUR_IP:8085")

    lines.append("\n" + "=" * 70)
    lines.append(f"  End of Debug Report — {ts}")
    lines.append("=" * 70)

    content = "\n".join(lines)
    with open(report_f, 'w') as f: f.write(content)

    # Print ke layar
    for line in lines:
        if "❌" in line:  print(f"  {c(C.RED, line.strip())}")
        elif "⚠️" in line: print(f"  {c(C.YELLOW, line.strip())}")
        elif "✅" in line: print(f"  {c(C.GREEN, line.strip())}")
        elif line.startswith("──"): print(c(C.CYAN, line))
        elif line.startswith("="): print(c(C.BLUE, line))
        else:              print(f"  {c(C.DIM, line.strip())}")

    print(f"\n  {c(C.GREEN,f'✅ Laporan disimpan: {report_f}')}")
    pause()


# ═══════════════════════════════════════════════════════════════
#  MENU 6: GRAFANA & OBSERVABILITY
# ═══════════════════════════════════════════════════════════════
def menu_grafana():
    while True:
        clear(); banner()
        divider("📈 GRAFANA & OBSERVABILITY", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} ❤️  Cek Status Stack Observability
  {c(C.CYAN,'2.')} 🌐 URL & Akses Grafana / Prometheus / Loki
  {c(C.CYAN,'3.')} 📚 Panduan Grafana (Claude jelaskan)
  {c(C.CYAN,'4.')} 🔍 Query Prometheus Berguna
  {c(C.CYAN,'5.')} 📋 Cara Baca Loki Logs
  {c(C.CYAN,'6.')} 🚨 Setup Alert Dasar
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': grafana_status()
        elif ch=='2': grafana_urls()
        elif ch=='3': grafana_guide_claude()
        elif ch=='4': grafana_prometheus_queries()
        elif ch=='5': grafana_loki_guide()
        elif ch=='6': grafana_alert_guide()
        elif ch=='0': break

def grafana_status():
    clear(); banner()
    divider("STATUS OBSERVABILITY STACK", C.CYAN)
    services = [
        ("Grafana",    "gas-grafana",    3000, "http://localhost:3000"),
        ("Prometheus", "gas-prometheus", 9090, "http://localhost:9090"),
        ("Loki",       "gas-loki",       3100, "http://localhost:3100"),
        ("Promtail",   "gas-promtail",   None,  None),
        ("MinIO",      "gas-minio",      9000, "http://localhost:9000"),
    ]
    running = get_running()
    print()
    for name,container,port,url in services:
        is_running = container in running
        port_ok    = ping_port("localhost",port) if port else None

        status = c(C.GREEN,"● running") if is_running else c(C.RED,"○ stopped")
        port_s = ""
        if port:
            port_s = c(C.GREEN,f" | :{port} ✓") if port_ok else c(C.RED,f" | :{port} ✗")

        print(f"  {c(C.WHITE,name):<14} {status}{port_s}")
        if url and is_running: print(f"  {c(C.DIM,'  → '+url)}")
    pause()

def grafana_urls():
    clear(); banner()
    divider("URL & AKSES", C.CYAN)
    print(f"""
  {c(C.WHITE,'Grafana Dashboard:')}
  {c(C.CYAN,'→')} http://YOUR_VPS_IP:3000
  {c(C.DIM,'   Default login: admin / admin')}
  {c(C.DIM,'   Ganti password setelah login pertama!')}

  {c(C.WHITE,'Prometheus:')}
  {c(C.CYAN,'→')} http://YOUR_VPS_IP:9090
  {c(C.DIM,'   Bisa query metric langsung di sini')}

  {c(C.WHITE,'Loki (via Grafana):')}
  {c(C.CYAN,'→')} Buka Grafana → Explore → pilih Loki datasource

  {c(C.WHITE,'MinIO (Object Storage):')}
  {c(C.CYAN,'→')} http://YOUR_VPS_IP:9010
  {c(C.DIM,'   Untuk lihat data Parquet / dataset')}

  {c(C.YELLOW,'⚠️  Pastikan port di firewall GCP sudah dibuka:')}
  {c(C.DIM,'   gcloud compute firewall-rules create allow-monitoring')}
  {c(C.DIM,'   --allow tcp:3000,tcp:9090,tcp:9010 --source-ranges=YOUR_IP/32')}
""")
    pause()

def grafana_guide_claude():
    clear(); banner()
    divider("PANDUAN GRAFANA (CLAUDE)", C.CYAN)
    print(c(C.DIM,"\n  Claude sedang membuat panduan Grafana...\n"))

    # Gunakan BASE_DIR sebagai cwd (tidak perlu service spesifik)
    output,_ = run_claude(PROMPT_GRAFANA_EXPLAIN, BASE_DIR)
    log_file  = LOG_BASE/"grafana-guide.txt"
    save_log(log_file, output, "PANDUAN GRAFANA")

    print(f"\n{c(C.WHITE,'  Panduan Grafana:')}\n")
    for line in output.split('\n'): print(f"  {line}")
    print(f"\n  {c(C.DIM,f'Disimpan: {log_file}')}")
    pause()

def grafana_prometheus_queries():
    clear(); banner()
    divider("QUERY PROMETHEUS BERGUNA", C.CYAN)
    queries = [
        ("CPU Usage Container",     'sum(rate(container_cpu_usage_seconds_total{name=~"gas-.*"}[5m])) by (name)'),
        ("Memory Usage",            'container_memory_usage_bytes{name=~"gas-.*"}'),
        ("HTTP Request Rate",       'sum(rate(http_requests_total[5m])) by (job)'),
        ("HTTP Error Rate (5xx)",   'sum(rate(http_requests_total{status=~"5.."}[5m])) by (job)'),
        ("Request Duration P99",    'histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))'),
        ("Container Restarts",      'increase(kube_pod_container_status_restarts_total[1h])'),
        ("Up/Down Services",        'up{job=~"gas-.*"}'),
        ("Redis Connected Clients", 'redis_connected_clients'),
    ]
    print()
    for name,query in queries:
        print(f"  {c(C.WHITE,name)}")
        print(f"  {c(C.CYAN,query)}")
        print()
    print(c(C.DIM,"  Copy query di atas ke Prometheus → http://localhost:9090"))
    pause()

def grafana_loki_guide():
    clear(); banner()
    divider("CARA BACA LOKI LOGS", C.CYAN)
    print(f"""
  {c(C.WHITE,'Loki Query Language (LogQL):')}

  {c(C.CYAN,'1. Lihat log semua container GAS:')}
  {c(C.DIM,'   {container_name=~"gas-.*"}')}

  {c(C.CYAN,'2. Filter log ERROR dari service tertentu:')}
  {c(C.DIM,'   {container_name="gas-signal-service"} |= "ERROR"')}

  {c(C.CYAN,'3. Cari exception di semua service:')}
  {c(C.DIM,'   {container_name=~"gas-.*"} |= "Exception" or "Traceback"')}

  {c(C.CYAN,'4. Log dalam 5 menit terakhir:')}
  {c(C.DIM,'   {container_name=~"gas-.*"}[5m]')}

  {c(C.CYAN,'5. Count error per service per menit:')}
  {c(C.DIM,'   sum by (container_name) (rate({container_name=~"gas-.*"} |= "ERROR" [1m]))')}

  {c(C.WHITE,'Cara akses di Grafana:')}
  {c(C.DIM,'  Grafana → Explore → Pilih Loki datasource → Paste query')}
""")
    pause()

def grafana_alert_guide():
    clear(); banner()
    divider("SETUP ALERT DASAR", C.CYAN)
    print(f"""
  {c(C.WHITE,'Alert yang WAJIB dibuat untuk GAS:')}

  {c(C.RED,'🔴 CRITICAL alerts:')}
  {c(C.DIM,'  • Service down > 1 menit')}
  {c(C.DIM,'  • Error rate > 10% dalam 5 menit')}
  {c(C.DIM,'  • RAM usage > 90%')}
  {c(C.DIM,'  • Disk usage > 85%')}

  {c(C.YELLOW,'🟡 WARNING alerts:')}
  {c(C.DIM,'  • CPU usage > 80% selama 10 menit')}
  {c(C.DIM,'  • Response time P99 > 3 detik')}
  {c(C.DIM,'  • Container restart > 3x dalam 1 jam')}

  {c(C.WHITE,'Cara buat alert di Grafana:')}
  {c(C.DIM,'  1. Buka dashboard → Edit panel')}
  {c(C.DIM,'  2. Tab "Alert" → Create alert rule')}
  {c(C.DIM,'  3. Set condition & threshold')}
  {c(C.DIM,'  4. Notification channel → Telegram (pakai bot token GAS)')}

  {c(C.WHITE,'Kirim alert ke Telegram Bot GAS lo:')}
  {c(C.DIM,'  Grafana → Alerting → Contact points → Add Telegram')}
  {c(C.DIM,'  Bot token: (sama dengan gas-telegram-bot ENV)')}
""")
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 7: DOCKER MANAGER
# ═══════════════════════════════════════════════════════════════
def menu_docker():
    while True:
        clear(); banner()
        divider("🐳 DOCKER MANAGER", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} 📋 docker ps (semua container)
  {c(C.CYAN,'2.')} 💾 docker stats (CPU & RAM realtime)
  {c(C.CYAN,'3.')} 🔍 Inspect Container
  {c(C.CYAN,'4.')} 🧹 Docker Prune (bersihkan unused)
  {c(C.CYAN,'5.')} 🖼️  List Semua Image GAS
  {c(C.CYAN,'6.')} 📦 List Volumes
  {c(C.CYAN,'7.')} 🌐 List Networks
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': docker_ps()
        elif ch=='2': docker_stats()
        elif ch=='3': docker_inspect()
        elif ch=='4': docker_prune()
        elif ch=='5': docker_images()
        elif ch=='6': docker_volumes()
        elif ch=='7': docker_networks()
        elif ch=='0': break

def docker_ps():
    clear(); banner()
    stdout,_,_ = run_cmd("docker ps -a --format 'table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}'")
    gas = [l for l in stdout.split('\n') if 'gas-' in l or 'CONTAINER' in l]
    print()
    for line in gas:
        if "Up" in line: print(f"  {c(C.GREEN,line)}")
        elif "Exited" in line: print(f"  {c(C.RED,line)}")
        else: print(f"  {c(C.DIM,line)}")
    pause()

def docker_stats():
    clear(); banner()
    divider("DOCKER STATS REALTIME", C.CYAN)
    print(c(C.DIM,"  Tekan Ctrl+C untuk berhenti\n"))
    time.sleep(1)
    try: subprocess.run("docker stats $(docker ps --filter name=gas- -q)",shell=True)
    except KeyboardInterrupt: pass
    pause()

def docker_inspect():
    clear(); banner()
    divider("INSPECT CONTAINER", C.CYAN)
    running = get_running()
    gas_svc = sorted([s for s in running if s.startswith("gas-")])
    for i,svc in enumerate(gas_svc,1):
        print(f"  {c(C.CYAN,str(i)+'.')} {svc}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")
    ch = input(c(C.WHITE,"  Pilih: ")).strip()
    try:
        idx=int(ch)-1
        if 0<=idx<len(gas_svc):
            stdout,_,_ = run_cmd(f"docker inspect {gas_svc[idx]}")
            data = json.loads(stdout)[0] if stdout else {}
            print(f"\n  {c(C.WHITE,'Container:')} {data.get('Name','')}")
            print(f"  {c(C.WHITE,'Image:')}     {data.get('Config',{}).get('Image','')}")
            print(f"  {c(C.WHITE,'Status:')}    {data.get('State',{}).get('Status','')}")
            print(f"  {c(C.WHITE,'Started:')}   {data.get('State',{}).get('StartedAt','')[:19]}")
            mounts = data.get('Mounts',[])
            if mounts:
                print(f"  {c(C.WHITE,'Mounts:')}")
                for m in mounts[:3]: print(f"    {c(C.DIM,m.get('Source',''))} → {m.get('Destination','')}")
    except (ValueError,json.JSONDecodeError): pass
    pause()

def docker_prune():
    clear(); banner()
    divider("DOCKER PRUNE", C.YELLOW)
    print(f"""
  {c(C.YELLOW,'Pilih apa yang mau dibersihkan:')}

  {c(C.CYAN,'1.')} 🧹 Prune stopped containers
  {c(C.CYAN,'2.')} 🖼️  Prune unused images
  {c(C.CYAN,'3.')} 📦 Prune unused volumes
  {c(C.CYAN,'4.')} 🌐 Prune unused networks
  {c(C.CYAN,'5.')} ☢️  Prune SEMUA (system prune)
  {c(C.CYAN,'0.')} ← Batal
""")
    ch = input(c(C.WHITE,"  Pilih: ")).strip()
    cmds = {
        '1': "docker container prune -f",
        '2': "docker image prune -f",
        '3': "docker volume prune -f",
        '4': "docker network prune -f",
        '5': "docker system prune -f",
    }
    if ch in cmds:
        if ch=='5' and input(c(C.RED,"  ⚠️  Yakin system prune? (YES): ")).strip()!="YES": return
        stdout,stderr,code = run_cmd(cmds[ch])
        print(c(C.GREEN if code==0 else C.RED, f"\n  {'✅ '+stdout[:200] if code==0 else '❌ '+stderr[:200]}"))
    pause()

def docker_images():
    clear(); banner()
    stdout,_,_ = run_cmd("docker images --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}'")
    gas = [l for l in stdout.split('\n') if 'gas-' in l or 'REPOSITORY' in l]
    print()
    for line in gas: print(f"  {line}")
    pause()

def docker_volumes():
    clear(); banner()
    stdout,_,_ = run_cmd("docker volume ls")
    gas = [l for l in stdout.split('\n') if 'gas' in l or 'DRIVER' in l]
    print()
    for line in gas: print(f"  {line}")
    pause()

def docker_networks():
    clear(); banner()
    stdout,_,_ = run_cmd("docker network ls")
    gas = [l for l in stdout.split('\n') if 'gas' in l or 'NETWORK' in l]
    print()
    for line in gas: print(f"  {line}")
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 8: HEALTH CHECK
# ═══════════════════════════════════════════════════════════════
def menu_health():
    clear(); banner()
    divider("🔌 HEALTH CHECK SEMUA SERVICE", C.CYAN)
    running = get_running()
    print()

    ok=warn=err=0
    results = []
    for svc,cat in ALL_SERVICES:
        port       = PORTS.get(svc)
        is_running = svc in running
        port_ok    = ping_port("localhost",port) if port else None
        icon       = ICONS.get(cat,"📦")

        if   not is_running:       status=c(C.RED,"○ stopped");  err+=1
        elif port and not port_ok: status=c(C.YELLOW,"⚠ no resp"); warn+=1
        else:                      status=c(C.GREEN,"● healthy");  ok+=1

        port_str = f":{port}" if port else "    "
        print(f"  {icon} {c(C.CYAN,svc):<46} {port_str:<6} {status}")

    print(f"\n  {c(C.GREEN,f'✅ {ok}')}  {c(C.YELLOW,f'⚠️  {warn}')}  {c(C.RED,f'❌ {err}')}")
    pause()

# ═══════════════════════════════════════════════════════════════
#  MENU 9: LAPORAN
# ═══════════════════════════════════════════════════════════════
def menu_report():
    while True:
        clear(); banner()
        divider("📋 LAPORAN", C.CYAN)
        print(f"""
  {c(C.CYAN,'1.')} 📊 Generate Laporan Lengkap (semua service)
  {c(C.CYAN,'2.')} 📁 Lihat Laporan Sebelumnya
  {c(C.CYAN,'0.')} ← Kembali
""")
        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': report_generate()
        elif ch=='2': report_list()
        elif ch=='0': break

def report_generate():
    clear(); banner()
    divider("GENERATE LAPORAN", C.CYAN)
    print(c(C.DIM,"\n  Mengumpulkan data semua service...\n"))

    running    = get_running()
    issues     = load_json(ISSUES_FILE)
    all_c      = get_all_containers()
    gas_c      = {k:v for k,v in all_c.items() if k.startswith("gas-")}
    timestamp  = datetime.now().strftime("%Y%m%d-%H%M")
    report_file= REPORT_DIR/f"report-{timestamp}.txt"
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    lines = []
    lines.append("="*70)
    lines.append(f"  GAS — LAPORAN SISTEM LENGKAP")
    lines.append(f"  Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("="*70)

    # Container status
    lines.append("\n── CONTAINER STATUS ──────────────────────────────────────────────────")
    up=down=0
    for svc,cat in ALL_SERVICES:
        is_up = svc in running
        status = "● UP   " if is_up else "○ DOWN "
        port   = PORTS.get(svc,"")
        lines.append(f"  {status} {svc:<48} port:{port}")
        if is_up: up+=1
        else: down+=1
    lines.append(f"\n  Total UP: {up} | DOWN: {down}")

    # Port check
    lines.append("\n── PORT / HEALTH CHECK ───────────────────────────────────────────────")
    for svc,_ in ALL_SERVICES:
        port = PORTS.get(svc)
        if not port: continue
        ok   = ping_port("localhost",port)
        lines.append(f"  {'✅' if ok else '❌'} {svc:<48} :{port}")

    # Scan issues
    lines.append("\n── HASIL SCAN (AUDIT) ────────────────────────────────────────────────")
    if issues:
        crit = [(s,v) for s,v in issues.items() if v.get("critical")]
        envm = [(s,v) for s,v in issues.items() if v.get("env_missing")]
        lines.append(f"  Critical   : {len(crit)}")
        lines.append(f"  ENV Missing: {len(envm)}")
        for s,v in crit:
            lines.append(f"\n  🔴 {s}:")
            for i in v.get("critical",[]):
                lines.append(f"     • {i}")
        for s,v in envm:
            lines.append(f"\n  🟡 {s}: {', '.join(v.get('env_missing',[]))}")
    else:
        lines.append("  Belum ada hasil scan. Jalankan Audit → Scan dulu.")

    # Docker resource
    lines.append("\n── RESOURCE USAGE ────────────────────────────────────────────────────")
    stdout,_,_ = run_cmd("docker stats --no-stream --format '{{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}'")
    for line in stdout.split('\n'):
        if 'gas-' in line: lines.append(f"  {line}")

    lines.append("\n" + "="*70)
    lines.append(f"  End of Report — {timestamp}")
    lines.append("="*70)

    report_content = "\n".join(lines)
    with open(report_file,'w') as f: f.write(report_content)

    print(report_content)
    print(f"\n  {c(C.GREEN,f'✅ Laporan disimpan: {report_file}')}")
    pause()

def report_list():
    clear(); banner()
    REPORT_DIR.mkdir(parents=True,exist_ok=True)
    reports = sorted(REPORT_DIR.glob("*.txt"),reverse=True)
    if not reports:
        print(c(C.YELLOW,"\n  Belum ada laporan.")); pause(); return

    divider("LAPORAN SEBELUMNYA", C.CYAN)
    for i,r in enumerate(reports,1):
        size = r.stat().st_size//1024
        print(f"  {c(C.CYAN,str(i)+'.')} {r.name}  {c(C.DIM,f'{size}KB')}")
    print(f"  {c(C.CYAN,'0.')} ← Batal\n")

    ch = input(c(C.WHITE,"  Pilih untuk lihat: ")).strip()
    try:
        idx=int(ch)-1
        if 0<=idx<len(reports):
            content = reports[idx].read_text()
            print()
            for line in content.split('\n'): print(f"  {line}")
    except ValueError: pass
    pause()

# ═══════════════════════════════════════════════════════════════
#  MAIN MENU
# ═══════════════════════════════════════════════════════════════
def main_menu():
    LOG_BASE.mkdir(parents=True,exist_ok=True)

    while True:
        clear(); banner()

        issues   = load_json(ISSUES_FILE)
        n_crit   = len([s for s,v in issues.items() if v.get("critical")])
        n_env    = len([s for s,v in issues.items() if v.get("env_missing")])
        running  = len(get_running())
        total    = len(ALL_SERVICES)

        divider("MENU UTAMA")
        print(f"""
  {c(C.CYAN,'1.')} 🔍 Audit & Debug         {c(C.DIM,f'scan + debug service')} {c(C.RED, f'[{n_crit} crit]') if n_crit else ''}
  {c(C.CYAN,'2.')} 🚀 Deploy & Restart      {c(C.DIM,'build, start, stop service')}
  {c(C.CYAN,'3.')} 📊 Monitor & Log         {c(C.DIM,'status, log realtime, error')}
  {c(C.CYAN,'4.')} 🔑 ENV Manager           {c(C.DIM,'list, edit, validasi env')} {c(C.YELLOW,f'[{n_env} missing]') if n_env else ''}
  {c(C.CYAN,'5.')} 🖥️  Terminal UI           {c(C.DIM,'test endpoint, frontend, debug BE+FE')}
  {c(C.CYAN,'6.')} 📈 Grafana & Observ.     {c(C.DIM,'prometheus, loki, alert')}
  {c(C.CYAN,'7.')} 🐳 Docker Manager        {c(C.DIM,'ps, stats, prune, inspect')}
  {c(C.CYAN,'8.')} 🔌 Health Check          {c(C.DIM,f'ping semua port [{running}/{total} up]')}
  {c(C.CYAN,'9.')} 📋 Laporan               {c(C.DIM,'generate report lengkap')}
  {c(C.CYAN,'0.')} ❌ Keluar
""")
        if not in_tmux():
            print(c(C.YELLOW,"  ⚠️  Belum di tmux! Ketik: tmux new -s gas\n"))

        ch = input(c(C.WHITE,"  Pilih: ")).strip()
        if   ch=='1': menu_audit()
        elif ch=='2': menu_deploy()
        elif ch=='3': menu_monitor()
        elif ch=='4': menu_env()
        elif ch=='5': menu_terminal_ui()
        elif ch=='6': menu_grafana()
        elif ch=='7': menu_docker()
        elif ch=='8': menu_health(); 
        elif ch=='9': menu_report()
        elif ch=='0':
            print(c(C.CYAN,"\n  Bye bro! Gas terus GAS! 🚀\n"))
            sys.exit(0)

# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Cek docker
    if not check_docker():
        print(c(C.RED, "\n  ❌ Docker tidak ditemukan! Install docker dulu."))
        sys.exit(1)

    # Cek Claude CLI
    claude_path = _find_claude()
    if not claude_path:
        print(c(C.YELLOW, """
  ⚠️  Claude CLI tidak ditemukan!

  Cara install:
    # Pastikan Node.js 18+ dulu:
    node --version

    # Install Claude:
    npm install -g @anthropic-ai/claude-code

    # Atau kalau pakai npm global tanpa sudo:
    mkdir -p ~/.npm-global
    npm config set prefix ~/.npm-global
    echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
    npm install -g @anthropic-ai/claude-code

    # Login:
    claude login
"""))
        ans = input(c(C.DIM, "  Lanjut tanpa Claude AI? (y/n): ")).strip().lower()
        if ans != 'y':
            sys.exit(0)
    else:
        print(c(C.DIM, f"  Claude CLI ditemukan: {claude_path}"))

    # Peringatan API key
    if check_api_key_conflict():
        print(c(C.YELLOW, """
  ⚠️  PERHATIAN: ANTHROPIC_API_KEY terdeteksi di environment!
  Ini akan menggunakan BILLING API, bukan quota Pro $20 lo.

  Untuk pakai quota Pro $20:
    unset ANTHROPIC_API_KEY
    # Atau hapus dari ~/.bashrc lalu: source ~/.bashrc

  gas-tools.py sudah otomatis ignore API key saat panggil Claude.
"""))
        input(c(C.DIM, "  Tekan Enter untuk lanjut..."))

    main_menu()
