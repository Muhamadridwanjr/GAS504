# 🌐 GAS Web Backend

**Private Repository** — Powered by **Golden AI Strategy v4**  
Built by **Muhamad RidwanJr** | Full Stack Dev & AI Engineer

> 💻 **SaaS Dashboard + BFF (Backend for Frontend)**  
> Service ini adalah **jantung pengalaman pengguna** di ekosistem GAS. Bertugas sebagai **aggregator data** untuk dashboard web, landing page, dan profil pengguna.

---

## 📋 Daftar Isi

- [🌟 Gambaran Umum](#-gambaran-umum)
- [🏗️ Arsitektur & Peran dalam Ekosistem](#️-arsitektur--peran-dalam-ekosistem)
- [⚙️ Tech Stack](#️-tech-stack)
- [📖 Tutorial Lengkap: Run, Stop, Delete, Restart](#-tutorial-lengkap-run-stop-delete-restart)
  - [🐍 Di Python (Local Development)](#-di-python-local-development)
  - [🐳 Di Docker (Production / Containerized)](#-di-docker-production--containerized)
- [🐙 Cara Push ke GitHub Pertama Kali](#-cara-push-ke-github-pertama-kali)
- [🔄 Cara Commit Update Project ke GitHub](#-cara-commit-update-project-ke-github)
- [🔧 Setup & Konfigurasi](#-setup--konfigurasi)
- [🧩 Modul & Endpoint API](#-modul--endpoint-api)

---

## 🌟 Gambaran Umum

`gas-web-backend` adalah service **Backend for Frontend (BFF)** yang melayani semua kebutuhan data untuk website GAS. Service ini mengumpulkan data dari service internal dan menyajikannya untuk frontend. Berjalan pada port **8005**.

---

## 🏗️ Arsitektur & Peran dalam Ekosistem

Web Backend (Port 8005) berkomunikasi **secara internal** dengan service lain:
- User Service (8002)
- Billing Service (8004)
- Signal Service (8106)
- Journal Service (8107)
- Notification Service (8112)
- TCG Service (8300)

Semua lalu lintas dari frontend **harus** melalui Gateway API (8000), yang akan meneruskan request ke 8005 beserta header `X-User-ID` bila endpoints memerlukan autentikasi.

---

## ⚙️ Tech Stack

- **Framework**: Python 3.11+ / FastAPI
- **HTTP Client**: `httpx`
- **Container**: Docker & Docker Compose
- **Logging**: `structlog`

---

## 📖 Tutorial Lengkap: Run, Stop, Delete, Restart

### 🐍 Di Python (Local Development)

Pastikan Anda berada di direktori project `gas-web-backend`.

1. **Membuat dan Mengaktifkan Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Untuk Linux/Mac
   # atau
   .\venv\Scripts\activate   # Untuk Windows
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **RUN (Menjalankan server)**:
   ```bash
   # Masuk ke direktori web backend
   cd /home/mridwan3101/goldenaistrategy/gas-web-backend
   # Jalankan menggunakan uvicorn (dengan auto-reload)
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8005
   ```

4. **STOP (Menghentikan server)**:
   - Tekan `Ctrl + C` di terminal tempat server berjalan.

5. **RESTART (Mengulang server)**:
   - Jika menggunakan `--reload`, uvicorn akan otomatis merestart saat file diubah.
   - Jika ingin restart manual, stop server dengan `Ctrl + C`, lalu jalankan kembali perintah RUN.

6. **DELETE (Menghapus environment)**:
   - Hapus folder `venv`.
   ```bash
   rm -rf venv
   ```

### 🐳 Di Docker (Production / Containerized)

Pastikan docker demon sudah berjalan.

1. **RUN (Menjalankan docker via compose)**:
   ```bash
   # Masuk ke direktori web backend
   cd /home/mridwan3101/goldenaistrategy/gas-web-backend
   # Build image dan jalankan container di background (detached)
   docker-compose up -d --build
   ```
   > **Catatan**: Container ID / Nama harus **sama dengan nama project** yaitu `gas-web-backend`. Kita mendefinisikan `container_name: gas-web-backend` di dalam `docker-compose.yml`.

2. **Melihat Status Docker (Memastikan Up & Healthy)**:
   ```bash
   docker ps | grep gas-web-backend
   ```
   *Anda seharusnya melihat `Up X minutes (healthy)`*

3. **STOP (Menghentikan container)**:
   ```bash
   docker-compose stop
   ```

4. **RESTART (Me-restart container)**:
   ```bash
   # Pilihan 1: Jika tidak ada perubahan gambar/image
   docker-compose restart
   
   # Pilihan 2: Jika ada update kodingan dan perlu build lagi
   docker-compose up -d --build
   ```

5. **DELETE (Menghapus container dan network)**:
   ```bash
   # Menghentikan dan menghapus container saja (menghapus resource)
   docker-compose down
   
   # Untuk menghapus image juga (hati-hati, akan download ulang kalau run lagi):
   docker-compose down --rmi all
   ```

---

## 🐙 Cara Push ke GitHub Pertama Kali

Karena repository private untuk `gas-web-backend` sudah dibuat di akun GitHub *Muhamadridwanjr*, berikut cara push **pertama kali**:

1. Pastikan ekstensi Git sudah ter-install di terminal.
2. Buka terminal, masuk ke folder project:
   ```bash
   cd /home/mridwan3101/goldenaistrategy/gas-web-backend
   ```
3. Lakukan inisialisasi Git:
   ```bash
   git init
   ```
4. Tambahkan semua file agar masuk ke pre-commit / staging:
   ```bash
   git add .
   ```
5. Beri keterangan commit pertama:
   ```bash
   git commit -m "feat: initial commit for gas-web-backend"
   ```
6. Ganti branch utama menjadi `main`:
   ```bash
   git branch -M main
   ```
7. Hubungkan ke GitHub repo (Remote Origin):
   ```bash
   git remote add origin git@github.com:Muhamadridwanjr/gas-web-backend.git
   ```
8. **PUSH**:
   ```bash
   git push -u origin main
   ```
*(Note: Jika Anda pernah setup `git remote add origin` sebelumnya, Anda bisa abaikan langkah 7)*

---

## 🔄 Cara Commit Update Project ke GitHub

Setelah Anda membuat perubahan pada kode project (misalkan update API Dashboard), lakukan cara ini untuk mengirim updatenya:

1. Lihat status file apa yang berubah:
   ```bash
   git status
   ```
2. Tambahkan semua perubahan:
   ```bash
   git add .
   ```
3. Beri commit/pesan yang jelas mengenai perubahan tersebut:
   ```bash
   git commit -m "fix: logic API dashboard aggregation"
   ```
4. **Push Update** ke branch default (`main`):
   ```bash
   git push
   ```

---

🔥 **Gaskeun!** 🔥
