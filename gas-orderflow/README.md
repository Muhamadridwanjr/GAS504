# 📊 GAS Order Flow Engine

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Edge Legendary Layer (VPS 5)**  
Service yang menganalisis order flow secara real-time: delta, cumulative delta, imbalance ratio, dan zona likuiditas. Terinspirasi dari konsep smart money dan order flow trading.

📛 **SERVICE NAME**
`gas-orderflow` | API | 9514 | Order Flow & Liquidity | Delta, Imbalance, Liquidity Zone | Tick Data → OrderFlow → Sinyal Tekanan | Active

---

## 🌐 HEALTH CHECK
**Endpoint:** `http://localhost:9514/health`

## 📡 API Reference
### `GET /orderflow/{symbol}/current` – Metrik order flow terkini
### `GET /orderflow/{symbol}/liquidity` – Zona likuiditas
### `POST /orderflow/tick` – Ingest tick data

## 🐳 Docker
```bash
docker-compose up -d --build
docker ps | grep orderflow
docker-compose down
```
