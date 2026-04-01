import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, Zap, BarChart2, Globe, RefreshCw, ArrowRight } from 'lucide-react';
import { fetchBinanceTicker } from '../services/api';

// ── Mode card definitions ──────────────────────────────────────────────────────
const MODES = [
  {
    id: 'forex_ai',
    icon: '💱',
    title: 'FOREX AI',
    subtitle: 'MT5 · Exness · Gold · Indices',
    desc: 'TA + FA combined · Session-aware signals',
    color: '#f59e0b',
    gradient: 'from-[#f59e0b]/20 to-[#f59e0b]/5',
    borderHover: '#f59e0b',
    badge: 'LIVE',
    btnLabel: 'Enter Forex AI',
    pricePair: 'XAUUSD',
    priceLabel: 'XAUUSD',
  },
  {
    id: 'binance_ai',
    icon: '₿',
    title: 'BINANCE AI',
    subtitle: 'Crypto · Spot · Futures',
    desc: 'Volume + Momentum analysis',
    color: '#f7931a',
    gradient: 'from-[#f7931a]/20 to-[#f7931a]/5',
    borderHover: '#f7931a',
    badge: 'LIVE',
    btnLabel: 'Enter Binance AI',
    pricePair: 'btcLive',
    priceLabel: 'BTC/USDT',
  },
  {
    id: 'polymarket',
    icon: '🔮',
    title: 'POLYMARKET',
    subtitle: 'Prediction Markets · YES/NO',
    desc: '4-model weighted consensus · Ultra plan',
    color: '#6366f1',
    gradient: 'from-[#6366f1]/20 to-[#6366f1]/5',
    borderHover: '#6366f1',
    badge: 'NEW',
    btnLabel: 'Enter Polymarket',
    pricePair: null,
    priceLabel: null,
  },
  {
    id: 'memecoin',
    icon: '🎰',
    title: 'MEMECOIN',
    subtitle: 'Dexscreener · Anti-Rug · Multi-Chain',
    desc: 'BUY EARLY detection · Premium plan',
    color: '#9945ff',
    gradient: 'from-[#9945ff]/20 to-[#9945ff]/5',
    borderHover: '#9945ff',
    badge: 'HOT',
    btnLabel: 'Enter Memecoin',
    pricePair: null,
    priceLabel: null,
  },
  {
    id: 'stock_idx',
    icon: '🏦',
    title: 'STOCK IDX AI',
    subtitle: 'BEI · Saham Indonesia · AI Analysis',
    desc: 'Technical + SMC + Scanner · 100+ saham IDX',
    color: '#10b981',
    gradient: 'from-[#10b981]/20 to-[#10b981]/5',
    borderHover: '#10b981',
    badge: 'NEW',
    btnLabel: 'Enter Stock IDX',
    pricePair: null,
    priceLabel: 'IHSG',
  },
];

// ── Market pulse pairs ─────────────────────────────────────────────────────────
const PULSE_PAIRS = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'GBPJPY', 'AUDUSD'];

const STATS = [
  { label: 'AI Features',  value: '22',          icon: Zap,      color: '#f59e0b' },
  { label: 'Active Models', value: '4 AI',        icon: Activity, color: '#3b82f6' },
  { label: 'Live Markets',  value: 'MT5+BNB+IDX', icon: Globe,    color: '#10b981' },
  { label: 'Uptime',        value: '99.9%',        icon: BarChart2,color: '#8b5cf6' },
];

function formatPrice(price, symbol) {
  if (!price || isNaN(price)) return '--';
  if (symbol === 'XAUUSD' || price > 1000) return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (price < 1) return price.toFixed(5);
  return price.toFixed(4);
}

function formatIDXPrice(price) {
  if (!price || isNaN(price)) return '--';
  return Number(price).toLocaleString('id-ID', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

function formatIDXChange(val) {
  if (val === null || val === undefined || isNaN(val)) return null;
  return Number(val);
}

// ── Mode Card ─────────────────────────────────────────────────────────────────
function ModeCard({ mode, isActive, prices, btcPrice, ihsgPrice, onClick }) {
  const [hovered, setHovered] = useState(false);

  const livePrice = mode.pricePair === 'btcLive'
    ? btcPrice
    : mode.pricePair
      ? (prices[mode.pricePair] || 0)
      : null;

  return (
    <div
      className={`relative rounded-2xl border p-5 cursor-pointer transition-all duration-300 bg-gradient-to-br ${mode.gradient} overflow-hidden`}
      style={{
        borderColor: hovered || isActive ? mode.color : 'var(--border-color)',
        boxShadow: hovered || isActive ? `0 0 24px ${mode.color}30` : 'none',
      }}
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={() => onClick(mode.id)}
    >
      {/* Active indicator */}
      {isActive && (
        <div className="absolute top-3 right-3 w-2 h-2 rounded-full animate-pulse" style={{ background: mode.color }} />
      )}

      {/* Badge */}
      <div className="flex items-center justify-between mb-4">
        <div className="text-3xl font-black" style={{ color: mode.color }}>{mode.icon}</div>
        <span
          className="text-[8px] font-black px-2 py-0.5 rounded-full"
          style={{ background: `${mode.color}25`, color: mode.color }}
        >
          {mode.badge}
        </span>
      </div>

      {/* Title */}
      <div className="text-base font-black text-[var(--text-primary)] mb-0.5">{mode.title}</div>
      <div className="text-[9px] font-bold text-[var(--text-dim)] uppercase tracking-widest mb-2">{mode.subtitle}</div>
      <div className="text-[10px] text-[var(--text-secondary)] mb-4 leading-relaxed">{mode.desc}</div>

      {/* Live price snippet */}
      {mode.id === 'stock_idx' && ihsgPrice ? (
        <div className="mb-4 flex items-center gap-2">
          <span className="text-[9px] text-[var(--text-dim)] font-bold">IHSG</span>
          <span className="text-sm font-black font-mono" style={{ color: mode.color }}>
            {formatIDXPrice(ihsgPrice)}
          </span>
        </div>
      ) : mode.priceLabel && mode.id !== 'stock_idx' ? (
        <div className="mb-4 flex items-center gap-2">
          <span className="text-[9px] text-[var(--text-dim)] font-bold">{mode.priceLabel}</span>
          <span className="text-sm font-black font-mono" style={{ color: mode.color }}>
            {mode.pricePair === 'btcLive'
              ? (btcPrice ? `$${btcPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}` : '--')
              : (livePrice ? formatPrice(livePrice, mode.pricePair) : '--')
            }
          </span>
        </div>
      ) : null}

      {/* CTA button */}
      <button
        className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl text-[10px] font-black uppercase tracking-widest transition-all"
        style={{ background: `${mode.color}20`, color: mode.color }}
        onMouseEnter={e => { e.currentTarget.style.background = `${mode.color}35`; }}
        onMouseLeave={e => { e.currentTarget.style.background = `${mode.color}20`; }}
      >
        <ArrowRight size={12} /> {mode.btnLabel}
      </button>
    </div>
  );
}

// ── Pulse ticker card ─────────────────────────────────────────────────────────
function PulseCard({ symbol, price, pairs }) {
  const pair = pairs.find(p => p.symbol === symbol);
  const base = pair?.base || price;
  const chg = base ? ((price - base) / base * 100) : 0;
  const isUp = chg >= 0;
  return (
    <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-3 py-2 min-w-[110px]">
      <div className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-wide">{symbol}</div>
      <div className={`text-xs font-black font-mono ${isUp ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
        {price ? formatPrice(price, symbol) : '--'}
      </div>
      <div className={`text-[8px] font-bold ${isUp ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
        {isUp ? '+' : ''}{chg.toFixed(3)}%
      </div>
    </div>
  );
}

// ── IDX Stock Mini-Card ────────────────────────────────────────────────────────
function IDXStockCard({ stock }) {
  const chg = formatIDXChange(stock.change_pct);
  const isUp = chg !== null ? chg >= 0 : null;
  const accentColor = isUp === null ? '#6b7280' : isUp ? '#10b981' : '#f43f5e';

  // Build a tiny 3-point sparkline using day_low, price, day_high
  const lo = parseFloat(stock.day_low) || 0;
  const hi = parseFloat(stock.day_high) || 0;
  const cur = parseFloat(stock.price) || 0;
  const range = hi - lo || 1;
  const w = 52, h = 22;
  // Map points: x0=lo at left, x1=cur at mid, x2=hi at right
  // y is inverted (SVG y increases downward)
  const pts = [
    `0,${h}`,                                                  // low  → bottom-left
    `${w / 2},${h - ((cur - lo) / range) * h}`,               // cur  → middle
    `${w},0`,                                                  // high → top-right
  ].join(' ');

  return (
    <div style={{
      minWidth: 110,
      background: 'var(--bg-panel)',
      border: `1px solid ${accentColor}30`,
      borderRadius: 12,
      padding: '10px 12px',
      display: 'flex',
      flexDirection: 'column',
      gap: 4,
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 10, fontWeight: 900, color: '#e2e8f0', letterSpacing: '0.04em' }}>{stock.symbol}</span>
        {isUp !== null && (
          <span style={{ fontSize: 8, fontWeight: 800, color: accentColor }}>
            {isUp ? '▲' : '▼'}
          </span>
        )}
      </div>
      <div style={{ fontSize: 12, fontWeight: 900, fontFamily: 'monospace', color: '#f1f5f9' }}>
        {formatIDXPrice(stock.price)}
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{
          fontSize: 9, fontWeight: 800,
          color: accentColor,
        }}>
          {chg !== null ? `${isUp ? '+' : ''}${chg.toFixed(2)}%` : '--'}
        </span>
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`} style={{ overflow: 'visible' }}>
          <polyline
            points={pts}
            fill="none"
            stroke={accentColor}
            strokeWidth="1.5"
            strokeLinejoin="round"
            strokeLinecap="round"
            opacity="0.8"
          />
        </svg>
      </div>
    </div>
  );
}

// ── IDX Skeleton Card ─────────────────────────────────────────────────────────
function IDXSkeletonCard() {
  return (
    <div style={{
      minWidth: 110,
      background: 'var(--bg-panel)',
      border: '1px solid rgba(16,185,129,0.15)',
      borderRadius: 12,
      padding: '10px 12px',
      display: 'flex',
      flexDirection: 'column',
      gap: 6,
    }}>
      <div style={{ height: 10, width: '60%', background: 'rgba(255,255,255,0.07)', borderRadius: 4 }} />
      <div style={{ height: 14, width: '80%', background: 'rgba(255,255,255,0.05)', borderRadius: 4 }} />
      <div style={{ height: 9, width: '50%', background: 'rgba(255,255,255,0.04)', borderRadius: 4 }} />
    </div>
  );
}

// ── IDX Market Widget ─────────────────────────────────────────────────────────
function IDXMarketWidget({ onSelectMode }) {
  const [ihsg, setIhsg] = useState(null);
  const [stocks, setStocks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const IDX_SYMBOLS = 'BBCA,BBRI,BMRI,TLKM,GOTO,ADRO,BREN,ANTM';

  const fetchIDX = async () => {
    const token = localStorage.getItem('gas-token');
    const headers = token ? { Authorization: `Bearer ${token}` } : {};
    try {
      const [ihsgRes, tickersRes] = await Promise.allSettled([
        fetch('/terminal/idx/ihsg', { headers }),
        fetch(`/terminal/idx/tickers?symbols=${IDX_SYMBOLS}`, { headers }),
      ]);

      if (ihsgRes.status === 'fulfilled' && ihsgRes.value.ok) {
        const data = await ihsgRes.value.json();
        setIhsg(data);
      }

      if (tickersRes.status === 'fulfilled' && tickersRes.value.ok) {
        const data = await tickersRes.value.json();
        // Accept array or object with tickers key
        const list = Array.isArray(data) ? data : (data.tickers || data.data || []);
        setStocks(list);
      }

      setError(null);
    } catch (e) {
      setError('Data tidak tersedia');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchIDX();
    const iv = setInterval(fetchIDX, 60000);
    return () => clearInterval(iv);
  }, []);

  const ihsgChg = ihsg ? formatIDXChange(ihsg.change_pct) : null;
  const ihsgUp = ihsgChg !== null ? ihsgChg >= 0 : null;
  const ihsgColor = ihsgUp === null ? '#94a3b8' : ihsgUp ? '#10b981' : '#f43f5e';

  return (
    <div style={{
      background: 'linear-gradient(135deg, rgba(16,185,129,0.08) 0%, rgba(16,185,129,0.02) 100%)',
      border: '1px solid rgba(16,185,129,0.25)',
      borderRadius: 20,
      padding: '20px 20px 16px',
      position: 'relative',
      overflow: 'hidden',
    }}>
      {/* Subtle glow backdrop */}
      <div style={{
        position: 'absolute', top: -30, right: -30, width: 120, height: 120,
        background: 'radial-gradient(circle, rgba(16,185,129,0.12) 0%, transparent 70%)',
        pointerEvents: 'none',
      }} />

      {/* Section header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          {/* Animated pulse dot */}
          <div style={{ position: 'relative', width: 10, height: 10 }}>
            <div style={{
              position: 'absolute', inset: 0, borderRadius: '50%',
              background: '#10b981', opacity: 0.4,
              animation: 'ping 1.5s cubic-bezier(0,0,0.2,1) infinite',
            }} />
            <div style={{
              position: 'absolute', inset: '20%', borderRadius: '50%',
              background: '#10b981',
            }} />
          </div>
          <span style={{ fontSize: 11, fontWeight: 900, color: '#10b981', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            IDX Market
          </span>
          <span style={{ fontSize: 9, color: '#94a3b8', fontWeight: 700 }}>· Bursa Efek Indonesia</span>
        </div>
        <span style={{
          fontSize: 8, fontWeight: 900, background: 'rgba(16,185,129,0.15)',
          color: '#10b981', padding: '2px 8px', borderRadius: 20, letterSpacing: '0.06em',
        }}>
          LIVE · IDX
        </span>
      </div>

      {/* IHSG Hero Card */}
      {loading ? (
        <div style={{
          background: 'rgba(255,255,255,0.03)', borderRadius: 14, padding: '14px 16px',
          marginBottom: 14, border: '1px solid rgba(16,185,129,0.12)',
        }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <div style={{ height: 12, width: 80, background: 'rgba(255,255,255,0.07)', borderRadius: 4 }} />
            <div style={{ height: 12, width: 50, background: 'rgba(255,255,255,0.05)', borderRadius: 4 }} />
          </div>
          <div style={{ height: 32, width: 160, background: 'rgba(255,255,255,0.06)', borderRadius: 6, marginTop: 8 }} />
          <div style={{ display: 'flex', gap: 8, marginTop: 8 }}>
            {[1,2,3].map(i => (
              <div key={i} style={{ height: 10, width: 70, background: 'rgba(255,255,255,0.04)', borderRadius: 4 }} />
            ))}
          </div>
        </div>
      ) : error && !ihsg ? (
        <div style={{
          background: 'rgba(255,255,255,0.03)', borderRadius: 14, padding: '14px 16px',
          marginBottom: 14, border: '1px solid rgba(255,255,255,0.08)',
          color: '#94a3b8', fontSize: 11, textAlign: 'center',
        }}>
          {error}
        </div>
      ) : ihsg ? (
        <div style={{
          background: 'rgba(16,185,129,0.06)', borderRadius: 14, padding: '14px 16px',
          marginBottom: 14, border: '1px solid rgba(16,185,129,0.18)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
            <span style={{ fontSize: 11, fontWeight: 900, color: '#e2e8f0', letterSpacing: '0.06em' }}>IHSG</span>
            <span style={{
              fontSize: 8, fontWeight: 800, background: 'rgba(16,185,129,0.2)',
              color: '#10b981', padding: '1px 6px', borderRadius: 10,
            }}>IDX:COMPOSITE</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: 12, flexWrap: 'wrap' }}>
            <span style={{ fontSize: 28, fontWeight: 900, fontFamily: 'monospace', color: '#f1f5f9', lineHeight: 1 }}>
              {formatIDXPrice(ihsg.price || ihsg.close || ihsg.last)}
            </span>
            {ihsgChg !== null && (
              <span style={{
                fontSize: 15, fontWeight: 800, color: ihsgColor,
                display: 'flex', alignItems: 'center', gap: 3,
              }}>
                {ihsgUp ? '▲' : '▼'} {ihsgUp ? '+' : ''}{ihsgChg.toFixed(2)}%
              </span>
            )}
          </div>
          {/* Open/High/Low row */}
          <div style={{ display: 'flex', gap: 16, marginTop: 8, flexWrap: 'wrap' }}>
            {[
              { label: 'Open', val: ihsg.open },
              { label: 'High', val: ihsg.day_high || ihsg.high },
              { label: 'Low',  val: ihsg.day_low  || ihsg.low  },
            ].map(({ label, val }) => val ? (
              <div key={label} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                <span style={{ fontSize: 8, color: '#64748b', fontWeight: 700, textTransform: 'uppercase' }}>{label}</span>
                <span style={{ fontSize: 10, color: '#94a3b8', fontWeight: 800, fontFamily: 'monospace' }}>
                  {formatIDXPrice(val)}
                </span>
              </div>
            ) : null)}
          </div>
        </div>
      ) : null}

      {/* Stock mini-cards horizontal scroll */}
      <div style={{ marginBottom: 14 }}>
        <div style={{ fontSize: 9, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 8 }}>
          Top Saham
        </div>
        <div style={{
          display: 'flex', gap: 8, overflowX: 'auto', paddingBottom: 4,
          scrollbarWidth: 'thin', scrollbarColor: 'rgba(16,185,129,0.3) transparent',
        }}>
          {loading
            ? Array.from({ length: 8 }).map((_, i) => <IDXSkeletonCard key={i} />)
            : stocks.length > 0
              ? stocks.map(s => <IDXStockCard key={s.symbol} stock={s} />)
              : (
                <div style={{ fontSize: 10, color: '#64748b', padding: '8px 0' }}>
                  Data tidak tersedia
                </div>
              )
          }
        </div>
      </div>

      {/* CTA button */}
      <button
        onClick={() => onSelectMode('stock_idx')}
        style={{
          width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center',
          gap: 6, padding: '10px 0', borderRadius: 12, border: '1px solid rgba(16,185,129,0.35)',
          background: 'rgba(16,185,129,0.12)', color: '#10b981',
          fontSize: 11, fontWeight: 900, letterSpacing: '0.06em', textTransform: 'uppercase',
          cursor: 'pointer', transition: 'all 0.2s',
        }}
        onMouseEnter={e => {
          e.currentTarget.style.background = 'rgba(16,185,129,0.22)';
          e.currentTarget.style.boxShadow = '0 0 16px rgba(16,185,129,0.2)';
        }}
        onMouseLeave={e => {
          e.currentTarget.style.background = 'rgba(16,185,129,0.12)';
          e.currentTarget.style.boxShadow = 'none';
        }}
      >
        🏦 Buka Stock IDX <ArrowRight size={13} />
      </button>

      {/* CSS keyframes for pulse dot */}
      <style>{`
        @keyframes ping {
          75%, 100% { transform: scale(2); opacity: 0; }
        }
      `}</style>
    </div>
  );
}

// ── Main DashboardView ─────────────────────────────────────────────────────────
export default function DashboardView({ onSelectMode, prices = {}, pairs = [] }) {
  const [wibTime, setWibTime] = useState(() => new Date(Date.now() + 7 * 3600000));
  const [btcPrice, setBtcPrice] = useState(null);
  const [btcLoading, setBtcLoading] = useState(false);
  const [activeMode, setActiveMode] = useState(() => localStorage.getItem('gas-last-mode') || null);
  const [ihsgPrice, setIhsgPrice] = useState(null);

  // WIB (GMT+7 Jakarta) clock
  useEffect(() => {
    const iv = setInterval(() => setWibTime(new Date(Date.now() + 7 * 3600000)), 1000);
    return () => clearInterval(iv);
  }, []);

  // Fetch BTC price once
  useEffect(() => {
    const loadBtc = async () => {
      setBtcLoading(true);
      try {
        const data = await fetchBinanceTicker('BTC/USDT');
        if (data?.last || data?.price) setBtcPrice(data.last || data.price);
        else if (data?.ticker?.last) setBtcPrice(data.ticker.last);
      } catch {
        // silent — use fallback
      } finally {
        setBtcLoading(false);
      }
    };
    loadBtc();
  }, []);

  // Fetch IHSG price for the mode card snippet
  useEffect(() => {
    const loadIhsg = async () => {
      try {
        const token = localStorage.getItem('gas-token');
        const headers = token ? { Authorization: `Bearer ${token}` } : {};
        const res = await fetch('/terminal/idx/ihsg', { headers });
        if (res.ok) {
          const data = await res.json();
          const p = data?.price || data?.close || data?.last;
          if (p) setIhsgPrice(p);
        }
      } catch {
        // silent
      }
    };
    loadIhsg();
  }, []);

  const handleModeSelect = (modeId) => {
    setActiveMode(modeId);
    localStorage.setItem('gas-last-mode', modeId);
    onSelectMode(modeId);
  };

  const pad = n => String(n).padStart(2, '0');
  const wibStr = `${pad(wibTime.getUTCHours())}:${pad(wibTime.getUTCMinutes())}:${pad(wibTime.getUTCSeconds())}`;

  return (
    <div className="p-4 md:p-6 pb-24 md:pb-6 max-w-5xl mx-auto space-y-8">

      {/* ── Hero Header ─────────────────────────────────────────────────────── */}
      <div className="flex flex-col items-center text-center py-6 gap-4">
        <div className="w-16 h-16 rounded-2xl overflow-hidden border-2 border-[var(--accent)]/30 shadow-[0_0_30px_rgba(250,204,21,0.15)]">
          <img
            src="https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg"
            alt="GAS"
            className="w-full h-full object-cover"
          />
        </div>
        <div>
          <h1 className="text-2xl font-black text-[var(--text-primary)] font-mono tracking-tight">
            Golden AI <span className="text-[var(--accent)]">Strategy</span>
          </h1>
          <p className="text-[11px] text-[var(--text-dim)] font-bold uppercase tracking-widest mt-1">
            Multi Market · 22 AI Features · Real-Time Intelligence
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)]">
            <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
            <span className="text-[9px] font-black uppercase tracking-widest text-[#10b981]">Systems Online</span>
          </div>
          <div className="text-[10px] font-mono font-black text-[var(--text-dim)] px-3 py-1.5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg">
            {wibStr} WIB
          </div>
        </div>
      </div>

      {/* ── Section 1: Mode Selector ─────────────────────────────────────────── */}
      <div>
        <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4 flex items-center gap-2">
          <Zap size={11} className="text-[var(--accent)]" />
          Select Trading Mode
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {MODES.map(mode => (
            <ModeCard
              key={mode.id}
              mode={mode}
              isActive={activeMode === mode.id}
              prices={prices}
              btcPrice={btcPrice}
              ihsgPrice={ihsgPrice}
              onClick={handleModeSelect}
            />
          ))}
        </div>
      </div>

      {/* ── Section 2: Market Pulse ──────────────────────────────────────────── */}
      <div>
        <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3 flex items-center gap-2">
          <Activity size={11} className="text-[#10b981]" />
          Market Pulse · Live
        </div>
        <div className="flex flex-wrap gap-2">
          {PULSE_PAIRS.map(sym => (
            <PulseCard
              key={sym}
              symbol={sym}
              price={prices[sym] || pairs.find(p => p.symbol === sym)?.base || 0}
              pairs={pairs}
            />
          ))}
          {btcPrice && (
            <div className="bg-[var(--bg-panel)] border border-[#f7931a]/30 rounded-xl px-3 py-2 min-w-[110px]">
              <div className="text-[9px] font-black text-[#f7931a] uppercase tracking-wide">BTC/USDT</div>
              <div className="text-xs font-black font-mono text-[var(--text-primary)]">
                ${btcPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </div>
              <div className="text-[8px] font-bold text-[#f7931a]">LIVE</div>
            </div>
          )}
        </div>
      </div>

      {/* ── Section 2b: IDX Market Widget ───────────────────────────────────── */}
      <IDXMarketWidget onSelectMode={handleModeSelect} />

      {/* ── Section 3: Quick Stats ───────────────────────────────────────────── */}
      <div>
        <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3 flex items-center gap-2">
          <BarChart2 size={11} className="text-[#3b82f6]" />
          Platform Stats
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
          {STATS.map(stat => {
            const Icon = stat.icon;
            return (
              <div key={stat.label} className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-4 flex flex-col gap-2">
                <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: `${stat.color}15` }}>
                  <Icon size={14} style={{ color: stat.color }} />
                </div>
                <div className="text-lg font-black font-mono" style={{ color: stat.color }}>{stat.value}</div>
                <div className="text-[9px] font-bold text-[var(--text-dim)] uppercase tracking-wide">{stat.label}</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── Section 4: Recent Activity / CTA ────────────────────────────────── */}
      <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-6 text-center">
        {activeMode ? (
          <div className="space-y-3">
            <div className="text-xs text-[var(--text-dim)] font-bold">Last used mode</div>
            <div className="text-base font-black text-[var(--text-primary)]">
              {MODES.find(m => m.id === activeMode)?.icon} {MODES.find(m => m.id === activeMode)?.title}
            </div>
            <button
              onClick={() => handleModeSelect(activeMode)}
              className="flex items-center gap-2 mx-auto px-5 py-2.5 rounded-xl text-xs font-black uppercase tracking-widest transition-all"
              style={{
                background: `${MODES.find(m => m.id === activeMode)?.color}20`,
                color: MODES.find(m => m.id === activeMode)?.color,
              }}
            >
              <ArrowRight size={13} /> Continue to {MODES.find(m => m.id === activeMode)?.title}
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            <div className="text-2xl">👆</div>
            <p className="text-xs font-bold text-[var(--text-secondary)]">Start by selecting a trading mode above</p>
            <p className="text-[10px] text-[var(--text-dim)]">Forex AI · Binance AI · Polymarket · Memecoin · Stock IDX</p>
          </div>
        )}
      </div>
    </div>
  );
}
