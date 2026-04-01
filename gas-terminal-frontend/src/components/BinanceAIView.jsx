import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  RefreshCw, Zap, BarChart2, Activity, TrendingUp, TrendingDown,
  AlertTriangle, ChevronUp, ChevronDown, Wifi, WifiOff, ArrowUpRight, ArrowDownRight,
} from 'lucide-react';
import { fetchBinanceTickers, fetchBinanceSignal } from '../services/api';
import AutoSignalPanel from './AutoSignalPanel';
import MarketAnalysisPanel from './MarketAnalysisPanel';

// ── Top 10 pairs displayed in Markets tab ─────────────────────────────────────
const CRYPTO_ICON = (sym) =>
  `https://cdn.jsdelivr.net/gh/atomiclabs/cryptocurrency-icons@master/128/color/${sym.toLowerCase()}.png`;

const TOP_PAIRS = [
  { symbol: 'BTC/USDT',   name: 'Bitcoin',   emoji: '₿',  logo: CRYPTO_ICON('btc'),   color: '#f7931a' },
  { symbol: 'ETH/USDT',   name: 'Ethereum',  emoji: '⬡',  logo: CRYPTO_ICON('eth'),   color: '#627eea' },
  { symbol: 'BNB/USDT',   name: 'BNB',       emoji: '⬟',  logo: CRYPTO_ICON('bnb'),   color: '#f3ba2f' },
  { symbol: 'SOL/USDT',   name: 'Solana',    emoji: '◎',  logo: CRYPTO_ICON('sol'),   color: '#9945ff' },
  { symbol: 'XRP/USDT',   name: 'XRP',       emoji: '✕',  logo: CRYPTO_ICON('xrp'),   color: '#346aa9' },
  { symbol: 'ADA/USDT',   name: 'Cardano',   emoji: '◈',  logo: CRYPTO_ICON('ada'),   color: '#0033ad' },
  { symbol: 'DOGE/USDT',  name: 'Dogecoin',  emoji: '🐶', logo: CRYPTO_ICON('doge'),  color: '#c2a633' },
  { symbol: 'TRX/USDT',   name: 'TRON',      emoji: '♦',  logo: CRYPTO_ICON('trx'),   color: '#c23631' },
  { symbol: 'DOT/USDT',   name: 'Polkadot',  emoji: '●',  logo: CRYPTO_ICON('dot'),   color: '#e6007a' },
  { symbol: 'MATIC/USDT', name: 'Polygon',   emoji: '⬡',  logo: CRYPTO_ICON('matic'), color: '#8247e5' },
];

const SCANNER_PAIRS = [
  // Crypto Major 10
  'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT',
  'ADA/USDT', 'DOGE/USDT', 'TRX/USDT', 'DOT/USDT', 'MATIC/USDT',
  // Extended large-cap
  'LINK/USDT', 'AVAX/USDT', 'LTC/USDT', 'UNI/USDT', 'ATOM/USDT',
  'NEAR/USDT', 'ARB/USDT', 'OP/USDT', 'TON/USDT', 'INJ/USDT',
];

const TABS = [
  { id:'Overview',   icon:'fa-solid fa-gauge-high',   label:'Overview' },
  { id:'Markets',    icon:'fa-brands fa-bitcoin',       label:'Markets' },
  { id:'Signals',    icon:'fa-solid fa-bolt',           label:'Signals' },
  { id:'Technical',  icon:'fa-solid fa-chart-area',     label:'Technical' },
  { id:'Data',       icon:'fa-solid fa-table',           label:'Data' },
  { id:'AI Insight', icon:'fa-solid fa-brain',           label:'AI Insight' },
];
const TIMEFRAMES = ['M15', 'H1', 'H4', 'D1'];

// Top futures pairs (USDT-M perpetual)
const FUTURES_PAIRS = [
  { symbol: 'BTC/USDT:USDT',   name: 'Bitcoin Perp',    emoji: '₿',  logo: CRYPTO_ICON('btc'),  color: '#f7931a' },
  { symbol: 'ETH/USDT:USDT',   name: 'Ethereum Perp',   emoji: '⬡',  logo: CRYPTO_ICON('eth'),  color: '#627eea' },
  { symbol: 'BNB/USDT:USDT',   name: 'BNB Perp',        emoji: '⬟',  logo: CRYPTO_ICON('bnb'),  color: '#f3ba2f' },
  { symbol: 'SOL/USDT:USDT',   name: 'Solana Perp',     emoji: '◎',  logo: CRYPTO_ICON('sol'),  color: '#9945ff' },
  { symbol: 'XRP/USDT:USDT',   name: 'XRP Perp',        emoji: '✕',  logo: CRYPTO_ICON('xrp'),  color: '#346aa9' },
  { symbol: 'ADA/USDT:USDT',   name: 'Cardano Perp',    emoji: '◈',  logo: CRYPTO_ICON('ada'),  color: '#0033ad' },
  { symbol: 'DOGE/USDT:USDT',  name: 'Dogecoin Perp',   emoji: '🐶', logo: CRYPTO_ICON('doge'), color: '#c2a633' },
  { symbol: 'AVAX/USDT:USDT',  name: 'Avalanche Perp',  emoji: '▲',  logo: CRYPTO_ICON('avax'), color: '#e84142' },
  { symbol: 'LINK/USDT:USDT',  name: 'Chainlink Perp',  emoji: '⬡',  logo: CRYPTO_ICON('link'), color: '#375bd2' },
  { symbol: 'ARB/USDT:USDT',   name: 'Arbitrum Perp',   emoji: '◇',  logo: CRYPTO_ICON('arb'),  color: '#28a0f0' },
];

// ── All Market Pairs (20 — full markets list) ────────────────────────────────
const ALL_MARKET_PAIRS = [
  { symbol: 'BTC/USDT',   name: 'Bitcoin',    short: 'BTC',   logo: CRYPTO_ICON('btc'),   color: '#f7931a', hot: true  },
  { symbol: 'ETH/USDT',   name: 'Ethereum',   short: 'ETH',   logo: CRYPTO_ICON('eth'),   color: '#627eea', hot: true  },
  { symbol: 'BNB/USDT',   name: 'BNB',        short: 'BNB',   logo: CRYPTO_ICON('bnb'),   color: '#f3ba2f', hot: false },
  { symbol: 'SOL/USDT',   name: 'Solana',     short: 'SOL',   logo: CRYPTO_ICON('sol'),   color: '#9945ff', hot: true  },
  { symbol: 'XRP/USDT',   name: 'XRP',        short: 'XRP',   logo: CRYPTO_ICON('xrp'),   color: '#346aa9', hot: true  },
  { symbol: 'ADA/USDT',   name: 'Cardano',    short: 'ADA',   logo: CRYPTO_ICON('ada'),   color: '#0033ad', hot: false },
  { symbol: 'DOGE/USDT',  name: 'Dogecoin',   short: 'DOGE',  logo: CRYPTO_ICON('doge'),  color: '#c2a633', hot: true  },
  { symbol: 'TRX/USDT',   name: 'TRON',       short: 'TRX',   logo: CRYPTO_ICON('trx'),   color: '#c23631', hot: false },
  { symbol: 'DOT/USDT',   name: 'Polkadot',   short: 'DOT',   logo: CRYPTO_ICON('dot'),   color: '#e6007a', hot: false },
  { symbol: 'MATIC/USDT', name: 'Polygon',    short: 'MATIC', logo: CRYPTO_ICON('matic'), color: '#8247e5', hot: false },
  { symbol: 'LINK/USDT',  name: 'Chainlink',  short: 'LINK',  logo: CRYPTO_ICON('link'),  color: '#375bd2', hot: false },
  { symbol: 'AVAX/USDT',  name: 'Avalanche',  short: 'AVAX',  logo: CRYPTO_ICON('avax'),  color: '#e84142', hot: false },
  { symbol: 'LTC/USDT',   name: 'Litecoin',   short: 'LTC',   logo: CRYPTO_ICON('ltc'),   color: '#bfbbbb', hot: false },
  { symbol: 'UNI/USDT',   name: 'Uniswap',    short: 'UNI',   logo: CRYPTO_ICON('uni'),   color: '#ff007a', hot: false },
  { symbol: 'ATOM/USDT',  name: 'Cosmos',     short: 'ATOM',  logo: CRYPTO_ICON('atom'),  color: '#6f7390', hot: false },
  { symbol: 'NEAR/USDT',  name: 'NEAR',       short: 'NEAR',  logo: CRYPTO_ICON('near'),  color: '#00c08b', hot: false },
  { symbol: 'ARB/USDT',   name: 'Arbitrum',   short: 'ARB',   logo: CRYPTO_ICON('arb'),   color: '#28a0f0', hot: true  },
  { symbol: 'OP/USDT',    name: 'Optimism',   short: 'OP',    logo: CRYPTO_ICON('op'),    color: '#ff0420', hot: false },
  { symbol: 'TON/USDT',   name: 'Toncoin',    short: 'TON',   logo: CRYPTO_ICON('ton'),   color: '#0088cc', hot: true  },
  { symbol: 'INJ/USDT',   name: 'Injective',  short: 'INJ',   logo: CRYPTO_ICON('inj'),   color: '#00a3ff', hot: true  },
];

// ── New Listings (✨ New tab) ─────────────────────────────────────────────────
const NEW_LISTINGS_PAIRS = [
  { symbol: 'JUP/USDT',   name: 'Jupiter',       short: 'JUP',   logo: CRYPTO_ICON('jup'),   color: '#c7a229', hot: false },
  { symbol: 'WIF/USDT',   name: 'dogwifhat',     short: 'WIF',   logo: CRYPTO_ICON('wif'),   color: '#9945ff', hot: true  },
  { symbol: 'ENA/USDT',   name: 'Ethena',        short: 'ENA',   logo: CRYPTO_ICON('ena'),   color: '#7b61ff', hot: false },
  { symbol: 'NOT/USDT',   name: 'Notcoin',       short: 'NOT',   logo: CRYPTO_ICON('not'),   color: '#e5ac00', hot: false },
  { symbol: 'CATI/USDT',  name: 'Catizen',       short: 'CATI',  logo: CRYPTO_ICON('cati'),  color: '#ff9900', hot: false },
  { symbol: 'EIGEN/USDT', name: 'Eigenlayer',    short: 'EIGEN', logo: CRYPTO_ICON('eigen'), color: '#6366f1', hot: false },
  { symbol: 'IO/USDT',    name: 'io.net',        short: 'IO',    logo: CRYPTO_ICON('io'),    color: '#00d4ff', hot: false },
  { symbol: 'BOME/USDT',  name: 'Book of Meme',  short: 'BOME',  logo: CRYPTO_ICON('bome'),  color: '#ff6b35', hot: false },
  { symbol: 'HMSTR/USDT', name: 'Hamster Kombat',short: 'HMSTR', logo: CRYPTO_ICON('hmstr'), color: '#c2a633', hot: false },
  { symbol: 'DOGS/USDT',  name: 'Dogs',          short: 'DOGS',  logo: CRYPTO_ICON('dogs'),  color: '#a0a0a0', hot: false },
];

// ── Helpers ────────────────────────────────────────────────────────────────────
function formatVolume(v) {
  if (!v || isNaN(v)) return '$--';
  if (v >= 1e9) return `$${(v / 1e9).toFixed(1)}B`;
  if (v >= 1e6) return `$${(v / 1e6).toFixed(0)}M`;
  if (v >= 1e3) return `$${(v / 1e3).toFixed(0)}K`;
  return `$${v.toFixed(0)}`;
}

function formatPrice(price, symbol) {
  if (!price || isNaN(price)) return '--';
  if (price < 0.001) return price.toFixed(8);
  if (price < 1) return price.toFixed(6);
  if (price < 100) return price.toFixed(4);
  if (price < 10000) return price.toFixed(2);
  return price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

// ── Market Row (Binance/OKX style) ────────────────────────────────────────────
function MarketRow({ meta, ticker, onSignal, isSelected }) {
  const price  = ticker?.last || 0;
  const change = ticker?.changePercent ?? ticker?.percentage ?? 0;
  const vol    = (ticker?.volume || 0) * (price || 1);
  const high24 = ticker?.high || 0;
  const low24  = ticker?.low  || 0;
  const isUp   = change >= 0;
  const has    = price > 0;
  const rangePct = (high24 > low24 && has)
    ? Math.min(100, Math.max(0, ((price - low24) / (high24 - low24)) * 100))
    : 50;

  return (
    <div
      onClick={() => onSignal(meta.symbol)}
      style={{
        display:'flex', alignItems:'center',
        padding:'11px 14px',
        borderBottom:'1px solid var(--border-color)',
        cursor:'pointer',
        background: isSelected ? 'rgba(59,130,246,0.06)' : 'transparent',
        transition:'background 0.15s',
      }}
      onMouseEnter={e => { if (!isSelected) e.currentTarget.style.background='var(--bg-card)'; }}
      onMouseLeave={e => { if (!isSelected) e.currentTarget.style.background='transparent'; }}
    >
      {/* Logo + Name */}
      <div style={{ display:'flex', alignItems:'center', gap:10, flex:1, minWidth:0 }}>
        <div style={{ position:'relative', flexShrink:0, width:34, height:34 }}>
          <img src={meta.logo} alt={meta.short} width={34} height={34}
            style={{ borderRadius:'50%', display:'block', objectFit:'cover' }}
            onError={e => { e.target.style.display='none'; e.target.nextSibling.style.display='flex'; }}
          />
          <div style={{
            display:'none', width:34, height:34, borderRadius:'50%',
            background:`${meta.color}22`, border:`1.5px solid ${meta.color}55`,
            alignItems:'center', justifyContent:'center',
            fontSize:13, fontWeight:900, color:meta.color, position:'absolute', inset:0,
          }}>{meta.short[0]}</div>
        </div>
        <div style={{ minWidth:0 }}>
          <div style={{ display:'flex', alignItems:'baseline', gap:3 }}>
            <span style={{ fontSize:13, fontWeight:900, color:'var(--text-primary)', letterSpacing:'-0.3px' }}>{meta.short}</span>
            <span style={{ fontSize:9, color:'var(--text-dim)', fontWeight:600 }}>/USDT</span>
          </div>
          <div style={{ fontSize:9, color:'var(--text-dim)', fontWeight:500, marginTop:1 }}>{meta.name}</div>
        </div>
      </div>

      {/* Price + 24h range */}
      <div style={{ textAlign:'right', flexShrink:0, width:'28%' }}>
        <div style={{ fontSize:13, fontWeight:800, fontFamily:'monospace', color:'var(--text-primary)', letterSpacing:'-0.5px' }}>
          {has ? `$${formatPrice(price)}` : <span style={{color:'var(--text-dim)'}}>--</span>}
        </div>
        {has && high24 > low24 && (
          <div style={{ height:2, background:'var(--bg-card)', borderRadius:2, marginTop:4, position:'relative', overflow:'hidden' }}>
            <div style={{ position:'absolute', left:`${Math.max(0, rangePct-3)}%`, width:6, height:'100%', background: isUp ? '#10b981':'#f43f5e', borderRadius:2 }} />
          </div>
        )}
      </div>

      {/* 24h % badge */}
      <div style={{ flexShrink:0, width:'22%', display:'flex', justifyContent:'flex-end', paddingLeft:8 }}>
        <span style={{
          fontSize:11, fontWeight:900, padding:'4px 8px', borderRadius:6, whiteSpace:'nowrap',
          background: isUp ? 'rgba(16,185,129,0.12)':'rgba(244,63,94,0.12)',
          color: isUp ? '#10b981':'#f43f5e',
        }}>
          {isUp ? '+' : ''}{has ? change.toFixed(2) : '--'}%
        </span>
      </div>

      {/* Volume — hidden on small screens */}
      <div className="mkt-vol" style={{ flexShrink:0, width:'18%', textAlign:'right' }}>
        <div style={{ fontSize:10, color:'var(--text-dim)', fontFamily:'monospace' }}>{has ? formatVolume(vol) : '--'}</div>
        {has && high24 > 0 && (
          <div style={{ fontSize:8, color:'var(--text-dim)', marginTop:2 }}>
            <span style={{color:'#10b981'}}>H:{formatPrice(high24)}</span>
            {' / '}
            <span style={{color:'#f43f5e'}}>L:{formatPrice(low24)}</span>
          </div>
        )}
      </div>

      {/* Signal button — hidden on small screens */}
      <div className="mkt-btn" style={{ flexShrink:0, paddingLeft:10 }}>
        <button
          onClick={e => { e.stopPropagation(); onSignal(meta.symbol); }}
          style={{
            padding:'5px 10px', fontSize:9, fontWeight:900, borderRadius:6, border:'none',
            background:'rgba(59,130,246,0.12)', color:'#3b82f6', cursor:'pointer',
            letterSpacing:'0.04em', textTransform:'uppercase', transition:'background 0.15s',
          }}
          onMouseEnter={e => e.currentTarget.style.background='rgba(59,130,246,0.25)'}
          onMouseLeave={e => e.currentTarget.style.background='rgba(59,130,246,0.12)'}
        >Signal</button>
      </div>
    </div>
  );
}

// ── WebSocket URL ──────────────────────────────────────────────────────────────
function getWsUrl() {
  const proto = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${proto}//${window.location.host}/terminal/ws/binance`;
}

// ── Main Component ─────────────────────────────────────────────────────────────
export default function BinanceAIView() {
  const [mode, setMode] = useState('manual');
  const [activeTab, setActiveTab] = useState('Markets');
  const [tickers, setTickers] = useState({});
  const [wsStatus, setWsStatus] = useState('connecting'); // connecting | live | error
  const [lastUpdated, setLastUpdated] = useState(null);
  const [timeframe, setTimeframe] = useState('H1');
  const wsRef = useRef(null);
  const reconnectRef = useRef(null);

  // Signals tab
  const [signalPair, setSignalPair] = useState('BTC/USDT');
  const [signalResult, setSignalResult] = useState(null);
  const [signalLoading, setSignalLoading] = useState(false);
  const [signalError, setSignalError] = useState('');

  // Futures tab
  const [futuresTickers, setFuturesTickers] = useState({});

  // Markets tab
  const [marketFilter, setMarketFilter] = useState('all');
  const [marketSearch, setMarketSearch] = useState('');

  // Scanner tab
  const [scannerData, setScannerData] = useState({});
  const [scannerLoading, setScannerLoading] = useState(false);
  const [scannerFilter, setScannerFilter] = useState('All');
  const [sortKey, setSortKey] = useState('change');
  const [sortAsc, setSortAsc] = useState(false);

  // ── WebSocket real-time connection ────────────────────────────────────────
  const connectWs = useCallback(() => {
    if (wsRef.current && wsRef.current.readyState <= 1) return; // already open/connecting
    setWsStatus('connecting');
    const ws = new WebSocket(getWsUrl());
    wsRef.current = ws;

    ws.onopen = () => {
      setWsStatus('live');
      // Request all market pairs + new listings + scanner + futures
      const spotSymbols = [...new Set([
        ...ALL_MARKET_PAIRS.map(p => p.symbol),
        ...NEW_LISTINGS_PAIRS.map(p => p.symbol),
        ...SCANNER_PAIRS,
      ])];
      const futSymbols  = FUTURES_PAIRS.map(p => p.symbol);
      const allSymbols  = [...spotSymbols, ...futSymbols];
      ws.send(JSON.stringify({ symbols: allSymbols.join(',') }));
    };

    ws.onmessage = (e) => {
      try {
        const msg = JSON.parse(e.data);
        if (msg.type === 'tickers' && msg.data) {
          const spotNorm = {}, futNorm = {};
          Object.entries(msg.data).forEach(([sym, t]) => {
            const norm = { ...t, percentage: t.changePercent ?? t.percentage ?? 0 };
            if (sym.includes(':USDT')) {
              futNorm[sym] = norm;
            } else {
              spotNorm[sym] = norm;
            }
          });
          if (Object.keys(spotNorm).length > 0) {
            setTickers(prev => ({ ...prev, ...spotNorm }));
            setScannerData(prev => ({ ...prev, ...spotNorm }));
          }
          if (Object.keys(futNorm).length > 0) {
            setFuturesTickers(prev => ({ ...prev, ...futNorm }));
          }
          setLastUpdated(new Date());
        }
      } catch (_) {}
    };

    ws.onerror = () => setWsStatus('error');

    ws.onclose = () => {
      setWsStatus('error');
      // Reconnect after 3s
      reconnectRef.current = setTimeout(() => connectWs(), 3000);
    };
  }, []);

  useEffect(() => {
    connectWs();
    return () => {
      clearTimeout(reconnectRef.current);
      if (wsRef.current) wsRef.current.close();
    };
  }, [connectWs]);

  // Fallback REST fetch if WS not delivering data after 5s
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (Object.keys(tickers).length === 0) {
        try {
          const allSymbols = [...new Set([...TOP_PAIRS.map(p => p.symbol), ...SCANNER_PAIRS])];
          const data = await fetchBinanceTickers(allSymbols);
          if (data) {
            setTickers(data);
            setScannerData(data);
            setLastUpdated(new Date());
          }
        } catch (_) {}
      }
    }, 5000);
    return () => clearTimeout(timer);
  }, [tickers]);

  // ── Manual refresh (REST fallback) ───────────────────────────────────────
  const fetchTickers = useCallback(async () => {
    try {
      const allSymbols = [...new Set([...TOP_PAIRS.map(p => p.symbol), ...SCANNER_PAIRS])];
      const data = await fetchBinanceTickers(allSymbols);
      if (data) {
        setTickers(data);
        setScannerData(data);
        setLastUpdated(new Date());
      }
    } catch (err) {
      console.error('Manual refresh error:', err);
    }
  }, []);

  const fetchScanner = useCallback(async () => {
    setScannerLoading(true);
    try {
      const data = await fetchBinanceTickers(SCANNER_PAIRS);
      if (data) setScannerData(data);
    } catch (err) {
      console.error('Scanner fetch error:', err);
    } finally {
      setScannerLoading(false);
    }
  }, []);

  // ── Market mood ────────────────────────────────────────────────────────────
  const tickerValues = Object.values(tickers);
  const greenCount = tickerValues.filter(t => (t?.percentage || 0) >= 0).length;
  const moodPct = tickerValues.length > 0 ? Math.round((greenCount / tickerValues.length) * 100) : 50;
  const moodLabel = moodPct >= 65 ? 'BULLISH' : moodPct >= 40 ? 'NEUTRAL' : 'BEARISH';
  const moodColor = moodPct >= 65 ? '#10b981' : moodPct >= 40 ? '#f59e0b' : '#f43f5e';

  // ── Signal fetch — uses real Binance OHLCV + indicator engine ─────────────
  const fetchSignal = async () => {
    setSignalError('');
    setSignalLoading(true);
    try {
      const res = await fetchBinanceSignal(signalPair, timeframe, 200);
      setSignalResult(res);
    } catch (err) {
      setSignalError(err?.response?.data?.detail || err?.message || 'Gagal ambil sinyal dari Binance.');
    } finally {
      setSignalLoading(false);
    }
  };

  // ── Scanner sort/filter ────────────────────────────────────────────────────
  const getScannerRows = () => {
    return SCANNER_PAIRS.map(sym => {
      const t = scannerData[sym] || {};
      return {
        symbol: sym,
        price: t.last || t.price || 0,
        change: t.percentage || t.change_pct || 0,
        volume: t.quoteVolume || t.volume || 0,
      };
    }).filter(r => {
      if (scannerFilter === 'Gainers') return r.change > 0;
      if (scannerFilter === 'Losers') return r.change < 0;
      if (scannerFilter === 'High Volume') return r.volume > 1e8;
      return true;
    }).sort((a, b) => {
      const aVal = a[sortKey];
      const bVal = b[sortKey];
      return sortAsc ? aVal - bVal : bVal - aVal;
    });
  };

  const handleSort = (key) => {
    if (sortKey === key) setSortAsc(v => !v);
    else { setSortKey(key); setSortAsc(false); }
  };

  const lastUpdatedStr = lastUpdated
    ? `${String(lastUpdated.getHours()).padStart(2,'0')}:${String(lastUpdated.getMinutes()).padStart(2,'0')}:${String(lastUpdated.getSeconds()).padStart(2,'0')}`
    : '--';

  return (
    <div className="p-4 md:p-6 pb-24 md:pb-6 max-w-5xl mx-auto space-y-5">
      {/* Mode Tabs */}
      <div className="flex gap-1 p-1 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)]">
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
        <div className="space-y-3">
          <AutoSignalPanel market="crypto" planDepth="essential" />
        </div>
      )}

      {mode === 'analysis' && (
        <div className="space-y-3">
          <MarketAnalysisPanel market="crypto" planDepth="essential" />
        </div>
      )}

      {mode === 'manual' && (<>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-xl bg-[#3b82f6]/10 border border-[#3b82f6]/20 flex items-center justify-center shrink-0">
            <Activity size={20} className="text-[#3b82f6]" />
          </div>
          <div>
            <h2 className="text-lg font-black text-[var(--text-primary)]">₿ Binance AI</h2>
            <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Crypto · Spot · Live Market Data</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {/* WS status badge */}
          <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg border ${
            wsStatus === 'live'
              ? 'bg-[#10b981]/10 border-[#10b981]/30'
              : wsStatus === 'connecting'
              ? 'bg-yellow-500/10 border-yellow-500/30'
              : 'bg-[#f43f5e]/10 border-[#f43f5e]/30'
          }`}>
            {wsStatus === 'live'
              ? <><span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" /><Wifi size={10} className="text-[#10b981]" /><span className="text-[9px] font-black uppercase tracking-widest text-[#10b981]">LIVE</span></>
              : wsStatus === 'connecting'
              ? <><RefreshCw size={10} className="text-yellow-400 animate-spin" /><span className="text-[9px] font-black uppercase tracking-widest text-yellow-400">CONNECTING</span></>
              : <><WifiOff size={10} className="text-[#f43f5e]" /><span className="text-[9px] font-black uppercase tracking-widest text-[#f43f5e]">OFFLINE</span></>
            }
          </div>
          <div className="text-[9px] font-mono font-bold text-[var(--text-dim)] px-2 py-1.5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg">
            {lastUpdatedStr}
          </div>
          <button
            onClick={fetchTickers}
            className="p-2 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors"
            title="Manual refresh"
          >
            <RefreshCw size={13} />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mkt-tab-wrap">
        {TABS.map(tab => (
          <button key={tab.id} className={`mkt-tab-btn${activeTab === tab.id ? ' mkt-tab-btn--on' : ''}`} onClick={() => setActiveTab(tab.id)}>
            <i className={tab.icon} />{tab.label}
          </button>
        ))}
      </div>

      {activeTab === 'Overview' && (
        <div className="space-y-4 p-4">
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label:'Market Trend',    value:'Bullish',    icon:'📈', badge:'green' },
              { label:'BTC Dominance',   value:'52.4%',      icon:'₿',  badge:'' },
              { label:'Risk Sentiment',  value:'Risk-On',    icon:'⚡', badge:'gold' },
              { label:'Altseason Index', value:'42 / 100',   icon:'🚀', badge:'' },
            ].map(c => (
              <div key={c.label} className="sig-card">
                <div className="text-xl mb-2">{c.icon}</div>
                <div className="text-[9px] font-bold text-[var(--text-dim)] uppercase tracking-wide mb-1">{c.label}</div>
                <div className={`text-sm font-black ${c.badge === 'green' ? 'text-[#10b981]' : c.badge === 'gold' ? 'text-[var(--accent)]' : 'text-[var(--text-primary)]'}`}>{c.value}</div>
              </div>
            ))}
          </div>
          <div className="sig-card">
            <div className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-3">🔥 Top Movers</div>
            <table className="data-tbl">
              <thead><tr><th>Asset</th><th>Price</th><th>24h Change</th><th>Volume</th></tr></thead>
              <tbody>
                {TOP_PAIRS.slice(0,5).map(p => (
                  <tr key={p.symbol}>
                    <td className="td-name">{p.emoji} {p.symbol.replace('/USDT','')}</td>
                    <td>—</td>
                    <td className="td-up">—</td>
                    <td>—</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ── TAB: Markets ──────────────────────────────────────────────────────── */}
      {activeTab === 'Markets' && (() => {
        const search = marketSearch.toLowerCase();
        const base = marketFilter === 'new' ? NEW_LISTINGS_PAIRS : ALL_MARKET_PAIRS;
        let filtered = base.filter(m =>
          !search || m.short.toLowerCase().includes(search) || m.name.toLowerCase().includes(search)
        );
        if (marketFilter === 'gainers')
          filtered = filtered.filter(m => (tickers[m.symbol]?.changePercent ?? 0) > 0)
            .sort((a,b) => (tickers[b.symbol]?.changePercent||0) - (tickers[a.symbol]?.changePercent||0));
        else if (marketFilter === 'losers')
          filtered = filtered.filter(m => (tickers[m.symbol]?.changePercent ?? 0) < 0)
            .sort((a,b) => (tickers[a.symbol]?.changePercent||0) - (tickers[b.symbol]?.changePercent||0));
        else if (marketFilter === 'hot')
          filtered = filtered.filter(m => m.hot);

        return (
          <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
            <style>{`
              @media (max-width: 640px) { .mkt-vol { display:none !important; } .mkt-btn { display:none !important; } }
              @media (max-width: 480px) { .mkt-name { display:none !important; } }
            `}</style>

            {/* Market Mood mini strip */}
            <div style={{ display:'flex', alignItems:'center', gap:10, padding:'8px 14px', background:'var(--bg-panel)', border:'1px solid var(--border-color)', borderRadius:12 }}>
              <span style={{ fontSize:9, fontWeight:900, textTransform:'uppercase', letterSpacing:'0.1em', color:'var(--text-dim)', whiteSpace:'nowrap' }}>Market Mood</span>
              <div style={{ flex:1, height:4, background:'var(--bg-card)', borderRadius:2, overflow:'hidden' }}>
                <div style={{ height:'100%', width:`${moodPct}%`, background:moodColor, borderRadius:2, transition:'width 0.7s' }} />
              </div>
              <span style={{ fontSize:9, fontWeight:900, color:moodColor, whiteSpace:'nowrap' }}>{moodLabel} · {moodPct}%</span>
            </div>

            {/* Filter tabs + Search */}
            <div style={{ display:'flex', alignItems:'center', gap:6, flexWrap:'wrap' }}>
              {[
                ['all',     'All'],
                ['gainers', '📈 Gainers'],
                ['losers',  '📉 Losers'],
                ['hot',     '🔥 Hot'],
                ['new',     '✨ New'],
              ].map(([k, label]) => (
                <button key={k} onClick={() => setMarketFilter(k)}
                  style={{
                    padding:'5px 13px', borderRadius:20, fontSize:10, fontWeight:900,
                    border: marketFilter === k ? 'none' : '1px solid var(--border-color)',
                    cursor:'pointer', transition:'all 0.15s',
                    background: marketFilter === k ? '#3b82f6' : 'var(--bg-panel)',
                    color: marketFilter === k ? '#fff' : 'var(--text-dim)',
                  }}
                >{label}</button>
              ))}
              <div style={{ marginLeft:'auto' }}>
                <input
                  type="text" placeholder="🔍 Search..."
                  value={marketSearch} onChange={e => setMarketSearch(e.target.value)}
                  style={{
                    background:'var(--bg-panel)', border:'1px solid var(--border-color)',
                    borderRadius:8, padding:'5px 10px', fontSize:10, color:'var(--text-primary)',
                    width:110, outline:'none',
                  }}
                  onFocus={e => e.target.style.borderColor='#3b82f6'}
                  onBlur={e => e.target.style.borderColor='var(--border-color)'}
                />
              </div>
            </div>

            {/* Table container */}
            <div style={{ background:'var(--bg-panel)', border:'1px solid var(--border-color)', borderRadius:16, overflow:'hidden' }}>

              {/* Column headers */}
              <div style={{ display:'flex', alignItems:'center', padding:'8px 14px', borderBottom:'1px solid var(--border-color)', background:'var(--bg-card)' }}>
                <div style={{ flex:1, fontSize:9, fontWeight:900, textTransform:'uppercase', letterSpacing:'0.1em', color:'var(--text-dim)' }}>Pair</div>
                <div style={{ width:'28%', textAlign:'right', fontSize:9, fontWeight:900, textTransform:'uppercase', letterSpacing:'0.1em', color:'var(--text-dim)' }}>Price</div>
                <div style={{ width:'22%', textAlign:'right', fontSize:9, fontWeight:900, textTransform:'uppercase', letterSpacing:'0.1em', color:'var(--text-dim)', paddingLeft:8 }}>24h</div>
                <div className="mkt-vol" style={{ width:'18%', textAlign:'right', fontSize:9, fontWeight:900, textTransform:'uppercase', letterSpacing:'0.1em', color:'var(--text-dim)' }}>Volume</div>
                <div className="mkt-btn" style={{ width:64 }} />
              </div>

              {/* Rows */}
              {filtered.length > 0
                ? filtered.map(meta => (
                    <MarketRow
                      key={meta.symbol}
                      meta={meta}
                      ticker={tickers[meta.symbol]}
                      onSignal={(sym) => { setSignalPair(sym); setActiveTab('Signals'); }}
                      isSelected={signalPair === meta.symbol}
                    />
                  ))
                : (
                  <div style={{ padding:'40px 14px', textAlign:'center', color:'var(--text-dim)', fontSize:12 }}>
                    No pairs found
                  </div>
                )
              }

              {/* Footer */}
              <div style={{ display:'flex', justifyContent:'space-between', alignItems:'center', padding:'8px 14px', borderTop:'1px solid var(--border-color)' }}>
                <span style={{ fontSize:9, color:'var(--text-dim)' }}>{filtered.length} pairs · Tap row to analyze</span>
                <div style={{ display:'flex', alignItems:'center', gap:5 }}>
                  <div style={{
                    width:6, height:6, borderRadius:'50%',
                    background: wsStatus === 'live' ? '#10b981' : '#f43f5e',
                    boxShadow: wsStatus === 'live' ? '0 0 6px #10b981' : 'none',
                  }} />
                  <span style={{ fontSize:9, fontWeight:900, color: wsStatus === 'live' ? '#10b981' : '#f43f5e' }}>
                    {wsStatus === 'live' ? 'LIVE' : wsStatus.toUpperCase()}
                  </span>
                </div>
              </div>
            </div>
          </div>
        );
      })()}

      {/* ── TAB: Signals ──────────────────────────────────────────────────────── */}
      {activeTab === 'Signals' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest">Select Pair</div>
              <div className="flex flex-wrap gap-2">
                {TOP_PAIRS.map(p => (
                  <button
                    key={p.symbol}
                    onClick={() => setSignalPair(p.symbol)}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${signalPair === p.symbol ? 'bg-[#3b82f6] text-white' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[#3b82f6]/40'}`}
                  >
                    {p.emoji} {p.symbol.replace('/USDT', '')}
                  </button>
                ))}
              </div>
            </div>
            <div className="shrink-0">
              <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest">Timeframe</div>
              <div className="flex gap-1">
                {TIMEFRAMES.map(tf => (
                  <button
                    key={tf}
                    onClick={() => setTimeframe(tf)}
                    className={`px-2.5 py-1.5 rounded-lg text-[10px] font-black transition-all ${timeframe === tf ? 'bg-[#3b82f6] text-white' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[#3b82f6]/40'}`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={fetchSignal}
            disabled={signalLoading}
            className="flex items-center gap-2 px-5 py-3 bg-[#3b82f6] text-white rounded-xl text-xs font-black uppercase tracking-widest hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {signalLoading ? <RefreshCw size={14} className="animate-spin" /> : <Zap size={14} />}
            {signalLoading ? 'Analyzing...' : `Analyze ${signalPair}`}
          </button>

          {signalError && (
            <div className="flex items-center gap-2 p-3 bg-[#f43f5e]/10 border border-[#f43f5e]/20 rounded-xl text-xs text-[#f43f5e] font-bold">
              <AlertTriangle size={14} /> {signalError}
            </div>
          )}

          {signalResult && (
            <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-5 space-y-4">
              {/* Signal Header */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className={`text-3xl font-black ${signalResult.bias === 'BULLISH' ? 'text-[#10b981]' : signalResult.bias === 'BEARISH' ? 'text-[#f43f5e]' : 'text-yellow-400'}`}>
                    {signalResult.signal || signalResult.bias || 'HOLD'}
                  </div>
                  <div>
                    <div className="text-xs font-black text-[var(--text-primary)]">{signalResult.symbol || signalPair}</div>
                    <div className="text-[9px] text-[var(--text-dim)]">{timeframe} · {signalResult.candles_analyzed || 0} candles · Real Binance Data</div>
                  </div>
                </div>
                {signalResult.confidence && (
                  <div className="text-right">
                    <div className={`text-xl font-black font-mono ${signalResult.confidence >= 65 ? 'text-[#10b981]' : signalResult.confidence >= 50 ? 'text-yellow-400' : 'text-[#f43f5e]'}`}>{signalResult.confidence}%</div>
                    <div className="text-[9px] text-[var(--text-dim)]">Confluence</div>
                  </div>
                )}
              </div>

              {/* Price + Entry / SL / TP row */}
              {signalResult.entry && (
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  <div className="bg-[var(--bg-card)] rounded-xl p-3 text-center">
                    <div className="text-[8px] text-[var(--text-dim)] font-black mb-1">PRICE</div>
                    <div className="text-[10px] font-black font-mono text-[var(--text-primary)]">${formatPrice(signalResult.price)}</div>
                  </div>
                  <div className="bg-[#3b82f6]/10 border border-[#3b82f6]/20 rounded-xl p-3 text-center">
                    <div className="text-[8px] text-[#3b82f6] font-black mb-1">ENTRY</div>
                    <div className="text-[10px] font-black font-mono text-[var(--text-primary)]">${formatPrice(signalResult.entry)}</div>
                  </div>
                  <div className="bg-[#f43f5e]/10 border border-[#f43f5e]/20 rounded-xl p-3 text-center">
                    <div className="text-[8px] text-[#f43f5e] font-black mb-1">STOP LOSS</div>
                    <div className="text-[10px] font-black font-mono text-[var(--text-primary)]">${formatPrice(signalResult.sl)}</div>
                  </div>
                  <div className="bg-[#10b981]/10 border border-[#10b981]/20 rounded-xl p-3 text-center">
                    <div className="text-[8px] text-[#10b981] font-black mb-1">TP1</div>
                    <div className="text-[10px] font-black font-mono text-[var(--text-primary)]">${formatPrice(signalResult.tp1)}</div>
                  </div>
                </div>
              )}

              {/* Indicators */}
              {signalResult.indicators && (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {Object.entries(signalResult.indicators).map(([key, val]) => (
                    <div key={key} className="bg-[var(--bg-card)] rounded-xl p-3">
                      <div className="text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">{key.replace('_', ' ')}</div>
                      <div className="text-[10px] font-bold font-mono text-[var(--text-primary)] leading-tight">
                        {String(val)}
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* SMC Structure */}
              {signalResult.smc && (
                <div className="bg-[var(--bg-card)] rounded-xl p-3">
                  <div className="text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">SMC Structure</div>
                  <div className="flex flex-wrap gap-3 text-[10px]">
                    <span className={`font-black ${signalResult.smc.trend === 'BULLISH' ? 'text-[#10b981]' : signalResult.smc.trend === 'BEARISH' ? 'text-[#f43f5e]' : 'text-yellow-400'}`}>
                      {signalResult.smc.structure}
                    </span>
                    {signalResult.smc.key_support_levels?.length > 0 && (
                      <span className="text-[var(--text-dim)]">
                        S: ${signalResult.smc.key_support_levels.map(x => formatPrice(x)).join(' / ')}
                      </span>
                    )}
                    {signalResult.smc.key_resistance_levels?.length > 0 && (
                      <span className="text-[var(--text-dim)]">
                        R: ${signalResult.smc.key_resistance_levels.map(x => formatPrice(x)).join(' / ')}
                      </span>
                    )}
                  </div>
                </div>
              )}

              {/* Reasoning */}
              {signalResult.reasoning && (
                <div className="text-[10px] text-[var(--text-dim)] leading-relaxed border-t border-[var(--border-color)] pt-3 space-y-1">
                  {signalResult.reasoning.split(' | ').map((r, i) => (
                    <div key={i} className="flex gap-1.5 items-start">
                      <span className="text-[#3b82f6] shrink-0">•</span>
                      <span>{r}</span>
                    </div>
                  ))}
                </div>
              )}

              {/* TP2 + ATR footer */}
              {signalResult.tp2 && (
                <div className="flex gap-4 text-[9px] text-[var(--text-dim)] font-mono border-t border-[var(--border-color)] pt-2">
                  <span>TP2: <span className="text-[#10b981] font-black">${formatPrice(signalResult.tp2)}</span></span>
                  {signalResult.atr && <span>ATR: <span className="text-[var(--text-primary)] font-black">{formatPrice(signalResult.atr)}</span></span>}
                  <span className="ml-auto text-[8px]">Source: {signalResult.source || 'binance-live'}</span>
                </div>
              )}
            </div>
          )}

          {!signalResult && !signalLoading && !signalError && (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center">
                <BarChart2 size={24} className="text-[var(--text-dim)]" />
              </div>
              <p className="text-xs text-[var(--text-dim)] font-bold">Select a pair and run AI analysis</p>
            </div>
          )}
        </div>
      )}

      {/* ── TAB: Futures ──────────────────────────────────────────────────────── */}
      {activeTab === 'Futures' && (
        <div className="space-y-4">
          <div className="flex items-center gap-2 px-1">
            <div className="w-1.5 h-1.5 rounded-full bg-[#f59e0b] animate-pulse" />
            <span className="text-[9px] font-black uppercase tracking-widest text-[#f59e0b]">USDT-M Perpetual Futures</span>
          </div>
          <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[var(--border-color)]">
                  <th className="px-4 py-3 text-left text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)]">Contract</th>
                  <th className="px-4 py-3 text-right text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)]">Mark Price</th>
                  <th className="px-4 py-3 text-right text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)]">24h Change</th>
                  <th className="px-4 py-3 text-right text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)]">Volume</th>
                  <th className="px-4 py-3 text-right text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)]">High / Low</th>
                </tr>
              </thead>
              <tbody>
                {FUTURES_PAIRS.map((meta, i) => {
                  const t = futuresTickers[meta.symbol] || {};
                  const price  = t.last || 0;
                  const change = t.percentage || 0;
                  const vol    = t.volume || 0;
                  const isUp   = change >= 0;
                  const hasData = price > 0;
                  return (
                    <tr key={meta.symbol} className={`border-b border-[var(--border-color)]/40 hover:bg-[var(--bg-hover)] transition-colors ${i % 2 === 0 ? '' : 'bg-[var(--bg-card)]/20'}`}>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{meta.emoji}</span>
                          <div>
                            <div className="text-[10px] font-black text-[var(--text-primary)]">{meta.name}</div>
                            <div className="text-[8px] text-[var(--text-dim)] font-mono">{meta.symbol.replace(':USDT', '')}</div>
                          </div>
                          <span className="ml-1 text-[7px] font-black px-1.5 py-0.5 rounded bg-[#f59e0b]/10 text-[#f59e0b] border border-[#f59e0b]/20">PERP</span>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-right">
                        <span className="text-[10px] font-black font-mono text-[var(--text-primary)]">
                          {hasData ? `$${formatPrice(price)}` : <span className="text-[var(--text-dim)]">—</span>}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-right">
                        {hasData ? (
                          <div className={`flex items-center justify-end gap-1 text-[10px] font-black ${isUp ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
                            {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                            {isUp ? '+' : ''}{change.toFixed(2)}%
                          </div>
                        ) : <span className="text-[var(--text-dim)] text-[10px]">—</span>}
                      </td>
                      <td className="px-4 py-3 text-right text-[10px] font-mono text-[var(--text-dim)]">
                        {hasData ? formatVolume(vol) : '—'}
                      </td>
                      <td className="px-4 py-3 text-right">
                        {hasData && t.high && t.low ? (
                          <div className="text-[9px] font-mono">
                            <span className="text-[#10b981]">${formatPrice(t.high)}</span>
                            <span className="text-[var(--text-dim)]"> / </span>
                            <span className="text-[#f43f5e]">${formatPrice(t.low)}</span>
                          </div>
                        ) : <span className="text-[var(--text-dim)] text-[10px]">—</span>}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
            {Object.keys(futuresTickers).length === 0 && (
              <div className="py-8 text-center text-xs text-[var(--text-dim)]">
                <RefreshCw size={16} className="animate-spin mx-auto mb-2 text-[#f59e0b]" />
                Connecting to futures stream...
              </div>
            )}
          </div>
        </div>
      )}

      {/* ── TAB: Scanner ──────────────────────────────────────────────────────── */}
      {activeTab === 'Scanner' && (
        <div className="space-y-4">
          {/* Controls */}
          <div className="flex flex-col sm:flex-row gap-3 items-start sm:items-center justify-between">
            <div className="flex gap-2">
              {['All', 'Gainers', 'Losers', 'High Volume'].map(f => (
                <button
                  key={f}
                  onClick={() => setScannerFilter(f)}
                  className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase tracking-widest transition-all ${scannerFilter === f ? 'bg-[#3b82f6] text-white' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[#3b82f6]/40'}`}
                >
                  {f}
                </button>
              ))}
            </div>
            <button
              onClick={fetchScanner}
              disabled={scannerLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[9px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors"
            >
              <RefreshCw size={11} className={scannerLoading ? 'animate-spin' : ''} /> Refresh
            </button>
          </div>

          {/* Table */}
          <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[var(--border-color)]">
                  {[
                    { key: 'symbol', label: 'Symbol' },
                    { key: 'price',  label: 'Price' },
                    { key: 'change', label: '24h %' },
                    { key: 'volume', label: 'Volume' },
                  ].map(col => (
                    <th
                      key={col.key}
                      onClick={() => handleSort(col.key)}
                      className="px-4 py-3 text-left text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)] cursor-pointer hover:text-[var(--text-primary)] transition-colors"
                    >
                      <div className="flex items-center gap-1">
                        {col.label}
                        {sortKey === col.key ? (
                          sortAsc ? <ChevronUp size={10} /> : <ChevronDown size={10} />
                        ) : null}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {scannerLoading ? (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center">
                      <RefreshCw size={20} className="animate-spin text-[var(--text-dim)] mx-auto" />
                    </td>
                  </tr>
                ) : getScannerRows().map((row, i) => {
                  const meta = TOP_PAIRS.find(p => p.symbol === row.symbol);
                  const isUp = row.change >= 0;
                  return (
                    <tr key={row.symbol} className={`border-b border-[var(--border-color)]/50 hover:bg-[var(--bg-hover)] transition-colors ${i % 2 === 0 ? '' : 'bg-[var(--bg-card)]/20'}`}>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-2">
                          <span className="text-sm">{meta?.emoji || '●'}</span>
                          <div>
                            <div className="text-[10px] font-black text-[var(--text-primary)]">{row.symbol.replace('/USDT', '')}</div>
                            <div className="text-[8px] text-[var(--text-dim)]">/USDT</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3 text-[10px] font-mono font-black text-[var(--text-primary)]">
                        ${formatPrice(row.price)}
                      </td>
                      <td className="px-4 py-3">
                        <div className={`flex items-center gap-1 text-[10px] font-black ${isUp ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
                          {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                          {isUp ? '+' : ''}{row.change.toFixed(2)}%
                        </div>
                      </td>
                      <td className="px-4 py-3 text-[10px] font-mono text-[var(--text-dim)]">
                        {formatVolume(row.volume)}
                      </td>
                    </tr>
                  );
                })}
                {!scannerLoading && getScannerRows().length === 0 && (
                  <tr>
                    <td colSpan={4} className="px-4 py-8 text-center text-xs text-[var(--text-dim)]">No data — click Refresh</td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {activeTab === 'Technical' && (
        <div className="space-y-4 p-4">
          <div className="sig-card">
            <div className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-3">📉 SMC + Indicators</div>
            <p className="ai-insight-text" style={{fontSize:'11px'}}>Select a pair from Markets tab then run Signal AI to generate technical analysis including Order Blocks, BOS/CHOCH, FVG zones, RSI, MACD, and VWAP.</p>
          </div>
          <div className="overflow-x-auto">
            <table className="data-tbl">
              <thead><tr><th>Pair</th><th>RSI</th><th>MACD</th><th>EMA20</th><th>Structure</th><th>Signal</th></tr></thead>
              <tbody>
                {TOP_PAIRS.slice(0,8).map(p => (
                  <tr key={p.symbol}>
                    <td className="td-name">{p.emoji} {p.symbol.replace('/USDT','')}</td>
                    <td>—</td><td>—</td><td>—</td><td>—</td><td>—</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeTab === 'Data' && (
        <div className="space-y-4 p-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
            <div className="px-4 py-2.5 border-b border-[var(--border-color)]">
              <span className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest">📊 Market Data</span>
            </div>
            <div className="overflow-x-auto">
              <table className="data-tbl">
                <thead><tr><th>Pair</th><th>Price</th><th>24h%</th><th>Volume</th><th>Funding</th><th>OI</th></tr></thead>
                <tbody>
                  {TOP_PAIRS.map(p => (
                    <tr key={p.symbol}>
                      <td><span className="td-name" style={{color:p.color}}>{p.emoji} {p.name}</span><br/><span style={{fontSize:'8px',color:'var(--text-dim)'}}>{p.symbol}</span></td>
                      <td>—</td><td className="td-up">—</td><td>—</td><td>—</td><td>—</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'AI Insight' && (
        <div className="space-y-4 p-4">
          <div className="ai-insight-card">
            <h4>🧠 Crypto AI Intelligence</h4>
            <p className="ai-insight-text">AI synthesizes on-chain metrics, funding rates, order book depth, and smart money flow to identify high-probability crypto setups. BTC dominance and altcoin rotation signals are continuously monitored.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">Binance API Live</span>
              <span className="ai-badge ai-badge--green">Order Book Active</span>
              <span className="ai-badge">Funding Rate</span>
              <span className="ai-badge">OI Analysis</span>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { label:'Smart Money Flow',  value:'Accumulation', icon:'🏦' },
              { label:'Liquidation Risk',  value:'Low',          icon:'💧' },
              { label:'Sentiment Score',   value:'67 / 100',     icon:'📊' },
            ].map(item => (
              <div key={item.label} className="sig-card">
                <div className="text-xl mb-2">{item.icon}</div>
                <div className="text-[9px] font-bold text-[var(--text-dim)] uppercase tracking-wide mb-1">{item.label}</div>
                <div className="text-sm font-black text-[var(--text-primary)]">{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      </>)}
    </div>
  );
}
