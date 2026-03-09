# 🗄️ GAS Vector Database Service

**Bagian dari Ekosistem GAS – AI Layer (VPS 3)**  
Service terpusat untuk menyimpan embedding dan melakukan similarity search.  
Menggunakan Chroma sebagai backend dan menyediakan REST API yang digunakan oleh seluruh komponen RAG.

---

## 📋 Daftar Isi

- [Ringkasan](#ringkasan)
- [Arsitektur](#arsitektur)
- [Teknologi](#teknologi)
- [Prasyarat](#prasyarat)
- [Struktur Direktori](#struktur-direktori)
- [Instalasi & Menjalankan](#instalasi--menjalankan)
- [Konfigurasi](#konfigurasi)
- [API Reference](#api-reference)
- [Integrasi dengan Service Lain](#integrasi-dengan-service-lain)
- [Pengembangan](#pengembangan)
- [Pengujian](#pengujian)
- [Lisensi](#lisensi)

---

## 🔍 Ringkasan

**gas-vector-db** adalah service yang membungkus ChromaDB (vector database) dengan REST API yang terstruktur. Tugasnya:

- Menyimpan embedding dari dokumen (analisis teknikal, berita makro, kalender ekonomi, dll) beserta metadata.
- Menyediakan endpoint untuk query similarity, sehingga RAG services dapat mengambil konteks yang relevan.
- Mendukung banyak koleksi (misal `technical_analysis`, `macro_news`, `economic_calendar`) dalam satu backend.

Service ini **tidak menyimpan data sendiri**, melainkan bergantung pada container Chroma yang sudah ada (`gas-rag-technical-chroma`). Dengan demikian, resource lebih efisien dan semua data vektor tersimpan terpusat.

---

## 🏗️ Arsitektur

```
┌─────────────────────────────────────────────────────┐
│                     Docker Network                  │
│  ┌─────────────────┐      ┌─────────────────────┐   │
│  │  gas-rag-       │      │  gas-rag-macro      │   │
│  │  technical      │      │  (port 9002)        │   │
│  │  (port 9001)    │      └──────────┬──────────┘   │
│  └────────┬────────┘                  │             │
│           │                           │             │
│           └──────────┬────────────────┘             │
│                      │                                │
│                      ▼                                │
│  ┌─────────────────────────────────────┐            │
│  │      gas-vector-db (port 9004)      │            │
│  │  ┌─────────────────────────────┐   │            │
│  │  │   FastAPI REST Server       │   │            │
│  │  └─────────────┬───────────────┘   │            │
│  │                │                    │            │
│  │                ▼                    │            │
│  │  ┌─────────────────────────────┐   │            │
│  │  │   Chroma HTTP Client        │   │            │
│  │  └─────────────┬───────────────┘   │            │
│  └────────────────┼────────────────────┘            │
│                   │                                 │
│                   ▼                                 │
│  ┌─────────────────────────────────────┐            │
│  │  gas-rag-technical-chroma           │            │
│  │  (ChromaDB container, port 8000)    │            │
│  └─────────────────────────────────────┘            │
└─────────────────────────────────────────────────────┘
```

- **ChromaDB** berjalan dalam container `gas-rag-technical-chroma` (image `chromadb/chroma`), terekspos di port `8000` secara internal.
- **gas-vector-db** berkomunikasi dengan Chroma melalui Docker network (menggunakan nama container).
- **RAG Services** dan **Ingestor** hanya berbicara dengan `gas-vector-db` via REST.

---

## 🛠️ Teknologi

- **Python 3.11**
- **FastAPI** – REST API framework
- **ChromaDB** – Vector database (client `chromadb`)
- **Pydantic** – Validasi data
- **Uvicorn** – ASGI server
- **Docker** – Containerization

---

## 📦 Prasyarat

- Docker & Docker Compose (versi terbaru)
- Container Chroma sudah berjalan dengan nama `gas-rag-technical-chroma` (atau Anda dapat menjalankannya ulang sesuai petunjuk)
- Network Docker `gas-network` (jika belum ada, akan dibuat otomatis atau bisa menggunakan default)

> **Catatan:** Jika container Chroma belum terhubung ke `gas-network`, Anda harus menghubungkannya atau restart ulang dengan compose yang terintegrasi (lihat bagian instalasi).

---

## 📁 Struktur Direktori

```
gas-vector-db/
├── src/
│   ├── __init__.py
│   ├── main.py                     # Entry point FastAPI
│   ├── config.py                    # Pydantic settings
│   ├── core/
│   │   ├── __init__.py
│   │   ├── vector_store.py          # Chroma client wrapper
│   │   └── exceptions.py             # Custom exceptions
│   ├── api/
│   │   ├── __init__.py
│   │   ├── dependencies.py           # FastAPI dependencies (get_store)
│   │   ├── models.py                 # Pydantic models
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── collections.py        # Manajemen koleksi
│   │       ├── documents.py           # Upsert dokumen
│   │       └── query.py               # Query similarity
│   └── lib/
│       ├── __init__.py
│       ├── logger.py                  # Logging konfigurasi
│       └── utils.py                    # Helper functions
├── .env.example
├── requirements.txt
├── Dockerfile
├── docker-compose.yml                 # Untuk menjalankan service saja
└── README.md                           # Dokumentasi ini
```

### Penjelasan File Penting

| File | Deskripsi |
|------|-----------|
| `src/main.py` | Inisialisasi FastAPI, startup event untuk koneksi Chroma, dan include router. |
| `src/config.py` | Membaca environment variables menggunakan `pydantic-settings`. |
| `src/core/vector_store.py` | Kelas `VectorStore` yang membungkus operasi Chroma (list collections, upsert, query). |
| `src/api/models.py` | Pydantic model untuk request/response (CollectionCreate, DocumentUpsert, QueryRequest, dll). |
| `src/api/routes/collections.py` | Endpoint untuk manajemen koleksi. |
| `src/api/routes/documents.py` | Endpoint untuk upsert dokumen. |
| `src/api/routes/query.py` | Endpoint untuk similarity search. |
| `src/api/dependencies.py` | Dependency `get_store` untuk menyuntikkan instance `VectorStore` ke router. |
| `src/lib/logger.py` | Konfigurasi logging dengan `logging`. |
| `src/lib/utils.py` | Fungsi bantu (misal konversi waktu, dll). |
| `requirements.txt` | Daftar dependensi Python. |
| `Dockerfile` | Untuk membangun image `gas-vector-db`. |
| `docker-compose.yml` | Menjalankan service bersama Chroma (opsional). |

---

## ⚙️ Instalasi & Menjalankan

### Opsi 1: Menggunakan Container Chroma yang Sudah Ada

Jika container `gas-rag-technical-chroma` sudah berjalan dan Anda ingin `gas-vector-db` terhubung ke sana:

1. **Pastikan network `gas-network` ada** (atau buat):
   ```bash
   docker network create gas-network
   ```

2. **Hubungkan container Chroma ke network tersebut** (jika belum):
   ```bash
   docker network connect gas-network gas-rag-technical-chroma
   ```

3. **Buat file `docker-compose.yml`** untuk `gas-vector-db` (terpisah):
   ```yaml
   version: '3.8'

   services:
     vector-db:
       build: .
       container_name: gas-vector-db
       ports:
         - "9004:9004"
       environment:
         - PORT=9004
         - CHROMA_HOST=gas-rag-technical-chroma
         - CHROMA_PORT=8000
         - DEFAULT_DIMENSION=1536
       networks:
         - gas-network
       restart: unless-stopped

   networks:
     gas-network:
       external: true
   ```

4. **Jalankan**:
   ```bash
   docker-compose up -d
   ```

### Opsi 2: Menjalankan Stack Lengkap (Chroma + vector-db) dari Awal

Jika Anda ingin memulai dari awal dan tidak menggunakan container Chroma yang sudah ada, buat file `docker-compose.yml` yang mencakup kedua service:

```yaml
version: '3.8'

services:
  chroma:
    image: chromadb/chroma:latest
    container_name: gas-chroma
    ports:
      - "9002:8000"          # tetap ekspos 9002 untuk kompatibilitas (opsional)
    volumes:
      - ./data/chroma:/chroma/chroma
    networks:
      - gas-network
    restart: unless-stopped

  vector-db:
    build: .
    container_name: gas-vector-db
    ports:
      - "9004:9004"
    environment:
      - PORT=9004
      - CHROMA_HOST=chroma
      - CHROMA_PORT=8000
      - DEFAULT_DIMENSION=1536
    depends_on:
      - chroma
    networks:
      - gas-network
    restart: unless-stopped

networks:
  gas-network:
    driver: bridge
```

Kemudian jalankan:
```bash
docker-compose up -d
```

> **Catatan:** Dalam konfigurasi ini, Chroma dapat diakses oleh service lain di network dengan nama `chroma:8000`.

---

## 🔧 Konfigurasi (Environment Variables)

Service ini membaca konfigurasi dari environment variables. Anda dapat mengaturnya di file `.env` atau langsung di `docker-compose.yml`.

| Variabel | Default | Deskripsi |
|----------|---------|-----------|
| `PORT` | `9004` | Port tempat FastAPI mendengarkan. |
| `CHROMA_HOST` | `localhost` | Hostname Chroma server (bisa berupa nama container). |
| `CHROMA_PORT` | `8000` | Port Chroma. |
| `CHROMA_SSL` | `false` | Apakah menggunakan HTTPS untuk koneksi ke Chroma. |
| `DEFAULT_DIMENSION` | `1536` | Dimensi embedding default (untuk koleksi baru). |
| `LOG_LEVEL` | `INFO` | Level logging (DEBUG, INFO, WARNING, ERROR). |

Contoh `.env`:
```
PORT=9004
CHROMA_HOST=gas-rag-technical-chroma
CHROMA_PORT=8000
DEFAULT_DIMENSION=1536
LOG_LEVEL=INFO
```

---

## 📡 API Reference

Dokumentasi interaktif tersedia di `http://localhost:9004/docs` (Swagger UI). Berikut ringkasan endpoint.

### **Collections**

#### `GET /collections`
Mengembalikan daftar semua koleksi yang ada.

**Response:**
```json
[
  {
    "name": "technical_analysis",
    "count": 123,
    "dimension": 768
  }
]
```

#### `POST /collections`
Membuat koleksi baru.

**Request Body:**
```json
{
  "name": "macro_news",
  "dimension": 1536,
  "metadata": {
    "description": "Berita ekonomi global"
  }
}
```

**Response:** `201 Created` dengan body `{"status": "created", "name": "macro_news"}`.

#### `DELETE /collections/{name}`
Menghapus koleksi beserta seluruh datanya.

**Response:** `200 OK` dengan `{"status": "deleted"}`.

### **Documents**

#### `POST /collections/{collection}/documents`
Upsert (tambah atau perbarui) batch dokumen ke koleksi.

**Request Body:**
```json
{
  "documents": [
    {
      "id": "doc_001",
      "embedding": [0.123, -0.456, ...],
      "metadata": {
        "date": "2025-03-01",
        "symbol": "XAUUSD",
        "source": "Bloomberg"
      },
      "text": "Inflasi AS naik 0.3% ..."
    }
  ]
}
```

**Response:** `{"status": "ok", "count": 1}`.

### **Query**

#### `POST /collections/{collection}/query`
Mencari dokumen paling mirip dengan embedding query.

**Request Body:**
```json
{
  "embedding": [0.123, -0.456, ...],
  "filter": {
    "symbol": "XAUUSD"
  },
  "top_k": 10,
  "include_metadata": true,
  "include_documents": false
}
```

- `filter` (opsional) – Filter metadata, mengikuti aturan Chroma (misal `{"symbol": "XAUUSD"}`).
- `top_k` – Jumlah hasil maksimal (default 10, maks 100).
- `include_metadata` – Sertakan metadata dalam hasil.
- `include_documents` – Sertakan teks asli dalam hasil.

**Response:**
```json
{
  "matches": [
    {
      "id": "doc_001",
      "score": 0.92,
      "metadata": {
        "date": "2025-03-01",
        "symbol": "XAUUSD"
      }
    }
  ]
}
```

### **Health**

#### `GET /health`
Pengecekan status service.

**Response:** `{"status": "ok"}`

---

## 🔗 Integrasi dengan Service Lain

### `gas-rag-technical` (port 9001)
- Gunakan koleksi `technical_analysis`.
- Embedding dihasilkan oleh model (misal OpenAI atau model sendiri).
- Contoh query:
  ```python
  import httpx
  async with httpx.AsyncClient() as client:
      resp = await client.post(
          "http://vector-db:9004/collections/technical_analysis/query",
          json={
              "embedding": query_emb,
              "top_k": 5,
              "include_metadata": True
          }
      )
      matches = resp.json()["matches"]
  ```

### `gas-rag-macro` (port 9002)
- Gunakan koleksi `macro_news` dan `economic_calendar`.
- Sama seperti di atas, dengan filter simbol jika diperlukan.

### `gas-macro-ingestor` (Google Sheets ingestor)
- Service ini akan membaca Google Sheets, menghasilkan embedding (OpenAI), lalu mengirim ke endpoint upsert.
- Contoh upsert:
  ```python
  requests.post(
      "http://vector-db:9004/collections/macro_news/documents",
      json={
          "documents": [
              {
                  "id": "news_001",
                  "embedding": embedding,
                  "metadata": {"date": "2025-03-01", "symbol": "XAUUSD"},
                  "text": full_text
              }
          ]
      }
  )
  ```

---

## 👨💻 Pengembangan

### Menjalankan Mode Development (Auto‑reload)
```bash
uvicorn src.main:app --reload --port 9004
```
Pastikan Chroma berjalan dan environment variables sudah diset.

### Menambahkan Endpoint Baru
1. Buat file route baru di `src/api/routes/`.
2. Definisikan model di `src/api/models.py`.
3. Tambahkan router ke `main.py`.
4. Tulis unit test.

### Aturan Kode
- Gunakan **type hints** untuk semua fungsi.
- Sertakan **docstring** (Google style) untuk fungsi publik.
- Ikuti **PEP 8** (gunakan `black` untuk formatting).
- Pastikan semua test lulus.

---

## 🧪 Pengujian

Unit test menggunakan `pytest`. Jalankan dari direktori proyek:
```bash
pytest tests/ -v
# dengan coverage
pytest --cov=src tests/
```

Test mencakup:
- Koneksi ke Chroma (mock)
- Validasi input pada setiap endpoint
- Error handling
- Integrasi sederhana

---

## 📄 Lisensi

**Hak Cipta © 2025 Muhamad RidwanJr dan Tim GAS.**  
Seluruh hak cipta dilindungi undang-undang. Repositori ini bersifat private dan hanya untuk tim internal GAS. Dilarang menyebarluaskan tanpa izin tertulis.
