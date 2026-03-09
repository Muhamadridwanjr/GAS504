# 📊 GAS Indicator Engine

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Kalkulator indikator teknikal super lengkap untuk semua timeframe.**  
> Engine ini menerima data OHLC dari MT5 (via `gas-market-data-processor` atau Redis) dan mengembalikan nilai indikator sesuai permintaan. Mendukung lebih dari 100 indikator, termasuk moving averages, momentum, volume, volatility, trend, statistik, Hilbert transform, candlestick patterns, pivot points, demand zone, dan custom features. Dapat berjalan secara realtime (setiap candle baru) atau on‑demand.

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Fitur Indikator](#fitur-indikator)
- [Arsitektur](#arsitektur)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Tutorial Lengkap Docker dan Python](#tutorial-lengkap-docker-dan-python)
- [Cara Push Github Pertama Kali](#cara-push-github-pertama-kali)
- [Konfigurasi](#konfigurasi)
- [API Reference](#api-reference)

---

## 🔍 Ikhtisar

**gas-indicator-engine** adalah service mandiri yang menyediakan berbagai indikator teknikal berdasarkan data harga (OHLC) dari MT5. Data dapat diberikan langsung dalam request atau diambil dari cache Redis.
Dilengkapi juga gRPC untuk komunikasi internal super cepat, serta REST API.

---

## 🚀 Tutorial Lengkap Docker dan Python

### Menjalankan dengan Python (Local Development)

1. **Buat Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

2. **Install Dependencies:**
   Pastikan Anda menginstall `TA-Lib` C library terlebih dahulu.
   ```bash
   # Di Ubuntu
   sudo apt-get install ta-lib
   # Di macOS
   brew install ta-lib
   
   pip install -r requirements-dev.txt
   ```

3. **Menjalankan Service (REST):**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8203 --reload
   ```

4. **Menjalankan Service (gRPC):**
   ```bash
   python src/main.py --mode grpc
   ```

5. **Stop:** `Ctrl+C` pada terminal.

### Menjalankan dengan Docker

1. **Build Container:**
   Pastikan nama container di `docker-compose.yml` adalah `gas-indicator-engine`.
   ```bash
   docker-compose build
   ```

2. **Run Container (Background):**
   ```bash
   docker-compose up -d
   ```

3. **Melihat Status Container (harus Up/Healthy):**
   ```bash
   docker ps -a | grep gas-indicator-engine
   ```

4. **Melihat Log (Debug):**
   ```bash
   docker logs -f gas-indicator-engine
   ```

5. **Stop Container:**
   ```bash
   docker-compose down
   ```

6. **Restart Container:**
   ```bash
   docker-compose restart gas-indicator-engine
   ```

7. **Delete Container / Images:**
   ```bash
   docker rm -f gas-indicator-engine
   docker rmi gas-indicator-engine_gas-indicator-engine
   ```

---

## 🐙 Cara Push Github Pertama Kali

Jika Anda sudah membuat repository di GitHub, ikuti langkah berikut:

1. **Inisialisasi Git:**
   ```bash
   git init
   ```

2. **Tambahkan file ke Staging Area:**
   ```bash
   git add .
   ```

3. **Buat Commit Pertama:**
   ```bash
   git commit -m "first commit: inisialisasi gas-indicator-engine"
   ```

4. **Ubah branch utama ke `main`:**
   ```bash
   git branch -M main
   ```

5. **Tambahkan remote origin repository Anda:**
   ```bash
   git remote add origin https://github.com/Muhamadridwanjr/gas-indicator-engine.git
   ```

6. **Push ke GitHub:**
   ```bash
   git push -u origin main
   ```

### Cara Commit Update (Selanjutnya)
```bash
git add .
git commit -m "update: fitur X"
git push
```

---

Untuk detil lebih lanjut tentang Arsitektur dan API, bisa lihat file referensi API Swagger / ReDoc pada endpoint `/docs`.
