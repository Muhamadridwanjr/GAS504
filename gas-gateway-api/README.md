# 🚀 GAS Gateway API

**Private Repository** — Powered by **Golden AI Strategy v4**  
Built by **Muhamad RidwanJr** | Full Stack Dev & AI Engineer

> 🔥 **Pintu Gerbang Utama Ekosistem GAS**  
> Gateway ini adalah **single entry point** untuk semua layanan microservices dalam ekosistem GAS (Golden AI Strategy). Menangani routing, autentikasi, rate limiting, logging, dan meneruskan request ke service internal.

---

## 🏗️ Arsitektur

Gateway bertindak sebagai proxy layer transparan yang menangani:
- **Router** – Meneruskan request ke service internal.
- **Security** – Verifikasi JWT (Supabase) & Rate Limiting (Redis).
- **Observability** – Logging terstruktur (JSON).

---

## 🔧 Setup & Konfigurasi

### Prasyarat
- Python 3.11+
- Redis (untuk rate limit)
- Docker & Docker Compose **(Utama/Rekomendasi 🚀)**

**Install Docker Compose (V2 - Pro Solution):**
```bash
sudo apt update && sudo apt install docker-compose-v2 -y
```

> **⚠️ troubleshooting:**
> Jika `docker compose` error (unknown shorthand flag), Anda mungkin butuh versi lama atau install plugin di atas.
> 
> **Kenapa ada 2 perintah?**
> - `docker-compose` (pakai strip): Versi lama (standalone). Sering error `TypeError` di VPS baru.
> - `docker compose` (pakai spasi): Versi baru (plugin). Lebih stabil & modern.

### Instalasi
1. Clone repositori:
   ```bash
   git clone https://github.com/Muhamadridwanjr/gas-gateway-api.git
   cd gas-gateway-api
   ```
2. Setup environment:
   ```bash
   cp .env.example .env
   # Edit .env dengan credentials Anda
   ```

---

## 🚀 Deployment & Operation (Docker Mode)

Gateway ini dijalankan menggunakan **Docker Compose** bersama dengan Redis untuk rate limiting.

### 1. Inisialisasi Network (Shared)
```bash
sudo docker network create gas-network || true
```

### 2. Menjalankan Gateway
```bash
sudo docker compose up -d --build
```

### 3. Monitoring & Management
- **Lihat Status Container**: `sudo docker ps`
- **Lihat Log Gateway**: `sudo docker compose logs -f gas-gateway-api`
- **Lihat Log Redis**: `sudo docker compose logs -f gas-redis`
- **Stop/Matikan**: `sudo docker compose down`

---

**Keamanan (Production API Key):**
Untuk komunikasi sistem-ke-sistem, Gateway ini mewajibkan penggunaan API Key.
- Header: `X-API-KEY: <your-api-key>`
- Key dikonfigurasi di file `.env` pada variabel `GATEWAY_API_KEY`.

**Production Hardening:**
Untuk keamanan lebih, Anda bisa mematikan Swagger UI (`/docs`) di server production:
- Di `.env`, set `ENABLE_DOCS=false`.
- Restart container: `sudo docker compose restart gas-gateway-api`.

**Cleanup (Sangat Penting jika Port Error):**
Jika muncul error `address already in use` (port 8000 atau 6379 terpakai):
1. **Hapus container standalone lama:**
   ```bash
   sudo docker stop gas-gateway-api && sudo docker rm gas-gateway-api
   ```
2. **Matikan Redis lokal (biar Redis Docker bisa jalan):**
   ```bash
   sudo systemctl stop redis-server
   ```
3. **Jalankan ulang dengan Docker Compose:**
   ```bash
   sudo docker compose up -d
   ```

**Cek Log (Sangat Penting):**
Untuk melihat apa yang terjadi di dalam container (error, request masuk, dll):
```bash
# Lihat log spesifik gateway (FastAPI)
sudo docker compose logs -f gas-gateway-api

# Lihat log semua service (Gateway + Redis)
sudo docker compose logs -f
```
Jika Anda ingin melihat log yang benar-benar bersih dari awal (menghapus memori log lama), silakan jalankan:

bash
sudo docker compose restart gas-gateway-api && sudo docker compose logs -f gas-gateway-api

### 2. Mode Development (Local)
Jika ingin running tanpa Docker:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
make dev # atau uvicorn src.main:app --reload
```

---

## 🔄 Update Terbaru & Push ke GitHub

Ikuti langkah ini untuk commit perubahan terbaru dan push ke repository:

1. **Cek Perubahan:**
   ```bash
   git status
   ```
2. **Tambah & Commit:**
   ```bash
   git add .
   git commit -m "update: pembaruan fitur dan migrasi ke docker"
   ```
3. **Push ke GitHub:**
   ```bash
   git push origin main
   ```

---

## 🏗️ Panduan Migrasi (Migration Guide)

### 1. Migrasi ke VPS Baru
Jika Anda pindah server VPS:
1. **Persiapkan Server:** Install Docker & Docker Compose.
2. **Clone & Setup:**
   ```bash
   git clone https://github.com/Muhamadridwanjr/gas-gateway-api.git
   cd gas-gateway-api
   ```
3. **Copy `.env`:** Copy file `.env` dari server lama.
4. **Run:** `sudo docker compose up -d`

### 2. Migrasi ke Cloud (GCP/AWS/Azure)
Gateway ini siap untuk Cloud Native:
- **CI/CD:** Gunakan GitHub Actions di `.github/workflows/deploy.yml` untuk auto-deploy ke **Google Cloud Run**.
- **Serverless:** Sangat cocok di-deploy ke Cloud Run (GCP) atau Fargate (AWS) karena sudah Dockerized.

---

## 🛠️ Testing
Jalankan test suite untuk memastikan semua fungsi berjalan normal:
```bash
pytest tests/
```

---

**© 2026 Golden AI Strategy** | [Muhamad RidwanJr](https://github.com/Muhamadridwanjr)
