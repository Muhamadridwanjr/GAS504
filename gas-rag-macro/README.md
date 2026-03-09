# 🌍 GAS RAG Macro

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 3 (AI Layer)**

> **Mesin analisis makroekonomi dan sentimen berita berbasis Retrieval-Augmented Generation (RAG).**
> Service ini menyediakan wawasan tentang faktor-faktor makroekonomi, berita pasar, sentimen, dan dampaknya terhadap aset trading. Terintegrasi dengan `gas-gateway-api` untuk autentikasi dan routing, serta mengambil data dari berbagai sumber eksternal (API berita, kalender ekonomi, data ekonomi riil) untuk memperkaya analisis.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Konfigurasi](#konfigurasi)
- [API Reference](#api-reference)
- [Integrasi dengan Gateway](#integrasi-dengan-gateway)
- [Pengujian](#pengujian)

---

## 🔍 Ikhtisar

**gas-rag-macro** adalah service AI khusus untuk analisis makroekonomi. Berbeda dengan analisis teknikal yang fokus pada harga dan pola, analisis makro melihat faktor-faktor eksternal seperti:

- Data ekonomi (inflasi, tenaga kerja, PDB, suku bunga)
- Kebijakan bank sentral (The Fed, ECB, dll)
- Berita geopolitik
- Sentimen pasar (risk-on/risk-off)
- Kalender ekonomi (rilis data penting)

Service ini menggunakan pendekatan **RAG** untuk menggabungkan:
- **Data realtime** dari API berita dan kalender ekonomi
- **Konteks historis** dari knowledge base makro
- **Data pasar** dari `gas-market-data-processor`

---

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌────────────────────────────────────┐
│  gas-gateway-api│────▶│         gas-rag-macro             │
│   (Port 8000)   │     │  ┌──────────┐  ┌───────────────┐  │
└─────────────────┘     │  │   REST   │  │  RAG Engine   │  │
                        │  │  API     │──│    Core       │  │
                        │  └──────────┘  └───────┬───────┘  │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │   Vector DB (Chroma)        │  │
                        │  └─────────────────────────────┘  │
                        │                         │          │
                        │  ┌─────────────────────────────┐  │
                        │  │    Provider Router         │  │
                        │  │  (Vertex AI | OpenAI)      │  │
                        │  └─────────────────────────────┘  │
                        └────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│   News API          │ │   Economic Calendar │ │   Market Data       │
│ (NewsAPI.org /      │ │ (ForexFactory JSON) │ │ (gas-market-data-   │
│  Google News RSS)   │ │                     │ │  processor)         │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

---

## ✨ Fitur Utama

- **Analisis Berita Realtime**: NewsAPI.org + Google News RSS fallback.
- **Integrasi Kalender Ekonomi**: ForexFactory JSON API, disortir berdasarkan impact.
- **RAG dengan Vector DB**: Chroma untuk semantic retrieval atas analisis historis.
- **Dual‑Provider AI**: Vertex AI (Gemini) + OpenAI (GPT‑4o) dengan automatic fallback.
- **Cache Redis**: Hasil analisis di-cache untuk efisiensi.
- **Multi‑Aset**: Mendukung forex, komoditas, indeks, crypto.
- **Structured Output**: JSON yang terstruktur (sentiment, confidence, key_factors).
- **Integrasi Gateway**: Header `X-User-ID` dari `gas-gateway-api`.

---

## 🛠️ Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Web Framework | FastAPI + uvicorn |
| AI Providers | Vertex AI (Gemini 1.5 Pro) / OpenAI (GPT-4o) |
| Vector DB | ChromaDB |
| News | NewsAPI.org / Google News RSS (feedparser) |
| Calendar | ForexFactory JSON |
| Cache | Redis |
| Language | Python 3.11+ |
| Container | Docker + Docker Compose |

---

## 📁 Struktur Direktori

```
.
├── src/
│   ├── api/
│   │   ├── dependencies.py      # Dapatkan user_id dari header
│   │   ├── models.py            # Pydantic models
│   │   └── routes/
│   │       ├── analyze.py       # POST /macro/analyze, GET /providers
│   │       └── admin.py         # POST /knowledge/update
│   ├── core/
│   │   ├── rag_engine.py        # Orkestrasi RAG pipeline
│   │   ├── context_builder.py   # Build prompt dari news/calendar/docs
│   │   ├── response_parser.py   # Parse output AI ke Pydantic
│   │   └── exceptions.py
│   ├── retrieval/
│   │   ├── vector_store.py      # Chroma wrapper
│   │   ├── embeddings.py        # OpenAI/Vertex embeddings
│   │   └── retrievers.py        # Higher-level retrieval
│   ├── providers/
│   │   ├── base.py              # Abstract BaseProvider
│   │   ├── vertex.py            # Vertex AI (Gemini)
│   │   ├── openai.py            # OpenAI (GPT-4o)
│   │   └── router.py            # Provider routing + fallback
│   ├── fetchers/
│   │   ├── news.py              # NewsAPI.org + Google News RSS
│   │   ├── calendar.py          # ForexFactory economic calendar
│   │   └── market.py            # gas-market-data-processor client
│   ├── knowledge/
│   │   ├── indexer.py           # Background indexing
│   │   └── document_loader.py   # Load & chunk documents
│   ├── lib/
│   │   ├── logger.py            # structlog setup
│   │   └── utils.py             # Shared helpers
│   ├── config.py                # Pydantic settings
│   └── main.py                  # FastAPI entry point
├── data/
│   ├── news_archive/
│   └── vector_store/
├── tests/
│   ├── conftest.py
│   ├── test_api.py
│   ├── test_providers.py
│   └── test_fetchers.py
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalasi & Menjalankan

### 🐍 Python Mode

#### Prasyarat
- Python 3.11+
- Redis (running)
- Chroma DB (via Docker)

#### 1. Setup Environment

```bash
cd /home/mridwan3101/goldenaistrategy/gas-rag-macro
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### 2. Copy Environment

```bash
cp .env.example .env
# Edit .env – isi API keys
```

#### 3. Jalankan Dependencies

```bash
# Redis
docker run -d --name gas-redis -p 6379:6379 redis

# ChromaDB
docker run -d --name gas-rag-macro-chroma -p 9102:8000 chromadb/chroma
```

#### ▶️ Run

```bash
source venv/bin/activate
uvicorn src.main:app --reload --port 9002
```

#### ⛔ Stop

```bash
# Ctrl+C di terminal, atau:
pkill -f "uvicorn src.main:app"
```

#### 🔄 Restart

```bash
pkill -f "uvicorn src.main:app"
sleep 1
source venv/bin/activate
uvicorn src.main:app --reload --port 9002
```

#### ❌ Delete Environment

```bash
deactivate
rm -rf venv
```

---

### 🐳 Docker Mode

#### ▶️ Build & Run

```bash
cd /home/mridwan3101/goldenaistrategy/gas-rag-macro
docker-compose up -d --build
```

#### 📊 Check Status

```bash
docker-compose ps
docker ps --filter name=gas-rag-macro
```

#### ⛔ Stop

```bash
docker-compose stop
```

#### 🔄 Restart

```bash
docker-compose restart
```

#### ❌ Delete Container / Image

```bash
docker-compose down -v
docker rmi gas-rag-macro-gas-rag-macro
```

---

## 📦 Setup GitHub (First Time)

```bash
cd /home/mridwan3101/goldenaistrategy/gas-rag-macro
echo "# gas-rag-macro-" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-rag-macro-.git
git push -u origin main
```

**Push existing repository:**

```bash
git remote add origin https://github.com/Muhamadridwanjr/gas-rag-macro-.git
git branch -M main
git push -u origin main
```

---

## 🔁 Update Project (Commit & Push)

```bash
cd /home/mridwan3101/goldenaistrategy/gas-rag-macro
git add .
git commit -m "feat: <deskripsi perubahan>"
git push origin main
```

---

## 📛 Container Naming

```
Container name: gas-rag-macro
```

---

## 🌐 Health Check (Status 200 OK)

**Endpoint:**
```
GET http://localhost:9002/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "gas-rag-macro",
  "version": "1.0.0",
  "environment": "development"
}
```

---

## 🧪 Debug & Logging

**Docker Logs:**
```bash
docker logs gas-rag-macro -f
docker logs gas-rag-macro --tail 100
```

**Application Logs:**
- Structured JSON logs via `structlog`
- Log level: `LOG_LEVEL=INFO` (configurable)

**Healthcheck Configuration:**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9002/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

---

## 🟢 Container Status

```
Expected: Up (healthy)
```

---

## 🔗 Integrasi gas-gateway-api

**Configuration:**
```env
# Di gas-gateway-api atau Nginx
MACRO_SERVICE_URL=http://gas-rag-macro:9002
```

**Request Example (dari gateway ke service):**
```bash
curl -X POST http://gas-rag-macro:9002/macro/analyze \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user_123" \
  -d '{
    "symbol": "XAUUSD",
    "query": "Dampak CPI AS terhadap emas?",
    "time_horizon": "24h",
    "model_preference": "openai"
  }'
```

---

## 📡 API Reference

### `POST /macro/analyze`

**Request:**
```json
{
  "symbol": "XAUUSD",
  "query": "Apa dampak rilis data CPI AS terhadap emas dalam 24 jam ke depan?",
  "time_horizon": "24h",
  "include_news": true,
  "include_calendar": true,
  "include_price_data": true,
  "model_preference": "openai",
  "temperature": 0.3,
  "max_tokens": 1200
}
```

**Response:**
```json
{
  "id": "macro_a1b2c3d4",
  "symbol": "XAUUSD",
  "timestamp": 1700001234,
  "summary": "CPI AS yang tinggi berpotensi memperkuat dolar dan menekan emas.",
  "sentiment": "bearish",
  "confidence": 0.75,
  "key_factors": [
    {"factor": "CPI AS", "impact": "USD naik → emas turun", "probability": 0.7}
  ],
  "news": [],
  "calendar_events": [],
  "historical_reaction": "Dalam 5 rilis CPI terakhir, emas turun rata-rata 0.5%.",
  "sources": ["Bloomberg"],
  "provider_used": "openai",
  "model_used": "gpt-4o",
  "processing_time_ms": 1234
}
```

### `GET /health` – Health check (Status 200)
### `GET /macro/providers` – List provider tersedia
### `POST /knowledge/update` – Re-index knowledge base (requires `X-API-Key` header)

---

## 🔌 Komunikasi Antar Service

**Network:**
```yaml
networks:
  gas-network:
    external: true
    name: gas-network
```

**Service Communication:**
```
gas-gateway-api:8000  ──▶  gas-rag-macro:9002
gas-rag-macro:9002    ──▶  gas-market-data-processor:8100
gas-rag-macro:9002    ──▶  gas-rag-macro-chroma:8000 (Vector DB)
gas-rag-macro:9002    ──▶  gas-redis:6379 (Cache)
gas-rag-macro:9002    ──▶  NewsAPI / ForexFactory (External)
```

---

## 🧪 Pengujian

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest tests/ -v

# With coverage
pytest --cov=src tests/
```

---

## 🧠 Integrasi dengan @goldenaistrategy

Service ini adalah bagian dari ekosistem GAS pada **VPS 3 (AI Layer)**:

| Service | Port | Fungsi |
|---------|------|--------|
| gas-gateway-api | 8000 | Entry point, autentikasi |
| gas-rag-macro | **9002** | Analisis makroekonomi (service ini) |
| gas-rag-technical | 9001 | Analisis teknikal |
| gas-ai-orchestrator | 9003 | Orkestrasi AI |

---

## ✅ Final Checklist

- [x] Container name sesuai project (`gas-rag-macro`)
- [x] Status container: Up (healthy)
- [x] Endpoint `/health` mengembalikan 200 OK
- [x] Tidak ada error pada logs
- [x] Terintegrasi dengan GAS Gateway API
- [x] Antar service dapat saling berkomunikasi

---

**🔥 GAS Strategy – Analisis Makro Bertenaga AI untuk Keputusan Trading Lebih Cerdas**

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS.** Seluruh hak cipta dilindungi undang-undang.
