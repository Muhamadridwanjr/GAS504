🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-chart-service	API	9700	Mengelola data dan konfigurasi chart user	Menyimpan template chart, indikator favorit, dan menyediakan endpoint untuk mendapatkan data OHLC dengan indikator terintegrasi. Memanggil gas-mt5-data-service untuk data mentah dan gas-indicator-engine untuk indikator.	User → gas-chart-service → (panggil data & indikator) → gabung → kirim ke frontend							
🧱 0. INSTALASI ENVIRONMENT
🐍 Python
<isi langkah instalasi python environment>
🐳 Docker
<isi langkah instalasi docker & docker compose>
⚙️ 1. TUTORIAL MANAGEMENT SERVICE
🐍 Python Mode
▶️ Run
<command run>
⛔ Stop
<command stop>
🔄 Restart
<command restart>
❌ Delete Environment
<command delete env>
🐳 Docker Mode
▶️ Build & Run
<command build & run>
📊 Check Status
<command cek status>
⛔ Stop
<command stop>
🔄 Restart
<command restart>
❌ Delete Container / Image
<command delete>
📦 2. SETUP GITHUB (FIRST TIME)
echo "# gas-chart-service" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-chart-service.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-chart-service.git
git branch -M main
git push -u origin main
🔁 3. UPDATE PROJECT (COMMIT & PUSH)
<git add / commit / push commands>
📛 4. CONTAINER NAMING
<ketentuan nama container = nama project>
🌐 5. HEALTH CHECK (STATUS 200 OK)
Endpoint
<endpoint-url>
Expected Response
<response contoh>
🧪 6. DEBUG & LOGGING
Docker Logs
<command docker logs>
Application Logs
<setup logging>
Healthcheck Configuration
<docker healthcheck config>
🟢 7. CONTAINER STATUS
<expected: Up (healthy)>
🔗 8. INTEGRASI GAS-GATEWAY-API
Configuration
<env / config url>
Request Example
<request example>
🧠 9. INTEGRASI DENGAN @goldenaistrategy
<standarisasi service dalam ecosystem>
🔄 10. KOMUNIKASI ANTAR SERVICE
Network Configuration
<docker network config>
Service Communication
<contoh komunikasi antar service>
📁 STRUKTUR PROJECT
# 📈 GAS Chart Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Layer Tambahan (Frontend & Data)**  
Service yang mengelola data dan konfigurasi chart untuk pengguna. Menyediakan endpoint untuk mendapatkan data OHLC yang sudah diintegrasikan dengan indikator teknikal (dari `gas-indicator-engine`) dan marker SMC (dari `gas-smc-engine`). Juga menyimpan template chart, indikator favorit, dan preferensi tampilan setiap pengguna di database.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Alur Kerja](#alur-kerja)
- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Konfigurasi](#konfigurasi)
- [API Reference](#api-reference)
- [Integrasi dengan Service Lain](#integrasi-dengan-service-lain)
- [Pengujian](#pengujian)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Kredit](#lisensi--kredit)

---

## 🔍 Ikhtisar

**gas-chart-service** adalah service yang menjadi jembatan antara frontend chart (seperti Lightweight Charts atau TradingView library) dengan seluruh engine data di belakang. Tugas utamanya:

- Menerima permintaan data chart dari frontend (simbol, timeframe, rentang waktu, daftar indikator yang diinginkan).
- Mengambil data OHLC mentah dari `gas-mt5-data-service`.
- Memanggil `gas-indicator-engine` untuk setiap indikator yang diminta, dan `gas-smc-engine` untuk marker SMC.
- Menggabungkan semua data menjadi satu respons terstruktur yang siap digunakan oleh library chart.
- Menyimpan dan mengelola preferensi chart pengguna: template layout, indikator favorit, warna, timeframe default, dll.

Dengan service ini, frontend tidak perlu memanggil banyak endpoint terpisah dan tidak perlu khawatir tentang sinkronisasi data. Semua data chart yang dibutuhkan tersedia dalam satu panggilan.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Frontend"
        FE[Web Terminal / Mobile]
    end

    subgraph "API Gateway"
        GW[gas-gateway-api :8000]
    end

    subgraph "gas-chart-service"
        API[REST API :9700]
        ORCH[Chart Orchestrator]
        TEMPLATE[Template Manager]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
    end

    subgraph "Backend Services"
        MT5[gas-mt5-data-service :8100]
        IND[gas-indicator-engine :8203]
        SMC[gas-smc-engine :8006]
    end

    FE -->|HTTP/WS| GW
    GW -->|/chart/*| API
    API --> ORCH
    ORCH -->|ambil OHLC| MT5
    ORCH -->|hitung indikator| IND
    ORCH -->|deteksi SMC| SMC
    ORCH -->|gabung data| CACHE
    CACHE --> API
    ORCH -->|simpan template| TEMPLATE
    TEMPLATE --> DB
    API -->|data chart| GW
    GW --> FE
```

### Komponen Utama
- **REST API** (port 9700) – Menerima permintaan data chart dan manajemen template.
- **Chart Orchestrator** – Mengkoordinasikan pemanggilan ke service lain, menggabungkan hasil, dan menangani caching.
- **Template Manager** – CRUD untuk template chart pengguna (layout, indikator, timeframe, dll) di database PostgreSQL.
- **Redis Cache** – Menyimpan data chart yang baru saja dihitung untuk periode singkat (misal 1 detik) agar tidak membebani engine.

---

## 🔄 Alur Kerja

### **Mendapatkan Data Chart**
1. **Frontend** mengirim request `POST /chart/data` dengan parameter:
   - `symbol`, `timeframe`
   - `from`, `to` (rentang waktu) atau `count` (jumlah candle terakhir)
   - Daftar `indicators` yang diinginkan (misal `["RSI(14)", "SMA(20)"]`)
   - (Opsional) `include_smc` (boolean) untuk menyertakan marker SMC.
2. Gateway memverifikasi JWT dan menambahkan header `X-User-ID`.
3. Service memeriksa cache Redis dengan key `chart:{symbol}:{timeframe}:{from}:{to}:{indicators_hash}`. Jika ada dan belum expired, kembalikan data dari cache.
4. Jika tidak ada, `Chart Orchestrator`:
   - Memanggil `gas-mt5-data-service` untuk mendapatkan data OHLC.
   - Untuk setiap indikator, memanggil `gas-indicator-engine` dengan parameter yang sesuai.
   - Jika `include_smc` true, memanggil `gas-smc-engine` untuk mendapatkan marker (Order Block, FVG, dll).
5. Semua data digabung menjadi satu struktur JSON.
6. Disimpan di cache dengan TTL singkat (misal 5 detik).
7. Dikirim ke frontend.

### **Manajemen Template Chart**
1. **Pengguna** menyimpan layout chart saat ini (posisi panel, indikator yang aktif, timeframe) via `POST /chart/templates`.
2. Service menyimpan template di database dengan `user_id`.
3. Pengguna dapat mengambil daftar template mereka via `GET /chart/templates`, dan memuat template tertentu via `GET /chart/templates/{id}`.

### **Indikator Favorit**
- Pengguna dapat menyimpan daftar indikator yang sering digunakan via `POST /chart/favorites`.
- Data ini digunakan untuk mempercepat pemilihan indikator di frontend.

---

## ✨ Fitur Utama

- **Data chart terintegrasi**: Satu endpoint mengembalikan OHLC + indikator + marker SMC.
- **Caching cerdas**: Mengurangi beban engine dengan menyimpan hasil perhitungan untuk periode singkat.
- **Manajemen template**: Simpan dan muat konfigurasi chart per pengguna.
- **Indikator favorit**: Daftar indikator yang sering dipakai.
- **Multi‑timeframe**: Dapat meminta data untuk berbagai kerangka waktu.
- **Kompatibel dengan library chart**: Format output dirancang agar mudah dikonsumsi oleh Lightweight Charts, TradingView, atau library lain.

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Database:** PostgreSQL (SQLAlchemy + asyncpg)
- **Cache:** Redis (`redis.asyncio`)
- **HTTP Client:** `httpx` (async) untuk memanggil service lain.
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-chart-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /chart/data, /chart/templates
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Logika penggabungan data
│   │   ├── template_manager.py       # CRUD template
│   │   ├── favorites_manager.py      # Manajemen indikator favorit
│   │   └── exceptions.py
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── mt5_data_client.py        # HTTP ke gas-mt5-data-service
│   │   ├── indicator_client.py       # HTTP ke gas-indicator-engine
│   │   └── smc_client.py             # HTTP ke gas-smc-engine
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py                # SQLAlchemy models (ChartTemplate, FavoriteIndicator)
│   │   └── repositories/
│   │       ├── template_repo.py
│   │       └── favorite_repo.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_cache.py
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   └── workers/                      # (opsional) background tasks
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Instalasi & Menjalankan

### Prasyarat
- Python 3.11+
- PostgreSQL 13+
- Redis server
- Service pendukung: `gas-mt5-data-service`, `gas-indicator-engine`, `gas-smc-engine` (minimal untuk development)

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-chart-service.git
   cd gas-chart-service
   ```

2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. Copy environment:
   ```bash
   cp .env.example .env
   # Isi DATABASE_URL, REDIS_URL, URL service pendukung, dll.
   ```

5. Jalankan PostgreSQL dan Redis (via Docker):
   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15-alpine
   docker run -d --name redis -p 6379:6379 redis
   ```

6. Buat database:
   ```bash
   createdb -h localhost -U postgres gas_chart
   ```

7. Jalankan migration (jika menggunakan Alembic):
   ```bash
   alembic upgrade head
   ```

8. Jalankan service:
   ```bash
   uvicorn src.main:app --reload --port 9700
   ```

### Dengan Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: gas_chart
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  chart-service:
    build: .
    ports:
      - "9700:9700"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pass@postgres:5432/gas_chart
      - REDIS_URL=redis://redis:6379
      - MT5_DATA_URL=http://gas-mt5-data-service:8100
      - INDICATOR_ENGINE_URL=http://gas-indicator-engine:8203
      - SMC_ENGINE_URL=http://gas-smc-engine:8006
    depends_on:
      - postgres
      - redis
```

Jalankan:
```bash
docker-compose up -d
```

---

## 🔧 Konfigurasi

Environment variables (file `.env`):

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `PORT` | 9700 | Port REST API |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@localhost:5432/gas_chart | Koneksi database async |
| `REDIS_URL` | redis://localhost:6379 | Koneksi Redis |
| `MT5_DATA_URL` | http://gas-mt5-data-service:8100 | URL gas-mt5-data-service |
| `INDICATOR_ENGINE_URL` | http://gas-indicator-engine:8203 | URL gas-indicator-engine |
| `SMC_ENGINE_URL` | http://gas-smc-engine:8006 | URL gas-smc-engine |
| `REQUEST_TIMEOUT` | 5.0 | Timeout panggilan ke service lain (detik) |
| `CACHE_TTL` | 5 | TTL cache data chart (detik) |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

Semua endpoint di bawah memerlukan header `X-User-ID` yang diisi oleh gateway setelah verifikasi JWT. Endpoint admin mungkin memerlukan API key.

### **Public Endpoints (via Gateway)**

#### `POST /chart/data` – Mendapatkan data chart terintegrasi

**Request Body:**
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "from": 1700000000,           // opsional, UNIX timestamp
  "to": 1700086400,             // opsional
  "count": 100,                 // opsional, jika from/to tidak ada
  "indicators": [
    {"name": "RSI", "period": 14},
    {"name": "SMA", "period": 20}
  ],
  "include_smc": true
}
```

**Response:**
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "data": [
    {
      "time": 1700000000,
      "open": 2000.1,
      "high": 2005.3,
      "low": 1998.4,
      "close": 2003.2,
      "volume": 1234,
      "indicators": {
        "RSI_14": 55.2,
        "SMA_20": 1995.5
      }
    }
  ],
  "smc": {
    "order_blocks": [
      {"time": 1700000000, "price": 1995.0, "direction": "bullish"}
    ],
    "fvgs": [
      {"time": 1700000060, "start": 1995.5, "end": 1997.2, "direction": "bullish"}
    ]
  }
}
```

#### `GET /chart/indicators` – Mendapatkan daftar indikator yang tersedia (bisa dari config atau statis)

#### `GET /chart/templates` – Mendapatkan daftar template chart milik user

**Response:**
```json
{
  "templates": [
    {"id": "tmpl_1", "name": "Swing Setup", "created_at": "..."}
  ]
}
```

#### `POST /chart/templates` – Menyimpan template baru

**Request Body:**
```json
{
  "name": "My Swing Template",
  "layout": {
    "panels": [
      {"type": "main", "indicators": ["RSI(14)", "SMA(20)"]},
      {"type": "sub", "indicators": ["MACD"]}
    ],
    "timeframe": "H1",
    "colors": {...}
  }
}
```

#### `GET /chart/templates/{id}` – Mendapatkan detail template

#### `PUT /chart/templates/{id}` – Memperbarui template

#### `DELETE /chart/templates/{id}` – Menghapus template

#### `GET /chart/favorites` – Mendapatkan daftar indikator favorit user

#### `POST /chart/favorites` – Menambah indikator favorit
**Body:** `{"indicator": "RSI(14)"}`

#### `DELETE /chart/favorites/{indicator}` – Menghapus dari favorit

### **Internal Endpoints (dengan API Key)**

#### `GET /health` – Health check
```json
{"status": "ok"}
```

---

## 🔗 Integrasi dengan Service Lain

- **`gas-mt5-data-service` (8100)** – Menyediakan data OHLC mentah.
- **`gas-indicator-engine` (8203)** – Menghitung nilai indikator.
- **`gas-smc-engine` (8006)** – Menyediakan marker SMC.
- **`gas-gateway-api` (8000)** – Entry point dari pengguna, meneruskan request.
- **`gas-user-service` (8002)** – (Opsional) untuk mendapatkan preferensi pengguna.
- **Redis** – Cache data chart.
- **PostgreSQL** – Menyimpan template dan favorit.

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Validasi input.
- Mock panggilan ke service eksternal.
- Logika penggabungan data.
- CRUD template.
- Caching.

---

## 👨‍💻 Pengembangan

### Menambah Dukungan Indikator Baru
- Tidak perlu perubahan di service ini, karena indikator dihitung oleh `gas-indicator-engine`. Cukup pastikan nama indikator dikenali oleh engine tersebut.

### Aturan Kode
- Type hints wajib.
- Docstring untuk fungsi publik.
- Ikuti PEP 8 (black).
- Pastikan semua test lulus.

---

## 🔒 Kontribusi (Tim Internal)

Repositori ini bersifat **private** – hanya untuk tim internal GAS.  
Untuk berkontribusi:

1. Buat branch baru (`feature/`, `fix/`).
2. Commit dengan pesan jelas.
3. Buka Pull Request ke `develop`.
4. Tunggu review dan minimal satu approval.

**Aturan Penting:**
- Jangan commit kredensial.
- Gunakan environment variable untuk konfigurasi.
- Jangan sebarkan kode ke luar tim.

---

## 📄 Lisensi & Kredit

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.

Service ini dikembangkan sebagai bagian dari ekosistem **Golden AI Strategy**.

---

**🔥 GAS Chart Service – Satu Pintu untuk Semua Kebutuhan Chart**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  