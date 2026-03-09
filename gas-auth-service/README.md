# 🔐 GAS Auth Service

**Private Repository** — Powered by **Golden AI Strategy v4**  
Built by **Muhamad RidwanJr** | Full Stack Dev & AI Engineer

> 🛡️ **Layanan Autentikasi Terpusat untuk Ekosistem GAS**  
> Service ini menangani semua operasi terkait autentikasi dan otorisasi pengguna. Menggunakan **Supabase Auth** sebagai backend, dengan tambahan logika bisnis seperti pembuatan profil default di `gas-user-service`.  
> **JWT yang dihasilkan digunakan oleh seluruh service dalam ekosistem.**

---

## 🌟 Gambaran Umum

`gas-auth-service` adalah microservice yang bertanggung jawab atas:

- **Registrasi** pengguna baru (sign-up).
- **Login** pengguna (sign-in) dan penerbitan JWT.
- **Refresh token** untuk memperpanjang sesi.
- **Logout** (invalidasi sesi).
- **Verifikasi token** (untuk service internal).
- **Manajemen sesi** dengan Supabase.

---

## 🏗️ Arsitektur & Peran dalam Ekosistem

Auth Service berada di **VPS 1 (Core Layer)** dan berkomunikasi dengan:

- **Supabase** – sebagai backend auth utama.
- **gas-user-service** – untuk membuat/memperbarui profil user.

---

## ⚙️ Tech Stack

- **Bahasa**: Python 3.11+
- **Framework**: FastAPI
- **Supabase Client**: `supabase-py` (resmi)
- **HTTP Client**: HTTPX (untuk memanggil user-service)
- **Logging**: `structlog` (JSON format)
- **Container**: Docker & Docker Compose

---

## 📁 Struktur Repositori

```
gas-auth-service/
├── src/
│   ├── main.py
│   ├── config.py
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py
│   │   │   └── health.py
│   ├── core/
│   │   ├── supabase_client.py
│   │   └── auth_handler.py
│   ├── services/
│   │   └── user_service_client.py
│   └── utils/
│       └── logger.py
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── README.md
```

---

---

## 🚀 Deployment & Operation (Docker Mode)

Service ini dijalankan menggunakan **Docker Compose** untuk kemudahan manajemen dan isolasi.

### 1. Inisialisasi Network (Shared)
Jika belum ada, buat network agar antar service bisa saling kenal:
```bash
sudo docker network create gas-network || true
```

### 2. Menjalankan Service
```bash
sudo docker compose up -d --build
```
*(Gunakan `docker-compose` jika versi docker Anda lama)*

### 3. Monitoring & Management
- **Cek Status Container**: `sudo docker ps`
- **Lihat Log Service**: `
`
- **Restart Service**: `sudo docker compose restart`
- **Stop Service**: `sudo docker compose stop`
- **Hapus & Bersihkan**: `sudo docker compose down`

---

## 🛠️ Git Workflow (Push & Update)

### Push Pertama Kali (Setup Repo)
```bash
git init
git add .
git commit -m "feat: initial commit for gas-auth-service"
git branch -M main
git remote add origin git@github.com:Muhamadridwanjr/gas-auth-service.git
git push -u origin main
```

### Update Terbaru & Push
```bash
git add .
git commit -m "fix: update logic and documentation"
git push origin main
```

---

## 🌍 Panduan Migrasi

### Migrasi ke VPS Baru
1. **Copy Folder**: Zip folder project atau `git clone` di VPS baru.
2. **Setup Env**: Salin file `.env` (isi dengan kredensial yang sama).
3. **Setup Network**: `sudo docker network create gas-network`.
4. **Docker Start**: Jalankan `sudo docker compose up -d --build`.

### Migrasi ke Cloud (Kubernetes/Managed)
Service ini siap untuk container orchestration seperti GKE atau AWS EKS karena sudah memiliki `Dockerfile` yang standar.

---

## 🔒 Keamanan & API Key
Untuk komunikasi sistem-ke-sistem via Gateway, gunakan:
- **Header**: `X-API-KEY`
- **Value**: Ambil dari `GATEWAY_API_KEY` di `.env`
- **Contoh**: `curl -H "X-API-KEY: your-key" http://localhost:8000/api/auth/v1/health`

---

## 📝 Catatan Pengembang
- Pastikan Port `8001` terbuka di Firewall jika ingin diakses langsung (tidak disarankan, lewat Gateway saja).
- Dokumentasi API tersedia di: `http://<IP_VPS>:8001/docs`
