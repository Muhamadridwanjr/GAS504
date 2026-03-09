# 💰 GAS Billing Service

**Private Repository** — Powered by **Golden AI Strategy v4**  
Built by **Muhamad RidwanJr** | Full Stack Dev & AI Engineer

> 💎 **AI SaaS Monetization Engine**  
> Service ini menangani semua aspek monetisasi dalam ekosistem GAS: **plan subscription, quota management, boost system, leveling, usage tracking, dan access control** untuk berbagai platform (Web, Telegram, Discord).  
> **Bukan sekadar billing, ini adalah otak komersial yang mengatur bagaimana pengguna membayar dan menggunakan layanan AI.**

---

## 📋 Daftar Isi

- [🌟 Gambaran Umum](#-gambaran-umum)
- [🏗️ Arsitektur & Peran dalam Ekosistem](#️-arsitektur--peran-dalam-ekosistem)
- [⚙️ Tech Stack](#️-tech-stack)
- [📁 Struktur Repositori](#-struktur-repositori)
- [🔧 Setup & Konfigurasi](#-setup--konfigurasi)
- [🚀 Tutorial Run, Stop, Delete, Restart](#-tutorial-run-stop-delete-restart)
- [🖥️ Cara Push GitHub Pertama Kali](#️-cara-push-github-pertama-kali)
- [🔄 Cara Commit & Update Project](#-cara-commit--update-project)
- [🧠 Core Concepts](#-core-concepts)
- [🗄️ Database Schema](#️-database-schema)
- [🔌 API Endpoints](#-api-endpoints)
- [🛡️ Keamanan](#️-keamanan)
- [🧪 Testing](#-testing)
- [🐳 Deployment](#-deployment)

---

## 🌟 Gambaran Umum

`gas-billing-service` adalah microservice yang mengelola seluruh aspek monetisasi pengguna dalam ekosistem GAS. Service ini bertanggung jawab untuk:
- **Plan Subscription** – Paket berlangganan bulanan (FREE, PREMIUM, ULTIMATE).
- **Quota Management** – Melacak penggunaan kuota per pengguna.
- **Boost System** – Penambahan kuota tambahan dengan masa berlaku 30 hari.
- **Level System** – Level pengguna (STARTER, PRIORITY, MASTER, VIP ELITE).
- **Access Control** – Menentukan akses berdasarkan plan dan level.
- **Usage Tracking** – Mencatat setiap konsumsi analisis.

---

## 🏗️ Arsitektur & Peran dalam Ekosistem

Billing Service berada di **VPS 1 (Core Layer)** dan berkomunikasi dengan:
- **gas-user-service** – Membaca/update data pengguna.
- **gas-gateway-api** – Menerima request dari client.
- **gas-engine** – Memeriksa kuota sebelum analisis.

---

## ⚙️ Tech Stack

- **Bahasa**: Python 3.11+
- **Framework**: FastAPI
- **Database**: PostgreSQL (via Supabase)
- **Container**: Docker & Docker Compose
- **Logging**: `structlog`

---

## 🚀 Tutorial Run, Stop, Delete, Restart

Berikut adalah panduan lengkap cara mengelola service ini menggunakan Python (Local) dan Docker.

### 🐍 Python (Local Development)

| Action | Command | Keterangan |
| :--- | :--- | :--- |
| **RUN** | `uvicorn src.main:app --reload --port 8004` | Menjalankan server dengan auto-reload. |
| **STOP** | `CTRL + C` di terminal | Menghentikan proses uvicorn yang sedang berjalan. |
| **DELETE** | `rm -rf venv` | Menghapus virtual environment jika ingin reset total. |
| **RESTART** | `CTRL + C` lalu jalankan lagi command RUN | Memulai ulang server. |

### 🐳 Docker (Lengkap)

Kami menyediakan **Makefile** untuk mempercepat pekerjaan, tapi berikut adalah perintah aslinya (Native) jika Abang ingin menjalankan satu per satu.

#### 1. Menjalankan Service (RUN)
Membangun image dan menjalankan container di background.
- **Makefile**: `make up`
- **Native**: 
  ```bash
  docker compose up -d --build
  ```

#### 2. Menghentikan Service (STOP)
Menghentikan container tanpa menghapusnya.
- **Makefile**: `make down`
- **Native**: 
  ```bash
  docker compose stop
  ```
> *Catatan: Gunakan `docker compose down` jika ingin menghentikan dan menghapus container sekaligus.*

#### 3. Memulai Ulang (RESTART)
Sangat berguna jika ada perubahan minor di `.env` atau ingin me-refresh proses.
- **Makefile**: `make restart`
- **Native**: 
  ```bash
  docker compose restart
  ```

#### 4. Menghapus Service & Image (DELETE)
Membersihkan container, volume, dan image agar VPS tidak penuh.
- **Makefile**: `make clean`
- **Native**: 
  ```bash
  docker compose down --rmi all --volumes
  ```

#### 5. Cek Status & Logs
- **Status**: `make status` atau `docker compose ps`
- **Logs**: `make logs` atau `docker compose logs -f`

---

## 🖥️ Cara Push GitHub Pertama Kali

Gunakan perintah berikut untuk menginisialisasi repository dan melakukan push pertama ke GitHub.

1. **Inisialisasi Git Lokal**:
   ```bash
   git init
   ```
2. **Tambah Semua File**:
   ```bash
   git add .
   ```
3. **Commit Pertama**:
   ```bash
   git commit -m "feat: initial commit for gas-billing-service"
   ```
4. **Pindah ke Branch Main**:
   ```bash
   git branch -M main
   ```
5. **Tambah Remote Origin**:
   ```bash
   git remote add origin git@github.com:Muhamadridwanjr/gas-billing-service.git
   ```
6. **Push ke GitHub**:
   ```bash
   git push -u origin main
   ```

---

## 🔄 Cara Commit & Update Project

Lakukan langkah ini setiap kali ada perubahan kode:

1. **Lihat Perubahan**:
   ```bash
   git status
   ```
2. **Tambah Perubahan**:
   ```bash
   git add .
   ```
3. **Commit**:
   ```bash
   git commit -m "perbaikan/fitur: deskripsi singkat perubahan"
   ```
4. **Push**:
   ```bash
   git push origin main
   ```

---

## 🧠 Core Concepts (Lebih Lanjut)
*Lihat bagian Core Concepts di atas untuk detail Business Logic (Dual Credit Engine, Level System, dll)*

---

## 🛡️ Keamanan
- **JWT Verification** via Gateway.
- **Internal API Key**: `X-API-Key`.
- **Data Validation**: Pydantic.

---

## 👨💻 Kredit

**Muhamad RidwanJr**  
Full Stack Developer & AI Engineer  
Pencipta **Golden AI Strategy v4**

🔥 **Gaskeun!** 🔥
