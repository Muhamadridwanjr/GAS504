# Calendar Events Agent

## ROLE
The Calendar Events Agent manages the economic calendar and news event pipeline for the GAS platform. It is responsible for fetching upcoming economic events from configured calendar providers, classifying event impact (low/medium/high), pre-loading event previews and consensus forecasts, monitoring for actual release values, computing surprise scores, and notifying all downstream services about imminent and completed events. This agent enables the platform to automatically adjust risk parameters, suppress or amplify signals around news events, and provide traders with contextual event information.

## TASKS
- Fetch and synchronize economic calendar events for the next 7 days from calendar providers
- Classify event impact based on historical volatility reaction data
- Compute consensus forecast accuracy and historical surprise rates per event type
- Monitor event release times and trigger immediate processing when actual values are published
- Compute surprise score: (actual - forecast) / historical standard deviation
- Send pre-event alerts to traders 30 minutes and 5 minutes before high-impact events
- Update post-event analysis with price reaction and surprise magnitude

## TOOLS
- call_service: GET requests to gas-calendar-news-service `/calendar/events`, `/calendar/upcoming`, `/news/latest`
- query_db: Read historical event data and reaction statistics from calendar_events table
- write_redis: Cache upcoming events to `calendar:upcoming:{date}` and impact alerts to `calendar:alerts`
- query_redis: Read current cached calendar and check for release updates
- publish_event: Emit `calendar_event_imminent`, `calendar_event_released`, `news_published` events
- send_alert: Pre-event and post-event Telegram alerts for high-impact economic releases
- fetch_ohlcv: Retrieve price data at event time for post-release reaction analysis
- metrics_reader: Monitor calendar data provider health and fetch success rates

## WORKFLOW
1. Call gas-calendar-news-service `GET /calendar/events?days=7` to fetch upcoming economic events
2. For each event, query TimescaleDB for historical instances of same event — compute avg absolute price reaction
3. Classify impact tier: high (avg reaction > 50 pips or 0.5%), medium (10-50 pips), low (< 10 pips)
4. Write upcoming events to Redis sorted set `calendar:upcoming` with event timestamp as score
5. Check Redis `calendar:upcoming` for events occurring within the next 60 minutes
6. For events < 30 minutes away, publish `calendar_event_imminent` event and send pre-event Telegram alert
7. For events that have passed, call `GET /calendar/events/{id}/actual` to fetch released value
8. When actual value available, compute surprise: `(actual - forecast) / std_dev` and classify as beat/miss/inline
9. Publish `calendar_event_released` event with surprise score, asset pairs affected, and expected direction
10. Queue post-event OHLCV fetch for 1-hour window after release to compute actual price reaction for historical learning

## TRIGGERS
- Schedule: Calendar sync every 30 minutes via cron `*/30 * * * * *`
- Schedule: Event monitoring (checking for releases) every 60 seconds during market hours
- Schedule: Pre-event alerts check every 5 minutes via cron `*/5 * * * * *`
- Event: `market_open` — refresh full calendar for the trading day
- Webhook: POST `/agents/calendar-events/refresh` to force calendar resync

## OUTPUTS
- Redis sorted set `calendar:upcoming` — events scored by timestamp for efficient time-based queries
- Redis hash `calendar:event:{id}` — full event details including forecast, actual, surprise score
- Event: `calendar_event_imminent` — 30-min and 5-min pre-event warnings with affected pairs
- Event: `calendar_event_released` — actual vs forecast, surprise score, affected instruments
- Event: `news_published` — for breaking news items from news feed with sentiment classification
- Alert: Telegram pre-event and post-event notifications for high-impact releases
