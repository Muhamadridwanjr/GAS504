# 📓 GAS Journal Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Pencatat riwayat trading dan analisis pengguna.**  
> Service ini bertugas mencatat setiap trade yang dieksekusi, analisis yang dilakukan, dan menyediakan data historis untuk keperluan jurnal, statistik, dan evaluasi performa. Terintegrasi dengan `gas-gateway-api` untuk autentikasi dan pengambilan data user.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Alur Kerja](#alur-kerja)
- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi Environment](#instalasi-environment)
- [Tutorial Run, Stop, Delete, Restart](#tutorial-run-stop-delete-restart)
- [Konfigurasi](#konfigurasi)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Pengujian](#pengujian)
- [Push ke GitHub (Pertama Kali)](#push-ke-github-pertama-kali)
- [Commit & Update Project ke GitHub](#commit--update-project-ke-github)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)

---

## 🔍 Ikhtisar

**gas-journal-service** adalah service mandiri yang menyediakan pencatatan riwayat trading dan analisis untuk setiap pengguna. Data yang disimpan mencakup:

- **Trade history**: entry, exit, lot, profit/loss, komisi, swap, dll.
- **Analisis**: sinyal yang digunakan, alasan entry, screenshot (opsional).
- **Metadata**: waktu, aset, timeframe, gaya trading, dll.

Service ini digunakan oleh:
- `gas-terminal-service` – untuk mencatat setiap eksekusi order (buy/sell) dari user.
- `gas-engine-orchestrator` – untuk mencatat hasil analisis/sinyal yang dihasilkan.
- Frontend (dashboard) – untuk menampilkan jurnal dan statistik kepada user.
- Telegram bot – untuk menampilkan riwayat singkat.

Semua request melalui **gateway API** (`gas-gateway-api`) yang menangani autentikasi JWT dan meneruskan user ID ke service ini.

---

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌────────────────────────────────────┐
│  gas-gateway-api│────▶│       gas-journal-service         │
│   (Port 8000)   │     │  ┌──────────┐  ┌───────────────┐  │
└─────────────────┘     │  │   REST   │  │   Service     │  │
                        │  │  API     │──│    Core       │  │
                        │  └──────────┘  └───────┬───────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │        Database (PostgreSQL)│  │
                        │  └─────────────────────────────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │   Redis (cache & queue)     │  │
                        │  └─────────────────────────────┘  │
                        └────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────┐
│  Sumber Data: gas-terminal-service, gas-engine-orchestrator │
└─────────────────────────────────────────────────────────┘
```

### Komunikasi Antar Service

- **REST API** (port 8107) – Endpoint yang dipanggil oleh gateway atau service internal dengan API key.
- **Autentikasi** – JWT token diverifikasi oleh gateway; journal service menerima `X-User-ID` dari gateway (setelah verifikasi) atau menggunakan API key internal untuk komunikasi antar service.
- **Redis** – Digunakan untuk caching data statistik dan queue untuk pencatatan async (opsional).
- **PostgreSQL** – Penyimpanan utama semua entri jurnal.

---

## 🔄 Alur Kerja

### 1. **Mencatat Trade Baru (dari Terminal)**
   - User mengeksekusi buy/sell via `gas-terminal-service`.
   - Terminal service mengirim request `POST /internal/trades` ke journal service (dengan API key internal) berisi detail trade.
   - Journal service menyimpan ke database.
   - Respon sukses, dan jika perlu publish ke Redis untuk notifikasi (misal ke realtime hub).

### 2. **Mencatat Analisis (dari Orchestrator)**
   - `gas-engine-orchestrator` menghasilkan sinyal/analisis.
   - Mengirim ke `POST /internal/analysis` (dengan API key internal).
   - Journal menyimpan analisis yang dapat direferensi oleh trade nantinya.

### 3. **User Melihat Jurnal (via Gateway)**
   - User request `GET /api/v1/journal/trades` ke gateway.
   - Gateway validasi JWT, tambahkan header `X-User-ID`, teruskan ke journal service.
   - Journal service query database berdasarkan user ID, kembalikan daftar trade.
   - Response dikirim ke gateway → user.

### Diagram Alur

```mermaid
sequenceDiagram
    participant User
    participant Gateway as gas-gateway-api
    participant Terminal as gas-terminal-service
    participant Journal as gas-journal-service
    participant DB as PostgreSQL

    User->>Gateway: POST /trade (via terminal)
    Gateway->>Terminal: forward
    Terminal->>Journal: POST /internal/trades (API Key)
    Journal->>DB: INSERT trade
    DB-->>Journal: OK
    Journal-->>Terminal: 201 Created
    Terminal-->>Gateway: trade result
    Gateway-->>User: response

    User->>Gateway: GET /api/v1/journal/trades
    Gateway->>Journal: GET /trades (X-User-ID)
    Journal->>DB: SELECT * FROM trades WHERE user_id = ?
    DB-->>Journal: data
    Journal-->>Gateway: JSON
    Gateway-->>User: journal
```

---

## ✨ Fitur Utama

- **CRUD Trades**: Catat, edit (jika ada perubahan), hapus (soft delete).
- **CRUD Analysis**: Catat analisis terpisah.
- **Filter & Pagination**: Berdasarkan aset, waktu, arah, profit/loss.
- **Statistik**: Hitung total profit, win rate, average RR, drawdown, dll.
- **Integrasi dengan Gateway**: Autentikasi via JWT, user ID dikirim sebagai header.
- **Internal API**: Endpoint khusus untuk service lain dengan API key.
- **Redis Caching**: Cache statistik untuk akses cepat (TTL 5 menit).
- **Soft Delete**: Data tidak benar-benar dihapus, hanya ditandai.

---

## 🛠️ Teknologi

| Teknologi | Versi | Fungsi |
|-----------|-------|--------|
| Python | 3.11+ | Bahasa utama |
| FastAPI | 0.109.0 | Web framework |
| SQLAlchemy | 2.0.25 | ORM (async) |
| asyncpg | 0.29.0 | PostgreSQL driver |
| Pydantic | 2.5.3 | Validasi data |
| Redis | 5.0.1 | Cache & pub/sub |
| PyJWT | 2.8.0 | JWT handling |
| httpx | 0.26.0 | HTTP client |
| Alembic | 1.13.1 | Migrasi database |
| Docker | - | Container |
| Docker Compose | - | Orchestration |

---

## 📁 Struktur Direktori

```
.
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Auth dependency (get user_id from header)
│   │   ├── middleware.py        # Logging, error handling
│   │   ├── models.py            # Pydantic models untuk request/response
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── trades.py        # Endpoint untuk trade
│   │       ├── analysis.py      # Endpoint untuk analisis
│   │       ├── stats.py         # Endpoint statistik
│   │       └── internal.py      # Endpoint internal (dengan API key)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── trade_service.py     # Logika bisnis trade
│   │   ├── analysis_service.py  # Logika bisnis analisis
│   │   ├── stats_service.py     # Perhitungan statistik
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py          # Koneksi async PostgreSQL
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── trade_repo.py
│   │       └── analysis_repo.py
│   ├── redis/
│   │   ├── __init__.py
│   │   └── client.py            # Redis client dan cache helper
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── utils.py
│   ├── config.py                 # Pydantic settings
│   └── main.py                   # Entry point FastAPI
├── migrations/                    # Alembic
├── tests/
│   ├── unit/
│   │   └── test_health.py
│   ├── integration/
│   └── conftest.py
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── .gitignore
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

---

## 🔧 Instalasi Environment

### Prasyarat
- Python 3.11+
- PostgreSQL 13+ (sudah ada di `gas-user-db` container)
- Redis 7+ (sudah ada di `gas-redis` container)
- Docker & Docker Compose
- Git

### Langkah Instalasi Python (Local Development)

```bash
# 1. Clone repositori
git clone https://github.com/goldenaistrategy/gas-journal-service.git
cd gas-journal-service

# 2. Buat virtual environment
python3 -m venv venv

# 3. Aktifkan virtual environment
source venv/bin/activate
# Pada Windows: venv\Scripts\activate

# 4. Install dependencies (production)
pip install -r requirements.txt

# 5. Install dependencies (development + testing)
pip install -r requirements-dev.txt

# 6. Copy file environment
cp .env.example .env
# Edit .env sesuai konfigurasi Anda

# 7. Pastikan PostgreSQL dan Redis sudah berjalan
# (biasanya via docker dari gas-gateway-api)

# 8. Buat database jika belum ada
docker exec gas-user-db psql -U postgres -c "CREATE DATABASE gas_journal;"
```

---

## 🚀 Tutorial Run, Stop, Delete, Restart

### ━━━━━━ 🐍 PYTHON (Local Development) ━━━━━━

#### ▶️ RUN (Menjalankan)

```bash
# Aktifkan virtual environment
source venv/bin/activate

# Jalankan service (development mode dengan auto-reload)
uvicorn src.main:app --reload --port 8107

# Atau jalankan di background
nohup uvicorn src.main:app --host 0.0.0.0 --port 8107 &

# Verifikasi berjalan
curl http://localhost:8107/health
```

#### ⏹️ STOP (Menghentikan)

```bash
# Jika di foreground: tekan Ctrl+C

# Jika di background, cari PID dan kill
ps aux | grep uvicorn
kill <PID>

# Atau kill semua proses uvicorn untuk service ini
pkill -f "uvicorn src.main:app"
```

#### 🔄 RESTART (Menjalankan Ulang)

```bash
# Kill proses lama
pkill -f "uvicorn src.main:app"

# Jalankan ulang
uvicorn src.main:app --reload --port 8107
```

#### 🗑️ DELETE (Menghapus Instalasi Python)

```bash
# Hentikan service
pkill -f "uvicorn src.main:app"

# Hapus virtual environment
deactivate
rm -rf venv

# Hapus database (opsional)
docker exec gas-user-db psql -U postgres -c "DROP DATABASE gas_journal;"

# Hapus folder project (jika ingin hapus semuanya)
cd ..
rm -rf gas-journal-service
```

---

### ━━━━━━ 🐳 DOCKER (Production/Staging) ━━━━━━

#### ▶️ RUN (Menjalankan Container)

```bash
# Pertama kali - build dan jalankan
docker compose up -d --build

# Cek status container
docker ps --filter name=gas-journal-service

# Cek log realtime
docker logs -f gas-journal-service

# Verifikasi healthy
curl http://localhost:8107/health

# Output yang diharapkan:
# {"status":"ok","service":"gas-journal-service","version":"1.0.0","redis_connected":true,"database_connected":true}
```

#### ⏹️ STOP (Menghentikan Container)

```bash
# Stop container (data tetap aman)
docker compose stop

# Atau stop container tertentu
docker stop gas-journal-service

# Verifikasi sudah berhenti
docker ps --filter name=gas-journal-service
# Tidak ada output = sudah berhenti
```

#### 🔄 RESTART (Menjalankan Ulang Container)

```bash
# Restart container
docker compose restart

# Atau restart container tertentu
docker restart gas-journal-service

# Restart dengan rebuild (jika ada perubahan code)
docker compose up -d --build

# Cek status setelah restart
docker ps --filter name=gas-journal-service
# Status harus: Up ... (healthy)
```

#### 🗑️ DELETE (Menghapus Container)

```bash
# Stop dan hapus container
docker compose down

# Hapus container + image yang dibuat
docker compose down --rmi local

# Hapus SEMUA termasuk volume data (HATI-HATI!)
docker compose down --rmi local --volumes

# Verifikasi sudah terhapus
docker ps -a --filter name=gas-journal-service
docker images | grep gas-journal

# Hapus database (opsional)
docker exec gas-user-db psql -U postgres -c "DROP DATABASE gas_journal;"
```

#### 🔍 DEBUG Container

```bash
# Cek logs
docker logs gas-journal-service
docker logs -f gas-journal-service              # follow
docker logs --tail 50 gas-journal-service       # 50 baris terakhir
docker logs --since 5m gas-journal-service      # 5 menit terakhir

# Masuk ke dalam container
docker exec -it gas-journal-service bash

# Cek health dari dalam container
docker exec gas-journal-service curl -s http://localhost:8107/health

# Cek resource usage
docker stats gas-journal-service

# Cek network
docker network inspect gas-network | grep gas-journal

# Cek environment variables
docker exec gas-journal-service env | sort
```

---

## 🔧 Konfigurasi

Environment variables (file `.env`):

| Variabel | Nilai Default | Deskripsi |
|----------|---------------|-----------|
| `PORT` | `8107` | Port REST API |
| `DATABASE_URL` | `postgresql+asyncpg://...` | Koneksi database async |
| `REDIS_URL` | `redis://gas-redis:6379/0` | Koneksi Redis |
| `INTERNAL_API_KEY` | (harus diisi) | API key untuk komunikasi antar service internal |
| `JWT_SECRET_KEY` | (opsional) | Secret untuk verifikasi JWT (dari gateway) |
| `LOG_LEVEL` | `INFO` | Level logging (DEBUG, INFO, WARNING, ERROR) |
| `ENVIRONMENT` | `development` | production / staging / development |

### Contoh `.env` untuk Development:

```env
PORT=8107
ENVIRONMENT=development
LOG_LEVEL=INFO
JWT_SECRET_KEY=dev_secret_key
INTERNAL_API_KEY=dev_internal_api_key
DATABASE_URL=postgresql+asyncpg://postgres:postgres@gas-user-db:5432/gas_journal
REDIS_URL=redis://gas-redis:6379/0
```

---

## 🗃️ Database Schema

### Tabel `trades`
| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | UUID (PK) | Primary key |
| `user_id` | UUID | ID user (dari auth service) |
| `symbol` | VARCHAR | Aset (XAUUSD, BTCUSD, dll) |
| `action` | ENUM('BUY','SELL') | Arah trade |
| `entry_price` | NUMERIC(18,8) | Harga entry |
| `exit_price` | NUMERIC(18,8) | Harga exit (jika sudah close) |
| `lot` | NUMERIC(12,4) | Ukuran lot |
| `profit` | NUMERIC(18,8) | Profit/loss dalam USD |
| `commission` | NUMERIC(12,4) | Komisi |
| `swap` | NUMERIC(12,4) | Swap |
| `entry_time` | TIMESTAMP(TZ) | Waktu entry |
| `exit_time` | TIMESTAMP(TZ) | Waktu exit |
| `status` | ENUM('OPEN','CLOSED','CANCELED') | Status |
| `analysis_id` | UUID (FK) | Referensi ke analisis (opsional) |
| `metadata_info` | JSONB | Informasi tambahan |
| `created_at` | TIMESTAMP(TZ) | Waktu record dibuat |
| `updated_at` | TIMESTAMP(TZ) | Waktu update terakhir |
| `deleted_at` | TIMESTAMP(TZ) | Soft delete marker |

### Tabel `analysis`
| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | UUID (PK) | Primary key |
| `user_id` | UUID | ID user |
| `symbol` | VARCHAR | Aset |
| `timeframe` | VARCHAR | Timeframe analisis |
| `signal` | ENUM('BUY','SELL','NEUTRAL') | Hasil sinyal |
| `entry_price` | NUMERIC(18,8) | Harga yang disarankan |
| `stop_loss` | NUMERIC(18,8) | Stop loss |
| `take_profit` | NUMERIC(18,8) | Take profit |
| `confidence` | FLOAT | 0-1 |
| `reason` | TEXT | Alasan analisis |
| `metadata_info` | JSONB | Data tambahan |
| `created_at` | TIMESTAMP(TZ) | Waktu dibuat |
| `deleted_at` | TIMESTAMP(TZ) | Soft delete marker |

**Indeks**: `user_id`, `symbol`, `entry_time`, `status`, `created_at`.

---

## 📡 API Reference

### Autentikasi
- **Endpoint publik (dari gateway)**: Gateway menambahkan header `X-User-ID` setelah memverifikasi JWT. Service ini mempercayai header tersebut.
- **Endpoint internal**: Memerlukan header `X-API-Key` dengan nilai sama dengan `INTERNAL_API_KEY`.

### Health Check

```bash
# Direct
curl http://localhost:8107/health

# Via Gateway
curl http://localhost:8000/api/v1/journal/health
```

**Response:**
```json
{
  "status": "ok",
  "service": "gas-journal-service",
  "version": "1.0.0",
  "redis_connected": true,
  "database_connected": true
}
```

---

### Public Endpoints (via Gateway)

#### `GET /trades` – Daftar trade user
```bash
curl -H "X-User-ID: <user_id>" "http://localhost:8107/trades?symbol=XAUUSD&status=CLOSED&limit=50&offset=0&sort=-entry_time"
```

**Query Parameters:**
| Parameter | Default | Deskripsi |
|-----------|---------|-----------|
| `symbol` | - | Filter aset |
| `status` | - | OPEN, CLOSED, CANCELED |
| `from` | - | ISO datetime start |
| `to` | - | ISO datetime end |
| `limit` | 50 | Maks 200 |
| `offset` | 0 | Skip records |
| `sort` | `-entry_time` | Prefix `-` untuk descending |

**Response:**
```json
{
  "total": 123,
  "limit": 50,
  "offset": 0,
  "data": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "symbol": "XAUUSD",
      "action": "BUY",
      "entry_price": 2000.5,
      "exit_price": 2010.0,
      "lot": 0.1,
      "profit": 95.0,
      "commission": 2.5,
      "swap": -0.3,
      "entry_time": "2025-03-20T10:00:00Z",
      "exit_time": "2025-03-20T14:30:00Z",
      "status": "CLOSED",
      "analysis_id": null,
      "metadata_info": null,
      "created_at": "2025-03-20T10:00:01Z",
      "updated_at": "2025-03-20T14:30:01Z"
    }
  ]
}
```

#### `GET /trades/{id}` – Detail satu trade
```bash
curl -H "X-User-ID: <user_id>" http://localhost:8107/trades/<trade_id>
```

#### `DELETE /trades/{id}` – Soft delete trade
```bash
curl -X DELETE -H "X-User-ID: <user_id>" http://localhost:8107/trades/<trade_id>
```

#### `GET /stats` – Statistik performa
```bash
curl -H "X-User-ID: <user_id>" "http://localhost:8107/stats?symbol=XAUUSD"
```

**Response:**
```json
{
  "total_trades": 120,
  "winning_trades": 70,
  "losing_trades": 48,
  "breakeven_trades": 2,
  "win_rate": 58.33,
  "total_profit": 1250.5,
  "total_commission": 300.0,
  "total_swap": -15.5,
  "net_profit": 935.0,
  "average_profit": 35.0,
  "average_loss": 18.75,
  "average_rr": 1.87,
  "max_drawdown": 320.0,
  "profit_factor": 1.45,
  "largest_win": 250.0,
  "largest_loss": 120.0
}
```

#### `GET /analysis` – Daftar analisis user
```bash
curl -H "X-User-ID: <user_id>" "http://localhost:8107/analysis?symbol=XAUUSD&timeframe=H1"
```

#### `GET /analysis/{id}` – Detail satu analisis
```bash
curl -H "X-User-ID: <user_id>" http://localhost:8107/analysis/<analysis_id>
```

#### `DELETE /analysis/{id}` – Soft delete analisis
```bash
curl -X DELETE -H "X-User-ID: <user_id>" http://localhost:8107/analysis/<analysis_id>
```

---

### Internal Endpoints (dengan API Key)

#### `POST /internal/trades` – Catat trade baru
```bash
curl -X POST http://localhost:8107/internal/trades \
  -H "X-API-Key: dev_internal_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "XAUUSD",
    "action": "BUY",
    "entry_price": 2000.5,
    "lot": 0.1,
    "entry_time": "2025-03-20T10:00:00Z",
    "analysis_id": null,
    "metadata_info": {}
  }'
```

#### `PATCH /internal/trades/{id}` – Update trade (close position)
```bash
curl -X PATCH http://localhost:8107/internal/trades/<trade_id> \
  -H "X-API-Key: dev_internal_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "exit_price": 2010.0,
    "exit_time": "2025-03-20T14:30:00Z",
    "profit": 95.0,
    "commission": 2.5,
    "swap": -0.3,
    "status": "CLOSED"
  }'
```

#### `POST /internal/analysis` – Catat analisis baru
```bash
curl -X POST http://localhost:8107/internal/analysis \
  -H "X-API-Key: dev_internal_api_key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "symbol": "XAUUSD",
    "timeframe": "H1",
    "signal": "BUY",
    "entry_price": 2000.0,
    "stop_loss": 1990.0,
    "take_profit": 2020.0,
    "confidence": 0.85,
    "reason": "Bullish engulfing di level demand zone H1"
  }'
```

---

## 🧪 Pengujian

```bash
# Aktifkan venv
source venv/bin/activate

# Jalankan semua test
pytest tests/ -v

# Dengan coverage report
pytest --cov=src tests/

# Test tertentu
pytest tests/unit/test_health.py -v
```

### Test yang tersedia:
- ✅ Health endpoint response
- ✅ Trade endpoint memerlukan X-User-ID
- ✅ Internal endpoint memerlukan X-API-Key
- ✅ Stats endpoint memerlukan X-User-ID
- ✅ Analysis endpoint memerlukan X-User-ID

---

## 🚀 Push ke GitHub (Pertama Kali)

### Langkah-langkah:

```bash
# 1. Masuk ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-journal-service

# 2. Inisialisasi Git repository
git init

# 3. Tambahkan semua file
git add .

# 4. Commit pertama
git commit -m "feat: initial gas-journal-service implementation

- FastAPI service on port 8107
- Trade & Analysis CRUD with soft delete
- Statistics (win rate, profit factor, drawdown)
- Redis caching for stats
- Internal API with API key auth
- Gateway integration via X-User-ID header
- Docker + Docker Compose with healthcheck
- PostgreSQL (async) + Redis"

# 5. Set branch utama
git branch -M main

# 6. Tambahkan remote repository
git remote add origin https://github.com/goldenaistrategy/gas-journal-service.git

# 7. Push ke GitHub
git push -u origin main
```

### Jika repo sudah dibuat tapi kosong:
```bash
git push -u origin main
```

### Jika terjadi error "remote already exists":
```bash
git remote set-url origin https://github.com/goldenaistrategy/gas-journal-service.git
git push -u origin main
```

---

## 📤 Commit & Update Project ke GitHub

### Setelah melakukan perubahan:

```bash
# 1. Cek status perubahan
git status

# 2. Lihat detail perubahan
git diff

# 3. Tambahkan file yang berubah
git add .
# Atau file tertentu:
git add src/core/trade_service.py

# 4. Commit dengan pesan deskriptif
git commit -m "fix: perbaiki kalkulasi drawdown di stats service"

# 5. Push ke GitHub
git push origin main
```

### Contoh pesan commit yang baik:
```
feat: tambah filter timeframe di endpoint analisis
fix: perbaiki soft delete yang tidak update cache
docs: update API reference di README
refactor: pisah stats calculation ke helper function
chore: upgrade fastapi ke versi 0.110.0
```

### Tips:
- Gunakan prefix `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- Commit secara berkala, jangan menumpuk banyak perubahan
- Selalu `git pull` sebelum `git push` jika bekerja tim

---

## 👨‍💻 Pengembangan

### Menambahkan Field Baru di Tabel
1. Update model SQLAlchemy di `src/db/models.py`
2. Buat migration dengan alembic (`alembic revision --autogenerate -m "add field"`)
3. Jalankan migration (`alembic upgrade head`)
4. Update Pydantic model di `src/api/models.py`
5. Sesuaikan service dan repository jika perlu
6. Update unit test

### Aturan Kode
- Gunakan type hints
- Sertakan docstring
- Ikuti PEP 8 (black)
- Pastikan semua test lulus

---

## 🔒 Kontribusi (Tim Internal)

Repositori ini bersifat **private** dan hanya untuk tim internal GAS.

### Langkah Kontribusi
1. Buat branch baru (`feature/`, `fix/`)
2. Lakukan perubahan sesuai pedoman
3. Commit dengan pesan jelas
4. Buka Pull Request ke `develop`
5. Tunggu review dan minimal satu approval

### Aturan Penting
- ❌ Jangan menyebarluaskan kode ke pihak luar tanpa izin
- ❌ Jangan commit kredensial
- ✅ Gunakan environment variable untuk konfigurasi

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS. Seluruh hak cipta dilindungi undang-undang.**

Repositori ini dan seluruh kode di dalamnya adalah milik eksklusif **Muhamad RidwanJr** dan tim **GAS (Gas Automatic Strategy)**.  
Tidak untuk disebarluaskan tanpa izin tertulis.

Untuk keperluan lisensi, kemitraan, atau pertanyaan, hubungi:  
📧 **ridwan@gasstrategy.io**

---

**🔥 GAS Strategy – Jurnal Trading Profesional untuk Evaluasi Kinerja**
