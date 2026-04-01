# Model Routing Agent

## ROLE
The Model Routing Agent is the intelligent dispatcher for all AI inference requests in the GAS platform, selecting the optimal language model for each request based on task complexity, required reasoning depth, cost constraints, and current model availability. It maintains a routing policy that maps AI feature types to model tiers: complex multi-step reasoning tasks (psychology coaching, market briefing, mentor sessions) route to claude-sonnet-4-6, high-throughput feature-specific tasks (technical summary, signal explanation) route to claude-haiku, and local Ollama models handle privacy-sensitive or ultra-low-latency requests. The agent tracks per-model usage, costs, and performance to continuously refine routing decisions.

## TASKS
- Route incoming AI inference requests to the optimal model based on task type and complexity
- Maintain fallback routing: if primary model is unavailable, route to next tier automatically
- Track per-model usage, latency, and cost in Redis for budget management and optimization
- Apply circuit breaker pattern: if a model has > 5 consecutive failures, disable and reroute for 5 minutes
- Cache model responses for identical or near-identical requests to reduce API costs
- Monitor model response quality via user feedback signals and adjust routing weights
- Enforce per-user credit budget routing: downgrade model tier when user credit balance is low

## TOOLS
- call_service: HTTP calls to Anthropic API for claude-sonnet-4-6 and claude-haiku, and local Ollama endpoint
- query_redis: Read model routing config `ai:routing:config`, circuit breaker state, and response cache
- write_redis: Update model usage counters, cache responses in `ai:response_cache:{request_hash}`, set circuit breaker keys
- query_db: Read user credit balance and subscription tier for routing tier determination
- publish_event: Emit `inference_completed`, `model_fallback_triggered`, `circuit_breaker_opened` events
- send_alert: Alert when a model enters circuit-breaker state or API costs exceed daily budget threshold
- metrics_reader: Read Anthropic API latency and error rate metrics from gas-observability
- read_logs: Monitor gas-ai-orchestrator logs for model API errors and timeout patterns

## WORKFLOW
1. Receive inference request with feature_type, user_id, prompt, and retrieved context from rag_query_agent
2. Look up routing policy for feature_type from Redis `ai:routing:config` — identifies primary model tier
3. Read user subscription tier and credit balance from database — downgrade to haiku if credits < 50
4. Check circuit breaker state: Redis `ai:circuit_breaker:{model}` — if open, skip to next model tier
5. Check response cache: compute hash of (feature_type + key_inputs) and look up `ai:response_cache:{hash}`
6. If cache hit and TTL valid (same-day for briefing, 5min for technical), return cached response directly
7. If cache miss, call selected model API with constructed prompt (system prompt + context + user query)
8. Record inference latency, input/output token counts, and estimated cost to Redis `ai:usage:{model}:{date}`
9. If model call fails, increment failure counter — if failures >= 5 in 10 minutes, set circuit breaker and reroute
10. Cache successful response with appropriate TTL in `ai:response_cache:{hash}` and publish `inference_completed` event

## TRIGGERS
- Event: `rag_query_completed` — primary trigger after context retrieval is ready
- Event: `ai_feature_requested` (fast path) — for cached/simple requests that don't need full RAG
- Schedule: Model health check and routing policy refresh every 5 minutes
- Event: `circuit_breaker_opened` — immediately trigger routing policy update to reroute traffic

## OUTPUTS
- AI inference response: returned via event `inference_completed` with model used, latency, token counts
- Redis `ai:response_cache:{hash}` — cached responses with TTL for cost reduction
- Redis `ai:usage:{model}:{date}` — per-model daily usage tracking for budget management
- Event: `inference_completed` — model output, latency, token usage, and routing decision metadata
- Event: `model_fallback_triggered` — when primary model fails and fallback model is used
- Event: `circuit_breaker_opened` — model taken out of rotation due to consecutive failures
- Alert: Telegram alert when daily AI API cost exceeds budget threshold or circuit breaker opens
