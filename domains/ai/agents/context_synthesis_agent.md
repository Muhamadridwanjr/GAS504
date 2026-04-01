# Context Synthesis Agent

## ROLE
The Context Synthesis Agent assembles the complete contextual payload required for high-quality AI feature responses on the GAS platform. It gathers and harmonizes data from multiple sources — live market state from Redis, retrieved knowledge from the RAG pipeline, user trading history from the database, regime context from the analysis domain, and conversation history for continuity — and synthesizes these into a structured, token-efficient context object that can be directly consumed by the model routing agent. This agent is responsible for ensuring that every AI response has access to the most relevant and current information without exceeding model context windows.

## TASKS
- Assemble per-feature context bundles by pulling from market data cache, RAG retrieval, and user history
- Compress and prioritize context components to fit within model token budget (default 8000 tokens)
- Maintain conversation context for multi-turn AI sessions (psychology coach, mentor mode)
- Enrich context with real-time market data: current price, daily change, recent OHLCV, active signals
- Include user-specific context: account performance, open positions, recent trades, subscription tier
- Build feature-specific context templates: each of the 18 AI features has its own context schema
- Cache assembled context objects for rapid retrieval when the same feature is called for the same symbol

## TOOLS
- query_redis: Read live market data, active signals, regime classifications, MTF scores for context assembly
- query_db: Fetch user trade history, journal entries, account stats, and conversation history
- call_service: POST to gas-ai-orchestrator `/context/assemble` for complex multi-source context building
- embed_text: Compress long text context sections via summarization before token budget check
- write_redis: Cache assembled context in `ai:context:{feature}:{user_id}:{symbol}` with 2-minute TTL
- publish_event: Emit `context_assembled`, `context_truncated`, `context_assembly_failed` events
- fetch_ohlcv: Pull recent OHLCV data for technical context sections requiring current price action
- metrics_reader: Monitor context assembly latency and token utilization statistics

## WORKFLOW
1. Receive context assembly request with feature_type, user_id, symbol, and timeframe
2. Check Redis `ai:context:{feature}:{user_id}:{symbol}` — return cached context if within TTL
3. Identify required context components from feature schema: market_data, regime, signals, rag_context, user_history
4. In parallel, fetch: (a) market prices/indicators from Redis, (b) regime and MTF from Redis, (c) active signals
5. Query database for user-specific data: recent closed trades (last 10), open positions, account equity, XP level
6. If conversation history needed (psychology/mentor), read last 5 turns from `ai:conversation:{user_id}:{feature}` Redis list
7. Retrieve RAG context from `rag:context:{query_id}` placed by rag_query_agent
8. Count total tokens across all context components — if over budget (8000 tokens), apply compression hierarchy:
   - First compress: conversation history (keep last 3 turns)
   - Then compress: knowledge chunks (keep top 3 instead of 5)
   - Finally compress: trade history (summarize instead of listing)
9. Assemble final context object with structured sections and write to Redis `ai:context:{feature}:{user_id}:{symbol}`
10. Publish `context_assembled` event with context reference ID for model_routing_agent to consume

## TRIGGERS
- Event: `rag_query_completed` — primary trigger after retrieval is done, context assembly is the next pipeline step
- Event: `ai_feature_requested` — direct trigger for features that skip RAG and go straight to context assembly
- Webhook: POST `/agents/context-synthesis/assemble` for direct context assembly requests

## OUTPUTS
- Redis hash `ai:context:{feature}:{user_id}:{symbol}` — complete structured context object with token count
- Event: `context_assembled` — context reference ID passed to model_routing_agent for inference
- Event: `context_truncated` — published when compression was required, with before/after token counts
- Event: `context_assembly_failed` — error details when a required data source is unavailable
- Prometheus: `gas_context_assembly_latency_ms`, `gas_context_token_utilization_pct` gauges
