🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-quant-backtester	API	9504	Backtesting Hub	Simulasi historis, Sharpe Ratio, Drawdown	Backtest → MarketData → Hasil	Planned																
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

echo "# gas-quant-backtester" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-quant-backtester.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-quant-backtester.git
git branch -M main
git push -u origin main
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
# 📊 GAS Quant Backtester

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Quant Layer (VPS 5)**  
Service yang menyediakan fasilitas **backtesting** untuk strategi kuantitatif dan algoritmik. Dengan menggunakan data historis dari `gas-market-data-processor` (atau sumber lain), service ini menjalankan simulasi strategi, menghitung metrik kinerja seperti Sharpe ratio, drawdown, win rate, dan menghasilkan laporan komprehensif untuk evaluasi strategi sebelum diterapkan secara live.

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

**gas-quant-backtester** adalah engine backtesting yang memungkinkan pengguna (trader, quant analyst, atau sistem otomatis) untuk menguji strategi trading pada data historis. Service ini menerima definisi strategi (dalam format JSON atau referensi ke strategi yang tersimpan), mengambil data OHLCV yang diperlukan, menjalankan simulasi dengan mempertimbangkan biaya transaksi, slippage, dan batasan lainnya, lalu mengembalikan metrik kinerja dan ekuitas curve. Hasil backtest dapat digunakan untuk menyempurnakan strategi sebelum digunakan secara live.

Service ini dirancang untuk:
- Mendukung berbagai jenis strategi: berbasis aturan (rule‑based), sinyal dari engine lain (seperti quant orchestrator), atau strategi kustom.
- Menyediakan analisis mendalam: Sharpe ratio, Sortino, maximum drawdown, profit factor, dan lain‑lain.
- Menyimpan hasil backtest di database untuk referensi dan perbandingan di masa depan.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Input"
        USER[User / Service] -->|definisi strategi| API
        MDP[gas-market-data-processor] -->|data historis| API
    end

    subgraph "gas-quant-backtester"
        API[REST API :9504]
        CORE[Backtest Engine]
        SIM[Simulator]
        METRIC[Metrik Calculator]
        DB[(PostgreSQL)]
    end

    subgraph "Output"
        RES[Hasil Backtest]
    end

    API --> CORE
    CORE --> SIM
    SIM --> METRIC
    METRIC --> DB
    DB --> API
    API --> RES
```

### Komponen Utama
- **REST API** (port 9504) – Menerima permintaan backtest, mengembalikan hasil, dan mengelola daftar backtest.
- **Backtest Engine** – Inti logika: membaca data, menjalankan simulasi berdasarkan aturan strategi.
- **Simulator** – Meniru eksekusi order, mempertimbangkan slippage, komisi, dan batasan modal.
- **Metrik Calculator** – Menghitung berbagai metrik kinerja dari ekuitas curve dan trade list.
- **PostgreSQL** – Menyimpan definisi strategi (jika diinginkan) dan riwayat hasil backtest.

---

## 🔄 Alur Kerja

1. **Pengguna** mengirim permintaan `POST /backtest` dengan payload yang berisi:
   - Parameter strategi (bisa berupa aturan sederhana, atau referensi ke strategi yang tersimpan di database).
   - Simbol, timeframe, rentang waktu.
   - Parameter simulasi (modal awal, biaya transaksi, slippage).
2. Service mengambil data historis dari `gas-market-data-processor` (atau cache internal) untuk periode yang diminta.
3. Backtest engine menjalankan simulasi:
   - Untuk setiap candle (atau tick), evaluasi aturan strategi.
   - Jika ada sinyal, buat order, perhitungkan eksekusi dengan slippage.
   - Update posisi dan ekuitas.
4. Setelah simulasi selesai, kumpulkan semua trade dan ekuitas curve.
5. Hitung metrik kinerja (total return, Sharpe, drawdown, dll).
6. Simpan hasil ke database (jika diminta) dan kembalikan ke pengguna.

**Contoh Request:**
```json
{
  "strategy": {
    "type": "rule_based",
    "rules": [
      {"indicator": "rsi_14", "operator": "<", "value": 30, "action": "BUY"},
      {"indicator": "rsi_14", "operator": ">", "value": 70, "action": "SELL"}
    ],
    "position_size": 0.1,
    "stop_loss": 50,
    "take_profit": 100
  },
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "from_date": "2025-01-01",
  "to_date": "2025-12-31",
  "initial_capital": 10000,
  "commission": 0.001,
  "slippage": 0.0001
}
```

**Contoh Response:**
```json
{
  "backtest_id": "bt_123456",
  "status": "completed",
  "summary": {
    "total_return": 0.1523,
    "annualized_return": 0.18,
    "sharpe_ratio": 1.45,
    "max_drawdown": 0.08,
    "win_rate": 0.55,
    "profit_factor": 1.8,
    "total_trades": 120
  },
  "equity_curve": [
    {"time": 1700000000, "equity": 10000},
    {"time": 1700086400, "equity": 10150},
    ...
  ],
  "trades": [
    {
      "entry_time": 1700000000,
      "exit_time": 1700086400,
      "action": "BUY",
      "entry_price": 2000.5,
      "exit_price": 2020.3,
      "pnl": 19.8,
      "pnl_percent": 0.0099
    }
  ]
}
```

---

## ✨ Fitur Utama

- **Multi‑strategi**: Mendukung strategi berbasis aturan (indikator, harga), strategi yang dihasilkan oleh engine quant lain (dengan mengimpor sinyal), atau strategi kustom dalam bentuk kode (jika diperluas).
- **Parameter fleksibel**: Modal awal, biaya transaksi (fix atau persentase), slippage (persentase atau absolut).
- **Metrik lengkap**: 
  - Kinerja: total return, annualized return, CAGR
  - Risiko: Sharpe ratio, Sortino ratio, max drawdown, drawdown duration
  - Trading: win rate, profit factor, average win/loss, total trades
- **Export hasil**: Equity curve dan daftar trade dalam format JSON (siap untuk visualisasi).
- **Penyimpanan**: Menyimpan backtest di database untuk analisis lebih lanjut atau perbandingan.
- **Integrasi dengan data historis**: Mengambil data dari `gas-market-data-processor` (OHLC) atau dari flat files (Parquet) jika dikonfigurasi.
- **Mode batch**: Dapat menjalankan banyak backtest sekaligus (misal untuk optimasi parameter).

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Komputasi:** `numpy`, `pandas`, `scipy`
- **Database:** PostgreSQL (SQLAlchemy + asyncpg)
- **Market Data Client:** HTTP ke `gas-market-data-processor` atau baca dari flat files (MinIO/S3)
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-quant-backtester/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /backtest
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── backtest_engine.py       # Logika utama backtest
│   │   ├── simulator.py              # Simulasi eksekusi
│   │   ├── metrics.py                # Hitung metrik kinerja
│   │   ├── strategy_parser.py        # Ubah definisi strategi ke fungsi
│   │   └── exceptions.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── market_data_client.py    # Ambil data dari MDP atau flat files
│   │   └── cache.py                 # Cache data historis (opsional)
│   ├── db/
│   │   ├── __init__.py
│   │   ├── database.py
│   │   ├── models.py                # SQLAlchemy models (backtest_results)
│   │   └── repositories/
│   │       └── backtest_repo.py
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
- PostgreSQL (untuk menyimpan hasil backtest)
- `gas-market-data-processor` berjalan (atau akses ke flat files)
- Redis (opsional, untuk caching)

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-quant-backtester.git
   cd gas-quant-backtester
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
   # Isi DATABASE_URL, MARKET_DATA_URL, dll.
   ```

5. Jalankan PostgreSQL dan Redis (jika perlu):
   ```bash
   docker run -d --name postgres -e POSTGRES_PASSWORD=pass -p 5432:5432 postgres:15-alpine
   docker run -d --name redis -p 6379:6379 redis
   ```

6. Buat database:
   ```bash
   createdb -h localhost -U postgres gas_backtest
   ```

7. Jalankan migration (jika menggunakan Alembic):
   ```bash
   alembic upgrade head
   ```

8. Jalankan service:
   ```bash
   uvicorn src.main:app --reload --port 9504
   ```

### Dengan Docker Compose

```yaml
version: '3.8'
services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: gas_backtest
    volumes:
      - pg_data:/var/lib/postgresql/data

  backtester:
    build: .
    ports:
      - "9504:9504"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:pass@postgres:5432/gas_backtest
      - MARKET_DATA_URL=http://gas-market-data-processor:8100
    depends_on:
      - postgres
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
| `PORT` | 9504 | Port REST API |
| `DATABASE_URL` | postgresql+asyncpg://user:pass@localhost:5432/gas_backtest | Koneksi database async |
| `MARKET_DATA_URL` | http://gas-market-data-processor:8100 | URL untuk ambil data historis |
| `MARKET_DATA_API_KEY` | (opsional) | API key jika diperlukan |
| `REDIS_URL` | redis://localhost:6379 | (Opsional) untuk caching |
| `CACHE_TTL` | 3600 | TTL cache data historis (detik) |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

### `POST /backtest` – Menjalankan backtest

**Request Body:**
```json
{
  "strategy": {
    "type": "rule_based",
    "rules": [
      {"indicator": "rsi_14", "operator": "<", "value": 30, "action": "BUY"},
      {"indicator": "rsi_14", "operator": ">", "value": 70, "action": "SELL"}
    ],
    "position_size": 0.1,
    "stop_loss": 50,
    "take_profit": 100
  },
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "from_date": "2025-01-01",
  "to_date": "2025-12-31",
  "initial_capital": 10000,
  "commission": 0.001,          // dalam persen atau fix? bisa ditentukan
  "slippage": 0.0001,
  "save_result": true           // simpan ke database
}
```

**Response:** `202 Accepted` dengan `backtest_id` jika diproses async, atau hasil langsung jika sync (bisa diatur). Untuk sementara kita buat sinkronus dulu.

**Response (sync):** seperti contoh di atas.

### `GET /backtest/{id}` – Mendapatkan hasil backtest yang tersimpan

### `GET /backtest` – Daftar backtest (dengan filter)

### `DELETE /backtest/{id}` – Hapus hasil backtest

### `GET /health` – Health check

---

## 🔗 Integrasi dengan Service Lain

- **`gas-market-data-processor` (8100)** – Menyediakan data OHLC historis.
- **`gas-feature-engine` (9499)** – (Opsional) Untuk menghitung indikator jika strategi membutuhkan fitur.
- **PostgreSQL** – Menyimpan hasil backtest.
- **`gas-quant-orchestrator` (9500)** – Bisa menggunakan backtester untuk menguji strategi sebelum live.
- **`gas-journal-service` (8107)** – (Opsional) Untuk membandingkan hasil backtest dengan trading real.

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Simulasi dengan data dummy.
- Perhitungan metrik.
- Validasi input.
- Database operations.

---

## 👨‍💻 Pengembangan

### Menambahkan Tipe Strategi Baru
- Perbarui `strategy_parser.py` untuk menangani tipe baru.
- Tambahkan logika evaluasi di `backtest_engine.py`.

### Optimasi Parameter
- Buat endpoint `/optimize` yang menerima rentang parameter dan menjalankan banyak backtest secara paralel (menggunakan Celery atau asyncio).

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

**🔥 GAS Quant Backtester – Validasi Strategi Sebelum Terjun ke Pasar Nyata**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  