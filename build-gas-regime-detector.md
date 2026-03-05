🚀 SERVICE TEMPLATE – @goldenaistrategy
📛 SERVICE NAME
gas-regime-detector	API	9503	Market Regime	Fase Trending/Ranging/High-Vol (ADX, ATR, ML)	Fitur → RegimeDetector → Regime	Planned																														
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

echo "# gas-regime-detector" >> README.md
git init
git add README.md
git commit -m "first commit"
git branch -M main
git remote add origin https://github.com/Muhamadridwanjr/gas-regime-detector.git
git push -u origin main
…or push an existing repository from the command line
git remote add origin https://github.com/Muhamadridwanjr/gas-regime-detector.git
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
# 🌪️ GAS Regime Detector

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Quant Layer (VPS 5)**  
Service yang bertugas mengidentifikasi **fase pasar (market regime)** secara real‑time. Dengan memanfaatkan fitur dari `gas-feature-engine`, service ini mengklasifikasikan kondisi pasar ke dalam kategori seperti **trending, ranging, high volatility, low volatility**, dan lain‑lain. Hasilnya digunakan oleh `gas-quant-orchestrator` untuk memilih strategi yang paling cocok (misal: trend following saat trending, mean reversion saat ranging).

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

**gas-regime-detector** menerima fitur numerik (returns, volatilitas, ADX, dll.) dari `gas-feature-engine` dan mengembalikan label regime beserta probabilitas/keyakinan. Penentuan regime dapat dilakukan dengan dua pendekatan:

1. **Rule‑based (sederhana):** Menggunakan ambang batas (threshold) pada indikator seperti ADX, ATR, atau rolling volatility.
2. **Machine Learning (lanjutan):** Model klasifikasi (misal Random Forest, GMM) yang dilatih pada data historis.

Dengan mengetahui regime, sistem dapat mengoptimalkan pemilihan strategi dan parameter risiko.

---

## 🏗️ Arsitektur

```mermaid
graph TD
    subgraph "Input"
        FE[gas-feature-engine] -->|fitur| API
    end

    subgraph "gas-regime-detector"
        API[REST API :9503]
        CORE[Regime Classifier]
        MODELS[Model Storage (ML)]
        CACHE[(Redis Cache)]
    end

    subgraph "Output"
        QO[gas-quant-orchestrator]
    end

    API --> CORE
    CORE -->|rule-based| CACHE
    CORE -->|ML| MODELS
    CACHE --> API
    API -->|regime| QO
```

### Komponen Utama
- **REST API** (port 9503) – Menerima permintaan deteksi regime.
- **Regime Classifier** – Inti logika: bisa rule‑based atau ML.
- **Model Storage** – Untuk menyimpan model ML yang sudah dilatih (file pickle atau database).
- **Redis Cache** – Menyimpan hasil regime untuk periode tertentu agar tidak perlu hitung ulang.

---

## 🔄 Alur Kerja

1. **Konsumen** (misal `gas-quant-orchestrator`) mengirim request `POST /regime` dengan data fitur untuk satu atau lebih simbol.
2. Service memeriksa cache berdasarkan `{simbol}:{timeframe}:regime`. Jika ada dan belum expired, kembalikan hasil cache.
3. Jika tidak ada, classifier menghitung regime:
   - **Jika mode rule‑based:** gunakan aturan sederhana pada fitur yang tersedia (ADX, ATR, volatilitas).
   - **Jika mode ML:** muat model yang sesuai, lakukan prediksi pada fitur.
4. Simpan hasil ke cache dengan TTL (misal 1 menit).
5. Kembalikan respons JSON berisi regime, confidence, dan metadata.

**Contoh Request:**
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "features": {
    "adx_14": 28.5,
    "atr_14": 0.35,
    "volatility_20": 0.0012,
    "rsi_14": 55.0
  }
}
```

**Contoh Response:**
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "regime": "TRENDING",
  "confidence": 0.85,
  "details": {
    "adx": 28.5,
    "volatility_percentile": 0.7
  }
}
```

---

## ✨ Fitur Utama

- **Multi‑regime detection**: Dapat mendefinisikan berbagai regime (TRENDING, RANGING, HIGH_VOL, LOW_VOL, BREAKOUT, dll).
- **Rule‑based & ML modes**: Fleksibel untuk berbagai tingkat kompleksitas.
- **Confidence score**: Menyertakan tingkat keyakinan.
- **Caching**: Mengurangi beban komputasi untuk permintaan berulang.
- **Multi‑timeframe**: Dapat beroperasi pada berbagai kerangka waktu.
- **Extensible**: Mudah menambah metode baru.

### Contoh Aturan Rule‑based Sederhana
```python
def detect_regime(features):
    adx = features.get('adx_14', 0)
    volatility = features.get('volatility_20', 0)
    if adx > 25:
        return "TRENDING", 0.7 + (adx-25)/100
    elif adx < 20:
        return "RANGING", 0.6
    else:
        return "TRANSITION", 0.5
```

### Machine Learning Approach
- Kumpulkan data historis dengan label regime (bisa dibuat otomatis dengan aturan sederhana atau manual).
- Latih model klasifikasi (Random Forest, SVM, atau GMM untuk unsupervised).
- Simpan model, load saat service start.

---

## 🛠️ Teknologi

- **Bahasa:** Python 3.11+
- **Web Framework:** FastAPI (REST)
- **Komputasi:** `numpy`, `pandas`, `scikit-learn` (jika ML)
- **Cache:** Redis (`redis.asyncio`)
- **Model Storage:** File lokal (`joblib`) atau database
- **Container:** Docker, Docker Compose

---

## 📁 Struktur Direktori

```
gas-regime-detector/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py                # Endpoint /regime
│   │   └── models.py                # Pydantic models
│   ├── core/
│   │   ├── __init__.py
│   │   ├── classifier.py            # Logika deteksi regime
│   │   ├── rule_based.py            # Aturan sederhana
│   │   ├── ml_model.py              # Interface model ML
│   │   └── exceptions.py
│   ├── cache/
│   │   ├── __init__.py
│   │   └── redis_cache.py
│   ├── lib/
│   │   ├── logger.py
│   │   └── utils.py
│   └── models/                        # Folder untuk menyimpan model ML
│       └── regime_model.pkl
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
- Redis server
- `gas-feature-engine` berjalan (sebagai penyedia fitur)

### Langkah Cepat (Development)

1. Clone repositori (internal):
   ```bash
   git clone https://github.com/gasstrategy/gas-regime-detector.git
   cd gas-regime-detector
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
   # Isi REDIS_URL, pilih metode, dll.
   ```

5. Jalankan Redis (jika belum):
   ```bash
   docker run -d -p 6379:6379 redis
   ```

6. Jalankan service:
   ```bash
   uvicorn src.main:app --reload --port 9503
   ```

### Dengan Docker Compose

```yaml
version: '3.8'
services:
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"

  regime-detector:
    build: .
    ports:
      - "9503:9503"
    environment:
      - REDIS_URL=redis://redis:6379
      - REGIME_METHOD=rule_based   # atau ml
    depends_on:
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
| `PORT` | 9503 | Port REST API |
| `REDIS_URL` | redis://localhost:6379 | Koneksi Redis untuk cache |
| `REGIME_METHOD` | rule_based | Metode: `rule_based` atau `ml` |
| `MODEL_PATH` | ./models/regime_model.pkl | Path ke model ML (jika method=ml) |
| `CACHE_TTL` | 60 | TTL cache dalam detik |
| `LOG_LEVEL` | INFO | Level logging |
| `ENVIRONMENT` | development | production/staging/development |

---

## 📡 API Reference

### `POST /regime` – Deteksi regime untuk satu simbol

**Request Body:**
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "features": {
    "adx_14": 28.5,
    "atr_14": 0.35,
    "volatility_20": 0.0012,
    "rsi_14": 55.0
  }
}
```

**Response:**
```json
{
  "symbol": "XAUUSD",
  "timeframe": "H1",
  "regime": "TRENDING",
  "confidence": 0.85,
  "details": {
    "adx": 28.5,
    "volatility_percentile": 0.7
  }
}
```

### `POST /regime/batch` – Untuk banyak simbol
Request: array of objects seperti di atas. Response: array dengan hasil masing‑masing.

### `GET /health` – Health check
```json
{"status": "ok"}
```

---

## 🔗 Integrasi dengan Service Lain

- **`gas-feature-engine` (9499)** – Menyediakan fitur yang dibutuhkan.
- **`gas-quant-orchestrator` (9500)** – Konsumen utama hasil regime.
- **Redis** – Cache hasil regime.

---

## 🧪 Pengujian

```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Unit test mencakup:
- Logika rule‑based.
- Mock model ML.
- Cache hit/miss.
- Validasi input.

---

## 👨‍💻 Pengembangan

### Menambah Metode Deteksi Baru
1. Buat fungsi di `core/classifier.py` atau file terpisah.
2. Daftarkan metode di `classifier.py` dengan menambah ke dictionary `methods`.
3. Sesuaikan konfigurasi jika perlu.

### Contoh Metode ML
```python
# core/ml_model.py
import joblib
class MLRegimeDetector:
    def __init__(self, model_path):
        self.model = joblib.load(model_path)

    def predict(self, features):
        # features harus berupa array 2D
        pred = self.model.predict(features)[0]
        proba = self.model.predict_proba(features)[0].max()
        return pred, proba
```

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

**🔥 GAS Regime Detector – Mengetahui Fase Pasar untuk Strategi Optimal**
✅ FINAL CHECKLIST
[ ] Container name sesuai project  
[ ] Status container: Up (healthy)  
[ ] Endpoint mengembalikan 200 OK  
[ ] Tidak ada error pada logs  
[ ] Terintegrasi dengan GAS Gateway API  
[ ] Antar service dapat saling berkomunikasi  