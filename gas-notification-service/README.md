# 📢 GAS Notification Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Realtime Layer**  
Service pengiriman notifikasi multi‑channel dengan sistem antrean. Menerima permintaan notifikasi dari berbagai komponen (alert engine, signal service, quant engine, dll.), menempatkannya dalam antrean, dan mengirimkannya ke kanal yang sesuai: **Telegram, Web Push, Email**. Didukung dengan mekanisme retry, rate limiting, dan templating pesan.

📛 **SERVICE NAME**
`gas-notification-service` | Realtime | 8112 | Multi-channel Notifier | Mengelola pengiriman notifikasi ke Telegram, Web, dan Email dengan sistem antrean (queueing). | Alert/Signal → Notification → Telegram/Push | Active

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

**gas-notification-service** bertugas mengirim notifikasi ke pengguna melalui berbagai kanal. Service ini menerima permintaan dari service lain (misal `gas-alert-engine`, `gas-signal-service`, `gas-quant-orchestrator`) melalui REST API, menempatkannya dalam antrean Redis, lalu memprosesnya secara asinkron menggunakan worker. Dengan pendekatan ini, pengiriman notifikasi tidak menghambat service pengirim dan dapat diskalakan secara horizontal.

Notifikasi dapat dikirim ke:
- **Telegram** – melalui bot Telegram yang sudah terdaftar.
- **Web Push** – dikirim ke `gas-realtime-hub` untuk diteruskan ke klien yang terhubung via WebSocket.
- **Email** – via SMTP.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Sumber Notifikasi"
        ALERT[gas-alert-engine]
        SIGNAL[gas-signal-service]
        QUANT[gas-quant-orchestrator]
        JOURNAL[gas-journal-service]
        SMC[gas-smc-engine]
    end

    subgraph "gas-notification-service"
        API[REST API :8112]
        QUEUE[Redis Queue: notifications]
        WORKER[Worker (Celery/RQ)]
    end

    subgraph "Output Channels"
        TG[Telegram Bot API]
        WS[gas-realtime-hub]
        SMTP[SMTP Server]
    end

    ALERT -->|POST /notify| API
    SIGNAL -->|POST /notify| API
    QUANT -->|POST /notify| API
    JOURNAL -->|POST /notify| API
    SMC -->|POST /notify| API

    API -->|enqueue| QUEUE
    WORKER -->|dequeue| QUEUE
    WORKER -->|send| TG
    WORKER -->|send| WS
    WORKER -->|send| SMTP

    WS -->|WebSocket| CLIENT[Web/Mobile Client]
    TG -->|Telegram| USER[User's Telegram]
    SMTP -->|Email| USER_EMAIL[User's Email]
```

### Komponen Utama
- **REST API** – Menerima permintaan notifikasi dari service internal (dengan API key) dan menempatkannya ke antrean.
- **Redis Queue** – Menyimpan pesan notifikasi yang belum terkirim. Bisa menggunakan Celery atau RQ.
- **Worker** – Mengambil pesan dari antrean, memproses pengiriman ke kanal yang diminta, menangani retry jika gagal.
- **Template Engine** – (Opsional) Membangun pesan berdasarkan template dan data yang diberikan.

---

## 🔄 Alur Kerja

1. **Service sumber** mengirim permintaan `POST /notify` ke `gas-notification-service` dengan body berisi:
   - `user_id` (untuk menentukan kanal mana yang aktif)
   - `channels` (list kanal tujuan: `telegram`, `web`, `email`)
   - `title`, `message`, `data` tambahan (misal link, image)
   - (Opsional) `template` jika menggunakan template engine.
2. **API** memvalidasi request (API key, format) dan menambahkan task ke Redis queue dengan status `pending`.
3. **Worker** secara asinkron mengambil task dari queue.
4. Untuk setiap kanal yang diminta, worker melakukan:
   - **Telegram**: memanggil Bot API dengan chat_id yang diperoleh dari `gas-user-service`.
   - **Web**: mengirim data ke `gas-realtime-hub` via Redis pub/sub, yang akan meneruskannya ke klien yang subscribe pada channel `user:{user_id}`.
   - **Email**: mengirim email via SMTP dengan template yang sesuai.
5. Jika pengiriman gagal (misal Telegram API error), worker akan melakukan **retry** dengan backoff (bisa diatur).
6. Setelah sukses atau gagal permanen, status task dicatat (opsional di database untuk riwayat notifikasi).

---

## ✨ Fitur Utama

- **Multi‑channel**: Kirim notifikasi ke Telegram, Web (realtime), dan Email dalam satu permintaan.
- **Antrean (Queue)**: Tidak ada notifikasi yang hilang meskipun layanan penerima sedang sibuk.
- **Retry & Backoff**: Pengiriman gagal akan diulang dengan jeda yang meningkat.
- **Rate Limiting**: Mencegah spam ke kanal tertentu (misal Telegram).
- **Templating**: Gunakan template (Jinja2) untuk membangun pesan dari data.
- **Preferensi Pengguna**: Hanya kirim ke kanal yang diaktifkan user (data dari `gas-user-service`).
- **Prioritas**: Notifikasi dapat memiliki prioritas (high, medium, low) yang mempengaruhi urutan antrean.
- **Tracking**: Riwayat notifikasi dapat disimpan di database (opsional).

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (untuk REST API)
- **Task Queue:** Celery (dengan Redis broker)
- **Redis:** Broker dan penyimpanan antrean
- **Telegram Bot:** `python-telegram-bot` atau request langsung ke API
- **Email:** SMTP via `aiosmtplib` / `email`
- **Web Push:** Redis pub/sub ke `gas-realtime-hub`
- **Templating:** Jinja2
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-notification-service/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /notify
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── queue.py                  # Interface ke Redis queue (Celery/RQ)
│   │   └── exceptions.py
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── celery_app.py             # Inisialisasi Celery
│   │   └── tasks.py                  # Task pengiriman notifikasi
│   ├── channels/
│   │   ├── __init__.py
│   │   ├── telegram.py                # Pengiriman via Telegram
│   │   ├── web.py                      # Pengiriman via WebSocket (hub)
│   │   └── email.py                    # Pengiriman via SMTP
│   ├── templates/                       # Folder untuk template email/telegram
│   │   └── email_notification.jinja2
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   └── monitoring/
│       └── metrics.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── requirements-dev.txt
└── README.md
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
Pastikan Docker dan Docker Compose telah terinstal.
```bash
docker-compose up -d --build
```

---

## ⚙️ 1. TUTORIAL MANAGEMENT SERVICE

### 🐍 Python Mode
▶️ **Run API**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8112 --reload
```
▶️ **Run Worker**
```bash
celery -A src.workers.celery_app worker --loglevel=info
```
⛔ **Stop**
`Ctrl + C` pada terminal.

🔄 **Restart**
Hentikan lalu jalankan ulang perintah Run.

### 🐳 Docker Mode
▶️ **Build & Run**
```bash
docker-compose up -d --build
```
📊 **Check Status**
```bash
docker ps | grep notification-
```
⛔ **Stop**
```bash
docker-compose stop notification-api notification-worker
```
🔄 **Restart**
```bash
docker-compose restart notification-api notification-worker
```
❌ **Delete Container / Image**
```bash
docker-compose down -v
```

---

## 📦 2. SETUP GITHUB (FIRST TIME)

```bash
echo "# gas-notification-service" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-notification-service.git
git push -u origin main
```

---

## 🔁 3. UPDATE PROJECT (COMMIT & PUSH)

```bash
git add .
git commit -m "Update service notification"
git push -u origin main
```

---

## 📛 4. CONTAINER NAMING

- Nama container: `gas-notification-service-api` dan `gas-notification-service-worker`
- Network: Menggunakan default bridge `gas-network` (atau disesuaikan di `docker-compose.yml`)

---

## 🌐 5. HEALTH CHECK (STATUS 200 OK)

**Endpoint:** `http://localhost:8112/health`

**Expected Response:**
```json
{
  "status": "ok",
  "service": "gas-notification-service"
}
```

---

## 🧪 6. DEBUG & LOGGING

**Docker Logs:**
```bash
docker logs -f gas-notification-service-api
docker logs -f gas-notification-service-worker
```

**Application Logs:**
Logging akan tampil di stdout dan format JSON (opsional). Atur parameter `LOG_LEVEL` di `.env` ke `DEBUG`.

**Healthcheck Configuration:**
Docker healthcheck akan mem-ping endpoint `/health` secara berkala.

---

## 🟢 7. CONTAINER STATUS
Status expected: `Up (healthy)`

---

## 🔗 8. INTEGRASI GAS-GATEWAY-API

**Configuration**
URL untuk internal (REST API key protected) tidak perlu terekspos langsung ke gateway kecuali ada endpoint untuk user ngambil riwayat notifikasi.

---

## 🧠 9. INTEGRASI DENGAN @goldenaistrategy

Service ini sesuai standarisasi ekosistem GAS. Ini hanya fokus pada layer pengiriman pesan dan antrean. Sinyal yang digenerate oleh `gas-quant-orchestrator` atau `gas-smc-engine` akan di-POST ke API layanan ini untuk dieksekusi proses notifikasinya ke berbagai channel (Telegram, dll).

---

## 🔄 10. KOMUNIKASI ANTAR SERVICE

**Network Configuration:**  
```yaml
networks:
  gas-network:
    external: true
```
Antar service menggunakan nama container, misal POST ke `http://gas-notification-service-api:8112/notify`.

---

## 📡 API Reference

### Endpoint Internal (dengan API Key)

Semua endpoint memerlukan header `X-API-Key`.

#### `POST /notify`

**Request Body:**
```json
{
  "user_id": "uuid-user-123",
  "channels": ["telegram", "web", "email"],
  "title": "Alert: Harga Emas Tembus 2000",
  "message": "Harga XAUUSD telah mencapai level 2000.",
  "data": {
    "symbol": "XAUUSD"
  },
  "priority": "high",
  "template": "price_alert"
}
```

**Response:** `202 Accepted`
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

#### `GET /health` – Health check
Response: `{"status": "ok"}`

---

## 🔒 Kontribusi (Tim Internal)

Repositori ini bersifat **private** – hanya untuk tim internal GAS.  

---

## 📄 Lisensi & Kredit

**Hak Cipta © 2026 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.
