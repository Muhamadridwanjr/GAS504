# SECURITY_MANAGER.md — Security Division
# WIN 6 | Guards: gateway · auth · billing · telegram

## SERVICES GUARDED
gas-gateway-api   :8000  → rate limit, request filtering (healthy ✅)
gas-auth-service  :8001  → JWT, sessions, OAuth (healthy ✅)
gas-billing-service :8004 → payment security (healthy ✅)
gas-telegram-bot  :8003  → bot token security (healthy ✅)

## WORKERS
auth_security_agent · api_firewall_agent · intrusion_detection_agent
audit_agent · rate_limit_agent

## AUTO-SCAN
```bash
echo "=== SECURITY SCAN ===" && date
docker logs gas-gateway-api --since=1h 2>/dev/null | grep -iE "401|403|429|blocked" | tail -20
docker logs gas-auth-service --since=1h 2>/dev/null | grep -iE "failed|invalid|expired" | tail -20
cat /root/gasstrategyai/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## RULES (NON-NEGOTIABLE)
❌ Never hardcode secrets | ❌ Never log API keys
❌ Never expose internal ports (only :8000 public via nginx)
❌ Never commit .env to git
✅ JWT expires: 24h | ✅ Rate limit: 60 req/min/user
✅ EA Token: X-EA-Token header | ✅ All secrets: os.getenv()
✅ Admin: role in JWT, checked in dependencies.py
✅ Payments: content=body JSON (not form-encoded)
