# 📈 GAS Trend Engine

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Edge Legendary Layer (VPS 5)**  
Service yang terinspirasi dari **Richard Dennis** dan eksperimen **Turtle Traders**. Menghasilkan sinyal trading berdasarkan **breakout** dan **MA cross**.

📛 **SERVICE NAME**
`gas-trend-engine` | API | 9513 | Trend Following (Richard Dennis) | Breakout & MA Cross | Fitur → TrendEngine → Sinyal | Active

---

## 🌐 HEALTH CHECK
**Endpoint:** `http://localhost:9513/health`

## 📡 API Reference
### `POST /trend` – Sinyal trend following
### `POST /trend/batch` – Batch sinyal

## 🐳 Docker
```bash
docker-compose up -d --build
docker ps | grep trend-engine
docker-compose down
```
