# 👤 GAS User Service
> **Private Repository — Powered by Golden AI Strategy v4**  
> **Built by Muhamad RidwanJr | Full Stack Dev & AI Engineer**

`gas-user-service` adalah microservice yang mengelola profile dan data pengguna dalam ekosistem Golden AI Strategy (GAS). Service ini menangani data di luar autentikasi dasar, seperti subscription tier, preferensi, dan API keys.

---

## 📋 Daftar Isi
1. [🌟 Gambaran Umum](#-gambaran-umum)
2. [🏗️ Arsitektur](#%EF%B8%8F-arsitektur)
3. [⚙️ Tech Stack](#%EF%B8%8F-tech-stack)
4. [🔧 Instalasi & Setup](#-instalasi--setup)
5. [🚀 Tutorial Run, Stop, Delete, Restart (LENGKAP)](#-tutorial-run-stop-delete-restart-lengkap)
    - [Python (Lokal)](#python-lokal)
    - [Docker (Kontainer)](#docker-kontainer)
6. [📦 GitHub Guide (Pertama Kali & Update)](#-github-guide-pertama-kali--update)
7. [🔌 API Endpoints](#-api-endpoints)
8. [🛡️ Keamanan](#%EF%B8%8F-keamanan)

---

## 🌟 Gambaran Umum
Mengelola data profil yang bersifat bisnis spesifik:
- **Profil Dasar**: Nama, Avatar, Email.
- **Subscription Tier**: free, premium, pro.
- **Settings**: Konfigurasi JSONB untuk preferensi user.
- **API Keys**: Manajemen key untuk integrasi pihak ketiga.

---

## 🏗️ Arsitektur
Berkomunikasi dengan:
- `gas-auth-service` (8001)
- `gas-billing-service` (8004)
- `gas-gateway-api` (8000)

---

## ⚙️ Tech Stack
- **Bahasa**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL 15+
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrasi**: Alembic
- **Logging**: Structlog (JSON)

---

## 🔧 Instalasi & Setup

1. **Clone & Masuk Folder**:
   ```bash
   git clone git@github.com:Muhamadridwanjr/gas-user-service.git
   cd gas-user-service
   ```

2. **Environment Variables**:
   Buat file `.env` di root folder:
   ```ini
   APP_NAME=GAS User Service
   DEBUG=true
   PORT=8002
   DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/gas_user_db
   LOG_LEVEL=INFO
   ```

---

## 🚀 Tutorial Run, Stop, Delete, Restart (LENGKAP)

### Python (Lokal)

#### 1. RUN (Menjalankan)
Pastikan Virtual Environment aktif dan dependencies terinstal.
```bash
# Buat & Aktifkan Venv
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Install Deps
pip install -r requirements.txt

# Jalankan Service
uvicorn src.main:app --host 0.0.0.0 --port 8002 --reload
```

#### 2. STOP (Berhenti)
Cukup tekan `CTRL + C` di terminal tempat service berjalan.

#### 3. DELETE (Bersihkan)
Untuk menghapus environment lokal:
```bash
rm -rf venv/
find . -name "__pycache__" -type d -exec rm -rf {} +
```

#### 4. RESTART (Mulai Ulang)
Jika menggunakan `--reload`, service akan restart otomatis setiap kali ada perubahan file. Manual: `CTRL + C` lalu jalankan perintah `uvicorn` kembali.

---

### Docker (Kontainer)

#### 1. RUN (Menjalankan)
Menggunakan Docker Compose adalah cara tercepat:
```bash
# Build dan Jalankan (Background)
docker-compose up -d --build
```
*Cek status:* `docker ps` atau `docker-compose ps`. Pastikan statusnya `Up (healthy)`.

#### 2. STOP (Berhenti)
```bash
# Menghentikan kontainer tanpa menghapus
docker-compose stop
```

#### 3. DELETE (Hapus)
```bash
# Hapus kontainer, network, dan volume (Opsional: -v)
docker-compose down -v
```

#### 4. RESTART (Mulai Ulang)
```bash
# Restart cepat
docker-compose restart

# Restart dengan rebuild (jika ganti kode)
docker-compose up -d --build
```

---

## 📦 GitHub Guide (Pertama Kali & Update)

### Cara Push Pertama Kali
```bash
git init
git add .
git commit -m "feat: initial commit for gas-user-service"
git branch -M main
git remote add origin git@github.com:Muhamadridwanjr/gas-user-service.git
git push -u origin main
```

### Cara Update Project (Commit & Push)
Lakukan ini setiap kali selesai mengubah fitur:
```bash
# 1. Cek file yang berubah
git status

# 2. Tambahkan perubahan
git add .

# 3. Commit dengan pesan yang jelas
git commit -m "update: menambahkan fitur X atau fix bug Y"

# 4. Push ke server
git push origin main
```

---

## 🔌 API Endpoints
- **Health Check**: `GET /health`
- **My Profile**: `GET /api/v1/profiles/me`
- **Internal Create**: `POST /internal/profiles`
- **Internal Tier**: `PUT /internal/profiles/{id}/tier`

---

## 🛡️ Keamanan
- **Internal API Key**: Header `X-API-Key` untuk komunikasi antar service.
- **Gateway Auth**: User ID diambil dari state yang dikirim oleh `gas-gateway-api`.
- **SQL Injection Prevention**: Menggunakan ORM SQLAlchemy.

---
**Muhamad RidwanJr** - *Golden AI Strategy v4*
