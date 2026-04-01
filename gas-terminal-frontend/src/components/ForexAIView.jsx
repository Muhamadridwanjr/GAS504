import React, { useState, useEffect, useCallback } from 'react';
import {
  TrendingUp, TrendingDown, RefreshCw, Zap, Clock,
  BarChart2, AlertTriangle, ArrowUpRight, ArrowDownRight,
  Minus, WifiOff, Target, Shield, ChevronRight, Layers,
} from 'lucide-react';
import { callAIFeature, fetchOverview } from '../services/api';
import { useAuth } from '../context/AuthContext';
import AutoSignalPanel from './AutoSignalPanel';
import MarketAnalysisPanel from './MarketAnalysisPanel';

// ── Pair metadata ─────────────────────────────────────────────────────────────
const FLAG = (cc) => `https://flagcdn.com/w40/${cc.toLowerCase()}.png`;
const FOREX_PAIRS = [
  { symbol: 'XAUUSD', name: 'Gold / USD',    emoji: '🥇', logo: null,        decimals: 2, type: 'commodity' },
  { symbol: 'EURUSD', name: 'Euro / USD',    emoji: '🇪🇺', logo: FLAG('eu'), decimals: 4, type: 'forex' },
  { symbol: 'GBPUSD', name: 'Pound / USD',   emoji: '🇬🇧', logo: FLAG('gb'), decimals: 4, type: 'forex' },
  { symbol: 'USDJPY', name: 'USD / Yen',     emoji: '🇯🇵', logo: FLAG('jp'), decimals: 2, type: 'forex' },
  { symbol: 'USDCHF', name: 'USD / Franc',   emoji: '🇨🇭', logo: FLAG('ch'), decimals: 4, type: 'forex' },
  { symbol: 'AUDUSD', name: 'Aussie / USD',  emoji: '🇦🇺', logo: FLAG('au'), decimals: 4, type: 'forex' },
  { symbol: 'NZDUSD', name: 'Kiwi / USD',    emoji: '🇳🇿', logo: FLAG('nz'), decimals: 4, type: 'forex' },
  { symbol: 'USDCAD', name: 'USD / CAD',     emoji: '🇨🇦', logo: FLAG('ca'), decimals: 4, type: 'forex' },
  { symbol: 'EURGBP', name: 'Euro / Pound',  emoji: '🇪🇺', logo: FLAG('eu'), decimals: 4, type: 'forex' },
  { symbol: 'EURJPY', name: 'Euro / Yen',    emoji: '🇪🇺', logo: FLAG('eu'), decimals: 2, type: 'forex' },
  { symbol: 'GBPJPY', name: 'Pound / Yen',   emoji: '🇬🇧', logo: FLAG('gb'), decimals: 2, type: 'forex' },
];

const TIMEFRAMES = ['M15', 'H1', 'H4', 'D1'];

const STYLES = [
  { id: 'scalping',  label: 'Scalping',  desc: 'M5–M15 · fast',   emoji: '⚡' },
  { id: 'intraday',  label: 'Intraday',  desc: 'H1–H4 · same day', emoji: '🎯' },
  { id: 'swing',     label: 'Swing',     desc: 'H4–D1 · multi-day', emoji: '🌊' },
];

// AI Model tiers — mirrors gas-strategy-core MODEL_TIERS
const PLAN_RANK = { free: 0, essential: 1, plus: 2, premium: 3, ultimate: 4, ultra: 5 };
const TIER_TO_PLAN_DEPTH = { basic:'essential', advanced:'plus', pro:'premium', ultra:'ultimate', gpt:'ultimate', agent:'ultra' };
const SIGNAL_MODEL_TIERS = [
  { tier: 'basic',    label: 'GAS Basic',    badge: 'V3',     desc: 'DeepSeek V3',          min_plan: 'essential', signal_cost: 1,  color: 'blue' },
  { tier: 'advanced', label: 'GAS Advanced', badge: 'FLASH',  desc: 'Gemini Flash 1.5',     min_plan: 'plus',      signal_cost: 2,  color: 'purple' },
  { tier: 'pro',      label: 'GAS Pro',      badge: 'HAIKU',  desc: 'Claude Haiku 4.5',     min_plan: 'premium',   signal_cost: 3,  color: 'emerald' },
  { tier: 'ultra',    label: 'GAS Ultra',    badge: 'SONNET', desc: 'Claude Sonnet 4.6',    min_plan: 'ultimate',  signal_cost: 5,  color: 'amber' },
  { tier: 'gpt',      label: 'GAS GPT',      badge: 'GPT',    desc: 'GPT-4o',               min_plan: 'ultimate',  signal_cost: 5,  color: 'teal' },
  { tier: 'agent',    label: 'GAS Agent',    badge: 'AGENT',  desc: 'Claude Opus 4.6',      min_plan: 'ultra',     signal_cost: 10, color: 'rose' },
];

// ── Session definitions (UTC hours) ──────────────────────────────────────────
const SESSIONS = [
  { id: 'asian',    name: 'Asian',    emoji: '🏯', open: 0,  close: 9,  color: '#f97316', pairs: ['USDJPY', 'AUDUSD', 'GBPJPY'] },
  { id: 'london',   name: 'London',   emoji: '🇬🇧', open: 7,  close: 16, color: '#8b5cf6', pairs: ['EURUSD', 'GBPUSD', 'XAUUSD'] },
  { id: 'newyork',  name: 'New York', emoji: '🗽', open: 12, close: 21, color: '#10b981', pairs: ['EURUSD', 'GBPUSD', 'XAUUSD', 'USDJPY'] },
];

function getUTCHour() {
  return new Date().getUTCHours();
}

function isSessionActive(session) {
  const h = getUTCHour();
  if (session.open < session.close) return h >= session.open && h < session.close;
  return h >= session.open || h < session.close;
}

function timeUntilSession(session) {
  const now = new Date();
  const h = now.getUTCHours();
  const m = now.getUTCMinutes();
  const currentMinutes = h * 60 + m;
  const openMinutes = session.open * 60;
  let diff = openMinutes - currentMinutes;
  if (diff < 0) diff += 1440;
  return { hours: Math.floor(diff / 60), minutes: diff % 60 };
}

// ── Market time context (client-side) ─────────────────────────────────────────
function getMarketTimeContext() {
  const h = getUTCHour();
  let killZone = null;
  if (h >= 6 && h < 8)   killZone = '🔥 London Open Kill Zone';
  else if (h >= 12 && h < 14) killZone = '🔥 NY Open Kill Zone';
  else if (h >= 15 && h < 16) killZone = '⚠️ London Close Kill Zone';
  else if (h >= 20 || h < 1)  killZone = '🌙 Asian Kill Zone';

  let amdPhase;
  if (h >= 0 && h < 5)        amdPhase = 'Accumulation';
  else if (h >= 5 && h < 10)  amdPhase = 'Manipulation';
  else if (h >= 10 && h < 17) amdPhase = 'Distribution';
  else                         amdPhase = 'Consolidation';

  const activeSessions = SESSIONS.filter(s => isSessionActive(s));
  const sessionName = activeSessions.length > 0 ? activeSessions.map(s => s.name).join(' + ') : 'Off-Hours';
  return { killZone, amdPhase, sessionName };
}

// ── Sub-components ─────────────────────────────────────────────────────────────
function PairCard({ pair, price, changePct, stale, noData, onAnalyze }) {
  const chg = changePct ?? 0;
  const isUp = chg >= 0;
  return (
    <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-3.5 hover:border-[var(--accent)]/40 hover:bg-[var(--bg-card)] transition-all group cursor-pointer" onClick={() => onAnalyze(pair.symbol)}>
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-lg">{pair.emoji}</span>
          <div>
            <div className="text-[10px] font-black text-[var(--text-primary)] tracking-wide">{pair.symbol}</div>
            <div className="text-[8px] text-[var(--text-dim)] font-medium">{pair.name}</div>
          </div>
        </div>
        {noData ? <WifiOff size={12} className="text-[var(--text-dim)]" /> :
         stale ? <span className="text-[7px] font-black px-1 py-0.5 rounded bg-yellow-400/20 text-yellow-400">STALE</span> :
         isUp ? <ArrowUpRight size={14} className="text-[#10b981]" /> : <ArrowDownRight size={14} className="text-[#f43f5e]" />}
      </div>
      <div className={`text-base font-black font-mono mb-0.5 ${noData ? 'text-[var(--text-dim)]' : isUp ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
        {price ? price.toFixed(pair.decimals) : '--'}
      </div>
      <div className={`text-[9px] font-bold mb-2.5 ${noData ? 'text-[var(--text-dim)]' : isUp ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
        {noData ? 'No data' : `${isUp ? '+' : ''}${chg.toFixed(3)}%`}
      </div>
      <div className="w-full text-[8px] font-black uppercase tracking-widest py-1.5 rounded-lg bg-[var(--accent)]/10 text-[var(--accent)] group-hover:bg-[var(--accent)]/20 transition-colors flex items-center justify-center gap-1">
        <Zap size={9} className="fill-[var(--accent)]" /> AI Analyze
      </div>
    </div>
  );
}

function SessionBox({ session, isActive }) {
  const countdown = !isActive ? timeUntilSession(session) : null;
  return (
    <div className={`flex-1 rounded-2xl p-4 border transition-all ${isActive ? 'border-opacity-60' : 'border-[var(--border-color)] bg-[var(--bg-panel)]'}`}
      style={isActive ? { borderColor: session.color, background: `${session.color}12` } : {}}>
      <div className="flex items-center gap-2 mb-2">
        <span className="text-base">{session.emoji}</span>
        <div>
          <div className="text-[10px] font-black text-[var(--text-primary)] uppercase tracking-wide">{session.name}</div>
          <div className="text-[9px] text-[var(--text-dim)]">{session.open}:00 – {session.close}:00 UTC</div>
        </div>
        {isActive && (
          <span className="ml-auto text-[8px] font-black px-1.5 py-0.5 rounded" style={{ background: session.color, color: '#000' }}>LIVE</span>
        )}
      </div>
      {!isActive && countdown && (
        <div className="text-[9px] text-[var(--text-dim)] font-bold">
          Opens in {countdown.hours}h {countdown.minutes}m
        </div>
      )}
      <div className="flex flex-wrap gap-1 mt-2">
        {session.pairs.map(p => (
          <span key={p} className="text-[8px] font-black px-1.5 py-0.5 rounded bg-[var(--bg-card)] text-[var(--text-dim)]">{p}</span>
        ))}
      </div>
    </div>
  );
}

function ResultModal({ result, error, symbol, onClose }) {
  if (!result && !error) return null;
  const rec = result?.recommendation || result?.bias || 'NEUTRAL';
  const isUp = rec === 'BUY' || rec === 'BULLISH';
  const isDown = rec === 'SELL' || rec === 'BEARISH';
  const recColor = isUp ? 'text-[#10b981]' : isDown ? 'text-[#f43f5e]' : 'text-yellow-400';
  const conf = result?.confidence || 0;
  const aiText = result?.ai_interpretation || result?.analysis || result?.reasoning || '';

  return (
    <div className="fixed inset-0 z-[500] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm" onClick={onClose}>
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 max-w-lg w-full shadow-2xl max-h-[80vh] overflow-y-auto" onClick={e => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-black text-[var(--text-primary)]">Quick Analysis · {symbol}</h3>
          <button onClick={onClose} className="text-[var(--text-dim)] hover:text-[var(--text-primary)] text-xl leading-none font-bold">×</button>
        </div>
        {error ? (
          <div className="flex flex-col items-center gap-3 py-6 text-center">
            <AlertTriangle size={32} className="text-[#f43f5e]" />
            <p className="text-sm font-bold text-[#f43f5e]">Analysis Failed</p>
            <p className="text-xs text-[var(--text-dim)]">{error}</p>
            <p className="text-[9px] text-[var(--text-dim)] mt-1">Make sure you are logged in and MT5 is connected.</p>
          </div>
        ) : result && (
          <div className="space-y-3 text-xs text-[var(--text-secondary)]">
            <div className={`text-xl font-black ${recColor}`}>{rec} <span className="text-sm font-bold text-[var(--text-dim)]">· {conf}% confidence</span></div>
            {result.setup_type && (
              <span className="inline-block text-[9px] font-black px-2 py-0.5 rounded bg-[var(--accent)]/10 text-[var(--accent)]">📐 {result.setup_type}</span>
            )}
            {result.confluence_score != null && (
              <div className="flex items-center gap-2">
                <span className="font-bold text-[var(--text-dim)]">Confluence:</span>
                <span className="font-black text-[var(--accent)]">{result.confluence_score}</span>
              </div>
            )}
            {aiText && (
              <div className="text-[10px] text-[var(--text-dim)] leading-relaxed border-t border-[var(--border-color)] pt-3">
                {aiText}
              </div>
            )}
            {result.current_price && (
              <div className="text-[9px] text-[var(--text-dim)] font-mono">Price: {result.current_price}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ── Tabs ───────────────────────────────────────────────────────────────────────
const TABS = [
  { id:'Overview',   icon:'fa-solid fa-gauge-high',      label:'Overview' },
  { id:'Signals',    icon:'fa-solid fa-bolt',             label:'Signals' },
  { id:'Technical',  icon:'fa-solid fa-chart-area',       label:'Technical' },
  { id:'Session',    icon:'fa-solid fa-clock',             label:'Session' },
  { id:'Data',       icon:'fa-solid fa-table',             label:'Data' },
  { id:'AI Insight', icon:'fa-solid fa-brain',             label:'AI Insight' },
];

export default function ForexAIView({ prices = {}, pairs = [] }) {
  const { isAdmin, userPlan } = useAuth() || {};
  const [activeTab, setActiveTab] = useState('Overview');
  const [timeframe, setTimeframe] = useState('H1');
  const [selectedPair, setSelectedPair] = useState('XAUUSD');
  const [utcNow, setUtcNow] = useState(new Date());

  // Live price data from overview endpoint
  const [livePriceMap, setLivePriceMap] = useState({}); // { XAUUSD: { price, change_pct, stale, no_data } }
  const [overviewLoading, setOverviewLoading] = useState(true);

  // Analysis modal state
  const [modalResult, setModalResult] = useState(null);
  const [modalSymbol, setModalSymbol] = useState('');
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState('');

  // Signal tab state
  const [signalResult, setSignalResult] = useState(null);
  const [signalLoading, setSignalLoading] = useState(false);
  const [signalError, setSignalError] = useState('');
  const [signalPair, setSignalPair] = useState('XAUUSD');
  const [signalStyle, setSignalStyle] = useState('intraday');
  const [signalModelTier, setSignalModelTier] = useState('basic');

  // Compute model unlock from AuthContext — no API call needed
  const effectivePlan = isAdmin ? 'ultimate' : (userPlan || 'essential');
  const userRank = PLAN_RANK[effectivePlan] ?? 1;
  const tiersWithAccess = SIGNAL_MODEL_TIERS.map(m => ({
    ...m,
    unlocked: isAdmin || (userRank >= (PLAN_RANK[m.min_plan] ?? 1)),
  }));

  // Mode tabs (auto / manual / analysis)
  const [mode, setMode] = useState('manual');

  // Technical tab state
  const [techResult, setTechResult] = useState(null);
  const [techLoading, setTechLoading] = useState(false);
  const [techError, setTechError] = useState('');

  // UTC clock
  useEffect(() => {
    const iv = setInterval(() => setUtcNow(new Date()), 1000);
    return () => clearInterval(iv);
  }, []);

  // Fetch live prices from overview endpoint
  const loadOverviewPrices = useCallback(async () => {
    try {
      const data = await fetchOverview();
      if (data?.pairs) {
        const map = {};
        data.pairs.forEach(p => {
          map[p.symbol] = {
            price: p.price,
            change_pct: p.change_pct ?? 0,
            stale: p.stale || false,
            no_data: p.no_data || !p.price,
          };
        });
        setLivePriceMap(map);
      }
    } catch (e) {
      // silent — keep stale map
    } finally {
      setOverviewLoading(false);
    }
  }, []);

  useEffect(() => {
    loadOverviewPrices();
    const iv = setInterval(loadOverviewPrices, 30_000);
    return () => clearInterval(iv);
  }, [loadOverviewPrices]);


  const getPrice = (symbol) => {
    return livePriceMap[symbol]?.price || prices[symbol] || 0;
  };

  // Analyze a pair (modal)
  const handleAnalyze = async (symbol) => {
    setAnalysisError('');
    setModalResult(null);
    setModalSymbol(symbol);
    setAnalysisLoading(true);
    try {
      const res = await callAIFeature('technical', { pair: symbol, timeframe: 'H1' });
      setModalResult(res);
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || 'Failed to reach analysis service.';
      setAnalysisError(detail);
    } finally {
      setAnalysisLoading(false);
    }
  };

  // Signal fetch
  const fetchSignal = async () => {
    setSignalError('');
    setSignalLoading(true);
    setSignalResult(null);
    try {
      const res = await callAIFeature('signal', { pair: signalPair, timeframe, style: signalStyle, model_tier: signalModelTier });
      setSignalResult(res);
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || 'Signal generation failed.';
      setSignalError(detail);
    } finally {
      setSignalLoading(false);
    }
  };

  // Technical fetch
  const fetchTechnical = async () => {
    setTechError('');
    setTechLoading(true);
    try {
      const res = await callAIFeature('technical', { pair: selectedPair, timeframe });
      setTechResult(res);
    } catch (err) {
      setTechError(err?.response?.data?.detail || 'Technical analysis failed.');
    } finally {
      setTechLoading(false);
    }
  };

  const utcStr = `${String(utcNow.getUTCHours()).padStart(2,'0')}:${String(utcNow.getUTCMinutes()).padStart(2,'0')} UTC`;

  return (
    <div className="p-4 md:p-6 pb-24 md:pb-6 max-w-5xl mx-auto space-y-5">
      {/* Mode Tabs */}
      <div className="flex gap-1 p-1 rounded-2xl bg-[var(--bg-panel)] border border-[var(--border-color)]">
        {[
          { id: 'auto',     label: 'Auto Signal', icon: '📡' },
          { id: 'manual',   label: 'Manual',      icon: '🎯' },
          { id: 'analysis', label: 'Analysis',    icon: '🧠' },
        ].map(tab => (
          <button key={tab.id}
            onClick={() => setMode(tab.id)}
            className={`flex-1 py-2 px-3 rounded-xl text-[9px] font-black transition-all flex items-center justify-center gap-1.5
              ${mode === tab.id
                ? 'bg-[var(--accent)] text-black shadow-md'
                : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
              }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {mode === 'auto' && (
        <div className="space-y-3">
          <AutoSignalPanel market="forex" planDepth={TIER_TO_PLAN_DEPTH[signalModelTier] || 'essential'} />
        </div>
      )}

      {mode === 'analysis' && (
        <div className="space-y-3">
          <MarketAnalysisPanel market="forex" planDepth={TIER_TO_PLAN_DEPTH[signalModelTier] || 'essential'} />
        </div>
      )}

      {mode === 'manual' && (<>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center gap-3">
        <div className="flex items-center gap-3 flex-1">
          <div className="w-10 h-10 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20 flex items-center justify-center shrink-0">
            <TrendingUp size={20} className="text-[var(--accent)]" />
          </div>
          <div>
            <h2 className="text-lg font-black text-[var(--text-primary)]">💱 Forex AI</h2>
            <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Live MT5 · Exness · Gold · Indices</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)]">
            {overviewLoading
              ? <RefreshCw size={9} className="animate-spin text-yellow-400" />
              : <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
            }
            <span className={`text-[9px] font-black uppercase tracking-widest ${overviewLoading ? 'text-yellow-400' : 'text-[#10b981]'}`}>
              {overviewLoading ? 'Loading...' : 'Live'}
            </span>
          </div>
          <div className="text-[10px] font-mono font-bold text-[var(--text-dim)] px-2 py-1.5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg">
            {utcStr}
          </div>
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

      {/* ── TAB: Overview ─────────────────────────────────────────────────────── */}
      {activeTab === 'Overview' && (
        <>
          {overviewLoading && (
            <div className="flex items-center gap-2 text-[10px] text-[var(--text-dim)] font-bold py-2">
              <RefreshCw size={11} className="animate-spin" /> Loading live prices...
            </div>
          )}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-3">
            {FOREX_PAIRS.map(pair => {
              const live = livePriceMap[pair.symbol];
              return (
                <PairCard
                  key={pair.symbol}
                  pair={pair}
                  price={live?.price || getPrice(pair.symbol)}
                  changePct={live?.change_pct}
                  stale={live?.stale}
                  noData={!live || live.no_data}
                  onAnalyze={handleAnalyze}
                />
              );
            })}
          </div>

          {/* Session Clocks */}
          <div>
            <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3 flex items-center gap-2">
              <Clock size={11} /> Session Status
            </div>
            <div className="flex flex-col sm:flex-row gap-3">
              {SESSIONS.map(s => (
                <SessionBox key={s.id} session={s} isActive={isSessionActive(s)} />
              ))}
            </div>
          </div>
        </>
      )}

      {/* ── TAB: Signals ──────────────────────────────────────────────────────── */}
      {activeTab === 'Signals' && (
        <div className="space-y-4">
          {/* Controls row */}
          <div className="flex flex-col gap-3">
            {/* Pair selector */}
            <div>
              <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest">Select Pair</div>
              <div className="flex flex-wrap gap-2">
                {FOREX_PAIRS.filter(p => p.type !== 'index').map(p => (
                  <button
                    key={p.symbol}
                    onClick={() => setSignalPair(p.symbol)}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${signalPair === p.symbol ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--accent)]/40'}`}
                  >
                    {p.emoji} {p.symbol}
                  </button>
                ))}
              </div>
            </div>

            {/* Timeframe + Style row */}
            <div className="flex flex-col sm:flex-row gap-3">
              <div className="shrink-0">
                <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest">Timeframe</div>
                <div className="flex gap-1">
                  {TIMEFRAMES.map(tf => (
                    <button
                      key={tf}
                      onClick={() => setTimeframe(tf)}
                      className={`px-2.5 py-1.5 rounded-lg text-[10px] font-black transition-all ${timeframe === tf ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--accent)]/40'}`}
                    >
                      {tf}
                    </button>
                  ))}
                </div>
              </div>
              <div className="flex-1">
                <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest">Trading Style</div>
                <div className="flex gap-2">
                  {STYLES.map(s => (
                    <button
                      key={s.id}
                      onClick={() => setSignalStyle(s.id)}
                      className={`flex-1 sm:flex-none px-3 py-1.5 rounded-lg text-[10px] font-black transition-all flex flex-col items-center gap-0.5 ${signalStyle === s.id ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--accent)]/40'}`}
                    >
                      <span>{s.emoji} {s.label}</span>
                      <span className={`text-[8px] font-bold ${signalStyle === s.id ? 'text-black/60' : 'text-[var(--text-dim)]'}`}>{s.desc}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* AI Model Tier Selector */}
          <div>
            <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest flex items-center gap-2">
              AI Model
              {isAdmin && <span className="text-[8px] font-black px-1.5 py-0.5 rounded bg-[var(--accent)]/10 text-[var(--accent)]">ADMIN · ALL UNLOCKED</span>}
            </div>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              {tiersWithAccess.map(m => {
                const isSelected = signalModelTier === m.tier;
                const isLocked = !m.unlocked;
                const colorMap = {
                  blue:    { bar: '#3b82f6', bg: 'bg-blue-500/10',    border: 'border-blue-500/40',    text: 'text-blue-300' },
                  purple:  { bar: '#8b5cf6', bg: 'bg-purple-500/10',  border: 'border-purple-500/40',  text: 'text-purple-300' },
                  emerald: { bar: '#10b981', bg: 'bg-emerald-500/10', border: 'border-emerald-500/40', text: 'text-emerald-300' },
                  amber:   { bar: '#f59e0b', bg: 'bg-amber-500/10',   border: 'border-amber-500/40',   text: 'text-amber-300' },
                  teal:    { bar: '#14b8a6', bg: 'bg-teal-500/10',    border: 'border-teal-500/40',    text: 'text-teal-300' },
                  rose:    { bar: '#f43f5e', bg: 'bg-rose-500/10',    border: 'border-rose-500/40',    text: 'text-rose-300' },
                };
                const c = colorMap[m.color] || colorMap.blue;
                return (
                  <button
                    key={m.tier}
                    onClick={() => !isLocked && setSignalModelTier(m.tier)}
                    title={isLocked ? `Requires ${m.min_plan} plan` : m.desc}
                    className={`relative flex items-stretch rounded-xl text-left transition-all border overflow-hidden ${
                      isLocked
                        ? 'opacity-40 cursor-not-allowed bg-[var(--bg-panel)] border-[var(--border-color)]'
                        : isSelected
                          ? `${c.bg} ${c.border}`
                          : 'bg-[var(--bg-panel)] border-[var(--border-color)] hover:border-[var(--accent)]/40 cursor-pointer'
                    }`}
                  >
                    {/* Left color bar accent when selected */}
                    {isSelected && !isLocked && (
                      <div className="w-1 shrink-0" style={{ background: c.bar }} />
                    )}
                    <div className="flex-1 px-3 py-2.5">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className={`text-[10px] font-black ${isLocked ? 'text-[var(--text-dim)]' : isSelected ? c.text : 'text-[var(--text-secondary)]'}`}>{m.badge}</span>
                        {isLocked
                          ? <span className="text-[9px] opacity-60">🔒</span>
                          : isSelected && <span className="text-[8px] font-black" style={{ color: c.bar }}>✓</span>
                        }
                      </div>
                      <div className={`text-[9px] font-bold truncate ${isLocked ? 'text-[var(--text-dim)]' : 'text-[var(--text-secondary)]'}`}>{m.label}</div>
                      <div className="text-[8px] opacity-60 mt-0.5">{isLocked ? `🔒 ${m.min_plan}` : `${isAdmin ? '0' : m.signal_cost}cr`}</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          <button
            onClick={fetchSignal}
            disabled={signalLoading || !tiersWithAccess.find(m=>m.tier===signalModelTier)?.unlocked}
            className="w-full flex items-center justify-center gap-2 py-3.5 rounded-2xl text-sm font-black uppercase tracking-widest transition-all disabled:opacity-40"
            style={{ background: signalLoading ? undefined : 'linear-gradient(135deg, var(--accent), #059669)', color: '#000' }}
          >
            {signalLoading ? <RefreshCw size={16} className="animate-spin" /> : <Zap size={16} className="fill-black" />}
            {signalLoading
              ? `Analyzing with ${SIGNAL_MODEL_TIERS.find(m=>m.tier===signalModelTier)?.label}...`
              : `⚡ Generate ${STYLES.find(s=>s.id===signalStyle)?.label} Signal · ${isAdmin ? 'FREE' : (SIGNAL_MODEL_TIERS.find(m=>m.tier===signalModelTier)?.signal_cost ?? 3)+'cr'}`
            }
          </button>

          {signalError && (
            <div className="flex items-start gap-2 p-3 bg-[#f43f5e]/10 border border-[#f43f5e]/20 rounded-xl text-xs text-[#f43f5e] font-bold">
              <AlertTriangle size={14} className="shrink-0 mt-0.5" />
              <div>
                <div>{signalError}</div>
                {signalError.includes('401') || signalError.includes('auth') || signalError.includes('Unauthorized') ? (
                  <div className="text-[9px] font-normal mt-1 opacity-70">Please log in to use AI signal generation.</div>
                ) : null}
              </div>
            </div>
          )}

          {signalResult && (() => {
            const sig = signalResult.signal || 'HOLD';
            const isUp = sig === 'BUY';
            const isDown = sig === 'SELL';
            const prob = signalResult.probability ?? signalResult.confidence ?? 0;
            const grade = signalResult.grade || 'B';
            const stars = signalResult.stars || (grade === 'SS' ? 5 : grade === 'S' ? 4 : grade.startsWith('A') ? 3 : grade === 'B' ? 2 : 1);
            const dec = FOREX_PAIRS.find(p => p.symbol === signalPair)?.decimals ?? 4;
            const fmt = v => (v != null && v !== 0 && v !== '') ? Number(v).toFixed(dec) : '--';

            const gradeConfig = {
              'SS': { color: '#f59e0b', bg: 'from-amber-500/20 to-yellow-500/10', border: 'border-amber-500/40', label: 'SUPREME', glow: 'shadow-amber-500/20' },
              'S':  { color: '#8b5cf6', bg: 'from-purple-500/20 to-violet-500/10', border: 'border-purple-500/40', label: 'STRONG', glow: 'shadow-purple-500/20' },
              'A+': { color: '#10b981', bg: 'from-emerald-500/20 to-green-500/10', border: 'border-emerald-500/40', label: 'PRIME', glow: 'shadow-emerald-500/20' },
              'A':  { color: '#3b82f6', bg: 'from-blue-500/20 to-cyan-500/10', border: 'border-blue-500/40', label: 'VALID', glow: 'shadow-blue-500/20' },
              'B':  { color: '#f59e0b', bg: 'from-yellow-500/10 to-orange-500/5', border: 'border-yellow-500/30', label: 'WATCH', glow: 'shadow-yellow-500/10' },
              'C':  { color: '#6b7280', bg: 'from-gray-500/10 to-gray-500/5', border: 'border-gray-500/20', label: 'WEAK', glow: '' },
            };
            const gc = gradeConfig[grade] || gradeConfig['B'];
            const sigGradient = isUp ? 'from-emerald-500/15 to-green-500/5 border-emerald-500/30' : isDown ? 'from-rose-500/15 to-red-500/5 border-rose-500/30' : 'from-yellow-500/10 to-yellow-500/5 border-yellow-500/20';
            const sigColor = isUp ? '#10b981' : isDown ? '#f43f5e' : '#f59e0b';

            const ctx = getMarketTimeContext();
            const kl = signalResult.key_levels || {};
            const corrSig = signalResult.correlation_signal || '';
            const dxyBias = signalResult.dxy_bias || '';
            const xauBias = signalResult.xau_bias || '';
            const corrColor = corrSig.includes('CONFIRMED') ? '#10b981' : corrSig.includes('CAUTION') ? '#f59e0b' : '#6b7280';

            // Plan A = primary signal
            const planA = {
              label: signalResult.order_type || (isUp ? 'BUY NOW' : isDown ? 'SELL NOW' : 'WAIT'),
              entry: signalResult.entry,
              sl:    signalResult.sl || signalResult.stop_loss,
              tp1:   signalResult.tp1 || signalResult.tp,
              tp2:   signalResult.tp2,
              tp3:   signalResult.tp3,
            };

            // Plan B = limit entry from key_levels if available
            const planBEntry = isUp ? (kl.support || null) : isDown ? (kl.resistance || null) : null;
            const hasPlanB = planBEntry && planBEntry !== planA.entry;
            const planBDiff = planA.sl && planBEntry ? Math.abs(planBEntry - planA.sl) : null;
            const planBTp1 = planBDiff
              ? (isUp ? planBEntry + planBDiff : planBEntry - planBDiff)
              : planA.tp1;

            const orderTypeColor = (ot = '') => {
              if (!ot) return 'bg-[var(--bg-card)] text-[var(--text-dim)]';
              const up = ot.toUpperCase();
              if (up.includes('NOW') || up.includes('MARKET')) return 'bg-[var(--accent)]/20 text-[var(--accent)]';
              if (up.includes('LIMIT')) return 'bg-blue-400/20 text-blue-400';
              if (up.includes('STOP')) return 'bg-orange-400/20 text-orange-400';
              return 'bg-[var(--bg-card)] text-[var(--text-dim)]';
            };

            return (
            <div className="space-y-3">
              {/* HERO SIGNAL CARD */}
              <div className={`bg-gradient-to-br ${sigGradient} border rounded-2xl p-5 shadow-lg`}>
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="flex flex-col">
                      <span style={{ color: sigColor }} className="text-4xl font-black tracking-tight">{sig}</span>
                      <span className="text-[10px] text-[var(--text-dim)] font-bold uppercase tracking-widest mt-0.5">{signalPair} · {timeframe} · {signalResult.style || 'INTRADAY'}</span>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-2">
                    {/* Grade Badge */}
                    <div className={`px-3 py-1.5 rounded-xl border ${gc.border} flex items-center gap-2`} style={{ background: `${gc.color}18` }}>
                      <span className="text-base font-black" style={{ color: gc.color }}>{grade}</span>
                      <span className="text-[8px] font-black tracking-widest uppercase" style={{ color: gc.color }}>{gc.label}</span>
                    </div>
                    {/* Stars */}
                    <div className="flex items-center gap-0.5">
                      {[1,2,3,4,5].map(i => (
                        <svg key={i} width="13" height="13" viewBox="0 0 24 24" fill={i <= stars ? gc.color : 'none'} stroke={i <= stars ? gc.color : '#374151'} strokeWidth="2">
                          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
                        </svg>
                      ))}
                    </div>
                  </div>
                </div>

                {/* Probability bar */}
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-[9px] font-black uppercase tracking-widest">
                    <span className="text-[var(--text-dim)]">Probability</span>
                    <span style={{ color: prob >= 78 ? '#10b981' : prob >= 65 ? '#f59e0b' : '#f43f5e' }}>{prob}%</span>
                  </div>
                  <div className="h-2 rounded-full bg-[var(--bg-card)] overflow-hidden">
                    <div className="h-full rounded-full transition-all duration-700" style={{ width: `${prob}%`, background: prob >= 78 ? 'linear-gradient(90deg,#10b981,#059669)' : prob >= 65 ? 'linear-gradient(90deg,#f59e0b,#d97706)' : 'linear-gradient(90deg,#f43f5e,#e11d48)' }} />
                  </div>
                </div>

                {/* Confluence factors */}
                {signalResult.confluence && Array.isArray(signalResult.confluence) && signalResult.confluence.length > 0 && (
                  <div className="flex flex-wrap gap-1 mt-3">
                    {signalResult.confluence.map((f, i) => (
                      <span key={i} className="text-[8px] font-bold px-2 py-0.5 rounded-lg bg-[var(--bg-card)]/60 text-[var(--text-dim)]">✓ {f}</span>
                    ))}
                  </div>
                )}
              </div>

              {/* ENTRY LEVELS */}
              <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-4">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Entry Plan</span>
                  <span className={`text-[9px] font-black px-2 py-0.5 rounded-lg ${orderTypeColor(planA.label)}`}>{planA.label}</span>
                </div>
                <div className="grid grid-cols-5 gap-2">
                  {[
                    { label: 'Entry', value: fmt(planA.entry), color: 'text-[var(--text-primary)]' },
                    { label: 'SL', value: fmt(planA.sl), color: 'text-[#f43f5e]' },
                    { label: 'TP1', value: fmt(planA.tp1), color: 'text-[#10b981]' },
                    { label: 'TP2', value: fmt(planA.tp2), color: 'text-[#10b981]/70' },
                    { label: 'TP3', value: fmt(planA.tp3), color: 'text-[#10b981]/50' },
                  ].map(({ label, value, color }) => (
                    <div key={label} className="bg-[var(--bg-card)] rounded-xl p-2.5 text-center">
                      <div className="text-[7px] text-[var(--text-dim)] font-bold uppercase mb-1">{label}</div>
                      <div className={`text-[10px] font-black font-mono ${color}`}>{value}</div>
                    </div>
                  ))}
                </div>
                {signalResult.rr && signalResult.rr !== 'N/A' && (
                  <div className="mt-2.5 flex items-center gap-2 text-[9px]">
                    <span className="text-[var(--text-dim)] font-bold">RR</span>
                    <span className="font-black text-[var(--accent)] font-mono">{signalResult.rr}</span>
                    {signalResult.score != null && <><span className="text-[var(--text-dim)]">·</span><span className="text-[var(--text-dim)] font-bold">Score</span><span className="font-black text-[var(--accent)]">{signalResult.score}/100</span></>}
                  </div>
                )}
              </div>

              {/* Plan B — limit entry */}
              {hasPlanB && (
                <div className="bg-[var(--bg-panel)] border border-blue-500/20 rounded-2xl p-4 opacity-85">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <div className="w-5 h-5 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center">
                        <span className="text-[8px] font-black text-blue-300">B</span>
                      </div>
                      <span className="text-[10px] font-black text-[var(--text-secondary)] uppercase tracking-widest">Plan B — Limit Entry</span>
                    </div>
                    <span className="text-[9px] font-black px-2 py-0.5 rounded-lg bg-blue-400/20 text-blue-400">{isUp ? 'BUY LIMIT' : 'SELL LIMIT'}</span>
                  </div>
                  <div className="grid grid-cols-3 gap-2">
                    <div className="bg-[var(--bg-card)] rounded-xl p-2.5 text-center">
                      <div className="text-[7px] text-[var(--text-dim)] font-bold uppercase mb-1">Limit Entry</div>
                      <div className="text-[10px] font-black font-mono text-blue-400">{fmt(planBEntry)}</div>
                    </div>
                    <div className="bg-[var(--bg-card)] rounded-xl p-2.5 text-center">
                      <div className="text-[7px] text-[var(--text-dim)] font-bold uppercase mb-1">SL</div>
                      <div className="text-[10px] font-black font-mono text-[#f43f5e]">{fmt(planA.sl)}</div>
                    </div>
                    <div className="bg-[var(--bg-card)] rounded-xl p-2.5 text-center">
                      <div className="text-[7px] text-[var(--text-dim)] font-bold uppercase mb-1">TP1</div>
                      <div className="text-[10px] font-black font-mono text-[#10b981]">{fmt(planBTp1)}</div>
                    </div>
                  </div>
                  <div className="mt-2 text-[9px] text-[var(--text-dim)]">
                    {signalResult.plan_b || `Wait for price to retrace to ${isUp ? 'support' : 'resistance'} level for better entry.`}
                  </div>
                </div>
              )}

              {/* CONTEXT CHIPS */}
              <div className="flex flex-wrap gap-1.5">
                <span className="text-[8px] font-black px-2 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)]">🕐 {signalResult.session || ctx.sessionName}</span>
                <span className="text-[8px] font-black px-2 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)]">📊 {signalResult.amd_phase || ctx.amdPhase}</span>
                {ctx.killZone && <span className="text-[8px] font-black px-2 py-1 rounded-lg bg-orange-400/10 border border-orange-400/30 text-orange-400">{ctx.killZone}</span>}
                {corrSig && <span className="text-[8px] font-black px-2 py-1 rounded-lg border" style={{ color: corrColor, borderColor: `${corrColor}40`, background: `${corrColor}10` }}>DXY {corrSig.replace('_',' ')}</span>}
                {dxyBias && <span className="text-[8px] font-black px-2 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)]">DXY {dxyBias}</span>}
                {xauBias && <span className="text-[8px] font-black px-2 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)]">XAU {xauBias}</span>}
                {signalResult.momentum && <span className="text-[8px] font-black px-2 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)]">⚡ {signalResult.momentum}</span>}
              </div>

              {/* MTF TABLE */}
              {signalResult.mtf_detail && Object.keys(signalResult.mtf_detail).length > 0 && (
                <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
                  <div className="px-3 py-2 border-b border-[var(--border-color)] flex items-center gap-2">
                    <span className="text-[8px] font-black text-[var(--text-dim)] uppercase tracking-widest">Multi-Timeframe</span>
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-[8px]">
                      <thead>
                        <tr className="bg-[var(--bg-card)]/50">
                          {['TF','Trend','RSI','MACD','EMA','ADX','Price'].map(h => (
                            <th key={h} className={`px-2 py-1.5 ${h==='TF'?'text-left':'text-center'} text-[var(--text-dim)] font-bold`}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(signalResult.mtf_detail).map(([tf, data]) => (
                          <tr key={tf} className="border-t border-[var(--border-color)]/30">
                            <td className="px-2 py-1.5 font-black text-[var(--accent)]">{tf}</td>
                            <td className="px-2 py-1.5 text-center font-black" style={{ color: data.trend==='BULLISH'?'#10b981':data.trend==='BEARISH'?'#f43f5e':'#f59e0b' }}>{data.trend?.slice(0,4) || '-'}</td>
                            <td className="px-2 py-1.5 text-center" style={{ color: data.rsi>70?'#f43f5e':data.rsi<30?'#10b981':'var(--text-secondary)' }}>{data.rsi?.toFixed(1) || '-'}</td>
                            <td className="px-2 py-1.5 text-center" style={{ color: data.macd_signal==='BULLISH'?'#10b981':data.macd_signal==='BEARISH'?'#f43f5e':'var(--text-dim)' }}>{data.macd_signal?.slice(0,4) || '-'}</td>
                            <td className="px-2 py-1.5 text-center" style={{ color: data.ema_signal==='BULLISH'?'#10b981':data.ema_signal==='BEARISH'?'#f43f5e':'var(--text-dim)' }}>{data.ema_signal?.slice(0,4) || '-'}</td>
                            <td className="px-2 py-1.5 text-center text-[var(--text-dim)]">{data.adx_value?.toFixed(0) || '-'}</td>
                            <td className="px-2 py-1.5 text-center text-[var(--text-primary)] font-mono">{data.price?.toFixed(2) || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* NARRATIVE CARDS */}
              <div className="space-y-2">
                {signalResult.trigger && (
                  <div className="flex items-start gap-2.5 bg-[var(--accent)]/5 border border-[var(--accent)]/15 rounded-xl px-3 py-2.5">
                    <Zap size={12} className="shrink-0 mt-0.5 text-[var(--accent)]" />
                    <p className="text-[10px] font-bold text-[var(--text-secondary)]">{signalResult.trigger}</p>
                  </div>
                )}
                {signalResult.reasoning && (
                  <div className="flex items-start gap-2.5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-3 py-2.5">
                    <Layers size={12} className="shrink-0 mt-0.5 text-[var(--text-dim)]" />
                    <p className="text-[10px] text-[var(--text-dim)] leading-relaxed">{signalResult.reasoning}</p>
                  </div>
                )}
                {signalResult.trading_plan && (
                  <div className="flex items-start gap-2.5 bg-blue-500/5 border border-blue-500/15 rounded-xl px-3 py-2.5">
                    <Target size={12} className="shrink-0 mt-0.5 text-blue-400" />
                    <p className="text-[10px] text-[var(--text-dim)] leading-relaxed">{signalResult.trading_plan}</p>
                  </div>
                )}
                {signalResult.invalidation && (
                  <div className="flex items-start gap-2.5 bg-[#f43f5e]/5 border border-[#f43f5e]/15 rounded-xl px-3 py-2.5">
                    <Shield size={12} className="shrink-0 mt-0.5 text-[#f43f5e]/60" />
                    <p className="text-[9px] text-[#f43f5e]/70 leading-relaxed"><span className="font-black">Invalidation:</span> {signalResult.invalidation}</p>
                  </div>
                )}
                {signalResult.htf_analysis && (
                  <div className="flex items-start gap-2.5 bg-purple-500/5 border border-purple-500/15 rounded-xl px-3 py-2.5">
                    <span className="text-[8px] font-black text-purple-400 shrink-0 mt-0.5">HTF</span>
                    <p className="text-[9px] text-[var(--text-dim)] leading-relaxed">{signalResult.htf_analysis}</p>
                  </div>
                )}
                {signalResult.ltf_entry && (
                  <div className="flex items-start gap-2.5 bg-cyan-500/5 border border-cyan-500/15 rounded-xl px-3 py-2.5">
                    <span className="text-[8px] font-black text-cyan-400 shrink-0 mt-0.5">LTF</span>
                    <p className="text-[9px] text-[var(--text-dim)] leading-relaxed">{signalResult.ltf_entry}</p>
                  </div>
                )}
                {signalResult.risk_management && (
                  <div className="flex items-start gap-2.5 bg-amber-500/5 border border-amber-500/15 rounded-xl px-3 py-2.5">
                    <span className="text-[8px] font-black text-amber-400 shrink-0 mt-0.5">RISK</span>
                    <p className="text-[9px] text-[var(--text-dim)] leading-relaxed">{signalResult.risk_management}</p>
                  </div>
                )}
                {signalResult.psychology && (
                  <div className="flex items-start gap-2.5 bg-green-500/5 border border-green-500/15 rounded-xl px-3 py-2.5">
                    <span className="text-[8px] font-black text-green-400 shrink-0 mt-0.5">🧠</span>
                    <p className="text-[9px] text-[var(--text-dim)] leading-relaxed">{signalResult.psychology}</p>
                  </div>
                )}
                {signalResult.observation && (
                  <div className="flex items-start gap-2.5 bg-blue-500/5 border border-blue-500/15 rounded-xl px-3 py-2.5">
                    <span className="text-[8px] font-black text-blue-400 shrink-0 mt-0.5">OBS</span>
                    <p className="text-[9px] text-[var(--text-dim)] leading-relaxed">{signalResult.observation}</p>
                  </div>
                )}
                {signalResult.journal_entry && (
                  <div className="flex items-start gap-2.5 bg-purple-500/5 border border-purple-500/15 rounded-xl px-3 py-2.5">
                    <span className="text-[8px] font-black text-purple-400 shrink-0 mt-0.5">JRNL</span>
                    <p className="text-[9px] text-[var(--text-dim)] leading-relaxed">{signalResult.journal_entry}</p>
                  </div>
                )}
                {signalResult.ai_source === 'indicator-fallback' && (
                  <div className="text-[8px] text-yellow-400 font-bold opacity-70 text-center">⚠️ AI model offline — signal from indicator engine</div>
                )}
              </div>
            </div>
            );
          })()}

          {!signalResult && !signalLoading && !signalError && (
            <div className="flex flex-col items-center justify-center py-14 text-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center">
                <Zap size={24} className="text-[var(--text-dim)]" />
              </div>
              <p className="text-xs text-[var(--text-dim)] font-bold">Select pair, style & timeframe</p>
              <p className="text-[9px] text-[var(--text-dim)]">Generates Plan A + Plan B with full SMC analysis · 3 credits</p>
            </div>
          )}
        </div>
      )}

      {/* ── TAB: Technical ────────────────────────────────────────────────────── */}
      {activeTab === 'Technical' && (
        <div className="space-y-4">
          <div className="flex flex-col sm:flex-row gap-3">
            <div className="flex-1">
              <div className="text-[9px] font-bold text-[var(--text-dim)] mb-1.5 uppercase tracking-widest">Pair</div>
              <div className="flex flex-wrap gap-2">
                {FOREX_PAIRS.filter(p => p.type !== 'index').slice(0, 8).map(p => (
                  <button
                    key={p.symbol}
                    onClick={() => setSelectedPair(p.symbol)}
                    className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${selectedPair === p.symbol ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--accent)]/40'}`}
                  >
                    {p.emoji} {p.symbol}
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
                    className={`px-2.5 py-1.5 rounded-lg text-[10px] font-black transition-all ${timeframe === tf ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--accent)]/40'}`}
                  >
                    {tf}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button
            onClick={fetchTechnical}
            disabled={techLoading}
            className="flex items-center gap-2 px-5 py-3 bg-[var(--accent)] text-black rounded-xl text-xs font-black uppercase tracking-widest hover:opacity-90 transition-opacity disabled:opacity-50"
          >
            {techLoading ? <RefreshCw size={14} className="animate-spin" /> : <BarChart2 size={14} />}
            {techLoading ? 'Analyzing...' : `Analyze ${selectedPair}`} · {timeframe}
          </button>

          {techError && (
            <div className="flex items-center gap-2 p-3 bg-[#f43f5e]/10 border border-[#f43f5e]/20 rounded-xl text-xs text-[#f43f5e] font-bold">
              <AlertTriangle size={14} /> {techError}
            </div>
          )}

          {techResult && (() => {
            // Strategy-core returns: recommendation, confidence, signals, ai_interpretation, confluence_score, setup_type
            const rec = techResult.recommendation || techResult.bias || 'NEUTRAL';
            const conf = techResult.confidence || 0;
            const signals = techResult.signals || techResult.indicators || {};
            const aiText = techResult.ai_interpretation || techResult.reasoning || techResult.analysis || '';
            const isUp = rec === 'BUY';
            const isDown = rec === 'SELL';
            const recColor = isUp ? 'text-[#10b981]' : isDown ? 'text-[#f43f5e]' : 'text-yellow-400';
            const recBg = isUp ? 'bg-[#10b981]/10 border-[#10b981]/30' : isDown ? 'bg-[#f43f5e]/10 border-[#f43f5e]/30' : 'bg-yellow-400/10 border-yellow-400/30';

            // Build flat indicator display map from signals
            const indicatorDisplay = {};
            Object.entries(signals).forEach(([key, val]) => {
              if (key === 'SMC' && typeof val === 'object' && val) {
                indicatorDisplay['SMC Bias'] = val.bias || 'N/A';
                if (val.structure) indicatorDisplay['Structure'] = val.structure;
                if (val.amd_phase) indicatorDisplay['AMD Phase'] = val.amd_phase;
                if (val.smc_score != null) indicatorDisplay['SMC Score'] = `${val.smc_score}/100`;
              } else if (typeof val === 'object' && val) {
                const v = val.value ?? val.macd ?? val.ema20 ?? '';
                const s = val.signal || val.action || '';
                indicatorDisplay[key] = v !== '' ? `${Number(v).toFixed(2)} — ${s}` : s;
              } else {
                indicatorDisplay[key] = String(val);
              }
            });

            return (
            <div className="space-y-4">
              {/* Recommendation Banner */}
              <div className={`rounded-2xl p-4 border flex items-center gap-4 ${recBg}`}>
                {isUp ? <TrendingUp size={24} className="text-[#10b981]" /> : isDown ? <TrendingDown size={24} className="text-[#f43f5e]" /> : <Minus size={24} className="text-yellow-400" />}
                <div className="flex-1">
                  <div className={`text-xl font-black ${recColor}`}>{rec}</div>
                  <div className="text-[10px] text-[var(--text-dim)]">{selectedPair} · {timeframe} · Confidence {conf}%</div>
                </div>
                {techResult.confluence_score != null && (
                  <div className="text-right">
                    <div className="text-lg font-black font-mono text-[var(--accent)]">{techResult.confluence_score}</div>
                    <div className="text-[8px] text-[var(--text-dim)]">Confluence</div>
                  </div>
                )}
              </div>

              {/* Indicators grid */}
              {Object.keys(indicatorDisplay).length > 0 && (
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                  {Object.entries(indicatorDisplay).map(([key, val]) => (
                    <div key={key} className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-3">
                      <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">{key}</div>
                      <div className="text-xs font-black font-mono text-[var(--text-primary)] truncate">{String(val)}</div>
                    </div>
                  ))}
                </div>
              )}

              {/* Setup type */}
              {techResult.setup_type && (
                <div className="flex gap-3 text-[10px]">
                  <span className="px-2 py-1 rounded-lg bg-[var(--accent)]/10 text-[var(--accent)] font-bold">📐 {techResult.setup_type}</span>
                  {techResult.current_price && <span className="px-2 py-1 rounded-lg bg-[var(--bg-card)] text-[var(--text-dim)] font-mono">Price: {techResult.current_price}</span>}
                </div>
              )}

              {/* AI interpretation */}
              {aiText && (
                <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-4">
                  <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">AI Analysis</div>
                  <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{aiText}</p>
                </div>
              )}
            </div>
            );
          })()}

          {!techResult && !techLoading && !techError && (
            <div className="flex flex-col items-center justify-center py-16 text-center gap-3">
              <div className="w-14 h-14 rounded-2xl bg-[var(--bg-panel)] border border-[var(--border-color)] flex items-center justify-center">
                <BarChart2 size={24} className="text-[var(--text-dim)]" />
              </div>
              <p className="text-xs text-[var(--text-dim)] font-bold">Select a pair and run technical analysis</p>
            </div>
          )}
        </div>
      )}

      {/* ── TAB: Session ──────────────────────────────────────────────────────── */}
      {activeTab === 'Session' && (
        <div className="space-y-5">
          <div className="text-center py-4 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl">
            <div className="text-3xl font-black font-mono text-[var(--accent)]">{utcStr}</div>
            <div className="text-[9px] text-[var(--text-dim)] mt-1 font-bold uppercase tracking-widest">Current UTC Time</div>
          </div>

          <div className="grid gap-4">
            {SESSIONS.map(session => {
              const active = isSessionActive(session);
              const countdown = !active ? timeUntilSession(session) : null;
              return (
                <div
                  key={session.id}
                  className={`rounded-2xl p-5 border transition-all ${active ? '' : 'bg-[var(--bg-panel)] border-[var(--border-color)]'}`}
                  style={active ? { borderColor: session.color, background: `${session.color}10` } : {}}
                >
                  <div className="flex items-center gap-3 mb-4">
                    <span className="text-2xl">{session.emoji}</span>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="text-sm font-black text-[var(--text-primary)]">{session.name} Session</div>
                        {active && (
                          <span className="text-[8px] font-black px-2 py-0.5 rounded-full text-black" style={{ background: session.color }}>
                            ACTIVE NOW
                          </span>
                        )}
                      </div>
                      <div className="text-[10px] text-[var(--text-dim)]">{session.open}:00 – {session.close}:00 UTC</div>
                    </div>
                    {!active && countdown && (
                      <div className="text-right">
                        <div className="text-xs font-black font-mono text-[var(--text-secondary)]">{countdown.hours}h {countdown.minutes}m</div>
                        <div className="text-[8px] text-[var(--text-dim)]">opens in</div>
                      </div>
                    )}
                  </div>

                  <div>
                    <div className="text-[9px] font-bold text-[var(--text-dim)] mb-2 uppercase tracking-wide">Best Pairs</div>
                    <div className="flex flex-wrap gap-2">
                      {session.pairs.map(p => (
                        <span
                          key={p}
                          className="text-[9px] font-black px-2 py-1 rounded-lg"
                          style={{ background: `${session.color}20`, color: session.color }}
                        >
                          {p}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Trading rec by session */}
          <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-4">
            <div className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">Session Trading Guide</div>
            <div className="space-y-2 text-[10px] text-[var(--text-secondary)]">
              <div className="flex items-start gap-2"><span className="text-[#f97316] font-black shrink-0">🏯 Asian:</span><span>Low volume, tight ranges. Best for range trading USDJPY, AUDUSD. Avoid wide-stop strategies.</span></div>
              <div className="flex items-start gap-2"><span className="text-[#8b5cf6] font-black shrink-0">🇬🇧 London:</span><span>Highest trending momentum. EUR/GBP pairs move strongly. XAUUSD breakouts frequent.</span></div>
              <div className="flex items-start gap-2"><span className="text-[#10b981] font-black shrink-0">🗽 New York:</span><span>Economic data releases drive USD pairs. Overlap with London 13:00–17:00 UTC is peak volatility.</span></div>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'Data' && (
        <div className="space-y-4">
          <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
            <div className="px-4 py-2.5 border-b border-[var(--border-color)] flex items-center gap-2">
              <i className="fa-solid fa-table text-[var(--accent)] text-xs" />
              <span className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest">OHLCV — Live Prices</span>
            </div>
            <div className="overflow-x-auto">
              <table className="data-tbl">
                <thead><tr>
                  <th>Pair</th><th>Price</th><th>Change</th><th>Spread</th><th>Type</th>
                </tr></thead>
                <tbody>
                  {FOREX_PAIRS.filter(p => p.type !== 'index').map(p => {
                    const pr = prices?.[p.symbol];
                    const chg = pr && p.base ? ((pr - p.base) / p.base * 100) : 0;
                    return (
                      <tr key={p.symbol} style={{ cursor:'pointer' }} onClick={() => setSelectedPair(p.symbol)}>
                        <td><span className="td-name">{p.emoji} {p.symbol}</span><br/><span style={{fontSize:'8px',color:'var(--text-dim)'}}>{p.name}</span></td>
                        <td>{pr ? pr.toFixed(p.decimals) : '--'}</td>
                        <td className={chg >= 0 ? 'td-up' : 'td-down'}>{chg >= 0 ? '+' : ''}{chg.toFixed(3)}%</td>
                        <td className="td-down" style={{opacity:.6}}>live</td>
                        <td><span style={{fontSize:'8px',padding:'2px 6px',borderRadius:'10px',background:'var(--bg-card)',border:'1px solid var(--border-color)',color:'var(--text-dim)'}}>{p.type}</span></td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* DXY correlation block */}
          <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4">
            <div className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-3">📉 DXY Correlation Matrix</div>
            <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
              {[{pair:'XAUUSD',corr:'-0.82'},{pair:'EURUSD',corr:'-0.91'},{pair:'GBPUSD',corr:'-0.87'},{pair:'USDJPY',corr:'+0.78'}].map(c => (
                <div key={c.pair} className="bg-[var(--bg-panel)] rounded-lg p-3 text-center">
                  <div className="text-[9px] font-black text-[var(--text-dim)]">{c.pair}</div>
                  <div className={`text-base font-black font-mono mt-1 ${c.corr.startsWith('-') ? 'text-[#f43f5e]' : 'text-[#10b981]'}`}>{c.corr}</div>
                  <div className="text-[8px] text-[var(--text-dim)]">correlation</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'AI Insight' && (
        <div className="space-y-4">
          <div className="ai-insight-card">
            <h4>🧠 AI Market Summary</h4>
            <p className="ai-insight-text">
              Real-time AI analysis synthesizes SMC structure, DXY correlation, session context, and multi-timeframe momentum to generate high-probability setups. Current market environment is analyzed across 6 dimensions: structure, momentum, session, macro, correlation, and sentiment.
            </p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">GAS Quantum v3</span>
              <span className="ai-badge ai-badge--green">SMC Active</span>
              <span className="ai-badge">MTF Confluence</span>
              <span className="ai-badge">DXY Corr</span>
              <span className="ai-badge">Session Bias</span>
            </div>
          </div>

          <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
            <div className="px-4 py-2.5 border-b border-[var(--border-color)]">
              <span className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest">🏆 AI Model Performance</span>
            </div>
            <table className="data-tbl">
              <thead><tr><th>Model</th><th>Tier</th><th>Accuracy</th><th>Cost</th><th>Best For</th></tr></thead>
              <tbody>
                {SIGNAL_MODEL_TIERS.map(m => (
                  <tr key={m.tier}>
                    <td className="td-name">{m.label}</td>
                    <td><span className="ai-badge ai-badge--gold">{m.badge}</span></td>
                    <td className="td-up">—</td>
                    <td>{m.signal_cost} cr</td>
                    <td style={{color:'var(--text-dim)',fontSize:'9px'}}>{m.desc}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { label:'Smart Money Flow', value:'Accumulation', badge:'gold', icon:'🏦' },
              { label:'Market Structure', value:'Bullish HTF', badge:'green', icon:'📊' },
              { label:'Risk Environment', value:'Medium', badge:'', icon:'🛡️' },
            ].map(item => (
              <div key={item.label} className="sig-card">
                <div className="text-lg mb-1">{item.icon}</div>
                <div className="text-[9px] font-bold text-[var(--text-dim)] uppercase tracking-wide mb-1">{item.label}</div>
                <div className="text-sm font-black text-[var(--text-primary)]">{item.value}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      </>)}

      {/* Analysis Modal */}
      {analysisLoading && (
        <div className="fixed inset-0 z-[500] flex items-center justify-center bg-black/60 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3">
            <RefreshCw size={32} className="animate-spin text-[var(--accent)]" />
            <p className="text-sm font-bold text-white">Analyzing {modalSymbol}...</p>
          </div>
        </div>
      )}
      {!analysisLoading && (modalResult || analysisError) && (
        <ResultModal
          result={modalResult}
          error={analysisError}
          symbol={modalSymbol}
          onClose={() => { setModalResult(null); setAnalysisError(''); setModalSymbol(''); }}
        />
      )}
    </div>
  );
}
