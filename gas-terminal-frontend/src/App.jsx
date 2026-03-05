import React, { useState, useEffect, useMemo, useRef } from 'react';
import {
  Zap, BarChart2, Star, Briefcase, Settings,
  Moon, Sun, Monitor, Bell, Search, LayoutGrid, Calendar
} from 'lucide-react';

import { PAIRS, GLOBAL_INDICES, MACRO_DATA, AI_ANALYSIS, NEWS_FEED } from './constants';
import { fetchOverview } from './services/api';
import { useWebSocket } from './hooks/useWebSocket';

import LoadingScreen from './components/LoadingScreen';
import SideBtn from './components/SideBtn';
import EmptyView from './components/EmptyView';
import PortfolioView from './components/PortfolioView';
import CalendarView from './components/CalendarView';
import SettingsView from './components/SettingsView';
import AICommandCenter from './components/AICommandCenter';
import MarketsView from './components/MarketsView';
import SignalView from './components/SignalView';

export default function App() {
  const [activeMenu, setActiveMenu] = useState('signal');
  const [theme, setTheme] = useState(() => localStorage.getItem('gas-theme') || 'dark');
  const [activePair, setActivePair] = useState('XAUUSD');
  const [pairs, setPairs] = useState(PAIRS);
  const [prices, setPrices] = useState({});
  const [currentSignal, setCurrentSignal] = useState(null);
  const [isNewSignal, setIsNewSignal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [eta, setEta] = useState(15);
  const [soundEnabled, setSoundEnabled] = useState(true);
  const [showAlert, setShowAlert] = useState(false);
  const [chartPair, setChartPair] = useState(PAIRS[0]);

  const [news, setNews] = useState(NEWS_FEED);
  const [globalIndices, setGlobalIndices] = useState(GLOBAL_INDICES);
  const [macroData, setMacroData] = useState(MACRO_DATA);
  const [aiAnalysis, setAiAnalysis] = useState(AI_ANALYSIS);

  const audioRef = useRef(null);
  const prevPricesRef = useRef({});
  const startTimeRef = useRef(Date.now());

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('gas-theme', theme);
  }, [theme]);

  // WebSocket Integration
  const wsUrl = import.meta.env.VITE_WS_BASE_URL || 'ws://35.197.97.60:8085/terminal/ws';
  const { isConnected, send } = useWebSocket(wsUrl, (data) => {
    if (data.type === 'price') {
      setPrices(prev => ({ ...prev, [data.symbol]: data.price }));
    }
    if (data.type === 'signal') {
      setCurrentSignal(data.signal);
      setIsNewSignal(true);
      setShowAlert(true);
      startTimeRef.current = Date.now();
      setEta(15);

      if (soundEnabled) {
        if (!audioRef.current) {
          audioRef.current = new Audio('https://assets.mixkit.co/active_storage/sfx/2869/2869-preview.mp3');
          audioRef.current.volume = 0.3;
        }
        audioRef.current.currentTime = 0;
        audioRef.current.play().catch(() => { });
      }

      setTimeout(() => setIsNewSignal(false), 2000);
      setTimeout(() => setShowAlert(false), 5000);
    }
  });

  useEffect(() => {
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // API Load
  useEffect(() => {
    const loadData = async () => {
      try {
        const overview = await fetchOverview();
        if (overview && overview.pairs) {
          setPairs(overview.pairs);
          const initialPrices = {};
          overview.pairs.forEach(p => initialPrices[p.symbol] = p.price || p.base);
          setPrices(initialPrices);

          if (overview.signal) setCurrentSignal(overview.signal);
          if (overview.news) setNews(overview.news.map(n => n.title || n)); // format handling
          if (overview.indices) setGlobalIndices(overview.indices);
          if (overview.macro) setMacroData(overview.macro);
          if (overview.ai) setAiAnalysis(overview.ai);

          const selPair = overview.pairs.find(p => p.symbol === 'XAUUSD');
          if (selPair) setChartPair(selPair);
        }
      } catch (err) {
        console.error("Failed to load generic overview, using fallback constants", err);
        const initialPrices = {};
        PAIRS.forEach(p => initialPrices[p.symbol] = p.base);
        setPrices(initialPrices);
      } finally {
        setIsLoading(false);
      }
    };

    // Slight delay to mimic init payload
    setTimeout(loadData, 800);

    const timerIv = setInterval(() => {
      const diff = Math.floor((Date.now() - startTimeRef.current) / 1000);
      setEta(15 - (diff % 15));
    }, 1000);

    return () => clearInterval(timerIv);
  }, []);

  const priceDirections = useMemo(() => {
    const map = {};
    pairs.forEach(p => {
      const cur = prices[p.symbol], prev = prevPricesRef.current[p.symbol];
      if (cur && prev) map[p.symbol] = cur > prev ? 'up' : cur < prev ? 'down' : null;
    });
    return map;
  }, [prices, pairs]);

  useEffect(() => {
    prevPricesRef.current = prices;
  }, [prices]);

  const loopPrices = useMemo(() => {
    const e = Object.entries(prices);
    return e.length < 12 && e.length > 0 ? [...e, ...e, ...e] : e;
  }, [prices]);

  const handleSelectPair = (symbol) => {
    if (navigator.vibrate) navigator.vibrate(30);
    const pair = pairs.find(p => p.symbol === symbol);
    setActivePair(symbol);
    if (pair) setChartPair(pair);
    setActiveMenu('signal');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  if (isLoading) return <LoadingScreen />;

  return (
    <div className="min-h-screen bg-[var(--bg-main)] text-[var(--text-primary)] font-sans overflow-hidden">
      {/* TOP TICKER */}
      <div className="h-8 bg-[var(--bg-card)] border-b border-[var(--border-color)] flex items-center overflow-hidden relative z-50">
        <div className="shrink-0 px-3 border-r border-[var(--border-color)] flex items-center gap-2 h-full">
          <Zap size={12} className="text-[var(--accent)] fill-[var(--accent)]" />
          <span className="text-[10px] font-black tracking-widest text-[var(--accent)] font-display">
            GAS PRO {isConnected ? <span className="text-[var(--success)] ml-1">●</span> : <span className="text-[var(--danger)] ml-1">●</span>}
          </span>
        </div>
        <div className="flex-1 overflow-hidden flex">
          <div className="ticker-scroll flex whitespace-nowrap gap-0 items-center">
            {loopPrices.map(([k, v], i) => {
              const pair = pairs.find(p => p.symbol === k) || PAIRS.find(p => p.symbol === k);
              const base = pair?.base || 1;
              const chg = ((v - base) / base * 100);
              const isUp = chg >= 0;
              return (
                <span key={i} className="inline-flex items-center gap-2 px-4 border-r border-[var(--border-color)] h-8 cursor-pointer hover:bg-[var(--bg-hover)] transition-colors" onClick={() => handleSelectPair(k)}>
                  <span className="text-[10px] font-bold text-[var(--text-dim)]">{k}</span>
                  <span className={`text-[10px] font-mono font-bold ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                    {v ? v.toFixed(pair?.type === 'Forex' ? 4 : 2) : '--'}
                  </span>
                  <span className={`text-[9px] font-mono ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{isUp ? '+' : ''}{chg.toFixed(2)}%</span>
                </span>
              );
            })}
          </div>
        </div>
        <div className="shrink-0 px-3 border-l border-[var(--border-color)] flex items-center gap-2 h-full">
          <button onClick={() => setSoundEnabled(!soundEnabled)} className="text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors text-[10px] uppercase font-bold tracking-widest">
            {soundEnabled ? 'Audio On' : 'Audio Muted'}
          </button>
        </div>
      </div>

      {/* LAYOUT */}
      <div className="flex h-[calc(100vh-32px)]">

        {/* SIDEBAR */}
        <aside className="w-14 md:w-[60px] xl:w-[220px] bg-[var(--bg-card)] border-r border-[var(--border-color)] flex flex-col shrink-0 z-40">
          <div className="h-14 flex items-center justify-center xl:justify-start xl:px-5 border-b border-[var(--border-color)]">
            <div className="xl:hidden w-8 h-8 rounded-lg bg-[var(--accent-soft)] flex items-center justify-center">
              <Zap size={16} className="text-[var(--accent)] fill-[var(--accent)] pulse-dot" />
            </div>
            <span className="hidden xl:block text-sm font-black tracking-tight font-display">GOLDEN <span className="text-[var(--accent)]">AI</span></span>
          </div>
          <nav className="flex-1 py-4 flex flex-col gap-1 overflow-y-auto scrollbar-none px-2">
            {[
              { id: 'signal', icon: Zap, label: 'Sinyal AI' },
              { id: 'markets', icon: BarChart2, label: 'Pasar' },
              { id: 'watchlist', icon: Star, label: 'Favorit' },
              { id: 'portfolio', icon: Briefcase, label: 'Portofolio' },
            ].map(item => (
              <SideBtn key={item.id} {...item} active={activeMenu === item.id} onClick={setActiveMenu} />
            ))}
            <div className="mx-2 my-3 border-t border-[var(--border-color)]" />
            <SideBtn id="more" icon={LayoutGrid} label="Alat Pro" active={activeMenu === 'more'} onClick={setActiveMenu} />
            <SideBtn id="alerts" icon={Bell} label="Alerts" active={activeMenu === 'alerts'} onClick={setActiveMenu} />
            <SideBtn id="calendars" icon={Calendar} label="Kalender" active={activeMenu === 'calendars'} onClick={setActiveMenu} />
            <div className="flex-1" />
            <SideBtn id="settings" icon={Settings} label="Pengaturan" active={activeMenu === 'settings'} onClick={setActiveMenu} />
          </nav>
        </aside>

        {/* MAIN */}
        <main className="flex-1 flex flex-col overflow-hidden relative">
          {/* HEADER BAR */}
          <header className="h-14 bg-[var(--bg-card)] border-b border-[var(--border-color)] flex items-center px-4 gap-4 shrink-0 z-30">
            <div className="flex items-center gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-md px-3 py-2 w-48 md:w-64 transition-all focus-within:border-[var(--text-dim)]">
              <Search size={14} className="text-[var(--text-dim)]" />
              <input type="text" placeholder="Cari pair aset..." className="bg-transparent text-xs text-[var(--text-primary)] outline-none w-full placeholder:text-[var(--text-dim)]" />
            </div>
            <div className="flex-1 hidden md:flex items-center gap-2 overflow-hidden px-2 border-l border-[var(--border-color)]">
              {pairs.slice(0, 4).map(p => {
                const cur = prices[p.symbol] || p.base;
                const chg = ((cur - p.base) / p.base * 100);
                const isUp = chg >= 0;
                return (
                  <button key={p.symbol} onClick={() => handleSelectPair(p.symbol)}
                    className={`flex items-center gap-2 px-3 py-1.5 rounded transition-all ${activePair === p.symbol ? 'bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/20' : 'border border-transparent text-[var(--text-dim)] hover:bg-[var(--bg-hover)]'}`}>
                    <span className="text-[10px] font-bold">{p.symbol}</span>
                    <span className={`text-[10px] font-mono ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{isUp ? '+' : ''}{chg.toFixed(2)}%</span>
                  </button>
                );
              })}
            </div>
            <div className="flex items-center gap-3 ml-auto">
              <div className="hidden sm:flex items-center gap-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded p-1">
                {[
                  { t: 'dark', i: <Moon size={12} /> },
                  { t: 'light', i: <Sun size={12} /> },
                  { t: 'term', i: <Monitor size={12} /> }
                ].map(({ t, i }) => (
                  <button
                    key={t}
                    onClick={() => setTheme(t === 'term' ? 'dark' : t)}
                    className={`p-1.5 rounded transition-colors ${theme === t ? 'bg-[var(--accent)] text-black' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}
                  >
                    {i}
                  </button>
                ))}
              </div>
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 p-[1px] cursor-pointer shadow-[0_0_10px_rgba(250,204,21,0.2)]">
                <div className="w-full h-full bg-[var(--bg-main)] rounded-full flex items-center justify-center text-[10px] font-black text-[var(--text-primary)]">JD</div>
              </div>
            </div>
          </header>

          {/* NEWS TICKER */}
          <div className="h-6 bg-[var(--bg-main)] border-b border-[var(--border-color)] overflow-hidden flex shrink-0">
            <div className="shrink-0 px-3 bg-yellow-400 flex items-center h-full z-10 shadow-[2px_0_10px_rgba(0,0,0,0.5)]">
              <span className="text-[9px] font-black text-black uppercase tracking-widest">LIVE NEWS</span>
            </div>
            <div className="flex-1 overflow-hidden flex items-center">
              <div className="news-scroll flex whitespace-nowrap items-center">
                {[...news, ...news, ...news].map((n, i) => (
                  <span key={i} className="text-[10px] font-bold text-[var(--text-dim)] px-8 border-r border-[var(--border-color)]">{typeof n === 'string' ? n : n.title}</span>
                ))}
              </div>
            </div>
          </div>

          {/* CONTENT AREA */}
          <div className="flex-1 overflow-y-auto scrollbar-none relative">
            {activeMenu === 'signal' && <SignalView signal={currentSignal} isNew={isNewSignal} timer={eta} chartPair={chartPair} prices={prices} onSelect={handleSelectPair} activePair={activePair} pairs={pairs} macroData={macroData} aiAnalysis={aiAnalysis} theme={theme} />}
            {activeMenu === 'markets' && <MarketsView pairs={pairs} prices={prices} directions={priceDirections} onSelect={handleSelectPair} activePair={activePair} />}
            {activeMenu === 'watchlist' && <EmptyView icon={<Star size={32} />} label="Favorit Kosong" sub="Tambahkan aset ke daftar favorit Anda" />}
            {activeMenu === 'portfolio' && <PortfolioView />}
            {activeMenu === 'more' && <AICommandCenter onSelect={id => setActiveMenu(id === 'ai_signal' ? 'signal' : id)} />}
            {activeMenu === 'settings' && <SettingsView />}
            {activeMenu === 'alerts' && <EmptyView icon={<Bell size={32} />} label="Belum Ada Alert" sub="Buat alert harga baru dari halaman Markets" />}
            {activeMenu === 'calendars' && <CalendarView />}
          </div>
        </main>

        {/* RIGHT PANEL (xl only) */}
        <aside className="hidden xl:flex w-[320px] bg-[var(--bg-card)] border-l border-[var(--border-color)] flex-col shrink-0 overflow-y-auto scrollbar-none">
          <div className="p-5 border-b border-[#1c1d24]">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Inteligensi AI</span>
              <div className="w-2 h-2 rounded-full bg-[var(--success)] pulse-dot" />
            </div>
            <p className={`text-3xl font-display font-black mb-4 ${aiAnalysis?.trend === 'BULLISH' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{aiAnalysis?.trend || 'ANALYZING...'}</p>
            <div className="space-y-2">
              {aiAnalysis?.logic && aiAnalysis.logic.map((l, i) => (
                <div key={i} className="flex items-start gap-3 text-[11px] p-3 rounded bg-[#13141a] border border-[#1c1d24]">
                  <Zap size={12} className="text-yellow-400 shrink-0 mt-0.5" />
                  <span className="text-[#aaa] leading-relaxed">{l}</span>
                </div>
              ))}
            </div>
          </div>
          <div className="p-5 border-b border-[#1c1d24]">
            <span className="text-[10px] font-black uppercase tracking-widest text-[#555] mb-4 block">Fundamental Makro</span>
            {macroData.map((m, i) => (
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
            {globalIndices.map((g, i) => (
              <div key={i} className="flex justify-between items-center py-2 text-[11px]">
                <span className="text-[#777] font-bold w-24 truncate">{g.name}</span>
                <span className="font-mono font-bold text-[#ccc]">{g.value.toLocaleString()}</span>
                <span className={`font-mono font-bold w-16 text-right ${g.pct >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>{g.pct >= 0 ? '+' : ''}{(g.pct || 0).toFixed(2)}%</span>
              </div>
            ))}
          </div>
        </aside>
      </div>

      {/* MOBILE BOTTOM NAV */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 h-16 bg-[#0d0e12] border-t border-[#1c1d24] flex items-center justify-around z-50 px-2 pb-1">
        {[
          { id: 'signal', icon: <Zap size={22} />, label: 'Sinyal' },
          { id: 'markets', icon: <BarChart2 size={22} />, label: 'Pasar' },
          { id: 'watchlist', icon: <Star size={22} />, label: 'Favorit' },
          { id: 'portfolio', icon: <Briefcase size={22} />, label: 'Portofolio' },
          { id: 'more', icon: <LayoutGrid size={22} />, label: 'Menu' },
        ].map(({ id, icon, label }) => (
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
