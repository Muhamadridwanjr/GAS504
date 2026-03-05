🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-tradingplan-service	API	9602	Plan Management	CRUD untuk rencana trading harian/mingguan user.	User → TradingPlan → DB							
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
echo "# gas-tradingplan-service" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-tradingplan-service.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-tradingplan-service.git
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
# 📅 GAS Trading Plan Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Layer Tambahan (Manajemen Pengguna)**  
Service yang menyediakan fitur manajemen rencana trading (trading plan) untuk setiap pengguna. Pengguna dapat membuat, membaca, memperbarui, dan menghapus rencana trading harian, mingguan, atau bulanan. Rencana ini dapat mencakup catatan analisis, level entry, stop loss, take profit, dan evaluasi. Data disimpan di PostgreSQL dan dapat diakses oleh pengguna melalui frontend atau API.

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

**gas-tradingplan-service** adalah service yang mengelola rencana trading pengguna. Fitur utamanya adalah CRUD (Create, Read, Update, Delete) untuk entitas rencana trading. Setiap rencana terkait dengan seorang pengguna (user_id) dan memiliki atribut seperti judul, deskripsi, tanggal, aset yang direncanakan, arah (BUY/SELL), level entry, stop loss, take profit, catatan, dan status (active/completed/canceled). Service ini memungkinkan pengguna untuk:

- Membuat rencana trading baru.
- Melihat daftar rencana mereka (dengan filter tanggal, status, dll).
- Memperbarui rencana yang ada.
- Menghapus rencana.
- Menandai rencana sebagai selesai atau dibatalkan.

Dengan adanya service ini, pengguna dapat mendokumentasikan strategi mereka, melacak rencana yang telah dibuat, dan mengevaluasi kinerja rencana di masa lalu. Data rencana juga dapat digunakan oleh service lain, misalnya `gas-journal-service` untuk membandingkan rencana dengan realisasi trade.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Pengguna"
        USER[Frontend / Mobile]
    end

    subgraph "API Gateway"
        GW[gas-gateway-api :8000]
    end

    subgraph "gas-tradingplan-service"
        API[REST API :9602]
        CORE[Plan Manager]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
    end

    USER -->|HTTP| GW
    GW -->|/tradingplan/*| API
    API --> CORE
    CORE --> DB
    CORE --> CACHE
    CACHE --> API
    API -->|response| GW
    GW --> USER
```

### Komponen Utama
- **REST API** (port 9602) – Menerima permintaan CRUD dari pengguna (via gateway) dan mengembalikan respons.
- **Plan Manager** – Logika bisnis untuk validasi, pembuatan, dan manipulasi rencana.
- **PostgreSQL** – Menyimpan data rencana trading (tabel `trading_plans`).
- **Redis Cache** – (Opsional) Menyimpan daftar rencana untuk akses cepat.

---

## 🔄 Alur Kerja

### **Membuat Rencana Baru**
1. Pengguna mengirim `POST /plans` dengan body JSON berisi detail rencana.
2. Gateway memverifikasi JWT dan menambahkan header `X-User-ID`.
3. Service menerima request, memvalidasi data (judul, tanggal, dll).
4. Menyimpan rencana ke database dengan `user_id` dari header.
5. Mengembalikan respons `201 Created` beserta ID rencana.

### **Mendapatkan Daftar Rencana**
1. Pengguna mengirim `GET /plans` dengan parameter filter opsional (status, dari tanggal, dll).
2. Service memeriksa cache (jika diaktifkan) berdasarkan user_id dan parameter.
3. Jika tidak ada di cache, query database.
4. Kembalikan daftar rencana dalam format JSON.

### **Memperbarui Rencana**
1. Pengguna mengirim `PUT /plans/{id}` dengan data yang diperbarui.
2. Service memeriksa apakah rencana dengan ID tersebut milik user yang sama.
3. Jika ya, perbarui data di database.
4. Kembalikan respons sukses.

### **Menghapus Rencana**
1. Pengguna mengirim `DELETE /plans/{id}`.
2. Service memeriksa kepemilikan, lalu hapus (soft delete atau hard delete sesuai konfigurasi).
3. Kembalikan respons `204 No Content`.

---

## ✨ Fitur Utama

- **CRUD lengkap**: Create, Read, Update, Delete untuk rencana trading.
- **Filter fleksibel**: Dapat memfilter berdasarkan status (active, completed, canceled), rentang tanggal, aset, dll.
- **Kepemilikan data**: Setiap rencana terikat dengan user_id, sehingga pengguna hanya dapat mengakses data mereka sendiri.
- **Soft delete** (opsional): Rencana tidak benar-benar dihapus, hanya ditandai sebagai `deleted_at`.
- **Cache Redis** (opsional): Mempercepat akses untuk daftar rencana yang sering dilihat.
- **Integrasi dengan gateway**: Semua request melewati gateway untuk autentikasi.

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Database:** PostgreSQL (SQLAlchemy + asyncpg)
- **Cache:** Redis (`redis.asyncio`) – opsional
- **Autentikasi:** Header `X-User-ID` dari gateway (JWT diverifikasi di gateway)
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-tradingplan-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /plans
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── plan_manager.py           # Logika bisnis
│   │   └── exceptions.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py                # SQLAlchemy models
│   │   └── repositories/
│   │       └── plan_repo.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_cache.py            # Opsional
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
- Redis (opsional)

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-tradingplan-service.git
   cd gas-tradingplan-service
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
   # Isi DATABASE_URL, REDIS_URL (opsional), dll.
   ```

5. Jalankan PostgreSQL dan Redis (via Docker):
   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15-alpine
   docker run -d --name redis -p 6379:6379 redis
   ```

6. Buat database:
   ```bash
   createdb -h localhost -U postgres gas_tradingplan
   ```

7. Jalankan migration (jika menggunakan Alembic):
   ```bash
   alembic upgrade head
   ```

8. Jalankan service:
   ```bash
   uvicorn src.main:app --reload --port 9602
   ```

### Dengan Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: gas_tradingplan
    volumes:
      - pg_data:/var/lib/postgresql/data

  redis:
    image: redis:alpine

  tradingplan-service:
    build: .
    ports:
      - "9602:9602"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pass@postgres:5432/gas_tradingplan
      - REDIS_URL=redis://redis:6379
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
| `PORT` | 9602 | Port REST API |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@localhost:5432/gas_tradingplan | Koneksi database async |
| `REDIS_URL` | (opsional) | Koneksi Redis (jika digunakan) |
| `CACHE_TTL` | 300 | TTL cache (detik) – hanya jika Redis aktif |
| `SOFT_DELETE` | true | Jika true, hapus secara logis (set `deleted_at`) |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

Semua endpoint di bawah memerlukan header `X-User-ID` yang diisi oleh gateway setelah verifikasi JWT. Endpoint admin mungkin memerlukan API key.

### **Public Endpoints (via Gateway)**

#### `POST /plans` – Membuat rencana baru

**Request Body:**
```json
{
  "title": "Swing Trade XAUUSD",
  "description": "Memanfaatkan FVG bullish di H1",
  "plan_date": "2025-03-15",
  "symbol": "XAUUSD",
  "direction": "BUY",
  "entry_price": 2000.5,
  "stop_loss": 1990.0,
  "take_profit": 2020.0,
  "notes": "Konfirmasi dengan RSI",
  "status": "active"
}
```

**Response:** `201 Created`
```json
{
  "id": "plan_123",
  "user_id": "user_456",
  "title": "Swing Trade XAUUSD",
  "created_at": "2025-03-14T10:00:00Z"
}
```

#### `GET /plans` – Mendapatkan daftar rencana

**Parameter Query:**
- `status` (string, optional) – `active`, `completed`, `canceled` (bisa multiple, dipisah koma)
- `from_date` (string, optional) – YYYY-MM-DD
- `to_date` (string, optional)
- `symbol` (string, optional)
- `limit` (int, default 50, max 100)
- `offset` (int, default 0)
- `sort_by` (string, default `-plan_date`)

**Response:**
```json
{
  "total": 10,
  "data": [
    {
      "id": "plan_123",
      "title": "Swing Trade XAUUSD",
      "plan_date": "2025-03-15",
      "symbol": "XAUUSD",
      "direction": "BUY",
      "entry_price": 2000.5,
      "stop_loss": 1990.0,
      "take_profit": 2020.0,
      "status": "active",
      "created_at": "2025-03-14T10:00:00Z"
    }
  ]
}
```

#### `GET /plans/{id}` – Mendapatkan detail rencana

#### `PUT /plans/{id}` – Memperbarui rencana

**Request Body:** (field yang ingin diubah, sama seperti POST)

#### `DELETE /plans/{id}` – Menghapus rencana (soft/hard sesuai konfigurasi)
**Response:** `204 No Content`

#### `PATCH /plans/{id}/complete` – Menandai rencana sebagai selesai
#### `PATCH /plans/{id}/cancel` – Menandai rencana sebagai dibatalkan

### **Internal Endpoints (dengan API Key)**
(Untuk keperluan admin atau service lain)

#### `GET /internal/plans/user/{user_id}` – Mendapatkan rencana user tertentu (dengan API key)

#### `GET /health` – Health check
```json
{"status": "ok"}
```

---

## 🔗 Integrasi dengan Service Lain

- **`gas-gateway-api` (8000)** – Entry point dari pengguna, meneruskan request ke service ini.
- **`gas-journal-service` (8107)** – Dapat menggunakan data rencana untuk membandingkan dengan trade real (misal: apakah trade sesuai rencana).
- **`gas-user-service` (8002)** – Untuk mendapatkan informasi pengguna (tidak langsung diperlukan, karena hanya user_id).
- **Redis** – Cache opsional.

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- CRUD operations.
- Validasi input.
- Filter dan pagination.
- Autentikasi (header X-User-ID).
- Soft delete behavior.

---

## 👨‍💻 Pengembangan

### Menambah Field Baru
1. Tambahkan kolom di model SQLAlchemy (`db/models.py`).
2. Perbarui migration (Alembic).
3. Tambahkan field di Pydantic model (`api/models.py`).
4. Perbarui repository jika perlu.

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

**🔥 GAS Trading Plan Service – Dokumentasi Strategi untuk Trader Disiplin**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  