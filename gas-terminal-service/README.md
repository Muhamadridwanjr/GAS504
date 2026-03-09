# 🏛️ GAS Terminal – Bloomberg‑like Financial Command Center

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Terminal Layer**  
Terminal service adalah **wajah utama platform GAS**. Seperti Bloomberg Terminal, ia menyatukan semua kekuatan ekosistem GAS ke dalam satu antarmuka terpadu: **chart, analisis, berita, eksekusi, kolaborasi, dan pendidikan**. Pengguna cukup duduk di depan terminal, mengetik perintah, dan semua informasi serta aksi tersedia dalam hitungan detik.

📛 **SERVICE NAME**
`gas-terminal-service` | Terminal | 8206 | Komando Trading (Execution) | Terminal Bloomberg‑like: menyatukan semua kekuatan GAS dalam satu antarmuka | User → TerminalService → Billing → RedisQueue → Worker → MT5 | Active

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Peta Fitur Bloomberg vs GAS](#peta-fitur-bloomberg-vs-gas)
- [Arsitektur Terminal Terintegrasi](#arsitektur-terminal-terintegrasi)
- [Alur Kerja](#alur-kerja)
- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Konfigurasi](#konfigurasi)
- [API Reference & Command Language](#api-reference--command-language)
- [Contoh Skenario](#contoh-skenario)
- [Implementasi Bertahap](#implementasi-bertahap)
- [Integrasi dengan Service Lain](#integrasi-dengan-service-lain)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Kredit](#lisensi--kredit)

---

## 🔍 Ikhtisar

**gas-terminal-service** adalah gerbang utama platform GAS – sebuah Bloomberg Terminal versi GAS. Ia bertanggung jawab menerima perintah dari pengguna (via command line, REST, atau WebSocket), mem-parsing perintah tersebut, lalu mendistribusikannya ke service di belakang yang tepat:

- `/chart XAUUSD H1` → `gas-chart-service`
- `@news gold` → `gas-calendar-news-service`
- `@research "analisis gold seminggu ke depan"` → `gas-rag-technical` + `gas-rag-macro`
- `/buy XAUUSD 0.1` → `gas-term-service` (eksekusi)
- `@ai "kenapa emas naik hari ini?"` → `gas-ai-orchestrator`

---

## 🗺️ Peta Fitur Bloomberg vs GAS Services

| Fitur Bloomberg | Deskripsi | GAS Services yang Terlibat | Peran dalam Terminal |
|-----------------|-----------|----------------------------|----------------------|
| **Research** | Analisis mendalam, laporan riset, model kuantitatif | `gas-rag-technical`, `gas-rag-macro`, `gas-fundamental-data-service`, `gas-pattern-detector`, `gas-quant-orchestrator`, `gas-vector-db` | Menyediakan hasil riset dalam panel terpisah. Pengguna bisa meminta riset via command (`@research gold 2020`) atau melihat laporan otomatis. |
| **News** | Berita pasar real‑time, kalender ekonomi | `gas-calendar-news-service`, `gas-rag-macro`, `gas-vector-db` | Panel berita yang terintegrasi dengan harga. Berita di‑embed untuk pencarian kontekstual. |
| **Access** | Manajemen akses, otorisasi, hak pengguna | `gas-auth-service`, `gas-billing-service`, `gas-gateway-api` | Login, role‑based features, pembatasan fitur sesuai tier. |
| **Charts** | Visualisasi harga, indikator, marker SMC | `gas-chart-service`, `gas-mt5-data-service`, `gas-realtime-hub`, `gas-indicator-engine`, `gas-smc-engine` | Panel chart utama dengan berbagai timeframe, indikator, dan anotasi SMC. |
| **Collaboration Tools** | Berbagi analisis, catatan, diskusi tim | `gas-social-service`, `gas-tradingplan-service`, `gas-notification-service` | Fitur follow trader, share sinyal, komentar, dan rencana trading bersama. |
| **Education** | Materi pembelajaran, tutorial, dokumentasi | `gas-ai-orchestrator` + RAG, `gas-strategy-core` dokumentasi, `gas-education-service` *(planned)* | Panel pendidikan yang berisi artikel, video, dan interaktif learning. Bisa juga AI tutor. |
| **Portfolio Analytics** | Kinerja portofolio, risiko, backtest | `gas-journal-service`, `gas-risk-engine`, `gas-quant-backtester`, `gas-fundamental-data-service` | Dashboard portofolio dengan P&L, drawdown, Sharpe ratio, dan simulasi strategi. |

---

## 🏗️ Arsitektur Terminal Terintegrasi

```mermaid
graph TD
    subgraph "Terminal UI"
        T[Terminal Core :8206]
        CMD[Command Line Parser]
    end

    subgraph "Panels"
        P1[Panel Chart]
        P2[Panel News]
        P3[Panel Research]
        P4[Panel Portofolio]
        P5[Panel Social]
    end

    subgraph "Backend Services"
        CHART[gas-chart-service]
        NEWS[gas-calendar-news-service]
        RAG_T[gas-rag-technical]
        RAG_M[gas-rag-macro]
        JOUR[gas-journal-service]
        RISK[gas-risk-engine]
        SOCIAL[gas-social-service]
        AI[gas-ai-orchestrator]
        TERM[gas-term-service]
        BILL[gas-billing-service]
    end

    T -->|command| CMD
    CMD -->|/chart| CHART
    CMD -->|@news| NEWS
    CMD -->|@research| RAG_T
    CMD -->|@research| RAG_M
    CMD -->|@ai| AI
    CMD -->|/buy /sell| TERM
    CMD -->|/portfolio| JOUR
    CMD -->|/share| SOCIAL
    TERM --> BILL
```

---

## 🧱 0. INSTALASI ENVIRONMENT

### 🐍 Python
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 🐳 Docker
```bash
docker-compose up -d --build
```

---

## ⚙️ 1. TUTORIAL MANAGEMENT SERVICE

### 🐍 Python Mode
▶️ **Run**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8206 --reload
```
⛔ **Stop**: `Ctrl + C`

🔄 **Restart**: Hentikan → jalankan ulang

### 🐳 Docker Mode
▶️ **Build & Run**
```bash
docker-compose up -d --build
```
📊 **Check Status**
```bash
docker ps | grep gas-terminal
```
⛔ **Stop**
```bash
docker-compose down
```
🔄 **Restart**
```bash
docker-compose restart gas-terminal-service
```
❌ **Delete Container / Image**
```bash
docker-compose down -v
```

---

## 📦 2. SETUP GITHUB (FIRST TIME)

```bash
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-terminal-service.git
git push -u origin main
```

---

## 📛 4. CONTAINER NAMING

- Nama container: `gas-terminal-service`
- Network: `gas-network`

---

## 🌐 5. HEALTH CHECK (STATUS 200 OK)

**Endpoint:** `http://localhost:8206/health`

**Expected Response:**
```json
{
  "status": "ok",
  "service": "gas-terminal-service"
}
```

---

## 🔧 Konfigurasi

Environment variables (`.env`):

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `PORT` | 8206 | Port REST API |
| `CHART_SERVICE_URL` | http://gas-chart-service:8101 | URL chart service |
| `NEWS_SERVICE_URL` | http://gas-calendar-news-service:8103 | URL berita |
| `RAG_TECHNICAL_URL` | http://gas-rag-technical:9001 | URL RAG teknikal |
| `RAG_MACRO_URL` | http://gas-rag-macro:9002 | URL RAG makro |
| `AI_ORCHESTRATOR_URL` | http://gas-ai-orchestrator:8100 | URL AI orchestrator |
| `TERM_SERVICE_URL` | http://gas-term-service:8205 | URL eksekusi order |
| `JOURNAL_SERVICE_URL` | http://gas-journal-service:8107 | URL journal |
| `SOCIAL_SERVICE_URL` | http://gas-social-service:8106 | URL social |
| `BILLING_SERVICE_URL` | http://gas-billing-service:8004 | URL billing |
| `INTERNAL_API_KEY` | (isi) | API key internal |
| `LOG_LEVEL` | INFO | Level logging |

---

## 📡 API Reference & Command Language

### REST / WebSocket Endpoints

#### `POST /command` – Trigger perintah terminal

```json
{
  "user_id": "uuid-user",
  "command": "/buy XAUUSD 0.1 sl:1990 tp:2020",
  "panel": "terminal"
}
```

**Response:** tergantung command yang diberikan.

#### `GET /health` – Health check

#### `GET /panels/chart?symbol=XAUUSD&tf=H1` – Chart data proxy

#### `GET /panels/news` – News feed proxy

#### `GET /panels/portfolio` – Portfolio summary proxy

### Command Language

| Command | Deskripsi | Service Target | Status |
|---------|-----------|----------------|--------|
| `/buy SYMBOL LOT [sl:X] [tp:Y]` | Beli instrument | `gas-term-service` | ✅ Active |
| `/sell SYMBOL LOT [sl:X] [tp:Y]` | Jual instrument | `gas-term-service` | ✅ Active |
| `/close ORDER_ID` | Tutup posisi | `gas-term-service` | ✅ Active |
| `/chart SYMBOL TIMEFRAME` | Tampilkan chart | `gas-chart-service` | ✅ Active |
| `/portfolio` | Lihat portofolio & P&L | `gas-journal-service` | ✅ Active |
| `/risk` | Cek drawdown & risk metrics | `gas-risk-engine` | ✅ Active |
| `/share [pesan]` | Share sinyal ke follower | `gas-social-service` | ✅ Active |
| `/help` | Daftar command | local | ✅ Active |
| `@news [keyword]` | Berita terkini & kalender | `gas-calendar-news-service` | ✅ Active |
| `@research [topik]` | Analisis teknikal RAG | `gas-rag-technical` | ✅ Active |
| `@macro [topik]` | Analisis makro + sentimen | `gas-rag-macro` | ✅ Active |
| `@fundamental [topik]` | Data fundamental (emas, rates) | `gas-fundamental-data-service` | ✅ Active |
| `@pattern SYMBOL` | Deteksi pola chart | `gas-pattern-detector` | 🔜 Planned |
| `@quant SYMBOL` | Skor kuantitatif & sinyal | `gas-quant-orchestrator` | 🔜 Planned |
| `@backtest SYMBOL [strategy]` | Simulasi strategi | `gas-quant-backtester` | 🔜 Planned |
| `@smc SYMBOL` | Analisis Smart Money Concept | `gas-smc-engine` | 🔜 Planned |
| `@learn [topik]` | Panel edukasi / AI tutor | `gas-ai-orchestrator` + RAG | 🔜 Planned |
| `@ai "pertanyaan"` | Tanya AI bebas | `gas-ai-orchestrator` | ✅ Active |

---

## 🔥 Contoh Skenario

### Skenario 1: Analisis cepat
```
@ai "bandingkan performa emas dan bitcoin selama 3 krisis terakhir"
```

### Skenario 2: Eksekusi trading
```
/buy XAUUSD 0.1 sl:1990 tp:2020
```

### Skenario 3: Riset teknikal
```
@research "analisis SMC XAUUSD H4"
```

---

## 📁 Struktur Direktori

```
gas-terminal-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── routes.py                # REST + WebSocket endpoints
│   │   └── models.py                # Request/Response models
│   ├── core/
│   │   ├── command_parser.py        # Parser command teks → action
│   │   ├── router.py                # Routing command → service
│   │   └── exceptions.py
│   ├── panels/
│   │   ├── chart.py                  # Proxy ke chart-service
│   │   ├── news.py                   # Proxy ke news-service
│   │   ├── research.py               # Proxy ke RAG services
│   │   ├── portfolio.py              # Proxy ke journal-service
│   │   └── social.py                 # Proxy ke social-service
│   └── lib/
│       └── logger.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## 🚀 Implementasi Bertahap

1. **Fase 1** – Core Terminal: Command line + health check + execution proxy (✅ Fase ini)
2. **Fase 2** – News & Research: Integrasi panel news & RAG
3. **Fase 3** – Portofolio & Risiko: Panel portofolio + journal
4. **Fase 4** – Sosial & Kolaborasi: social feed, shared signals
5. **Fase 5** – Pendidikan: AI tutor, konten edukasi dari vector DB

---

## 📄 Lisensi & Kredit

**Hak Cipta © 2026 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang.

**🔥 GAS Terminal – The Bloomberg of Crypto & Forex**
