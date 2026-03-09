# 🧠 GAS RAG Technical

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 3 (AI Layer)**

> Mesin analisis teknikal berbasis **Retrieval-Augmented Generation (RAG)** dengan dual-provider support: **Vertex AI (Gemini)** dan **OpenAI (GPT-4o)**.  
> Service menerima permintaan analisis teknikal, mengambil konteks relevan dari knowledge base, menggabungkannya dengan data pasar realtime, dan menghasilkan wawasan terstruktur.

---

## 📋 Info Service

| Key | Value |
|-----|-------|
| **Nama** | gas-rag-technical |
| **Port** | 9001 |
| **Tipe** | AI / RAG |
| **VPS** | VPS 3 – AI Layer |

---

## 🧱 0. INSTALASI ENVIRONMENT

### 🐍 Python Mode

```bash
# 1. Buat virtual environment
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements-dev.txt

# 3. Copy dan edit environment
cp .env.example .env
# Isi OPENAI_API_KEY atau GOOGLE_APPLICATION_CREDENTIALS sesuai provider

# 4. Jalankan dependency (Chroma + Redis)
docker run -d -p 8001:8000 --name gas-rag-chroma chromadb/chroma
docker run -d -p 6379:6379 --name gas-rag-redis redis:7-alpine

# 5. (Opsional) Inisialisasi knowledge base
python -m src.knowledge.indexer --init
```

### 🐳 Docker Mode

```bash
# Pastikan gas-network sudah ada
docker network create gas-network || true

# Copy dan isi .env terlebih dahulu
cp .env.example .env
```

---

## ⚙️ 1. TUTORIAL MANAGEMENT SERVICE

### 🐍 Python Mode

#### ▶️ Run
```bash
source venv/bin/activate
uvicorn src.main:app --reload --port 9001
```

#### ⛔ Stop
```bash
# Tekan Ctrl+C di terminal yang menjalankan uvicorn
```

#### 🔄 Restart
```bash
# Stop (Ctrl+C), lalu jalankan ulang:
uvicorn src.main:app --reload --port 9001
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
docker-compose up -d --build
```

#### 📊 Check Status
```bash
docker-compose ps
docker ps --filter name=gas-rag-technical
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
# Stop dan hapus container + volume
docker-compose down -v

# Hapus image
docker rmi gas-rag-technical-gas-rag-technical
```

---

## 📦 2. SETUP GITHUB (FIRST TIME)

```bash
echo "# gas-rag-technical" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-rag-technical.git
git push -u origin main
```

**atau push repositori yang sudah ada:**
```bash
git remote add origin https://github.com/Muhamadridwanjr/gas-rag-technical.git
git branch -M main
git push -u origin main
```

---

## 🔁 3. UPDATE PROJECT (COMMIT & PUSH)

```bash
git add .
git commit -m "feat: deskripsi perubahan"
git push origin main
```

---

## 📛 4. CONTAINER NAMING

```
Container name = gas-rag-technical
```

Sesuai dengan `container_name` di `docker-compose.yml`.

---

## 🌐 5. HEALTH CHECK (STATUS 200 OK)

**Endpoint:**
```
GET http://localhost:9001/health
```

**Expected Response:**
```json
{
  "status": "ok",
  "service": "gas-rag-technical",
  "version": "1.0.0",
  "environment": "production"
}
```

**Curl command:**
```bash
curl -s http://localhost:9001/health | python3 -m json.tool
```

---

## 🧪 6. DEBUG & LOGGING

### Docker Logs
```bash
# Semua log
docker logs gas-rag-technical

# Follow (real-time)
docker logs -f gas-rag-technical

# 100 baris terakhir
docker logs --tail 100 gas-rag-technical
```

### Application Logs
Log ditulis ke stdout dengan format:
```
[2025-01-01T12:00:00Z] INFO src.core.rag_engine: Generating analysis via openai/gpt-4o
```

Set `LOG_LEVEL=DEBUG` di `.env` untuk log lebih detail.

### Healthcheck Configuration
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:9001/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

---

## 🟢 7. CONTAINER STATUS

**Expected:** `Up (healthy)`
```bash
docker ps --filter name=gas-rag-technical --format "table {{.Names}}\t{{.Status}}"
```

---

## 🔗 8. INTEGRASI gas-gateway-api

### Configuration (.env gateway)
```env
RAG_TECHNICAL_URL=http://gas-rag-technical:9001
```

### Request Example
```bash
curl -X POST http://localhost:9001/analyze \
  -H "Content-Type: application/json" \
  -H "X-User-ID: user123" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "H4",
    "query": "Analisis struktur pasar dan level kunci untuk 24 jam ke depan",
    "model_preference": "openai",
    "include_sources": true
  }'
```

---

## 🧠 9. INTEGRASI DENGAN @goldenaistrategy

Service ini adalah **AI Layer** dalam ekosistem GAS:

```
gas-ai-orchestrator  →  gas-rag-technical (port 9001)
                              ↓
                     Vector DB (Chroma:8001)
                     Redis Cache (6379)
                     gas-market-data-processor (8100)
```

- **Input dari:** `gas-ai-orchestrator` via `POST /analyze`
- **Output ke:** Hasil analisis terstruktur JSON (signal, confidence, levels)
- **Mengonsumsi:** `gas-market-data-processor` untuk data OHLC realtime

---

## 🔄 10. KOMUNIKASI ANTAR SERVICE

### Network Configuration
```bash
# Pastikan semua container dalam jaringan yang sama
docker network create gas-network
docker network connect gas-network gas-rag-technical
```

### Service Communication
```python
# Contoh request dari gas-ai-orchestrator
import httpx

async with httpx.AsyncClient() as client:
    response = await client.post(
        "http://gas-rag-technical:9001/analyze",
        json={
            "symbol": "XAUUSD",
            "timeframe": "H4",
            "query": "Analisis pola breakout",
            "model_preference": "openai"
        },
        headers={"X-User-ID": "user123"}
    )
    analysis = response.json()
```

---

## 📁 STRUKTUR PROJECT

```
gas-rag-technical/
├── src/
│   ├── api/
│   │   ├── dependencies.py      # Auth header extraction
│   │   ├── models.py            # Pydantic request/response models
│   │   └── routes/
│   │       ├── analyze.py       # POST /analyze, /analyze/batch, GET /providers
│   │       └── admin.py         # POST /knowledge/update, GET /knowledge/stats
│   ├── core/
│   │   ├── rag_engine.py        # Main RAG pipeline orchestrator
│   │   ├── context_builder.py   # Prompt + context assembly
│   │   ├── response_parser.py   # LLM output → structured dict
│   │   └── exceptions.py
│   ├── retrieval/
│   │   ├── vector_store.py      # Chroma/FAISS abstraction
│   │   ├── embeddings.py        # Embedding generation
│   │   └── retrievers.py        # Semantic + filtered retrieval
│   ├── providers/
│   │   ├── base.py              # Abstract provider interface
│   │   ├── vertex.py            # Vertex AI Gemini
│   │   ├── openai.py            # OpenAI GPT-4o
│   │   └── router.py            # Dynamic provider selection
│   ├── knowledge/
│   │   ├── indexer.py           # Background indexing + CLI
│   │   ├── document_loader.py   # TXT/MD/JSON loader
│   │   └── chunker.py           # Text chunking
│   ├── market/
│   │   └── client.py            # HTTP client for market data
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   ├── config.py                # Pydantic settings
│   └── main.py                  # FastAPI entry point
├── data/
│   ├── knowledge_base/          # Dokumen RAG mentah (.txt, .md, .json)
│   └── vector_store/            # Chroma persistent store
├── tests/
│   ├── conftest.py
│   ├── test_retrieval.py
│   ├── test_providers.py
│   └── test_api.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-dev.txt
├── pytest.ini
├── .env.example
└── README.md
```

---

## 📡 API Reference

### `POST /analyze`
Analisis teknikal dengan RAG untuk satu simbol.

### `POST /analyze/batch`
Batch analysis untuk hingga 10 simbol sekaligus.

### `GET /health`
Health check endpoint.

### `GET /providers`
List provider AI yang tersedia dan statusnya.

### `POST /knowledge/update` *(admin)*
Trigger re-indexing knowledge base (*requires X-API-Key*).

### `GET /knowledge/stats` *(admin)*
Statistik vector database (*requires X-API-Key*).

---

## 🧪 Pengujian

```bash
# Jalankan semua tests
pytest tests/ -v

# Dengan coverage report
pytest --cov=src tests/
```

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.

Hubungi: ridwan@gasstrategy.io

---

**🔥 GAS Strategy – Analisis Teknikal Bertenaga AI dengan RAG**
