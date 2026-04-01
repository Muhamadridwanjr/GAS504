import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  TrendingUp, TrendingDown, BarChart2, Activity, Search, RefreshCw,
  Zap, Target, Shield, ChevronRight, ArrowUp, ArrowDown, Minus,
  AlertTriangle, CheckCircle, Clock, Building2, Star,
} from 'lucide-react';
import AutoSignalPanel from './AutoSignalPanel';
import MarketAnalysisPanel from './MarketAnalysisPanel';

// ── Constants ─────────────────────────────────────────────────────────────────
const MONO = "'JetBrains Mono','Fira Mono','Courier New',monospace";

// Major 25 blue-chip IDX stocks
const IDX_MAJOR = [
  'BBCA','BBRI','BMRI','BBNI','BRIS',
  'TLKM','ISAT','EXCL','GOTO','EMTK',
  'BREN','ADRO','PTBA','BYAN','CUAN',
  'INCO','ANTM','MDKA','AMMN','NCKL',
  'ASII','UNVR','ICBP','INDF','HMSP',
];
// New listings / high-growth picks
const IDX_NEW_LISTINGS = ['PGEO','WIFI','HEAL','DSSA','HRTA','RATU','CUAN','AMMN','BREN','NCKL'];
const IDX_WATCHLIST = [...new Set([...IDX_MAJOR, ...IDX_NEW_LISTINGS])];

const POPULAR_CHIPS = ['BBCA','BBRI','BMRI','TLKM','ASII','GOTO'];
const INTERVALS = ['1m','5m','15m','1h','1d','1wk'];
const PERIODS = ['1mo','3mo','6mo','1y'];

const IDX_TV_PAIRS = [
  { sym: 'IDX:COMPOSITE', label: 'IHSG',  name: 'Jakarta Composite',     sector: 'Index' },
  { sym: 'IDX:BBCA', label: 'BBCA', name: 'Bank Central Asia',           sector: 'Bank' },
  { sym: 'IDX:BBRI', label: 'BBRI', name: 'Bank Rakyat Indonesia',       sector: 'Bank' },
  { sym: 'IDX:BMRI', label: 'BMRI', name: 'Bank Mandiri',                sector: 'Bank' },
  { sym: 'IDX:BBNI', label: 'BBNI', name: 'Bank Negara Indonesia',       sector: 'Bank' },
  { sym: 'IDX:BRIS', label: 'BRIS', name: 'Bank Syariah Indonesia',      sector: 'Bank' },
  { sym: 'IDX:NISP', label: 'NISP', name: 'OCBC NISP',                   sector: 'Bank' },
  { sym: 'IDX:PNBN', label: 'PNBN', name: 'Panin Bank',                  sector: 'Bank' },
  { sym: 'IDX:BBTN', label: 'BBTN', name: 'Bank Tabungan Negara',        sector: 'Bank' },
  { sym: 'IDX:TLKM', label: 'TLKM', name: 'Telkom Indonesia',            sector: 'Telco' },
  { sym: 'IDX:ISAT', label: 'ISAT', name: 'Indosat Ooredoo',             sector: 'Telco' },
  { sym: 'IDX:EXCL', label: 'EXCL', name: 'XL Axiata',                   sector: 'Telco' },
  { sym: 'IDX:TBIG', label: 'TBIG', name: 'Tower Bersama',               sector: 'Telco' },
  { sym: 'IDX:GOTO', label: 'GOTO', name: 'GoTo Gojek Tokopedia',        sector: 'Tech' },
  { sym: 'IDX:EMTK', label: 'EMTK', name: 'Elang Mahkota Teknologi',    sector: 'Tech' },
  { sym: 'IDX:BREN', label: 'BREN', name: 'Barito Renewables Energy',    sector: 'Energi' },
  { sym: 'IDX:PGAS', label: 'PGAS', name: 'Perusahaan Gas Negara',       sector: 'Energi' },
  { sym: 'IDX:ESSA', label: 'ESSA', name: 'Essa Industries Indonesia',   sector: 'Energi' },
  { sym: 'IDX:ELSA', label: 'ELSA', name: 'Elnusa',                      sector: 'Energi' },
  { sym: 'IDX:MEDC', label: 'MEDC', name: 'Medco Energi Internasional',  sector: 'Energi' },
  { sym: 'IDX:ADRO', label: 'ADRO', name: 'Adaro Energy Indonesia',      sector: 'Batubara' },
  { sym: 'IDX:PTBA', label: 'PTBA', name: 'Bukit Asam',                  sector: 'Batubara' },
  { sym: 'IDX:INCO', label: 'INCO', name: 'Vale Indonesia',              sector: 'Tambang' },
  { sym: 'IDX:ANTM', label: 'ANTM', name: 'Aneka Tambang',               sector: 'Tambang' },
  { sym: 'IDX:TINS', label: 'TINS', name: 'Timah',                       sector: 'Tambang' },
  { sym: 'IDX:MDKA', label: 'MDKA', name: 'Merdeka Copper Gold',         sector: 'Tambang' },
  { sym: 'IDX:UNVR', label: 'UNVR', name: 'Unilever Indonesia',          sector: 'Konsumer' },
  { sym: 'IDX:ICBP', label: 'ICBP', name: 'Indofood CBP Sukses Makmur', sector: 'Konsumer' },
  { sym: 'IDX:INDF', label: 'INDF', name: 'Indofood Sukses Makmur',      sector: 'Konsumer' },
  { sym: 'IDX:HMSP', label: 'HMSP', name: 'HM Sampoerna',                sector: 'Konsumer' },
  { sym: 'IDX:MYOR', label: 'MYOR', name: 'Mayora Indah',                sector: 'Konsumer' },
  { sym: 'IDX:DLTA', label: 'DLTA', name: 'Delta Djakarta',              sector: 'Konsumer' },
  { sym: 'IDX:ULTJ', label: 'ULTJ', name: 'Ultra Jaya Milk Industry',    sector: 'Konsumer' },
  { sym: 'IDX:CPIN', label: 'CPIN', name: 'Charoen Pokphand Indonesia',  sector: 'Konsumer' },
  { sym: 'IDX:JPFA', label: 'JPFA', name: 'Japfa Comfeed Indonesia',     sector: 'Konsumer' },
  { sym: 'IDX:KLBF', label: 'KLBF', name: 'Kalbe Farma',                 sector: 'Farma' },
  { sym: 'IDX:SIDO', label: 'SIDO', name: 'Industri Jamu Sido Muncul',   sector: 'Farma' },
  { sym: 'IDX:MIKA', label: 'MIKA', name: 'Mitra Keluarga Karyasehat',   sector: 'Kesehatan' },
  { sym: 'IDX:HEAL', label: 'HEAL', name: 'Medikaloka Hermina',          sector: 'Kesehatan' },
  { sym: 'IDX:ASII', label: 'ASII', name: 'Astra International',         sector: 'Industri' },
  { sym: 'IDX:SMGR', label: 'SMGR', name: 'Semen Indonesia',             sector: 'Industri' },
  { sym: 'IDX:INKP', label: 'INKP', name: 'Indah Kiat Pulp & Paper',     sector: 'Industri' },
  { sym: 'IDX:TKIM', label: 'TKIM', name: 'Pabrik Kertas Tjiwi Kimia',  sector: 'Industri' },
  { sym: 'IDX:BSDE', label: 'BSDE', name: 'Bumi Serpong Damai',         sector: 'Properti' },
  { sym: 'IDX:PWON', label: 'PWON', name: 'Pakuwon Jati',                sector: 'Properti' },
  { sym: 'IDX:LPKR', label: 'LPKR', name: 'Lippo Karawaci',             sector: 'Properti' },
  { sym: 'IDX:SMRA', label: 'SMRA', name: 'Summarecon Agung',            sector: 'Properti' },
  { sym: 'IDX:ACES', label: 'ACES', name: 'Ace Hardware Indonesia',      sector: 'Retail' },
  { sym: 'IDX:MAPI', label: 'MAPI', name: 'Mitra Adi Perkasa',          sector: 'Retail' },
  { sym: 'IDX:ERAA', label: 'ERAA', name: 'Erajaya Swasembada',          sector: 'Retail' },
  { sym: 'IDX:AALI', label: 'AALI', name: 'Astra Agro Lestari',         sector: 'Agri' },
];

const CHART_SECTORS = ['Semua','Index','Bank','Telco','Tech','Energi','Batubara','Tambang','Konsumer','Farma','Kesehatan','Industri','Properti','Retail','Agri'];

const TV_INTERVALS = [
  { label: '1m',  value: '1'   },
  { label: '5m',  value: '5'   },
  { label: '15m', value: '15'  },
  { label: '30m', value: '30'  },
  { label: '1h',  value: '60'  },
  { label: '4h',  value: '240' },
  { label: '1D',  value: 'D'   },
  { label: '1W',  value: 'W'   },
];

// ── Helper functions ──────────────────────────────────────────────────────────
const fmtPrice = (n) => n != null ? Number(n).toLocaleString('id-ID') : '—';
const fmtVol = (n) => {
  if (n == null) return '—';
  if (n >= 1e9) return (n / 1e9).toFixed(1) + 'B';
  if (n >= 1e6) return (n / 1e6).toFixed(1) + 'M';
  if (n >= 1e3) return (n / 1e3).toFixed(0) + 'K';
  return String(n);
};
const fmtMktCap = (n) => {
  if (n == null) return '—';
  if (n >= 1e12) return 'Rp ' + (n / 1e12).toFixed(2) + 'T';
  if (n >= 1e9) return 'Rp ' + (n / 1e9).toFixed(1) + 'B';
  return 'Rp ' + Number(n).toLocaleString('id-ID');
};
const signalColor = (score) =>
  score >= 68 ? '#22c55e' : score <= 32 ? '#ef4444' : '#facc15';
const signalBg = (score) =>
  score >= 68 ? 'rgba(34,197,94,0.1)' : score <= 32 ? 'rgba(239,68,68,0.1)' : 'rgba(250,204,21,0.1)';
const changePctColor = (pct) =>
  pct > 0 ? '#22c55e' : pct < 0 ? '#ef4444' : 'var(--text-dim)';
const fmtPct = (n) => (n == null ? '—' : (n >= 0 ? '+' : '') + Number(n).toFixed(2) + '%');

// ── Sub-components ────────────────────────────────────────────────────────────

function Sparkline({ data, color = '#facc15', width = 60, height = 24 }) {
  if (!data || data.length < 2) return null;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const pts = data
    .map((v, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((v - min) / range) * height;
      return `${x},${y}`;
    })
    .join(' ');
  return (
    <svg width={width} height={height} style={{ overflow: 'visible' }}>
      <polyline
        points={pts}
        fill="none"
        stroke={color}
        strokeWidth="1.5"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
}

function RSIBar({ value }) {
  const v = value ?? 50;
  const color = v < 30 ? '#22c55e' : v > 70 ? '#ef4444' : '#facc15';
  return (
    <div style={{ position: 'relative', height: 6, background: 'var(--bg-panel)', borderRadius: 3, width: '100%' }}>
      <div style={{ position: 'absolute', left: '30%', top: -2, width: 1, height: 10, background: 'rgba(255,255,255,0.15)' }} />
      <div style={{ position: 'absolute', left: '70%', top: -2, width: 1, height: 10, background: 'rgba(255,255,255,0.15)' }} />
      <div style={{
        position: 'absolute',
        left: `${Math.min(Math.max(v, 2), 98)}%`,
        top: -3,
        width: 10,
        height: 12,
        background: color,
        borderRadius: 2,
        transform: 'translateX(-50%)',
      }} />
    </div>
  );
}

function Skeleton({ width = '100%', height = 16, radius = 6 }) {
  return (
    <div style={{
      width,
      height,
      borderRadius: radius,
      background: 'linear-gradient(90deg, var(--bg-panel) 25%, var(--bg-card) 50%, var(--bg-panel) 75%)',
      backgroundSize: '200% 100%',
      animation: 'shimmer 1.4s infinite',
    }} />
  );
}

function SectionHeader({ icon: Icon, label }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 12 }}>
      <Icon size={12} color="#facc15" />
      <span style={{
        fontFamily: MONO,
        fontSize: 10,
        letterSpacing: '0.1em',
        color: '#facc15',
        textTransform: 'uppercase',
        fontWeight: 700,
      }}>
        {label}
      </span>
    </div>
  );
}

function Card({ children, style = {} }) {
  return (
    <div style={{
      background: 'var(--bg-card)',
      border: '1px solid var(--border-color)',
      borderRadius: 14,
      padding: 16,
      ...style,
    }}>
      {children}
    </div>
  );
}

function ScoreCircle({ score }) {
  const r = 36;
  const circ = 2 * Math.PI * r;
  const pct = Math.min(Math.max(score ?? 0, 0), 100);
  const dash = (pct / 100) * circ;
  const color = signalColor(pct);

  return (
    <div style={{ position: 'relative', width: 88, height: 88, flexShrink: 0 }}>
      <svg width={88} height={88} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={44} cy={44} r={r} fill="none" stroke="var(--bg-panel)" strokeWidth={5} />
        <circle
          cx={44} cy={44} r={r}
          fill="none"
          stroke={color}
          strokeWidth={5}
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
      </svg>
      <div style={{
        position: 'absolute',
        inset: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexDirection: 'column',
      }}>
        <span style={{ fontFamily: MONO, fontSize: 18, fontWeight: 800, color, lineHeight: 1 }}>
          {pct}
        </span>
        <span style={{ fontFamily: MONO, fontSize: 8, color: 'var(--text-dim)', marginTop: 2 }}>SCORE</span>
      </div>
    </div>
  );
}

function ActionBadge({ action, score }) {
  const color = signalColor(score ?? 50);
  const bg = signalBg(score ?? 50);
  const label = action?.toUpperCase() ?? 'HOLD';
  return (
    <span style={{
      fontFamily: MONO,
      fontSize: 14,
      fontWeight: 800,
      color,
      background: bg,
      border: `1px solid ${color}44`,
      borderRadius: 8,
      padding: '4px 14px',
      boxShadow: `0 0 12px ${color}33`,
      letterSpacing: '0.08em',
    }}>
      {label}
    </span>
  );
}

function DayRangeBar({ low, high, current }) {
  if (!low || !high || low === high) return null;
  const pct = Math.min(Math.max(((current - low) / (high - low)) * 100, 0), 100);
  return (
    <div style={{ width: '100%' }}>
      <div style={{ position: 'relative', height: 4, background: 'var(--bg-panel)', borderRadius: 2, margin: '4px 0' }}>
        <div style={{
          position: 'absolute',
          left: 0,
          width: `${pct}%`,
          height: '100%',
          background: 'linear-gradient(90deg, #ef4444, #22c55e)',
          borderRadius: 2,
        }} />
        <div style={{
          position: 'absolute',
          left: `${pct}%`,
          top: -3,
          width: 10,
          height: 10,
          background: '#facc15',
          borderRadius: '50%',
          transform: 'translateX(-50%)',
          border: '2px solid var(--bg-card)',
        }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 2 }}>
        <span style={{ fontFamily: MONO, fontSize: 9, color: 'var(--text-dim)' }}>{fmtPrice(low)}</span>
        <span style={{ fontFamily: MONO, fontSize: 9, color: 'var(--text-dim)' }}>{fmtPrice(high)}</span>
      </div>
    </div>
  );
}

// ── TradingView Chart (IDX) ────────────────────────────────────────────────────
function IDXTVChart({ symbol, interval }) {
  const ref = useRef(null);
  const theme = localStorage.getItem('gas-theme') || 'dark';
  useEffect(() => {
    if (!ref.current) return;
    const s = document.createElement('script');
    s.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
    s.type = 'text/javascript';
    s.async = true;
    s.innerHTML = JSON.stringify({
      autosize: true,
      symbol,
      interval,
      timezone: 'Asia/Jakarta',
      theme: theme === 'light' ? 'light' : 'dark',
      style: '1',
      locale: 'id',
      enable_publishing: false,
      hide_side_toolbar: false,
      allow_symbol_change: true,
      studies: ['STD;EMA', 'STD;MA%20Exp;50', 'STD;MA%20Exp;200', 'STD;MACD', 'STD;RSI'],
      support_host: 'https://www.tradingview.com',
    });
    ref.current.innerHTML = '';
    ref.current.appendChild(s);
  }, [symbol, interval, theme]);
  return (
    <div ref={ref} className="tradingview-widget-container" style={{ height: '100%', width: '100%' }}>
      <div className="tradingview-widget-container__widget" style={{ height: 'calc(100% - 32px)', width: '100%' }} />
    </div>
  );
}

const TABS = [
  { id:'Overview',   icon:'fa-solid fa-gauge-high',   label:'Overview' },
  { id:'Signals',    icon:'fa-solid fa-chart-line',    label:'Signals' },
  { id:'Technical',  icon:'fa-solid fa-chart-area',    label:'Technical' },
  { id:'Session',    icon:'fa-solid fa-clock',          label:'Session' },
  { id:'Data',       icon:'fa-solid fa-table',           label:'Data' },
  { id:'AI Insight', icon:'fa-solid fa-brain',           label:'AI Insight' },
];

// ── Main Component ─────────────────────────────────────────────────────────────
export default function StockIDXView() {
  const [gasTab, setGasTab] = useState('Overview');
  const [mode, setMode] = useState('manual');
  const [tab, setTab] = useState('pasar');
  const [ihsg, setIhsg] = useState(null);
  const [tickers, setTickers] = useState([]);
  const [selectedStock, setSelectedStock] = useState('BBCA');
  const [signal, setSignal] = useState(null);
  const [smcData, setSmcData] = useState(null);
  const [ohlcv, setOhlcv] = useState([]);
  const [activeInterval, setActiveInterval] = useState('1d');
  const [period, setPeriod] = useState('3mo');
  const [scanner, setScanner] = useState({ gainers: [], losers: [], active: [] });
  const [scannerTab, setScannerTab] = useState('gainers');
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});
  const [autoRefresh, setAutoRefresh] = useState(false);
  const autoRefreshRef = useRef(null);
  const [chartSymbol, setChartSymbol] = useState('IDX:COMPOSITE');
  const [chartInterval, setChartInterval] = useState('D');
  const [chartSector, setChartSector] = useState('Semua');

  // ── API helpers ───────────────────────────────────────────────────────────
  const getHeaders = () => ({
    Authorization: `Bearer ${localStorage.getItem('gas-token')}`,
  });

  const setLoad = (key, val) => setLoading((p) => ({ ...p, [key]: val }));
  const setErr = (key, val) => setErrors((p) => ({ ...p, [key]: val }));

  // ── Fetchers ──────────────────────────────────────────────────────────────
  const fetchIHSG = useCallback(async () => {
    setLoad('ihsg', true);
    setErr('ihsg', null);
    try {
      const res = await fetch('/terminal/idx/ihsg', { headers: getHeaders() });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setIhsg(data);
    } catch (e) {
      setErr('ihsg', e.message);
    } finally {
      setLoad('ihsg', false);
    }
  }, []);

  const fetchTickers = useCallback(async () => {
    setLoad('tickers', true);
    setErr('tickers', null);
    try {
      const res = await fetch(
        '/terminal/idx/tickers?symbols=' + IDX_WATCHLIST.join(','),
        { headers: getHeaders() }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setTickers(Array.isArray(data) ? data : data.tickers ?? []);
    } catch (e) {
      setErr('tickers', e.message);
    } finally {
      setLoad('tickers', false);
    }
  }, []);

  const fetchSignal = useCallback(async (symbol = selectedStock, interval = activeInterval) => {
    setLoad('signal', true);
    setErr('signal', null);
    setSignal(null);
    try {
      const res = await fetch(
        `/terminal/idx/signal?symbol=${symbol}&interval=${interval}&period=${period}`,
        { headers: getHeaders() }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setSignal(data);
      setOhlcv(data.ohlcv ?? []);
    } catch (e) {
      setErr('signal', e.message);
    } finally {
      setLoad('signal', false);
    }
  }, [selectedStock, activeInterval, period]);

  const fetchSMC = useCallback(async (symbol = selectedStock, interval = activeInterval) => {
    setLoad('smc', true);
    setErr('smc', null);
    setSmcData(null);
    try {
      const res = await fetch(
        `/terminal/idx/smc?symbol=${symbol}&interval=${interval}&style=swing`,
        { headers: getHeaders() }
      );
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setSmcData(data);
    } catch (e) {
      setErr('smc', e.message);
    } finally {
      setLoad('smc', false);
    }
  }, [selectedStock, activeInterval]);

  const fetchScanner = useCallback(async () => {
    setLoad('scanner', true);
    setErr('scanner', null);
    try {
      const [g, l, a] = await Promise.all([
        fetch('/terminal/idx/top_gainer?n=10', { headers: getHeaders() }).then((r) => r.json()),
        fetch('/terminal/idx/top_loser?n=10', { headers: getHeaders() }).then((r) => r.json()),
        fetch('/terminal/idx/most_active?n=10', { headers: getHeaders() }).then((r) => r.json()),
      ]);
      setScanner({
        gainers: Array.isArray(g) ? g : g.data ?? [],
        losers: Array.isArray(l) ? l : l.data ?? [],
        active: Array.isArray(a) ? a : a.data ?? [],
      });
    } catch (e) {
      setErr('scanner', e.message);
    } finally {
      setLoad('scanner', false);
    }
  }, []);

  // ── Effects ───────────────────────────────────────────────────────────────
  useEffect(() => {
    fetchIHSG();
    fetchTickers();
  }, []);

  useEffect(() => {
    if (tab === 'analisa') fetchSignal(selectedStock, activeInterval);
  }, [tab, selectedStock, activeInterval, period]);

  useEffect(() => {
    if (tab === 'smc') fetchSMC(selectedStock, activeInterval);
  }, [tab, selectedStock, activeInterval]);

  useEffect(() => {
    if (tab === 'scanner') fetchScanner();
  }, [tab]);

  useEffect(() => {
    if (autoRefresh) {
      autoRefreshRef.current = setInterval(() => {
        fetchIHSG();
        fetchTickers();
        if (tab === 'analisa') fetchSignal(selectedStock, activeInterval);
      }, 30000);
    } else {
      clearInterval(autoRefreshRef.current);
    }
    return () => clearInterval(autoRefreshRef.current);
  }, [autoRefresh, tab, selectedStock, activeInterval]);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleSelectStock = (symbol) => {
    setSelectedStock(symbol);
    setTab('analisa');
  };

  // ── Filtered watchlist ────────────────────────────────────────────────────
  const filteredTickers = searchQuery
    ? tickers.filter((t) => t.symbol?.toLowerCase().includes(searchQuery.toLowerCase()))
    : tickers;

  // ── Sparkline data from tickers ───────────────────────────────────────────
  const ihsgSparkData = ihsg?.history ?? ohlcv.slice(-7).map((c) => c[4]);

  // ── Styles ────────────────────────────────────────────────────────────────
  const styles = {
    container: {
      fontFamily: MONO,
      color: 'var(--text-primary)',
      minHeight: '100vh',
      padding: '0 0 40px 0',
    },
    header: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '20px 20px 12px',
      borderBottom: '1px solid var(--border-color)',
    },
    tabBar: {
      display: 'flex',
      gap: 6,
      padding: '14px 20px 0',
      borderBottom: '1px solid var(--border-color)',
    },
    tab: (active) => ({
      fontFamily: MONO,
      fontSize: 12,
      fontWeight: 700,
      letterSpacing: '0.06em',
      padding: '6px 18px',
      borderRadius: 20,
      border: 'none',
      cursor: 'pointer',
      background: active ? '#facc15' : 'transparent',
      color: active ? '#000' : 'var(--text-dim)',
      transition: 'all 0.2s',
      marginBottom: -1,
    }),
    content: {
      padding: '20px',
    },
  };

  // ── CSS injection for shimmer ─────────────────────────────────────────────
  useEffect(() => {
    const id = 'idx-shimmer-style';
    if (!document.getElementById(id)) {
      const s = document.createElement('style');
      s.id = id;
      s.textContent = `@keyframes shimmer { 0%{background-position:200% 0} 100%{background-position:-200% 0} }`;
      document.head.appendChild(s);
    }
  }, []);

  // ═══════════════════════════════════════════════════════════════════════════
  // TAB: PASAR
  // ═══════════════════════════════════════════════════════════════════════════
  const renderPasar = () => {
    const ihsgChange = ihsg?.change ?? 0;
    const ihsgPct = ihsg?.change_pct ?? 0;
    const isUp = ihsgChange >= 0;

    return (
      <div>
        {/* IHSG Hero Card */}
        <Card style={{ marginBottom: 16 }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: 12 }}>
            <div style={{ flex: 1, minWidth: 200 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                <Building2 size={14} color="#facc15" />
                <span style={{ fontSize: 10, color: 'var(--text-dim)', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                  Jakarta Composite Index
                </span>
                <span style={{
                  fontSize: 9,
                  fontFamily: MONO,
                  background: 'rgba(250,204,21,0.12)',
                  color: '#facc15',
                  border: '1px solid #facc1544',
                  borderRadius: 4,
                  padding: '1px 6px',
                }}>
                  IDX:COMPOSITE
                </span>
              </div>

              {loading.ihsg ? (
                <Skeleton width={200} height={38} />
              ) : (
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 12 }}>
                  <span style={{ fontFamily: MONO, fontSize: 36, fontWeight: 800, color: 'var(--text-primary)', lineHeight: 1 }}>
                    {fmtPrice(ihsg?.price ?? ihsg?.value)}
                  </span>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    {isUp ? <ArrowUp size={14} color="#22c55e" /> : <ArrowDown size={14} color="#ef4444" />}
                    <span style={{ fontFamily: MONO, fontSize: 14, fontWeight: 700, color: changePctColor(ihsgPct) }}>
                      {fmtPct(ihsgPct)}
                    </span>
                    <span style={{ fontFamily: MONO, fontSize: 12, color: 'var(--text-dim)' }}>
                      ({ihsgChange >= 0 ? '+' : ''}{fmtPrice(ihsgChange)})
                    </span>
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', gap: 12, marginTop: 10, flexWrap: 'wrap' }}>
                {[
                  { label: 'Open', val: ihsg?.open },
                  { label: 'High', val: ihsg?.high },
                  { label: 'Low', val: ihsg?.low },
                  { label: 'Volume', val: fmtVol(ihsg?.volume) },
                ].map(({ label, val }) => (
                  <div key={label}>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 1, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
                    <div style={{ fontFamily: MONO, fontSize: 11, color: 'var(--text-primary)' }}>
                      {typeof val === 'number' ? fmtPrice(val) : val ?? '—'}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 8 }}>
              <Sparkline
                data={ihsgSparkData.length >= 2 ? ihsgSparkData : [7000, 7050, 7020, 7080, 7060, 7100, 7106]}
                color={isUp ? '#22c55e' : '#ef4444'}
                width={100}
                height={40}
              />
              <span style={{
                fontSize: 9,
                fontFamily: MONO,
                background: ihsg?.session_active ? 'rgba(34,197,94,0.12)' : 'rgba(255,255,255,0.05)',
                color: ihsg?.session_active ? '#22c55e' : 'var(--text-dim)',
                border: `1px solid ${ihsg?.session_active ? '#22c55e44' : 'var(--border-color)'}`,
                borderRadius: 4,
                padding: '2px 8px',
              }}>
                {ihsg?.session_active ? 'SESSION OPEN' : 'SESSION CLOSED'}
              </span>
            </div>
          </div>
        </Card>

        {/* Watchlist Grid */}
        {loading.tickers && tickers.length === 0 ? (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))', gap: 10 }}>
            {IDX_WATCHLIST.slice(0, 6).map((s) => (
              <Skeleton key={s} height={110} radius={14} />
            ))}
          </div>
        ) : errors.tickers ? (
          <Card style={{ textAlign: 'center', padding: 32 }}>
            <AlertTriangle size={28} color="#ef4444" style={{ margin: '0 auto 8px' }} />
            <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 10 }}>Failed to load tickers</div>
            <button
              onClick={fetchTickers}
              style={{ fontFamily: MONO, fontSize: 11, background: '#facc15', color: '#000', border: 'none', borderRadius: 8, padding: '6px 16px', cursor: 'pointer', fontWeight: 700 }}
            >
              Retry
            </button>
          </Card>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(200px,1fr))', gap: 10 }}>
            {filteredTickers.map((t) => (
              <TickerCard
                key={t.symbol}
                ticker={t}
                onSelect={handleSelectStock}
                selected={selectedStock === t.symbol}
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // TAB: ANALISA
  // ═══════════════════════════════════════════════════════════════════════════
  const renderAnalisa = () => {
    const tech = signal?.technical ?? {};
    const sig = tech?.signal ?? {};
    const ind = tech?.indicators ?? {};
    const fund = signal?.fundamental ?? {};
    const score = sig?.score ?? sig?.final_score ?? 50;
    const action = sig?.action ?? sig?.signal ?? 'HOLD';

    return (
      <div>
        {/* Stock Selector */}
        <Card style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap' }}>
            <div style={{ position: 'relative', flex: '0 0 auto' }}>
              <Search size={12} color="var(--text-dim)" style={{ position: 'absolute', left: 10, top: '50%', transform: 'translateY(-50%)' }} />
              <input
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search symbol..."
                style={{
                  fontFamily: MONO,
                  fontSize: 12,
                  background: 'var(--bg-panel)',
                  border: '1px solid var(--border-color)',
                  borderRadius: 8,
                  padding: '6px 10px 6px 28px',
                  color: 'var(--text-primary)',
                  width: 160,
                  outline: 'none',
                }}
              />
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {POPULAR_CHIPS.map((sym) => (
                <button
                  key={sym}
                  onClick={() => setSelectedStock(sym)}
                  style={{
                    fontFamily: MONO,
                    fontSize: 11,
                    fontWeight: 700,
                    background: selectedStock === sym ? '#facc15' : 'var(--bg-panel)',
                    color: selectedStock === sym ? '#000' : 'var(--text-dim)',
                    border: `1px solid ${selectedStock === sym ? '#facc15' : 'var(--border-color)'}`,
                    borderRadius: 6,
                    padding: '4px 10px',
                    cursor: 'pointer',
                    transition: 'all 0.15s',
                  }}
                >
                  {sym}
                </button>
              ))}
            </div>

            {/* Interval */}
            <div style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
              {INTERVALS.map((iv) => (
                <button
                  key={iv}
                  onClick={() => setActiveInterval(iv)}
                  style={{
                    fontFamily: MONO,
                    fontSize: 10,
                    fontWeight: 600,
                    background: activeInterval === iv ? 'rgba(250,204,21,0.15)' : 'transparent',
                    color: activeInterval === iv ? '#facc15' : 'var(--text-dim)',
                    border: `1px solid ${activeInterval === iv ? '#facc1555' : 'transparent'}`,
                    borderRadius: 5,
                    padding: '3px 8px',
                    cursor: 'pointer',
                  }}
                >
                  {iv}
                </button>
              ))}
            </div>
          </div>
        </Card>

        {loading.signal ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            <Skeleton height={120} radius={14} />
            <Skeleton height={180} radius={14} />
            <Skeleton height={120} radius={14} />
          </div>
        ) : errors.signal ? (
          <Card style={{ textAlign: 'center', padding: 32 }}>
            <AlertTriangle size={28} color="#ef4444" style={{ margin: '0 auto 8px' }} />
            <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 10 }}>{errors.signal}</div>
            <button
              onClick={() => fetchSignal()}
              style={{ fontFamily: MONO, fontSize: 11, background: '#facc15', color: '#000', border: 'none', borderRadius: 8, padding: '6px 16px', cursor: 'pointer', fontWeight: 700 }}
            >
              Retry
            </button>
          </Card>
        ) : (
          <>
            {/* Main Signal Card */}
            <Card style={{ marginBottom: 14 }}>
              <SectionHeader icon={Zap} label={`${selectedStock} · Signal Analysis`} />
              <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
                {/* Score Circle */}
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 10 }}>
                  <ScoreCircle score={score} />
                  <ActionBadge action={action} score={score} />
                  <div style={{ fontFamily: MONO, fontSize: 9, color: 'var(--text-dim)', textAlign: 'center' }}>
                    Tech: {sig?.technical_score ?? '—'} · SMC: {sig?.smc_score ?? '—'} · Final: {score}
                  </div>
                </div>

                {/* Indicators Grid */}
                <div style={{ flex: 1, minWidth: 240 }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                    {/* RSI */}
                    <div style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>RSI</div>
                      <div style={{ fontFamily: MONO, fontSize: 16, fontWeight: 700, color: (Number(ind.rsi) || 50) < 30 ? '#22c55e' : (Number(ind.rsi) || 50) > 70 ? '#ef4444' : '#facc15', marginBottom: 6 }}>
                        {ind.rsi != null && !isNaN(Number(ind.rsi)) ? Number(ind.rsi).toFixed(1) : '—'}
                      </div>
                      <RSIBar value={ind.rsi ?? 50} />
                    </div>

                    {/* MACD */}
                    <div style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>MACD</div>
                      <div style={{ fontFamily: MONO, fontSize: 14, fontWeight: 700, color: (Number(ind.macd) || 0) >= 0 ? '#22c55e' : '#ef4444' }}>
                        {ind.macd != null && !isNaN(Number(ind.macd)) ? Number(ind.macd).toFixed(4) : '—'}
                      </div>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 4 }}>
                        {ind.macd_signal != null ? ((Number(ind.macd) || 0) > Number(ind.macd_signal) ? 'BULLISH ↑' : 'BEARISH ↓') : '—'}
                      </div>
                    </div>

                    {/* EMA */}
                    <div style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>EMA 9 / 21 / 50</div>
                      {['ema9','ema21','ema50'].map((k) => (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                          <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-dim)' }}>{k.toUpperCase()}</span>
                          <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(ind[k])}</span>
                        </div>
                      ))}
                    </div>

                    {/* Bollinger */}
                    <div style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>Bollinger</div>
                      {[['Upper', ind.bb_upper], ['Mid', ind.bb_mid], ['Lower', ind.bb_lower]].map(([k, v]) => (
                        <div key={k} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 2 }}>
                          <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-dim)' }}>{k}</span>
                          <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(v)}</span>
                        </div>
                      ))}
                    </div>

                    {/* Stochastic */}
                    <div style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>Stochastic</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <div>
                          <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>%K</div>
                          <div style={{ fontFamily: MONO, fontSize: 13, color: 'var(--text-primary)' }}>{ind.stoch_k?.toFixed(1) ?? '—'}</div>
                        </div>
                        <div>
                          <div style={{ fontSize: 9, color: 'var(--text-dim)' }}>%D</div>
                          <div style={{ fontFamily: MONO, fontSize: 13, color: 'var(--text-primary)' }}>{ind.stoch_d?.toFixed(1) ?? '—'}</div>
                        </div>
                      </div>
                    </div>

                    {/* ATR & VWAP */}
                    <div style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', marginBottom: 4, textTransform: 'uppercase' }}>ATR / VWAP</div>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-dim)' }}>ATR</span>
                        <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(ind.atr)}</span>
                      </div>
                      <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-dim)' }}>VWAP</span>
                        <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(ind.vwap)}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Signal Reasons */}
                <div style={{ flex: '0 0 200px', minWidth: 160 }}>
                  <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>
                    Signal Reasons
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                    {(sig?.signals ?? sig?.reasons ?? []).slice(0, 6).map((reason, i) => (
                      <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: 6 }}>
                        <ChevronRight size={10} color="#facc15" style={{ marginTop: 2, flexShrink: 0 }} />
                        <span style={{ fontSize: 10, color: 'var(--text-dim)', lineHeight: 1.4 }}>{reason}</span>
                      </div>
                    ))}
                    {(!sig?.signals?.length && !sig?.reasons?.length) && (
                      <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>No signal data</span>
                    )}
                  </div>
                  <div style={{ marginTop: 12 }}>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Trend</div>
                    <span style={{
                      fontFamily: MONO,
                      fontSize: 10,
                      fontWeight: 700,
                      background: sig?.trend === 'uptrend' ? 'rgba(34,197,94,0.12)' : sig?.trend === 'downtrend' ? 'rgba(239,68,68,0.12)' : 'rgba(250,204,21,0.12)',
                      color: sig?.trend === 'uptrend' ? '#22c55e' : sig?.trend === 'downtrend' ? '#ef4444' : '#facc15',
                      borderRadius: 5,
                      padding: '3px 8px',
                    }}>
                      {(sig?.trend ?? 'SIDEWAYS').toUpperCase()}
                    </span>
                  </div>
                </div>
              </div>
            </Card>

            {/* Company Info */}
            {(fund?.sector || fund?.market_cap) && (
              <Card>
                <SectionHeader icon={Building2} label="Company Information" />
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(140px,1fr))', gap: 12 }}>
                  {[
                    { label: 'Sector', val: fund.sector },
                    { label: 'Industry', val: fund.industry },
                    { label: 'Market Cap', val: fmtMktCap(fund.market_cap) },
                    { label: 'P/E Ratio', val: fund.pe_ratio?.toFixed(2) },
                    { label: 'P/B Ratio', val: fund.pb_ratio?.toFixed(2) },
                    { label: 'Div Yield', val: fund.dividend_yield ? fund.dividend_yield.toFixed(2) + '%' : null },
                  ].map(({ label, val }) => val ? (
                    <div key={label}>
                      <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 3 }}>{label}</div>
                      <div style={{ fontFamily: MONO, fontSize: 12, color: 'var(--text-primary)', fontWeight: 600 }}>{val}</div>
                    </div>
                  ) : null)}
                </div>
                {fund['52w_high'] && fund['52w_low'] && (
                  <div style={{ marginTop: 14 }}>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>52-Week Range</div>
                    <DayRangeBar low={fund['52w_low']} high={fund['52w_high']} current={signal?.price ?? ((fund['52w_low'] + fund['52w_high']) / 2)} />
                  </div>
                )}
              </Card>
            )}
          </>
        )}
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // TAB: SMC
  // ═══════════════════════════════════════════════════════════════════════════
  const renderSMC = () => {
    const smc = smcData?.smc ?? smcData ?? {};
    const entry = smc?.entry_signal ?? {};
    const ms = smc?.market_structure ?? {};
    const obs = smc?.order_blocks ?? {};
    const fvgs = smc?.fair_value_gaps ?? [];
    const liq = smc?.liquidity ?? {};
    const timeCtx = smcData?.time_context ?? smc?.time_context ?? {};
    const confScore = smc?.confluence_score ?? entry?.score ?? 50;

    return (
      <div>
        {/* Stock + Interval Selector (reuse) */}
        <Card style={{ marginBottom: 14 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
            <span style={{ fontFamily: MONO, fontSize: 13, fontWeight: 800, color: '#facc15' }}>{selectedStock}</span>
            <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>SMC Analysis</span>
            <div style={{ display: 'flex', gap: 4, marginLeft: 'auto' }}>
              {INTERVALS.map((iv) => (
                <button
                  key={iv}
                  onClick={() => setActiveInterval(iv)}
                  style={{
                    fontFamily: MONO, fontSize: 10, fontWeight: 600,
                    background: activeInterval === iv ? 'rgba(250,204,21,0.15)' : 'transparent',
                    color: activeInterval === iv ? '#facc15' : 'var(--text-dim)',
                    border: `1px solid ${activeInterval === iv ? '#facc1555' : 'transparent'}`,
                    borderRadius: 5, padding: '3px 8px', cursor: 'pointer',
                  }}
                >
                  {iv}
                </button>
              ))}
            </div>
          </div>
        </Card>

        {loading.smc ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {[1,2,3,4].map((k) => <Skeleton key={k} height={100} radius={14} />)}
          </div>
        ) : errors.smc ? (
          <Card style={{ textAlign: 'center', padding: 32 }}>
            <AlertTriangle size={28} color="#ef4444" style={{ margin: '0 auto 8px' }} />
            <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 10 }}>{errors.smc}</div>
            <button onClick={() => fetchSMC()} style={{ fontFamily: MONO, fontSize: 11, background: '#facc15', color: '#000', border: 'none', borderRadius: 8, padding: '6px 16px', cursor: 'pointer', fontWeight: 700 }}>Retry</button>
          </Card>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill,minmax(300px,1fr))', gap: 12 }}>

            {/* Market Structure */}
            <Card>
              <SectionHeader icon={Activity} label="Market Structure" />
              <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                <span style={{
                  fontFamily: MONO, fontSize: 11, fontWeight: 700,
                  background: ms.trend === 'bullish' ? 'rgba(34,197,94,0.12)' : ms.trend === 'bearish' ? 'rgba(239,68,68,0.12)' : 'rgba(250,204,21,0.12)',
                  color: ms.trend === 'bullish' ? '#22c55e' : ms.trend === 'bearish' ? '#ef4444' : '#facc15',
                  borderRadius: 6, padding: '3px 10px',
                }}>
                  {(ms.trend ?? 'NEUTRAL').toUpperCase()}
                </span>
                <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>{ms.swing_direction ?? ''}</span>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {(ms.recent_events ?? ms.events ?? []).slice(0, 5).map((ev, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: 'var(--bg-panel)', borderRadius: 6 }}>
                    <span style={{
                      fontFamily: MONO, fontSize: 10, fontWeight: 700,
                      color: ev.type === 'BOS' ? '#22c55e' : ev.type === 'CHOCH' ? '#facc15' : 'var(--text-dim)',
                    }}>
                      {ev.type ?? '—'}
                    </span>
                    <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(ev.price)}</span>
                    <span style={{ fontSize: 9, color: 'var(--text-dim)' }}>{ev.direction ?? ''}</span>
                  </div>
                ))}
                {!(ms.recent_events ?? ms.events)?.length && (
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>No structure events</span>
                )}
              </div>
            </Card>

            {/* Order Blocks */}
            <Card>
              <SectionHeader icon={Target} label="Order Blocks" />
              {[['Bullish OBs', obs.bullish ?? [], '#22c55e'], ['Bearish OBs', obs.bearish ?? [], '#ef4444']].map(([label, list, color]) => (
                <div key={label} style={{ marginBottom: 10 }}>
                  <div style={{ fontSize: 9, color, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5, fontWeight: 700 }}>{label}</div>
                  {list.slice(0, 3).map((ob, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '4px 8px', background: `${color}11`, borderRadius: 6, marginBottom: 3, border: `1px solid ${color}22` }}>
                      <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(ob.high)} – {fmtPrice(ob.low)}</span>
                      <span style={{
                        fontSize: 8, fontFamily: MONO, fontWeight: 700,
                        color: ob.fresh ? color : 'var(--text-dim)',
                        background: ob.fresh ? `${color}22` : 'transparent',
                        borderRadius: 3, padding: '1px 5px',
                      }}>
                        {ob.fresh ? 'FRESH' : 'TESTED'}
                      </span>
                    </div>
                  ))}
                  {!list.length && <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>None detected</span>}
                </div>
              ))}
            </Card>

            {/* Fair Value Gaps */}
            <Card>
              <SectionHeader icon={BarChart2} label="Fair Value Gaps" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {(Array.isArray(fvgs) ? fvgs : []).slice(0, 6).map((fvg, i) => (
                  <div key={i} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '5px 8px', background: 'var(--bg-panel)', borderRadius: 6 }}>
                    <div>
                      <span style={{ fontFamily: MONO, fontSize: 10, color: fvg.type === 'bullish' ? '#22c55e' : '#ef4444' }}>
                        {fmtPrice(fvg.high)} – {fmtPrice(fvg.low)}
                      </span>
                    </div>
                    <span style={{
                      fontSize: 8, fontFamily: MONO, fontWeight: 700,
                      color: fvg.filled ? 'var(--text-dim)' : '#facc15',
                      background: fvg.filled ? 'rgba(255,255,255,0.05)' : 'rgba(250,204,21,0.12)',
                      borderRadius: 3, padding: '1px 6px',
                    }}>
                      {fvg.filled ? 'FILLED' : 'OPEN'}
                    </span>
                  </div>
                ))}
                {!fvgs.length && <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>No FVGs detected</span>}
              </div>
            </Card>

            {/* Liquidity */}
            <Card>
              <SectionHeader icon={Shield} label="Liquidity Pools" />
              {[['Buy-Side', liq.buy_side ?? [], '#22c55e'], ['Sell-Side', liq.sell_side ?? [], '#ef4444']].map(([label, pools, color]) => (
                <div key={label} style={{ marginBottom: 10 }}>
                  <div style={{ fontSize: 9, color, textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5, fontWeight: 700 }}>{label}</div>
                  {(Array.isArray(pools) ? pools : []).slice(0, 3).map((p, i) => (
                    <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 8px', background: `${color}0d`, borderRadius: 6, marginBottom: 3 }}>
                      <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-primary)' }}>{fmtPrice(p.price ?? p.level)}</span>
                      <span style={{ fontSize: 9, color: 'var(--text-dim)' }}>{p.strength ?? p.type ?? ''}</span>
                    </div>
                  ))}
                  {!(Array.isArray(pools) ? pools : []).length && <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>None</span>}
                </div>
              ))}
            </Card>

            {/* Entry Signal */}
            <Card style={{ gridColumn: 'span 2' }}>
              <SectionHeader icon={Zap} label="Entry Signal — OTE" />
              {Object.keys(entry).length ? (
                <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'flex-start' }}>
                  <div style={{ flex: '0 0 auto' }}>
                    <ScoreCircle score={confScore} />
                    <div style={{ textAlign: 'center', marginTop: 6 }}>
                      <ActionBadge action={entry.action ?? entry.signal ?? 'HOLD'} score={confScore} />
                    </div>
                  </div>
                  <div style={{ flex: 1, minWidth: 200, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                    {[
                      ['Entry', entry.entry ?? entry.entry_price],
                      ['Stop Loss', entry.sl ?? entry.stop_loss],
                      ['TP1', entry.tp1 ?? entry.take_profit_1],
                      ['TP2', entry.tp2 ?? entry.take_profit_2],
                      ['R:R', entry.rr ?? entry.risk_reward],
                      ['OTE Zone', entry.ote_low && entry.ote_high ? `${fmtPrice(entry.ote_low)}–${fmtPrice(entry.ote_high)}` : null],
                    ].map(([label, val]) => val != null ? (
                      <div key={label} style={{ background: 'var(--bg-panel)', borderRadius: 8, padding: 10 }}>
                        <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 3 }}>{label}</div>
                        <div style={{ fontFamily: MONO, fontSize: 13, fontWeight: 700, color: label === 'Stop Loss' ? '#ef4444' : label.startsWith('TP') ? '#22c55e' : label === 'R:R' ? '#facc15' : 'var(--text-primary)' }}>
                          {typeof val === 'number' ? fmtPrice(val) : val}
                        </div>
                      </div>
                    ) : null)}
                  </div>
                  <div style={{ flex: '0 0 auto', minWidth: 160 }}>
                    <div style={{ fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: 6 }}>Confluence</div>
                    <div style={{ position: 'relative', height: 8, background: 'var(--bg-panel)', borderRadius: 4, overflow: 'hidden' }}>
                      <div style={{ width: `${confScore}%`, height: '100%', background: signalColor(confScore), borderRadius: 4, transition: 'width 0.5s ease' }} />
                    </div>
                    <div style={{ fontFamily: MONO, fontSize: 20, fontWeight: 800, color: signalColor(confScore), marginTop: 6 }}>{confScore}</div>
                  </div>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: 20 }}>
                  <Minus size={20} color="var(--text-dim)" style={{ margin: '0 auto 6px' }} />
                  <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>No entry signal available</span>
                </div>
              )}
            </Card>

            {/* Time Context */}
            <Card>
              <SectionHeader icon={Clock} label="Time Context" />
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--bg-panel)', borderRadius: 8 }}>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>Session</span>
                  <span style={{ fontFamily: MONO, fontSize: 11, fontWeight: 700, color: '#facc15' }}>{timeCtx.session ?? 'N/A'}</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--bg-panel)', borderRadius: 8 }}>
                  <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>AMD Phase</span>
                  <span style={{ fontFamily: MONO, fontSize: 11, fontWeight: 700, color: timeCtx.amd_phase === 'Accumulation' ? '#22c55e' : timeCtx.amd_phase === 'Distribution' ? '#ef4444' : '#facc15' }}>
                    {timeCtx.amd_phase ?? 'Unknown'}
                  </span>
                </div>
                {timeCtx.market_open != null && (
                  <div style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 10px', background: 'var(--bg-panel)', borderRadius: 8 }}>
                    <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>Market</span>
                    <span style={{ fontFamily: MONO, fontSize: 11, fontWeight: 700, color: timeCtx.market_open ? '#22c55e' : '#ef4444' }}>
                      {timeCtx.market_open ? 'OPEN' : 'CLOSED'}
                    </span>
                  </div>
                )}
              </div>
            </Card>
          </div>
        )}
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // TAB: SCANNER
  // ═══════════════════════════════════════════════════════════════════════════
  const renderScanner = () => {
    const subTabs = [
      { id: 'gainers', label: 'Top Gainer', data: scanner.gainers, color: '#22c55e' },
      { id: 'losers',  label: 'Top Loser',  data: scanner.losers,  color: '#ef4444' },
      { id: 'active',  label: 'Most Active', data: scanner.active, color: '#facc15' },
    ];
    const active = subTabs.find((t) => t.id === scannerTab);
    const rows = active?.data ?? [];

    return (
      <div>
        {/* Sub-tab bar */}
        <div style={{ display: 'flex', gap: 6, marginBottom: 14 }}>
          {subTabs.map(({ id, label, color }) => (
            <button
              key={id}
              onClick={() => setScannerTab(id)}
              style={{
                fontFamily: MONO, fontSize: 11, fontWeight: 700,
                background: scannerTab === id ? '#facc15' : 'var(--bg-card)',
                color: scannerTab === id ? '#000' : 'var(--text-dim)',
                border: `1px solid ${scannerTab === id ? '#facc15' : 'var(--border-color)'}`,
                borderRadius: 20, padding: '5px 16px', cursor: 'pointer',
              }}
            >
              {label}
            </button>
          ))}
        </div>

        {loading.scanner ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {[...Array(8)].map((_, i) => <Skeleton key={i} height={44} radius={8} />)}
          </div>
        ) : errors.scanner ? (
          <Card style={{ textAlign: 'center', padding: 32 }}>
            <AlertTriangle size={28} color="#ef4444" style={{ margin: '0 auto 8px' }} />
            <div style={{ color: '#ef4444', fontSize: 13, marginBottom: 10 }}>{errors.scanner}</div>
            <button onClick={fetchScanner} style={{ fontFamily: MONO, fontSize: 11, background: '#facc15', color: '#000', border: 'none', borderRadius: 8, padding: '6px 16px', cursor: 'pointer', fontWeight: 700 }}>Retry</button>
          </Card>
        ) : rows.length === 0 ? (
          <Card style={{ textAlign: 'center', padding: 32 }}>
            <Star size={24} color="var(--text-dim)" style={{ margin: '0 auto 8px' }} />
            <span style={{ fontSize: 12, color: 'var(--text-dim)' }}>No data available</span>
          </Card>
        ) : (
          <Card style={{ padding: 0, overflow: 'hidden' }}>
            {/* Table header */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: '40px 1fr 120px 100px 100px 100px',
              padding: '10px 16px',
              background: 'var(--bg-panel)',
              borderBottom: '1px solid var(--border-color)',
              gap: 8,
            }}>
              {['#', 'Symbol', 'Price', 'Change %', 'Volume', 'Action'].map((h) => (
                <span key={h} style={{ fontFamily: MONO, fontSize: 9, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>{h}</span>
              ))}
            </div>
            {rows.map((row, i) => {
              const pct = row.change_pct ?? row.changesPercentage ?? row.pct_change ?? 0;
              return (
                <div
                  key={row.symbol ?? i}
                  style={{
                    display: 'grid',
                    gridTemplateColumns: '40px 1fr 120px 100px 100px 100px',
                    padding: '10px 16px',
                    borderBottom: '1px solid var(--border-color)',
                    gap: 8,
                    alignItems: 'center',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.background = 'var(--bg-panel)'}
                  onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                >
                  <span style={{ fontFamily: MONO, fontSize: 11, color: 'var(--text-dim)' }}>{i + 1}</span>
                  <div>
                    <div style={{ fontFamily: MONO, fontSize: 13, fontWeight: 800, color: 'var(--text-primary)' }}>{row.symbol}</div>
                    {row.name && <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 1 }}>{row.name}</div>}
                  </div>
                  <span style={{ fontFamily: MONO, fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>
                    {fmtPrice(row.price ?? row.last)}
                  </span>
                  <span style={{
                    fontFamily: MONO, fontSize: 12, fontWeight: 700,
                    color: changePctColor(pct),
                    background: pct > 0 ? 'rgba(34,197,94,0.1)' : pct < 0 ? 'rgba(239,68,68,0.1)' : 'transparent',
                    borderRadius: 5, padding: '2px 6px', display: 'inline-block',
                  }}>
                    {fmtPct(pct)}
                  </span>
                  <span style={{ fontFamily: MONO, fontSize: 11, color: 'var(--text-dim)' }}>
                    {fmtVol(row.volume)}
                  </span>
                  <button
                    onClick={() => handleSelectStock(row.symbol)}
                    style={{
                      fontFamily: MONO, fontSize: 10, fontWeight: 700,
                      background: 'rgba(250,204,21,0.1)',
                      color: '#facc15',
                      border: '1px solid #facc1544',
                      borderRadius: 6, padding: '4px 10px', cursor: 'pointer',
                      display: 'flex', alignItems: 'center', gap: 4,
                      transition: 'all 0.15s',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.background = '#facc15'; e.currentTarget.style.color = '#000'; }}
                    onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(250,204,21,0.1)'; e.currentTarget.style.color = '#facc15'; }}
                  >
                    Analisa <ChevronRight size={10} />
                  </button>
                </div>
              );
            })}
          </Card>
        )}
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // TAB: CHART
  // ═══════════════════════════════════════════════════════════════════════════
  const renderChart = () => {
    const filtered = chartSector === 'Semua'
      ? IDX_TV_PAIRS
      : IDX_TV_PAIRS.filter((p) => p.sector === chartSector);
    const active = IDX_TV_PAIRS.find((p) => p.sym === chartSymbol);
    return (
      <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
        {/* Symbol + Interval row */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ fontFamily: MONO, fontSize: 15, fontWeight: 800, color: '#facc15' }}>{active?.label ?? chartSymbol}</span>
            <span style={{ fontSize: 9, color: 'var(--text-dim)', maxWidth: 200, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{active?.name}</span>
            <span style={{ fontSize: 9, padding: '2px 7px', borderRadius: 4, background: 'rgba(250,204,21,0.12)', color: '#facc15', border: '1px solid #facc1444', fontFamily: MONO }}>IDX</span>
          </div>
          <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
            {TV_INTERVALS.map((iv) => (
              <button key={iv.value} onClick={() => setChartInterval(iv.value)} style={{
                padding: '4px 10px', borderRadius: 6, fontSize: 10, fontWeight: 700, cursor: 'pointer',
                border: '1px solid',
                borderColor: chartInterval === iv.value ? '#facc15' : 'var(--border-color)',
                background: chartInterval === iv.value ? 'rgba(250,204,21,0.15)' : 'var(--bg-card)',
                color: chartInterval === iv.value ? '#facc15' : 'var(--text-dim)',
                fontFamily: MONO,
              }}>{iv.label}</button>
            ))}
          </div>
        </div>

        {/* Sector filter */}
        <div style={{ display: 'flex', gap: 5, flexWrap: 'wrap' }}>
          {CHART_SECTORS.map((s) => (
            <button key={s} onClick={() => setChartSector(s)} style={{
              padding: '3px 10px', borderRadius: 10, fontSize: 9, fontWeight: 700, cursor: 'pointer',
              border: '1px solid',
              borderColor: chartSector === s ? '#facc15' : 'var(--border-color)',
              background: chartSector === s ? 'rgba(250,204,21,0.15)' : 'var(--bg-panel)',
              color: chartSector === s ? '#facc15' : 'var(--text-dim)',
            }}>{s}</button>
          ))}
        </div>

        {/* Pair chips — horizontal scroll */}
        <div style={{ display: 'flex', gap: 6, overflowX: 'auto', paddingBottom: 4, scrollbarWidth: 'none' }}>
          {filtered.map((p) => (
            <button key={p.sym} onClick={() => setChartSymbol(p.sym)} style={{
              flexShrink: 0, padding: '5px 13px', borderRadius: 8, cursor: 'pointer',
              border: '1px solid',
              borderColor: chartSymbol === p.sym ? '#facc15' : 'var(--border-color)',
              background: chartSymbol === p.sym ? 'rgba(250,204,21,0.15)' : 'var(--bg-card)',
              color: chartSymbol === p.sym ? '#facc15' : 'var(--text-primary)',
              fontFamily: MONO, fontSize: 11, fontWeight: 700,
              boxShadow: chartSymbol === p.sym ? '0 0 12px rgba(250,204,21,0.3)' : 'none',
              transition: 'all 0.15s',
            }}>{p.label}</button>
          ))}
        </div>

        {/* TradingView Chart */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-color)',
          borderRadius: 16,
          overflow: 'hidden',
          height: 560,
        }}>
          <IDXTVChart symbol={chartSymbol} interval={chartInterval} />
        </div>

        {/* Info bar */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: 8, padding: '8px 14px',
          background: 'var(--bg-card)', border: '1px solid var(--border-color)',
          borderRadius: 10, fontSize: 9, color: 'var(--text-dim)', fontFamily: MONO,
        }}>
          <span style={{ color: '#facc15' }}>★</span>
          <span>Data realtime dari TradingView · IDX Bursa Efek Indonesia · Zona waktu WIB (UTC+7)</span>
          <span style={{ marginLeft: 'auto', color: 'var(--text-dim)' }}>51 pair IDX tersedia</span>
        </div>
      </div>
    );
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // RENDER
  // ═══════════════════════════════════════════════════════════════════════════
  return (
    <div style={styles.container}>
      {/* Market Tab Bar */}
      <div className="mkt-tab-wrap">
        {TABS.map(tab => (
          <button key={tab.id} className={`mkt-tab-btn${gasTab === tab.id ? ' mkt-tab-btn--on' : ''}`} onClick={() => setGasTab(tab.id)}>
            <i className={tab.icon} />{tab.label}
          </button>
        ))}
      </div>

      {gasTab === 'Data' && (
        <div className="space-y-4 p-4">
          <div className="ai-insight-card">
            <h4>📊 IDX Market Data</h4>
            <p className="ai-insight-text">Live IHSG and stock data — OHLCV, broker summary, sector rotation, and institutional flow tracking for IDX-listed stocks.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">IDX Live Feed</span>
              <span className="ai-badge">Broker Summary</span>
              <span className="ai-badge">Sector Rotation</span>
            </div>
          </div>
        </div>
      )}

      {gasTab === 'AI Insight' && (
        <div className="space-y-4 p-4">
          <div className="ai-insight-card">
            <h4>🧠 IDX AI Intelligence</h4>
            <p className="ai-insight-text">AI tracks smart accumulation patterns, big money flow, sector strength, and generates top AI picks from IDX-listed stocks with full reasoning.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">Smart Accumulation</span>
              <span className="ai-badge ai-badge--green">Big Money Flow</span>
              <span className="ai-badge">Top Picks</span>
            </div>
          </div>
        </div>
      )}

      {(gasTab === 'Overview' || gasTab === 'Signals' || gasTab === 'Technical' || gasTab === 'Session') && (<>
      {/* Mode Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)] mb-3">
        {[
          { id: 'auto',     label: '📡 Auto Signal',  desc: 'Background AI' },
          { id: 'manual',   label: '🎯 Manual Signal', desc: 'On Demand' },
          { id: 'analysis', label: '🧠 Analysis',      desc: 'Market Intel' },
        ].map(tab => (
          <button key={tab.id}
            onClick={() => setMode(tab.id)}
            className={`flex-1 py-2 px-2 rounded-lg text-[9px] font-black transition-all flex flex-col items-center gap-0.5
              ${mode === tab.id
                ? 'bg-[var(--accent)] text-black shadow-lg'
                : 'text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)]'
              }`}
          >
            <span className="text-[11px]">{tab.label.split(' ')[0]}</span>
            <span>{tab.label.split(' ').slice(1).join(' ')}</span>
            <span className={`text-[7px] font-normal ${mode === tab.id ? 'text-black/60' : 'opacity-50'}`}>{tab.desc}</span>
          </button>
        ))}
      </div>

      {mode === 'auto' && (
        <div className="space-y-3 p-4">
          <AutoSignalPanel market="stock" planDepth="essential" />
        </div>
      )}

      {mode === 'analysis' && (
        <div className="space-y-3 p-4">
          <MarketAnalysisPanel market="stock" planDepth="essential" />
        </div>
      )}

      {mode === 'manual' && (<>
      {/* Header */}
      <div style={styles.header}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <Building2 size={18} color="#facc15" />
          <div>
            <div style={{ fontFamily: MONO, fontSize: 14, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: '0.04em' }}>
              IDX STOCK AI
            </div>
            <div style={{ fontFamily: MONO, fontSize: 9, color: 'var(--text-dim)', marginTop: 1 }}>
              Bursa Efek Indonesia · AI-Powered Analysis
            </div>
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          {/* Auto-refresh toggle */}
          <button
            onClick={() => setAutoRefresh((p) => !p)}
            title="Auto-refresh every 30s"
            style={{
              display: 'flex', alignItems: 'center', gap: 6,
              fontFamily: MONO, fontSize: 10, fontWeight: 600,
              background: autoRefresh ? 'rgba(250,204,21,0.12)' : 'var(--bg-card)',
              color: autoRefresh ? '#facc15' : 'var(--text-dim)',
              border: `1px solid ${autoRefresh ? '#facc1555' : 'var(--border-color)'}`,
              borderRadius: 8, padding: '5px 12px', cursor: 'pointer',
            }}
          >
            <RefreshCw size={11} style={{ animation: autoRefresh ? 'spin 2s linear infinite' : 'none' }} />
            Auto
          </button>

          {/* Manual refresh */}
          <button
            onClick={() => { fetchIHSG(); fetchTickers(); }}
            style={{
              display: 'flex', alignItems: 'center', gap: 4,
              fontFamily: MONO, fontSize: 10,
              background: 'var(--bg-card)',
              color: 'var(--text-dim)',
              border: '1px solid var(--border-color)',
              borderRadius: 8, padding: '5px 10px', cursor: 'pointer',
            }}
          >
            <RefreshCw size={11} />
          </button>
        </div>
      </div>

      {/* Tab Bar */}
      <div style={styles.tabBar}>
        {[
          { id: 'chart',   label: '📊 Chart' },
          { id: 'pasar',   label: 'Pasar' },
          { id: 'analisa', label: 'Analisa' },
          { id: 'smc',     label: 'SMC' },
          { id: 'scanner', label: 'Scanner' },
        ].map(({ id, label }) => (
          <button key={id} style={styles.tab(tab === id)} onClick={() => setTab(id)}>
            {label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={styles.content}>
        {tab === 'chart'   && renderChart()}
        {tab === 'pasar'   && renderPasar()}
        {tab === 'analisa' && renderAnalisa()}
        {tab === 'smc'     && renderSMC()}
        {tab === 'scanner' && renderScanner()}
      </div>

      {/* Spin animation */}
      <style>{`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}</style>
      </>)}
      </>)}
    </div>
  );
}

// ── Ticker Card ───────────────────────────────────────────────────────────────
function TickerCard({ ticker, onSelect, selected }) {
  const pct = ticker.change_pct ?? ticker.changesPercentage ?? 0;
  const isUp = pct >= 0;
  const price = ticker.price ?? ticker.last ?? ticker.close;
  const low = ticker.day_low ?? ticker.low;
  const high = ticker.day_high ?? ticker.high;
  const vol = ticker.volume;

  return (
    <div
      onClick={() => onSelect(ticker.symbol)}
      style={{
        background: 'var(--bg-card)',
        border: `1px solid ${selected ? '#facc1566' : 'var(--border-color)'}`,
        borderRadius: 14,
        padding: 14,
        cursor: 'pointer',
        transition: 'all 0.18s',
        boxShadow: selected ? '0 0 0 1px #facc1533' : 'none',
      }}
      onMouseEnter={(e) => { if (!selected) e.currentTarget.style.borderColor = 'rgba(250,204,21,0.3)'; }}
      onMouseLeave={(e) => { if (!selected) e.currentTarget.style.borderColor = 'var(--border-color)'; }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 8 }}>
        <div>
          <div style={{ fontFamily: MONO, fontSize: 14, fontWeight: 800, color: 'var(--text-primary)' }}>{ticker.symbol}</div>
          <div style={{ fontSize: 9, color: 'var(--text-dim)', marginTop: 1, maxWidth: 110, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
            {ticker.name ?? ticker.shortName ?? ''}
          </div>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 3 }}>
          {isUp ? <ArrowUp size={11} color="#22c55e" /> : <ArrowDown size={11} color="#ef4444" />}
          <span style={{ fontFamily: MONO, fontSize: 11, fontWeight: 700, color: changePctColor(pct) }}>
            {fmtPct(pct)}
          </span>
        </div>
      </div>

      <div style={{ fontFamily: MONO, fontSize: 18, fontWeight: 800, color: isUp ? '#22c55e' : '#ef4444', marginBottom: 8 }}>
        {fmtPrice(price)}
      </div>

      {low != null && high != null && price != null && (
        <DayRangeBar low={low} high={high} current={price} />
      )}

      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8, alignItems: 'center' }}>
        <span style={{ fontSize: 9, color: 'var(--text-dim)' }}>Vol</span>
        <span style={{ fontFamily: MONO, fontSize: 10, color: 'var(--text-dim)' }}>{fmtVol(vol)}</span>
      </div>
    </div>
  );
}
