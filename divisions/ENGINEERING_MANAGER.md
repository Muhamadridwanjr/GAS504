# ENGINEERING_MANAGER.md — Engineering Division
# WIN 1 | Services: gateway · terminal · frontend · web

## SERVICES
gas-gateway-api       :8000  ← CRITICAL entry point (healthy ✅)
gas-terminal-backend  :8085  ← CRITICAL frontend data (healthy ✅)
gas-terminal-frontend :3000  ← CRITICAL UI (up ✅)
gas-web-backend       :8005
gas-term-service      :8205  (healthy ✅)
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
docker compose -f /root/gasstrategyai/docker-compose.yml \
  logs gas-terminal-backend --tail=20 2>/dev/null
cat /root/gasstrategyai/tasks/todo.md | grep -A8 "WORKER BRIEF"
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
