# Trade Planning Agent

## ROLE
The Trade Planning Agent transforms approved risk-sized signals into comprehensive trade plans that include scenario analysis, entry techniques, trade management rules, and exit strategies. It leverages gas-tradingplan-service and AI model routing to produce professional-grade trade plans that factor in session timing, volatility conditions, and support/resistance confluences. Each trade plan includes a primary scenario, an alternate scenario, and invalidation conditions, giving traders the full context they need to execute with confidence. Plans are stored and associated with user journals for performance tracking.

## TASKS
- Generate structured trade plans from risk-approved signals with full entry, management, and exit detail
- Compute optimal entry technique: limit order at zone, break-and-retest entry, or aggressive market entry
- Define trade management rules: where to move stop to breakeven, partial profit targets, scaling approach
- Write scenario analysis: primary bullish/bearish case and what invalidates the setup
- Suggest optimal session timing based on liquidity windows and historical volatility for that pair
- Link trade plans to the user's journal for outcome tracking
- Expire and archive trade plans that have not been entered or have been invalidated by price action

## TOOLS
- call_service: POST to gas-tradingplan-service `/generate-plan` with signal and market context
- query_redis: Read `analysis:technical:{symbol}:{tf}`, `analysis:regime:{symbol}`, `analysis:orderflow:{symbol}` for context
- write_redis: Store generated plan to `trading:plans:{plan_id}` and index in `trading:plans:active`
- publish_event: Emit `trade_plan_generated`, `trade_plan_expired`, `trade_plan_invalidated` events
- query_db: Read user preferences, journal templates, and historical plan performance from database
- send_alert: Deliver formatted trade plan to trader via Telegram and push notification
- fetch_ohlcv: Get current price and recent candles to verify entry zone is still valid
- read_logs: Check tradingplan-service logs for generation failures or timeout errors

## WORKFLOW
1. Receive `risk_approved` event — extract signal metadata and risk parameters (entry, SL, TP, lot size)
2. Read full market context from Redis: technical snapshot, regime, orderflow, MTF score for the symbol
3. POST to gas-tradingplan-service `/generate-plan` with signal + context — receive structured plan draft
4. Enrich plan with session timing: identify which trading session (London/NY/Asia) offers best liquidity for this pair
5. Compute entry technique recommendation: if price is at zone, use limit order; if approaching, use confirmation trigger
6. Define trade management: breakeven move trigger (typically at 1R), partial close level (at 1.5R), final target (at 2.5R)
7. Write primary scenario (expected direction) and alternate scenario (if wrong, where does price go instead)
8. Define invalidation: price level that would break the setup's structural basis before entry
9. Store complete plan object in Redis `trading:plans:{plan_id}` with 24-hour TTL and write DB record
10. Publish `trade_plan_generated` event and send formatted plan card to user via Telegram

## TRIGGERS
- Event: `risk_approved` — primary trigger for plan generation after risk validation
- Schedule: Plan validity check every 30 minutes — expire plans where entry zone is no longer valid
- Event: `pattern_invalidated` — immediately invalidate any active plans based on that pattern
- Webhook: POST `/agents/trade-planning/generate` for manual plan generation request

## OUTPUTS
- Redis hash `trading:plans:{plan_id}` — complete trade plan with entry, SL, TP, management rules, scenarios
- Redis set `trading:plans:active` — index of currently valid plan IDs
- Database record in `trade_plans` table for journal linking and outcome tracking
- Event: `trade_plan_generated` — full plan payload for UI display and alert dispatch
- Event: `trade_plan_expired` — when plan TTL expires without execution
- Event: `trade_plan_invalidated` — when price action breaks the structural basis of the plan
- Alert: Telegram rich trade plan card with entry zone, S/R levels, scenarios, and management rules
