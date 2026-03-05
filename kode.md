import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Zap, BarChart2, Star, Bell, Calendar, Briefcase, Settings,
  Moon, Sun, Monitor, TrendingUp, TrendingDown, Clock,
  ShieldAlert, Target, Copy, Send, ChevronRight, Search,
  Award, Flame, Activity, Maximize2, BellDot, History, CheckCircle2,
  Trophy, Percent, Wallet, Info, Volume2, VolumeX, AlertCircle, Share2,
  ArrowRight, MousePointer2, Cpu, Lock, CheckCircle, Smartphone,
  Filter, MessageSquare, LayoutGrid, Globe, ShieldCheck, Droplet,
  BrainCircuit, Bot, Webhook, BookOpen, Users, CreditCard,
  ChevronUp, ChevronDown, ArrowUpRight, ArrowDownRight
} from 'lucide-react';

// ─── DATA & CONFIG ────────────────────────────────────────────────────────────
const PAIRS = [
  { symbol: 'XAUUSD', name: 'Gold / USD',     base: 2034.50, vol: 0.8,   type: 'Commodity', trend: [30,45,40,60,55,75,70,65,80,75] },
  { symbol: 'BTCUSD', name: 'Bitcoin / USD',  base: 64230.15,vol: 25.0,  type: 'Crypto',    trend: [50,40,70,60,90,80,100,85,95,90] },
  { symbol: 'NVDA',   name: 'NVIDIA Corp.',   base: 176.32,  vol: 1.5,   type: 'Stock',     trend: [60,55,65,75,70,85,90,80,88,92] },
  { symbol: 'EURUSD', name: 'Euro / USD',     base: 1.0854,  vol:0.0006, type: 'Forex',     trend: [20,25,22,30,28,35,32,38,30,36] },
  { symbol: 'TSLA',   name: 'Tesla Inc.',     base: 247.10,  vol: 3.2,   type: 'Stock',     trend: [80,70,75,65,60,70,80,75,85,78] },
  { symbol: 'USDJPY', name: 'USD / Yen',      base: 149.85,  vol: 0.12,  type: 'Forex',     trend: [40,50,45,55,60,58,65,62,70,67] },
];

const GLOBAL_INDICES = [
  { name: 'S&P 500',    value: 5274.39, change: -14.39, pct: -0.27 },
  { name: 'DOW30',      value: 38772.81,change: -213.81,pct: -0.55 },
  { name: 'HANGSENG',   value: 25183.57,change: +123.57,pct: +0.49 },
  { name: 'NIKKEI225',  value: 40142.15,change: +122.15,pct: +0.31 },
  { name: 'SHANGHAI',   value: 3829.23, change: -12.23, pct: -0.32 },
  { name: 'FTSE',       value: 9624.89, change: -122.89,pct: -1.26 },
];

const NEWS_FEED = [
  "🔥 FED beri sinyal tahan suku bunga Q3",
  "📈 Emas melonjak usai rilis data CPI rendah",
  "🚀 BTC tembus resistensi kuat $65k",
  "💡 Pasar global reli didorong sektor teknologi",
  "⚡ NVIDIA catat rekor pendapatan Q4",
];

const AI_ANALYSIS = {
  trend: "BULLISH", strength: 8.7,
  logic: [
    "Liquidity sweep terdeteksi di 2028.50",
    "Order block tervalidasi pada H1",
    "Momentum bullish divergence (RSI)",
  ],
};

const MACRO_DATA = [
  { title: "Fed Rate",   value: "5.50%", impact: "HIGH",   bias: "BEARISH USD" },
  { title: "CPI YoY",    value: "3.2%",  impact: "HIGH",   bias: "BULLISH GOLD" },
  { title: "NFP",        value: "187K",  impact: "MEDIUM", bias: "USD NEUTRAL" },
  { title: "DXY",        value: "104.2", impact: "MEDIUM", bias: "USD STRONG" },
];

const MORE_CATEGORIES = [
  { title: "Alat AI Premium", highlight: true, items: [
    { id: 'ai_signal',   label: 'Sinyal AI Pro',    icon: Zap,         pro: true },
    { id: 'ai_analysis', label: 'Analisa Multi-TF', icon: BrainCircuit,pro: true },
    { id: 'ai_backtest', label: 'Mesin Backtest',   icon: Activity,    pro: true },
    { id: 'risk_manager',label: 'Manajemen Risiko', icon: ShieldCheck, pro: true },
  ]},
  { title: "Alat Trading", items: [
    { id: 'screener',   label: 'Screener Aset',     icon: Filter },
    { id: 'calendars',  label: 'Kalender Ekonomi',  icon: Calendar },
    { id: 'sentiment',  label: 'Sentimen Pasar',    icon: BarChart2 },
    { id: 'liquidity',  label: 'Peta Likuiditas',   icon: Droplet },
  ]},
  { title: "Otomatisasi", items: [
    { id: 'alerts',   label: 'Peringatan Harga', icon: Bell },
    { id: 'telegram', label: 'Bot Telegram',     icon: Bot },
    { id: 'webhook',  label: 'API / Webhook',    icon: Webhook },
  ]},
  { title: "Utilitas & Komunitas", items: [
    { id: 'journal',      label: 'Jurnal Trading',   icon: BookOpen },
    { id: 'forum',        label: 'Forum VIP',        icon: Users },
    { id: 'leaderboard',  label: 'Papan Peringkat',  icon: Trophy },
    { id: 'subscription', label: 'Langganan',        icon: CreditCard },
  ]},
];

const generateSignal = (pairSymbol) => {
  const pair = PAIRS.find(p => p.symbol === pairSymbol) || PAIRS[0];
  const type = Math.random() > 0.45 ? 'BUY' : 'SELL';
  const score = Math.random() * 10;
  const precision = pair.type === 'Forex' ? 4 : 2;
  const entryPrice = (pair.base + (Math.random() - 0.5) * pair.vol * 10).toFixed(precision);
  return {
    id: Math.random().toString(36).substr(2, 9),
    pair: pairSymbol, type,
    grade: score > 9 ? 'A+' : score > 7 ? 'A' : 'B+',
    level: score > 9 ? 'HOT' : score > 7 ? 'VALID' : 'WAIT',
    entry: entryPrice,
    sl:  (parseFloat(entryPrice) * (type === 'BUY' ? 0.990 : 1.010)).toFixed(precision),
    tp1: (parseFloat(entryPrice) * (type === 'BUY' ? 1.015 : 0.985)).toFixed(precision),
    tp2: (parseFloat(entryPrice) * (type === 'BUY' ? 1.028 : 0.972)).toFixed(precision),
    confidence: Math.floor(Math.random() * 3) + 7,
    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    rr: '1:2.5',
  };
};

// ─── SPARKLINE ────────────────────────────────────────────────────────────────
function Sparkline({ data, color, width = 80, height = 32 }) {
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - ((v - min) / range) * (height - 4) - 2;
    return `${x},${y}`;
  }).join(' ');
  return (
    <svg width={width} height={height} className="overflow-visible">
      <defs>
        <linearGradient id={`sg-${color}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity="0.3"/>
          <stop offset="100%" stopColor={color} stopOpacity="0"/>
        </linearGradient>
      </defs>
      <polyline points={pts} fill="none" stroke={color} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round"/>
    </svg>
  );
}

// ─── CANDLE CHART ─────────────────────────────────────────────────────────────
function MiniCandleChart({ pair }) {
  const candles = useMemo(() => {
    const c = []; let price = pair.base;
    for (let i = 0; i < 40; i++) {
      const open = price;
      const close = price + (Math.random() - 0.48) * pair.vol * 8;
      const high = Math.max(open, close) + Math.random() * pair.vol * 3;
      const low = Math.min(open, close) - Math.random() * pair.vol * 3;
      c.push({ open, close, high, low });
      price = close;
    }
    return c;
  }, [pair.symbol, pair.base, pair.vol]);

  const allVals = candles.flatMap(c => [c.high, c.low]);
  const min = Math.min(...allVals), max = Math.max(...allVals);
  const range = max - min || 1;
  const W = 600, H = 160, pad = 4;
  const cw = W / candles.length;

  const toY = (v) => H - pad - ((v - min) / range) * (H - pad * 2);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-full" preserveAspectRatio="none">
      {candles.map((c, i) => {
        const x = i * cw + cw / 2;
        const isUp = c.close >= c.open;
        const col = isUp ? '#10b981' : '#ef4444';
        const bodyTop = toY(Math.max(c.open, c.close));
        const bodyBot = toY(Math.min(c.open, c.close));
        const bodyH = Math.max(bodyBot - bodyTop, 1);
        return (
          <g key={i}>
            <line x1={x} y1={toY(c.high)} x2={x} y2={toY(c.low)} stroke={col} strokeWidth="0.8" opacity="0.7"/>
            <rect x={x - cw * 0.35} y={bodyTop} width={cw * 0.7} height={bodyH} fill={col} opacity="0.9" rx="0.5"/>
          </g>
        );
      })}
    </svg>
  );
}

// ─── MAIN APP ─────────────────────────────────────────────────────────────────
export default function App() {
  const [activeMenu, setActiveMenu]     = useState('signal');
  const [activePair, setActivePair]     = useState('XAUUSD');
  const [prices, setPrices]             = useState({});
  const [currentSignal, setCurrentSignal] = useState(null);
  const [isNewSignal, setIsNewSignal]   = useState(false);
  const [isLoading, setIsLoading]       = useState(true);
  const [eta, setEta]                   = useState(15);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showAlert, setShowAlert]       = useState(false);
  const [chartPair, setChartPair]       = useState(PAIRS[0]);

  const audioRef = useRef(null);
  const prevPricesRef = useRef({});
  const startTimeRef = useRef(Date.now());

  useEffect(() => () => { if (audioRef.current) { audioRef.current.pause(); audioRef.current = null; } }, []);

  useEffect(() => {
    const t = setTimeout(() => {
      const init = {}; PAIRS.forEach(p => init[p.symbol] = p.base);
      setPrices(init);
      setCurrentSignal(generateSignal('XAUUSD'));
      setIsLoading(false);
    }, 1800);
    const priceIv = setInterval(() => {
      setPrices(prev => {
        const next = { ...prev };
        PAIRS.forEach(p => next[p.symbol] = (prev[p.symbol] || p.base) + (Math.random() - 0.5) * p.vol);
        return next;
      });
    }, 1000);
    const timerIv = setInterval(() => {
      const diff = Math.floor((Date.now() - startTimeRef.current) / 1000);
      setEta(15 - (diff % 15));
    }, 1000);
    return () => { clearTimeout(t); clearInterval(priceIv); clearInterval(timerIv); };
  }, []);

  useEffect(() => {
    if (isLoading) return;
    let t1, t2;
    const iv = setInterval(() => {
      const sig = generateSignal(activePair);
      setCurrentSignal(sig); setIsNewSignal(true); setShowAlert(true);
      startTimeRef.current = Date.now(); setEta(15);
      if (soundEnabled) {
        if (!audioRef.current) { audioRef.current = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3'); audioRef.current.volume = 0.3; }
        audioRef.current.currentTime = 0; audioRef.current.play().catch(() => {});
      }
      t1 = setTimeout(() => setIsNewSignal(false), 2000);
      t2 = setTimeout(() => setShowAlert(false), 5000);
    }, 15000);
    return () => { clearInterval(iv); clearTimeout(t1); clearTimeout(t2); };
  }, [activePair, isLoading, soundEnabled]);

  const priceDirections = useMemo(() => {
    const map = {};
    PAIRS.forEach(p => {
      const cur = prices[p.symbol], prev = prevPricesRef.current[p.symbol];
      if (cur && prev) map[p.symbol] = cur > prev ? 'up' : cur < prev ? 'down' : null;
    });
    return map;
  }, [prices]);

  useEffect(() => { prevPricesRef.current = prices; }, [prices]);

  const loopPrices = useMemo(() => {
    const e = Object.entries(prices);
    return e.length < 12 ? [...e, ...e, ...e] : e;
  }, [prices]);

  const handleSelectPair = (symbol) => {
    if (navigator.vibrate) navigator.vibrate(30);
    const pair = PAIRS.find(p => p.symbol === symbol);
    setActivePair(symbol);
    if (pair) setChartPair(pair);
    setActiveMenu('signal');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (isLoading) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-[#0a0b0f] text-[#e0e0e8] font-sans overflow-hidden">
      <style dangerouslySetInnerHTML={{ __html: CSS }} />

      {/* TOP TICKER */}
      <div className="h-8 bg-[#0d0e12] border-b border-[#1c1d24] flex items-center overflow-hidden relative z-50">
        <div className="shrink-0 px-3 border-r border-[#1c1d24] flex items-center gap-2 h-full">
          <Zap size={12} className="text-yellow-400 fill-yellow-400" />
          <span className="text-[10px] font-black tracking-widest text-yellow-400 font-display">GAS PRO</span>
        </div>
        <div className="flex-1 overflow-hidden flex">
          <div className="ticker-scroll flex whitespace-nowrap gap-0 items-center">
            {loopPrices.map(([k, v], i) => {
              const pair = PAIRS.find(p => p.symbol === k);
              const base = pair?.base || 1;
              const chg = ((v - base) / base * 100);
              const isUp = chg >= 0;
              return (
                <span key={i} className="inline-flex items-center gap-2 px-4 border-r border-[#1c1d24] h-8 cursor-pointer hover:bg-[#14151c] transition-colors" onClick={() => handleSelectPair(k)}>
                  <span className="text-[10px] font-bold text-[#888]">{k}</span>
                  <span className={`text-[10px] font-mono font-bold ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                    {v ? v.toFixed(pair?.type === 'Forex' ? 4 : 2) : '--'}
                  </span>
                  <span className={`text-[9px] font-mono ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>{isUp ? '+' : ''}{chg.toFixed(2)}%</span>
                </span>
              );
            })}
          </div>
        </div>
        <div className="shrink-0 px-3 border-l border-[#1c1d24] flex items-center gap-2 h-full">
          <button onClick={() => setSoundEnabled(!soundEnabled)} className="text-[#555] hover:text-[#aaa] transition-colors">
            {soundEnabled ? <Volume2 size={12}/> : <VolumeX size={12}/>}
          </button>
        </div>
      </div>

      {/* LAYOUT */}
      <div className="flex h-[calc(100vh-32px)]">

        {/* SIDEBAR */}
        <aside className="w-14 md:w-[60px] xl:w-[220px] bg-[#0d0e12] border-r border-[#1c1d24] flex flex-col shrink-0 z-40">
          <div className="h-14 flex items-center justify-center xl:justify-start xl:px-5 border-b border-[#1c1d24]">
            <div className="xl:hidden w-8 h-8 rounded-lg bg-yellow-400/10 flex items-center justify-center">
              <Zap size={16} className="text-yellow-400 fill-yellow-400 pulse-dot" />
            </div>
            <span className="hidden xl:block text-sm font-black tracking-tight font-display">GOLDEN <span className="text-yellow-400">AI</span></span>
          </div>
          <nav className="flex-1 py-4 flex flex-col gap-1 overflow-y-auto scrollbar-none px-2">
            {[
              { id: 'signal',    icon: Zap,        label: 'Sinyal AI' },
              { id: 'markets',   icon: BarChart2,  label: 'Pasar' },
              { id: 'watchlist', icon: Star,       label: 'Favorit' },
              { id: 'portfolio', icon: Briefcase,  label: 'Portofolio' },
            ].map(item => (
              <SideBtn key={item.id} {...item} active={activeMenu === item.id} onClick={setActiveMenu} />
            ))}
            <div className="mx-2 my-3 border-t border-[#1c1d24]" />
            <SideBtn id="more"      icon={LayoutGrid} label="Alat Pro"   active={activeMenu === 'more'}      onClick={setActiveMenu} />
            <SideBtn id="alerts"    icon={Bell}       label="Alerts"     active={activeMenu === 'alerts'}    onClick={setActiveMenu} />
            <SideBtn id="calendars" icon={Calendar}   label="Kalender"   active={activeMenu === 'calendars'} onClick={setActiveMenu} />
            <div className="flex-1" />
            <SideBtn id="settings"  icon={Settings}   label="Pengaturan" active={activeMenu === 'settings'}  onClick={setActiveMenu} />
          </nav>
        </aside>

        {/* MAIN */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          {/* HEADER BAR */}
          <header className="h-14 bg-[#0d0e12] border-b border-[#1c1d24] flex items-center px-4 gap-4 shrink-0 z-30">
            <div className="flex items-center gap-2 bg-[#13141a] border border-[#1c1d24] rounded-md px-3 py-2 w-48 md:w-64 transition-all focus-within:border-[#2a2b35]">
              <Search size={14} className="text-[#555]" />
              <input type="text" placeholder="Cari pair aset..." className="bg-transparent text-xs text-[#ccc] outline-none w-full placeholder:text-[#444]" />
            </div>
            <div className="flex-1 hidden md:flex items-center gap-2 overflow-hidden px-2 border-l border-[#1c1d24]">
              {PAIRS.slice(0, 4).map(p => {
                const cur = prices[p.symbol] || p.base;
                const chg = ((cur - p.base) / p.base * 100);
                const isUp = chg >= 0;
                return (
                  <button key={p.symbol} onClick={() => handleSelectPair(p.symbol)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded transition-all ${activePair === p.symbol ? 'bg-yellow-400/10 text-yellow-400 border border-yellow-400/20' : 'border border-transparent text-[#777] hover:bg-[#14151c]'}`}>
                    <span className="text-[10px] font-bold">{p.symbol}</span>
                    <span className={`text-[10px] font-mono ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>{isUp ? '+' : ''}{chg.toFixed(2)}%</span>
                  </button>
                );
              })}
            </div>
            <div className="flex items-center gap-3 ml-auto">
              <div className="hidden sm:flex items-center gap-1 bg-[#13141a] border border-[#1c1d24] rounded p-1">
                {[{t:'dark',i:<Moon size={12}/>},{t:'light',i:<Sun size={12}/>},{t:'term',i:<Monitor size={12}/>}].map(({t,i}) => (
                  <button key={t} className={`p-1.5 rounded text-[10px] transition-colors ${t==='dark' ? 'bg-yellow-400 text-black' : 'text-[#555] hover:text-[#aaa]'}`}>{i}</button>
                ))}
              </div>
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 p-[1px] cursor-pointer shadow-[0_0_10px_rgba(250,204,21,0.2)]">
                <div className="w-full h-full bg-[#0a0b0f] rounded-full flex items-center justify-center text-[10px] font-black text-white">JD</div>
              </div>
            </div>
          </header>

          {/* NEWS TICKER */}
          <div className="h-6 bg-[#0f1016] border-b border-[#1c1d24] overflow-hidden flex shrink-0">
            <div className="shrink-0 px-3 bg-yellow-400 flex items-center h-full z-10 shadow-[2px_0_10px_rgba(0,0,0,0.5)]">
              <span className="text-[9px] font-black text-black uppercase tracking-widest">LIVE NEWS</span>
            </div>
            <div className="flex-1 overflow-hidden flex items-center">
              <div className="news-scroll flex whitespace-nowrap items-center">
                {[...NEWS_FEED, ...NEWS_FEED].map((n, i) => (
                  <span key={i} className="text-[10px] font-bold text-[#888] px-8 border-r border-[#1c1d24]">{n}</span>
                ))}
              </div>
            </div>
          </div>

          {/* CONTENT AREA */}
          <div className="flex-1 overflow-y-auto scrollbar-none">
            {activeMenu === 'signal'    && <SignalView signal={currentSignal} isNew={isNewSignal} timer={eta} chartPair={chartPair} prices={prices} directions={priceDirections} onSelect={handleSelectPair} activePair={activePair} />}
            {activeMenu === 'markets'   && <MarketsView prices={prices} directions={priceDirections} onSelect={handleSelectPair} activePair={activePair} />}
            {activeMenu === 'watchlist' && <EmptyView icon={<Star size={32}/>} label="Favorit Kosong" sub="Tambahkan aset ke daftar favorit Anda" />}
            {activeMenu === 'portfolio' && <PortfolioView />}
            {activeMenu === 'more'      && <AICommandCenter onSelect={id => setActiveMenu(id === 'ai_signal' ? 'signal' : id)} />}
            {activeMenu === 'settings'  && <SettingsView />}
            {activeMenu === 'alerts'    && <EmptyView icon={<Bell size={32}/>} label="Belum Ada Alert" sub="Buat alert harga baru dari halaman Markets" />}
            {activeMenu === 'calendars' && <CalendarView />}
          </div>
        </main>

        {/* RIGHT PANEL (xl only) */}
        <aside className="hidden xl:flex w-[320px] bg-[#0d0e12] border-l border-[#1c1d24] flex-col shrink-0 overflow-y-auto scrollbar-none">
          <div className="p-5 border-b border-[#1c1d24]">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-black uppercase tracking-widest text-[#555]">Inteligensi AI</span>
              <div className="w-2 h-2 rounded-full bg-emerald-400 pulse-dot" />
            </div>
            <p className={`text-3xl font-display font-black mb-4 ${AI_ANALYSIS.trend === 'BULLISH' ? 'text-emerald-400' : 'text-red-400'}`}>{AI_ANALYSIS.trend}</p>
            <div className="space-y-2">
              {AI_ANALYSIS.logic.map((l, i) => (
                <div key={i} className="flex items-start gap-3 text-[11px] p-3 rounded bg-[#13141a] border border-[#1c1d24]">
                  <ShieldAlert size={12} className="text-yellow-400 shrink-0 mt-0.5" />
                  <span className="text-[#aaa] leading-relaxed">{l}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="p-5 border-b border-[#1c1d24]">
            <span className="text-[10px] font-black uppercase tracking-widest text-[#555] mb-4 block">Fundamental Makro</span>
            {MACRO_DATA.map((m, i) => (
              <div key={i} className="flex justify-between items-center py-2.5 border-b border-[#1c1d24] last:border-0 text-[11px]">
                <span className="text-[#777] font-bold">{m.title}</span>
                <div className="text-right">
                  <span className="font-mono font-bold text-[#eee] mr-3">{m.value}</span>
                  <span className={`text-[9px] font-black ${m.impact === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}`}>{m.bias}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="p-5">
            <span className="text-[10px] font-black uppercase tracking-widest text-[#555] mb-4 block">Indeks Global</span>
            {GLOBAL_INDICES.map((g, i) => (
              <div key={i} className="flex justify-between items-center py-2 text-[11px]">
                <span className="text-[#777] font-bold w-24 truncate">{g.name}</span>
                <span className="font-mono font-bold text-[#ccc]">{g.value.toLocaleString()}</span>
                <span className={`font-mono font-bold w-16 text-right ${g.pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>{g.pct >= 0 ? '+' : ''}{g.pct.toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </aside>
      </div>

      {/* MOBILE BOTTOM NAV */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#0d0e12] border-t border-[#1c1d24] flex items-center justify-around z-50 px-2 pb-1">
        {[
          { id: 'signal',    icon: <Zap size={22}/>,        label: 'Sinyal' },
          { id: 'markets',   icon: <BarChart2 size={22}/>,  label: 'Pasar' },
          { id: 'watchlist', icon: <Star size={22}/>,       label: 'Favorit' },
          { id: 'portfolio', icon: <Briefcase size={22}/>,  label: 'Portofolio' },
          { id: 'more',      icon: <LayoutGrid size={22}/>, label: 'Menu' },
        ].map(({id, icon, label}) => (
          <button key={id} onClick={() => setActiveMenu(id)}
            className={`flex flex-col items-center justify-center w-14 h-full gap-1 transition-all ${activeMenu === id ? 'text-yellow-400' : 'text-[#555]'}`}>
            {React.cloneElement(icon, { className: activeMenu === id ? 'fill-current' : '' })}
            <span className="text-[8px] font-bold">{label}</span>
          </button>
        ))}
      </nav>

      {/* FLOATING ALERT PRO */}
      {showAlert && (
        <div className="fixed top-14 right-4 z-[300] slide-in">
          <div className="bg-[#0d0e12] border border-yellow-400/30 rounded-xl p-4 flex items-center gap-4 shadow-2xl min-w-[260px] overflow-hidden">
            <div className="w-10 h-10 rounded-lg bg-yellow-400/10 flex items-center justify-center shrink-0">
              <Zap size={20} className="text-yellow-400 fill-yellow-400 pulse-dot" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-[10px] text-yellow-400 font-black uppercase tracking-widest mb-0.5">Sinyal {currentSignal?.level}</p>
              <p className="text-sm font-bold text-white truncate">{currentSignal?.pair} · {currentSignal?.type}</p>
            </div>
            <div className="absolute bottom-0 left-0 h-[2px] bg-yellow-400 alert-bar" />
          </div>
        </div>
      )}
    </div>
  );
}

// ─── SIGNAL VIEW ──────────────────────────────────────────────────────────────
function SignalView({ signal, isNew, timer, chartPair, prices, directions, onSelect, activePair }) {
  if (!signal) return null;
  const isBuy = signal.type === 'BUY';
  const pairData = PAIRS.find(p => p.symbol === signal.pair) || PAIRS[0];
  const curPrice = prices[signal.pair] || pairData.base;

  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6">
      {/* Pair Quick Selector */}
      <div className="flex gap-3 overflow-x-auto scrollbar-none pb-2">
        {PAIRS.map(p => {
          const cur = prices[p.symbol] || p.base;
          const chg = ((cur - p.base) / p.base * 100);
          const isUp = chg >= 0;
          return (
            <button key={p.symbol} onClick={() => onSelect(p.symbol)}
              className={`shrink-0 flex flex-col px-4 py-2.5 rounded-lg border text-left transition-all ${activePair === p.symbol ? 'bg-yellow-400/10 border-yellow-400/30 text-yellow-400 shadow-[0_0_15px_rgba(250,204,21,0.05)]' : 'bg-[#0d0e12] border-[#1c1d24] text-[#666] hover:border-[#2a2b35]'}`}>
              <span className="text-[11px] font-bold">{p.symbol}</span>
              <span className={`text-[10px] font-mono mt-0.5 ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>{isUp ? '+' : ''}{chg.toFixed(2)}%</span>
            </button>
          );
        })}
      </div>

      <div className="grid xl:grid-cols-[1fr_360px] gap-6">
        {/* Left: Chart + Signal */}
        <div className="space-y-6">
          {/* Pro Chart Panel */}
          <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl overflow-hidden">
            <div className="flex items-center justify-between px-5 py-4 border-b border-[#1c1d24]">
              <div className="flex items-center gap-4">
                <div>
                  <span className="text-base font-black text-white">{chartPair.symbol}</span>
                  <span className="text-xs text-[#555] ml-2">{chartPair.name}</span>
                </div>
                <div className="h-6 w-px bg-[#1c1d24]"></div>
                <span className={`text-lg font-mono font-bold ${isBuy ? 'text-emerald-400' : 'text-red-400'}`}>{curPrice.toFixed(pairData.type === 'Forex' ? 4 : 2)}</span>
              </div>
              <div className="flex items-center gap-2 bg-[#13141a] p-1 rounded border border-[#1c1d24]">
                {['1m','5m','15m','1h','4h','1d'].map(tf => (
                  <button key={tf} className={`text-[10px] px-3 py-1 rounded transition-colors ${tf === '15m' ? 'bg-[#2a2b35] text-white font-bold' : 'text-[#666] hover:text-[#aaa]'}`}>{tf}</button>
                ))}
              </div>
            </div>
            <div className="h-56 p-4">
              <MiniCandleChart pair={chartPair} />
            </div>
            <div className="grid grid-cols-4 divide-x divide-[#1c1d24] border-t border-[#1c1d24] bg-[#13141a]">
              {[['Open', (curPrice * 0.999).toFixed(2)], ['High', (curPrice * 1.003).toFixed(2)], ['Low', (curPrice * 0.997).toFixed(2)], ['Vol', '1.24B']].map(([k, v]) => (
                <div key={k} className="px-5 py-3">
                  <p className="text-[10px] text-[#555] uppercase font-bold">{k}</p>
                  <p className="text-xs font-mono font-bold text-[#ddd] mt-1">{v}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Pro Signal Card */}
          <div className={`bg-[#0d0e12] border rounded-xl p-6 transition-all duration-300 relative overflow-hidden ${isNew ? 'border-yellow-400/40 shadow-[0_0_30px_rgba(250,204,21,0.1)]' : 'border-[#1c1d24]'}`}>
            <div className={`absolute -top-20 -right-20 w-64 h-64 blur-[120px] opacity-20 ${isBuy ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
            
            <div className="flex items-start justify-between mb-6 relative z-10">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <span className={`text-[10px] font-black px-2.5 py-1 rounded-md uppercase tracking-widest ${isBuy ? 'bg-emerald-400/10 text-emerald-400 border border-emerald-400/20' : 'bg-red-400/10 text-red-400 border border-red-400/20'}`}>
                    {signal.level} SETUP
                  </span>
                  <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-bold">
                    <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full pulse-dot" />LIVE
                  </div>
                </div>
                <p className="text-3xl font-display font-black text-white">{signal.pair}</p>
                <p className="text-[10px] text-[#666] mt-1 font-bold">{signal.timestamp} · M15 TIMEFRAME · GRADE {signal.grade}</p>
              </div>
              <div className={`px-6 py-3 rounded-lg text-lg font-black shadow-lg border ${isBuy ? 'bg-emerald-400 text-black border-emerald-300' : 'bg-red-400 text-white border-red-300'}`}>
                {signal.type}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6 relative z-10">
              <PriceBox label="Entry Level" value={signal.entry} />
              <PriceBox label="Stop Loss" value={signal.sl} color={isBuy ? 'red' : 'green'} />
              <PriceBox label="Take Profit 1" value={signal.tp1} color={isBuy ? 'green' : 'red'} />
              <PriceBox label="Take Profit 2" value={signal.tp2} color={isBuy ? 'green' : 'red'} highlight />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 relative z-10">
              <div className="bg-[#13141a] border border-[#1c1d24] rounded-lg p-4">
                <div className="flex justify-between items-center mb-2">
                  <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest">Akurasi AI</p>
                  <span className={`text-sm font-black ${isBuy ? 'text-emerald-400' : 'text-red-400'}`}>{signal.confidence * 10}%</span>
                </div>
                <div className="h-2 bg-[#1c1d24] rounded-full overflow-hidden">
                  <div className={`h-full rounded-full transition-all duration-1000 ${isBuy ? 'bg-emerald-400 shadow-[0_0_10px_#34d399]' : 'bg-red-400 shadow-[0_0_10px_#f87171]'}`} style={{ width: `${signal.confidence * 10}%` }} />
                </div>
              </div>
              <div className="bg-[#13141a] border border-[#1c1d24] rounded-lg p-4 flex justify-between items-center">
                <div>
                  <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">Berlaku Dalam</p>
                  <div className="flex items-center gap-2">
                    <Clock size={14} className="text-yellow-400" />
                    <span className="font-mono font-black text-yellow-400 text-xl">{timer}s</span>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-1">R:R Rasio</p>
                  <span className="font-mono font-black text-white text-lg">{signal.rr}</span>
                </div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 relative z-10">
              <button className="flex items-center justify-center gap-2 py-3.5 rounded-lg bg-[#13141a] border border-[#1c1d24] text-xs font-bold text-[#888] hover:border-[#2a2b35] hover:text-[#ccc] transition-colors">
                <Copy size={14}/> Salin Level
              </button>
              <button className="flex items-center justify-center gap-2 py-3.5 rounded-lg bg-[#13141a] border border-[#1c1d24] text-xs font-bold text-[#888] hover:border-[#2a2b35] hover:text-[#ccc] transition-colors">
                <Share2 size={14}/> Bagikan
              </button>
              <button className={`flex items-center justify-center gap-2 py-3.5 rounded-lg text-sm font-black transition-all shadow-lg ${isBuy ? 'bg-emerald-400 text-black hover:bg-emerald-300' : 'bg-red-400 text-white hover:bg-red-300'}`}>
                <Zap size={16} className="fill-current"/> Eksekusi Instan
              </button>
            </div>
          </div>
        </div>

        {/* Right: Market Summary (visible on smaller xl) */}
        <div className="xl:hidden space-y-6">
          <MacroSidebar />
        </div>
      </div>
    </div>
  );
}

function PriceBox({ label, value, color, highlight }) {
  const cls = color === 'green' ? 'text-emerald-400' : color === 'red' ? 'text-red-400' : 'text-white';
  return (
    <div className={`bg-[#13141a] rounded-lg p-4 border ${highlight ? 'border-yellow-400/20 shadow-[0_0_15px_rgba(250,204,21,0.05)]' : 'border-[#1c1d24]'}`}>
      <p className="text-[10px] text-[#666] font-bold uppercase tracking-widest mb-2">{label}</p>
      <p className={`font-mono font-black text-lg ${cls}`}>{value}</p>
    </div>
  );
}

// ─── MARKETS VIEW ─────────────────────────────────────────────────────────────
function MarketsView({ prices, directions, onSelect, activePair }) {
  const [tab, setTab] = useState('Aktif');
  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6">
      <div className="flex justify-between items-end">
        <div>
          <h2 className="text-2xl font-display font-black text-white uppercase">Market Hub</h2>
          <p className="text-[10px] text-[#555] uppercase tracking-widest mt-1">Data Feed Real-time</p>
        </div>
      </div>

      <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl overflow-hidden">
        <div className="flex items-center gap-0 border-b border-[#1c1d24] bg-[#13141a]">
          {['Aktif', 'Top Gainer', 'Top Loser', 'Kripto', 'Forex'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              className={`px-6 py-3.5 text-xs font-bold border-b-2 transition-colors ${tab === t ? 'border-yellow-400 text-yellow-400 bg-[#1c1d24]/50' : 'border-transparent text-[#666] hover:text-[#aaa]'}`}>{t}</button>
          ))}
        </div>
        <div className="overflow-x-auto scrollbar-none">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-[#555] border-b border-[#1c1d24] bg-[#0d0e12]">
                <th className="text-left px-5 py-3 font-bold uppercase tracking-widest">Simbol</th>
                <th className="text-right px-5 py-3 font-bold uppercase tracking-widest">Harga</th>
                <th className="text-right px-5 py-3 font-bold uppercase tracking-widest">Perubahan</th>
                <th className="text-right px-5 py-3 font-bold uppercase tracking-widest">%</th>
                <th className="text-right px-5 py-3 font-bold uppercase tracking-widest hidden sm:table-cell">Tren 24J</th>
              </tr>
            </thead>
            <tbody>
              {PAIRS.map(p => {
                const cur = prices[p.symbol] || p.base;
                const chg = cur - p.base;
                const pct = (chg / p.base * 100);
                const isUp = pct >= 0;
                const dir = directions[p.symbol];
                return (
                  <tr key={p.symbol} onClick={() => onSelect(p.symbol)}
                    className={`border-b border-[#1c1d24] cursor-pointer transition-colors ${activePair === p.symbol ? 'bg-yellow-400/5' : 'hover:bg-[#13141a]'}`}>
                    <td className="px-5 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-[#1c1d24] flex items-center justify-center text-[10px] font-black text-[#aaa]">{p.symbol.slice(0,2)}</div>
                        <div>
                          <p className="font-bold text-[#eee] text-sm">{p.symbol}</p>
                          <p className="text-[10px] text-[#555] mt-0.5">{p.name}</p>
                        </div>
                      </div>
                    </td>
                    <td className={`px-5 py-3 text-right font-mono font-bold text-sm transition-colors ${dir === 'up' ? 'text-emerald-400' : dir === 'down' ? 'text-red-400' : 'text-[#ccc]'}`}>
                      {cur.toFixed(p.type === 'Forex' ? 4 : 2)}
                    </td>
                    <td className={`px-5 py-3 text-right font-mono ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                      {isUp ? '+' : ''}{chg.toFixed(p.type === 'Forex' ? 4 : 2)}
                    </td>
                    <td className={`px-5 py-3 text-right font-mono font-bold ${isUp ? 'text-emerald-400' : 'text-red-400'}`}>
                      <div className="flex items-center justify-end gap-1">
                        {isUp ? <ChevronUp size={12}/> : <ChevronDown size={12}/>}
                        {Math.abs(pct).toFixed(2)}%
                      </div>
                    </td>
                    <td className="px-5 py-3 text-right hidden sm:table-cell">
                      <Sparkline data={p.trend} color={isUp ? '#10b981' : '#ef4444'} width={80} height={28} />
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── MACRO SIDEBAR ────────────────────────────────────────────────────────────
function MacroSidebar() {
  return (
    <div className="space-y-6">
      <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl p-5">
        <span className="text-[10px] font-black uppercase tracking-widest text-[#555] mb-4 block">Fundamental Makro</span>
        {MACRO_DATA.map((m, i) => (
          <div key={i} className="flex justify-between items-center py-3 border-b border-[#1c1d24] last:border-0 last:pb-0 text-xs">
            <span className="text-[#888] font-bold">{m.title}</span>
            <div className="text-right">
              <span className="font-mono font-bold text-[#eee] mr-3">{m.value}</span>
              <span className={`text-[9px] font-black tracking-wider ${m.impact === 'HIGH' ? 'text-red-400' : 'text-yellow-400'}`}>{m.bias}</span>
            </div>
          </div>
        ))}
      </div>
      <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl p-5">
        <div className="flex items-center justify-between mb-4">
          <span className="text-[10px] font-black uppercase tracking-widest text-[#555]">Logika AI</span>
          <div className="flex items-center gap-1.5 text-[10px] text-emerald-400 font-bold">
            <div className="w-1.5 h-1.5 bg-emerald-400 rounded-full pulse-dot" />
            LIVE
          </div>
        </div>
        <p className={`text-2xl font-display font-black mb-4 ${AI_ANALYSIS.trend === 'BULLISH' ? 'text-emerald-400' : 'text-red-400'}`}>{AI_ANALYSIS.trend}</p>
        <div className="space-y-2">
          {AI_ANALYSIS.logic.map((l, i) => (
            <div key={i} className="flex items-start gap-3 text-[11px] p-3 rounded-lg bg-[#13141a] border border-[#1c1d24]">
              <ShieldAlert size={12} className="text-yellow-400 shrink-0 mt-0.5" />
              <span className="text-[#aaa] leading-relaxed">{l}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── PORTFOLIO VIEW ────────────────────────────────────────────────────────────
function PortfolioView() {
  const stats = [
    { label: 'Saldo', value: '$18,410.50', sub: 'Total Ekuitas Aktif' },
    { label: 'P&L Hari Ini', value: '+$420.00', sub: '+2.34% vs Kemarin', green: true },
    { label: 'Win Rate', value: '72.5%', sub: 'Dari 1,240 Total Trade' },
    { label: 'Drawdown', value: '-4.2%', sub: 'Maksimal Drawdown', red: true },
  ];
  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
      <h2 className="text-2xl font-display font-black text-white uppercase">Portofolio Akun</h2>
      
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {stats.map((s, i) => (
          <div key={i} className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl p-6">
            <p className="text-[10px] text-[#555] font-bold uppercase tracking-widest mb-2">{s.label}</p>
            <p className={`text-3xl font-black font-mono mb-1 ${s.green ? 'text-emerald-400' : s.red ? 'text-red-400' : 'text-white'}`}>{s.value}</p>
            <p className="text-[10px] text-[#777] font-bold">{s.sub}</p>
          </div>
        ))}
      </div>

      <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl overflow-hidden mt-6">
        <div className="px-6 py-4 border-b border-[#1c1d24] flex items-center justify-between bg-[#13141a]">
          <span className="text-xs font-black uppercase text-[#ccc] tracking-widest">Riwayat Trade</span>
          <button className="text-[10px] font-bold text-yellow-400 hover:text-yellow-300">Export CSV</button>
        </div>
        <div className="overflow-x-auto scrollbar-none">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-[#555] border-b border-[#1c1d24] bg-[#0d0e12]">
                {['Waktu','Aset','Aksi','Harga Entry','Ukuran (Lot)','P&L'].map(h => (
                  <th key={h} className="px-6 py-3 text-left font-bold uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[
                { t:'11:20:41', a:'XAUUSD', act:'BUY',  p:'2031.50', l:'0.10', pl:'+$84.00', up:true },
                { t:'11:13:41', a:'BTCUSD', act:'SELL', p:'64105.00',l:'0.01', pl:'-$32.00', up:false},
                { t:'11:06:41', a:'NVDA',   act:'BUY',  p:'175.49',  l:'10',   pl:'+$62.00', up:true },
                { t:'10:52:41', a:'EURUSD', act:'BUY',  p:'1.0851',  l:'0.50', pl:'+$31.00', up:true },
                { t:'09:14:22', a:'XAUUSD', act:'SELL', p:'2040.10', l:'0.10', pl:'-$12.50', up:false},
              ].map((r,i) => (
                <tr key={i} className="border-b border-[#1c1d24] hover:bg-[#13141a] transition-colors cursor-pointer">
                  <td className="px-6 py-4 text-[#777] font-mono">{r.t}</td>
                  <td className="px-6 py-4 font-bold text-[#eee]">{r.a}</td>
                  <td className="px-6 py-4">
                    <span className={`px-2.5 py-1 rounded text-[9px] font-black tracking-widest ${r.up ? 'bg-emerald-400/10 text-emerald-400' : 'bg-red-400/10 text-red-400'}`}>
                      {r.act}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-mono text-[#bbb]">{r.p}</td>
                  <td className="px-6 py-4 font-mono text-[#888]">{r.l}</td>
                  <td className={`px-6 py-4 font-mono font-bold ${r.up ? 'text-emerald-400' : 'text-red-400'}`}>{r.pl}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── AI COMMAND CENTER ────────────────────────────────────────────────────────
function AICommandCenter({ onSelect }) {
  return (
    <div className="p-4 md:p-6 space-y-8 pb-24 md:pb-6 max-w-7xl mx-auto">
      <div>
        <h2 className="text-2xl font-display font-black text-white uppercase">Pusat Komando AI</h2>
        <p className="text-[10px] text-[#666] uppercase tracking-widest mt-1 font-bold">Suite Alat Trading Kelas Pro</p>
      </div>

      {MORE_CATEGORIES.map((cat, idx) => (
        <div key={idx} className="space-y-4">
          <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[#555] px-1">{cat.title}</p>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {cat.items.map(item => (
              <button key={item.id} onClick={() => onSelect(item.id)}
                className={`p-5 rounded-xl border text-left transition-all hover:-translate-y-1 ${cat.highlight ? 'bg-[#13141a] border-yellow-400/30 hover:border-yellow-400 shadow-[0_4px_20px_rgba(250,204,21,0.05)]' : 'bg-[#0d0e12] border-[#1c1d24] hover:border-[#2a2b35] hover:bg-[#13141a]'}`}>
                <div className="flex justify-between items-start mb-4">
                  <div className={`p-2.5 rounded-lg ${cat.highlight ? 'bg-yellow-400/10 text-yellow-400' : 'bg-[#1c1d24] text-[#888]'}`}>
                    <item.icon size={20} />
                  </div>
                  {item.pro && <span className="text-[8px] bg-yellow-400 text-black font-black px-2 py-0.5 rounded uppercase tracking-wider">Pro</span>}
                </div>
                <span className={`text-xs font-bold block mb-1 ${cat.highlight ? 'text-[#eee]' : 'text-[#ccc]'}`}>{item.label}</span>
                <span className="text-[10px] text-[#555]">Akses modul {item.label.toLowerCase()}</span>
              </button>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── CALENDAR VIEW ────────────────────────────────────────────────────────────
function CalendarView() {
  const events = [
    { date: 'Mar 6',  name: 'ADP Non-Farm Employment', impact: 'HIGH',   time: '13:15' },
    { date: 'Mar 7',  name: 'US Unemployment Claims',  impact: 'MEDIUM', time: '13:30' },
    { date: 'Mar 8',  name: 'Non-Farm Payrolls',        impact: 'HIGH',   time: '13:30' },
    { date: 'Mar 12', name: 'CPI Month over Month',     impact: 'HIGH',   time: '13:30' },
    { date: 'Mar 19', name: 'FOMC Statement',           impact: 'HIGH',   time: '18:00' },
  ];
  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-5xl mx-auto">
      <h2 className="text-2xl font-display font-black text-white uppercase">Kalender Ekonomi</h2>
      <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl overflow-hidden">
        <table className="w-full text-xs">
          <thead><tr className="text-[#555] border-b border-[#1c1d24] bg-[#13141a]">
            {['Tanggal','Waktu','Event','Impact'].map(h => <th key={h} className="px-6 py-3.5 text-left font-bold uppercase tracking-wider">{h}</th>)}
          </tr></thead>
          <tbody>
            {events.map((e, i) => (
              <tr key={i} className="border-b border-[#1c1d24] hover:bg-[#13141a] transition-colors">
                <td className="px-6 py-4 text-[#777] font-mono">{e.date}</td>
                <td className="px-6 py-4 text-[#888] font-mono">{e.time}</td>
                <td className="px-6 py-4 font-bold text-[#eee]">{e.name}</td>
                <td className="px-6 py-4">
                  <span className={`px-2.5 py-1 rounded text-[9px] font-black tracking-widest ${e.impact === 'HIGH' ? 'bg-red-400/10 text-red-400' : 'bg-yellow-400/10 text-yellow-400'}`}>{e.impact}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// ─── SETTINGS VIEW ────────────────────────────────────────────────────────────
function SettingsView() {
  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-2xl mx-auto">
      <h2 className="text-2xl font-display font-black text-white uppercase">Pengaturan Terminal</h2>
      <div className="bg-[#0d0e12] border border-[#1c1d24] rounded-xl divide-y divide-[#1c1d24]">
        {[
          { label: 'Notifikasi Sinyal Push', sub: 'Terima notifikasi di browser/HP saat sinyal baru', checked: true },
          { label: 'Audio Alert System', sub: 'Mainkan suara (ping) saat sinyal HOT masuk', checked: true },
          { label: 'Auto Refresh Data Feed', sub: 'Refresh harga real-time via WebSocket', checked: true },
          { label: 'Mode Gelap Ekstrem', sub: 'Gunakan palet warna High-Contrast Pro Terminal', checked: true },
        ].map((s, i) => (
          <div key={i} className="flex items-center justify-between px-6 py-5">
            <div>
              <p className="text-sm font-bold text-[#eee] mb-1">{s.label}</p>
              <p className="text-[10px] text-[#666]">{s.sub}</p>
            </div>
            <div className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${s.checked ? 'bg-yellow-400' : 'bg-[#2a2b35]'}`}>
              <div className={`absolute top-1 w-3 h-3 rounded-full bg-black transition-all ${s.checked ? 'left-6' : 'left-1'}`} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── EMPTY STATE ──────────────────────────────────────────────────────────────
function EmptyView({ icon, label, sub }) {
  return (
    <div className="flex flex-col items-center justify-center h-[60vh] text-center p-8">
      <div className="text-[#2a2b35] mb-6 scale-150">{icon}</div>
      <p className="font-display font-black text-[#555] text-xl uppercase tracking-widest">{label}</p>
      <p className="text-xs text-[#444] mt-2 font-bold">{sub}</p>
    </div>
  );
}

// ─── SIDEBAR BUTTON ───────────────────────────────────────────────────────────
function SideBtn({ icon: Icon, label, id, active, onClick }) {
  return (
    <button onClick={() => onClick(id)}
      className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all relative group ${active ? 'bg-[#1c1d24] text-yellow-400' : 'text-[#666] hover:bg-[#13141a] hover:text-[#aaa]'}`}>
      {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-1 bg-yellow-400 rounded-r" />}
      <Icon size={18} className={`mx-auto xl:mx-0 ${active ? 'text-yellow-400' : ''}`} />
      <span className="hidden xl:block text-[11px] font-bold tracking-wider truncate">{label}</span>
    </button>
  );
}

// ─── LOADING ──────────────────────────────────────────────────────────────────
function LoadingScreen() {
  return (
    <div className="min-h-screen bg-[#0a0b0f] flex flex-col items-center justify-center gap-8">
      <style dangerouslySetInnerHTML={{ __html: `
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800&family=DM+Sans:wght@400;500;700&display=swap');
        * { font-family: 'DM Sans', sans-serif; }
        @keyframes pulse-dot-anim { 0%,100%{opacity:1} 50%{opacity:0.4} }
        .pulse-dot { animation: pulse-dot-anim 1.5s ease-in-out infinite; }
        @keyframes loading-bar { 0%{width:0%;opacity:1} 80%{width:100%;opacity:1} 100%{width:100%;opacity:0} }
        .loading-bar { animation: loading-bar 1.8s ease-in-out forwards; }
      `}} />
      <div className="w-16 h-16 rounded-2xl bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center pulse-dot shadow-[0_0_30px_rgba(250,204,21,0.1)]">
        <Zap size={28} className="text-yellow-400 fill-yellow-400" />
      </div>
      <div className="space-y-3 w-64 text-center">
        <div className="h-1 bg-[#1c1d24] rounded-full overflow-hidden">
          <div className="h-full bg-yellow-400 loading-bar" />
        </div>
        <p className="text-[10px] font-bold text-[#555] uppercase tracking-[0.5em]">Memuat Mesin v3.0 Pro</p>
      </div>
    </div>
  );
}