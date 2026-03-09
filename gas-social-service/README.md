# 👥 GAS Social Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Jantung interaksi sosial antar pengguna.**
> Service ini mengelola follow, unfollow, berbagi sinyal (insider), like, komentar, dan feed sosial. Memungkinkan pengguna untuk berinteraksi, mengikuti trader lain, dan menerima notifikasi aktivitas dari orang yang diikuti. Terintegrasi dengan `gas-signal-service` untuk menyimpan sinyal insider dan `gas-notification-service` untuk notifikasi.

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
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Pengujian](#pengujian)
- [Push ke GitHub](#push-ke-github)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)

---

## 🔍 Ikhtisar

**gas-social-service** menyediakan lapisan sosial untuk platform GAS. Fitur utamanya:

- **Follow/Unfollow**: Pengguna dapat mengikuti trader lain.
- **Insider Signals**: Pengguna dapat membagikan hasil analisis mandiri mereka sebagai sinyal yang hanya terlihat oleh pengikut (insider). Sinyal ini disimpan di `gas-signal-service` dengan tier `insider`.
- **Feed**: Setiap pengguna memiliki feed yang berisi sinyal insider dari orang yang diikuti.
- **Notifikasi**: Ketika seseorang yang diikuti memposting sinyal, pengikut mendapat notifikasi via `gas-notification-service`.

Service ini berkomunikasi dengan:
- `gas-gateway-api` – untuk autentikasi dan routing.
- `gas-signal-service` – untuk menyimpan sinyal insider.
- `gas-notification-service` – untuk mengirim notifikasi realtime.

---

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌────────────────────────────────────┐
│  gas-gateway-api│────▶│        gas-social-service         │
│   (Port 8000)   │     │  ┌──────────┐  ┌───────────────┐  │
└─────────────────┘     │  │   REST   │  │   Service     │  │
                        │  │  API     │──│    Core       │  │
                        │  │ :8500    │  └───────┬───────┘  │
                        │  └──────────┘           │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │   PostgreSQL (gas_social)   │  │
                        │  └─────────────────────────────┘  │
                        └────────────────────────────────────┘
                                      │
              ┌───────────────────────┼───────────────────────┐
              ▼                       ▼                       ▼
┌─────────────────────┐ ┌─────────────────────┐ ┌─────────────────────┐
│ gas-signal-service  │ │ gas-notification-   │ │ gas-gateway-api     │
│ (tier insider)      │ │ service             │ │ (autentikasi JWT)   │
└─────────────────────┘ └─────────────────────┘ └─────────────────────┘
```

### Komunikasi Antar Service

| Jalur | Protokol | Keterangan |
|-------|----------|------------|
| Gateway → Social | REST + `X-User-ID` | Semua request publik |
| Social → Signal | REST + `X-API-Key` | Simpan/ambil insider signal |
| Social → Notification | REST + `X-API-Key` | Kirim notifikasi ke follower |

---

## 🔄 Alur Kerja

### 1. Follow/Unfollow
```
User A ──POST /follow/{userId}──▶ gateway ──▶ social-service
                                               ├─ Simpan di DB (tabel follows)
                                               └─ 201 Created
```

### 2. Posting Sinyal Insider
```
User B ──POST /signals/insider──▶ gateway ──▶ social-service
                                               ├─ Validasi input
                                               ├─ POST ke gas-signal-service (tier=insider)
                                               ├─ GET follower IDs dari DB
                                               ├─ Fan-out notifikasi ke tiap follower
                                               └─ 201 Created
```

### 3. Melihat Feed
```
User A ──GET /feed──▶ gateway ──▶ social-service
                                  ├─ GET following IDs dari DB
                                  ├─ GET insider signals dari gas-signal-service
                                  └─ Return feed JSON
```

### Diagram Sequence

```mermaid
sequenceDiagram
    participant UserB
    participant Gateway
    participant Social as gas-social-service
    participant Signal as gas-signal-service
    participant Notif as gas-notification-service
    participant DB

    UserB->>Gateway: POST /signals/insider
    Gateway->>Social: forward (X-User-ID: B)
    Social->>Signal: POST /internal/signals (tier=insider)
    Signal-->>Social: { signal_id }
    Social->>DB: SELECT followers WHERE followee = B
    DB-->>Social: [follower_ids]
    loop each follower
        Social->>Notif: POST /internal/notify
    end
    Social-->>UserB: 201 Created
```

---

## ✨ Fitur Utama

| Fitur | Status |
|-------|--------|
| Follow/Unfollow user | ✅ |
| Cek status follow | ✅ |
| Daftar followers/following | ✅ |
| Post sinyal insider | ✅ |
| Fan-out notifikasi ke follower | ✅ |
| Feed sinyal dari following | ✅ |
| Internal endpoint (inter-service) | ✅ |
| Health check | ✅ |
| Like/Komentar | 🔜 Dapat dikembangkan |

---

## 🛠️ Teknologi

| Komponen | Teknologi |
|----------|-----------|
| Bahasa | Python 3.11+ |
| Web Framework | FastAPI 0.109 |
| Database ORM | SQLAlchemy 2.0 (async) |
| Database Driver | asyncpg 0.29 |
| Database | PostgreSQL 13+ |
| Cache/Queue | Redis 7+ |
| Validasi | Pydantic v2 |
| Migrasi | Alembic |
| HTTP Client | httpx (async) |
| Testing | pytest + pytest-asyncio |
| Container | Docker + Docker Compose |

---

## 📁 Struktur Direktori

```
gas-social-service/
├── src/
│   ├── __init__.py
│   ├── main.py                      # FastAPI app entrypoint
│   ├── config.py                    # Konfigurasi (pydantic-settings)
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py          # Autentikasi & API key validation
│   │   ├── models.py                # Pydantic request/response schemas
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── follows.py           # POST/DELETE /follow, GET followers/following
│   │       ├── signals.py           # POST /signals/insider
│   │       ├── feed.py              # GET /feed
│   │       └── internal.py          # /internal/* (inter-service)
│   ├── core/
│   │   ├── __init__.py
│   │   ├── follow_service.py        # Logika follow/unfollow
│   │   ├── signal_service.py        # Post insider + fan-out notifikasi
│   │   ├── feed_service.py          # Susun feed sosial
│   │   └── exceptions.py            # Custom HTTP exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py              # AsyncEngine + session factory
│   │   ├── models.py                # SQLAlchemy ORM (Follow)
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── follow_repo.py       # CRUD untuk tabel follows
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── signal_client.py         # HTTP client ke gas-signal-service
│   │   └── notification_client.py   # HTTP client ke gas-notification-service
│   └── lib/
│       ├── __init__.py
│       ├── logger.py                # Structured logger
│       └── utils.py                 # Helper utilities
├── migrations/
│   ├── env.py                       # Alembic async env
│   ├── script.py.mako               # Template migrasi
│   ├── README
│   └── versions/                    # File migrasi
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   └── test_follows.py
├── alembic.ini
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

## ⚙️ Instalasi & Menjalankan

### 0. Prasyarat

- Python 3.11+
- Docker & Docker Compose
- Git
- PostgreSQL 13+ (atau via Docker)
- Redis 7+ (atau via Docker)
- `gas-gateway-api` berjalan di `gas-network`

---

### Cara 1: Python (Development)

#### 🟢 START – Menjalankan Service

```bash
# 1. Masuk ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-social-service

# 2. Buat virtual environment
python -m venv venv

# 3. Aktifkan virtual environment
source venv/bin/activate          # Linux/macOS
# venv\Scripts\activate           # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy dan isi environment variables
cp .env.example .env
# Edit .env sesuai kebutuhan

# 6. Pastikan PostgreSQL & Redis sudah jalan (bisa via Docker):
docker run -d --name gas-user-db \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=gas_social \
  -p 5432:5432 postgres:15

docker run -d --name gas-redis \
  -p 6379:6379 redis:7

# 7. Jalankan migrasi database
alembic upgrade head

# 8. Jalankan service (development dengan auto-reload)
uvicorn src.main:app --host 0.0.0.0 --port 8500 --reload

# Atau production mode:
uvicorn src.main:app --host 0.0.0.0 --port 8500 --workers 4
```

#### 🔴 STOP – Menghentikan Service (Python)

```bash
# Tekan Ctrl+C di terminal untuk stop uvicorn

# Atau kill proses berdasarkan port:
lsof -ti:8500 | xargs kill -9

# Nonaktifkan virtual environment:
deactivate
```

#### 🔁 RESTART – Restart Service (Python)

```bash
# Stop dulu (Ctrl+C), lalu jalankan ulang:
uvicorn src.main:app --host 0.0.0.0 --port 8500 --reload

# Atau gunakan script simpel:
pkill -f "uvicorn src.main:app" && uvicorn src.main:app --host 0.0.0.0 --port 8500 --reload
```

#### 🗑️ DELETE – Hapus Environment Python

```bash
# Nonaktifkan venv
deactivate

# Hapus virtual environment
rm -rf venv/

# Hapus file cache Python
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

---

### Cara 2: Docker (Recommended)

#### 🟢 START – Menjalankan Service via Docker

```bash
# Masuk ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-social-service

# Pastikan gas-network sudah ada (buat jika belum):
docker network create gas-network

# Build dan jalankan container
docker compose up -d --build

# Cek status container (should be "Up (healthy)"):
docker ps | grep gas-social-service

# Lihat logs startup:
docker logs gas-social-service --follow
```

#### 🔴 STOP – Menghentikan Container

```bash
# Stop container (tanpa hapus data):
docker compose stop

# Atau stop + hapus container (volume tetap tersimpan):
docker compose down

# Stop container spesifik:
docker stop gas-social-service
```

#### 🔁 RESTART – Restart Container

```bash
# Restart container yang sudah berjalan:
docker compose restart

# Atau restart container spesifik:
docker restart gas-social-service

# Restart dengan rebuild image (setelah update kode):
docker compose down && docker compose up -d --build

# Hot-reload (development, kode langsung apply via volume mount):
docker compose up -d  # Sudah pakai --reload di command, cukup save file
```

#### 🗑️ DELETE – Hapus Container & Image

```bash
# Hapus container (tapi volume & image tetap):
docker compose down

# Hapus container + volume database:
docker compose down -v

# Hapus container + image yang dibangun:
docker compose down --rmi local

# Hapus SEMUA (container + volume + image):
docker compose down -v --rmi local

# Hapus image manual:
docker rmi gas-social-service-gas-social-service

# Bersihkan dangling images:
docker image prune -f
```

---

### Cara 3: Docker – Perintah Harian

```bash
# Lihat status semua container GAS:
docker ps --filter "name=gas"

# Lihat logs realtime:
docker logs gas-social-service -f

# Lihat logs 100 baris terakhir:
docker logs gas-social-service --tail=100

# Masuk ke dalam container:
docker exec -it gas-social-service bash

# Cek health check:
docker inspect --format='{{.State.Health.Status}}' gas-social-service

# Test endpoint langsung dari dalam container:
docker exec gas-social-service curl -s http://localhost:8500/health
```

---

## 🔧 Konfigurasi

Environment variables (file `.env`):

| Variabel | Nilai Default | Deskripsi |
|----------|---------------|-----------|
| `PORT` | `8500` | Port REST API |
| `ENVIRONMENT` | `development` | `production` / `staging` / `development` |
| `LOG_LEVEL` | `INFO` | Level logging: `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@gas-user-db:5432/gas_social` | Koneksi PostgreSQL async |
| `REDIS_URL` | `redis://gas-redis:6379/3` | Koneksi Redis (DB index 3) |
| `INTERNAL_API_KEY` | `internal_secret_key_change_me` | API key untuk endpoint internal |
| `SIGNAL_SERVICE_URL` | `http://gas-signal-service:8106` | Base URL gas-signal-service |
| `SIGNAL_SERVICE_API_KEY` | _(isi)_ | API key ke signal service |
| `NOTIFICATION_SERVICE_URL` | `http://gas-notification-service:8112` | Base URL gas-notification-service |
| `NOTIFICATION_SERVICE_API_KEY` | _(isi)_ | API key ke notification service |
| `GATEWAY_URL` | `http://gas-gateway-api:8000` | Base URL gas-gateway-api |

---

## 🗃️ Database Schema

Database: `gas_social`

### Tabel `follows`

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| `id` | `VARCHAR(36)` PK | UUID primary key |
| `follower_id` | `VARCHAR(36)` | ID user yang mengikuti |
| `followee_id` | `VARCHAR(36)` | ID user yang diikuti |
| `created_at` | `TIMESTAMP WITH TIME ZONE` | Waktu follow dibuat |

**Constraint Unik:** `(follower_id, followee_id)` – satu user tidak bisa follow user yang sama dua kali.

**Index:** `follower_id`, `followee_id` – diindex untuk query feed dan notifikasi cepat.

---

## 📡 API Reference

Base URL: `http://localhost:8500`

> **Autentikasi**: Semua endpoint publik memerlukan header `X-User-ID` yang diinjeksi oleh `gas-gateway-api` setelah validasi JWT.

### 📊 System

#### `GET /health` – Health Check
```json
// Response 200 OK
{
  "status": "ok",
  "service": "gas-social-service",
  "version": "1.0.0",
  "environment": "development"
}
```

#### `GET /` – Service Info
```json
// Response 200 OK
{
  "service": "gas-social-service",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/health"
}
```

---

### 👥 Follow Management

#### `POST /follow/{userId}` – Follow User
```bash
curl -X POST http://localhost:8500/follow/user-B-id \
  -H "X-User-ID: user-A-id"
```
```json
// Response 201 Created
{
  "follower_id": "user-A-id",
  "followee_id": "user-B-id",
  "followed_at": "2026-02-25T14:58:00+00:00"
}
```

Kemungkinan error:
- `400 Bad Request` – Mencoba follow diri sendiri
- `409 Conflict` – Sudah follow user ini

---

#### `DELETE /follow/{userId}` – Unfollow User
```bash
curl -X DELETE http://localhost:8500/follow/user-B-id \
  -H "X-User-ID: user-A-id"
```
```
// Response 204 No Content
```

---

#### `GET /follow/{userId}/status` – Cek Status Follow
```bash
curl http://localhost:8500/follow/user-B-id/status \
  -H "X-User-ID: user-A-id"
```
```json
// Response 200 OK
{ "is_following": true }
```

---

#### `GET /follow/followers/me` – Daftar Pengikut Saya
```bash
curl "http://localhost:8500/follow/followers/me?limit=20&offset=0" \
  -H "X-User-ID: user-A-id"
```
```json
// Response 200 OK
{
  "total": 3,
  "limit": 20,
  "offset": 0,
  "data": [
    { "user_id": "user-X-id", "followed_at": "2026-02-25T12:00:00+00:00" }
  ]
}
```

---

#### `GET /follow/following/me` – Daftar Yang Saya Ikuti
```bash
curl "http://localhost:8500/follow/following/me?limit=20&offset=0" \
  -H "X-User-ID: user-A-id"
```
```json
// Response 200 OK (format sama dengan followers)
```

---

### 📡 Insider Signals

#### `POST /signals/insider` – Post Sinyal Insider
```bash
curl -X POST http://localhost:8500/signals/insider \
  -H "X-User-ID: user-B-id" \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "XAUUSD",
    "timeframe": "H1",
    "action": "BUY",
    "entry_price": 2000.5,
    "stop_loss": 1990.0,
    "take_profit": 2020.0,
    "confidence": 0.85,
    "note": "Analisis ICT: FVG terisi, Bullish OB terkonfirmasi."
  }'
```
```json
// Response 201 Created (data dari gas-signal-service)
{
  "id": "signal-uuid",
  "user_id": "user-B-id",
  "tier": "insider",
  "symbol": "XAUUSD",
  "action": "BUY",
  ...
}
```

---

### 📰 Feed

#### `GET /feed` – Feed Sinyal Insider dari Following
```bash
curl "http://localhost:8500/feed?limit=20&offset=0" \
  -H "X-User-ID: user-A-id"
```
```json
// Response 200 OK
{
  "total": 42,
  "limit": 20,
  "offset": 0,
  "data": [
    {
      "id": "signal-uuid",
      "user_id": "user-B-id",
      "symbol": "XAUUSD",
      "action": "BUY",
      "entry_price": 2000.5,
      "created_at": "2026-02-25T14:00:00+00:00"
    }
  ]
}
```

**Query Parameters:**
| Parameter | Tipe | Default | Deskripsi |
|-----------|------|---------|-----------|
| `limit` | int | 20 | Jumlah item per halaman (max 100) |
| `offset` | int | 0 | Offset pagination |
| `from` | string | - | ISO timestamp filter (ambil setelah waktu ini) |

---

### 🔒 Internal Endpoints (Hanya untuk Service-to-Service)

> Memerlukan header `X-API-Key: <INTERNAL_API_KEY>`

#### `GET /internal/ping` – Ping Internal
```bash
curl http://localhost:8500/internal/ping \
  -H "X-API-Key: internal_secret_key_change_me"
```

#### `POST /internal/signal-posted` – Notifikasi Sinyal Baru
```bash
curl -X POST http://localhost:8500/internal/signal-posted \
  -H "X-API-Key: internal_secret_key_change_me" \
  -H "Content-Type: application/json" \
  -d '{ "signal_id": "uuid", "user_id": "user-B-id", "created_at": "2026-02-25T14:00:00Z" }'
```

---

## 🧪 Pengujian

### Jalankan Tests

```bash
# Pastikan virtual environment aktif
source venv/bin/activate

# Install dev dependencies
pip install -r requirements-dev.txt

# Jalankan semua test
pytest tests/ -v

# Jalankan dengan coverage report
pytest --cov=src tests/ --cov-report=term-missing

# Jalankan test spesifik
pytest tests/test_health.py -v
pytest tests/test_follows.py -v
```

### Test Manual via curl

```bash
# 1. Health check
curl http://localhost:8500/health

# 2. Follow user (butuh gateway atau mock X-User-ID)
curl -X POST http://localhost:8500/follow/target-user-id \
  -H "X-User-ID: my-user-id"

# 3. Lihat following
curl http://localhost:8500/follow/following/me \
  -H "X-User-ID: my-user-id"

# 4. Lihat feed
curl "http://localhost:8500/feed?limit=10" \
  -H "X-User-ID: my-user-id"

# 5. Ping internal
curl http://localhost:8500/internal/ping \
  -H "X-API-Key: internal_secret_key_change_me"
```

### Docs Interaktif

Buka di browser (development mode):
- Swagger UI: **http://localhost:8500/docs**
- ReDoc: **http://localhost:8500/redoc**

---

## 🐙 Push ke GitHub

### Pertama Kali (New Repository)

```bash
cd /home/mridwan3101/goldenaistrategy/gas-social-service

# 1. Inisialisasi Git
git init

# 2. Tambahkan semua file
git add .

# 3. Commit pertama
git commit -m "feat: initial commit – gas-social-service

- FastAPI REST API on port 8500
- Follow/unfollow with PostgreSQL
- Insider signal posting + fan-out notifications  
- Social feed from followed users
- Docker containerized with health check
- Integrated with gas-gateway-api, gas-signal-service, gas-notification-service"

# 4. Set branch ke main
git branch -M main

# 5. Tambahkan remote origin (repo yang sudah dibuat di GitHub)
git remote add origin https://github.com/Muhamadridwanjr/gas-social-service.git

# 6. Push ke GitHub
git push -u origin main
```

### Update / Commit Setelah Perubahan

```bash
cd /home/mridwan3101/goldenaistrategy/gas-social-service

# Lihat file yang berubah
git status

# Tambahkan semua perubahan
git add .

# Atau tambahkan file spesifik
git add src/api/routes/follows.py

# Commit dengan pesan deskriptif
git commit -m "fix: handle duplicate follow gracefully with 409 Conflict"

# Push ke branch aktif
git push

# Atau push ke branch spesifik
git push origin main
```

### Workflow Branch (Fitur Baru)

```bash
# Buat branch baru untuk fitur
git checkout -b feature/add-like-system

# ... kerjakan fitur ...

# Commit
git add .
git commit -m "feat: add like/unlike endpoint for insider signals"

# Push branch baru ke GitHub
git push origin feature/add-like-system

# Buka Pull Request di GitHub UI
# Setelah di-merge, kembali ke main dan sync
git checkout main
git pull origin main
```

### Tips Git Penting

```bash
# Lihat riwayat commit
git log --oneline -10

# Lihat perubahan sebelum commit
git diff

# Batalkan perubahan file (belum di-stage)
git checkout -- src/main.py

# Batalkan staging (sudah git add tapi belum commit)
git reset HEAD src/main.py

# Lihat remote URLs
git remote -v
```

---

## 👨💻 Pengembangan

### Menambahkan Fitur Like/Komentar

1. Tambahkan model di `src/db/models.py`:
   ```python
   class Like(Base):
       __tablename__ = "likes"
       id = ...
       user_id = ...
       signal_id = ...
   ```

2. Buat repository `src/db/repositories/like_repo.py`

3. Buat service `src/core/like_service.py`

4. Tambahkan route di `src/api/routes/likes.py`

5. Include router di `src/main.py`

6. Jalankan `alembic revision --autogenerate -m "add likes table"`

7. `alembic upgrade head`

### Manajemen Migrasi Database

```bash
# Buat migrasi baru (auto-detect perubahan model)
alembic revision --autogenerate -m "add likes table"

# Terapkan semua migrasi
alembic upgrade head

# Rollback satu versi
alembic downgrade -1

# Rollback ke awal
alembic downgrade base

# Lihat versi saat ini
alembic current

# Lihat histori migrasi
alembic history
```

### Aturan Kode

- ✅ Type hints wajib di semua fungsi
- ✅ Docstring untuk setiap fungsi publik
- ✅ Ikuti PEP 8 (gunakan `black`, `isort`)
- ✅ Semua test harus lulus sebelum merge
- ❌ Jangan commit file `.env` asli
- ❌ Jangan hardcode credentials

---

## 🔒 Kontribusi (Tim Internal)

Repositori private – hanya tim internal GAS.

### Langkah Kontribusi

1. Buat branch dari `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/nama-fitur
   ```
2. Implementasi fitur.
3. Pastikan semua test lulus: `pytest tests/ -v`
4. Commit dengan pesan jelas (lihat format di atas).
5. Push dan buka Pull Request ke `develop`.
6. Tunggu code review dari tim.

### Aturan Penting

- 🔒 Jangan sebarkan kode ke luar tim.
- 🔑 Jangan commit API keys atau credentials.
- 🌿 Gunakan environment variable untuk semua konfigurasi.
- 📝 Update README jika menambahkan endpoint baru.

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS.**
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.

Hubungi: ridwan@gasstrategy.io

---

**🔥 GAS Strategy – Sosial Trading untuk Komunitas Cerdas**
