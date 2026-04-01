#!/bin/bash
# ═══════════════════════════════════════════════════════════════
# GOLDEN AI STRATEGY — Terminal Launcher v6.0
# by Muhamad Ridwanjr
# ═══════════════════════════════════════════════════════════════

BASE="$HOME/gasstrategyai"
CONFIG="$BASE/.gas-agent-config"
TASKS="$BASE/tasks/todo.md"

# Colors
R='\033[0m'
CORAL='\033[38;2;205;95;70m'
AMBER='\033[38;2;245;185;85m'
CREAM='\033[38;2;245;235;215m'
CYAN='\033[38;2;80;220;220m'
GREEN='\033[38;2;80;200;120m'
RED='\033[38;2;220;80;80m'
DIM='\033[2m'
BOLD='\033[1m'
YELLOW='\033[38;2;255;215;0m'

unset ANTHROPIC_API_KEY

# Load config
load_config() {
  [ -f "$CONFIG" ] && source "$CONFIG"
  KIMI_API_KEY="${KIMI_API_KEY:-}"
  DEEPSEEK_API_KEY="${DEEPSEEK_API_KEY:-}"
  OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}"
  GEMINI_API_KEY="${GEMINI_API_KEY:-}"
  VERTEX_API_KEY="${VERTEX_API_KEY:-}"
  VERTEX_PROJECT="${VERTEX_PROJECT:-}"
  CURRENT_MODEL="${CURRENT_MODEL:-claude}"
}

# Check health of a port
check_port() {
  local port=$1
  local result
  result=$(curl -s --max-time 1 "localhost:$port/health" 2>/dev/null)
  if echo "$result" | grep -qi "ok\|healthy\|running"; then
    echo "✅"
  else
    # fallback: check if port is open
    (echo >/dev/tcp/localhost/$port) 2>/dev/null && echo "🟡" || echo "❌"
  fi
}

# Status bar
show_status() {
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
  printf "  ${DIM}STATUS${R}  "

  # Claude
  claude_ok=$(claude --version 2>/dev/null | head -1)
  [ -n "$claude_ok" ] && printf "${GREEN}Claude ✅${R}  " || printf "${RED}Claude ❌${R}  "

  # Aider
  aider_ok=$(aider --version 2>/dev/null | head -1)
  [ -n "$aider_ok" ] && printf "${GREEN}Aider ✅${R}  " || printf "${DIM}Aider ─${R}  "

  # Docker
  dc_count=$(docker compose -f "$BASE/docker-compose.yml" ps --filter status=running -q 2>/dev/null | wc -l)
  printf "${GREEN}Docker ${dc_count} up${R}  "

  # Model
  printf "${AMBER}Model: ${CURRENT_MODEL}${R}"
  printf "\n"
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
}

# Header
show_header() {
  clear
  printf "\n"
  printf "${CORAL}  ╔═══════════════════════════════════════════════════════╗${R}\n"
  printf "${CORAL}  ║${R}                                                       ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}   ${BOLD}${AMBER} ██████╗  █████╗ ███████╗${R}                        ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}   ${BOLD}${AMBER}██╔════╝ ██╔══██╗██╔════╝${R}                        ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}   ${BOLD}${AMBER}██║  ███╗███████║███████╗${R}  ${CREAM}Golden AI Strategy${R}    ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}   ${BOLD}${AMBER}██║   ██║██╔══██║╚════██║${R}  ${DIM}by Muhamad Ridwanjr${R}   ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}   ${BOLD}${AMBER}╚██████╔╝██║  ██║███████║${R}  ${DIM}v6.0 · 2026${R}          ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}   ${BOLD}${AMBER} ╚═════╝ ╚═╝  ╚═╝╚══════╝${R}                        ${CORAL}║${R}\n"
  printf "${CORAL}  ║${R}                                                       ${CORAL}║${R}\n"
  printf "${CORAL}  ╚═══════════════════════════════════════════════════════╝${R}\n"
  printf "\n"
  show_status
}

# Service health panel
show_health() {
  printf "\n${BOLD}${CREAM}  SERVICE HEALTH${R}\n"
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"

  declare -A services=(
    ["gateway"]=8000 ["auth"]=8001 ["billing"]=8004 ["terminal-be"]=8085
    ["web-backend"]=8005 ["ai-orch"]=9003 ["signal"]=8106 ["realtime"]=8111
    ["mt5-ws"]=8110 ["binance"]=9612 ["quant-orch"]=9500 ["smc-engine"]=8006
    ["strategy-core"]=7003 ["calendar"]=9601 ["fundamental"]=9603
    ["chart"]=9700 ["frontend"]=3000
  )

  local order=("gateway" "auth" "billing" "terminal-be" "web-backend" "ai-orch"
               "signal" "realtime" "mt5-ws" "binance" "quant-orch" "smc-engine"
               "strategy-core" "calendar" "fundamental" "chart" "frontend")

  local col=0
  for svc in "${order[@]}"; do
    port=${services[$svc]}
    status=$(check_port $port)
    printf "  ${status} ${DIM}%-18s${R}:${CYAN}%-5s${R}" "$svc" "$port"
    col=$((col+1))
    [ $((col % 2)) -eq 0 ] && printf "\n"
  done
  [ $((col % 2)) -ne 0 ] && printf "\n"
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
  printf "\n  ${DIM}Press any key to return...${R}"
  read -r -n1
}

# Todo viewer
show_todo() {
  printf "\n${BOLD}${CREAM}  TASK BOARD${R}\n"
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
  if [ -f "$TASKS" ]; then
    while IFS= read -r line; do
      if echo "$line" | grep -q "^## "; then
        printf "  ${BOLD}${AMBER}${line}${R}\n"
      elif echo "$line" | grep -q "❌\|DOWN\|CRITICAL"; then
        printf "  ${RED}${line}${R}\n"
      elif echo "$line" | grep -q "✅\|healthy\|DONE"; then
        printf "  ${GREEN}${line}${R}\n"
      elif echo "$line" | grep -q "\- \[ \]"; then
        printf "  ${YELLOW}${line}${R}\n"
      else
        printf "  ${DIM}${line}${R}\n"
      fi
    done < "$TASKS"
  else
    printf "  ${RED}tasks/todo.md not found${R}\n"
  fi
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
  printf "\n  ${DIM}Press any key to return...${R}"
  read -r -n1
}

# Model switcher
show_model_menu() {
  while true; do
    clear
    printf "\n${BOLD}${CREAM}  MODEL SWITCHER${R}\n"
    printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
    printf "  Current: ${AMBER}${CURRENT_MODEL}${R}\n\n"
    printf "  ${BOLD}${GREEN}── PRIMARY ──────────────────────────────────────────${R}\n"
    printf "  ${BOLD}1${R}  ${GREEN}Claude Code${R}                     ${DIM}(browser auth · best overall)${R}\n"
    printf "\n  ${BOLD}${CYAN}── DIRECT API ───────────────────────────────────────${R}\n"
    printf "  ${BOLD}2${R}  ${CYAN}Kimi 2.5${R}    ${DIM}[Moonshot Direct]${R}  ${DIM}(KIMI_API_KEY · kimi-latest)${R}\n"
    printf "  ${BOLD}3${R}  ${CYAN}Gemini 2.5 Flash${R} ${DIM}[AI Studio]${R}   ${DIM}(GEMINI_API_KEY · free tier)${R}\n"
    printf "  ${BOLD}4${R}  ${CYAN}Gemini 2.5 Flash${R} ${DIM}[Vertex AI]${R}   ${DIM}(VERTEX_API_KEY · enterprise)${R}\n"
    printf "\n  ${BOLD}${YELLOW}── VIA OPENROUTER ───────────────────────────────────${R}\n"
    printf "  ${BOLD}5${R}  ${YELLOW}Kimi K2.5${R}        ${DIM}[OR]${R}          ${DIM}(\$0.45/\$2.20/1M · 262k ctx)${R}\n"
    printf "  ${BOLD}6${R}  ${YELLOW}DeepSeek V3.2${R}    ${DIM}[OR]${R}          ${DIM}(\$0.26/\$0.38/1M · 163k)${R}\n"
    printf "  ${BOLD}7${R}  ${YELLOW}DeepSeek R1${R}      ${DIM}[OR]${R}          ${DIM}(\$0.45/\$2.15/1M · reasoning)${R}\n"
    printf "  ${BOLD}8${R}  ${YELLOW}Grok 4.20 Multi-Agent${R} ${DIM}[OR]${R}    ${DIM}(x-ai · multi-agent-beta)${R}\n"
    printf "  ${BOLD}9${R}  ${YELLOW}Gemini 3.1 Flash Lite${R} ${DIM}[OR]${R}    ${DIM}(google · OR free preview)${R}\n"
    printf "  ${BOLD}A${R}  ${YELLOW}Gemini 2.5 Flash${R}  ${DIM}[OR]${R}          ${DIM}(\$0.30/\$2.50/1M · 1M ctx)${R}\n"
    printf "  ${BOLD}B${R}  ${YELLOW}Gemini 2.5 Flash Lite${R} ${DIM}[OR]${R}    ${DIM}(\$0.10/\$0.40/1M · ultra cheap)${R}\n"
    printf "  ${BOLD}C${R}  ${YELLOW}Gemini 2.5 Pro${R}    ${DIM}[OR]${R}          ${DIM}(\$1.25/\$10/1M · most capable)${R}\n"
    printf "  ${BOLD}D${R}  ${YELLOW}Qwen3-Coder FREE${R}  ${DIM}[OR]${R}          ${DIM}(\$0.00 FREE · 262k ctx)${R}\n"
    printf "  ${BOLD}E${R}  ${YELLOW}Claude Haiku 4.5${R}  ${DIM}[OR]${R}          ${DIM}(\$1.00/\$5.00/1M · fast)${R}\n"
    printf "  ${BOLD}F${R}  ${YELLOW}Claude Sonnet 4.5${R} ${DIM}[OR]${R}          ${DIM}(\$3.00/\$15/1M · smart)${R}\n"
    printf "\n  ${BOLD}${DIM}── DEEPSEEK DIRECT API ──────────────────────────────${R}\n"
    printf "  ${BOLD}d${R}  ${DIM}DeepSeek V3 (direct)${R}            ${DIM}(DEEPSEEK_API_KEY required)${R}\n"
    printf "  ${BOLD}r${R}  ${DIM}DeepSeek R1 (direct)${R}            ${DIM}(DEEPSEEK_API_KEY required)${R}\n"
    printf "\n  ${BOLD}q${R}  Back\n"
    printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
    printf "  Choice: "
    read -r -n1 mchoice
    printf "\n"

    _save_model() { sed -i "s/^CURRENT_MODEL=.*/CURRENT_MODEL=$1/" "$CONFIG" 2>/dev/null || echo "CURRENT_MODEL=$1" >> "$CONFIG"; }
    case $mchoice in
      1)   CURRENT_MODEL="claude";              _save_model claude;              break ;;
      # Direct API
      2)   CURRENT_MODEL="kimi-2.5-direct";    _save_model kimi-2.5-direct;     break ;;
      3)   CURRENT_MODEL="gemini-studio";       _save_model gemini-studio;       break ;;
      4)   CURRENT_MODEL="gemini-vertex";       _save_model gemini-vertex;       break ;;
      # OpenRouter
      5)   CURRENT_MODEL="kimi-k2.5";           _save_model kimi-k2.5;           break ;;
      6)   CURRENT_MODEL="deepseek-v3.2";       _save_model deepseek-v3.2;       break ;;
      7)   CURRENT_MODEL="deepseek-r1";         _save_model deepseek-r1;         break ;;
      8)   CURRENT_MODEL="grok-openrouter";     _save_model grok-openrouter;     break ;;
      9)   CURRENT_MODEL="gemini-lite-or";      _save_model gemini-lite-or;      break ;;
      a|A) CURRENT_MODEL="gemini-flash";        _save_model gemini-flash;        break ;;
      b|B) CURRENT_MODEL="gemini-flash-lite";   _save_model gemini-flash-lite;   break ;;
      c|C) CURRENT_MODEL="gemini-2.5-pro";      _save_model gemini-2.5-pro;      break ;;
      e|E) CURRENT_MODEL="claude-haiku";        _save_model claude-haiku;        break ;;
      f|F) CURRENT_MODEL="claude-sonnet";       _save_model claude-sonnet;       break ;;
      g|G) CURRENT_MODEL="qwen3-coder-free";    _save_model qwen3-coder-free;    break ;;
      # DeepSeek direct
      d)   CURRENT_MODEL="deepseek-v3";         _save_model deepseek-v3;         break ;;
      r)   CURRENT_MODEL="deepseek-r1-direct";  _save_model deepseek-r1-direct;  break ;;
      q|Q) break ;;
    esac
  done
}

# Launch Claude Code
launch_claude() {
  local ctx="${1:-ORCHESTRATOR}"
  local ctx_file=""

  case $ctx in
    1|ORCHESTRATOR) ctx_file="$BASE/ORCHESTRATOR.md" ;;
    2|ENGINEERING)  ctx_file="$BASE/divisions/ENGINEERING_MANAGER.md" ;;
    3|DATA)         ctx_file="$BASE/divisions/DATA_MANAGER.md" ;;
    4|TRADING)      ctx_file="$BASE/divisions/TRADING_MANAGER.md" ;;
    5|PLATFORM)     ctx_file="$BASE/divisions/PLATFORM_MANAGER.md" ;;
    6|DEVOPS)       ctx_file="$BASE/divisions/DEVOPS_MANAGER.md" ;;
    7|SECURITY)     ctx_file="$BASE/divisions/SECURITY_MANAGER.md" ;;
    *)              ctx_file="" ;;
  esac

  cd "$BASE" || exit 1
  unset ANTHROPIC_API_KEY

  if [ -f "$ctx_file" ]; then
    printf "\n${GREEN}  Launching Claude Code → ${BOLD}${ctx}${R}\n"
    printf "  ${DIM}Role context: $(basename "$ctx_file")${R}\n"
    printf "  ${DIM}Mode: interactive · --append-system-prompt${R}\n\n"
    sleep 0.3
    claude --permission-mode dontAsk \
           --append-system-prompt "$(cat "$ctx_file")" \
           --name "GAS-${ctx}"
  else
    printf "\n${GREEN}  Launching Claude Code (bare)${R}\n\n"
    sleep 0.3
    claude --permission-mode dontAsk --name "GAS-bare"
  fi
}

# Launch Aider
launch_aider() {
  local model="${CURRENT_MODEL:-claude}"
  printf "\n${CYAN}  Launching Aider → model: ${model}${R}\n"
  sleep 0.5
  cd "$BASE" || exit 1

  # Helper: launch via OpenRouter
  _aider_or() {
    if [ -n "$OPENROUTER_API_KEY" ]; then
      OPENROUTER_API_KEY="$OPENROUTER_API_KEY" aider \
        --model "$1" --no-auto-commits --dirty-commits
    else
      printf "${RED}  ⚠ OPENROUTER_API_KEY not set. Edit .gas-agent-config${R}\n"; sleep 2
    fi
  }

  case $model in

    # ── Kimi 2.5 · Moonshot Direct API ───────────────────────────────────
    kimi-2.5-direct)
      if [ -n "$KIMI_API_KEY" ]; then
        printf "${CYAN}  Model: kimi-latest via api.moonshot.ai${R}\n"; sleep 0.5
        OPENAI_API_BASE="https://api.moonshot.ai/v1" \
        OPENAI_API_KEY="$KIMI_API_KEY" \
          aider --model openai/kimi-latest --no-auto-commits --dirty-commits \
          2>/dev/null || \
        OPENAI_API_BASE="https://api.moonshot.ai/v1" \
        OPENAI_API_KEY="$KIMI_API_KEY" \
          aider --model openai/moonshot-v1-8k --no-auto-commits --dirty-commits
      else
        printf "${RED}  ⚠ KIMI_API_KEY not set. Edit .gas-agent-config${R}\n"; sleep 2
      fi ;;

    # ── Gemini 2.5 Flash · Google AI Studio ──────────────────────────────
    gemini-studio)
      if [ -n "$GEMINI_API_KEY" ]; then
        printf "${BLUE}  Model: gemini-2.5-flash via Google AI Studio${R}\n"; sleep 0.5
        GEMINI_API_KEY="$GEMINI_API_KEY" \
          aider --model gemini/gemini-2.5-flash --no-auto-commits --dirty-commits \
          2>/dev/null || \
        GEMINI_API_KEY="$GEMINI_API_KEY" \
          aider --model gemini/gemini-2.0-flash --no-auto-commits --dirty-commits
      else
        printf "${RED}  ⚠ GEMINI_API_KEY not set. Edit .gas-agent-config${R}\n"; sleep 2
      fi ;;

    # ── Gemini 2.5 Flash · Vertex AI ─────────────────────────────────────
    gemini-vertex)
      if [ -n "$VERTEX_API_KEY" ]; then
        printf "${PURPLE}  Model: gemini-2.5-flash via Vertex AI${R}\n"
        printf "${DIM}  Note: Vertex AI key / bearer token from .gas-agent-config${R}\n"; sleep 0.5
        # Try as API key first (new Vertex AI API key feature)
        VERTEXAI_API_KEY="$VERTEX_API_KEY" \
          aider --model vertex_ai/gemini-2.5-flash --no-auto-commits --dirty-commits \
          2>/dev/null || {
          # Fallback: set as gcloud access token via GOOGLE_OAUTH_ACCESS_TOKEN
          printf "${AMBER}  Trying with Bearer token auth...${R}\n"
          GOOGLE_OAUTH_ACCESS_TOKEN="$VERTEX_API_KEY" \
          VERTEXAI_PROJECT="${VERTEX_PROJECT:-gas-ai}" \
          VERTEXAI_LOCATION="us-central1" \
            aider --model vertex_ai/gemini-2.5-flash --no-auto-commits --dirty-commits \
            2>/dev/null || printf "${RED}  ⚠ Vertex AI auth failed. Check VERTEX_API_KEY / VERTEX_PROJECT${R}\n"
          sleep 2
        }
      else
        printf "${RED}  ⚠ VERTEX_API_KEY not set. Edit .gas-agent-config${R}\n"; sleep 2
      fi ;;

    # ── Kimi K2.5 via OpenRouter ──────────────────────────────────────────
    kimi-k2.5)
      _aider_or "openrouter/moonshotai/kimi-k2.5" ;;

    # ── DeepSeek via OpenRouter ───────────────────────────────────────────
    deepseek-v3.2)
      _aider_or "openrouter/deepseek/deepseek-v3.2" ;;
    deepseek-r1)
      _aider_or "openrouter/deepseek/deepseek-r1-0528" ;;

    # ── Grok 4.20 Multi-Agent via OpenRouter ──────────────────────────────
    grok-openrouter)
      printf "${AMBER}  Model: x-ai/grok-4.20-multi-agent-beta via OpenRouter${R}\n"; sleep 0.5
      _aider_or "openrouter/x-ai/grok-4.20-multi-agent-beta" ;;

    # ── Gemini 3.1 Flash Lite via OpenRouter [separate from AI Studio] ────
    gemini-lite-or)
      printf "${YELLOW}  Model: google/gemini-3.1-flash-lite-preview via OpenRouter${R}\n"; sleep 0.5
      _aider_or "openrouter/google/gemini-3.1-flash-lite-preview" ;;

    # ── Gemini via OpenRouter ─────────────────────────────────────────────
    gemini-flash)
      _aider_or "openrouter/google/gemini-2.5-flash" ;;
    gemini-flash-lite)
      _aider_or "openrouter/google/gemini-2.5-flash-lite" ;;
    gemini-2.5-pro)
      _aider_or "openrouter/google/gemini-2.5-pro" ;;

    # ── Qwen3 Coder FREE via OpenRouter ──────────────────────────────────
    qwen3-coder-free)
      _aider_or "openrouter/qwen/qwen3-coder:free" ;;

    # ── Claude via OpenRouter ─────────────────────────────────────────────
    claude-haiku)
      _aider_or "openrouter/anthropic/claude-haiku-4.5" ;;
    claude-sonnet)
      _aider_or "openrouter/anthropic/claude-sonnet-4.5" ;;

    # ── DeepSeek direct API ───────────────────────────────────────────────
    deepseek-v3)
      if [ -n "$DEEPSEEK_API_KEY" ]; then
        DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" aider \
          --model deepseek/deepseek-chat \
          --no-auto-commits --dirty-commits
      else
        printf "${RED}  ⚠ DEEPSEEK_API_KEY not set. Edit .gas-agent-config${R}\n"; sleep 2
      fi ;;
    deepseek-r1-direct)
      if [ -n "$DEEPSEEK_API_KEY" ]; then
        DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" aider \
          --model deepseek/deepseek-reasoner \
          --no-auto-commits --dirty-commits
      else
        printf "${RED}  ⚠ DEEPSEEK_API_KEY not set. Edit .gas-agent-config${R}\n"; sleep 2
      fi ;;

    # ── Claude Code (default) ─────────────────────────────────────────────
    claude|*)
      aider --no-auto-commits --dirty-commits 2>/dev/null \
        || { printf "${RED}  ⚠ Aider not installed. Run: pip install aider-chat${R}\n"; sleep 2; }
      ;;
  esac
}

# Token usage panel
show_token_usage() {
  local mode="${1:-test}"
  if ! command -v python3 &>/dev/null; then
    printf "${RED}  ⚠ python3 not found${R}\n"; sleep 2; return
  fi
  local script="$BASE/scripts/gas_token_test.py"
  if [ ! -f "$script" ]; then
    printf "${RED}  ⚠ gas_token_test.py not found at scripts/${R}\n"; sleep 2; return
  fi
  case $mode in
    stats) python3 "$script" --stats ;;
    reset) python3 "$script" --reset ;;
    *)     python3 "$script" ;;
  esac
  printf "\n  ${DIM}Press any key to return...${R}"
  read -r -n1
}

# Edit config
edit_config() {
  if [ ! -f "$CONFIG" ]; then
    cat > "$CONFIG" << 'EOF'
# GAS Agent Config — DO NOT COMMIT THIS FILE
KIMI_API_KEY=
DEEPSEEK_API_KEY=
OPENROUTER_API_KEY=
GEMINI_API_KEY=
CURRENT_MODEL=claude
EOF
    chmod 600 "$CONFIG"
  fi
  ${EDITOR:-nano} "$CONFIG"
}

# Docker quick actions
docker_menu() {
  while true; do
    clear
    printf "\n${BOLD}${CREAM}  DOCKER QUICK${R}\n"
    printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
    printf "  ${BOLD}1${R}  docker compose ps\n"
    printf "  ${BOLD}2${R}  docker compose logs (errors last 30m)\n"
    printf "  ${BOLD}3${R}  docker stats (no-stream)\n"
    printf "  ${BOLD}4${R}  Restart a service\n"
    printf "  ${BOLD}5${R}  Rebuild + up a service\n"
    printf "  ${BOLD}6${R}  docker compose up -d (all)\n"
    printf "  ${BOLD}q${R}  Back\n"
    printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
    printf "  Choice: "
    read -r -n1 dc
    printf "\n"

    cd "$BASE" || return
    case $dc in
      1) docker compose ps; read -r -p "  Press enter..." ;;
      2) docker compose logs --since=30m 2>/dev/null | grep -iE "error|fatal|warn" | tail -30; read -r -p "  Press enter..." ;;
      3) docker stats --no-stream; read -r -p "  Press enter..." ;;
      4) printf "  Service name: "; read -r svc; docker compose restart "$svc"; read -r -p "  Press enter..." ;;
      5) printf "  Service name: "; read -r svc; docker compose build "$svc" && docker compose up -d "$svc"; read -r -p "  Press enter..." ;;
      6) docker compose up -d; read -r -p "  Press enter..." ;;
      q|Q) break ;;
    esac
  done
}

# Git quick actions
git_quick() {
  cd "$BASE" || return
  printf "\n${BOLD}${CREAM}  GIT STATUS${R}\n"
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
  git status --short | head -20
  printf "\n  ${DIM}Last 5 commits:${R}\n"
  git log --oneline -5
  printf "${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
  printf "\n  ${DIM}Press any key to return...${R}"
  read -r -n1
}

# Logs tail
tail_logs() {
  printf "\n  ${DIM}Service name (e.g. gas-signal-service): ${R}"
  read -r svc
  [ -z "$svc" ] && return
  cd "$BASE" && docker compose logs -f "$svc" --tail=50
}

# Main menu
main_menu() {
  load_config
  while true; do
    show_header
    printf "\n  ${BOLD}AGENTS${R}\n"
    printf "  ${CORAL}1${R}  ${BOLD}ORCHESTRATOR${R}        ${DIM}Master brain — scan + assign${R}\n"
    printf "  ${CORAL}2${R}  ${BOLD}Engineering${R}         ${DIM}gateway · terminal · frontend${R}\n"
    printf "  ${CORAL}3${R}  ${BOLD}Data${R}                ${DIM}mt5 · scrapers · rag · realtime${R}\n"
    printf "  ${CORAL}4${R}  ${BOLD}Trading${R}             ${DIM}signal · quant · strategy · risk${R}\n"
    printf "  ${CORAL}5${R}  ${BOLD}Platform${R}            ${DIM}auth · billing · user · telegram${R}\n"
    printf "  ${CORAL}6${R}  ${BOLD}DevOps${R}              ${DIM}docker · nginx · monitoring${R}\n"
    printf "  ${CORAL}7${R}  ${BOLD}Security${R}            ${DIM}firewall · audit · rate-limit${R}\n"
    printf "\n  ${BOLD}TOOLS${R}\n"
    printf "  ${CYAN}m${R}  Model switcher        ${DIM}[current: ${CURRENT_MODEL}]${R}\n"
    printf "  ${CYAN}a${R}  Launch Aider          ${DIM}[current: ${CURRENT_MODEL}]${R}\n"
    printf "  ${CYAN}c${R}  Launch Claude (bare)${R}\n"
    printf "  ${CYAN}u${R}  ${BOLD}Token Usage${R}           ${DIM}[test all models + usage stats]${R}\n"
    printf "  ${CYAN}U${R}  Token stats only      ${DIM}[show saved stats, no API calls]${R}\n"
    printf "  ${CYAN}s${R}  Service health panel${R}\n"
    printf "  ${CYAN}l${R}  Tail service logs${R}\n"
    printf "  ${CYAN}t${R}  View task board${R}\n"
    printf "  ${CYAN}g${R}  Git status${R}\n"
    printf "  ${CYAN}k${R}  Docker quick menu${R}\n"
    printf "  ${CYAN}o${R}  Edit .gas-agent-config${R}\n"
    printf "  ${CYAN}h${R}  Show this menu${R}\n"
    printf "  ${DIM}q  Quit${R}\n"
    printf "\n${CORAL}  ───────────────────────────────────────────────────────────${R}\n"
    printf "  ${BOLD}Pick: ${R}"
    read -r -n1 choice
    printf "\n"

    case $choice in
      1) launch_claude "ORCHESTRATOR" ;;
      2) launch_claude "ENGINEERING" ;;
      3) launch_claude "DATA" ;;
      4) launch_claude "TRADING" ;;
      5) launch_claude "PLATFORM" ;;
      6) launch_claude "DEVOPS" ;;
      7) launch_claude "SECURITY" ;;
      m|M) show_model_menu ;;
      a|A) launch_aider ;;
      c|C) cd "$BASE" && unset ANTHROPIC_API_KEY && claude --permission-mode dontAsk --name "GAS-bare" ;;
      u)   show_token_usage "test" ;;
      U)   show_token_usage "stats" ;;
      s|S) show_health ;;
      l|L) tail_logs ;;
      t|T) show_todo ;;
      g|G) git_quick ;;
      k|K) docker_menu ;;
      o|O) edit_config ;;
      h|H) : ;;
      q|Q) printf "\n${DIM}  Bye bro. Keep building.\n\n${R}"; exit 0 ;;
      *) printf "  ${DIM}Unknown option${R}\n"; sleep 0.5 ;;
    esac
  done
}

# Entry point
main_menu
