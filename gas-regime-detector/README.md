# 🌪️ GAS Regime Detector

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Quant Layer (VPS 5)**  
Service yang bertugas mengidentifikasi **fase pasar (market regime)** secara real‑time. Dengan memanfaatkan fitur dari `gas-feature-engine`, service ini mengklasifikasikan kondisi pasar ke dalam kategori seperti **trending, ranging, high volatility, low volatility**. Hasilnya digunakan oleh `gas-quant-orchestrator` untuk memilih strategi yang paling cocok.

📛 **SERVICE NAME**
`gas-regime-detector` | API | 9503 | Market Regime | Fase Trending/Ranging/High-Vol (ADX, ATR, ML) | Fitur → RegimeDetector → Regime | Active

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Arsitektur](#arsitektur)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [API Reference](#api-reference)

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

---

## ⚙️ Instalasi & Menjalankan

### 🐳 Docker Mode
▶️ **Build & Run**
```bash
docker-compose up -d --build
```
📊 **Check Status**
```bash
docker ps | grep regime-detector
```
⛔ **Stop**
```bash
docker-compose down
```

---

## 🌐 HEALTH CHECK (STATUS 200 OK)

**Endpoint:** `http://localhost:9503/health`
```json
{
  "status": "ok",
  "service": "gas-regime-detector"
}
```

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
    "regime_method": "rule_based"
  }
}
```
