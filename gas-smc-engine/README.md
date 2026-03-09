# 🔍 GAS SMC Engine (Upgrade: Integrasi PAC, SMC, ICT & Analisis 4 Timeframe)

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Detektor struktur pasar universal yang menggabungkan konsep Price Action Classic (PAC), Smart Money Concepts (SMC), dan Inner Circle Trader (ICT).**  
> Engine ini tidak hanya mendeteksi Order Block, FVG, BOS, CHoCH, tetapi juga memahami anatomi pasar secara utuh: market structure, zona institusional, likuiditas, entry trigger, dan konteks waktu. Dilengkapi dengan analisis 4 Timeframe (4 TF) untuk menghasilkan sinyal berkualitas tinggi sesuai gaya trading (scalping, intraday, swing).

---

## 📋 Daftar Isi

- [Ikhtisar & Filosofi](#ikhtisar--filosofi)
- [Daftar Indikator Universal](#daftar-indikator-universal)
- [Alur Logika 4 Timeframe](#alur-logika-4-timeframe)
- [Alur Kerja Eksekusi Sistem](#alur-kerja-eksekusi-sistem)
- [Arsitektur & Komponen Baru](#arsitektur--komponen-baru)
- [Teknologi](#teknologi)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Konfigurasi](#konfigurasi)
- [API Reference](#api-reference)
- [Pengujian](#pengujian)
- [Pengembangan](#pengembangan)
- [Kontribusi (Tim Internal)](#kontribusi-tim-internal)
- [Lisensi & Hak Cipta](#lisensi--hak-cipta)
- [Tutorial Git & GitHub](#tutorial-git--github)

---

## 🔍 Ikhtisar & Filosofi

PAC, SMC, dan ICT sebenarnya membahas **anatomi harga yang sama**—hanya dengan sudut pandang berbeda. Untuk menciptakan sistem yang koheren, kita menyaring dan mengelompokkan semua istilah ke dalam satu **Daftar Indikator Universal**. Engine ini mampu:

- Mendeteksi struktur pasar (HH/HL, LH/LL, BOS, CHoCH).
- Mengidentifikasi zona institusional (Order Block, FVG, Supply/Demand).
- Menandai area likuiditas dan jebakan (Liquidity Pools, Sweeps, Inducement).
- Memberikan sinyal entry berbasis candle rejection dan OTE Fibonacci.
- Menerapkan filter waktu (Kill Zones, AMD) untuk meningkatkan probabilitas.

Dengan analisis **4 Timeframe (Top-Down)**, engine ini dapat menyesuaikan output untuk berbagai gaya trading: **scalping, intraday, swing**.

---

## 🧠 Daftar Indikator Universal

Alih-alih memanggil PAC, SMC, atau ICT secara terpisah, engine mengelompokkan deteksi ke dalam 5 kategori komputasi:

### A. Market Structure (Arah Tren)
| Istilah | Deskripsi |
|---------|-----------|
| **Swing Points** | Higher High (HH), Higher Low (HL), Lower High (LH), Lower Low (LL). |
| **BOS (Break of Structure)** | Harga menembus struktur searah tren (konfirmasi kelanjutan). |
| **CHoCH (Change of Character)** | Harga menembus ayunan kunci berlawanan arah (sinyal reversal). (Sinonim: MSS) |

### B. Institutional Zones (Area Reaksi / POI)
| Istilah | Deskripsi |
|---------|-----------|
| **SnR Klasik** | Support & Resistance, Zona Supply & Demand (dari PAC). |
| **Order Block (OB)** | Candle terakhir sebelum pergerakan impulsif yang memecah struktur. Biasanya berlawanan arah. |
| **Fair Value Gap (FVG)** | Celah harga kosong pada deret 3 candle, menunjukkan ketidakseimbangan agresif. |

### C. Liquidity & Traps (Area Jebakan)
| Istilah | Deskripsi |
|---------|-----------|
| **Liquidity Pools** | Kumpulan Stop Loss ritel (buy-side di atas resistensi, sell-side di bawah support). |
| **Liquidity Sweep / Stop Hunt** | Harga menembus area likuiditas sejenak lalu berbalik cepat (rejection). |
| **Inducement** | Pullback minor sebelum zona OB/FVG asli, memancing trader masuk terlalu awal. |

### D. Entry Triggers (Pemicu Masuk)
| Istilah | Deskripsi |
|---------|-----------|
| **Candle Rejection** | Pin bar, Engulfing, atau pola candlestick reversal lainnya. |
| **OTE (Optimal Trade Entry)** | Area pullback di rasio Fibonacci 62%–79% dari pergerakan impulsif. |

### E. Time Context (Filter Waktu)
| Istilah | Deskripsi |
|---------|-----------|
| **Kill Zones** | Waktu spesifik sesi London/New York (misal: 09:30–11:00 NY, 03:00–05:00 London). |
| **AMD** | Fase Accumulation (Sideways), Manipulation (Sweep/Stop hunt), Distribution (Tren target). |

---

## 📊 Alur Logika 4 Timeframe (Top-Down Analysis)

Engine menerima data OHLC dari 4 timeframe berbeda secara bersamaan dan menjalankan logika bertingkat:

1. **TF 1 (Macro):** Penentu bias/arah utama.
2. **TF 2 (Narrative):** Pemetaan zona (OB/FVG/SnR).
3. **TF 3 (Setup):** Deteksi manipulasi (Sweep) & perubahan karakter (CHoCH).
4. **TF 4 (Execution):** Pemicu entry presisi.

### Matriks Gaya Trading
| Gaya Trading | TF 1 (Macro) | TF 2 (Narrative) | TF 3 (Setup) | TF 4 (Execution) |
|--------------|---------------|-------------------|--------------|------------------|
| **Swing**    | Weekly (W1)   | Daily (D1)        | 4 Hour (H4)  | 1 Hour (H1) / 15M |
| **Intraday** | Daily (D1)    | 4 Hour (H4)       | 1 Hour (H1)  | 15 Min (M15) / 5M |
| **Scalping** | 4 Hour (H4)   | 1 Hour (H1)       | 15 Min (M15) | 5 Min (M5) / 1M |

---

## 🚀 Instalasi & Menjalankan (SUPER DETAIL)

### Pilihan 1: Menggunakan Python Secara Langsung (Development)

Pastikan Python 3.11+ sudah terinstal di sistem Anda.

1. **Buat Virtual Environment (Wajib untuk Isolasi):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/macOS
   # atau
   venv\Scripts\activate     # Untuk Windows
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Duplikat `.env.example` ke `.env`:**
   ```bash
   cp .env.example .env
   ```

4. **Jalankan Aplikasi:**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Stop Aplikasi:**
   Tekan `Ctrl+C` di terminal tempat aplikasi berjalan.

### Pilihan 2: Menggunakan Docker (Production & Staging)

Sangat disarankan memakai Docker agar portabilitas tinggi (tanpa perlu install Python manual).

1. **Build dan Jalankan Container (RUN):**
   ```bash
   docker-compose up -d --build
   ```
   *Perintah ini akan membuat image Docker berdasarkan `Dockerfile` dan menjalankan container di background (`-d`).*
   Ketik `docker ps` untuk memastikan container `gas-smc-engine` memiliki status **Up (healthy)**.

2. **Melihat Logs:**
   ```bash
   docker-compose logs -f
   ```

3. **Menghentikan Container (STOP):**
   ```bash
   docker-compose stop
   ```

4. **Menghapus Container dan Network (DELETE):**
   ```bash
   docker-compose down
   ```
   *Jika ingin menghapus volume juga, tambahkan parameter `-v`*: `docker-compose down -v`

5. **Restart Container (RESTART):**
   ```bash
   docker-compose restart
   ```
   *atau menghentikan lalu membangun ulang*:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

---

## 🐙 Tutorial Git & GitHub

### 1. Cara Push Project ke GitHub Pertama Kali

Buka terminal dan navigasi ke folder project Anda:
```bash
# Inisialisasi git local repository
git init

# Tambahkan semua file agar masuk staging area
git add .
# Catatan: Kita tidak memakai 'git add README.md' saja, tapi semua file dengan '.'

# Buat commit pertama
git commit -m "first commit"

# Ubah nama branch utama jadi 'main'
git branch -M main

# Hubungkan repository lokal Anda ke repository GitHub secara remote
git remote add origin https://github.com/Muhamadridwanjr/gas-smc-engine.git

# Mulai mendorong (push) kodingan ke origin branch main
git push -u origin main
```

### 2. Cara Commit & Update Project ke GitHub (Bila Ada Perubahan)

Setiap kali Anda mengubah file (menambah kode, mengedit README, dll), jalankan 3 perintah sakti ini:
```bash
# 1. Masukkan semua perubahan ke staging area
git add .

# 2. Beri pesan / keterangan tentang apa yang diubah
git commit -m "update: menambahkan fitur market structure detector"

# 3. Kirim perubahan ke GitHub
git push
```

---

## 🔧 Konfigurasi

Semua konfigurasi dilakukan melalui file `.env`. Anda bisa menggandakan file `.env.example`.

| Variabel                      | Nilai Default        | Deskripsi                                       |
|-------------------------------|----------------------|-------------------------------------------------|
| `APP_PORT`                    | 8000                 | Port dimana aplikasi FastAPI berjalan           |
| `KILL_ZONES`                  | "09:30-11:00,14:00-16:00" | Sesi Kill Zones (format JSON atau string)       |
| `DEFAULT_TRADING_STYLE`       | intraday             | Gaya trading default (scalping/intraday/swing)  |
| `MTF_ENABLED`                 | true                 | Aktifkan analisis multi‑timeframe                |
| `API_GATEWAY_URL`             | "http://gas-gateway-api:8000" | URL Gateway jika butuh callback                 |

---

## 📡 API Reference

Aplikasi ini berjalan di port `8000` di dalam container.

### Endpoint `/health` (GET)
Digunakan oleh Docker untuk memeriksa `healthcheck` dan memastikan status **Up (healthy)**.
```bash
curl http://localhost:8000/health
# Response: {"status":"ok","service":"gas-smc-engine"}
```

### Endpoint `/detect` (POST)
Melakukan analisis struktur pasar 4 TF.
```json
// Request Body
{
  "symbol": "XAUUSD",
  "timeframes": {
    "tf1": "H4",
    "tf2": "H1",
    "tf3": "M15",
    "tf4": "M5"
  },
  "ohlc": { ... },
  "options": {
    "trading_style": "scalping"
  }
}
```

---

## 🔒 Kontribusi (Tim Internal)
Bagi developer internal GoldenAIStrategy, pastikan Anda membuat branch baru saat mengerjakan fitur.
```bash
git checkout -b feature/nama-fitur
```
Dan minta Pull Request ketika sudah selesai.

## 📄 Lisensi & Hak Cipta
Copyright © 2026 GoldenAIStrategy (GAS). All rights reserved.
