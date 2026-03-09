# ⚡ GAS Realtime Hub

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Realtime Layer**  
Service WebSocket terpusat yang bertugas menerima data realtime dari berbagai sumber (MT5, engine, alert, sinyal) dan mendistribusikannya ke semua klien yang terhubung (terminal web, mobile app, dashboard). Memastikan setiap klien mendapatkan update harga, notifikasi, dan sinyal secara instan.

📛 **SERVICE NAME**
`gas-realtime-hub` | Realtime | 8111 | WebSocket Broadcast Hub | Menerima data dari berbagai sumber (MT5, Engine, Alert) dan melakukan broadcast ke client yang berlangganan. | Publisher → Hub → (broadcast) → Terminal/App | Active

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
- [API & Protokol WebSocket](#api--protokol-websocket)
- [Pengiriman Data ke Hub](#pengiriman-data-ke-hub)
- [Pengujian](#pengujian)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Kredit](#lisensi--kredit)

---

## 🔍 Ikhtisar

**gas-realtime-hub** adalah service WebSocket yang menjadi **pusat lalu lintas data realtime** di ekosistem GAS. Semua komponen yang menghasilkan data realtime (seperti `gas-mt5-websocket`, `gas-signal-service`, `gas-alert-engine`, dll.) mengirimkan data ke hub ini, dan hub akan **broadcast** ke semua klien yang berlangganan (subscribe) pada channel tertentu. Dengan arsitektur ini, klien tidak perlu terhubung ke banyak sumber, cukup satu koneksi WebSocket ke hub.

Service ini mendukung:
- **Broadcast ke semua klien** (misal: tick harga untuk semua simbol).
- **Subscribe ke channel spesifik** (misal: klien hanya ingin menerima update untuk simbol XAUUSD).
- **Private channel** (misal: notifikasi khusus user, dikirim hanya ke user tersebut).

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Sumber Data"
        MT5[gas-mt5-websocket] -->|tick/OHLC| Redis
        SIG[gas-signal-service] -->|sinyal baru| Redis
        ALERT[gas-alert-engine] -->|notifikasi| Redis
        QUANT[gas-quant-orchestrator] -->|sinyal quant| Redis
        OTHER[Service Lain] -->|data realtime| Redis
    end

    subgraph "Redis Pub/Sub"
        CH1[Channel: market:ticks]
        CH2[Channel: market:ohlc]
        CH3[Channel: signals:new]
        CH4[Channel: notifications:user:{user_id}]
    end

    subgraph "gas-realtime-hub"
        HUB[WebSocket Server]
        HUB -->|subscribe| Redis
        HUB -->|broadcast| CLIENTS
    end

    subgraph "Klien"
        WEB[Web Terminal]
        MOBILE[Mobile App]
        DASH[Dashboard]
    end

    MT5 -->|publish| CH1
    SIG -->|publish| CH3
    ALERT -->|publish| CH4
    HUB -->|subscribe| CH1
    HUB -->|subscribe| CH2
    HUB -->|subscribe| CH3
    HUB -->|subscribe| CH4
    HUB -->|websocket| WEB
    HUB -->|websocket| MOBILE
    HUB -->|websocket| DASH
```

### Komponen Utama
1. **WebSocket Server** – Menerima koneksi dari klien, menangani subscribe/unsubscribe ke channel, dan mengirim pesan.
2. **Redis Pub/Sub Client** – Berlangganan ke channel Redis untuk menerima data dari service lain, lalu meneruskannya ke klien yang relevan.
3. **Channel Manager** – Mengelola mapping antara klien dan channel yang mereka subscribe.
4. **Authentication Middleware** – Memverifikasi token JWT (dari `gas-auth-service`) saat koneksi dibuat.

---

## 🔄 Alur Kerja

### 1. **Koneksi Klien**
   - Klien membuka koneksi WebSocket ke `ws://hub.gasstrategy.io:8111` dengan menyertakan token JWT di header atau sebagai parameter query.
   - Hub memverifikasi token ke `gas-auth-service` (via REST internal) atau secara lokal jika ada secret.
   - Jika valid, koneksi diterima dan klien diberi `connection_id`.

### 2. **Subscribe ke Channel**
   - Klien mengirim pesan JSON: `{ "type": "subscribe", "channels": ["market:XAUUSD", "user:123"] }`
   - Hub mencatat bahwa klien ini berlangganan ke channel tersebut.

### 3. **Penerimaan Data dari Publisher**
   - Service lain (misal `gas-mt5-websocket`) mempublikasikan data ke Redis channel, misal:
     ```
     PUBLISH market:ticks '{"symbol":"XAUUSD", "price":1950.5, "timestamp": ...}'
     ```
   - Hub yang berlangganan ke Redis channel `market:*` menerima pesan tersebut.

### 4. **Broadcast ke Klien**
   - Hub menentukan klien mana yang subscribe ke channel terkait (misal `market:XAUUSD`).
   - Mengirim pesan ke semua klien tersebut melalui koneksi WebSocket masing-masing.

### 5. **Unsubscribe / Disconnect**
   - Klien dapat mengirim `{ "type": "unsubscribe", "channels": [...] }` atau langsung menutup koneksi.
   - Hub membersihkan data subscription.

---

## ✨ Fitur Utama

- **Multi‑channel**: Setiap klien dapat subscribe ke banyak channel sekaligus.
- **Wildcard subscription**: Misal subscribe ke `market:*` untuk menerima semua data pasar.
- **Private channel**: Channel khusus user (misal `user:{user_id}`) yang hanya bisa diakses oleh user tersebut.
- **Autentikasi JWT**: Setiap koneksi diverifikasi, user_id diekstrak untuk private channel.
- **Scalability**: Dengan Redis Pub/Sub, hub dapat di‑scale horizontal (multiple instance) karena komunikasi antar instance via Redis.
- **Monitoring**: Endpoint health check dan metrics (Prometheus).
- **Logging**: Setiap koneksi dan pesan dicatat untuk debugging.

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **WebSocket Library:** `websockets` (asyncio) / `fastapi`
- **Web Framework (opsional untuk health):** FastAPI
- **Redis:** `redis.asyncio` untuk Pub/Sub
- **Autentikasi:** JWT verification
- **Container:** Docker, Docker Compose
- **Monitoring:** Prometheus endpoint (via `prometheus_client`)

---

## 📁 Struktur Direktori

```
gas-realtime-hub/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Entry point: menjalankan WebSocket server
│   ├── config.py                # Pydantic settings
│   ├── server/
│   │   ├── __init__.py
│   │   ├── websocket_server.py  # Logika WebSocket (koneksi, pesan)
│   │   ├── connection_manager.py # Mengelola semua koneksi aktif
│   │   └── auth.py               # Verifikasi JWT
│   ├── redis/
│   │   ├── __init__.py
│   │   └── pubsub.py            # Subscribe ke Redis channel, forward ke manager
│   ├── models/
│   │   └── messages.py           # Pydantic model untuk pesan WebSocket
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   └── monitoring/
│       └── metrics.py            # Endpoint Prometheus (opsional)
├── tests/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── requirements.txt
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
▶️ **Run**
```bash
python src/main.py
```
atau dengan Uvicorn:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8111 --reload
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
docker ps | grep gas-realtime-hub
```
⛔ **Stop**
```bash
docker-compose stop realtime-hub
```
🔄 **Restart**
```bash
docker-compose restart realtime-hub
```
❌ **Delete Container / Image**
```bash
docker-compose down -v
```

---

## 📦 2. SETUP GITHUB (FIRST TIME)

```bash
echo "# gas-realtime-hub" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-realtime-hub.git
git push -u origin main
```

---

## 🔁 3. UPDATE PROJECT (COMMIT & PUSH)

```bash
git add .
git commit -m "Update service realtime hub"
git push -u origin main
```

---

## 📛 4. CONTAINER NAMING

- Nama container: `gas-realtime-hub`
- Network: Menggunakan default bridge `gas-network` (atau disesuaikan di `docker-compose.yml`)

---

## 🌐 5. HEALTH CHECK (STATUS 200 OK)

**Endpoint:** `http://localhost:8111/health`

**Expected Response:**
```json
{
  "status": "ok",
  "service": "gas-realtime-hub",
  "connections": 0
}
```

---

## 🧪 6. DEBUG & LOGGING

**Docker Logs:**
```bash
docker logs -f gas-realtime-hub
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
URL untuk diarahkan dari API Gateway (jika melakukan routing WS):
```
ws://gas-realtime-hub:8111/
```

**Request Example**
Koneksi websocket dari client/gateway harus meneruskan header auth:
```javascript
const ws = new WebSocket('ws://hub.gasstrategy.io:8111?token=YOUR_JWT_TOKEN');
```

---

## 🧠 9. INTEGRASI DENGAN @goldenaistrategy

Service ini sesuai standarisasi ekosistem GAS. Bertindak sebagai "bridge" untuk menyebarkan sinyal `gas-signal-service`, notifikasi dari `gas-alert-engine`, dan data harga realtime dari `gas-mt5-websocket` ke semua terminal user atau frontend secara bersamaan.

---

## 🔄 10. KOMUNIKASI ANTAR SERVICE

**Network Configuration:**  
Pastikan Redis dan Hub berada dalam network yang sama.
```yaml
networks:
  gas-network:
    external: true
```
Service lain terhubung menggunakan redis pub/sub `redis://gas-redis:6379`.

**Service Communication:**
- **Publisher** mem-publish ke channel Redis (misal `market:XAUUSD`).
- **Hub** yang berlangganan secara asinkron menangkap pesan dari redis dan melakukan broadcast melalui WebSocket ke client.

---

## 📡 API & Protokol WebSocket

### Koneksi
```
ws://<host>:8111/?token=<JWT_TOKEN>
```

### Pesan dari Klien ke Server

#### Subscribe
```json
{
  "type": "subscribe",
  "channels": ["market:XAUUSD", "user:123", "signals:premium"]
}
```

#### Unsubscribe
```json
{
  "type": "unsubscribe",
  "channels": ["market:XAUUSD"]
}
```

#### Ping (keep-alive)
```json
{
  "type": "ping"
}
```

### Pesan dari Server ke Klien

#### Data Update
```json
{
  "type": "data",
  "channel": "market:XAUUSD",
  "data": {
    "symbol": "XAUUSD",
    "price": 1950.5,
    "timestamp": 1700000000
  }
}
```

#### Error / Info
```json
{
  "type": "error",
  "message": "Invalid channel"
}
```

#### Pong
```json
{
  "type": "pong"
}
```

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

**Hak Cipta © 2026 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.

Service ini dikembangkan sebagai bagian dari ekosistem **Golden AI Strategy**.
