# 🚀 Integrasi Frontend Terminal GAS dengan Backend

Bro, kita akan **rapihkan dan integrasikan** kode React yang lo berikan dengan backend service `gas-terminal-backend` yang sudah kita desain. Berikut adalah langkah-langkahnya, termasuk struktur folder, modifikasi komponen, dan cara menghubungkannya ke API gateway.

---

## 📁 Struktur Folder Final (Frontend)

```
gas-terminal-frontend/
├── public/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── Sidebar.jsx
│   │   ├── SignalView.jsx
│   │   ├── MarketsView.jsx
│   │   ├── PortfolioView.jsx
│   │   ├── AICommandCenter.jsx
│   │   ├── CalendarView.jsx
│   │   ├── SettingsView.jsx
│   │   ├── EmptyView.jsx
│   │   ├── LoadingScreen.jsx
│   │   ├── Sparkline.jsx
│   │   └── MiniCandleChart.jsx
│   ├── hooks/
│   │   └── useWebSocket.js
│   ├── services/
│   │   ├── api.js
│   │   └── websocket.js
│   ├── App.jsx
│   ├── main.jsx
│   ├── index.css
│   └── constants.js          # (opsional) untuk data statis seperti PAIRS, dll.
├── .env
├── index.html
├── package.json
├── vite.config.js
└── README.md
```

---

## 🔧 Langkah 1: Setup Environment Variables

Buat file `.env` di root frontend:

```
VITE_API_BASE_URL=http://localhost:8000/terminal
VITE_WS_BASE_URL=ws://localhost:8000/terminal/ws
```

> **Catatan:** `localhost:8000` adalah alamat gateway. Sesuaikan dengan domain/IP yang digunakan.

---

## 🔗 Langkah 2: Service API (`src/services/api.js`)

```javascript
import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_BASE_URL;

// Helper untuk menyertakan token (dari auth)
const getHeaders = () => ({
  'X-User-ID': 'dummy-user', // nanti diganti dengan user ID dari hasil login
  'Authorization': `Bearer ${localStorage.getItem('token')}`
});

export const fetchOverview = async () => {
  const res = await axios.get(`${API_BASE}/overview`, { headers: getHeaders() });
  return res.data;
};

export const fetchPairs = async () => {
  const res = await axios.get(`${API_BASE}/pairs`, { headers: getHeaders() });
  return res.data;
};

export const fetchLatestSignal = async (pair) => {
  const res = await axios.get(`${API_BASE}/signal/latest?pair=${pair}`, { headers: getHeaders() });
  return res.data;
};

export const fetchNews = async () => {
  const res = await axios.get(`${API_BASE}/news`, { headers: getHeaders() });
  return res.data;
};

export const fetchCalendar = async (params) => {
  const res = await axios.get(`${API_BASE}/calendar`, { params, headers: getHeaders() });
  return res.data;
};

export const fetchChartData = async (symbol, timeframe, from, to) => {
  const res = await axios.get(`${API_BASE}/chart/${symbol}`, {
    params: { timeframe, from, to },
    headers: getHeaders()
  });
  return res.data;
};

export const saveUserPreferences = async (prefs) => {
  const res = await axios.post(`${API_BASE}/user/preferences`, prefs, { headers: getHeaders() });
  return res.data;
};

export const fetchUserPreferences = async () => {
  const res = await axios.get(`${API_BASE}/user/preferences`, { headers: getHeaders() });
  return res.data;
};
```

---

## 📡 Langkah 3: WebSocket Hook (`src/hooks/useWebSocket.js`)

```javascript
import { useEffect, useRef, useState } from 'react';

export function useWebSocket(url, onMessage) {
  const ws = useRef(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    ws.current = new WebSocket(url);
    ws.current.onopen = () => setIsConnected(true);
    ws.current.onclose = () => setIsConnected(false);
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };
    return () => ws.current.close();
  }, [url]);

  const send = (msg) => {
    if (ws.current && isConnected) {
      ws.current.send(JSON.stringify(msg));
    }
  };

  return { isConnected, send };
}
```

---

## 🧠 Langkah 4: Modifikasi `App.jsx`

Kita akan mengganti data dummy dengan state dan useEffect untuk mengambil data dari API. Berikut potongan kode penting (full code akan terlalu panjang, tapi lo bisa lihat perubahannya).

### a. Impor dan state tambahan

```javascript
import { useEffect, useState } from 'react';
import { fetchOverview, fetchPairs, fetchLatestSignal } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';
```

### b. State untuk data dari API

```javascript
const [pairs, setPairs] = useState([]);
const [prices, setPrices] = useState({});
const [currentSignal, setCurrentSignal] = useState(null);
const [news, setNews] = useState([]);
const [globalIndices, setGlobalIndices] = useState([]);
const [macroData, setMacroData] = useState([]);
const [aiAnalysis, setAiAnalysis] = useState(null);
```

### c. useEffect untuk load data awal

```javascript
useEffect(() => {
  const loadInitialData = async () => {
    try {
      const overview = await fetchOverview();
      setPairs(overview.pairs);
      setPrices(overview.pairs.reduce((acc, p) => ({ ...acc, [p.symbol]: p.price }), {}));
      setCurrentSignal(overview.signal);
      setNews(overview.news);
      setGlobalIndices(overview.indices);
      setMacroData(overview.macro);
      setAiAnalysis(overview.ai);
    } catch (error) {
      console.error('Failed to load initial data', error);
    } finally {
      setIsLoading(false);
    }
  };
  loadInitialData();
}, []);
```

### d. WebSocket untuk update real-time

```javascript
const wsUrl = `${import.meta.env.VITE_WS_BASE_URL}?token=${localStorage.getItem('token')}`;
useWebSocket(wsUrl, (data) => {
  if (data.type === 'price') {
    setPrices(prev => ({ ...prev, [data.symbol]: data.price }));
  }
  if (data.type === 'signal') {
    setCurrentSignal(data.signal);
    setIsNewSignal(true);
    setShowAlert(true);
    if (soundEnabled) playSound();
    setTimeout(() => setIsNewSignal(false), 2000);
    setTimeout(() => setShowAlert(false), 5000);
  }
  // handle other types
});
```

### e. Hapus data dummy constants

Hapus `PAIRS`, `GLOBAL_INDICES`, `NEWS_FEED`, `AI_ANALYSIS`, `MACRO_DATA` dari file (pindahkan ke `constants.js` jika masih diperlukan sebagai fallback).

---

## 🧩 Langkah 5: Memecah Komponen ke File Terpisah

Pisahkan setiap komponen besar ke file masing-masing di folder `components/`. Contoh:

- `components/SignalView.jsx`
- `components/MarketsView.jsx`
- `components/PortfolioView.jsx`
- `components/AICommandCenter.jsx`
- `components/CalendarView.jsx`
- `components/SettingsView.jsx`
- `components/EmptyView.jsx`
- `components/Sidebar.jsx`
- `components/LoadingScreen.jsx`
- `components/Sparkline.jsx`
- `components/MiniCandleChart.jsx`

Setiap komponen akan menerima props yang diperlukan (misal `signal`, `prices`, dll) dan menggunakan data dari state.

Contoh `SignalView` akan menerima props:

```javascript
function SignalView({ signal, isNew, timer, chartPair, prices, onSelect, activePair }) {
  // ...
}
```

---

## 🎨 Langkah 6: CSS dan Animasi

Pindahkan semua CSS yang ada di dalam `<style>` di `App.jsx` ke file `index.css`. Tambahkan juga aturan untuk animasi scroll dan alert.

Contoh `index.css`:

```css
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap');

* {
  font-family: 'DM Sans', sans-serif;
}

@keyframes pulse-dot-anim {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.pulse-dot {
  animation: pulse-dot-anim 1.5s ease-in-out infinite;
}

@keyframes loading-bar {
  0% { width: 0%; opacity: 1; }
  80% { width: 100%; opacity: 1; }
  100% { width: 100%; opacity: 0; }
}

.loading-bar {
  animation: loading-bar 1.8s ease-in-out forwards;
}

/* Ticker scroll animation */
.ticker-scroll {
  animation: ticker 30s linear infinite;
}

@keyframes ticker {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* News scroll animation */
.news-scroll {
  animation: news 40s linear infinite;
}

@keyframes news {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}
```

---

## 🚀 Langkah 7: Menjalankan Frontend

1. Install dependensi:
   ```bash
   npm install
   ```

2. Jalankan development server:
   ```bash
   npm run dev
   ```

3. Buka `http://localhost:5173` (default Vite).

Pastikan backend `gas-terminal-backend` dan gateway sudah berjalan.

---

## 🔗 Integrasi dengan Gateway

Gateway harus meneruskan request dengan prefix `/terminal` ke `gas-terminal-backend`. Contoh konfigurasi di `gas-gateway-api` (FastAPI):

```python
@app.route('/terminal/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE'])
async def proxy_terminal(request: Request, path: str):
    # tambahkan header X-User-ID dari JWT yang sudah diverifikasi
    headers = dict(request.headers)
    headers['X-User-ID'] = request.state.user_id
    async with httpx.AsyncClient() as client:
        url = f"http://gas-terminal-backend:8085/{path}"
        resp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            params=request.query_params,
            content=await request.body()
        )
        return Response(content=resp.content, status_code=resp.status_code, headers=dict(resp.headers))
```

Untuk WebSocket, gateway perlu melakukan proxy juga (bisa menggunakan `websockets` library).

---

## ✅ Kesimpulan

Dengan langkah di atas, frontend terminal GAS akan:

- Mengambil data real dari backend via REST API.
- Menerima update real‑time via WebSocket.
- Memiliki kode yang terstruktur dan mudah dipelihara.

Selanjutnya, lo tinggal menyesuaikan endpoint di backend sesuai dengan kebutuhan data yang dikembalikan. Jangan lupa untuk mengganti `dummy-user` dengan user ID yang sesungguhnya setelah sistem autentikasi terpasang.

Gas terus, bro! 🔥 Kalau ada bagian yang mau didetailin, tinggal tunjuk.