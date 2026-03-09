# 🐍 GAS Engine Orchestrator (Python Edition)

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Otak utama yang mengoordinasikan seluruh proses analisis teknikal, deteksi Smart Money Concepts (SMC), dan pembangkitan sinyal trading.**  
> Service ini bertindak sebagai konduktor, memanggil engine‑engine spesifik, menggabungkan hasil, dan menerapkan aturan strategi untuk menghasilkan sinyal siap pakai.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Alur Kerja Lengkap](#alur-kerja-lengkap)
- [Komponen Internal](#komponen-internal)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
  - [Manajemen via Python (Development)](#manajemen-via-python-development)
  - [Manajemen via Docker (Production)](#manajemen-via-docker-production)
- [Tutorial Git & GitHub](#tutorial-git--github)
  - [Cara Push ke GitHub Pertama Kali](#1-cara-push-ke-github-pertama-kali)
  - [Cara Commit & Update Project ke GitHub](#2-cara-commit--update-project-ke-github)
- [Konfigurasi](#konfigurasi)
- [API Reference](#api-reference)
- [Keamanan & Konektivitas](#keamanan--konektivitas)
- [Pengujian](#pengujian)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)

---

## 🔍 Ikhtisar

**gas-engine-orchestrator** adalah service kunci di VPS 2 yang menerima permintaan analisis dari gateway (`gas-gateway-api`) atau dari service lain (misal `gas-terminal-service`). Tugas utamanya:

- Mengambil data pasar terkini (dari cache Redis atau langsung dari `gas-market-data-processor`).
- Memanggil **`gas-indicator-engine`** untuk menghitung indikator teknikal (RSI, MA, MACD, Bollinger Bands, dll).
- Memanggil **`gas-smc-engine`** untuk mendeteksi struktur SMC (Order Block, Fair Value Gap, Break of Structure, Change of Character).
- Menggabungkan semua hasil menjadi satu kesatuan data.
- Menjalankan aturan strategi dari **`gas-strategy-core`** (library internal) untuk menghasilkan sinyal beli/jual/tahan.
- Mengembalikan hasil analisis atau sinyal ke pemanggil, dan/atau mengirimkannya ke `gas-realtime-hub` untuk didistribusikan secara realtime ke klien.

Service ini dirancang modular dan dapat diperluas – menambahkan engine baru atau strategi kustom cukup dengan konfigurasi tanpa mengubah alur inti.

---

## 🏗️ Arsitektur

```
┌─────────────────┐      ┌─────────────────────────────────────────────────┐
│   Gateway       │      │               gas-engine-orchestrator            │
│ (gas-gateway-   │─────▶│  ┌──────────┐  ┌──────────┐  ┌──────────────┐  │
│    api)         │      │  │   API    │  │Orchestra-│  │   Aggregator  │  │
└─────────────────┘      │  │  Server  │──│   tor    │──│    & Strategy │  │
         │               │  └──────────┘  └────┬─────┘  └───────┬──────┘  │
         │               │                      │                 │        │
         │               │         ┌────────────┼─────────────────┼────┐   │
         │               │         ▼            ▼                 ▼    │   │
         │               │  ┌────────────┐ ┌────────────┐ ┌─────────────────┐
         │               │  │   Redis    │ │   Redis    │ │  gas-strategy-  │
         │               │  │   Cache    │ │   Queue    │ │   core (lib)    │
         │               │  └────────────┘ └────────────┘ └─────────────────┘
         │               └─────────────────────────────────────────────────┘
         │                                    │
         │                 ┌──────────────────┼──────────────────┐
         ▼                 ▼                  ▼                  ▼
┌─────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Klien (Web,   │ │   gas-       │ │   gas-smc-   │ │   gas-market- │
│   Telegram,     │ │ indicator-   │ │   engine     │ │ data-processor│
│   Terminal)     │ │ engine       │ │              │ │   (lib)       │
└─────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘
```

---

## 🔄 Alur Kerja Lengkap

*(Sesuai dengan spesifikasi utama)*

---

## 🧩 Komponen Internal

*(Sesuai dengan spesifikasi utama)*

---

## 🛠️ Teknologi

*(Sesuai dengan spesifikasi utama)*

---

## ⚙️ Instalasi & Menjalankan

### Prasyarat
- Python 3.11+
- Docker & Docker Compose (untuk development dengan Redis dan engine lain)
- Protobuf compiler (`protoc`) jika mengubah file proto

### Langkah Cepat (Development)

1. Clone repositori (akses terbatas):
   ```bash
   git clone https://github.com/Muhamadridwanjr/gas-engine-orchestrator.git
   cd gas-engine-orchestrator
   ```

2. Buat virtual environment dan instal dependensi:
   ```bash
   python -m venv venv
   source venv/bin/activate  # atau `venv\Scripts\activate` di Windows
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

3. Salin file environment:
   ```bash
   cp .env.example .env
   # Edit sesuai konfigurasi lokal
   ```

---

## 🚀 Tutorial Terperinci: Manajemen Server (Python & Docker)

Berikut adalah panduan lengkap dan super detail untuk melakukan eksekusi aplikasi: RUN, STOP, RESTART, dan DELETE.

### Manajemen via Python (Development)

Digunakan saat Anda ingin mengembangkan aplikasi, melakukan debugging, dan melihat log secara langsung.

1. **RUN (Menjalankan Aplikasi):**
   Gunakan uvicorn untuk menjalankan server API.
   ```bash
   # Pastikan Anda berada dalam virtual environment
   source venv/bin/activate
   # Jalankan server dengan auto-reload
   uvicorn src.main:app --host 0.0.0.0 --port 8105 --reload
   ```

2. **STOP (Menghentikan Aplikasi):**
   Jika berjalan di terminal (foreground), tekan `CTRL + C` satu kali. Tunggu proses terhenti dengan aman.

3. **RESTART (Mengulang Aplikasi):**
   - Hentikan aplikasi: `CTRL + C`
   - Tekan tanda panah ke atas pada keyboard untuk memanggil ulang perintah `uvicorn src.main:app --host 0.0.0.0 --port 8105 --reload`
   - Tekan `Enter`.

4. **DELETE (Menghapus Lingkungan Development):**
   Jika ingin melakukan clean up dependensi:
   ```bash
   # Keluar dari virtual environment
   deactivate
   # Hapus folder venv
   rm -rf venv/
   # Hapus cache python
   find . -type d -name "__pycache__" -exec rm -rf {} +
   ```

---

### Manajemen via Docker (Production)

Digunakan untuk men-deploy aplikasi pada server (VPS) agas sistem terisolasi dan mudah di-manage. Aplikasi berjalan pada container bernama **`gas-engine-orchestrator`** dengan status yang memastikan `Up (healthy)`.

1. **RUN (Membuat dan Menjalankan Container):**
   Jalankan perintah ini di direktori project yang terdapat file `docker-compose.yml`.
   ```bash
   # Build image dan jalankan container di background (detached mode)
   docker-compose up -d --build
   
   # Cek status container (pastikan statusnya "Up (healthy)")
   docker ps | grep gas-engine-orchestrator
   ```

2. **STOP (Menghentikan Container):**
   Hanya menghentikan container dari proses berjalan, tanpa menghapus data atau container itu sendiri.
   ```bash
   docker-compose stop
   ```

3. **RESTART (Mengulang Container):**
   Sangat berguna jika ada pembaruan pada file `.env` tanpa adanya perubahan struktur kode.
   ```bash
   docker-compose restart
   ```
   **Catatan:** Jika ada *perubahan pada kode*, hindari menggunakan restart biasa. Sebaiknya jalankan ulang perintah RUN: `docker-compose up -d --build`.

4. **DELETE (Menghapus Container & Image):**
   ```bash
   # Menghapuskan semua container, network bawaan yang terkait dari service ini:
   docker-compose down
   
   # Hapus SECARA TOTAL beserta image dari docker system (Hard Delete):
   docker-compose down --rmi all -v
   ```

---

## 📖 Tutorial Git & GitHub

Berikut panduan detail untuk menghubungkan project lokal Anda dengan repository GitHub: `https://github.com/Muhamadridwanjr/gas-engine-orchestrator.git`.

### 1. Cara Push ke GitHub Pertama Kali

Anda hanya perlu melakukan ini **satu kali** di awal project untuk menginisialisasi Git dan menghubungkan lokal ke remote server GitHub.

```bash
# 1. Posisikan diri di folder utama project
cd /path/to/gas-engine-orchestrator

# 2. Inisiasi / Buat repository git lokal
git init

# 3. Tambahkan semua file agar dilacak oleh Git (titik berarti 'semua file')
git add .

# 4. Berikan pesan komit (commit message) pertama
git commit -m "first commit: inisialisasi project gas-engine-orchestrator"

# 5. Ganti/pastikan nama branch utama adalah 'main'
git branch -M main

# 6. Hubungkan project lokal ini ke alamat GitHub Anda
git remote add origin https://github.com/Muhamadridwanjr/gas-engine-orchestrator.git

# 7. Push repository lokal Anda ke GitHub dan jadikan 'main' sebagai default upstream
git push -u origin main
```

### 2. Cara Commit & Update Project ke GitHub

Gunakan serangkaian langkah berikut setiap kali Anda selesai melakukan pembaruan kode dan ingin menyimpannya di GitHub.

```bash
# 1. Cek status file mana saja yang berubah
git status

# 2. Tambahkan perubahan siap commit (staging)
git add .
# (Atau jika ingin spesifik satu file: git add nama_file.py)

# 3. Buat commit dengan pesan yang jelas (apa yang Anda ubah/tambahkan)
git commit -m "feat: menambah endpoint analyze dan signal"

# 4. Push / Unggah perubahan terbaru ke GitHub
git push
```

---

## 🔒 Keamanan & Konektivitas

Sesuai standar ekosistem GAS:
- **Konektivitas Service**: Container `gas-engine-orchestrator` tergabung dalam docker network eksternal (misal: `gas-network`) sehingga dapat "berbicara" langsung dengan `gas-gateway-api` pada port internal masing-masing tanpa harus melewati public internet.
- **Validasi JWT & Autentikasi**: Endpoint dilindungi dengan middleware JWT untuk mencegah akses tidak sah.
- **Healthcheck `200 OK`**: Service dan Docker Compose dilengkapi utilitas `/health` (curl status: healthy) guna mendeteksi crash, sehingga auto-rekoveri bisa bekerja secara optimal.

---

## 🔧 Konfigurasi

Konfigurasi menggunakan environment variable (file `.env`) atau langsung di system.

| Variabel                      | Nilai Default        | Deskripsi                                       |
|-------------------------------|----------------------|-------------------------------------------------|
| `PORT`                        | 8105                 | Port HTTP service                               |
| `REDIS_HOST`                  | localhost            | Host Redis                                      |
| `REDIS_PORT`                  | 6379                 | Port Redis                                      |
| `REDIS_PASSWORD`              | (kosong)             | Password Redis                                  |
| `INDICATOR_ENGINE_GRPC_URL`   | localhost:8201       | gRPC endpoint gas-indicator-engine              |
| `SMC_ENGINE_GRPC_URL`         | localhost:8202       | gRPC endpoint gas-smc-engine                    |
| `STRATEGY_PATH`               | ./strategies         | Path ke folder aturan strategi (YAML)           |
| `JWT_SECRET_KEY`              | (harus diisi)        | Secret key untuk verifikasi JWT                 |
| `LOG_LEVEL`                   | INFO                 | Level logging (DEBUG, INFO, WARNING, ERROR)     |
| `ENVIRONMENT`                 | development          | environment (development/staging/production)    |

---

## 📡 API Reference

### Endpoint REST

| Method | Endpoint        | Deskripsi                                      | Request Body                                                                 | Response                                                                 |
|--------|-----------------|------------------------------------------------|------------------------------------------------------------------------------|---------------------------------------------------------------------------|
| POST   | `/analyze`      | Menganalisis simbol dengan parameter tertentu  | `{"symbol":"XAUUSD","timeframe":"H1","indicators":["RSI"],"smc":true}`      | `{"symbol":..., "indicators":..., "smc":..., "signal":...}`              |
| GET    | `/health`       | Pengecekan kesehatan service                   | -                                                                            | `{"status": "ok"}`                                                        |
| POST   | `/signal`       | Menghasilkan sinyal berdasarkan strategi       | `{"symbol":"EURUSD","timeframe":"M15","strategy":"golden_cross"}`           | `{"symbol":..., "signal": "BUY", "metadata":...}`                         |
| GET    | `/strategies`   | Mendaftar semua strategi yang tersedia         | -                                                                            | `[{"name": "rsi_fvg", "version": "1.0"}, ...]`                            |

---

## 🔒 Kontribusi (Tim Internal)

Repositori ini bersifat **private** dan hanya diperuntukkan bagi tim internal GAS. Seluruh pengembangan dilakukan secara tertutup untuk menjaga kerahasiaan strategi dan keunggulan kompetitif.

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2026 Muhamad RidwanJr dan Tim GAS. Seluruh hak cipta dilindungi undang-undang.**

Repositori ini dan seluruh kode di dalamnya adalah milik eksklusif **Muhamad RidwanJr** dan tim **GAS (Gas Automatic Strategy)**.

**🔥 GAS Strategy – Membangun Masa Depan Trading Algoritmik dengan Python**
