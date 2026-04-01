# GAS — Lessons Learned
# Review every session start | Updated: 2026-03-15

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
L011: payments.py → use content=body JSON, not data=json.dumps (form-encoded = 502)
L012: Admin role in JWT → dependencies.py extracts → skip credit deduction
L013: pytz removed → use stdlib datetime.timezone(timedelta(hours=7))
L014: Base dir is /root/gasstrategyai/ NOT ~/goldenaistrategy/
L015: gateway :8000 internal-only — nginx-proxy handles public SSL
L016: gas-ai-orchestrator :9003 DOWN — check on every session start
