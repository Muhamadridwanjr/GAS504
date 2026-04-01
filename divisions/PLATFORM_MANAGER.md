# PLATFORM_MANAGER.md — Platform Division (SaaS Layer)
# WIN 4 | Services: auth · billing · user · telegram

## SERVICES
gas-auth-service         :8001  ← CRITICAL (healthy ✅)
gas-billing-service      :8004  ← CRITICAL REVENUE (healthy ✅)
gas-user-service         :8002  (healthy ✅)
gas-telegram-bot         :8003  (healthy ✅)
gas-notification-service :8112  (healthy ✅)
gas-alert-engine         :8400  (up ✅)
gas-journal-service      :8107  (healthy ✅)
gas-social-service       :8500
gas-web-backend          :8005

## WORKERS
auth_agent · billing_agent · notification_agent · bot_agent · user_agent

## AUTO-SCAN
```bash
echo "=== PLATFORM SCAN ===" && date
for p in 8001 8004 8002 8003 8107 8400; do
  curl -s --max-time 1 localhost:$p/health 2>/dev/null | grep -c "ok" > /dev/null \
    && echo "✅ :$p" || echo "❌ :$p"
done
cat /root/gasstrategyai/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## BILLING CRITICAL
EVERY AI call → check credits → deduct → call AI (NEVER bypass)
Plans: Essential $2.99/100cr · Plus $5.99/200cr
       Premium $11.99/400cr · Ultimate $19.99/700cr
1 credit = $0.009 AI cost (40% cost, 60% margin)
Admin: JWT role=admin → skip credit deduction + Redis auto-set ultimate

## MODELS PER PLAN (OpenRouter)
Essential:  deepseek(0.8x) · gpt4o-mini(1x) · grok(1.5x) · gemini-pro(5x)
Plus:       qwen(0.5x) · gemini-flash(1x) · kimi(1.5x) · gemini-pro(4x)
Premium:    gemini-lite(0.7x) · claude-haiku(1x) · gemini-pro(3x) · opus(5x)
Ultimate:   glm5(0.8x) · claude-sonnet(1x) · gpt4o(2x) · claude-opus(3.5x)
