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
Base    : /root/gasstrategyai/
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
cat /root/gasstrategyai/tasks/todo.md
cat /root/gasstrategyai/tasks/lessons.md
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
cat >> /root/gasstrategyai/tasks/todo.md << EOF
## ⚡ CHECKPOINT — $(date)
Engine     : [claude/aider/kimi/deepseek]
My task    : [service being built]
Progress   : [last step completed]
Files done : [list]
Next step  : [exact next action]
Resume     : bash /root/gasstrategyai/gas-terminal.sh → pick 1
EOF
```

## INTER-SERVICE DEPS
redis → ALL | postgres → auth,billing,signal,journal
gateway → frontend,EA | billing → ai-orch
signal → realtime → frontend-WS | mt5-ws → data pipeline

## DIVISION WINDOWS
WIN 0 ORCHESTRATOR | WIN 1 ENGINEERING | WIN 2 DATA
WIN 3 TRADING | WIN 4 PLATFORM | WIN 5 DEVOPS | WIN 6 SECURITY
