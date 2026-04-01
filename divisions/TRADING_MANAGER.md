# TRADING_MANAGER.md — Trading Division (Core Product)
# WIN 3 | Services: signal · quant · strategy · indicators

## SERVICES
gas-signal-service    :8106  ← CRITICAL (healthy ✅)
gas-quant-orch        :9500  ← CRITICAL (composite score) (healthy ✅)
gas-feature-engine    :9499
gas-regime-detector   :9503
gas-pattern-detector  :9501
gas-indicator-engine  :8203  (up ✅)
gas-smc-engine        :8006  (healthy ✅)
gas-strategy-core     :7003  (up ✅)
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
cat /root/gasstrategyai/tasks/todo.md | grep -A8 "WORKER BRIEF"
```

## SIGNAL PIPELINE
indicator:8203 → feature:9499 → regime:9503 → pattern:9501
→ quant-orch:9500 (composite 0-100) → signal:8106 → realtime:8111

## FEATURE CREDITS
ta:3cr · signal:3cr · risk:3cr · calendar:4cr · sentiment:5cr
hybrid:8cr · journal:8cr · backtesting:20cr · scanner:15cr · mentor:10cr
