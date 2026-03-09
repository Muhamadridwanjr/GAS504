# 📡 GAS Signal Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Pusat manajemen sinyal trading dari berbagai sumber.**  
> Service ini bertugas menerima, menyimpan, dan mendistribusikan sinyal trading dengan sistem tier (insider, premium, ultimate). Sinyal dapat berasal dari analisis mandiri user (insider), dari engine indikator/SMC (premium), atau dari AI/developer (ultimate). Service ini juga menangani query sinyal dengan mempertimbangkan hak akses user melalui integrasi dengan `gas-billing-service`.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Alur Kerja](#alur-kerja)
- [Fitur Utama](#fitur-utama)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan (TUTORIAL LENGKAP)](#instalasi--menjalankan-tutorial-lengkap)
- [Konfigurasi](#konfigurasi)
- [Database Schema](#database-schema)
- [API Reference](#api-reference)
- [Pengujian](#pengujian)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)

---

## 🔍 Ikhtisar

**gas-signal-service** adalah service mandiri yang mengelola seluruh sinyal trading dalam ekosistem GAS. Sinyal dikategorikan dalam tiga tier:

- **Insider**: Sinyal yang dibuat oleh pengguna biasa (misal dari analisa mandiri) dan dapat dibagikan ke pengikut/follower. Bersifat sosial.
- **Premium**: Sinyal yang dihasilkan secara otomatis oleh sistem berdasarkan indikator teknikal dan SMC (dari `gas-engine-orchestrator`). Hanya dapat diakses oleh pengguna dengan level tertentu atau yang memiliki paket premium.
- **Ultimate**: Sinyal eksklusif dari AI/developer, membutuhkan akses tertinggi (VIP Elite).

Service ini menyediakan endpoint untuk:
- Menerima sinyal baru dari berbagai sumber (dengan autentikasi dan validasi).
- Menyimpan sinyal ke database PostgreSQL dengan metadata lengkap (tier, sumber, aset, timeframe, harga entry, SL, TP, dll).
- Mengambil daftar sinyal berdasarkan filter (simbol, tier, waktu, dll) dengan memperhatikan hak akses user via `gas-billing-service`.
- Menyediakan notifikasi realtime (melalui Redis pub/sub) ke `gas-realtime-hub` untuk diteruskan ke klien yang subscribe.

---

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌────────────────────────────────────┐
│   Sumber Sinyal │     │        gas-signal-service          │
│  (Orchestrator, │────▶│  ┌──────────┐  ┌───────────────┐  │
│   User, AI)     │     │  │   API    │  │   Service     │  │
└─────────────────┘     │  │  Server  │──│    Core       │  │
                        │  └──────────┘  └───────┬───────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │        Database (PostgreSQL)│  │
                        │  └─────────────────────────────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │   Redis (cache + pub/sub)   │  │
                        │  └─────────────────────────────┘  │
                        └────────────────────────────────────┘
                                      │
                                      ▼
                        ┌─────────────────────────────┐
                        │      gas-billing-service    │
                        │  (untuk cek akses user)     │
                        └─────────────────────────────┘
```

### Komunikasi Antar Service

- **REST API** (port 8106) – Digunakan oleh sumber sinyal (orchestrator, user) untuk mengirim sinyal, dan oleh klien (web/telegram) untuk mengambil sinyal.
- **gRPC** (opsional) – Untuk komunikasi internal dengan service lain yang memerlukan throughput tinggi.
- **Redis** – Untuk caching sinyal terbaru dan pub/sub notifikasi ke `gas-realtime-hub`.
- **PostgreSQL** – Penyimpanan utama sinyal dan metadata.
- **Integrasi dengan `gas-billing-service`** – Setiap permintaan akses sinyal akan divalidasi via REST/gRPC ke billing service untuk memastikan user memiliki hak yang sesuai.

---

## 🔄 Alur Kerja

### 1. **Menerima Sinyal Baru**
   - Sumber: `gas-engine-orchestrator` (sinyal premium/ultimate), `gas-social-service` (sinyal insider dari user), atau manual dari developer.
   - Request `POST /signals` dengan body berisi detail sinyal dan `tier`.
   - Service memvalidasi data (simbol, harga, dll) dan menyimpan ke database.
   - Jika sinyal bersifat publik (premium/ultimate) atau untuk follower, publish ke Redis channel `signals:new` untuk notifikasi realtime.

### 2. **User Meminta Daftar Sinyal**
   - User (terautentikasi) melakukan `GET /signals` dengan filter (tier, simbol, dll).
   - Service memanggil `gas-billing-service` untuk mendapatkan level user dan tier apa saja yang dapat diakses.
   - Query database hanya mengembalikan sinyal dengan tier yang diizinkan.
   - Hasil dikembalikan dalam format JSON.

### 3. **User Berlangganan Sinyal Realtime**
   - User dapat subscribe ke channel Redis tertentu via WebSocket di `gas-realtime-hub`.
   - `gas-signal-service` akan mengirim notifikasi sinyal baru ke Redis pub/sub, dan hub meneruskannya ke klien.

---

## ✨ Fitur Utama

- **Multi‑tier sinyal**: Insider, Premium, Ultimate.
- **Filter fleksibel**: Berdasarkan simbol, timeframe, tier, waktu, sumber.
- **Integrasi billing**: Validasi akses otomatis.
- **Notifikasi realtime**: Redis pub/sub untuk update langsung.
- **Manajemen sinyal**: CRUD untuk admin/internal.
- **History sinyal**: Menyimpan riwayat untuk analisis dan jurnal.
- **Pagination dan sorting** pada endpoint list.

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Database:** PostgreSQL (dengan SQLAlchemy / asyncpg)
- **Cache/Message Broker:** Redis (redis-py asyncio)
- **Validasi:** Pydantic
- **Autentikasi:** JWT (verifikasi via `gas-auth-service`, atau internal)
- **Testing:** pytest, httpx
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
.
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py      # Dependency injection (auth, db, redis)
│   │   ├── middleware.py        # Logging, error handling
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── signals.py       # Endpoint sinyal
│   │   │   └── internal.py      # Endpoint untuk internal (gRPC/REST)
│   │   └── models.py            # Pydantic models untuk request/response
│   ├── core/
│   │   ├── __init__.py
│   │   ├── service.py           # Logika bisnis (simpan, query)
│   │   ├── billing_client.py    # Klien untuk gas-billing-service
│   │   └── exceptions.py        # Custom exceptions
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py          # Koneksi PostgreSQL (async)
│   │   ├── models.py            # SQLAlchemy models
│   │   └── repositories/
│   │       ├── __init__.py
│   │       └── signal_repo.py   # Query ke tabel signals
│   ├── redis/
│   │   ├── __init__.py
│   │   └── client.py            # Redis client dan pub/sub
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   ├── config.py                # Pydantic settings
│   └── main.py                  # Entry point FastAPI
├── migrations/                   # Alembic (jika digunakan)
├── tests/
│   ├── unit/
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

## ⚙️ Instalasi & Menjalankan (TUTORIAL LENGKAP)

### 🚀 Menjalankan dengan Python (Tanpa Docker/Untuk Development)

Menjalankan langsung dengan Python ideal untuk saat Anda sedang meng-coding (developer mode).

1. **Clone repository (Bila belum ada):**
   ```bash
   git clone https://github.com/Muhamadridwanjr/gas-signal-service.git
   cd gas-signal-service
   ```

2. **Buat & Aktifkan Virtual Environment:**
   Linux/macOS:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
   Windows (CMD/PowerShell):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Siapkan Konfigurasi:**
   ```bash
   cp .env.example .env
   ```
   Lalu sesuaikan nilai `DATABASE_URL` dan `REDIS_URL` di file `.env` dengan server postgres/redis lokal Anda.

5. **Jalankan Aplikasi:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8106 --reload
   ```
   *(Aplikasi bisa diakses di http://localhost:8106/docs)*

> ***Cara Stop (`Stop`):*** Tekan `CTRL + C` di terminal tempat uvicorn berjalan.
> ***Cara Restart (`Restart`):*** Karena pakai flag `--reload`, aplikasi otomatis restart saat kode disave. Jika ingin manual, kill proses (Ctrl+C) lalu jalankan kembali perintah uvicorn di atas.

---

### 🐳 Menjalankan dengan Docker Compose (Sangat Disarankan!)

Ini adalah cara standar produksi (di-deploy ke server).

1. **Siapkan Konfigurasi:**
   ```bash
   cp .env.example .env
   # ubah isi .env sesuai peruntukan
   ```

2. **Build dan Jalankan Container (RUN):**
   Ini akan mengunduh docker python, install dependencies (dari requirements.txt) dan menjalankan uvicorn di background.
   ```bash
   docker-compose up -d --build
   ```

3. **Melihat Log (Opsional):**
   ```bash
   docker-compose logs -f
   ```

4. **Menghentikan Container (STOP):**
   Akan memberhentikan service tanpa menghapus datanya (network/volume).
   ```bash
   docker-compose stop
   ```

5. **Menghapus Container dan Network (DELETE):**
   Akan menghapus container `gas-signal-service` tapi tidak berimbas ke container `gas-network` (karena bersifat external).
   ```bash
   docker-compose down
   ```

6. **Restart Container (RESTART):**
   Gunakan perintah ini apabila ada perubahan environment variables atau habis update file tertentu.
   ```bash
   docker-compose restart
   ```
   Jika kode Python yang diupdate, lakukan re-build:
   ```bash
   docker-compose up -d --build
   ```

---

## 🛠️ PUSH PERTAMA KALI KE GITHUB:

Gunakan instruksi ini, BILA ingin mengupload kode gas-signal-service ini ke Github untuk pertama kalinya:

```bash
# Pastikan berada di dalam folder proyek
cd /lokasi/dari/gas-signal-service/

# Inisiasi git
git init

# Tambahkan atau masukkan semua file dan folder ke staging
git add .
# Atau jika hanya untuk README.md (sesuai req): git add README.md

# Komitmen pertama
git commit -m "first commit"

# Ganti branch menjadi `main`
git branch -M main

# Daftarkan repo origin
git remote add origin https://github.com/Muhamadridwanjr/gas-signal-service.git

# Push ke repositori (Push & hubungkan secara permanent ke origin)
git push -u origin main
```

**Bila repo sudah terhubung (Commit Update Lanjutan)**:
```bash
git add .
git commit -m "update: perbaikan pada signal routing dan model"
git push
```

---

## 🔧 Konfigurasi

Environment variables (file `.env`):

| Variabel | Nilai Default | Deskripsi |
|----------|---------------|-----------|
| `PORT` | 8106 | Port REST API |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@localhost:5432/gas_signals | Koneksi database async |
| `REDIS_URL` | redis://localhost:6379/0 | Koneksi Redis |
| `BILLING_SERVICE_URL` | http://localhost:8004 | Base URL gas-billing-service |
| `BILLING_API_KEY` | (opsional) | API key jika diperlukan |
| `JWT_SECRET_KEY` | (harus diisi) | Secret untuk verifikasi JWT (dari gas-auth-service) |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 🗃️ Database Schema

Tabel `signals`:

| Kolom | Tipe | Deskripsi |
|-------|------|-----------|
| id | UUID (PK) | Primary key |
| tier | ENUM('insider','premium','ultimate') | Kategori sinyal |
| source | VARCHAR | Sumber sinyal (misal: user_id, "orchestrator", "ai") |
| symbol | VARCHAR | Aset (XAUUSD, BTCUSD, dll) |
| timeframe | VARCHAR | M1, M5, H1, dll (opsional) |
| action | ENUM('BUY','SELL') | Arah sinyal |
| entry_price | DECIMAL | Harga entry |
| stop_loss | DECIMAL | Stop loss |
| take_profit | DECIMAL | Take profit |
| confidence | FLOAT | (opsional) 0-1 |
| metadata | JSONB | Informasi tambahan (alasan, gambar, dll) |
| created_at | TIMESTAMP | Waktu sinyal dibuat |
| expires_at | TIMESTAMP | (opsional) waktu kadaluarsa |
| is_active | BOOLEAN | Default true, bisa dinonaktifkan manual |

Indeks: `symbol`, `tier`, `created_at`, `source`.

---

## 📡 API Reference

### Autentikasi
Semua endpoint (kecuali health check) memerlukan JWT token di header `Authorization: Bearer <token>`. Token diverifikasi via `gas-auth-service` secara internal (middleware).

### Endpoints

#### `POST /signals` – Menambahkan sinyal baru
**Request Body:**
```json
{
  "tier": "premium",
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "action": "BUY",
  "entry_price": 2000.5,
  "stop_loss": 1990.0,
  "take_profit": 2020.0,
  "confidence": 0.85,
  "metadata": {
    "reason": "FVG + OB confluence"
  }
}
```
**Response:** `201 Created` dengan data sinyal (termasuk id).

#### `GET /signals` – Mendapatkan daftar sinyal
**Query Parameters:**
- `tier` (optional) – filter berdasarkan tier (bisa multiple, dipisah koma)
- `symbol` (optional)
- `timeframe` (optional)
- `from` (optional) – waktu mulai (ISO)
- `to` (optional) – waktu akhir
- `limit` (default 50, max 100)
- `offset` (default 0)
- `sort_by` (default "created_at") – field sorting
- `order` (default "desc")

**Response:**
```json
{
  "total": 123,
  "limit": 50,
  "offset": 0,
  "data": [ { ... }, ... ]
}
```

#### `GET /signals/{id}` – Detail sinyal
**Response:** Objek sinyal tunggal.

#### `DELETE /signals/{id}` – Hapus sinyal (hanya untuk admin/internal)
Memerlukan autorisasi khusus (role admin).

#### `POST /signals/{id}/expire` – Menandai sinyal kadaluarsa
Hanya untuk sumber sinyal atau admin.

#### `GET /health` – Health check
Response: `{"status": "ok"}`

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Validasi input.
- Query dengan filter.
- Integrasi mock dengan billing service.
- Redis pub/sub.

---

## 👨💻 Pengembangan

### Menambahkan Tier Baru
1. Update enum `tier` di database (migration).
2. Tambahkan di model Pydantic dan SQLAlchemy.
3. Sesuaikan logika billing client untuk memetakan tier ke level user.

### Menambahkan Sumber Sinyal Baru
Cukup kirim POST dengan `source` yang sesuai (misal "insider:user123" atau "orchestrator:swing").

### Aturan Kode
- Gunakan type hints.
- Sertakan docstring.
- Ikuti PEP 8.
- Pastikan semua test lulus.

---

## 🔒 Kontribusi (Tim Internal)

Repositori ini bersifat **private** dan hanya untuk tim internal GAS.

### Langkah Kontribusi
1. Buat branch baru (`feature/`, `fix/`).
2. Lakukan perubahan sesuai pedoman.
3. Commit dengan pesan jelas.
4. Buka Pull Request ke `develop`.
5. Tunggu review dan minimal satu approval.

### Aturan Penting
- Jangan menyebarluaskan kode ke pihak luar tanpa izin.
- Jangan commit kredensial.
- Gunakan environment variable untuk konfigurasi.

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS. Seluruh hak cipta dilindungi undang-undang.**

Repositori ini dan seluruh kode di dalamnya adalah milik eksklusif **Muhamad RidwanJr** dan tim **GAS (Gas Automatic Strategy)**.  
Tidak untuk disebarluaskan tanpa izin tertulis.

Untuk keperluan lisensi, kemitraan, atau pertanyaan, hubungi:  
📧 **ridwan@gasstrategy.io**

---

**🔥 GAS Strategy – Sinyal Presisi dari Berbagai Sumber**
