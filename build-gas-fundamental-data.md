🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-fundamental-data	API	9603	Macro Database	Simpan data suku bunga, GDP, hingga cadangan emas untuk validasi fundamental.	User/Service → Fundamental → DB							
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
echo "# gas-fundamental-data" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-fundamental-data.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-fundamental-data.git
git branch -M main
git push -u origin main🔁 3. UPDATE PROJECT (COMMIT & PUSH)
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
# 📊 GAS Fundamental Data Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Layer Tambahan (Data Fundamental)**  
Service yang menyediakan data fundamental ekonomi untuk berbagai aset, seperti suku bunga, produk domestik bruto (GDP), inflasi, cadangan emas, data ketenagakerjaan, dan indikator makro lainnya. Data ini digunakan oleh `gas-rag-macro` untuk analisis sentimen, oleh `gas-quant-orchestrator` sebagai fitur tambahan, serta oleh pengguna untuk validasi fundamental sebelum mengambil keputusan trading.

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

**gas-fundamental-data-service** adalah service yang mengelola data fundamental ekonomi secara terpusat. Data yang disimpan mencakup:

- **Suku bunga** bank sentral (The Fed, ECB, BOJ, dll.)
- **Produk Domestik Bruto (GDP)** – kuartalan, tahunan
- **Inflasi** – CPI, PPI, dll.
- **Ketenagakerjaan** – NFP, tingkat pengangguran
- **Cadangan emas** bank sentral
- **Data komoditas** – produksi, persediaan
- **Data kripto** – supply, hash rate (opsional)

Data ini dapat diambil dari sumber eksternal (misal FRED API, World Bank, Investing.com) secara periodik atau dimasukkan secara manual melalui endpoint admin. Service menyediakan REST API untuk query data berdasarkan simbol, indikator, dan rentang waktu. Selain itu, data juga dapat diekspor dalam bentuk ringkasan teks untuk keperluan RAG.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Sumber Data Eksternal"
        FRED[FRED API]
        WB[World Bank API]
        MANUAL[Admin Input]
    end

    subgraph "gas-fundamental-data-service"
        API[REST API :9603]
        INGEST[Data Ingestor]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
        SUMMARY[Summary Generator]
    end

    subgraph "Konsumen"
        RAG[gas-rag-macro]
        QUANT[gas-quant-orchestrator]
        USER[Pengguna / Frontend]
    end

    FRED --> INGEST
    WB --> INGEST
    MANUAL --> API
    INGEST --> DB
    API --> DB
    API --> CACHE
    DB --> SUMMARY
    SUMMARY --> API
    API -->|data mentah| QUANT
    API -->|ringkasan| RAG
    API -->|query| USER
```

### Komponen Utama
- **REST API** (port 9603) – Endpoint untuk query data fundamental dan administrasi.
- **Data Ingestor** – Background worker yang secara periodik mengambil data dari sumber eksternal dan memperbarui database.
- **PostgreSQL** – Penyimpanan utama data fundamental, dengan tabel yang dioptimalkan untuk query time‑series.
- **Redis Cache** – Menyimpan hasil query yang sering diminta untuk mengurangi beban database.
- **Summary Generator** – Membuat ringkasan tekstual dari data untuk keperluan RAG (dapat dipicu secara berkala atau on‑demand).

---

## 🔄 Alur Kerja

### **Pengambilan Data oleh Konsumen**
1. **Konsumen** (misal `gas-rag-macro`) mengirim request `GET /fundamental/{symbol}` dengan parameter indikator dan rentang waktu.
2. Service memeriksa cache Redis berdasarkan key `{symbol}:{indicator}:{date_range}`. Jika ada dan belum expired, kembalikan data dari cache.
3. Jika tidak ada, query database PostgreSQL.
4. Data dikembalikan dalam format JSON, dan disimpan ke cache dengan TTL tertentu.
5. Untuk keperluan RAG, konsumen dapat meminta ringkasan teks via endpoint `GET /fundamental/{symbol}/summary`.

### **Ingestion Data dari Sumber Eksternal**
- **Scheduler** (misal cron) memicu worker setiap hari/jam.
- Worker memanggil API eksternal (FRED, World Bank) untuk indikator yang dikonfigurasi.
- Data baru di-insert ke database, dengan mekanisme upsert (jika sudah ada, update nilai terbaru).
- Setelah selesai, cache untuk indikator terkait di‑invalidate (atau diupdate).

### **Input Manual (Admin)**
- Admin dapat menambah/mengubah data melalui endpoint `POST /fundamental` dengan API key internal.

---

## ✨ Fitur Utama

- **Multi‑indikator**: Mendukung berbagai jenis data fundamental (suku bunga, GDP, inflasi, dll.)
- **Query fleksibel**: Filter berdasarkan simbol, indikator, rentang waktu (dari tanggal, ke tanggal, atau jumlah data terakhir).
- **Ringkasan teks**: Menghasilkan deskripsi naratif dari data untuk RAG.
- **Cache Redis**: Mempercepat akses data yang sering diminta.
- **Ingestion otomatis**: Dapat mengambil data dari sumber eksternal secara periodik.
- **Admin endpoints**: Untuk input manual dan manajemen data.
- **Versioning data**: Menyimpan riwayat perubahan (jika diperlukan).

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Database:** PostgreSQL (SQLAlchemy + asyncpg)
- **Cache:** Redis (`redis.asyncio`)
- **HTTP Client:** `httpx` (untuk mengambil data eksternal)
- **Scheduling:** `apscheduler` atau cron job
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-fundamental-data-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /fundamental
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── data_service.py           # Logika query dan manajemen data
│   │   ├── summary_generator.py      # Buat ringkasan teks
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py                # SQLAlchemy models (tabel fundamental_data)
│   │   └── repositories/
│   │       └── fundamental_repo.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_cache.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   ├── base.py                  # Base class untuk sumber eksternal
│   │   ├── fred.py                   # FRED API client
│   │   ├── worldbank.py               # World Bank API client
│   │   └── scheduler.py               # Worker untuk ingestion periodik
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

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-fundamental-data-service.git
   cd gas-fundamental-data-service
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
   # Isi DATABASE_URL, REDIS_URL, API keys eksternal, dll.
   ```

5. Jalankan PostgreSQL dan Redis (via Docker):
   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15-alpine
   docker run -d --name redis -p 6379:6379 redis
   ```

6. Buat database:
   ```bash
   createdb -h localhost -U postgres gas_fundamental
   ```

7. Jalankan migration (jika menggunakan Alembic):
   ```bash
   alembic upgrade head
   ```

8. Jalankan service:
   ```bash
   uvicorn src.main:app --reload --port 9603
   ```

9. (Opsional) Jalankan scheduler ingestion:
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
      POSTGRES_DB: gas_fundamental
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  fundamental-service:
    build: .
    ports:
      - "9603:9603"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pass@postgres:5432/gas_fundamental
      - REDIS_URL=redis://redis:6379
      - FRED_API_KEY=your_key
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
| `PORT` | 9603 | Port REST API |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@localhost:5432/gas_fundamental | Koneksi database async |
| `REDIS_URL` | redis://localhost:6379 | Koneksi Redis |
| `CACHE_TTL` | 3600 | TTL cache (detik) |
| `FRED_API_KEY` | (opsional) | API key FRED (Federal Reserve Economic Data) |
| `WORLD_BANK_API_KEY` | (opsional) | API key World Bank |
| `INGESTION_SCHEDULE` | "0 2 * * *" | Jadwal cron untuk ingestion otomatis |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

### **Public Endpoints (via Gateway)**

#### `GET /fundamental/{symbol}` – Mendapatkan data fundamental untuk suatu aset

**Parameter Query:**
- `indicator` (string, required) – Nama indikator (misal `interest_rate`, `gdp`, `cpi`).
- `from` (int, optional) – UNIX timestamp awal.
- `to` (int, optional) – UNIX timestamp akhir.
- `limit` (int, optional) – Jumlah data terakhir (default 100, maks 1000).

**Response:**
```json
{
  "symbol": "XAUUSD",
  "indicator": "central_bank_gold_reserves",
  "data": [
    {"time": 1700000000, "value": 8133.5, "unit": "tonnes"},
    {"time": 1700086400, "value": 8140.2}
  ]
}
```

#### `GET /fundamental/{symbol}/summary` – Mendapatkan ringkasan teks untuk suatu indikator (berguna untuk RAG)

**Parameter Query:**
- `indicator` (string, required)
- `period` (string, optional) – `day`, `week`, `month`, `year` (default `month`)

**Response:**
```json
{
  "symbol": "XAUUSD",
  "indicator": "interest_rate",
  "summary": "The Federal Reserve maintained interest rates at 5.25% in March 2025, marking the fifth consecutive hold. Market expectations for rate cuts have shifted to mid-2025.",
  "period": "month"
}
```

### **Admin Endpoints (dengan API Key)**

#### `POST /fundamental` – Menambah atau memperbarui data fundamental
**Request Body:**
```json
{
  "symbol": "XAUUSD",
  "indicator": "central_bank_gold_reserves",
  "time": 1700000000,
  "value": 8133.5,
  "unit": "tonnes",
  "source": "FRED"
}
```

#### `POST /fundamental/batch` – Batch upsert.

#### `DELETE /fundamental/{id}` – Hapus data.

### **Health**
#### `GET /health`
```json
{"status": "ok"}
```

---

## 🔗 Integrasi dengan Service Lain

- **`gas-rag-macro` (9002)** – Menggunakan data fundamental untuk analisis makro dan sentimen. Memanggil endpoint `/summary` untuk mendapatkan ringkasan teks.
- **`gas-quant-orchestrator` (9500)** – Dapat menggunakan data fundamental sebagai fitur tambahan (misal suku bunga sebagai input regime).
- **`gas-calendar-news-service` (9601)** – Dapat berbagi data ekonomi (misal rilis data) dengan fundamental service.
- **`gas-data-ingestor` (9604)** – Dapat menyediakan data historis fundamental yang lebih panjang.
- **`gas-journal-service` (8107)** – Mencatat penggunaan data fundamental oleh pengguna (opsional).

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Query database.
- Logika caching.
- Ringkasan teks.
- Validasi input.
- Integrasi mock dengan API eksternal.

---

## 👨‍💻 Pengembangan

### Menambah Sumber Data Eksternal
1. Buat kelas baru di `ingestion/` yang mewarisi `BaseSource`.
2. Implementasikan metode `fetch(indicator, from_time, to_time)`.
3. Daftarkan di scheduler.

### Menambah Indikator Baru
- Cukup tambahkan di database, tidak perlu perubahan kode (karena indikator hanya string). Namun pastikan ada logika untuk mengambil data dari sumber eksternal.

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

**🔥 GAS Fundamental Data Service – Pilar Analisis Makro**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  