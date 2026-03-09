# 📈 GAS MT5 Data Service

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 3 (Market Data Layer)**

> **Penyedia data OHLC historis dari MT5.**
> Service ini menyediakan REST API untuk mengambil data harga historis (OHLC) dari MetaTrader 5. Data dapat diambil langsung dari terminal MT5 (via library atau EA) atau dari database cache untuk mengurangi beban dan mempercepat respons. Terintegrasi dengan `gas-gateway-api` untuk autentikasi dan routing.

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
- [Pengujian](#pengujian)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)

---

## 🔍 Ikhtisar

**gas-mt5-data-service** menyediakan endpoint REST untuk mengambil data OHLC historis. Data dapat bersumber dari:

- **Live MT5 terminal** – Service terhubung ke MetaTrader 5 (via MT5 Python API atau EA) untuk mengambil data realtime/historis langsung.
- **Database cache** – Data yang sudah pernah diminta disimpan di PostgreSQL atau Redis untuk akses lebih cepat dan mengurangi permintaan berulang ke MT5.

Service ini digunakan oleh:
- `gas-engine-orchestrator` – untuk mendapatkan data saat menjalankan analisis.
- `gas-web-backend` – untuk menampilkan chart di frontend.
- Pengguna langsung (via gateway) – misal untuk backtesting atau analisis manual.

Semua request melalui `gas-gateway-api` untuk autentikasi dan logging.

---

## 🏗️ Arsitektur

```
┌─────────────────┐     ┌────────────────────────────────────┐
│  gas-gateway-api│────▶│      gas-mt5-data-service         │
│   (Port 8000)   │     │  ┌──────────┐  ┌───────────────┐  │
└─────────────────┘     │  │   REST   │  │   Service     │  │
                        │  │  API     │──│    Core       │  │
                        │  └──────────┘  └───────┬───────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │      MT5 Connector          │  │
                        │  │  (MT5 terminal / EA)       │  │
                        │  └─────────────────────────────┘  │
                        │                         │          │
                        │                         ▼          │
                        │  ┌─────────────────────────────┐  │
                        │  │   Database (PostgreSQL/Redis│  │
                        │  │         Cache Layer         │  │
                        │  └─────────────────────────────┘  │
                        └────────────────────────────────────┘
```

### Komunikasi

- **REST API** (port 8100) – Endpoint publik untuk mengambil data OHLC.
- **MT5 Connector** – Bisa menggunakan library `MetaTrader5` Python jika berjalan di VPS yang sama dengan terminal MT5, atau menggunakan socket/EA untuk komunikasi jarak jauh.
- **Database** – PostgreSQL untuk penyimpanan jangka panjang (jika diperlukan), Redis untuk cache sementara.

---

## ⚙️ Instalasi & Menjalankan

### Prasyarat
- Python 3.11+
- MetaTrader 5 (jika menggunakan MT5 lokal) – harus terinstall di Windows.
- Redis (untuk cache)
- Docker & Docker Compose (opsional tapi direkomendasikan)

### Langkah Cepat (Development) dengan Python

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/mridwans/gas-mt5-data-service.git
   cd gas-mt5-data-service
   ```

2. Buat virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Copy environment:
   ```bash
   cp .env.example .env
   # Sesuaikan konfigurasi (REDIS, MT5_PATH jika lokal, dll)
   ```

5. Jalankan Redis (via Docker) jika tidak ada Redis server yang menyala:
   ```bash
   docker run -d -p 6379:6379 --name gas-mt5-redis redis:alpine
   ```

6. Jalankan service `gas-mt5-data-service`:
   ```bash
   uvicorn src.main:app --reload --port 8100
   ```
   *Terminal akan terus menyala. Untuk STOP tekan `Ctrl+C`.*

### Dengan Docker Compose

1. Build dan jalankan service di background (`-d` / detached mode):
   ```bash
   docker-compose up -d --build
   ```

2. Lihat log container:
   ```bash
   docker-compose logs -f app
   ```
   *Tekan `Ctrl+C` untuk keluar dari logs (container tetap menyala).*

3. Menghentikan service:
   ```bash
   docker-compose down
   ```

4. Restart service:
   ```bash
   docker-compose restart app
   ```

5. Hapus semua container dan data (volume Redis):
   ```bash
   docker-compose down -v
   ```

**Pastikan status container Up (healthy):**
Jalankan `docker-compose ps` untuk melihat statusnya. Harus terdapat tulisan `Up (healthy)`.

---

## 🐙 Cara Push ke GitHub Pertama Kali

Anda dapat meng-upload project ini ke repo GitHub yang sudah dibuat (`https://github.com/mridwans/gas-mt5-data-service`):

```bash
# Inisialisasi git local
git init

# Tambahkan semua file
git add .

# Lakukan commit pertama
git commit -m "Initial commit: Set up gas-mt5-data-service project structure"

# Atur nama branch utama menjadi main
git branch -M main

# Tambahkan remote repository
git remote add origin https://github.com/mridwans/gas-mt5-data-service.git

# Push ke GitHub
git push -u origin main
```

*(Catatan: Pastikan Anda sudah login GitHub di terminal atau menggunakan token/SSH yang tepat).*

## 🔄 Cara Commit Update Project ke GitHub

Setiap kali Anda mengubah file (contoh: update route, ganti config), lakukan commit dan push:

```bash
# Lihat file apa yang berubah
git status

# Tambahkan semua perubahan ke staging
git add .

# Berikan pesan yang jelas mengenai update tersebut
git commit -m "feat: Menambahkan caching Redis untuk endpoint history"

# Kirim ke GitHub
git push
```

---

## 📡 API Reference

### Endpoint

#### `GET /history` – Mengambil data OHLC historis

**Query Parameters:**
- `symbol` (string, required) – Simbol, misal `XAUUSD`.
- `timeframe` (string, required) – Timeframe: `M1`, `M5`, `M15`, `M30`, `H1`, `H4`, `D1`, `W1`, `MN`.
- `from_time` (int, optional) – UNIX timestamp awal (dalam detik).
- `to_time` (int, optional) – UNIX timestamp akhir.
- `count` (int, optional) – Jumlah candle terakhir (jika `from_time` tidak ditentukan). Maks 5000.
- `include_volume` (bool, default true) – Sertakan volume.

**Contoh Request:**
```
GET /history?symbol=XAUUSD&timeframe=H1&count=100
```

#### `GET /health` – Health check
Response: `{"status": "ok", "service": "gas-mt5-data-service", "version": "1.0.0"}`

---

## 📄 Lisensi & Hak Cipta

**Hak Cipta © 2026 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Tidak untuk disebarluaskan tanpa izin tertulis.
