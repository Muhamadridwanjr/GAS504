# 🧠 GAS Strategy Core

**Bagian dari Ekosistem GAS (Gas Automatic Strategy) – VPS 2 (Engine Layer)**

> **Library inti untuk mengeksekusi aturan strategi trading.**  
> `gas-strategy-core` adalah pustaka internal (bukan service mandiri) yang menggabungkan hasil dari `gas-indicator-engine` dan `gas-smc-engine`, lalu menerapkan aturan strategi untuk menghasilkan sinyal trading mentah (buy/sell/neutral). Library ini dipanggil oleh `gas-engine-orchestrator` dan menjadi otak pengambilan keputusan.
> *Catatan Tambahan*: Repository ini juga dibungkus sebagai service FastAPI minimal agar dapat dikonfigurasi sebagai Docker Container mandiri dengan Healthcheck (untuk memudahkan orkestrasi via `gas-gateway-api`).

---

## 📋 Daftar Isi

- [Ikhtisar](#ikhtisar)
- [Instalasi & Menjalankan (TUTORIAL SUPER DETAIL)](#instalasi--menjalankan-tutorial-super-detail)
  - [Menggunakan Docker (Direkomendasikan)](#menggunakan-docker-direkomendasikan)
  - [Menggunakan Python Murni (Local/Host)](#menggunakan-python-murni-localhost)
- [Panduan Git: Push ke GitHub Pertama Kali](#panduan-git-push-ke-github-pertama-kali)
  - [Cara Commit dan Update Project](#cara-commit-dan-update-project-ke-github)
- [Arsitektur](#arsitektur)
- [Struktur Strategi](#struktur-strategi)
- [API Reference](#api-reference)

---

## 🔍 Ikhtisar

**gas-strategy-core** adalah komponen kunci yang menentukan **kapan** dan **di mana** harus masuk pasar. Library ini menerima:
- Data pasar terkini (OHLC)
- Hasil indikator teknikal dari `gas-indicator-engine`
- Hasil deteksi SMC dari `gas-smc-engine`

Outputnya adalah **sinyal mentah** yang siap diproses lebih lanjut oleh orchestrator.

---

## 🚀 Instalasi & Menjalankan (TUTORIAL SUPER DETAIL)

Service ini dapat berjalan di VPS dengan dua opsi: menggunakan Docker atau Python murni. Kami sangat merekomendasikan **DOCKER** agar mudah dikelola dan saling terkoneksi dengan service lain (status Up/Healthy).

### Menggunakan Docker (Direkomendasikan)

Pastikan Docker dan Docker Compose sudah terinstal di VPS/PC Anda. Container akan bernama `gas-strategy-core` dan berjalan di port `7003` (menyesuaikan, untuk API health check/evaluate).

#### 1. Menjalankan Container (RUN)
Terdapat perintah `docker-compose up -d`. Opsi `-d` berarti *detached* (berjalan di background).
```bash
# Pindah ke direktori project
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core

# Build dan jalankan container di background
docker-compose up --build -d
```
*Gunakan `--build` jika baru pertama kali atau ada perubahan kode (requirement.txt, Dockerfile, dsb).*

Pastikan status container **Up (healthy)**:
```bash
docker ps -a | grep gas-strategy-core
# Output yang diharapkan:
# Up X minutes (healthy)  0.0.0.0:7003->7003/tcp  gas-strategy-core
```

#### 2. Menghentikan Container (STOP)
Jika Anda hanya ingin menjeda/menghentikan container (tanpa menghapus data/image):
```bash
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core
docker-compose stop
```

#### 3. Merestart Container (RESTART)
Jika Anda mengganti file kode (tanpa menamnbah libari pip) atau mengubah file `.env`:
```bash
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core
docker-compose restart
```

#### 4. Menghapus Container (DELETE)
Jika Anda ingin menghapus container seutuhnya (beserta network bawaan compose):
```bash
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core
docker-compose down
```
Untuk menghapus sekalian images yang sudah di-build, tambahkan `--rmi all`:
```bash
docker-compose down --rmi all
```

---

### Menggunakan Python Murni (Local/Host)

Jika hanya ingin tes kodingan tanpa Docker.

#### 1. Membuat Virtual Environment & Instalasi (INSTALL)
```bash
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core

# Pastikan menggunakan Python 3.11+
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependency
pip install -r requirements.txt
# Atau jalankan package library
pip install -e .
```

#### 2. Menjalankan Service (RUN)
```bash
source venv/bin/activate
# Jalankan FastAPI wrapper
uvicorn src.main:app --host 0.0.0.0 --port 7003 --reload
```
Aplikasi bisa diakses di `http://localhost:7003/health` -> (Harus mengembalikan status 200 OK).

#### 3. Menghentikan Service (STOP)
- Tekan `Ctrl + C` pada terminal tempat aplikasi berjalan.

#### 4. Menghapus Environment (DELETE)
```bash
rm -rf venv
```

---

## 🐙 Panduan Git: Push ke GitHub Pertama Kali

Direktori ini seharusnya sudah siap. Untuk pertama kali mengirimnya ke GitHub, ikuti perintah berurutan ini:

```bash
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core

# 1. Inisialisasi Git
git init

# 2. Tambahkan semua file yang akan di commit
git add .
# Atau jika instruksi awal hanya minta README: git add README.md

# 3. Buat commit pertama
git commit -m "first commit"

# 4. Buat dan masuk ke branch utama (main)
git branch -M main

# 5. Hubungkan ke Remote URL git mu
git remote add origin https://github.com/Muhamadridwanjr/gas-strategy-core.git

# 6. Push kode ke GitHub (branch main)
git push -u origin main
```

*(Catatan: Anda mungkin butuh Personal Access Token (PAT) atau SSH key jika diminta password saat git push).*

### Cara Commit dan Update Project ke GitHub

Setiap kali Anda mengubah kode (misal menambah file baru, memperbaiki sistem, update strategi), berikut adalah *workflow* mengupdate GitHub:

```bash
cd /home/mridwan3101/goldenaistrategy/gas-strategy-core

# 1. Cek file apa saja yang diubah
git status

# 2. Tambahkan perubahan ke staging
git add .
# (Atau spesifik: git add file_yang_berubah.py)

# 3. Beri pesan/catatan commit (Gunakan pesan yang jelas!)
git commit -m "Update: menambahkan strategi baru RSI FVG di /strategies"

# 4. Push ke GitHub repository
git push origin main
```

---

## 🏗️ Arsitektur

Library ini tidak hanya berjalan sebagai module Python import-able, tetapi di *containerize* agar gateway API (dan orchestrator) dari ekosistem GAS bisa memastikan koneksi `200 OK` (Health Check). 

---

## ✍️ Struktur Strategi & Menulis Aturan

Strategi didefinisikan dalam YAML di folder `/strategies`. Contoh di `strategies/ict_scalper.yaml`.
Baca konfigurasi lebih lanjut pada contoh `strategies` yang tersedia di direktori kode.

---
**Hak Cipta © 2026 Muhamad RidwanJr dan Tim GAS. Seluruh hak cipta dilindungi undang-undang.**
Semua perubahan bisa di cek dengan test integrasi yang berjalan!
🔥 GAS Strategy – Logika Strategi Cerdas untuk Keputusan Trading Presisi
