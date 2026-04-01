# GOLDEN AI STRATEGY — BOOTSTRAP PROMPT v6.0
# Super Complete · Division Architecture · Claude Code + Aider
# Owner: Muhamad Ridwanjr
#
# CARA PAKAI:
#   cd ~/goldenaistrategy
#   claude --dangerously-skip-permissions < GAS_BOOTSTRAP_PROMPT_v6.md

---

You are bootstrapping the complete **Golden AI Strategy** agent system.
Owner: Muhamad Ridwanjr | Base: ~/goldenaistrategy/

Generate ALL files below. Scan first, then generate, then report.

---

## PHASE 0 — FULL SCAN

```bash
echo "╔══════════════════════════════════════════════╗"
echo "║  GOLDEN AI STRATEGY — BOOTSTRAP SCAN v6.0  ║"
echo "║  by Muhamad Ridwanjr                        ║"
echo "╚══════════════════════════════════════════════╝"
date && whoami && hostname

unset ANTHROPIC_API_KEY
[ -n "$ANTHROPIC_API_KEY" ] && echo "⚠️ API KEY CONFLICT!" || echo "✅ Claude auth: OK"

echo "=== SERVICE FOLDERS ==="
ls -d ~/goldenaistrategy/gas-*/ 2>/dev/null | while read f; do
  name=$(basename $f)
  src=$([ -d "$f/src" ] && echo "✅" || echo "❌")
  main=$([ -f "$f/src/main.py" ] && echo "✅" || echo "❌")
  dock=$([ -f "$f/Dockerfile" ] && echo "✅" || echo "❌")
  agent=$([ -f "$f/AGENT.md" ] && echo "✅" || echo "❌")
  echo "  $name | src:$src | main:$main | docker:$dock | agent:$agent"
done

echo "=== DOCKER ==="
docker compose ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null

echo "=== PORT HEALTH ==="
for e in "8000:gateway" "8001:auth" "8004:billing" "8085:terminal-be" \
         "9003:ai-orch" "8106:signal" "8111:realtime" "8110:mt5-ws" \
         "3000:frontend" "6379:redis" "5432:postgres"; do
  p=${e%:*}; s=${e#*:}
  up=$(curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" || echo 0)
  [ "$up" -gt 0 ] && echo "  ✅ $s :$p" || echo "  ❌ $s :$p"
done

echo "=== GIT ==="
cd ~/goldenaistrategy && git log --oneline -5 2>/dev/null
git status --short 2>/dev/null

echo "=== EXISTING FILES ==="
ls ~/goldenaistrategy/ORCHESTRATOR.md 2>/dev/null && echo "ORCHESTRATOR.md: exists" || echo "ORCHESTRATOR.md: missing"
ls ~/goldenaistrategy/divisions/ 2>/dev/null || echo "divisions/: missing"
ls ~/goldenaistrategy/gas-terminal.sh 2>/dev/null && echo "gas-terminal.sh: exists" || echo "gas-terminal.sh: missing"

echo "=== RESOURCES ==="
free -h | grep Mem && df -h / | tail -1
```

---

## PHASE 1 — ORCHESTRATOR.md

Create: `~/goldenaistrategy/ORCHESTRATOR.md`

```markdown
# ORCHESTRATOR.md — Golden AI Strategy
# Master Brain · WIN 0 · Always Active
# Owner: Muhamad Ridwanjr

## IDENTITY
Project : Golden AI Strategy — SaaS AI Trading Platform
Owner   : Muhamad Ridwanjr (mridwan3101)
Role    : Orchestrator (scan · decide · assign · build parallel)
Window  : tmux WIN 0 (permanent)
Partner : WORKER (1 floating agent, WIN 1-6)
Sync    : tasks/todo.md ← shared board
Stack   : FastAPI · React19/Vite · Redis · PostgreSQL
AI Route: OpenRouter (4 models per plan) — NOT direct Anthropic API
Auth    : Claude Code CLI browser auth | NEVER set ANTHROPIC_API_KEY

## RULES (Boris Cherny / Anthropic Best Practices)
1. PLAN FIRST — 3+ steps → write plan to tasks/todo.md before coding
2. PARALLEL SMART — assign WORKER zero-dependency-conflict tasks
3. SELF-IMPROVE — Ridwan correction → update tasks/lessons.md immediately
4. VERIFY DONE — done = curl OK + docker healthy + logs clean
5. ELEGANT — "ada yang lebih elegant?" before every submit
6. AUTONOMOUS — bug report → scan logs → fix → done. No hand-holding.
7. NO LAZY — complete code, no placeholders, no truncation
8. TOKEN EFFICIENT — read CLAUDE_MINI.md for quick ref

## ON SESSION START
```bash
unset ANTHROPIC_API_KEY
echo "=== ORCHESTRATOR SCAN ===" && date
for e in "8000:gateway" "8004:billing" "9003:ai-orch" "8085:terminal-be" \
         "8106:signal" "8111:realtime" "8110:mt5-ws" "3000:frontend"; do
  p=${e%:*}; s=${e#*:}
  up=$(curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" || echo 0)
  [ "$up" -gt 0 ] && echo "  ✅ $s :$p" || echo "  ❌ $s :$p"
done
docker compose logs --since=1h 2>/dev/null | grep -iE "error|fatal" | tail -10
cat ~/goldenaistrategy/tasks/todo.md
cat ~/goldenaistrategy/tasks/lessons.md
```
After scan → report to Ridwan + write WORKER BRIEF to todo.md + start own task.

## PARALLEL RULES
SAFE (no dependency):
  ✅ gateway + frontend | ✅ billing + signal | ✅ auth + mt5-ws

NEVER parallel:
  ❌ redis + anything | ❌ billing + ai-orch | ❌ signal + realtime-hub

## WORKER BRIEF FORMAT (write to tasks/todo.md)
```
## WORKER BRIEF — [datetime]
Window  : WIN [N] ([division])
Service : [name] :[port]
Task    : [what to build — be specific]
Context : divisions/[DIVISION]_MANAGER.md
Done    : curl localhost:[port]/health → {"status":"ok"}
```

## LIMIT PROTOCOL
```bash
cat >> ~/goldenaistrategy/tasks/todo.md << EOF
## ⚡ CHECKPOINT — $(date)
Engine     : [claude/aider/kimi/deepseek]
My task    : [service being built]
Progress   : [last step completed]
Files done : [list]
Next step  : [exact next action]
Resume     : bash ~/goldenaistrategy/gas-terminal.sh → pick 1
EOF
```

## INTER-SERVICE DEPS
redis → ALL | postgres → auth,billing,signal,journal
gateway → frontend,EA | billing → ai-orch
signal → realtime → frontend-WS | mt5-ws → data pipeline

## DIVISION WINDOWS
WIN 0 ORCHESTRATOR | WIN 1 ENGINEERING | WIN 2 DATA
WIN 3 TRADING | WIN 4 PLATFORM | WIN 5 DEVOPS | WIN 6 SECURITY
```

---

## PHASE 2 — 6 DIVISION MANAGER FILES

Create folder: `~/goldenaistrategy/divisions/`

### divisions/ENGINEERING_MANAGER.md
```markdown
# ENGINEERING_MANAGER.md — Engineering Division
# WIN 1 | Services: gateway · terminal · frontend · web

## SERVICES
gas-gateway-api       :8000  ← CRITICAL entry point
gas-terminal-backend  :8085  ← CRITICAL frontend data
gas-terminal-frontend :3000  ← CRITICAL UI
gas-web-backend       :8005
gas-term-service      :8205
gas-terminal-service  :8206

## WORKERS
debug_agent · refactor_agent · test_agent · deploy_agent

## AUTO-SCAN
```bash
echo "=== ENGINEERING SCAN ===" && date
for p in 8000 8085 3000 8005; do
  curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" > /dev/null \
    && echo "✅ :$p" || echo "❌ :$p"
done
docker compose logs gas-terminal-backend --tail=20 2>/dev/null
cat ~/goldenaistrategy/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## FRONTEND RULES (NEVER CHANGE)
bg:#0a0b0f · surface:#0d0e12 · accent:yellow-400
Fonts: Syne(display) · JetBrains Mono(mono) · DM Sans(body)
Base layout: kode.md — extend only, never replace

## GATEWAY RULES
- Single entry point for ALL traffic
- JWT validation on every request
- Rate limit: 60 req/min per user
- Proxy /terminal/* → terminal-backend:8085
- EA endpoint: /v1/ea/* with X-EA-Token header

## DONE = curl OK + docker healthy + no console errors + todo.md ✅
```

### divisions/DATA_MANAGER.md
```markdown
# DATA_MANAGER.md — Data Division
# WIN 2 | Services: MT5 · scrapers · RAG · realtime

## SERVICES
gas-mt5-websocket            :8110  ← CRITICAL (EA connects here)
gas-mt5-data-service         :8100
gas-market-data-processor    internal
gas-data-ingestor            :9604
gas-calendar-news-service    :9601  ← ecocal scraper 05:00 WIB
gas-fundamental-data-service :9603
gas-vector-db                :9004
gas-rag-technical            :9001
gas-rag-macro                :9002
gas-realtime-hub             :8111  ← CRITICAL (WS broadcast)

## WORKERS
data_pipeline_agent · data_cleaning_agent · vector_db_agent
rag_agent · market_data_agent

## AUTO-SCAN
```bash
echo "=== DATA SCAN ===" && date
for p in 8110 8100 9601 9603 9004 9001 9002 8111; do
  curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" > /dev/null \
    && echo "✅ :$p" || echo "❌ :$p"
done
docker logs gas-calendar-news-service --tail=10 2>/dev/null
cat ~/goldenaistrategy/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## DATA FLOW
MT5 EA → mt5-websocket:8110 → market-data-processor
       → data-ingestor:9604 → vector-db:9004 → rag:9001/9002
       → realtime-hub:8111 → frontend WS

## ECOCAL: cron 05:00 WIB → gas-calendar-news-service
```

### divisions/TRADING_MANAGER.md
```markdown
# TRADING_MANAGER.md — Trading Division (Core Product)
# WIN 3 | Services: signal · quant · strategy · indicators

## SERVICES
gas-signal-service    :8106  ← CRITICAL
gas-quant-orch        :9500  ← CRITICAL (composite score)
gas-feature-engine    :9499
gas-regime-detector   :9503
gas-pattern-detector  :9501
gas-indicator-engine  :8203
gas-smc-engine        :8006
gas-strategy-core     :7003
gas-risk-engine       :9511
gas-trend-engine      :9513
gas-correlation       :9512
gas-orderflow         :9514
gas-statarb-engine    :9502
gas-quant-backtester  :9504
gas-screener-service  :9600
gas-tradingplan-service :9602
gas-market-phase      :9510

## WORKERS
strategy_agent · signal_agent · risk_agent
backtest_agent · market_structure_agent

## AUTO-SCAN
```bash
echo "=== TRADING SCAN ===" && date
for p in 8106 9500 9499 9503 9501 8203 9511; do
  curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" > /dev/null \
    && echo "✅ :$p" || echo "❌ :$p"
done
cat ~/goldenaistrategy/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## SIGNAL PIPELINE
indicator:8203 → feature:9499 → regime:9503 → pattern:9501
→ quant-orch:9500 (composite 0-100) → signal:8106 → realtime:8111

## FEATURE CREDITS
ta:3 · signal:3 · risk:3 · calendar:4 · sentiment:5
hybrid:8 · journal:8 · backtesting:20 · scanner:15
```

### divisions/PLATFORM_MANAGER.md
```markdown
# PLATFORM_MANAGER.md — Platform Division (SaaS Layer)
# WIN 4 | Services: auth · billing · user · telegram

## SERVICES
gas-auth-service         :8001  ← CRITICAL
gas-billing-service      :8004  ← CRITICAL REVENUE
gas-user-service         :8002
gas-telegram-bot         :8003
gas-notification-service :8112
gas-alert-engine         :8400
gas-journal-service      :8107
gas-social-service       :8500

## WORKERS
auth_agent · billing_agent · notification_agent · bot_agent · user_agent

## AUTO-SCAN
```bash
echo "=== PLATFORM SCAN ===" && date
for p in 8001 8004 8002 8003 8107 8400; do
  curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" > /dev/null \
    && echo "✅ :$p" || echo "❌ :$p"
done
cat ~/goldenaistrategy/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## BILLING CRITICAL
EVERY AI call → check credits → deduct → call AI (NEVER bypass)
Plans: Essential $2.99/100cr · Plus $5.99/200cr
       Premium $11.99/400cr · Ultimate $19.99/700cr
1 credit = $0.009 AI cost (40% cost, 60% margin)

## MODELS PER PLAN (OpenRouter)
Essential:  deepseek(0.8x) · gpt4o-mini(1x) · grok(1.5x) · gemini-pro(5x)
Plus:       qwen(0.5x) · gemini-flash(1x) · kimi(1.5x) · gemini-pro(4x)
Premium:    gemini-lite(0.7x) · claude-haiku(1x) · gemini-pro(3x) · opus(5x)
Ultimate:   glm5(0.8x) · claude-sonnet(1x) · gpt4o(2x) · claude-opus(3.5x)
```

### divisions/DEVOPS_MANAGER.md
```markdown
# DEVOPS_MANAGER.md — DevOps Division
# WIN 5 | Services: docker · nginx · monitoring · ai-orch

## SERVICES
gas-ai-orchestrator     :9003  ← CRITICAL (OpenRouter routing)
gas-engine-orchestrator :8105
gas-quant-orch          :9500
docker-compose (all services)
nginx-proxy
gas-observability (prometheus/grafana)

## WORKERS
service_monitor_agent · log_analyzer_agent · auto_restart_agent
deploy_agent · docker_agent

## AUTO-SCAN
```bash
echo "=== DEVOPS SCAN ===" && date
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null
docker compose logs --since=30m 2>/dev/null | grep -iE "error|fatal" | tail -15
free -h | grep Mem && df -h / | tail -1
cat ~/goldenaistrategy/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## QUICK COMMANDS
```bash
docker compose restart [service]
docker compose build [service] && docker compose up -d [service]
docker compose logs -f [service] --tail=50
docker stats --no-stream
python3 ~/goldenaistrategy/gas-tools.py  # menu 8
```

## AI ORCHESTRATOR RULES
Every AI call: check billing → get model_id from plan → call OpenRouter
OpenRouter key: from OPENROUTER_API_KEY env var
Retry: 429 → backoff 1s/2s/4s (max 3x) | 400/401 → fail fast
```

### divisions/SECURITY_MANAGER.md
```markdown
# SECURITY_MANAGER.md — Security Division
# WIN 6 | Guards: gateway · auth · billing · telegram

## SERVICES GUARDED
gas-gateway-api   :8000  → rate limit, request filtering
gas-auth-service  :8001  → JWT, sessions, OAuth
gas-billing-service :8004 → payment security
gas-telegram-bot  :8003  → bot token security

## WORKERS
auth_security_agent · api_firewall_agent · intrusion_detection_agent
audit_agent · rate_limit_agent

## AUTO-SCAN
```bash
echo "=== SECURITY SCAN ===" && date
docker logs gas-gateway-api --since=1h 2>/dev/null | grep -iE "401|403|429|blocked" | tail -20
docker logs gas-auth-service --since=1h 2>/dev/null | grep -iE "failed|invalid|expired" | tail -20
cat ~/goldenaistrategy/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## RULES (NON-NEGOTIABLE)
❌ Never hardcode secrets | ❌ Never log API keys
❌ Never expose internal ports (only :8000 public)
❌ Never commit .env to git
✅ JWT expires: 24h | ✅ Rate limit: 60 req/min/user
✅ EA Token: X-EA-Token header | ✅ All secrets: os.getenv()
```

---

## PHASE 3 — GENERATE gas-terminal.sh

Create: `~/goldenaistrategy/gas-terminal.sh`

This is the beautiful interactive terminal launcher.
Copy the EXACT content from the gas-terminal.sh file provided in the bootstrap.

The terminal must have:
- ASCII art header "GOLDEN AI STRATEGY" in coral/amber colors
- "Terminal by Muhamad Ridwanjr" subtitle
- Status bar showing Claude/Aider/Docker health
- Main menu: 1-7 agents + m=model + a=aider + c=claude + s/l/t/g/k/o/h
- Model switcher: Claude Code, Kimi K2.5, DeepSeek V3/R1, Gemini 2.5 Pro, Qwen3, Claude Haiku, Kimi via OR
- Launch Claude Code with --dangerously-skip-permissions
- Launch Aider with correct flags per model source (Moonshot/DeepSeek/OpenRouter)
- Service health display with color-coded status
- Todo viewer with color-coded priorities
- Config editor

Make it chmod +x after creating.

---

## PHASE 4 — GENERATE gas-office.sh

Create: `~/goldenaistrategy/gas-office.sh`

7-window tmux workspace — starts gas-terminal.sh in WIN 0:

```bash
#!/bin/bash
# GOLDEN AI STRATEGY — Office Workspace
# 7 Division Windows

BASE="$HOME/goldenaistrategy"
SESSION="GAS"
unset ANTHROPIC_API_KEY

tmux kill-session -t $SESSION 2>/dev/null
sleep 0.5

# WIN 0: Terminal launcher (auto-start)
tmux new-session -d -s $SESSION -n "0-terminal" -x 220 -y 55
tmux send-keys -t $SESSION:"0-terminal" \
  "cd $BASE && bash gas-terminal.sh" Enter

# Division windows (idle)
wins=(
  "1-engineering:Engineering  | gateway · terminal-be/fe · web"
  "2-data:Data          | mt5-ws · scrapers · rag · realtime"
  "3-trading:Trading      | signal · quant · strategy · risk"
  "4-platform:Platform     | auth · billing · user · telegram"
  "5-devops:DevOps       | docker · nginx · ai-orchestrator"
  "6-security:Security     | firewall · audit · rate-limit"
)

for entry in "${wins[@]}"; do
  wname=${entry%%:*}; label=${entry#*:}
  tmux new-window -t $SESSION -n "$wname"
  tmux send-keys -t $SESSION:"$wname" \
    "cd $BASE && clear && echo '' && printf '\033[38;2;205;95;70m  ═══════════════════════════════════════════════════\033[0m\n' && echo -e '  \033[1m\033[38;2;245;235;215m$label\033[0m' && printf '\033[38;2;205;95;70m  ═══════════════════════════════════════════════════\033[0m\n' && echo '' && echo -e '  \033[2mStatus: STANDBY — waiting for task assignment\033[0m' && echo '' && echo -e '  \033[38;2;80;220;220mActivate: bash gas-terminal.sh → pick division number\033[0m'" Enter
done

tmux select-window -t $SESSION:"0-terminal"

echo ""
printf '\033[38;2;205;95;70m  ╔══════════════════════════════════════════════════════╗\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  \033[1m\033[38;2;245;235;215mGOLDEN AI STRATEGY — Office Open\033[0m                  \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ╠══════════════════════════════════════════════════════╣\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 0  \033[38;2;255;195;0mterminal\033[0m   ← Main launcher (auto-started)     \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 1  engineering                              \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 2  data                                     \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 3  trading                                  \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 4  platform                                 \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 5  devops                                   \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  WIN 6  security                                 \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ╠══════════════════════════════════════════════════════╣\033[0m\n'
printf '\033[38;2;205;95;70m  ║\033[0m  \033[2mCtrl+b [0-6] navigate │ Ctrl+b d detach\033[0m           \033[38;2;205;95;70m║\033[0m\n'
printf '\033[38;2;205;95;70m  ╚══════════════════════════════════════════════════════╝\033[0m\n'
echo ""

tmux attach -t $SESSION
```

---

## PHASE 5 — SUPPORTING FILES

### tasks/todo.md
Generate from scan results. Include:
- Office Status table (UP/DOWN from scan)
- Critical tasks (services DOWN = needs building)
- Worker Brief section (empty, ORCHESTRATOR fills this)
- Done section (services UP = mark done)
- Checkpoint section (empty)

### tasks/lessons.md
```markdown
# GAS — Lessons Learned
# Review every session start

L001: NEVER set ANTHROPIC_API_KEY → breaks Claude Pro quota
L002: Docker inter-service: use service NAME not localhost
L003: Frontend layout = kode.md base — extend never replace
L004: MQL5 functions: prefix GAS_ to avoid built-in conflicts
L005: EVERY AI call → deduct credits via billing FIRST
L006: OpenRouter 429 → backoff 1s/2s/4s max 3 retry
L007: Plan first for 3+ step tasks — write to todo.md
L008: Token limit → checkpoint to todo.md BEFORE stopping
L009: Parallel tasks must have zero dependency conflict
L010: Aider = better for file editing; Claude = better for architecture
```

### CLAUDE_MINI.md
```markdown
# GAS MINI — Quick Reference (token-efficient)
# Full context: ORCHESTRATOR.md

ID: Golden AI Strategy · Owner: Muhamad Ridwanjr · ~/goldenaistrategy/
Stack: FastAPI + React19/Vite + Redis + PostgreSQL + OpenRouter
Auth: claude browser login | NEVER ANTHROPIC_API_KEY

PORTS (Phase 1 critical):
8000=gateway 8001=auth 8004=billing 8085=terminal-be
9003=ai-orch 8106=signal 8111=realtime 8110=mt5-ws
3000=frontend 6379=redis 5432=postgres

RULES: plan→build→verify | parallel=no-deps | checkpoint on limit
BILLING: every AI call → check credits → deduct → call OpenRouter
FRONTEND: bg:#0a0b0f yellow-400 JetBrains-Mono — NEVER CHANGE

DIVISIONS: W1=engineering W2=data W3=trading W4=platform W5=devops W6=security
MODELS: essential=deepseek/gpt4o-mini | plus=qwen/gemini-flash
        premium=haiku/gemini-pro | ultimate=sonnet/gpt4o
1cr=$0.009 | ta:3cr | signal:3cr | sentiment:5cr | backtest:20cr
```

### .claude/settings.json
```json
{
  "permissions": {
    "allow": [
      "Bash(*)", "Read(*)", "Write(*)", "Edit(*)",
      "MultiEdit(*)", "TodoRead(*)", "TodoWrite(*)",
      "WebFetch(*)", "WebSearch(*)", "Glob(*)", "Grep(*)"
    ],
    "deny": []
  }
}
```

### .gitignore additions
```
.gas-agent-config
*.env
.env*
.env.local
gas-terminal.log
tasks/terminal.log
```

---

## PHASE 6 — INSTALL AIDER (if not installed)

```bash
# Check if aider is installed
if ! command -v aider &>/dev/null; then
  echo "Installing aider..."
  pip install aider-chat --break-system-packages 2>/dev/null \
    || pip3 install aider-chat 2>/dev/null \
    || pip install aider-chat --user 2>/dev/null
fi
aider --version 2>/dev/null && echo "✅ Aider ready" || echo "⚠️ Aider install manually: pip install aider-chat"
```

---

## PHASE 7 — MAKE EXECUTABLE + VERIFY

```bash
chmod +x ~/goldenaistrategy/gas-terminal.sh
chmod +x ~/goldenaistrategy/gas-office.sh
chmod 600 ~/goldenaistrategy/.gas-agent-config 2>/dev/null

echo "=== VERIFICATION ==="
ls -la ~/goldenaistrategy/gas-terminal.sh
ls -la ~/goldenaistrategy/gas-office.sh
ls -la ~/goldenaistrategy/ORCHESTRATOR.md
ls -la ~/goldenaistrategy/divisions/
find ~/goldenaistrategy/divisions -name "*.md" | sort
ls -la ~/goldenaistrategy/tasks/
```

---

## PHASE 8 — FINAL REPORT

```
╔═══════════════════════════════════════════════════════════════╗
║  GOLDEN AI STRATEGY — BOOTSTRAP COMPLETE v6.0              ║
║  by Muhamad Ridwanjr                                        ║
╚═══════════════════════════════════════════════════════════════╝

📊 SCAN RESULTS
  Services UP    : [N from scan]
  Services DOWN  : [N from scan]
  Service folders: [N found]

📁 FILES GENERATED
  ✅ ORCHESTRATOR.md              (master brain)
  ✅ divisions/ENGINEERING_MANAGER.md
  ✅ divisions/DATA_MANAGER.md
  ✅ divisions/TRADING_MANAGER.md
  ✅ divisions/PLATFORM_MANAGER.md
  ✅ divisions/DEVOPS_MANAGER.md
  ✅ divisions/SECURITY_MANAGER.md
  ✅ gas-terminal.sh              (beautiful terminal UI)
  ✅ gas-office.sh                (7-window tmux)
  ✅ tasks/todo.md
  ✅ tasks/lessons.md
  ✅ CLAUDE_MINI.md
  ✅ .claude/settings.json

🤖 AGENT SYSTEM
  WIN 0: Terminal launcher → pick agent from menu
  WIN 1: Engineering  (gateway · terminal · frontend)
  WIN 2: Data         (mt5 · scrapers · rag · realtime)
  WIN 3: Trading      (signal · quant · strategy)
  WIN 4: Platform     (auth · billing · telegram)
  WIN 5: DevOps       (docker · nginx · monitoring)
  WIN 6: Security     (firewall · audit)

⚡ MODEL SWITCHING
  Terminal menu → m → pilih:
  Claude Code → Kimi K2.5 → DeepSeek V3 → Gemini 2.5 Pro → Qwen3

🚀 CARA MULAI
  Step 1: nano ~/goldenaistrategy/.gas-agent-config → isi API keys
  Step 2: bash ~/goldenaistrategy/gas-office.sh
          → WIN 0 auto-launch gas-terminal.sh
  Step 3: Pick 1 (ORCHESTRATOR) → auto-scan → mulai build

🔑 API KEYS NEEDED
  Kimi    : platform.moonshot.cn → KIMI_API_KEY
  DeepSeek: platform.deepseek.com → DEEPSEEK_API_KEY
  OpenRouter: sudah ada di config

Siap bro. Buka kantor dengan:
  bash ~/goldenaistrategy/gas-office.sh
```

---

## CONSTRAINTS
- Scan FIRST, generate AFTER — base content on ACTUAL results
- gas-terminal.sh: complete working bash, all functions implemented
- Division MANAGER.md: max 100 lines each
- ORCHESTRATOR.md + CLAUDE_MINI.md: concise
- .gas-agent-config: template with EMPTY api keys (never real keys)
- Verify: bash --norc --noprofile -n ~/goldenaistrategy/gas-terminal.sh (syntax check)