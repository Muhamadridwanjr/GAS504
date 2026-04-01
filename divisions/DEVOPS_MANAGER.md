# DEVOPS_MANAGER.md — DevOps Division
# WIN 5 | Services: docker · nginx · monitoring · ai-orch

## SERVICES
gas-ai-orchestrator     :9003  ← CRITICAL (OpenRouter routing)
gas-engine-orchestrator :8105  (up ✅)
gas-quant-orch          :9500  (healthy ✅)
gas-chart-service       :9700  (healthy ✅)
docker-compose          /root/gasstrategyai/docker-compose.yml
nginx-proxy             /root/gasstrategyai/nginx-proxy/
certbot                 (up ✅, SSL renewal)
gas-observability       (prometheus/grafana — to build)

## WORKERS
service_monitor_agent · log_analyzer_agent · auto_restart_agent
deploy_agent · docker_agent

## AUTO-SCAN
```bash
echo "=== DEVOPS SCAN ===" && date
cd /root/gasstrategyai
docker compose ps --format "table {{.Name}}\t{{.Status}}" 2>/dev/null
docker compose logs --since=30m 2>/dev/null | grep -iE "error|fatal" | tail -15
free -h | grep Mem && df -h / | tail -1
cat /root/gasstrategyai/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## QUICK COMMANDS
```bash
cd /root/gasstrategyai
docker compose restart [service]
docker compose build [service] && docker compose up -d [service]
docker compose logs -f [service] --tail=50
docker stats --no-stream
```

## AI ORCHESTRATOR RULES
Every AI call: check billing → get model_id from plan → call OpenRouter
OpenRouter key: from OPENROUTER_API_KEY env var
Retry: 429 → backoff 1s/2s/4s (max 3x) | 400/401 → fail fast
gas-ai-orchestrator :9003 — currently DOWN, needs attention
