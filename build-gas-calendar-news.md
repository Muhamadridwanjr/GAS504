🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-calendar-news	API	9601	News & Macro Hub	Ambil data ekonomi (ForexFactory, dll) pakai ecocal. Data di-embed ke gas-vector-db untuk RAG.	Sumber → Calendar → DB → (User/RAG)							
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
echo "# gas-calendar-news" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-calendar-news.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-calendar-news.git
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
# 📰 GAS Calendar News Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Layer Tambahan (Data Fundamental)**  
Service yang menyediakan kalender ekonomi dan berita pasar secara real‑time dengan memanfaatkan library Python **`ecocal`** . Data yang diperoleh (event ekonomi, rilis data, berita pasar) disimpan di database PostgreSQL, dan secara periodik di‑embed untuk disimpan di `gas-vector-db`, sehingga dapat digunakan oleh `gas-rag-macro` untuk analisis sentimen dan konteks makroekonomi.

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

**gas-calendar-news-service** bertugas mengumpulkan data kalender ekonomi dari berbagai sumber menggunakan library **`ecocal`** . Library ini mendukung pengambilan data ekonomi dunia dengan detail lengkap (aktual, forecast, previous) serta berita pasar terkait . Data yang diperoleh kemudian:

- Disimpan di database PostgreSQL untuk keperluan query historis.
- Diolah menjadi ringkasan teks dan di‑embed untuk disimpan di `gas-vector-db`.
- Digunakan oleh `gas-rag-macro` untuk memberikan konteks makro dalam analisis.
- Dapat diakses oleh pengguna melalui REST API untuk ditampilkan di frontend (kalender ekonomi, berita terbaru).

Dengan pendekatan ini, seluruh ekosistem GAS memiliki akses ke informasi fundamental yang selalu up‑to‑date.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Sumber Data"
        EC[ecocal Library]
        FF[ForexFactory]
        INV[Investing.com]
    end

    subgraph "gas-calendar-news-service"
        API[REST API :9601]
        WORKER[Calendar Worker]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
        EMBED[Embedding Generator]
    end

    subgraph "Penyimpanan Vektor"
        VDB[gas-vector-db :9004]
    end

    subgraph "Konsumen"
        RAG[gas-rag-macro :9002]
        USER[Frontend / Terminal]
    end

    EC --> WORKER
    FF --> WORKER
    INV --> WORKER
    WORKER --> DB
    WORKER --> EMBED
    EMBED --> VDB
    API --> DB
    API --> CACHE
    CACHE --> API
    API -->|data mentah| USER
    VDB -->|ringkasan| RAG
```

### Komponen Utama
- **Calendar Worker** – Background job yang secara periodik menjalankan `ecocal` untuk mengambil data kalender terbaru .
- **PostgreSQL** – Menyimpan data mentah event dan berita.
- **Embedding Generator** – Mengubah event menjadi ringkasan teks dan mengirimkannya ke `gas-vector-db`.
- **REST API** – Endpoint untuk query data kalender dan berita.

---

## 🔄 Alur Kerja

### **Pengambilan Data oleh Worker**
1. **Scheduler** (misal cron setiap jam) memicu `Calendar Worker`.
2. Worker menginisialisasi `ecocal.Calendar` dengan parameter `startHorizon` dan `endHorizon` (misal H-7 sampai H+7) .
3. Library `ecocal` melakukan scraping multithreaded dari sumber eksternal .
4. Data mentah diproses:
   - Normalisasi field (tanggal, waktu, negara, dampak, dll.)
   - Konversi waktu ke UTC dan timezone lokal
   - Simpan ke tabel `economic_events` di PostgreSQL
5. Untuk setiap event penting (impact high/medium), buat ringkasan teks:
   > "Pada 15 Maret 2025, AS merilis data NFP dengan aktual 236K (forecast 210K, previous 205K). Dampak: High."
6. Ringkasan di‑embed menggunakan model (OpenAI/Vertex) dan dikirim ke `gas-vector-db` via endpoint `/collections/economic_events/documents` .

### **Pengambilan Data oleh Konsumen**
1. **User/Frontend** memanggil `GET /calendar` dengan parameter filter (negara, dampak, rentang waktu).
2. Service memeriksa cache Redis. Jika ada, kembalikan data dari cache.
3. Jika tidak ada, query database PostgreSQL.
4. Data dikembalikan dalam format JSON dan disimpan di cache dengan TTL tertentu.

### **Integrasi dengan RAG**
- `gas-rag-macro` dapat memanggil endpoint `/summary` untuk mendapatkan ringkasan event dalam rentang waktu tertentu, atau langsung melakukan query similarity ke `gas-vector-db` untuk mencari event relevan.

---

## ✨ Fitur Utama

- **Multi‑sumber**: Mendukung ForexFactory, Investing.com, dan sumber lain melalui library `ecocal` .
- **Data lengkap**: Aktual, forecast, previous, dampak, negara, kategori .
- **Filter fleksibel**: Berdasarkan negara, dampak (high/medium/low), tanggal, kategori.
- **Embedding otomatis**: Event penting di‑embed dan disimpan di vector DB untuk RAG .
- **Cache Redis**: Mempercepat akses data yang sering diminta.
- **Scheduler bawaan**: Worker dapat dijadwalkan secara periodik (setiap jam/hari).
- **API RESTful**: Dokumentasi otomatis via Swagger UI.

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Calendar Library:** `ecocal` (install via pip) 
- **Scraping (alternatif):** `Economic-Calendar-Parser`  atau `market-calendar-tool` 
- **Database:** PostgreSQL (SQLAlchemy + asyncpg)
- **Cache:** Redis (`redis.asyncio`)
- **Embedding:** `openai` atau `vertexai` library
- **Scheduling:** `apscheduler` atau cron job
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-calendar-news-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /calendar, /news, /summary
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── calendar_service.py       # Logika query calendar
│   │   ├── news_service.py           # Logika query berita
│   │   ├── summary_generator.py      # Buat ringkasan teks
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py                # SQLAlchemy models (EconomicEvent, News)
│   │   └── repositories/
│   │       ├── event_repo.py
│   │       └── news_repo.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_cache.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── ecocal_worker.py          # Worker menggunakan ecocal
│   │   ├── parser_factory.py          # Factory untuk berbagai sumber
│   │   └── scheduler.py               # Scheduler untuk worker
│   ├── embedding/
│   │   ├── __init__.py
│   │   ├── embedder.py                # Generate embedding
│   │   └── vector_client.py           # Client ke gas-vector-db
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   └── workers/                      # Background tasks
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
- `gas-vector-db` berjalan (untuk penyimpanan embedding)

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-calendar-news-service.git
   cd gas-calendar-news-service
   ```

2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements-dev.txt
   # Install ecocal
   pip install ecocal
   ```

4. Copy environment:
   ```bash
   cp .env.example .env
   # Isi DATABASE_URL, REDIS_URL, VECTOR_DB_URL, dll.
   ```

5. Jalankan PostgreSQL dan Redis (via Docker):
   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15-alpine
   docker run -d --name redis -p 6379:6379 redis
   ```

6. Buat database:
   ```bash
   createdb -h localhost -U postgres gas_calendar
   ```

7. Jalankan migration (jika menggunakan Alembic):
   ```bash
   alembic upgrade head
   ```

8. Jalankan service API:
   ```bash
   uvicorn src.main:app --reload --port 9601
   ```

9. Jalankan worker (di terminal terpisah):
   ```bash
   python src/ingestion/scheduler.py
   ```

### Dengan Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: gas_calendar
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  calendar-service:
    build: .
    ports:
      - "9601:9601"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pass@postgres:5432/gas_calendar
      - REDIS_URL=redis://redis:6379
      - VECTOR_DB_URL=http://gas-vector-db:9004
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
| `PORT` | 9601 | Port REST API |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@localhost:5432/gas_calendar | Koneksi database async |
| `REDIS_URL` | redis://localhost:6379 | Koneksi Redis |
| `CACHE_TTL` | 3600 | TTL cache (detik) |
| `VECTOR_DB_URL` | http://gas-vector-db:9004 | URL vector DB |
| `VECTOR_DB_COLLECTION` | economic_events | Nama koleksi di vector DB |
| `EMBEDDING_MODEL` | text-embedding-3-small | Model embedding (OpenAI) |
| `OPENAI_API_KEY` | (opsional) | Jika pakai OpenAI |
| `INGESTION_SCHEDULE` | "0 * * * *" | Jadwal cron untuk worker (setiap jam) |
| `ECOCAL_THREADS` | 20 | Jumlah thread untuk ecocal (multithreading)  |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

### **Public Endpoints**

#### `GET /calendar` – Mendapatkan daftar event ekonomi

**Parameter Query:**
- `country` (string, optional) – Kode negara (USD, EUR, GBP, dll.) 
- `importance` (string, optional) – `high`, `medium`, `low` (bisa multiple, dipisah koma)
- `from_date` (string, optional) – Tanggal mulai (YYYY-MM-DD)
- `to_date` (string, optional) – Tanggal akhir (YYYY-MM-DD)
- `limit` (int, optional) – Jumlah data (default 100)

**Response:**
```json
{
  "total": 25,
  "data": [
    {
      "id": "evt_123",
      "provider": "forex_factory",
      "title": "Non-Farm Employment Change",
      "country": "USD",
      "importance": "high",
      "time_utc": "2025-03-15T12:30:00Z",
      "actual_value": 236000,
      "forecast_value": 210000,
      "previous_value": 205000,
      "unit": "persons"
    }
  ]
}
```

#### `GET /news` – Mendapatkan berita pasar (opsional, jika ada)

#### `GET /summary` – Ringkasan event dalam periode tertentu (untuk RAG)

**Parameter Query:**
- `from_date` (string, required)
- `to_date` (string, required)
- `format` (string, optional) – `text` atau `json` (default `text`)

**Response (format text):**
```
Economic Events Summary (2025-03-15 to 2025-03-16):
- USD: Non-Farm Employment Change (High) actual 236K, forecast 210K, previous 205K
- EUR: CPI (Medium) actual 2.4%, forecast 2.3%, previous 2.2%
- GBP: BOE Interest Rate Decision (High) actual 5.25%, forecast 5.25%, previous 5.25%
```

### **Admin Endpoints (dengan API Key)**

#### `POST /ingest/run` – Menjalankan worker secara manual

#### `GET /health` – Health check
```json
{"status": "ok"}
```

---

## 🔗 Integrasi dengan Service Lain

- **`gas-vector-db` (9004)** – Menyimpan embedding ringkasan event untuk keperluan RAG .
- **`gas-rag-macro` (9002)** – Menggunakan data dari service ini untuk analisis makro dan sentimen.
- **`gas-gateway-api` (8000)** – Entry point dari pengguna, meneruskan request ke service ini.
- **`gas-fundamental-data-service` (9603)** – Dapat berbagi data fundamental (saling melengkapi).
- **`gas-journal-service` (8107)** – Mencatat penggunaan data kalender oleh pengguna (opsional).

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Integrasi mock dengan ecocal.
- Query database.
- Logika caching.
- Embedding dan pengiriman ke vector DB.
- Endpoint API.

---

## 👨‍💻 Pengembangan

### Menambah Sumber Data Baru
1. Buat parser baru di `ingestion/` yang mengimplementasikan `BaseParser`.
2. Tambahkan ke factory.
3. Pastikan output dinormalisasi sesuai model database.

### Contoh Penggunaan Ecocal
```python
from ecocal import Calendar

def fetch_events(start_date, end_date):
    ec = Calendar(
        startHorizon=start_date,
        endHorizon=end_date,
        withDetails=True,
        nbThreads=20,  # multithreading 
        preBuildCalendar=True
    )
    # ec memiliki atribut events
    return ec.events
```

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

Service ini menggunakan library **`ecocal`**  yang dikembangkan oleh Lucas Rodriguez dan dirilis di bawah lisensi MIT .

---

**🔥 GAS Calendar News Service – Sumber Informasi Makro Real‑time**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  