#!/bin/bash
# ═══════════════════════════════════════════════════════════════════
#   GOLDEN AI STRATEGY — Terminal by Muhamad Ridwanjr
#   Version: 2.0 | Powered by Claude Code + Aider Multi-Model
# ═══════════════════════════════════════════════════════════════════

# ── COLORS (Claude-inspired palette) ──────────────────────────────
RESET='\033[0m'
BOLD='\033[1m'
DIM='\033[2m'
ITALIC='\033[3m'
BLINK='\033[5m'

# Claude palette
CC_CORAL='\033[38;2;205;95;70m'       # Claude coral/orange
CC_AMBER='\033[38;2;240;160;60m'      # Warm amber
CC_CREAM='\033[38;2;245;235;215m'     # Cream white
CC_SAND='\033[38;2;200;180;150m'      # Sand/muted
CC_DARK='\033[38;2;30;25;20m'         # Dark bg text

# Accent colors
AC_GOLD='\033[38;2;255;195;0m'        # Gold accent
AC_GREEN='\033[38;2;80;200;120m'      # Success green
AC_RED='\033[38;2;255;80;80m'         # Error red
AC_BLUE='\033[38;2;100;160;255m'      # Info blue
AC_PURPLE='\033[38;2;180;120;255m'    # Purple accent
AC_CYAN='\033[38;2;80;220;220m'       # Cyan

# Background colors
BG_DARK='\033[48;2;15;12;10m'         # Dark bg
BG_CARD='\033[48;2;25;20;15m'         # Card bg
BG_CORAL='\033[48;2;205;95;70m'       # Coral bg
BG_GOLD='\033[48;2;255;195;0m'        # Gold bg

BASE="$HOME/goldenaistrategy"
CONFIG="$BASE/.gas-agent-config"
LOGFILE="$BASE/tasks/terminal.log"

# ── HELPERS ────────────────────────────────────────────────────────
log() { echo "[$(date '+%H:%M:%S')] $1" >> "$LOGFILE" 2>/dev/null; }
W=$(tput cols 2>/dev/null || echo 100)

line() {
  local char="${1:-─}"
  local color="${2:-$CC_SAND}"
  echo -e "${color}$(printf '%*s' "$W" | tr ' ' "$char")${RESET}"
}

center() {
  local text="$1"
  local color="${2:-$CC_CREAM}"
  local clean=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
  local len=${#clean}
  local pad=$(( (W - len) / 2 ))
  printf "%${pad}s"
  echo -e "${color}${text}${RESET}"
}

box_line() {
  local text="$1"
  local color="${2:-$CC_SAND}"
  local clean=$(echo -e "$text" | sed 's/\x1b\[[0-9;]*m//g')
  local len=${#clean}
  local inner=$((W - 4))
  local pad=$((inner - len))
  echo -e "${color}║${RESET} ${text}$(printf '%*s' $pad)${color} ║${RESET}"
}

# ── CLEAR + HEADER ─────────────────────────────────────────────────
print_header() {
  clear
  echo ""
  line "═" "$CC_CORAL"
  echo ""

  # ASCII Art — GOLDEN AI STRATEGY
  echo -e "${CC_CORAL}${BOLD}"
  center "  ██████╗  ██████╗ ██╗     ██████╗ ███████╗███╗   ██╗"
  center " ██╔════╝ ██╔═══██╗██║     ██╔══██╗██╔════╝████╗  ██║"
  center " ██║  ███╗██║   ██║██║     ██║  ██║█████╗  ██╔██╗ ██║"
  center " ██║   ██║██║   ██║██║     ██║  ██║██╔══╝  ██║╚██╗██║"
  center " ╚██████╔╝╚██████╔╝███████╗██████╔╝███████╗██║ ╚████║"
  center "  ╚═════╝  ╚═════╝ ╚══════╝╚═════╝ ╚══════╝╚═╝  ╚═══╝"
  echo -e "${RESET}"

  echo -e "${AC_GOLD}${BOLD}"
  center "   █████╗ ██╗    ███████╗████████╗██████╗  █████╗ ████████╗███████╗ ██████╗██╗   ██╗"
  center " ██╔══██╗██║    ██╔════╝╚══██╔══╝██╔══██╗██╔══██╗╚══██╔══╝██╔════╝██╔════╝╚██╗ ██╔╝"
  center " ███████║██║    ███████╗   ██║   ██████╔╝███████║   ██║   █████╗  ██║  ███╗ ╚████╔╝ "
  center " ██╔══██║██║    ╚════██║   ██║   ██╔══██╗██╔══██║   ██║   ██╔══╝  ██║   ██║  ╚██╔╝  "
  center " ██║  ██║██║    ███████║   ██║   ██║  ██║██║  ██║   ██║   ███████╗╚██████╔╝   ██║   "
  center " ╚═╝  ╚═╝╚═╝    ╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝ ╚═════╝    ╚═╝   "
  echo -e "${RESET}"

  echo ""
  center "── Terminal by ${CC_CORAL}${BOLD}Muhamad Ridwanjr${RESET} ──" "$CC_SAND"
  center "SaaS AI Trading Platform · Forex · Crypto · IDX" "$DIM$CC_SAND"
  echo ""
  line "═" "$CC_CORAL"
}

# ── STATUS BAR ─────────────────────────────────────────────────────
print_status() {
  local claude_ok=false
  local aider_ok=false
  local docker_ok=false
  local services_up=0
  local services_total=0

  # Check Claude
  claude --version &>/dev/null && claude_ok=true

  # Check Aider
  aider --version &>/dev/null && aider_ok=true

  # Check Docker
  docker info &>/dev/null && docker_ok=true

  # Count services
  if $docker_ok; then
    services_up=$(docker compose -f "$BASE/docker-compose.yml" ps --status running 2>/dev/null | grep -c "running" || echo 0)
    services_total=$(docker compose -f "$BASE/docker-compose.yml" ps 2>/dev/null | tail -n +2 | wc -l | tr -d ' ' || echo 0)
  fi

  # Active model
  local active_model="─"
  [ -f "$CONFIG" ] && source "$CONFIG" 2>/dev/null
  active_model="${ACTIVE_MODEL:-Claude Code}"

  echo ""
  echo -e "  ${DIM}${CC_SAND}┌─ STATUS ─────────────────────────────────────────────────────────────┐${RESET}"
  printf "  ${DIM}${CC_SAND}│${RESET}  "

  # Claude Code status
  if $claude_ok; then
    printf "${AC_GREEN}● Claude Code${RESET}  "
  else
    printf "${AC_RED}○ Claude Code${RESET}  "
  fi

  # Aider status
  if $aider_ok; then
    printf "${AC_GREEN}● Aider${RESET}  "
  else
    printf "${AC_RED}○ Aider${RESET}  "
  fi

  # Docker status
  if $docker_ok; then
    printf "${AC_GREEN}● Docker${RESET}  "
    printf "${AC_CYAN}Services: ${BOLD}${services_up}/${services_total}${RESET}  "
  else
    printf "${AC_RED}○ Docker${RESET}  "
  fi

  # Active model
  printf "${AC_GOLD}Model: ${BOLD}${active_model}${RESET}  "

  # Time
  printf "${DIM}${CC_SAND}$(date '+%H:%M:%S %Z')${RESET}"

  echo ""
  echo -e "  ${DIM}${CC_SAND}└──────────────────────────────────────────────────────────────────────┘${RESET}"
  echo ""
}

# ── MAIN MENU ──────────────────────────────────────────────────────
print_main_menu() {
  echo -e "  ${CC_CORAL}${BOLD}MAIN MENU${RESET}"
  echo ""

  # Agent launcher section
  echo -e "  ${AC_GOLD}${BOLD}[ AGENT LAUNCHER ]${RESET}"
  echo -e "  ${CC_CORAL}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}1${RESET}  ${CC_CREAM}🧠  ORCHESTRATOR${RESET}          ${DIM}Master brain · scan · delegate${RESET}         ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}2${RESET}  ${CC_CREAM}⚙️   ENGINEERING${RESET}           ${DIM}gateway · terminal · frontend${RESET}          ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}3${RESET}  ${CC_CREAM}📊  DATA${RESET}                  ${DIM}mt5 · scrapers · rag · realtime${RESET}        ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}4${RESET}  ${CC_CREAM}📈  TRADING${RESET}               ${DIM}signal · quant · strategy · risk${RESET}       ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}5${RESET}  ${CC_CREAM}🖥️   PLATFORM${RESET}              ${DIM}auth · billing · user · telegram${RESET}       ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}6${RESET}  ${CC_CREAM}☁️   DEVOPS${RESET}               ${DIM}docker · nginx · monitoring${RESET}            ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}║${RESET}  ${BOLD}${AC_CYAN}7${RESET}  ${CC_CREAM}🔐  SECURITY${RESET}              ${DIM}firewall · audit · rate-limit${RESET}          ${CC_CORAL}║${RESET}"
  echo -e "  ${CC_CORAL}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
  echo ""

  # Model switcher
  echo -e "  ${AC_GOLD}${BOLD}[ MODEL SWITCHER ]${RESET}"
  echo -e "  ${AC_PURPLE}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "  ${AC_PURPLE}║${RESET}  ${BOLD}${AC_CYAN}m${RESET}  ${CC_CREAM}🔄  SWITCH MODEL${RESET}           ${DIM}Claude → Kimi → DeepSeek → Gemini${RESET}      ${AC_PURPLE}║${RESET}"
  echo -e "  ${AC_PURPLE}║${RESET}  ${BOLD}${AC_CYAN}a${RESET}  ${CC_CREAM}🔧  AIDER MODE${RESET}             ${DIM}Force Aider + current model${RESET}            ${AC_PURPLE}║${RESET}"
  echo -e "  ${AC_PURPLE}║${RESET}  ${BOLD}${AC_CYAN}c${RESET}  ${CC_CREAM}✨  CLAUDE CODE${RESET}            ${DIM}Force Claude Code CLI${RESET}                  ${AC_PURPLE}║${RESET}"
  echo -e "  ${AC_PURPLE}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
  echo ""

  # Tools section
  echo -e "  ${AC_GOLD}${BOLD}[ TOOLS ]${RESET}"
  echo -e "  ${AC_BLUE}╔══════════════════════════════════════════════════════════════════════╗${RESET}"
  echo -e "  ${AC_BLUE}║${RESET}  ${BOLD}${AC_CYAN}s${RESET}  ${CC_CREAM}📋  SERVICE STATUS${RESET}         ${DIM}Health check semua service${RESET}             ${AC_BLUE}║${RESET}"
  echo -e "  ${AC_BLUE}║${RESET}  ${BOLD}${AC_CYAN}l${RESET}  ${CC_CREAM}📜  LOGS${RESET}                  ${DIM}Docker logs realtime${RESET}                   ${AC_BLUE}║${RESET}"
  echo -e "  ${AC_BLUE}║${RESET}  ${BOLD}${AC_CYAN}t${RESET}  ${CC_CREAM}✅  TODO${RESET}                  ${DIM}Baca tasks/todo.md${RESET}                     ${AC_BLUE}║${RESET}"
  echo -e "  ${AC_BLUE}║${RESET}  ${BOLD}${AC_CYAN}g${RESET}  ${CC_CREAM}🌿  GIT STATUS${RESET}             ${DIM}git log + status${RESET}                       ${AC_BLUE}║${RESET}"
  echo -e "  ${AC_BLUE}║${RESET}  ${BOLD}${AC_CYAN}k${RESET}  ${CC_CREAM}⚙️   CONFIG${RESET}               ${DIM}Edit API keys + preferences${RESET}            ${AC_BLUE}║${RESET}"
  echo -e "  ${AC_BLUE}║${RESET}  ${BOLD}${AC_CYAN}o${RESET}  ${CC_CREAM}🏢  OPEN OFFICE${RESET}            ${DIM}Launch full 7-window tmux workspace${RESET}    ${AC_BLUE}║${RESET}"
  echo -e "  ${AC_BLUE}╚══════════════════════════════════════════════════════════════════════╝${RESET}"
  echo ""

  echo -e "  ${DIM}${CC_SAND}q = quit  │  h = help  │  r = refresh${RESET}"
  echo ""
}

# ── MODEL SWITCHER MENU ────────────────────────────────────────────
model_menu() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}MODEL SWITCHER${RESET}  ${DIM}— pilih AI model untuk semua agent${RESET}"
  echo ""

  # Load config
  [ -f "$CONFIG" ] && source "$CONFIG" 2>/dev/null

  echo -e "  ${CC_CORAL}${BOLD}Claude Code (Primary)${RESET}"
  echo -e "  ${CC_CORAL}┌─────────────────────────────────────────────────────────────────────┐${RESET}"
  echo -e "  ${CC_CORAL}│${RESET}  ${BOLD}1${RESET}  ${BOLD}${CC_CREAM}Claude Sonnet 4.6${RESET}     ${AC_GREEN}${BOLD}BEST${RESET}  ${DIM}Primary · architecture · complex${RESET}      ${CC_CORAL}│${RESET}"
  echo -e "  ${CC_CORAL}└─────────────────────────────────────────────────────────────────────┘${RESET}"
  echo ""

  echo -e "  ${AC_PURPLE}${BOLD}Aider + Kimi (Moonshot AI)${RESET}  ${DIM}~10x cheaper than Sonnet${RESET}"
  echo -e "  ${AC_PURPLE}┌─────────────────────────────────────────────────────────────────────┐${RESET}"
  echo -e "  ${AC_PURPLE}│${RESET}  ${BOLD}2${RESET}  ${BOLD}${CC_CREAM}Kimi K2.5${RESET}             ${AC_GOLD}${BOLD}⭐ REC${RESET} ${DIM}\$0.15/1M · setara Sonnet · Moonshot${RESET}   ${AC_PURPLE}│${RESET}"
  echo -e "  ${AC_PURPLE}│${RESET}  ${BOLD}3${RESET}  ${BOLD}${CC_CREAM}Kimi K1.5${RESET}             ${DIM}cheaper · good for simple tasks${RESET}        ${AC_PURPLE}│${RESET}"
  echo -e "  ${AC_PURPLE}└─────────────────────────────────────────────────────────────────────┘${RESET}"
  echo ""

  echo -e "  ${AC_CYAN}${BOLD}Aider + DeepSeek${RESET}"
  echo -e "  ${AC_CYAN}┌─────────────────────────────────────────────────────────────────────┐${RESET}"
  echo -e "  ${AC_CYAN}│${RESET}  ${BOLD}4${RESET}  ${BOLD}${CC_CREAM}DeepSeek V3 Chat${RESET}      ${AC_GREEN}${BOLD}CHEAP${RESET} ${DIM}\$0.27/1M · best price/quality${RESET}        ${AC_CYAN}│${RESET}"
  echo -e "  ${AC_CYAN}│${RESET}  ${BOLD}5${RESET}  ${BOLD}${CC_CREAM}DeepSeek R1${RESET}           ${DIM}\$0.55/1M · reasoning mode${RESET}             ${AC_CYAN}│${RESET}"
  echo -e "  ${AC_CYAN}└─────────────────────────────────────────────────────────────────────┘${RESET}"
  echo ""

  echo -e "  ${AC_BLUE}${BOLD}Aider + OpenRouter (Lainnya)${RESET}"
  echo -e "  ${AC_BLUE}┌─────────────────────────────────────────────────────────────────────┐${RESET}"
  echo -e "  ${AC_BLUE}│${RESET}  ${BOLD}6${RESET}  ${BOLD}${CC_CREAM}Gemini 2.5 Pro${RESET}        ${DIM}\$1.25/1M · powerful · fast${RESET}             ${AC_BLUE}│${RESET}"
  echo -e "  ${AC_BLUE}│${RESET}  ${BOLD}7${RESET}  ${BOLD}${CC_CREAM}Qwen3 235B${RESET}            ${DIM}\$0.22/1M · paling murah${RESET}               ${AC_BLUE}│${RESET}"
  echo -e "  ${AC_BLUE}│${RESET}  ${BOLD}8${RESET}  ${BOLD}${CC_CREAM}Claude Haiku 4.5${RESET}      ${DIM}\$1/1M · cepat · ringan${RESET}                ${AC_BLUE}│${RESET}"
  echo -e "  ${AC_BLUE}│${RESET}  ${BOLD}9${RESET}  ${BOLD}${CC_CREAM}Kimi K2.5 (OpenRouter)${RESET} ${DIM}via OpenRouter tanpa Moonshot key${RESET}     ${AC_BLUE}│${RESET}"
  echo -e "  ${AC_BLUE}└─────────────────────────────────────────────────────────────────────┘${RESET}"
  echo ""

  echo -e "  ${DIM}Current active: ${AC_GOLD}${BOLD}${ACTIVE_MODEL:-Claude Code}${RESET}"
  echo ""
  echo -ne "  ${CC_CREAM}Pilih model [1-9] atau ${DIM}b=back${CC_CREAM}: ${RESET}"
  read -r choice

  case "$choice" in
    1) set_model "claude" "Claude Code" "" "" "" ;;
    2) set_model "aider" "Kimi K2.5" "moonshot-v1-128k" "$KIMI_API_KEY" "https://api.moonshot.cn/v1" ;;
    3) set_model "aider" "Kimi K1.5" "moonshot-v1-32k" "$KIMI_API_KEY" "https://api.moonshot.cn/v1" ;;
    4) set_model "aider" "DeepSeek V3" "deepseek/deepseek-chat-v3-5" "$OPENROUTER_API_KEY" "https://openrouter.ai/api/v1" ;;
    5) set_model "aider" "DeepSeek R1" "deepseek/deepseek-r1" "$OPENROUTER_API_KEY" "https://openrouter.ai/api/v1" ;;
    6) set_model "aider" "Gemini 2.5 Pro" "google/gemini-2.5-pro" "$OPENROUTER_API_KEY" "https://openrouter.ai/api/v1" ;;
    7) set_model "aider" "Qwen3 235B" "qwen/qwen3-235b-a22b" "$OPENROUTER_API_KEY" "https://openrouter.ai/api/v1" ;;
    8) set_model "aider" "Claude Haiku 4.5" "anthropic/claude-haiku-4-5" "$OPENROUTER_API_KEY" "https://openrouter.ai/api/v1" ;;
    9) set_model "aider" "Kimi K2.5 (OR)" "moonshotai/kimi-k2" "$OPENROUTER_API_KEY" "https://openrouter.ai/api/v1" ;;
    b|B) return ;;
  esac
}

set_model() {
  local engine="$1" name="$2" model="$3" key="$4" base="$5"

  # Update config
  if [ -f "$CONFIG" ]; then
    sed -i "s/^ACTIVE_ENGINE=.*/ACTIVE_ENGINE=\"$engine\"/" "$CONFIG"
    sed -i "s/^ACTIVE_MODEL=.*/ACTIVE_MODEL=\"$name\"/" "$CONFIG"
    sed -i "s/^ACTIVE_MODEL_ID=.*/ACTIVE_MODEL_ID=\"$model\"/" "$CONFIG"
    sed -i "s/^ACTIVE_API_KEY=.*/ACTIVE_API_KEY=\"$key\"/" "$CONFIG"
    sed -i "s/^ACTIVE_BASE_URL=.*/ACTIVE_BASE_URL=\"$base\"/" "$CONFIG"
  fi

  echo ""
  echo -e "  ${AC_GREEN}${BOLD}✅ Model switched to: $name${RESET}"
  echo -e "  ${DIM}Engine: $engine | Model: $model${RESET}"
  log "Model switched: $name ($model)"
  sleep 1.5
}

# ── SERVICE STATUS ─────────────────────────────────────────────────
show_status() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}SERVICE HEALTH CHECK${RESET}  ${DIM}— $(date)${RESET}"
  echo ""

  declare -A DIVISION_SERVICES=(
    ["⚙️  ENGINEERING"]="8000:gateway 8085:terminal-be 3000:frontend 8005:web"
    ["📊 DATA"]="8110:mt5-ws 8100:mt5-data 9601:calendar 9603:fundamental 8111:realtime"
    ["📈 TRADING"]="9500:quant-orch 8106:signal 9499:feature 9503:regime 9501:pattern 8203:indicator"
    ["🖥️  PLATFORM"]="8001:auth 8004:billing 8002:user 8003:telegram 8107:journal"
    ["☁️  DEVOPS"]="9003:ai-orch 8105:eng-orch 6379:redis 5432:postgres"
    ["🔐 SECURITY"]="8000:gateway 8001:auth 8004:billing"
  )

  local total_up=0 total_down=0

  for division in "⚙️  ENGINEERING" "📊 DATA" "📈 TRADING" "🖥️  PLATFORM" "☁️  DEVOPS"; do
    echo -e "  ${CC_CORAL}${BOLD}$division${RESET}"
    local services="${DIVISION_SERVICES[$division]}"
    local row=""
    for svc in $services; do
      port=${svc%:*}; name=${svc#*:}
      up=$(curl -s --max-time 1 localhost:$port/health 2>/dev/null | grep -c "ok" || echo 0)
      if [ "$up" -gt "0" ]; then
        row+="    ${AC_GREEN}●${RESET} ${CC_CREAM}${name}${RESET}${DIM}:${port}${RESET}  "
        ((total_up++))
      else
        row+="    ${AC_RED}○${RESET} ${DIM}${name}:${port}${RESET}  "
        ((total_down++))
      fi
    done
    echo -e "$row"
    echo ""
  done

  line "─" "$CC_SAND"
  local pct=0
  [ $((total_up + total_down)) -gt 0 ] && pct=$(( total_up * 100 / (total_up + total_down) ))
  echo -e "  ${AC_GOLD}Total: ${AC_GREEN}${BOLD}${total_up} UP${RESET}  ${AC_RED}${total_down} DOWN${RESET}  ${CC_SAND}(${pct}% healthy)${RESET}"
  echo ""
  echo -ne "  ${DIM}Press Enter to continue...${RESET}"
  read -r
}

# ── LAUNCH AGENT ───────────────────────────────────────────────────
launch_agent() {
  local role="$1"
  local division="$2"

  [ -f "$CONFIG" ] && source "$CONFIG" 2>/dev/null

  local engine="${ACTIVE_ENGINE:-claude}"
  local model="${ACTIVE_MODEL:-Claude Code}"
  local model_id="${ACTIVE_MODEL_ID:-}"
  local api_key="${ACTIVE_API_KEY:-}"
  local base_url="${ACTIVE_BASE_URL:-}"

  print_header

  echo -e "  ${AC_GOLD}${BOLD}LAUNCHING AGENT${RESET}"
  echo ""
  echo -e "  ${CC_CREAM}Division  : ${CC_CORAL}${BOLD}$division${RESET}"
  echo -e "  ${CC_CREAM}Engine    : ${AC_CYAN}${BOLD}$engine${RESET}"
  echo -e "  ${CC_CREAM}Model     : ${AC_GOLD}${BOLD}$model${RESET}"
  echo -e "  ${CC_CREAM}Context   : ${DIM}$BASE/divisions/${role^^}_MANAGER.md${RESET}"
  echo ""
  line "─" "$CC_CORAL"
  echo ""

  # Determine context file
  local ctx_file="$BASE/ORCHESTRATOR.md"
  [ "$role" != "orchestrator" ] && ctx_file="$BASE/divisions/${role^^}_MANAGER.md"

  if [ ! -f "$ctx_file" ]; then
    echo -e "  ${AC_RED}❌ Context file not found: $ctx_file${RESET}"
    echo -e "  ${DIM}Run bootstrap first: bash gas-bootstrap.sh${RESET}"
    echo ""
    echo -ne "  Press Enter..."
    read -r
    return
  fi

  log "Launching $role agent | engine:$engine | model:$model"

  if [ "$engine" = "claude" ]; then
    # Claude Code CLI
    echo -e "  ${AC_GREEN}${BOLD}✅ Starting Claude Code CLI...${RESET}"
    echo ""
    sleep 0.5
    cd "$BASE"
    claude --dangerously-skip-permissions \
      "Read $ctx_file and tasks/todo.md and tasks/lessons.md.
       You are the $division agent for Golden AI Strategy.
       Owner: Muhamad Ridwanjr.
       Run your AUTO-SCAN first, then report findings and await instructions."

  elif [ "$engine" = "aider" ]; then
    # Aider with selected model
    echo -e "  ${AC_PURPLE}${BOLD}✅ Starting Aider + $model...${RESET}"
    echo ""

    if ! command -v aider &>/dev/null; then
      echo -e "  ${AC_RED}❌ Aider not installed${RESET}"
      echo -e "  ${DIM}Install: pip install aider-chat${RESET}"
      echo -ne "  Press Enter..."
      read -r
      return
    fi

    sleep 0.5
    cd "$BASE"

    # Build aider flags based on model source
    if [[ "$base_url" == *"moonshot"* ]]; then
      # Kimi via Moonshot direct API
      OPENAI_API_KEY="$api_key" \
      OPENAI_API_BASE="$base_url" \
      aider \
        --model "$model_id" \
        --read "$ctx_file" \
        --read "tasks/todo.md" \
        --read "tasks/lessons.md" \
        --no-auto-commits \
        --pretty \
        --stream \
        --message "Read your context file. You are the $division agent. Run your AUTO-SCAN first."

    elif [[ "$base_url" == *"deepseek"* ]]; then
      # DeepSeek direct API
      OPENAI_API_KEY="$api_key" \
      OPENAI_API_BASE="$base_url" \
      aider \
        --model "openai/$model_id" \
        --read "$ctx_file" \
        --read "tasks/todo.md" \
        --read "tasks/lessons.md" \
        --no-auto-commits \
        --pretty \
        --stream

    else
      # OpenRouter
      OPENAI_API_KEY="$api_key" \
      OPENAI_API_BASE="$base_url" \
      aider \
        --model "openrouter/$model_id" \
        --read "$ctx_file" \
        --read "tasks/todo.md" \
        --read "tasks/lessons.md" \
        --no-auto-commits \
        --pretty \
        --stream
    fi
  fi
}

# ── TODO VIEWER ────────────────────────────────────────────────────
show_todo() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}TASK BOARD — tasks/todo.md${RESET}"
  echo ""

  if [ ! -f "$BASE/tasks/todo.md" ]; then
    echo -e "  ${AC_RED}❌ tasks/todo.md not found${RESET}"
    echo -e "  ${DIM}Run bootstrap first${RESET}"
  else
    # Color-coded output
    while IFS= read -r line; do
      if [[ "$line" == *"CRITICAL"* ]]; then
        echo -e "  ${AC_RED}${line}${RESET}"
      elif [[ "$line" == *"✅"* ]] || [[ "$line" == *"[x]"* ]]; then
        echo -e "  ${AC_GREEN}${line}${RESET}"
      elif [[ "$line" == *"[ ]"* ]]; then
        echo -e "  ${CC_CREAM}${line}${RESET}"
      elif [[ "$line" == "##"* ]]; then
        echo -e "  ${AC_GOLD}${BOLD}${line}${RESET}"
      elif [[ "$line" == "###"* ]]; then
        echo -e "  ${CC_CORAL}${line}${RESET}"
      elif [[ "$line" == *"CHECKPOINT"* ]]; then
        echo -e "  ${AC_PURPLE}${line}${RESET}"
      else
        echo -e "  ${DIM}${line}${RESET}"
      fi
    done < "$BASE/tasks/todo.md"
  fi

  echo ""
  echo -ne "  ${DIM}Press Enter to continue...${RESET}"
  read -r
}

# ── LOGS ───────────────────────────────────────────────────────────
show_logs() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}DOCKER LOGS${RESET}  ${DIM}— pilih service${RESET}"
  echo ""

  local services=(
    "ALL services (follow)"
    "gas-gateway-api"
    "gas-terminal-backend"
    "gas-ai-orchestrator"
    "gas-billing-service"
    "gas-signal-service"
    "gas-mt5-websocket"
    "gas-realtime-hub"
    "gas-terminal-frontend"
  )

  for i in "${!services[@]}"; do
    echo -e "  ${BOLD}${AC_CYAN}$i${RESET}  ${CC_CREAM}${services[$i]}${RESET}"
  done

  echo ""
  echo -ne "  ${CC_CREAM}Pilih [0-8] atau ${DIM}b=back${CC_CREAM}: ${RESET}"
  read -r choice

  cd "$BASE"
  case "$choice" in
    0) docker compose logs -f --tail=50 2>/dev/null ;;
    [1-8])
      local svc="${services[$choice]}"
      docker compose logs -f "$svc" --tail=100 2>/dev/null || echo "Service not found"
      ;;
    b|B) return ;;
  esac
}

# ── CONFIG EDITOR ──────────────────────────────────────────────────
edit_config() {
  if [ ! -f "$CONFIG" ]; then
    create_default_config
  fi
  ${EDITOR:-nano} "$CONFIG"
}

# ── GIT STATUS ─────────────────────────────────────────────────────
show_git() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}GIT STATUS${RESET}"
  echo ""
  cd "$BASE"
  echo -e "  ${CC_CORAL}── Recent Commits ──${RESET}"
  git log --oneline --graph --color=always -10 2>/dev/null || echo "  No git repo"
  echo ""
  echo -e "  ${CC_CORAL}── Working Tree ──${RESET}"
  git status --short 2>/dev/null
  echo ""
  echo -ne "  ${DIM}Press Enter to continue...${RESET}"
  read -r
}

# ── OPEN OFFICE (full tmux) ────────────────────────────────────────
open_office() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}OPENING FULL OFFICE...${RESET}"
  echo ""
  echo -e "  ${DIM}Launching 7-window tmux workspace${RESET}"
  sleep 1

  if [ -f "$BASE/gas-office.sh" ]; then
    bash "$BASE/gas-office.sh"
  else
    echo -e "  ${AC_RED}❌ gas-office.sh not found${RESET}"
    echo -e "  ${DIM}Run: bash gas-bootstrap.sh${RESET}"
    echo -ne "  Press Enter..."
    read -r
  fi
}

# ── HELP ───────────────────────────────────────────────────────────
show_help() {
  print_header
  echo -e "  ${AC_GOLD}${BOLD}HELP — GOLDEN AI STRATEGY TERMINAL${RESET}"
  echo ""
  echo -e "  ${CC_CORAL}${BOLD}AGENT NUMBERS (1-7)${RESET}"
  echo -e "  ${CC_CREAM}  1  ORCHESTRATOR${RESET}  ${DIM}Master brain — scan semua service, assign WORKER${RESET}"
  echo -e "  ${CC_CREAM}  2  ENGINEERING${RESET}   ${DIM}gateway:8000 · terminal-be:8085 · frontend:3000${RESET}"
  echo -e "  ${CC_CREAM}  3  DATA${RESET}           ${DIM}mt5-ws:8110 · scrapers · rag · realtime:8111${RESET}"
  echo -e "  ${CC_CREAM}  4  TRADING${RESET}        ${DIM}signal:8106 · quant:9500 · strategy · risk${RESET}"
  echo -e "  ${CC_CREAM}  5  PLATFORM${RESET}       ${DIM}auth:8001 · billing:8004 · user · telegram${RESET}"
  echo -e "  ${CC_CREAM}  6  DEVOPS${RESET}         ${DIM}docker · nginx · ai-orchestrator:9003${RESET}"
  echo -e "  ${CC_CREAM}  7  SECURITY${RESET}       ${DIM}firewall · audit · rate-limiting${RESET}"
  echo ""
  echo -e "  ${CC_CORAL}${BOLD}MODEL SWITCHING${RESET}"
  echo -e "  ${DIM}  m  → Model menu (Claude / Kimi / DeepSeek / Gemini)${RESET}"
  echo -e "  ${DIM}  a  → Force Aider mode dengan model yang aktif${RESET}"
  echo -e "  ${DIM}  c  → Force Claude Code CLI${RESET}"
  echo ""
  echo -e "  ${CC_CORAL}${BOLD}WORKFLOW${RESET}"
  echo -e "  ${DIM}  1. Start dengan pilih 1 (ORCHESTRATOR)${RESET}"
  echo -e "  ${DIM}  2. ORCHESTRATOR scan project → assign WORKER task di todo.md${RESET}"
  echo -e "  ${DIM}  3. Buka window baru (Ctrl+b c) → pilih division yang diassign${RESET}"
  echo -e "  ${DIM}  4. 2 Claude/Aider jalan paralel di 2 window tmux${RESET}"
  echo -e "  ${DIM}  5. Kalau Claude limit → tekan m → switch ke Kimi/DeepSeek${RESET}"
  echo ""
  echo -ne "  ${DIM}Press Enter...${RESET}"
  read -r
}

# ── DEFAULT CONFIG ─────────────────────────────────────────────────
create_default_config() {
  mkdir -p "$(dirname $CONFIG)"
  cat > "$CONFIG" << 'EOF'
# GOLDEN AI STRATEGY — Agent Config
# Owner: Muhamad Ridwanjr
# DO NOT COMMIT TO GIT

# ── ACTIVE MODEL (auto-updated by terminal) ──
ACTIVE_ENGINE="claude"
ACTIVE_MODEL="Claude Code"
ACTIVE_MODEL_ID=""
ACTIVE_API_KEY=""
ACTIVE_BASE_URL=""

# ── KIMI (Moonshot AI) ──
# Get key: https://platform.moonshot.cn
KIMI_API_KEY=""
KIMI_MODEL="moonshot-v1-128k"
KIMI_BASE_URL="https://api.moonshot.cn/v1"

# ── DEEPSEEK (Direct) ──
# Get key: https://platform.deepseek.com
DEEPSEEK_API_KEY=""
DEEPSEEK_MODEL="deepseek-chat"
DEEPSEEK_BASE_URL="https://api.deepseek.com/v1"

# ── OPENROUTER ──
OPENROUTER_API_KEY="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"
OPENROUTER_BASE_URL="https://openrouter.ai/api/v1"

# ── AI SETTINGS ──
AI_MAX_TOKENS=8000
AI_TEMPERATURE=0.3
EOF
  chmod 600 "$CONFIG"
}

# ── FORCE MODES ────────────────────────────────────────────────────
force_claude() {
  set_model "claude" "Claude Code" "" "" ""
  echo -e "  ${AC_GREEN}${BOLD}✅ Forced Claude Code CLI${RESET}"
  sleep 1
}

force_aider() {
  [ -f "$CONFIG" ] && source "$CONFIG" 2>/dev/null
  if [ -z "$ACTIVE_MODEL_ID" ]; then
    echo -e "  ${AC_RED}❌ No Aider model set. Use 'm' to select model first.${RESET}"
    sleep 2
    return
  fi
  sed -i "s/^ACTIVE_ENGINE=.*/ACTIVE_ENGINE=\"aider\"/" "$CONFIG"
  echo -e "  ${AC_GREEN}${BOLD}✅ Forced Aider mode with $ACTIVE_MODEL${RESET}"
  sleep 1
}

# ── BOOTSTRAP CHECK ────────────────────────────────────────────────
check_bootstrap() {
  if [ ! -f "$BASE/ORCHESTRATOR.md" ] || [ ! -d "$BASE/divisions" ]; then
    print_header
    echo -e "  ${AC_RED}${BOLD}⚠️  PROJECT NOT BOOTSTRAPPED${RESET}"
    echo ""
    echo -e "  ${CC_CREAM}ORCHESTRATOR.md dan divisions/ belum ada.${RESET}"
    echo -e "  ${DIM}Jalankan bootstrap dulu:${RESET}"
    echo ""
    echo -e "  ${AC_CYAN}  claude --dangerously-skip-permissions < GAS_BOOTSTRAP_PROMPT_v5.md${RESET}"
    echo ""
    echo -ne "  ${DIM}Lanjut anyway? [y/n]: ${RESET}"
    read -r ans
    [ "$ans" != "y" ] && exit 0
  fi
}

# ── INIT ───────────────────────────────────────────────────────────
init() {
  unset ANTHROPIC_API_KEY
  mkdir -p "$BASE/tasks"
  touch "$LOGFILE"
  [ ! -f "$CONFIG" ] && create_default_config
  log "Terminal started"
}

# ══════════════════════════════════════════════════════════════════
#  MAIN LOOP
# ══════════════════════════════════════════════════════════════════
init
check_bootstrap

while true; do
  print_header
  print_status
  print_main_menu

  echo -ne "  ${CC_CORAL}${BOLD}golden-ai-strategy${RESET}${CC_SAND} ❯ ${RESET}"
  read -r choice

  case "$choice" in
    1) launch_agent "orchestrator"  "🧠 ORCHESTRATOR" ;;
    2) launch_agent "engineering"   "⚙️  ENGINEERING" ;;
    3) launch_agent "data"          "📊 DATA" ;;
    4) launch_agent "trading"       "📈 TRADING" ;;
    5) launch_agent "platform"      "🖥️  PLATFORM" ;;
    6) launch_agent "devops"        "☁️  DEVOPS" ;;
    7) launch_agent "security"      "🔐 SECURITY" ;;
    m|M) model_menu ;;
    a|A) force_aider ;;
    c|C) force_claude ;;
    s|S) show_status ;;
    l|L) show_logs ;;
    t|T) show_todo ;;
    g|G) show_git ;;
    k|K) edit_config ;;
    o|O) open_office ;;
    h|H) show_help ;;
    r|R) continue ;;
    q|Q)
      echo ""
      echo -e "  ${CC_CORAL}${BOLD}GOLDEN AI STRATEGY${RESET}  ${DIM}Session ended.${RESET}"
      echo -e "  ${DIM}by Muhamad Ridwanjr${RESET}"
      echo ""
      log "Terminal exited"
      exit 0
      ;;
    *)
      echo -e "  ${AC_RED}Invalid option. Press h for help.${RESET}"
      sleep 1
      ;;
  esac
done