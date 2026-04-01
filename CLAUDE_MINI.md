# GAS MINI — Quick Reference (token-efficient)
# Full context: ORCHESTRATOR.md

ID: Golden AI Strategy · Owner: Muhamad Ridwanjr · /root/gasstrategyai/
Stack: FastAPI + React19/Vite + Redis + PostgreSQL + OpenRouter
Auth: claude browser login | NEVER ANTHROPIC_API_KEY

PORTS (critical):
8000=gateway 8001=auth 8004=billing 8085=terminal-be
9003=ai-orch 8106=signal 8111=realtime 8110=mt5-ws
3000=frontend 6379=redis 5432=postgres
9612=binance 8006=smc-engine 8010=market-data 7003=strategy-core

RULES: plan→build→verify | parallel=no-deps | checkpoint on limit
BILLING: every AI call → check credits → deduct → call OpenRouter
FRONTEND: bg:#0a0b0f yellow-400 JetBrains-Mono — NEVER CHANGE
AUTH: JWT in localStorage as gas-token | Bearer header | 24h expiry

DIVISIONS: W1=engineering W2=data W3=trading W4=platform W5=devops W6=security

MODELS PER PLAN (OpenRouter):
essential:  deepseek(0.8x) · gpt4o-mini(1x) · grok(1.5x) · gemini-pro(5x)
plus:       qwen(0.5x) · gemini-flash(1x) · kimi(1.5x) · gemini-pro(4x)
premium:    gemini-lite(0.7x) · claude-haiku(1x) · gemini-pro(3x) · opus(5x)
ultimate:   glm5(0.8x) · claude-sonnet(1x) · gpt4o(2x) · claude-opus(3.5x)

CREDITS: 1cr=$0.009 | ta:3cr | signal:3cr | risk:3cr | calendar:4cr
         sentiment:5cr | hybrid:8cr | journal:8cr | scanner:15cr | backtest:20cr

PLANS: Essential $2.99/100cr · Plus $5.99/200cr
       Premium $11.99/400cr · Ultimate $19.99/700cr

18 AI FEATURES:
Essential+: technical, signal, alert, session
Plus+:      + correlation, fundamental, calendar, sentiment, risk
Premium+:   + hybrid, drawdown, briefing, psychology, journal, propfirm
Ultimate:   + scanner(15cr), backtesting(20cr), mentor(10cr)
