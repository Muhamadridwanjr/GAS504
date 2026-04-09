# Terms of Service (TOS) & Privacy Policy
**Golden AI Strategy (GAS)**

Terakhir diperbarui: 6 April 2026

Selamat datang di Golden AI Strategy (GAS). Dokumen ini mengatur perjanjian hukum antara Anda ("Pengguna") dan GAS ("Kami" atau "Layanan"). Dengan menggunakan layanan kami via Telegram Bot, Web, MetaTrader 5 (MT5), TradingView, API Binance, atau platform lainnya, Anda setuju untuk terikat oleh Ketentuan Layanan dan Kebijakan Privasi di bawah ini.

---

## BAGIAN I: KETENTUAN LAYANAN (TERMS OF SERVICE)

### 1. Deskripsi Layanan
GAS menyediakan layanan perangkat lunak *trading intelligence* berbasis Artificial Intelligence (AI) yang mencakup analisa teknikal, analisa fundamental, pelacakan sentimen pasar, manajemen risiko, serta _psychology coaching_. Layanan kami beroperasi sebagai asisten dan alat bantu analisa, **bukan** sebagai manajer investasi.

### 2. Penafian Risiko (Risk Disclaimer) - SANGAT PENTING
*   **Risiko Tinggi:** Trading aset keuangan (Forex, Kripto, Saham, dll) membawa risiko kerugian tingkat tinggi.
*   **Bukan Nasihat Keuangan:** Semua sinyal, skor (Confluence Score), analisis makro, rekomendasi, atau notifikasi dari GAS adalah **sumber informasi dan edukasi semata**. Keputusan untuk mengeksekusi *trade* sepenuhnya merupakan tanggung jawab Anda.
*   **Kinerja Masa Lalu:** Hasil *backtesting* histori yang sukses tidak menjamin hasil serupa di masa depan.
*   **Konektivitas & Sistem:** Kami tidak bertanggung jawab atas kerugian yang disebabkan oleh kendala jaringan, jeda eksekusi API (Binance/MT5), gangguan server Telegram, atau hal-hal teknis di luar kendali kami.

### 3. Penggunaan Platform dan API Key
*   Untuk menggunakan integrasi dengan MT5 dan API Binance, Pengguna harus memberikan API Key dan kredensial yang sah.
*   Pengguna bertanggung jawab penuh atas keamanan kredensial pihak ketiga yang dihubungkan. Pastikan API Key Binance yang Anda berikan **tidak memiliki izin penarikan dana (No Withdrawal Permission)**.

### 4. Pembayaran, Tingkatan (Plan), dan Refund
*   **Sistem Kredit:** Pengoperasian layanan AI spesifik menggunakan kalkulasi poin kredit (misal: 1 cr - 20 cr per eksekusi fungsi).
*   **Plan Tersedia:** Essential, Plus, Premium, Ultimate. Masing-masing memiliki batasan akses model dan besaran bonus XP/Credit.
*   **Pengembalian Dana:** Seluruh pembelian *subscription*, *booster*, atau top-up kredit bersifat final. **Tidak ada pengembalian dana (No Refund)** kecuali jika terdapat kesalahan pemotongan berganda di sistem *billing* kami.

### 5. Penghentian Akses
Kami berhak memblokir atau menghapus akun Anda tanpa kompensasi jika terdeteksi aktivitas:
*   Penyalahgunaan API atau upaya *reverse engineering*.
*   Membagikan akses (Account Sharing) secara tidak sah.
*   Spam atau gangguan server GAS secara sengaja.

---

## BAGIAN II: KEBIJAKAN PRIVASI (PRIVACY POLICY)

Privasi dan keamanan data Anda adalah prioritas utama Golden AI Strategy. 

### 1. Data Apa Saja yang Kami Kumpulkan?
Saat Anda mendaftar dan menggunakan GAS, kami mengumpulkan:
*   **Informasi Profil:** Telegram ID, username, dan pengaturan preferensi bahasa.
*   **Data API Pihak Ketiga:** Kredensial untuk Read/Trade via MetaTrader 5 dan API Binance (Disimpan secara terenkripsi, *non-retrievable* dalam bentuk *plain text*).
*   **Histori Perdagangan (Trade History):** Metadata transaksi seperti entri harga, pair, Stop Loss (SL), Take Profit (TP), profit/loss, yang kami ambil khusus untuk keperluan fitur *AI Trade Journal* dan *Psychology Coach/Mentor Mode*.
*   **Data Interaksi:** Riwayat prompt/perintah komando di bot Telegram untuk tujuan layanan fungsional.

### 2. Bagaimana Kami Menggunakan Data Anda?
*   **Penyediaan Layanan Utama:** Mengeksekusi order via MT5/Binance, menganalisa pola dan profil risiko trading Anda, serta memberi *push notification*.
*   **Personalisasi Output AI:** Kami memproses riwayat loss dan win akun Anda agar AI bisa mendeteksi sindrom "FOMO" atau memberikan peringatan *Drawdown Recovery*.
*   **Peningkatan Model AI:** Logika market akan disimpan di _Vector Database / RAG_ kami sebagai data pembelajaran _Anonymous_ untuk mengasah ketajaman Model Analisis Sentimen (Data pribadi Anda dikupas/dihapus sebelum tahap ini).

### 3. Keamanan Data
*   Kami mengamankan lalu lintas data menggunakan TLS/SSL standar industri. 
*   Kami mengimplementasikan **Defense in Depth**: Gateway API dengan *rate limiting* dan keamanan JWT *(JSON Web Token)* berlapis, sehingga service internal aman dari modifikasi luar.
*   **API KEY tidak akan pernah digunakan selain untuk mengeksekusi order atas perintah Anda sendiri atau algoritma risk-manager yang Anda setujui sebelumnya.**

### 4. Pembagian Data ke Pihak Ketiga
Kami **TIDAK dan TIDAK AKAN PERNAH** menjual data transaksi, sinyal privat, atau histori portofolio Anda kepada layanan analitik pihak ketiga secara terang-terangan.
*   Data perintah mungkin dikirimkan dengan aman melalui API model bahasa AI (seperti ke infrastruktur Vertex AI untuk analisis model Claude Haiku/Sonnet/Opus) untuk diproses, namun model tersebut terikat kebijakan privasi Enterprise dan *tidak* akan melatih data Anda ke AI generik publik.

### 5. Hak Anda atas Data
*   Anda berhak mencabut (*revoke*) koneksi API Binance, MT5 atau broker lain dari sistem kami kapan saja melalui dashboard atau komando di bot.
*   Anda berhak meminta penghapusan permanen atas riwayat akun Telegram Anda dari rekam jejak server GAS dengan menghubungi layanan Support kami.

---

*Halaman dokumen ini mengikat secara sistem ketika Anda mengetikkan `/start`, melakukan integrasi broker, atau membeli Plan GAS apa pun.*
