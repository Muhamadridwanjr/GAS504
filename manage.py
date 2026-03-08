#!/usr/bin/env python3
"""
GAS Service Manager
Manage all Golden AI Strategy Docker services
"""

import os
import subprocess
import sys
import time
from pathlib import Path

# ── Colors ──────────────────────────────────────────────────────────────────
R  = "\033[0m"
B  = "\033[1m"
C  = "\033[96m"   # cyan
G  = "\033[92m"   # green
Y  = "\033[93m"   # yellow
RD = "\033[91m"   # red
M  = "\033[95m"   # magenta
DIM= "\033[2m"

BASE = Path(__file__).parent

SERVICES = [
    "gas-ai-orchestrator",
    "gas-alert-engine",
    "gas-auth-service",
    "gas-billing-service",
    "gas-calendar-news-service",
    "gas-chart-service",
    "gas-correlation",
    "gas-data-ingestor",
    "gas-engine-orchestrator",
    "gas-feature-engine",
    "gas-fundamental-data-service",
    "gas-gateway-api",
    "gas-indicator-engine",
    "gas-journal-service",
    "gas-market-data-processor",
    "gas-market-phase",
    "gas-mt5-data-service",
    "gas-mt5-websocket",
    "gas-notification-service",
    "gas-observability",
    "gas-orderflow",
    "gas-pattern-detector",
    "gas-quant-backtester",
    "gas-quant-orch",
    "gas-rag-macro",
    "gas-rag-technical",
    "gas-realtime-hub",
    "gas-regime-detector",
    "gas-risk-engine",
    "gas-screener-service",
    "gas-signal-service",
    "gas-smc-engine",
    "gas-social-service",
    "gas-statarb-engine",
    "gas-strategy-core",
    "gas-telegram-bot",
    "gas-term-service",
    "gas-terminal-backend",
    "gas-terminal-service",
    "gas-tradingplan-service",
    "gas-trend-engine",
    "gas-user-service",
    "gas-vector-db",
    "gas-web-backend",
]


# ── Helpers ──────────────────────────────────────────────────────────────────

def clear():
    os.system("clear")

def run(cmd, cwd=None, capture=False):
    if capture:
        result = subprocess.run(cmd, shell=True, cwd=cwd,
                                capture_output=True, text=True)
        return result.stdout.strip(), result.returncode
    else:
        subprocess.run(cmd, shell=True, cwd=cwd)

def service_dir(name):
    return BASE / name

def has_compose(name):
    return (service_dir(name) / "docker-compose.yml").exists()

def container_status(name):
    out, _ = run(f"docker inspect --format='{{{{.State.Status}}}}' {name} 2>/dev/null", capture=True)
    return out.strip("'") if out else "not found"

def health_status(name):
    out, _ = run(
        f"docker inspect --format='{{{{if .State.Health}}}}{{{{.State.Health.Status}}}}{{{{else}}}}no-health{{{{end}}}}' {name} 2>/dev/null",
        capture=True
    )
    return out.strip("'") if out else ""

def status_color(s):
    if s == "running":   return f"{G}{s}{R}"
    if s == "exited":    return f"{RD}{s}{R}"
    if s == "restarting":return f"{Y}{s}{R}"
    if s == "not found": return f"{DIM}{s}{R}"
    return f"{Y}{s}{R}"

def health_color(h):
    if h == "healthy":   return f"{G}healthy{R}"
    if h == "unhealthy": return f"{RD}unhealthy{R}"
    return ""

def pause():
    input(f"\n{DIM}[Enter untuk kembali ke menu]{R}")


# ── Header ───────────────────────────────────────────────────────────────────

def header():
    clear()
    print(f"{B}{C}╔══════════════════════════════════════════════╗{R}")
    print(f"{B}{C}║     GAS SERVICE MANAGER — GoldenAIStrategy  ║{R}")
    print(f"{B}{C}╚══════════════════════════════════════════════╝{R}")
    print()


# ── Status overview ──────────────────────────────────────────────────────────

def show_status(services=None):
    targets = services or SERVICES
    print(f"{B}{'#':<4} {'SERVICE':<35} {'STATUS':<18} {'HEALTH'}{R}")
    print("─" * 70)
    for i, svc in enumerate(targets, 1):
        st = container_status(svc)
        hl = health_status(svc)
        hl_str = f"  {health_color(hl)}" if hl and hl != "no-health" else ""
        print(f"{DIM}{i:<4}{R}{svc:<35} {status_color(st):<28}{hl_str}")
    print()


# ── Start ────────────────────────────────────────────────────────────────────

def start_service(name):
    d = service_dir(name)
    if not has_compose(name):
        print(f"{RD}[SKIP]{R} {name} — tidak ada docker-compose.yml")
        return
    print(f"{G}[START]{R} {name}...")
    run("docker compose up -d --remove-orphans", cwd=d)

def start_all():
    header()
    print(f"{B}{G}▶ START ALL SERVICES{R}\n")
    for svc in SERVICES:
        start_service(svc)
    print(f"\n{G}✓ Semua service di-start{R}")
    pause()

def start_selected():
    header()
    print(f"{B}{G}▶ START — Pilih Service{R}\n")
    for i, s in enumerate(SERVICES, 1):
        print(f"  {DIM}{i:>2}.{R} {s}")
    print(f"\n  {Y}0.{R} Kembali")
    print(f"\n{DIM}Masukkan nomor (pisah koma, misal: 1,3,5 atau 'all'){R}")
    raw = input(f"{C}> {R}").strip()
    if raw == "0" or not raw:
        return
    selected = parse_selection(raw)
    print()
    for i in selected:
        start_service(SERVICES[i])
    print(f"\n{G}✓ Done{R}")
    pause()


# ── Stop ─────────────────────────────────────────────────────────────────────

def stop_service(name):
    d = service_dir(name)
    if not has_compose(name):
        return
    print(f"{Y}[STOP]{R} {name}...")
    run("docker compose stop", cwd=d)

def stop_all():
    header()
    print(f"{B}{Y}■ STOP ALL SERVICES{R}\n")
    for svc in SERVICES:
        stop_service(svc)
    print(f"\n{Y}✓ Semua service di-stop{R}")
    pause()

def stop_selected():
    header()
    print(f"{B}{Y}■ STOP — Pilih Service{R}\n")
    for i, s in enumerate(SERVICES, 1):
        st = container_status(s)
        print(f"  {DIM}{i:>2}.{R} {s:<35} {status_color(st)}")
    print(f"\n  {Y}0.{R} Kembali")
    print(f"\n{DIM}Masukkan nomor (pisah koma, misal: 1,3,5 atau 'all'){R}")
    raw = input(f"{C}> {R}").strip()
    if raw == "0" or not raw:
        return
    selected = parse_selection(raw)
    print()
    for i in selected:
        stop_service(SERVICES[i])
    print(f"\n{Y}✓ Done{R}")
    pause()


# ── Delete ───────────────────────────────────────────────────────────────────

def delete_service(name):
    d = service_dir(name)
    if not has_compose(name):
        return
    print(f"{RD}[DELETE]{R} {name}...")
    run("docker compose down --remove-orphans", cwd=d)

def delete_all():
    header()
    print(f"{B}{RD}✕ DELETE ALL CONTAINERS{R}\n")
    confirm = input(f"{RD}Yakin mau hapus semua container? (ketik 'yes'): {R}").strip()
    if confirm.lower() != "yes":
        print("Dibatalkan.")
        pause()
        return
    for svc in SERVICES:
        delete_service(svc)
    print(f"\n{RD}✓ Semua container dihapus{R}")
    pause()

def delete_selected():
    header()
    print(f"{B}{RD}✕ DELETE — Pilih Service{R}\n")
    for i, s in enumerate(SERVICES, 1):
        st = container_status(s)
        print(f"  {DIM}{i:>2}.{R} {s:<35} {status_color(st)}")
    print(f"\n  {Y}0.{R} Kembali")
    print(f"\n{DIM}Masukkan nomor (pisah koma, misal: 1,3,5 atau 'all'){R}")
    raw = input(f"{C}> {R}").strip()
    if raw == "0" or not raw:
        return
    selected = parse_selection(raw)
    confirm = input(f"{RD}Yakin hapus {len(selected)} service? (yes/no): {R}").strip()
    if confirm.lower() != "yes":
        print("Dibatalkan.")
        pause()
        return
    print()
    for i in selected:
        delete_service(SERVICES[i])
    print(f"\n{RD}✓ Done{R}")
    pause()


# ── Logs ─────────────────────────────────────────────────────────────────────

def logs_all():
    header()
    print(f"{B}{M}📋 LOGS — Semua Service (Ctrl+C untuk keluar){R}\n")
    running = [s for s in SERVICES if container_status(s) == "running"]
    if not running:
        print(f"{RD}Tidak ada service yang running.{R}")
        pause()
        return
    containers = " ".join(running)
    try:
        subprocess.run(f"docker logs --tail=20 --follow {' '.join([f'$(docker ps -qf name={s})' for s in running])} 2>&1 | head -500", shell=True)
    except KeyboardInterrupt:
        pass
    pause()

def logs_per_service():
    header()
    print(f"{B}{M}📋 LOGS — Pilih Service{R}\n")
    for i, s in enumerate(SERVICES, 1):
        st = container_status(s)
        print(f"  {DIM}{i:>2}.{R} {s:<35} {status_color(st)}")
    print(f"\n  {Y}0.{R} Kembali")
    raw = input(f"\n{C}Nomor service: {R}").strip()
    if raw == "0" or not raw:
        return
    try:
        idx = int(raw) - 1
        name = SERVICES[idx]
    except (ValueError, IndexError):
        print(f"{RD}Input tidak valid{R}")
        pause()
        return

    header()
    print(f"{B}{M}📋 LOGS — {name}{R}")
    print(f"{DIM}Ctrl+C untuk keluar | tail=100{R}\n")
    try:
        subprocess.run(f"docker logs --tail=100 --follow {name}", shell=True)
    except KeyboardInterrupt:
        pass
    pause()

def debug_service():
    header()
    print(f"{B}{RD}🔍 DEBUG LOGS — Pilih Service{R}\n")
    for i, s in enumerate(SERVICES, 1):
        st = container_status(s)
        print(f"  {DIM}{i:>2}.{R} {s:<35} {status_color(st)}")
    print(f"\n  {Y}0.{R} Kembali")
    raw = input(f"\n{C}Nomor service: {R}").strip()
    if raw == "0" or not raw:
        return
    try:
        idx = int(raw) - 1
        name = SERVICES[idx]
    except (ValueError, IndexError):
        print(f"{RD}Input tidak valid{R}")
        pause()
        return

    header()
    print(f"{B}{RD}🔍 DEBUG — {name}{R}\n")
    print(f"{B}Container Info:{R}")
    run(f"docker inspect {name} --format='Status: {{{{.State.Status}}}} | Exit: {{{{.State.ExitCode}}}} | Error: {{{{.State.Error}}}}' 2>/dev/null")
    print(f"\n{B}Last 50 lines logs (stderr+stdout):{R}\n")
    run(f"docker logs --tail=50 {name} 2>&1")
    pause()


# ── Status Menu ──────────────────────────────────────────────────────────────

def status_all():
    header()
    print(f"{B}📊 STATUS SEMUA SERVICE{R}\n")
    show_status()
    # Summary
    running = sum(1 for s in SERVICES if container_status(s) == "running")
    stopped = sum(1 for s in SERVICES if container_status(s) == "exited")
    missing = sum(1 for s in SERVICES if container_status(s) == "not found")
    print(f"  {G}Running: {running}{R}  |  {RD}Stopped: {stopped}{R}  |  {DIM}Not Found: {missing}{R}")
    pause()


# ── Rebuild ──────────────────────────────────────────────────────────────────

def rebuild_service():
    header()
    print(f"{B}{C}🔨 REBUILD — Pilih Service{R}\n")
    for i, s in enumerate(SERVICES, 1):
        print(f"  {DIM}{i:>2}.{R} {s}")
    print(f"\n  {Y}0.{R} Kembali")
    raw = input(f"\n{C}Nomor service: {R}").strip()
    if raw == "0" or not raw:
        return
    try:
        idx = int(raw) - 1
        name = SERVICES[idx]
    except (ValueError, IndexError):
        print(f"{RD}Input tidak valid{R}")
        pause()
        return

    d = service_dir(name)
    print(f"\n{C}[REBUILD]{R} {name}...")
    run(f"docker compose build --no-cache {name}", cwd=d)
    run(f"docker compose up -d {name}", cwd=d)
    print(f"\n{G}✓ Rebuild selesai{R}")
    pause()


# ── Helper ───────────────────────────────────────────────────────────────────

def parse_selection(raw):
    if raw.lower() == "all":
        return list(range(len(SERVICES)))
    result = []
    for part in raw.split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            result.extend(range(int(a)-1, int(b)))
        else:
            result.append(int(part)-1)
    return [i for i in result if 0 <= i < len(SERVICES)]


# ── Menus ────────────────────────────────────────────────────────────────────

def start_menu():
    while True:
        header()
        print(f"{B}{G}▶ START{R}\n")
        print(f"  {G}1.{R} Start SEMUA service")
        print(f"  {G}2.{R} Start service tertentu")
        print(f"  {Y}0.{R} Kembali")
        ch = input(f"\n{C}> {R}").strip()
        if ch == "1": start_all()
        elif ch == "2": start_selected()
        elif ch == "0": break

def stop_menu():
    while True:
        header()
        print(f"{B}{Y}■ STOP{R}\n")
        print(f"  {Y}1.{R} Stop SEMUA service")
        print(f"  {Y}2.{R} Stop service tertentu")
        print(f"  {Y}0.{R} Kembali")
        ch = input(f"\n{C}> {R}").strip()
        if ch == "1": stop_all()
        elif ch == "2": stop_selected()
        elif ch == "0": break

def delete_menu():
    while True:
        header()
        print(f"{B}{RD}✕ DELETE{R}\n")
        print(f"  {RD}1.{R} Delete SEMUA container")
        print(f"  {RD}2.{R} Delete container tertentu")
        print(f"  {Y}0.{R} Kembali")
        ch = input(f"\n{C}> {R}").strip()
        if ch == "1": delete_all()
        elif ch == "2": delete_selected()
        elif ch == "0": break

def logs_menu():
    while True:
        header()
        print(f"{B}{M}📋 LOGS{R}\n")
        print(f"  {M}1.{R} Logs semua service (stream)")
        print(f"  {M}2.{R} Logs per service")
        print(f"  {RD}3.{R} Debug logs per service")
        print(f"  {Y}0.{R} Kembali")
        ch = input(f"\n{C}> {R}").strip()
        if ch == "1": logs_all()
        elif ch == "2": logs_per_service()
        elif ch == "3": debug_service()
        elif ch == "0": break


# ── Main Menu ─────────────────────────────────────────────────────────────────

def main():
    while True:
        header()
        print(f"  {B}Total Services: {len(SERVICES)}{R}\n")
        print(f"  {G}1.{R} {B}▶ Start{R}     — Jalankan service")
        print(f"  {Y}2.{R} {B}■ Stop{R}      — Hentikan service")
        print(f"  {RD}3.{R} {B}✕ Delete{R}    — Hapus container")
        print(f"  {M}4.{R} {B}📋 Logs{R}      — Lihat logs & debug")
        print(f"  {C}5.{R} {B}📊 Status{R}    — Status semua service")
        print(f"  {C}6.{R} {B}🔨 Rebuild{R}   — Rebuild service tertentu")
        print(f"\n  {DIM}q. Keluar{R}")
        print()
        ch = input(f"{C}Pilih menu: {R}").strip().lower()

        if ch == "1": start_menu()
        elif ch == "2": stop_menu()
        elif ch == "3": delete_menu()
        elif ch == "4": logs_menu()
        elif ch == "5": status_all()
        elif ch == "6": rebuild_service()
        elif ch in ("q", "quit", "exit"):
            clear()
            print(f"{G}Bye! Docker tetap off ya bro.{R}\n")
            sys.exit(0)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear()
        print(f"{G}Bye!{R}\n")
        sys.exit(0)
