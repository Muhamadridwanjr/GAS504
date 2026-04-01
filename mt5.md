Bro, gue mappingin **3 opsi konkret** buat jalanin MT5 di serverless VNC yang selalu update. Ini berdasarkan riset dari beberapa repo yang aktif di GitHub dan pengalaman pengguna .

---

## 🗺️ **3 Opsi Utama MT5 Docker + VNC + Auto Update**

| **Opsi** | **Image/Repo** | **Cara Update MT5** | **API Support** | **Ukuran Image** | **Kelebihan** | **Kekurangan** |
|---------|----------------|---------------------|-----------------|------------------|---------------|----------------|
| **1. Wine-Based (Stabil)** | `jsfrnc/mt5-docker-api`  atau `gmag11/metatrader5_vnc`  | **Auto-update** saat pertama run & via Wine  | ✅ REST API + Swagger + WebSocket + Python mt5linux | ~600 MB (v1.0) – 4 GB (v2.0)  | • Paling ringan<br>• Web VNC port 3000 langsung<br>• Banyak dipakai komunitas | • Wine kadang bermasalah di Wine 10.4+ <br>• ARM tidak support |
| **2. Full Windows VM (KVM)** | `psyb0t/mt5-httpapi`  | **Auto-update via Windows Update** (karena Windows asli) | ✅ REST API lengkap (order, history, positions) | ~20 GB (Windows 11 tiny11) | • **Real Windows** → 100% kompatibel<br>• Bisa multiple broker/akun<br>• Stabil untuk production | • Berat (min 5 GB RAM + swap)<br>• Startup lama (~10 menit) |
| **3. Wine + RPYC** | `fortesenselabs/metatrader5-terminal`  | **Manual** (perlu rebuild image) | ✅ RPYC API + VNC | ~1.6 GB | • Support RPYC untuk remote call<br>• Ada `easy-novnc` | • **Update versi terakhir 1 tahun lalu** <br>• Perlu reverse proxy buat VNC |

---

## 🔧 **Cara Kerja Auto-Update di Tiap Opsi**

### **1. Wine-Based (gmag11/jsfrnc)**

Dari dokumentasi , mereka pake trik ini:

```dockerfile
# Entrypoint script otomatis download installer terbaru
wget https://download.mql5.com/cdn/web/metaquotes.software.corp/mt5/mt5setup.exe
wine mt5setup.exe /auto
```

**Penjelasan**: Setiap container restart, dia bakal cek dan download installer terbaru dari MetaQuotes. Jadi **MT5 version selalu latest**, independent dari image .

### **2. Full Windows VM**

Ini pake `dockurr/windows` yang jalanin Windows 11 via KVM . Update jalan **persis kayak di Windows asli**:
- Windows Update jalan di background
- MT5 auto-update lewat installer-nya
- Tapi ukuran gila: **20 GB+**

### **3. Wine + RPYC**

Yang ini agak males, karena terakhir update **1 tahun lalu** . Lo harus rebuild image sendiri kalo mau versi terbaru.

---

## 🚀 **Rekomendasi Buat GAS**

| **Kebutuhan** | **Pilihan Terbaik** | **Alasan** |
|--------------|---------------------|------------|
| **Testing / Development** | `gmag11/metatrader5_vnc:1.0` | Ringan (600 MB), auto-update, web VNC   |
| **Production / Multi‑Account** | `psyb0t/mt5-httpapi`  | Real Windows, REST API lengkap, bisa jalanin 10+ terminal  |
| **Butuh Python API doang** | `jsfrnc/mt5-docker-api`  | REST API + WebSocket + mt5linux, dokumentasi jelas |

### **Command Cepat Buat Testing**

```bash
# Opsi 1: gmag11 (paling simple)
docker run -d \
  --name mt5-exness \
  -p 3000:3000 \
  -p 8001:8001 \
  -v mt5_data:/config \
  -e CUSTOM_USER=gas \
  -e PASSWORD=gas123 \
  gmag11/metatrader5_vnc:latest

# Akses VNC: http://IP_VPS:3000
# Python API: port 8001 pake mt5linux
```

**PENTING**: Image versi 2.0 gede (4 GB) tapi udah include Python environment. Versi 1.0 lebih kecil, cocok buat lo yang cuma butuh VNC buat setting EA .

---

## 💡 **Kesimpulan untuk GAS**

1. **Untuk Exness (sekarang)**: Pake `gmag11/metatrader5_vnc` karena ringan, auto-update, dan udah terbukti .
2. **Nanti kalo tambah Binance**: Lo bisa jalanin **2 container terpisah**:
   - Container 1: MT5 Exness (Wine)
   - Container 2: Binance adapter (native Python)
3. **Kalo butuh banyak broker sekaligus**: Migrasi ke `mt5-httpapi`  yang support multi‑terminal.

Lo udah di jalur yang bener, bro. **Auto-update-nya jalan otomatis**, gak perlu khawatir versi ketinggalan. Yang penting lo mount volume `/config` biar data login persist .

Ada yang mau didiskusiin lebih lanjut? 🔥