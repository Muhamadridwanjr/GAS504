# 🔗 GAS Correlation Engine

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – Edge Legendary Layer (VPS 5)**  
Service yang terinspirasi dari **Ray Dalio** dan pendekatan **All Weather Portfolio**. Menghitung rolling correlation antar aset dan memberikan bias (bullish/bearish) berdasarkan pergerakan aset berkorelasi.

📛 **SERVICE NAME**
`gas-correlation` | API | 9512 | Cross-Asset Correlation (Dalio) | Rolling correlation & intermarket bias | Multi-simbol → Correlation → Bias | Active

---

## 🌐 HEALTH CHECK
**Endpoint:** `http://localhost:9512/health`

## 📡 API Reference

### `GET /correlation/matrix` – Matriks korelasi
### `GET /correlation/pair?symbol1=X&symbol2=Y` – Korelasi pair
### `POST /bias` – Bias suatu aset berdasarkan korelasi

## 🐳 Docker
```bash
docker-compose up -d --build
docker ps | grep correlation
docker-compose down
```
