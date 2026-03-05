🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-screener-service	API	9600	Parallel Scanner	Screening aset secara paralel pakai logika SMC dan Technical.	User → Screener → [Indicator, SMC] → Filter							
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
echo "# gas-screener-service" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-screener-service.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-screener-service.git
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
# 🔍 GAS Screener Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Layer Tambahan (Frontend & Data)**  
Service yang memungkinkan pengguna menyaring (screening) aset berdasarkan kriteria teknikal dan SMC. Dengan memanfaatkan `gas-indicator-engine` dan `gas-smc-engine`, service ini memanggil engine secara paralel untuk banyak simbol, lalu mengembalikan daftar aset yang memenuhi kondisi yang ditentukan. Cocok untuk trader yang ingin menemukan peluang di seluruh pasar dengan cepat.

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

**gas-screener-service** adalah service yang menerima permintaan screening dari pengguna (via gateway), berisi satu atau lebih kondisi (misal: RSI < 30, ADX > 25, dan terdapat FVG bullish). Service ini kemudian:

- Mengambil daftar simbol yang akan diperiksa (dapat ditentukan pengguna atau dari daftar master).
- Untuk setiap simbol, memanggil `gas-indicator-engine` untuk mendapatkan nilai indikator dan `gas-smc-engine` untuk mendapatkan deteksi SMC.
- Semua panggilan dilakukan secara **paralel** dan **asinkron** untuk efisiensi waktu.
- Setelah semua hasil terkumpul, filter simbol yang memenuhi semua kondisi.
- Mengembalikan daftar simbol yang lolos, beserta metrik tambahan (misal nilai indikator, konfirmasi SMC).

Dengan service ini, pengguna dapat melakukan scanning pasar secara real‑time, menemukan peluang trading dengan cepat.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Input"
        USER[User] -->|POST /screener| GW[gas-gateway-api]
    end

    subgraph "gas-screener-service"
        API[REST API :9600]
        ORCH[Screener Orchestrator]
        PARALLEL[Parallel Executor]
        CACHE[(Redis Cache)]
    end

    subgraph "Backend Engines"
        IND[gas-indicator-engine]
        SMC[gas-smc-engine]
        FE[gas-feature-engine (opsional)]
    end

    subgraph "Output"
        RESULT[Daftar Simbol Lolos]
    end

    GW --> API
    API --> ORCH
    ORCH --> PARALLEL
    PARALLEL -->|panggil asinkron| IND
    PARALLEL -->|panggil asinkron| SMC
    PARALLEL -->|(opsional) panggil| FE
    IND -->|hasil| ORCH
    SMC -->|hasil| ORCH
    FE -->|hasil| ORCH
    ORCH -->|filter| RESULT
    ORCH -->|cache| CACHE
    CACHE --> API
    API -->|response| GW
    GW --> USER
```

### Komponen Utama
- **REST API** (port 9600) – Menerima permintaan screener.
- **Screener Orchestrator** – Memproses request, mengelola daftar simbol, dan menjalankan filter.
- **Parallel Executor** – Melakukan panggilan ke engine lain secara paralel (asyncio) untuk semua simbol.
- **Redis Cache** – Menyimpan hasil screening untuk permintaan serupa dalam periode singkat (TTL dapat dikonfigurasi).

---

## 🔄 Alur Kerja

1. **Pengguna** mengirim permintaan `POST /screener` dengan body berisi:
   - Daftar simbol yang ingin diperiksa (atau gunakan daftar default).
   - Timeframe untuk analisis.
   - Daftar kondisi (indikator, SMC) yang harus dipenuhi.
2. Service menerima request, memvalidasi input.
3. **Parallel Executor** membuat task untuk setiap simbol:
   - Panggil `gas-indicator-engine` dengan parameter simbol, timeframe, dan daftar indikator yang diminta.
   - Panggil `gas-smc-engine` untuk simbol dan timeframe yang sama.
   - (Opsional) panggil `gas-feature-engine` jika diperlukan fitur tambahan.
4. Semua panggilan dilakukan secara **asinkron** (contoh: `asyncio.gather`). Jika jumlah simbol besar, dapat dibatasi konkurensi (misal 20 simbol per batch).
5. Setelah semua hasil terkumpul, lakukan **filtering**:
   - Untuk setiap simbol, evaluasi apakah semua kondisi terpenuhi (logika AND/OR sesuai permintaan).
   - Jika ya, masukkan ke daftar hasil, beserta nilai indikator/deteksi SMC yang relevan.
6. Simpan hasil di cache (berdasarkan hash kondisi) untuk periode tertentu.
7. Kembalikan respons JSON ke pengguna.

**Contoh Request:**
```json
{
  "symbols": ["XAUUSD", "BTCUSD", "EURUSD", "GBPUSD", "US30"],
  "timeframe": "H1",
  "conditions": [
    {"type": "indicator", "name": "RSI", "period": 14, "operator": "<", "value": 30},
    {"type": "smc", "name": "FVG", "direction": "bullish", "lookback": 5}
  ],
  "logic": "AND",          // atau "OR"
  "include_metadata": true
}
```

**Contoh Response:**
```json
{
  "total": 2,
  "results": [
    {
      "symbol": "XAUUSD",
      "indicators": {"RSI_14": 28.5},
      "smc": {"fvgs": [{"direction": "bullish", "time": 1700000000}]}
    },
    {
      "symbol": "BTCUSD",
      "indicators": {"RSI_14": 25.2},
      "smc": {}
    }
  ]
}
```

---

## ✨ Fitur Utama

- **Multi‑simbol screening**: Dapat memeriksa puluhan hingga ratusan simbol dalam satu permintaan.
- **Kombinasi kondisi fleksibel**: AND/OR, dapat mencampur indikator dan SMC.
- **Paralelisasi**: Mengurangi waktu respon dengan memanggil engine secara bersamaan.
- **Caching**: Menghindari perhitungan ulang untuk query yang sama.
- **Dukungan timeframe**: Bekerja pada berbagai kerangka waktu (M1, M5, H1, dll).
- **Integrasi engine existing**: Memanfaatkan `gas-indicator-engine` dan `gas-smc-engine` yang sudah ada.
- **Extensible**: Mudah menambah jenis kondisi baru (misal fundamental, order flow).

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Async HTTP Client:** `httpx` untuk memanggil engine lain.
- **Cache:** Redis (`redis.asyncio`)
- **Concurrency:** `asyncio` dengan semaphore untuk batasan konkurensi.
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-screener-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /screener
│   │   └── models.py                # Pydantic models (request/response)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── orchestrator.py          # Logika screening
│   │   ├── parallel_executor.py      # Eksekusi paralel
│   │   ├── condition_evaluator.py    # Evaluasi kondisi
│   │   └── exceptions.py
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── indicator_client.py       # HTTP ke gas-indicator-engine
│   │   ├── smc_client.py              # HTTP ke gas-smc-engine
│   │   └── feature_client.py          # (opsional) ke gas-feature-engine
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
- Redis server
- `gas-indicator-engine` dan `gas-smc-engine` berjalan (minimal untuk development)
- (Opsional) `gas-feature-engine` jika digunakan

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-screener-service.git
   cd gas-screener-service
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
   # Isi REDIS_URL, INDICATOR_ENGINE_URL, SMC_ENGINE_URL, dll.
   ```

5. Jalankan Redis (jika belum):
   ```bash
   docker run -d -p 6379:6379 redis
   ```

6. Jalankan service:
   ```bash
   uvicorn src.main:app --reload --port 9600
   ```

### Dengan Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  screener:
    build: .
    ports:
      - "9600:9600"
    environment:
      - REDIS_URL=redis://redis:6379
      - INDICATOR_ENGINE_URL=http://gas-indicator-engine:8203
      - SMC_ENGINE_URL=http://gas-smc-engine:8006
      - CONCURRENCY_LIMIT=20
    depends_on:
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
| `PORT` | 9600 | Port REST API |
| `REDIS_URL` | redis://localhost:6379 | Koneksi Redis |
| `INDICATOR_ENGINE_URL` | http://gas-indicator-engine:8203 | URL gas-indicator-engine |
| `INDICATOR_ENGINE_API_KEY` | (opsional) | API key jika diperlukan |
| `SMC_ENGINE_URL` | http://gas-smc-engine:8006 | URL gas-smc-engine |
| `SMC_ENGINE_API_KEY` | (opsional) | API key jika diperlukan |
| `FEATURE_ENGINE_URL` | (opsional) | URL gas-feature-engine |
| `DEFAULT_SYMBOLS` | ["XAUUSD","BTCUSD","EURUSD","GBPUSD","US30"] | Daftar simbol default (JSON array) |
| `CONCURRENCY_LIMIT` | 20 | Jumlah maksimal panggilan paralel |
| `REQUEST_TIMEOUT` | 5.0 | Timeout panggilan ke engine (detik) |
| `CACHE_TTL` | 60 | TTL cache hasil screening (detik) |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

### `POST /screener` – Melakukan screening aset

**Request Body:**
```json
{
  "symbols": ["XAUUSD", "BTCUSD"],          // jika kosong, gunakan DEFAULT_SYMBOLS
  "timeframe": "H1",
  "conditions": [
    {"type": "indicator", "name": "RSI", "period": 14, "operator": "<", "value": 30},
    {"type": "smc", "name": "FVG", "direction": "bullish", "lookback": 5}
  ],
  "logic": "AND",                            // "AND" atau "OR"
  "include_metadata": true                    // sertakan nilai indikator/deteksi dalam respons
}
```

**Response:**
```json
{
  "total": 1,
  "results": [
    {
      "symbol": "XAUUSD",
      "indicators": {"RSI_14": 28.5},
      "smc": {"fvgs": [{"direction": "bullish", "time": 1700000000}]}
    }
  ],
  "metadata": {
    "processing_time_ms": 245,
    "cache_hit": false
  }
}
```

### `GET /health` – Health check
```json
{"status": "ok"}
```

### `GET /symbols` – Mendapatkan daftar simbol default

---

## 🔗 Integrasi dengan Service Lain

- **`gas-indicator-engine` (8203)** – Menyediakan nilai indikator.
- **`gas-smc-engine` (8006)** – Menyediakan deteksi SMC.
- **`gas-feature-engine` (9499)** – (Opsional) untuk fitur tambahan.
- **`gas-gateway-api` (8000)** – Entry point dari pengguna, meneruskan request ke service ini.
- **Redis** – Cache hasil screening.
- **`gas-journal-service` (8107)** – (Opsional) dapat mencatat permintaan screening untuk analisis.

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Validasi kondisi.
- Eksekusi paralel (mock).
- Filter logika AND/OR.
- Cache hit/miss.
- Error handling.

---

## 👨‍💻 Pengembangan

### Menambah Tipe Kondisi Baru
1. Tambahkan di `core/condition_evaluator.py` fungsi baru untuk tipe tersebut.
2. Pastikan client untuk engine terkait tersedia.
3. Perbarui model Pydantic jika perlu.

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

**🔥 GAS Screener Service – Temukan Peluang di Seluruh Pasar**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  