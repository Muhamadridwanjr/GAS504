# ⏰ GAS Alert Engine

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Mesin pemantau kondisi pasar realtime untuk notifikasi personal pengguna.**  
> Service ini memungkinkan pengguna membuat aturan (alert) berbasis harga, indikator, atau struktur SMC. Setiap kali data pasar baru masuk (tick atau candle), engine mengevaluasi semua alert yang relevan dan mengirim notifikasi ke `gas-notification-service` jika kondisi terpenuhi.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Alur Kerja](#alur-kerja)
- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi Environment](#instalasi-environment)
- [Tutorial: Run, Stop, Delete, Restart](#tutorial-run-stop-delete-restart)
  - [Mode Python (Development)](#mode-python-development)
  - [Mode Docker (Production)](#mode-docker-production)
- [Konfigurasi](#konfigurasi)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Pengujian](#pengujian)
- [Tutorial: Push ke GitHub (Pertama Kali)](#tutorial-push-ke-github-pertama-kali)
- [Tutorial: Commit & Update Project ke GitHub](#tutorial-commit--update-project-ke-github)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)

---

## 🔍 Ikhtisar

**gas-alert-engine** adalah service yang mengelola **alert buatan pengguna** (analisa mandiri). Pengguna dapat mendefinisikan kondisi seperti:

- Harga menembus level tertentu.
- Indikator teknikal mencapai nilai tertentu (RSI < 30, MACD cross).
- Struktur SMC terdeteksi (Order Block, FVG, BOS, CHoCH).
- Kombinasi kondisi (AND/OR).

Setiap kali ada data pasar baru (tick atau candle) dari `gas-market-data-processor`, engine akan mengevaluasi semua alert yang aktif. Jika kondisi terpenuhi, engine akan mengirim permintaan notifikasi ke `gas-notification-service` (Telegram, WebSocket, email).

Service ini dirancang untuk **realtime**, **skalabel**, dan **mendukung jutaan alert** dengan penggunaan Redis sebagai antrian dan penyimpanan sementara kondisi.

---

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌────────────────────────────────────┐
│ Market Data     │     │         gas-alert-engine           │
│ (Redis Pub/Sub) │────▶│  ┌──────────┐  ┌───────────────┐  │
└─────────────────┘     │  │  Worker  │  │   Evaluator   │  │
                        │  │  (consume│──│    Engine     │  │
                        │  │   data)  │  └───────┬───────┘  │
                        │  └──────────┘          │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │        PostgreSQL           │  │
                        │  │  (alerts definitions)       │  │
                        │  └─────────────────────────────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │   Redis (queue + cache)     │  │
                        │  └─────────────────────────────┘  │
                        └────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │   gas-notification-service  │
                        │   (Telegram, WS, Email)     │
                        └─────────────────────────────┘
```

### Komponen Utama

| Komponen | Deskripsi |
|----------|-----------|
| **Worker** | Berlangganan ke channel Redis `market:data` (dari `gas-market-data-processor`). Setiap ada data baru (tick/OHLC), worker mengambil semua alert yang relevan untuk simbol dan timeframe tersebut. |
| **Evaluator Engine** | Menerima alert dan data pasar, mengeksekusi kondisi menggunakan operator mapping (aman, tanpa `eval`). Hasilnya (true/false) digunakan untuk menentukan apakah alert terpicu. |
| **PostgreSQL** | Menyimpan definisi alert (user, kondisi, simbol, timeframe, status aktif, dll). |
| **Redis** | Cache untuk alert aktif per simbol/timeframe agar evaluasi cepat, juga untuk queue notifikasi. |

---

## 🔄 Alur Kerja

### 1. **Pengguna Membuat Alert**
   - User mengirim request `POST /alerts` (via gateway) dengan body berisi kondisi (format JSON).
   - Alert disimpan di PostgreSQL dengan status `active`.
   - Engine memperbarui cache Redis untuk simbol/timeframe tersebut.

### 2. **Data Pasar Masuk**
   - `gas-market-data-processor` mempublikasikan data OHLC baru ke Redis channel `market:data`.
   - Format pesan: `{ "symbol": "XAUUSD", "timeframe": "M1", "ohlc": {...}, "indicators": {...}, "smc": {...} }`

### 3. **Evaluasi Alert**
   - Worker `gas-alert-engine` menerima pesan.
   - Dari Redis, ambil semua ID alert yang aktif untuk `symbol` dan `timeframe` tersebut.
   - Untuk setiap alert, ambil definisi lengkap dari cache atau DB, lalu evaluasi kondisi dengan data terkini.
   - Jika kondisi terpenuhi:
     - Kirim task ke Redis queue `notifications`.
     - Tandai alert agar tidak terpicu lagi dalam periode tertentu (cooldown).

### 4. **Notifikasi**
   - `gas-notification-service` mengonsumsi queue `notifications`.
   - Mengirim notifikasi sesuai preferensi user (Telegram, WebSocket, email).

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Multi‑kondisi** | Kondisi kompleks dengan operator AND/OR, nested |
| **Dukungan indikator** | RSI, MACD, dll — evaluasi otomatis |
| **Dukungan SMC** | FVG, OB, BOS, CHoCH — deteksi struktur |
| **Realtime evaluasi** | Setiap tick/candle baru langsung dievaluasi |
| **Cooldown** | Mencegah notifikasi berulang dalam waktu singkat |
| **CRUD Alert** | Buat, baca, update, hapus, aktifkan/nonaktifkan |
| **History notifikasi** | Catatan kapan alert terpicu |
| **Skalabilitas** | Redis cache + queue, bisa di‑scale horizontal |

---

## 🛠️ Teknologi

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| Python | 3.11+ | Bahasa pemrograman utama |
| FastAPI | 0.109.0 | Web framework untuk API |
| SQLAlchemy | 2.0.25 | ORM database (async) |
| asyncpg | 0.29.0 | Driver PostgreSQL async |
| Redis | 5.0.1 | Cache, pub/sub, queue |
| Pydantic | 2.5.3 | Validasi data |
| PyJWT | 2.8.0 | Autentikasi token |
| Docker | Latest | Containerization |

---

## 📁 Struktur Direktori

```
gas-alert-engine/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Auth & DI
│   │   ├── models.py            # Pydantic schemas
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── alerts.py        # CRUD alert endpoints
│   │       └── internal.py      # Endpoint evaluasi manual
│   ├── core/
│   │   ├── __init__.py
│   │   ├── evaluator.py         # Logika evaluasi kondisi
│   │   ├── worker.py            # Consumer Redis pub/sub
│   │   └── exceptions.py        # Custom exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py          # AsyncEngine + Session
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── alert_repo.py    # Data access layer
│   ├── redis/
│   │   ├── __init__.py
│   │   ├── client.py            # Redis client (pub/sub, queue)
│   │   └── cache.py             # Alert cache helpers
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── logger.py            # Logging setup
│   │   └── utils.py             # Utility functions
│   ├── __init__.py
│   ├── config.py                # Pydantic settings
│   └── main.py                  # FastAPI app + worker startup
├── tests/
│   ├── __init__.py
│   └── test_evaluator.py        # Unit tests evaluator
├── migrations/
├── docker-compose.yml
├── Dockerfile
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## 🔧 Instalasi Environment

### Prasyarat

| Software | Versi Minimum | Cek Versi |
|----------|---------------|-----------|
| Python | 3.11+ | `python3 --version` |
| pip | 21+ | `pip --version` |
| Docker | 20+ | `docker --version` |
| Docker Compose | 2.0+ | `docker compose version` |
| Git | 2.30+ | `git --version` |

### Langkah Instalasi Environment

#### 1. Clone Repository
```bash
git clone https://github.com/Muhamadridwanjr/gas-alert-engine.git
cd gas-alert-engine
```

#### 2. Buat Virtual Environment (untuk development lokal)
```bash
python3 -m venv venv
source venv/bin/activate   # Linux/Mac
# atau
venv\Scripts\activate      # Windows
```

#### 3. Install Dependencies
```bash
# Production dependencies
pip install -r requirements.txt

# Development dependencies (termasuk pytest)
pip install -r requirements-dev.txt
```

#### 4. Setup Environment Variables
```bash
cp .env.example .env
# Edit .env sesuai kebutuhan
nano .env
```

#### 5. Pastikan PostgreSQL & Redis Running
```bash
# Jika menggunakan Docker (dari gas-gateway-api)
docker ps | grep -E "gas-user-db|gas-redis"
```

---

## 🚀 Tutorial: Run, Stop, Delete, Restart

### Mode Python (Development)

#### ▶️ RUN (Menjalankan)

```bash
# 1. Masuk ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-alert-engine

# 2. Aktifkan virtual environment
source venv/bin/activate

# 3. Jalankan service
uvicorn src.main:app --reload --host 0.0.0.0 --port 8400

# Output yang diharapkan:
# INFO:     Uvicorn running on http://0.0.0.0:8400 (Press CTRL+C to quit)
# INFO:     Started reloader process [xxxxx]

# 4. Cek apakah berjalan
curl http://localhost:8400/health
# Response: {"status":"ok","service":"gas-alert-engine","version":"1.0.0",...}
```

#### ⏹️ STOP (Menghentikan)

```bash
# Tekan CTRL+C di terminal yang menjalankan uvicorn
# ATAU (jika berjalan di background):

# Cari PID proses
ps aux | grep "uvicorn src.main:app"

# Kill proses
kill -9 <PID>

# Verifikasi sudah berhenti
curl http://localhost:8400/health
# Harus error: Connection refused
```

#### 🔄 RESTART (Menjalankan Ulang)

```bash
# 1. Stop dulu
# Tekan CTRL+C atau kill PID

# 2. Jalankan lagi
uvicorn src.main:app --reload --host 0.0.0.0 --port 8400
```

#### 🗑️ DELETE (Menghapus Environment)

```bash
# 1. Stop service terlebih dahulu

# 2. Hapus virtual environment
deactivate
rm -rf venv

# 3. Hapus cache
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
```

---

### Mode Docker (Production)

#### ▶️ RUN (Menjalankan)

```bash
# 1. Masuk ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-alert-engine

# 2. Build dan jalankan container
docker compose up -d --build

# 3. Cek status container
docker ps --filter name=gas-alert-engine
# Harus menampilkan: STATUS = Up ... (healthy)

# 4. Cek log
docker logs gas-alert-engine

# 5. Cek health
curl http://localhost:8400/health
# Response: {"status":"ok","service":"gas-alert-engine",...}
```

#### ⏹️ STOP (Menghentikan)

```bash
# Stop container (TIDAK menghapus)
docker compose stop

# Verifikasi
docker ps --filter name=gas-alert-engine
# Seharusnya kosong (container berhenti)

# Cek container yang berhenti
docker ps -a --filter name=gas-alert-engine
# STATUS = Exited
```

#### 🔄 RESTART (Menjalankan Ulang)

```bash
# Restart container yang sedang jalan
docker compose restart

# ATAU jika sudah di-stop:
docker compose start

# ATAU rebuild + restart (jika ada perubahan kode):
docker compose up -d --build

# Cek status setelah restart
docker ps --filter name=gas-alert-engine
```

#### 🗑️ DELETE (Menghapus Container)

```bash
# 1. Stop dan hapus container
docker compose down

# 2. Hapus container + image
docker compose down --rmi all

# 3. Hapus container + image + volume (HATI-HATI: data hilang!)
docker compose down --rmi all -v

# 4. Verifikasi
docker ps -a --filter name=gas-alert-engine
# Seharusnya kosong

docker images | grep gas-alert-engine
# Seharusnya kosong
```

#### 📊 Monitoring Container

```bash
# Lihat status realtime
docker ps --filter name=gas-alert-engine --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Lihat log realtime (follow)
docker logs -f gas-alert-engine

# Lihat resource usage
docker stats gas-alert-engine --no-stream

# Masuk ke dalam container (debug)
docker exec -it gas-alert-engine bash

# Jalankan perintah di dalam container
docker exec gas-alert-engine curl -s http://localhost:8400/health
```

---

## ⚙️ Konfigurasi

Environment variables (file `.env`):

| Variabel | Nilai Default | Deskripsi |
|----------|---------------|-----------|
| `PORT` | `8400` | Port REST API |
| `ENVIRONMENT` | `development` | production/staging/development |
| `LOG_LEVEL` | `INFO` | Level logging (DEBUG, INFO, WARNING, ERROR) |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Koneksi database async |
| `REDIS_URL` | `redis://localhost:6379/0` | Koneksi Redis |
| `MARKET_DATA_CHANNEL` | `market:data` | Channel Redis untuk data pasar |
| `NOTIFICATION_QUEUE` | `notifications` | Redis queue untuk notifikasi |
| `ALERT_CACHE_PREFIX` | `alert` | Prefix key Redis cache |
| `WORKER_CONCURRENCY` | `10` | Jumlah worker thread |
| `JWT_SECRET_KEY` | - | Secret key untuk JWT auth |
| `NOTIFICATION_SERVICE_URL` | - | URL notification service |
| `GATEWAY_URL` | - | URL gateway API |

---

## 🗃️ Database Schema

### Tabel `alerts`

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | UUID (PK) | Primary key |
| `user_id` | UUID | ID pemilik alert |
| `name` | VARCHAR(255) | Nama alert (opsional) |
| `symbol` | VARCHAR(20) | Aset (XAUUSD, BTCUSD, dll) |
| `timeframe` | VARCHAR(10) | M1, M5, H1, dll (null = semua) |
| `condition` | JSONB | Struktur kondisi |
| `cooldown` | INTEGER | Cooldown dalam detik |
| `last_triggered` | TIMESTAMP | Waktu terakhir terpicu |
| `active` | BOOLEAN | Alert aktif / nonaktif |
| `metadata_info` | JSONB | Info tambahan |
| `created_at` | TIMESTAMP | Waktu dibuat |
| `updated_at` | TIMESTAMP | Waktu terakhir diubah |

### Tabel `alert_history`

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | UUID (PK) | Primary key |
| `alert_id` | UUID (FK) | Referensi ke alerts |
| `triggered_at` | TIMESTAMP | Kapan alert terpicu |
| `trigger_data` | JSONB | Snapshot data pemicu |

### Format Kondisi (JSON)

**Contoh kondisi compound (AND + indikator + SMC):**
```json
{
  "operator": "and",
  "conditions": [
    {
      "type": "indicator",
      "name": "RSI",
      "period": 14,
      "operator": "less_than",
      "value": 30
    },
    {
      "type": "smc",
      "name": "FVG",
      "direction": "bullish",
      "lookback": 5
    }
  ]
}
```

**Contoh price alert:**
```json
{
  "type": "price",
  "operator": "cross_above",
  "value": 2000.0
}
```

**Operator yang didukung:** `greater_than`, `less_than`, `greater_equal`, `less_equal`, `equals`, `not_equals`, `cross_above`, `cross_below`

---

## 📡 API Reference

Semua endpoint (kecuali `/health`) memerlukan header `Authorization: Bearer <JWT_TOKEN>`.

### System

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/health` | Health check |

### Alert CRUD

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `GET` | `/alerts` | Daftar alert milik user |
| `POST` | `/alerts` | Buat alert baru |
| `GET` | `/alerts/{id}` | Detail alert |
| `PUT` | `/alerts/{id}` | Update alert |
| `DELETE` | `/alerts/{id}` | Hapus alert (soft delete) |
| `POST` | `/alerts/{id}/activate` | Aktifkan alert |
| `POST` | `/alerts/{id}/deactivate` | Nonaktifkan alert |
| `GET` | `/alerts/{id}/history` | Riwayat trigger alert |

### Internal

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| `POST` | `/internal/evaluate` | Evaluasi manual (debugging) |

### Contoh Request

**Buat Alert Baru:**
```bash
curl -X POST http://localhost:8400/alerts \
  -H "Authorization: Bearer <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "RSI Oversold XAUUSD",
    "symbol": "XAUUSD",
    "timeframe": "M15",
    "condition": {
      "operator": "and",
      "conditions": [
        {"type": "indicator", "name": "RSI", "period": 14, "operator": "less_than", "value": 30},
        {"type": "price", "operator": "greater_than", "value": 1900}
      ]
    },
    "cooldown": 300,
    "active": true
  }'
```

**Daftar Alert:**
```bash
curl http://localhost:8400/alerts?active=true&symbol=XAUUSD \
  -H "Authorization: Bearer <TOKEN>"
```

---

## 🧪 Pengujian

```bash
# Jalankan semua test
pytest tests/ -v

# Dengan coverage report
pytest --cov=src tests/

# Test evaluator saja
pytest tests/test_evaluator.py -v
```

---

## 🚀 Tutorial: Push ke GitHub (Pertama Kali)

### Langkah-langkah Push Repository Baru

```bash
# 1. Masuk ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-alert-engine

# 2. Inisialisasi repository git
git init

# 3. Tambahkan semua file
git add .

# 4. Commit pertama
git commit -m "first commit"

# 5. Set branch utama ke main
git branch -M main

# 6. Tambahkan remote origin
git remote add origin https://github.com/Muhamadridwanjr/gas-alert-engine.git

# 7. Push ke GitHub
git push -u origin main
```

### Verifikasi Push Berhasil
```bash
# Cek remote
git remote -v
# Output:
# origin  https://github.com/Muhamadridwanjr/gas-alert-engine.git (fetch)
# origin  https://github.com/Muhamadridwanjr/gas-alert-engine.git (push)

# Cek status
git status
# Output: nothing to commit, working tree clean
```

---

## 📤 Tutorial: Commit & Update Project ke GitHub

### Setiap Kali Ada Perubahan Kode

```bash
# 1. Lihat file apa saja yang berubah
git status

# 2. Lihat detail perubahan
git diff

# 3. Tambahkan file yang berubah
git add .
# ATAU tambahkan file tertentu saja:
git add src/core/evaluator.py src/api/routes/alerts.py

# 4. Commit dengan pesan yang jelas
git commit -m "feat: tambah kondisi SMC baru untuk BOS detection"

# 5. Push ke GitHub
git push origin main
```

### Konvensi Pesan Commit

| Prefix | Kapan Digunakan | Contoh |
|--------|-----------------|--------|
| `feat:` | Fitur baru | `feat: tambah dukungan indikator Stochastic` |
| `fix:` | Perbaikan bug | `fix: perbaiki cooldown logic yang salah hitung` |
| `docs:` | Perubahan dokumentasi | `docs: update API reference di README` |
| `refactor:` | Refactoring kode | `refactor: pisahkan evaluator ke modul terpisah` |
| `test:` | Tambah/ubah test | `test: tambah test untuk compound condition nested` |
| `chore:` | Maintenance | `chore: update dependencies` |

### Tips Penting
```bash
# Jangan lupa pull dulu jika ada perubahan dari kolaborator
git pull origin main

# Jika ada konflik:
git stash          # Simpan perubahan lokal
git pull           # Pull perubahan remote
git stash pop      # Terapkan kembali perubahan lokal
# Resolve konflik secara manual, lalu:
git add .
git commit -m "fix: resolve merge conflict"
git push origin main
```

---

## 👨‍💻 Pengembangan

### Menambahkan Tipe Kondisi Baru

1. Tambahkan fungsi evaluator di `src/core/evaluator.py`:
   ```python
   def evaluate_my_new_condition(condition: dict, market_data: dict) -> bool:
       # Implementasi logic
       return True
   ```

2. Daftarkan di fungsi `evaluate_condition()`:
   ```python
   elif cond_type == "my_new_type":
       return evaluate_my_new_condition(condition, market_data)
   ```

3. Tulis unit test di `tests/test_evaluator.py`

4. Update model Pydantic jika perlu

### Aturan Kode
- Type hints wajib.
- Docstring untuk fungsi publik.
- Ikuti PEP 8.
- Pastikan semua test lulus.
- Jangan gunakan `eval()` atau `exec()`.

---

## 🔒 Kontribusi (Tim Internal)

Repositori private – hanya tim internal GAS.

### Langkah Kontribusi
1. Buat branch (`feature/`, `fix/`).
2. Commit dengan pesan jelas.
3. Buka Pull Request ke `develop`.
4. Tunggu review.

### Aturan Penting
- ❌ Jangan sebarkan kode ke luar.
- ❌ Jangan commit kredensial/secret.
- ✅ Gunakan environment variable.
- ✅ Tulis test untuk setiap fitur baru.

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.

Hubungi: ridwan@gasstrategy.io

---

**🔥 GAS Strategy – Pantau Pasar dengan Alert Cerdas**
