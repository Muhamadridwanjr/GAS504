# 🌐 GAS MT5 WebSocket
Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 3 (Market Data Layer)

Streaming data realtime dari MT5 ke ekosistem GAS.
Service ini bertugas menerima data tick atau OHLC secara langsung dari MetaTrader 5 (baik via library MT5 Python maupun koneksi socket dari EA), lalu meneruskannya ke gas-realtime-hub untuk didistribusikan ke seluruh klien (web, terminal, telegram). Dengan demikian, seluruh sistem mendapatkan data pasar terkini secara realtime.

## 📋 Daftar Isi
- [Ikhtisar](#-ikhtisar)
- [Arsitektur](#-arsitektur)
- [Alur Kerja](#-alur-kerja)
- [Fitur Utama](#-fitur-utama)
- [Teknologi](#-teknologi)
- [Struktur Direktori](#-struktur-direktori)
- [Instalasi & Menjalankan](#-instalasi--menjalankan)
- [Panduan Pengoperasian (Python & Docker)](#-panduan-pengoperasian-python--docker)
- [Panduan GitHub](#-panduan-github)
- [Konfigurasi](#-konfigurasi)
- [Pengujian](#-pengujian)
- [Lisensi & Hak Cipta](#-lisensi--hak-cipta)

## 🔍 Ikhtisar
**gas-mt5-websocket** adalah komponen penting dalam aliran data pasar. Data yang dikirimkan meliputi:
- **Tick**: harga terbaru beserta volume dan waktu.
- **OHLC**: candle baru setiap periode (misal setiap menit, setiap 5 menit, dll), dapat dikonfigurasi.

Service ini beroperasi dalam dua mode:
1.  **Mode Local**: Berjalan di VPS Windows yang sama dengan MT5. Menggunakan library `MetaTrader5` Python untuk membaca data langsung.
2.  **Mode Socket**: Berjalan di VPS mana pun (Linux/Windows) dan menerima koneksi dari EA (Expert Advisor) yang berjalan di MT5 via WebSocket.

## 🏗️ Arsitektur
```text
┌─────────────┐     ┌────────────────────────────────────┐
│   MT5 EA    │     │        gas-mt5-websocket          │
│ (Socket Mode)│────▶│  ┌──────────┐  ┌───────────────┐  │
└─────────────┘     │  │  Socket   │  │   Processor   │  │
                    │  │  Server   │──│    & Forward  │  │
                    │  └──────────┘  └───────┬───────┘  │
                    │                         │          │
┌─────────────┐     │                         ▼          │
│ MT5 Terminal│     │  ┌─────────────────────────────┐  │
│ (Local Mode)│────▶│  │      MT5 Library Reader    │  │
└─────────────┘     │  └─────────────────────────────┘  │
                    └────────────────────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │  Redis (Pub/Sub)    │
                          │  channel: market:*  │
                          └─────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │ gas-realtime-hub    │
                          │ (WebSocket ke client)│
                          └─────────────────────┘
```

## 📁 Struktur Direktori
```text
.
├── src/
│   ├── __init__.py
│   ├── main.py                      # Entry point (memilih mode)
│   ├── config.py                     # Konfigurasi dari env
│   ├── models/
│   │   ├── __init__.py
│   │   └── messages.py               # Pydantic model untuk tick/ohlc
│   ├── connectors/
│   │   ├── __init__.py
│   │   ├── local_mt5.py              # Mode local: baca dari MT5
│   │   └── socket_server.py           # Mode socket: terima dari EA
│   ├── processor/
│   │   ├── __init__.py
│   │   └── forwarder.py               # Kirim ke Redis
│   ├── lib/
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── utils.py
│   └── redis_client/
│       ├── __init__.py
│       └── client.py                  # Redis async client
├── docker-compose.yml
├── Dockerfile
├── .env.example
├── requirements.txt
└── README.md
```

## 🚀 Instalasi & Menjalankan

### Prasyarat
- Python 3.11+
- Redis Server
- Docker & Docker Compose (untuk opsi container)

### Langkah Cepat
1. **Clone Repositori**:
   ```bash
   git clone https://github.com/Muhamadridwanjr/gas-mt5-websocket.git
   cd gas-mt5-websocket
   ```

2. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/macOS
   # atau
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   cp .env.example .env
   ```

---

## 🛠 Panduan Pengoperasian (Python & Docker)

### 🐍 Menggunakan Python (Manual)

| Aksi | Perintah |
| :--- | :--- |
| **RUN** | `python -m src.main` |
| **STOP** | Tekan `CTRL + C` di terminal |
| **RESTART** | Tekan `CTRL + C` lalu jalankan `python -m src.main` lagi |
| **DELETE (Cleanup)** | `rm -rf venv` (menghapus virtual environment) |

### 🐳 Menggunakan Docker (Rekomendasi)

Pastikan nama container adalah `gas-mt5-websocket`.

| Aksi | Perintah | Deskripsi |
| :--- | :--- | :--- |
| **RUN** | `docker-compose up -d --build` | Menjalankan di background dan build ulang jika ada perubahan. |
| **STOP** | `docker-compose stop` | Menghentikan container tanpa menghapus. |
| **RESTART** | `docker-compose restart` | Memulai ulang container yang sedang berjalan/berhenti. |
| **DELETE** | `docker-compose down` | Menghentikan dan menghapus container, network, dan image terkait. |
| **STATUS** | `docker ps` atau `docker-compose ps` | Memastikan status **Up (healthy)**. |
| **LOGS** | `docker logs -f gas-mt5-websocket` | Melihat log realtime untuk debugging. |

---

## 🐙 Panduan GitHub

### 1. Push Pertama Kali ke Repositori Baru
Jika repositori di GitHub masih kosong:
```bash
echo "# gas-mt5-websocket" >> README.md
git init
git add .
git commit -m "Initial commit: service structure and core logic"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-mt5-websocket.git
git push -u origin main
```

### 2. Commit & Update Project
Setiap kali ada perubahan kode:
```bash
git add .
git commit -m "Update: deskripsi perubahan kamu di sini"
git push origin main
```

---

## 🔧 Konfigurasi
Edit file `.env` untuk menyesuaikan parameter:

| Variabel | Nilai Default | Deskripsi |
| :--- | :--- | :--- |
| `MODE` | `socket` | `local` atau `socket` |
| `SOCKET_PORT` | `8110` | Port WebSocket server |
| `REDIS_URL` | `redis://localhost:6379/0` | URL Koneksi Redis |
| `LOG_LEVEL` | `INFO` | Level logging (`DEBUG`, `INFO`, `ERROR`) |

---

## 🧪 Pengujian
Untuk memastikan integrasi berjalan dengan baik:
1. Jalankan service: `docker-compose up -d`
2. Cek kesehatan container: `docker inspect --format='{{json .State.Health}}' gas-mt5-websocket`
3. Pastikan output menunjukkan `"status":"healthy"`.

Untuk integrasi dengan **gas-gateway-api**:
- Pastikan `gas-gateway-api` dapat berkomunikasi dengan service ini melalui network Docker yang sama (`gas-network`).
- Health check service ini akan mengembalikan status sukses jika port internal terbuka dan siap melayani.

---

## 👨‍💻 Pengembangan & Debugging
- Gunakan **Loguru** untuk logging yang detail. Log disimpan dan ditampilkan via stdout container.
- Pantau Redis menggunakan `redis-cli monitor` untuk melihat data yang dipublikasikan.
- Pastikan service ini adalah bagian dari project besar `goldenaistrategy/`.

---

## 📄 Lisensi & Hak Cipta
Hak Cipta © 2025 **Muhamad RidwanJr** dan **Tim GAS**.
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.

**GAS Strategy – Data Realtime MT5 ke Seluruh Ekosistem**
