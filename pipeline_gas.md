# GAS Strategy AI — Full Pipeline Documentation

> Last updated: 2026-03-24
> Platform: GAS (Golden AI Strategy) — Multi-service AI Trading Terminal

---

## Arsitektur Umum

```
User Browser
    │
    └── nginx-proxy (SSL :443)
            │
            ├── /auth/v1/*         → gas-auth-service:8001
            ├── /terminal/*        → gas-terminal-backend:8085
            ├── /web/api/v1/*      → gas-web-backend:8005
            └── static             → gas-terminal-frontend (React/Vite, nginx :3000)
```

---

## 1. 📈 ForexAI Pipeline

```
User klik "Analisa" / "Sinyal"
        │
        ├── [Live Prices] fetchOverview()
        │       │
        │       └── GET /terminal/overview
        │               ↓
        │           gas-terminal-backend:8085
        │               ↓ untuk setiap pair (22 pairs)
        │           ├── Redis → market:{SYMBOL}          ← MT5 EA push tick (gas-mt5-websocket:8110)
        │           ├── fallback: gas-binance-service:9612  (crypto BTC/ETH only)
        │           └── fallback: Redis → market:last:{SYMBOL}  (stale cache 24h)
        │           + GET gas-calendar-news-service:9601/news/latest
        │           + GET gas-fundamental-data-service:9603/fundamental/macro
        │           + GET gas-strategy-core:7003/v1/analysis/briefing
        │           return: prices 22 pairs + market status + news + macro + AI briefing
        │
        ├── [Technical Analysis] callAIFeature('technical')
        │       │
        │       └── POST /web/api/v1/analysis/technical
        │               ↓
        │           gas-web-backend:8005
        │           → JWT auth → cek plan user
        │           → deduct credits (2 cr)
        │               ↓
        │           POST gas-strategy-core:7003/v1/analysis/technical
        │               ↓
        │           Redis → get_ohlc_smart({SYMBOL}, timeframe)  ← MT5 EA OHLC
        │           + compute: EMA/RSI/MACD/Bollinger/ATR/ADX
        │           + SMC analysis: BOS, ChoCH, OB, FVG, Liquidity
        │           + DXY correlation check (multi-TF)
        │           + DeepSeek AI via OpenRouter
        │           return: signal, confidence, reason, entry/sl/tp, trading plan
        │
        └── [Signal] callAIFeature('signal')
                │
                └── POST /web/api/v1/analysis/signal
                        ↓
                    gas-web-backend:8005
                    → JWT auth → cek plan user
                    → cek model tier (basic/pro/ultra/gpt/agent)
                    → deduct credits (3–15 cr tergantung tier)
                        ↓
                    POST gas-strategy-core:7003/v1/analysis/signal
                        ↓
                    Redis → OHLC multi-TF matrix (H4/H1/M15/M5) ← MT5
                    + DXY inverse correlation logic
                    + Fear & Greed Index (external: alternative.me API)
                    + COT Gold data (external: CFTC/Quandl)
                    + DeepSeek / GPT-4o / Claude via OpenRouter
                        ↓
                    return: full signal + entry/sl/tp + trading plan + psychology

```

### Services Involved — ForexAI
| Service | Port | Fungsi |
|---|---|---|
| `gas-terminal-backend` | 8085 | BFF aggregator, price hub |
| `gas-web-backend` | 8005 | Auth gate + credit deduction |
| `gas-strategy-core` | 7003 | Core AI engine (DeepSeek/GPT/Claude) |
| `gas-mt5-websocket` | 8110 | Tick receiver dari MT5 EA |
| `gas-calendar-news-service` | 9601 | Economic calendar + news feed |
| `gas-fundamental-data-service` | 9603 | Macro data scraper |
| `gas-redis` | 6379 | OHLC cache + tick cache |

### External Data Sources — ForexAI
| Source | Data |
|---|---|
| MT5 EA (GAS_AutoTrader.mq5) | Live tick + OHLC semua pairs |
| alternative.me | Crypto Fear & Greed Index |
| CFTC/Quandl | COT (Commitment of Traders) Gold |
| OpenRouter | LLM inference (DeepSeek/GPT-4o/Claude/Gemini) |

---

## 2. 🟡 BinanceAI Pipeline

```
Halaman load → WebSocket connect
        │
        ├── [Live Tickers — Real-time]
        │       WebSocket /terminal/ws/binance
        │               ↓
        │           gas-terminal-backend:8085 (WS handler)
        │               ↓ polling tiap 2 detik
        │           GET gas-binance-service:9612/tickers?symbols=BTC/USDT,ETH/USDT,...
        │               ↓
        │           CCXT library → Binance Public REST API
        │           return: price, change24h%, volume, bid, ask, high24h, low24h
        │
        ├── [Fallback REST] fetchBinanceTickers()
        │       │
        │       └── GET /terminal/binance/tickers?symbols=...
        │               ↓ gas-terminal-backend:8085
        │               ↓ gas-binance-service:9612/tickers
        │               ↓ CCXT → api.binance.com
        │
        ├── [Scanner] fetchScanner()
        │       │
        │       └── GET /terminal/binance/tickers?symbols={SCANNER_PAIRS}
        │               ↓ sama seperti tickers tapi untuk 50+ pairs
        │
        └── [Signal / Analisa] fetchBinanceSignal()
                │
                └── GET /terminal/binance/analyze?symbol=BTC/USDT&timeframe=H1&limit=200
                        ↓
                    gas-terminal-backend:8085 (binance.py route)
                        ↓
                    GET gas-binance-service:9612/ohlcv?symbol=BTC/USDT&timeframe=H1&limit=200
                        ↓ CCXT → Binance OHLCV
                    ┌─────────────────────────────────────────────────────┐
                    │  LOCAL TA Compute di binance.py (no LLM):           │
                    │  EMA(9, 21, 50, 200)                                │
                    │  RSI(14)                                            │
                    │  MACD(12, 26, 9)                                    │
                    │  Bollinger Bands(20, 2)                             │
                    │  ATR(14)                                            │
                    │  Swing Points → Market Structure (BOS/ChoCH)        │
                    │  → Scoring: bullish/bearish per indikator           │
                    │  → return: signal BUY/SELL/NEUTRAL + confluence     │
                    └─────────────────────────────────────────────────────┘
                    ⚠️  TIDAK pakai AI LLM — pure TA compute lokal
```

### Services Involved — BinanceAI
| Service | Port | Fungsi |
|---|---|---|
| `gas-terminal-backend` | 8085 | WS proxy + TA compute engine |
| `gas-binance-service` | 9612 | CCXT Binance wrapper |

### External Data Sources — BinanceAI
| Source | Data |
|---|---|
| `api.binance.com` | Spot tickers, OHLCV (public, no API key) |

---

## 3. 📊 Stock IDX AI Pipeline

```
Tab load → fetch paralel IHSG + watchlist tickers
        │
        ├── [IHSG Index]
        │       GET /terminal/idx/ihsg
        │               ↓
        │           gas-terminal-backend:8085 → /terminal/idx/* prefix
        │               ↓ proxy ke
        │           gas-idx-service:9615/idx/ihsg
        │               ↓
        │           yfinance Ticker("^JKSE")
        │           → Yahoo Finance API
        │           return: IHSG level, change%, volume
        │
        ├── [Watchlist Tickers]
        │       GET /terminal/idx/tickers?symbols=BBCA.JK,GOTO.JK,...
        │               ↓ gas-idx-service:9615
        │               ↓ yfinance batch fetch (chunks of 10)
        │           return: price, change%, volume, open/high/low per saham
        │
        ├── [Signal / TA]
        │       GET /terminal/idx/signal?symbol=BBCA&interval=1d&period=6mo
        │               ↓ gas-idx-service:9615/idx/signal
        │               ↓ yfinance OHLCV → compute:
        │           SMA(20,50,200), EMA(9,21), RSI(14), MACD,
        │           Stochastic, Bollinger Bands, ADX, Volume MA
        │           → scoring per indikator → strength score
        │           return: signal, strength, BUY/SELL/NEUTRAL, reason
        │
        ├── [SMC Analysis]
        │       GET /terminal/idx/smc?symbol=BBCA&interval=1d&style=swing
        │               ↓ gas-idx-service:9615/idx/smc
        │               ↓ yfinance OHLCV (lebih banyak candle, 1y)
        │           → detect: BOS (Break of Structure)
        │           → detect: ChoCH (Change of Character)
        │           → detect: OB (Order Block) bullish/bearish
        │           → detect: FVG (Fair Value Gap)
        │           → detect: Liquidity zones (equal H/L)
        │           → style: swing / intraday
        │           return: struktur pasar + SMC levels
        │
        └── [Scanner] parallel fetch 3 endpoints:
                GET /terminal/idx/top_gainer?n=10
                GET /terminal/idx/top_loser?n=10
                GET /terminal/idx/most_active?n=10
                        ↓ gas-idx-service:9615
                        ↓ yfinance screener / batch fetch + sort
                return: top 10 mover/loser/most active dengan perubahan harga
```

### Services Involved — StockIDX AI
| Service | Port | Fungsi |
|---|---|---|
| `gas-terminal-backend` | 8085 | IDX proxy router |
| `gas-idx-service` | 9615 | yfinance wrapper + TA/SMC compute |

### External Data Sources — StockIDX AI
| Source | Data |
|---|---|
| `Yahoo Finance` via `yfinance` lib | OHLCV, ticker info, IHSG index semua saham BEI |

---

## 4. 🎰 PolymarketAI Pipeline

```
├── [Free Data — no credits required]
│       │
│       ├── GET /terminal/polymarket/top5
│       ├── GET /terminal/polymarket/markets?category=...&limit=...
│       ├── GET /terminal/polymarket/analytics
│       ├── GET /terminal/polymarket/history?limit=20
│       └── GET /terminal/polymarket/categories
│               ↓
│           gas-terminal-backend:8085 → polymarket.py proxy
│               ↓
│           gas-polymarket-service:9613
│               ↓ gamma_client.py
│               ↓ EXTERNAL APIs (Polymarket):
│                   https://gamma-api.polymarket.com   ← market list + metadata + odds
│                   https://clob.polymarket.com         ← order book, best yes/no price
│                   https://data-api.polymarket.com     ← volume, liquidity, history
│           return: event list, yes/no odds, volume, kategori
│
└── [AI Predict — PAID Credits]
        │
        └── POST /web/api/v1/polymarket/predict
                ↓
            gas-web-backend:8005
            → JWT auth + plan check (Ultra/Ultimate only)
            → deduct: 3 cr (signal_only=true) atau 8 cr (4-agent full)
            → check Redis cache key gas:poly:predict2:{event_id} (60s TTL)
                ↓
            POST gas-polymarket-service:9613/polymarket/predict
                ↓
            prediction_engine.py:
            1. Fetch market data dari Polymarket APIs (odds + volume + history)
            2. Build context: yes_price, no_price, volume_24h, open_interest
            3. POST gas-strategy-core:7003/v1/analysis/technical
               → kirim: event description + current odds sebagai "market context"
               → DeepSeek / Claude via OpenRouter
                ↓
            return: YES/NO probability, confidence %, reasoning, key factors

        signal_only=true → 1 model (claude), 3 cr
        signal_only=false → 4 model parallel (claude+gpt+deepseek+gemini), 8 cr
```

### Services Involved — PolymarketAI
| Service | Port | Fungsi |
|---|---|---|
| `gas-terminal-backend` | 8085 | Free data proxy |
| `gas-web-backend` | 8005 | Plan gate + credit deduction |
| `gas-polymarket-service` | 9613 | Polymarket API wrapper |
| `gas-strategy-core` | 7003 | AI inference engine |

### External Data Sources — PolymarketAI
| Source | Data |
|---|---|
| `gamma-api.polymarket.com` | Market list, event metadata, current odds |
| `clob.polymarket.com` | Live order book, best bid/ask YES/NO |
| `data-api.polymarket.com` | Volume, liquidity, trade history |
| OpenRouter (via strategy-core) | LLM inference untuk probabilitas prediksi |

---

## 5. 🐸 MemecoinAI Pipeline

```
├── [Free Data — no credits required]
│       │
│       ├── GET /terminal/memecoin/trending?chain=solana&limit=30
│       ├── GET /terminal/memecoin/stats
│       └── GET /terminal/memecoin/search?q=BONK&limit=15
│               ↓
│           gas-terminal-backend:8085 → memecoin.py proxy
│               ↓
│           gas-memecoin-service:9614
│               ↓ dexscreener.py
│               ↓ EXTERNAL: https://api.dexscreener.com
│                   /token-profiles/latest/v1           ← trending tokens
│                   /dex/search?q={query}               ← token search
│                   /dex/tokens/{address}               ← token detail
│           return: token list + price + volume + liquidity + dex_url
│
└── [AI Signal — PAID: 5 cr]
        │
        └── POST /web/api/v1/memecoin/signal
                ↓
            gas-web-backend:8005
            → JWT auth + plan check (Premium+ plan minimum)
            → deduct 5 cr
            → check Redis cache gas:meme:signal:{token_address} (60s TTL)
                ↓
            POST gas-memecoin-service:9614/memecoin/signal
                ↓
            ai_engine.py — 4 MODEL PARALLEL asyncio.gather():
            ┌─────────────────────────────────────────────────────────┐
            │  Model         Weight  Specialty                        │
            │  ─────────     ──────  ──────────────────────────────   │
            │  claude         1.3    Rug Pull Detection + Safety      │
            │  gpt            1.0    Volume & Momentum Analysis       │
            │  deepseek       1.0    Price Action Technical           │
            │  gemini         1.0    Liquidity & Market Depth         │
            └─────────────────────────────────────────────────────────┘
            Tiap model → POST gas-strategy-core:7003/v1/analysis/technical
            dengan payload: token_data + rug_detection_result + model_focus
                ↓
            Weighted score merge:
            → check liquidity threshold (rug filter)
            → adjust claude weight berdasarkan rug risk
            → final_score = Σ(model_score × weight) / Σ(weights)
                ↓
            return: BUY/SELL/HOLD, confidence %, risk level,
                    rug_risk score, reasoning per model
```

### Services Involved — MemecoinAI
| Service | Port | Fungsi |
|---|---|---|
| `gas-terminal-backend` | 8085 | Free data proxy |
| `gas-web-backend` | 8005 | Plan gate + credit deduction |
| `gas-memecoin-service` | 9614 | DexScreener wrapper + rug detection |
| `gas-strategy-core` | 7003 | AI inference (4-model parallel) |

### External Data Sources — MemecoinAI
| Source | Data |
|---|---|
| `api.dexscreener.com` | Trending tokens, search, price, volume, liquidity (public, no key) |
| OpenRouter (via strategy-core) | LLM inference 4 model: Claude, GPT-4o, DeepSeek, Gemini |

---

## 6. 🤖 Quant Signal Pipeline (EA / Internal)

```
MT5 EA polling tiap N detik
        │
        └── POST gas-quant-orch:9500/signal/generate
                {symbol, timeframe, market: {bid,ask,spread,atr}, session, context}
                ↓
            gas-quant-orch:9500 (orchestrator.py)
            → spread guard check
            → asyncio.gather() — 6 ENGINE PARALLEL:
            ┌─────────────────────────────────────────────────────────────┐
            │  Engine           Port    Endpoint                          │
            │  ─────────────    ────    ───────────────────────────────   │
            │  regime-detector  9503    POST /regime                      │
            │  pattern-detector 9501    POST /detect                      │
            │  statarb-engine   9502    POST /signal                      │
            │  trend-engine     9513    POST /trend                       │
            │  market-phase     9510    POST /phase                       │
            │  orderflow        9514    GET  /orderflow/{symbol}/signal   │
            └─────────────────────────────────────────────────────────────┘
            Tiap engine fetch data dari Redis (MT5 OHLC)
                ↓
            scorer.py — weighted score:
            → regime adjusts weights (TRENDING: trend×1.5, RANGING: statarb×1.5)
            → BREAKOUT: orderflow×1.4
            → final_score = Σ(engine_score × weight) / Σ(weights)
            → signal = BUY if score ≥ 0.5, SELL if ≤ -0.5
                ↓
            generate_gas_signal():
            → compute entry/sl/tp dari ATR
            → grade signal (A+/A/B+/B/C)
            → build reason string (all 6 engine results)
            → check session kill zone
                ↓
            return: {action, entry, sl, tp1, tp_final, lot, reason,
                     trading_plan, risk_management, psychology, mindset,
                     regime, session, confidence, grade, level}
```

### Services Involved — Quant Signal
| Service | Port | Fungsi |
|---|---|---|
| `gas-quant-orch` | 9500 | Orchestrator 6 engine |
| `gas-regime-detector` | 9503 | Market regime (TRENDING/RANGING/BREAKOUT) |
| `gas-pattern-detector` | 9501 | Chart pattern detection (H&S, W-Bottom, Flag, etc.) |
| `gas-statarb-engine` | 9502 | Statistical arbitrage signal (XAUUSD_DXY spread) |
| `gas-trend-engine` | 9513 | Trend direction + strength |
| `gas-market-phase` | 9510 | Market phase (accumulation/distribution/markup/markdown) |
| `gas-orderflow` | 9514 | Order flow: buy/sell pressure + delta |
| `gas-feature-engine` | 9499 | Feature extraction backbone (dipakai engines) |
| `gas-redis` | 6379 | OHLC + tick cache source |

---

## 7. 🧠 Morning Briefing / RAG Pipeline

```
Scheduler tiap 06:30 WIB (atau on-demand cache miss)
        │
        └── gas-strategy-core:7003 scheduler.py
                ↓ asyncio.gather() semua fetch paralel:
            ┌────────────────────────────────────────────────────────────┐
            │  fetch_fear_greed()          → alternative.me API          │
            │  get_macro_data("US")        → local macro.py scraper      │
            │  _build_mtf_features_with_dxy("XAUUSD", "intraday")       │
            │    └─→ Redis OHLC H4/H1/M15/M5 XAU + DXY                 │
            │  _get_dxy_candles("H4")      → Redis OHLC DXY              │
            │  get_upcoming_events()       → gas-calendar-news:9601      │
            │  _fetch_rag_macro()          → gas-rag-macro:9002          │
            │    └─→ POST /macro/analyze   → ChromaDB vector search      │
            │         → OpenAI/Vertex AI embedding + LLM                 │
            │  _fetch_rag_technical()      → gas-rag-technical:9001      │
            │    └─→ POST /analyze         → ChromaDB vector search      │
            │         → OpenAI/Vertex AI embedding + LLM                 │
            └────────────────────────────────────────────────────────────┘
                ↓
            ai.analyze_briefing() → DeepSeek via OpenRouter
            → blend semua data jadi morning briefing
            → merge RAG insights (rag_macro_summary, rag_key_factors,
              rag_technical_summary, rag_key_levels)
                ↓
            set_cached_briefing() → Redis cache (sampai hari berikutnya)
                ↓
            Expose via: GET /terminal/overview → ai field
                   dan: POST /web/api/v1/analysis/briefing
```

### Services Involved — Briefing/RAG
| Service | Port | Fungsi |
|---|---|---|
| `gas-strategy-core` | 7003 | Briefing generator + scheduler |
| `gas-calendar-news-service` | 9601 | Economic calendar events |
| `gas-rag-macro` | 9002 | RAG macro analysis (ChromaDB + LLM) |
| `gas-rag-technical` | 9001 | RAG technical analysis (ChromaDB + LLM) |
| `gas-data-ingestor` | - | Feed dokumen ke vector DB |
| `gas-vector-db` | - | ChromaDB vector store |
| `gas-redis` | 6379 | Cache briefing result harian |

---

## 8. 🔔 Alert & Screener & TradingPlan Pipeline (baru terhubung)

```
[Screener]
Frontend → POST /terminal/screener
                ↓
            gas-terminal-backend:8085 → screener.py
                ↓
            POST gas-screener-service:9600/screener
            → scan semua pairs berdasarkan filter criteria
            return: list pairs dengan sinyal + strength

[Alerts]
Frontend → GET/POST/PUT/DELETE /terminal/alerts
                ↓
            gas-terminal-backend:8085 → alerts.py
                ↓
            gas-alert-engine:8400/alerts
            → CRUD alert rules (price level, indicator cross, etc.)
            → evaluate triggers → gas-notification-service

[TradingPlan]
Frontend → GET/POST/PUT/DELETE /terminal/plans
                ↓
            gas-terminal-backend:8085 → tradingplan.py
                ↓
            gas-tradingplan-service:9602/plans
            → CRUD trading plans dengan PostgreSQL storage

[Backtest]
Frontend → POST /terminal/backtest
                ↓
            gas-terminal-backend:8085 → backtest.py
                ↓
            gas-quant-backtester:9504/backtest
            → run backtest job
            → GET /terminal/backtest/{id} untuk poll result
```

---

## Summary — Semua Services & Port

| Service | Port | Category | Konsumer Utama |
|---|---|---|---|
| `gas-terminal-frontend` | 3000 | UI | User browser |
| `gas-terminal-backend` | 8085 | BFF | Frontend |
| `gas-web-backend` | 8005 | BFF (credits/auth) | Frontend |
| `gas-auth-service` | 8001 | Auth | Semua |
| `gas-strategy-core` | 7003 | AI Core | web-backend, polymarket, memecoin |
| `gas-mt5-websocket` | 8110 | Data Bridge | Redis (tick push) |
| `gas-mt5-data-service` | 8100 | Data Bridge | strategy-core |
| `gas-redis` | 6379 | Cache | Semua |
| `gas-binance-service` | 9612 | Market Data | terminal-backend |
| `gas-idx-service` | 9615 | Market Data | terminal-backend |
| `gas-polymarket-service` | 9613 | Market Data | terminal-backend, web-backend |
| `gas-memecoin-service` | 9614 | Market Data | terminal-backend, web-backend |
| `gas-calendar-news-service` | 9601 | Data | terminal-backend, strategy-core |
| `gas-fundamental-data-service` | 9603 | Data | terminal-backend |
| `gas-quant-orch` | 9500 | Quant Engine | EA (MT5) |
| `gas-regime-detector` | 9503 | Quant Engine | quant-orch |
| `gas-pattern-detector` | 9501 | Quant Engine | quant-orch |
| `gas-statarb-engine` | 9502 | Quant Engine | quant-orch |
| `gas-trend-engine` | 9513 | Quant Engine | quant-orch |
| `gas-market-phase` | 9510 | Quant Engine | quant-orch |
| `gas-orderflow` | 9514 | Quant Engine | quant-orch |
| `gas-feature-engine` | 9499 | Quant Backbone | quant engines |
| `gas-smc-engine` | 8000 | TA Engine | strategy-core |
| `gas-screener-service` | 9600 | Utility | terminal-backend |
| `gas-alert-engine` | 8400 | Utility | terminal-backend |
| `gas-tradingplan-service` | 9602 | Utility | terminal-backend |
| `gas-quant-backtester` | 9504 | Utility | terminal-backend |
| `gas-rag-macro` | 9002 | RAG | strategy-core |
| `gas-rag-technical` | 9001 | RAG | strategy-core |
| `gas-ai-orchestrator` | 9003 | AI | terminal-backend |
| `gas-notification-service` | - | Utility | alert-engine |
| `gas-signal-service` | 8106 | Signal | terminal-backend |
| `gas-chart-service` | 9700 | Chart | terminal-backend |
| `gas-realtime-hub` | 8111 | WebSocket Hub | frontend |
| `nginx-proxy` | 443/80 | Gateway | Internet → internal |

---

## Summary — Semua External APIs

| External Source | Protocol | Dipakai Oleh | Data |
|---|---|---|---|
| MT5 EA (GAS_AutoTrader.mq5) | WebSocket push | gas-mt5-websocket | Live tick + OHLC semua pairs |
| `api.binance.com` | REST (CCXT) | gas-binance-service | Spot tickers, OHLCV |
| `Yahoo Finance` (yfinance) | REST | gas-idx-service | BEI stocks, IHSG |
| `gamma-api.polymarket.com` | REST | gas-polymarket-service | Prediction market events |
| `clob.polymarket.com` | REST | gas-polymarket-service | Order book YES/NO |
| `data-api.polymarket.com` | REST | gas-polymarket-service | Volume + trade history |
| `api.dexscreener.com` | REST | gas-memecoin-service | Trending tokens, DEX data |
| `alternative.me` | REST | gas-strategy-core | Crypto Fear & Greed Index |
| `CFTC/Quandl` | REST | gas-strategy-core | COT Gold data |
| `OpenRouter` | REST | gas-strategy-core | LLM: DeepSeek/GPT-4o/Claude/Gemini |

---

## Credit Cost per Feature

| Feature | Plan Minimum | Credit Cost |
|---|---|---|
| Technical Analysis | Essential | 2 cr |
| Signal (basic) | Essential | 3 cr |
| Signal (pro) | Plus | 5 cr |
| Signal (ultra) | Premium | 8 cr |
| Signal (gpt/agent) | Ultimate | 10–15 cr |
| Correlation | Plus | 3 cr |
| Fundamental | Plus | 2 cr |
| Calendar | Plus | 1 cr |
| Sentiment | Plus | 2 cr |
| Risk Manager | Plus | 1 cr |
| Hybrid Analysis | Premium | 5 cr |
| Drawdown Recovery | Premium | 3 cr |
| Psychology Coach | Premium | 2 cr |
| Briefing | Premium | 3 cr |
| Journal AI | Premium | 2 cr |
| PropFirm | Premium | 3 cr |
| Screener | Ultimate | 15 cr |
| Backtesting | Ultimate | 20 cr |
| Mentor Mode | Ultimate | 10 cr |
| Polymarket Predict (signal) | Ultimate | 3 cr |
| Polymarket Predict (4-agent) | Ultimate | 8 cr |
| Memecoin AI Signal | Premium | 5 cr |
