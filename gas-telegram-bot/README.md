# 🤖 GAS Telegram Bot

**Private Repository** — Powered by **Golden AI Strategy v4**  
Built by **Muhamad RidwanJr** | Full Stack Dev & AI Engineer

> 💎 **Control Panel Trading di Genggaman Anda**  
> Bot Telegram ini adalah antarmuka utama pengguna untuk berinteraksi dengan ekosistem GAS. Mulai dari analisis pasar, manajemen langganan, hingga eksekusi trading — semuanya dalam satu chat.

---

## 📋 Daftar Isi

- [🌟 Gambaran Umum](#-gambaran-umum)
- [🏗️ Arsitektur & Peran dalam Ekosistem](#️-arsitektur--peran-dalam-ekosistem)
- [⚙️ Tech Stack](#️-tech-stack)
- [📁 Struktur Repositori](#-struktur-repositori)
- [🔧 Setup & Konfigurasi](#-setup--konfigurasi)
- [🚀 Panduan Operasional (RUN, STOP, DELETE, RESTART)](#-panduan-operasional)
- [🛠️ Tutorial GitHub](#️-tutorial-github)
- [🧠 Fitur & Alur Lengkap](#-fitur--alur-lengkap)
- [📊 Monitoring & Logging](#-monitoring--logging)
- [🧪 Testing](#-testing)
- [🐳 Deployment](#-deployment)
- [📄 Lisensi](#-lisensi)

---

## 🌟 Gambaran Umum

`gas-telegram-bot` adalah **lapisan interaksi pengguna** dalam ekosistem GAS. Melalui bot ini, pengguna dapat menjalankan analisis teknikal & fundamental dengan AI, menerima sinyal trading, mengelola langganan, dan melakukan eksekusi trading terintegrasi dengan MT5.

---

## 🔧 Setup & Konfigurasi

### Prasyarat
- Python 3.11+
- Docker & Docker Compose
- Token Bot Telegram dari [@BotFather](https://t.me/botfather)

### Instalasi Lokal
1. **Clone & Masuk ke Folder:**
   ```bash
   git clone git@github.com:Muhamadridwanjr/gas-telegram-bot.git
   cd gas-telegram-bot
   ```
2. **Virtual Environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate  # Windows
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables:**
   ```bash
   cp .env.example .env
   # Edit .env dan masukkan token bot Anda
   ```

---

## 🚀 Panduan Operasional

### 🐍 Menggunakan Python (Lokal)
| Aksi | Perintah |
| :--- | :--- |
| **RUN** | `python src/main.py` |
| **STOP** | Tekan `CTRL + C` di terminal |
| **RESTART** | Hentikan dengan `CTRL + C`, lalu jalankan `python src/main.py` lagi |
| **DELETE** | Untuk menghapus environment: `rm -rf venv/` |

### 🐳 Menggunakan Docker (Rekomendasi)
| Aksi | Perintah |
| :--- | :--- |
| **RUN** | `docker-compose up -d --build` |
| **STOP** | `docker-compose stop` |
| **START** | `docker-compose start` |
| **RESTART** | `docker-compose restart` |
| **DELETE** | `docker-compose down` (Hapus kontainer & network) |
| **DELETE ALL** | `docker-compose down --rmi all` (Hapus kontainer, network, & image) |
| **LOGS** | `docker-compose logs -f` |

---

## 🛠️ Tutorial GitHub

### 1. Cara Push Pertama Kali
Jika Anda baru saja menginisialisasi folder project:
```bash
git init
git add .
git commit -m "first commit: Initial project structure and keyboards"
git branch -M main
git remote add origin git@github.com:Muhamadridwanjr/gas-telegram-bot.git
git push -u origin main
```

### 2. Cara Update Project ke GitHub
Lakukan ini setiap ada perubahan kode:
```bash
git add .
git commit -m "update: Deskripsi perubahan Anda"
git push origin main
```

---

## 🏗️ Arsitektur & Struktur
Bot ini berjalan di port **8003** dan berkomunikasi dengan **gas-gateway-api** di port **8000**.

### Struktur Repositori
```
gas-telegram-bot/
├── src/
│   ├── main.py                 # Entry point bot
│   ├── config.py                # Konfigurasi Pydantic
│   ├── bot/
│   │   └── handlers.py          # Registrasi handler
│   ├── keyboards/                # Semua keyboard (SOP v4)
│   ├── services/
│   │   └── gateway_client.py     # Client ke Gateway API
│   └── utils/
│       └── logger.py            # Structured JSON Logging
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---

## 🔒 Security & Quality
- **Non-root user** di Docker untuk keamanan maksimal.
- **Healthcheck** otomatis untuk memastikan status `Up (healthy)`.
- **JSON Logging** untuk debug presisi dan mendalam.
- **Security Headers** & Isolation via Docker Network.

---

> 👨‍💻 Built by **Muhamad RidwanJr** | **Golden AI Strategy**
