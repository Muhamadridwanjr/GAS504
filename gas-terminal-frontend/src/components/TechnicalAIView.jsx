import React, { useState } from 'react';
import {
  BarChart2, Zap, RefreshCw, TrendingUp, TrendingDown, Activity,
  Crosshair, Clock, Cpu, Shield, AlertTriangle, CheckCircle2, ChevronDown, ChevronUp,
} from 'lucide-react';
import { callAIFeature } from '../services/api';
import PairSelector from './PairSelector';
import StyleSelector, { STYLE_MATRIX } from './StyleSelector';

// ── Indicator definitions grouped by category ────────────────────────────────
const INDICATOR_GROUPS = [
  {
    id: 'ma', label: 'Moving Averages', emoji: '📈',
    items: [
      { key: 'sma5',   name: 'SMA 5',    sub: 'Fast SMA',      color: '#f59e0b' },
      { key: 'sma10',  name: 'SMA 10',   sub: 'Short SMA',     color: '#f59e0b' },
      { key: 'sma20',  name: 'SMA 20',   sub: 'Medium SMA',    color: '#f59e0b' },
      { key: 'sma50',  name: 'SMA 50',   sub: 'Trend SMA',     color: '#f59e0b' },
      { key: 'sma100', name: 'SMA 100',  sub: 'Slow SMA',      color: '#f59e0b' },
      { key: 'sma200', name: 'SMA 200',  sub: 'Major SMA',     color: '#f59e0b' },
      { key: 'ema5',   name: 'EMA 5',    sub: 'Fast EMA',      color: '#10b981' },
      { key: 'ema10',  name: 'EMA 10',   sub: 'Short EMA',     color: '#10b981' },
      { key: 'ema20',  name: 'EMA 20',   sub: 'Medium EMA',    color: '#10b981' },
      { key: 'ema50',  name: 'EMA 50',   sub: 'Trend EMA',     color: '#10b981' },
      { key: 'ema100', name: 'EMA 100',  sub: 'Slow EMA',      color: '#10b981' },
      { key: 'ema200', name: 'EMA 200',  sub: 'Major EMA',     color: '#14b8a6' },
    ],
  },
  {
    id: 'osc', label: 'Oscillators', emoji: '📊',
    items: [
      { key: 'rsi',       name: 'RSI 14',          sub: 'Relative Strength',    color: '#3b82f6' },
      { key: 'stoch',     name: 'Stochastic',       sub: '9,6 · K/D Lines',      color: '#fac815' },
      { key: 'stochrsi',  name: 'Stoch RSI',        sub: '14 · Fast Momentum',   color: '#f97316' },
      { key: 'macd',      name: 'MACD',             sub: '12,26,9 · Trend Mom',  color: '#8b5cf6' },
      { key: 'cci',       name: 'CCI 14',           sub: 'Commodity Channel',    color: '#ec4899' },
      { key: 'williamsr', name: 'Williams %R',      sub: '14 · Overbought/sold', color: '#06b6d4' },
      { key: 'uo',        name: 'Ultimate Osc',     sub: '7,14,28 · Weighted',   color: '#a855f7' },
      { key: 'roc',       name: 'ROC',              sub: '9 · Rate of Change',   color: '#84cc16' },
      { key: 'bullpower', name: 'Bull Power',       sub: '13 · Elder Ray',       color: '#10b981' },
      { key: 'bearpower', name: 'Bear Power',       sub: '13 · Elder Ray',       color: '#ef4444' },
    ],
  },
  {
    id: 'trend', label: 'Trend & Volatility', emoji: '💪',
    items: [
      { key: 'adx',     name: 'ADX 14',         sub: 'Trend Strength',      color: '#f97316' },
      { key: 'atr',     name: 'ATR 14',         sub: 'Average True Range',  color: '#06b6d4' },
      { key: 'bb',      name: 'Bollinger Bands',sub: '20 · ±2σ Bands',      color: '#ec4899' },
      { key: 'highs',   name: 'Highs/Lows',     sub: '14 · Swing Points',   color: '#fac815' },
    ],
  },
  {
    id: 'pivot', label: 'Pivot Points', emoji: '🎯',
    items: [
      { key: 'pivot_classic', name: 'Classic Pivots',   sub: 'P / R1-R3 / S1-S3',     color: '#a855f7' },
      { key: 'pivot_fib',     name: 'Fibonacci Pivots', sub: 'P / FibR1-R3 / FibS1-S3', color: '#f59e0b' },
    ],
  },
  {
    id: 'smc', label: 'Smart Money', emoji: '🧱',
    items: [
      { key: 'smc', name: 'SMC Structure', sub: 'OB · FVG · BOS · CHoCH', color: '#a855f7' },
    ],
  },
];

const ALL_INDICATORS = INDICATOR_GROUPS.flatMap(g => g.items);

// Signal classification helpers
const SIGNAL_BUY  = new Set(['BUY','BULLISH','OVERSOLD','STRONG BUY','UPTREND','ABOVE','BULLISH CROSS']);
const SIGNAL_SELL = new Set(['SELL','BEARISH','OVERBOUGHT','STRONG SELL','DOWNTREND','BELOW','BEARISH CROSS']);

function sigClass(sig = '') {
  const s = sig.toUpperCase();
  if (SIGNAL_BUY.has(s))  return 'text-emerald-400';
  if (SIGNAL_SELL.has(s)) return 'text-red-400';
  return 'text-[var(--text-dim)]';
}

function sigBg(sig = '') {
  const s = sig.toUpperCase();
  if (SIGNAL_BUY.has(s))  return { bg: 'rgba(16,185,129,0.05)', border: 'rgba(16,185,129,0.3)' };
  if (SIGNAL_SELL.has(s)) return { bg: 'rgba(239,68,68,0.05)',  border: 'rgba(239,68,68,0.3)' };
  return { bg: 'var(--bg-card)', border: 'var(--border-color)' };
}

function countSignals(signals = {}) {
  let buy = 0, sell = 0, neutral = 0;
  Object.values(signals).forEach(v => {
    if (!v || typeof v !== 'object') return;
    const sig = (v.signal || v.action || '').toUpperCase();
    if (SIGNAL_BUY.has(sig))  buy++;
    else if (SIGNAL_SELL.has(sig)) sell++;
    else neutral++;
  });
  return { buy, sell, neutral, total: buy + sell + neutral };
}

// ── Confluence bar ────────────────────────────────────────────────────────────
function ConfluenceBar({ score }) {
  const color = score >= 70 ? 'text-emerald-400' : score >= 50 ? 'text-yellow-400' : 'text-red-400';
  const bg    = score >= 70 ? 'bg-emerald-400'   : score >= 50 ? 'bg-yellow-400'   : 'bg-red-400';
  const label = score >= 70 ? 'STRONG'           : score >= 50 ? 'MODERATE'        : 'WEAK';
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 space-y-1">
        <div className="flex items-center justify-between">
          <span className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-wider">Confluence Score</span>
          <span className={`text-xs font-black font-mono ${color}`}>{score}/100 · {label}</span>
        </div>
        <div className="h-2 bg-[var(--bg-hover)] rounded-full overflow-hidden">
          <div className={`h-full rounded-full transition-all duration-700 ${bg}`}
            style={{ width: `${score}%` }} />
        </div>
      </div>
    </div>
  );
}

// ── Summary Gauge (TradingView style) ────────────────────────────────────────
function SummaryGauge({ buy, neutral, sell, label = 'Summary' }) {
  const total = buy + neutral + sell || 1;
  const verdict = buy > sell * 1.5 ? 'STRONG BUY'
    : buy > sell ? 'BUY'
    : sell > buy * 1.5 ? 'STRONG SELL'
    : sell > buy ? 'SELL'
    : 'NEUTRAL';
  const verdictColor =
    verdict === 'STRONG BUY'  ? 'text-emerald-400' :
    verdict === 'BUY'         ? 'text-green-400' :
    verdict === 'STRONG SELL' ? 'text-red-400' :
    verdict === 'SELL'        ? 'text-rose-400' :
    'text-[var(--text-dim)]';

  return (
    <div className="bg-[var(--bg-panel)] rounded-xl p-3 border border-[var(--border-color)] text-center space-y-2">
      <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)]">{label}</p>
      <p className={`text-base font-black font-mono ${verdictColor}`}>{verdict}</p>
      {/* Bar */}
      <div className="flex h-1.5 rounded-full overflow-hidden gap-px">
        <div className="bg-emerald-400 rounded-l-full transition-all duration-500" style={{ width: `${(buy/total)*100}%` }} />
        <div className="bg-[var(--bg-hover)] transition-all duration-500"          style={{ width: `${(neutral/total)*100}%` }} />
        <div className="bg-red-400 rounded-r-full transition-all duration-500"     style={{ width: `${(sell/total)*100}%` }} />
      </div>
      <div className="flex justify-between text-[8px] font-black">
        <span className="text-emerald-400">{buy} Buy</span>
        <span className="text-[var(--text-dim)]">{neutral} Neutral</span>
        <span className="text-red-400">{sell} Sell</span>
      </div>
    </div>
  );
}

// ── Tag chip ─────────────────────────────────────────────────────────────────
function Tag({ label, color = 'text-purple-400', bg = 'bg-purple-400/10', border = 'border-purple-400/25', icon: Icon }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-lg border text-[9px] font-black ${color} ${bg} ${border}`}>
      {Icon && <Icon size={8} />} {label}
    </span>
  );
}

// ── Pivot table row ───────────────────────────────────────────────────────────
function PivotRow({ label, value, type }) {
  const isR = label.startsWith('R');
  const isS = label.startsWith('S');
  const isP = label === 'Pivot';
  return (
    <div className={`flex items-center justify-between px-3 py-1.5 rounded-lg border ${
      isR ? 'border-emerald-400/20 bg-emerald-400/5' :
      isS ? 'border-red-400/20 bg-red-400/5' :
      'border-[var(--border-color)] bg-[var(--bg-hover)]'
    }`}>
      <span className={`text-[9px] font-black ${isR ? 'text-emerald-400' : isS ? 'text-red-400' : 'text-[var(--accent)]'}`}>
        {label}
      </span>
      <span className="text-[10px] font-mono font-black text-[var(--text-primary)]">
        {value != null ? (typeof value === 'number' ? value.toFixed(4) : value) : '-'}
      </span>
    </div>
  );
}

// ── Collapsible group header ──────────────────────────────────────────────────
function GroupHeader({ emoji, label, count, total, open, onToggle }) {
  return (
    <button onClick={onToggle}
      className="w-full flex items-center gap-2 px-3 py-2 rounded-xl border border-[var(--border-color)] bg-[var(--bg-panel)] hover:bg-[var(--bg-hover)] transition-all">
      <span className="text-sm">{emoji}</span>
      <span className="text-[9px] font-black uppercase tracking-wider text-[var(--text-secondary)] flex-1 text-left">{label}</span>
      <span className="text-[8px] text-[var(--text-dim)] font-mono">{count}/{total} selected</span>
      {open ? <ChevronUp size={12} className="text-[var(--text-dim)]" /> : <ChevronDown size={12} className="text-[var(--text-dim)]" />}
    </button>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
export default function TechnicalAIView() {
  const [pair, setPair]       = useState('XAUUSD');
  const [style, setStyle]     = useState('scalping');
  const [loading, setLoading] = useState(false);
  const [result, setResult]   = useState(null);
  const [openGroups, setOpenGroups] = useState({ ma: true, osc: true, trend: true, pivot: false, smc: true });
  const [selectedIndicators, setSelectedIndicators] = useState([
    'rsi','macd','ema50','ema200','sma20','sma50','adx','stoch','atr','bb','smc','pivot_classic',
  ]);

  const styleTFs   = STYLE_MATRIX[style]?.tfs || ['H4','H1','M15','M5'];
  const primaryTF  = styleTFs[2] || 'M15';

  const toggleIndicator = (key) => {
    setSelectedIndicators(prev =>
      prev.includes(key) ? prev.filter(k => k !== key) : [...prev, key]
    );
  };

  const toggleGroup = (id) => setOpenGroups(prev => ({ ...prev, [id]: !prev[id] }));

  const selectAll   = (groupId) => {
    const keys = INDICATOR_GROUPS.find(g => g.id === groupId)?.items.map(i => i.key) || [];
    setSelectedIndicators(prev => [...new Set([...prev, ...keys])]);
  };
  const deselectAll = (groupId) => {
    const keys = new Set(INDICATOR_GROUPS.find(g => g.id === groupId)?.items.map(i => i.key) || []);
    setSelectedIndicators(prev => prev.filter(k => !keys.has(k)));
  };

  const fetchAnalysis = async () => {
    setLoading(true);
    setResult(null);
    try {
      const res = await callAIFeature('technical', {
        pair,
        style,
        timeframe: primaryTF,
        timeframes: styleTFs,
        indicators: selectedIndicators.map(k => k.toUpperCase()),
      });
      setResult(res);
    } catch (err) {
      setResult({ error: true, message: err?.response?.data?.detail || 'Gagal memuat analisa. Pastikan EA MT5 berjalan.' });
    } finally {
      setLoading(false);
    }
  };

  // ── Result helpers ──────────────────────────────────────────────────────────
  const bias      = result?.recommendation || result?.bias || result?.signal;
  const isBuy     = bias === 'BUY' || bias === 'STRONG BUY';
  const isSell    = bias === 'SELL' || bias === 'STRONG SELL';
  const smc       = result?.signals?.SMC || null;
  const hasSMC    = result?.smc_available && smc;
  const signals   = result?.signals || {};

  // Signals per group (excluding SMC & pivots)
  const maKeys  = new Set(INDICATOR_GROUPS.find(g=>g.id==='ma')?.items.map(i=>i.key.toUpperCase()) || []);
  const oscKeys = new Set(INDICATOR_GROUPS.find(g=>g.id==='osc')?.items.map(i=>i.key.toUpperCase()) || []);

  const maSigs  = Object.fromEntries(Object.entries(signals).filter(([k]) => maKeys.has(k)));
  const oscSigs = Object.fromEntries(Object.entries(signals).filter(([k]) => oscKeys.has(k)));
  const allSigs = Object.fromEntries(Object.entries(signals).filter(([k]) => k !== 'SMC' && !k.startsWith('PIVOT')));

  const maCount   = countSignals(maSigs);
  const oscCount  = countSignals(oscSigs);
  const allCount  = countSignals(allSigs);

  // Pivot data
  const pivotClassic = result?.pivot_classic || result?.signals?.PIVOT_CLASSIC;
  const pivotFib     = result?.pivot_fib     || result?.signals?.PIVOT_FIB;

  // MTF results
  const mtfResults = result?.mtf_results || result?.timeframe_results || null;

  return (
    <div className="p-4 md:p-6 space-y-5 pb-24 md:pb-6 max-w-5xl mx-auto">

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
          style={{ background: 'rgba(99,102,241,0.12)', border: '1px solid rgba(99,102,241,0.25)' }}>
          📊
        </div>
        <div className="flex-1">
          <h2 className="text-lg font-display font-black text-[var(--text-primary)] leading-tight">
            Technical Analysis AI
          </h2>
          <p className="text-[9px] text-[var(--text-dim)] uppercase tracking-widest font-bold mt-0.5">
            Indicator Engine · SMC · Pivot Points · Multi-TF → AI
          </p>
        </div>
        <span className="text-[8px] font-black uppercase tracking-wider px-2.5 py-1 rounded-full"
          style={{ background: 'rgba(59,130,246,0.12)', color: '#60a5fa', border: '1px solid rgba(59,130,246,0.25)' }}>
          Essential+
        </span>
      </div>

      {/* ── Data Flow ──────────────────────────────────────────────────────── */}
      <div className="flex flex-wrap items-center gap-1.5 px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
        <span className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-wider shrink-0">Alur:</span>
        {[
          ['MT5 / Binance',     'text-blue-400 bg-blue-400/10'],
          ['OHLC 200 bar',      'text-[var(--text-dim)] bg-[var(--bg-hover)]'],
          ['30+ Indicators',    'text-[var(--text-secondary)] bg-[var(--bg-hover)]'],
          ['Pivot Engine',      'text-yellow-400 bg-yellow-400/10'],
          ['SMC Engine',        'text-purple-400 bg-purple-400/10'],
          ['AI Confluence',     'text-emerald-400 bg-emerald-400/10'],
        ].map(([label, cls], i) => (
          <React.Fragment key={i}>
            <span className={`text-[7px] font-black px-1.5 py-0.5 rounded ${cls}`}>{label}</span>
            {i < 5 && <span className="text-[var(--text-dim)] text-[8px]">→</span>}
          </React.Fragment>
        ))}
      </div>

      {/* ── Config Row ─────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <PairSelector value={pair} onChange={setPair} label="Pair / Aset" />
        <div>
          <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Setup TF (Primary)</p>
          <div className="flex items-center gap-2 px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
            <span className="text-[10px] font-black text-[var(--accent)] font-mono">{primaryTF}</span>
            <span className="text-[8px] text-[var(--text-dim)] font-bold mr-auto">· dari style {style}</span>
            {styleTFs.map(tf => (
              <span key={tf} className="text-[7px] font-black px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-dim)]">{tf}</span>
            ))}
          </div>
        </div>
      </div>

      {/* ── Style Selector ─────────────────────────────────────────────────── */}
      <StyleSelector value={style} onChange={setStyle} showMatrix={true} />

      {/* ── Indicator Selector ─────────────────────────────────────────────── */}
      <div className="space-y-2">
        <div className="flex items-center justify-between mb-1">
          <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">
            Pilih Indikator
          </p>
          <span className="text-[8px] font-black px-2 py-0.5 rounded-full"
            style={{ background: 'rgba(245,166,35,0.12)', color: 'var(--accent)', border: '1px solid rgba(245,166,35,0.2)' }}>
            {selectedIndicators.length} dipilih · {ALL_INDICATORS.length} total
          </span>
        </div>

        {INDICATOR_GROUPS.map(group => {
          const groupSelected = group.items.filter(i => selectedIndicators.includes(i.key));
          const isOpen = openGroups[group.id];
          return (
            <div key={group.id} className="space-y-1.5">
              <div className="flex items-center gap-1">
                <div className="flex-1">
                  <GroupHeader
                    emoji={group.emoji}
                    label={group.label}
                    count={groupSelected.length}
                    total={group.items.length}
                    open={isOpen}
                    onToggle={() => toggleGroup(group.id)}
                  />
                </div>
                <button onClick={() => selectAll(group.id)}
                  className="text-[7px] font-black px-2 py-1 rounded-lg bg-emerald-400/10 text-emerald-400 border border-emerald-400/20 hover:bg-emerald-400/20 transition-all">
                  All
                </button>
                <button onClick={() => deselectAll(group.id)}
                  className="text-[7px] font-black px-2 py-1 rounded-lg bg-red-400/10 text-red-400 border border-red-400/20 hover:bg-red-400/20 transition-all">
                  Clear
                </button>
              </div>
              {isOpen && (
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5 pl-1">
                  {group.items.map(ind => {
                    const active = selectedIndicators.includes(ind.key);
                    return (
                      <button key={ind.key} onClick={() => toggleIndicator(ind.key)}
                        className="flex items-center gap-2 p-2.5 rounded-xl border text-left transition-all hover:scale-[1.02] active:scale-[0.98]"
                        style={active
                          ? { background: `${ind.color}15`, borderColor: `${ind.color}50`, color: ind.color }
                          : { background: 'var(--bg-card)', borderColor: 'var(--border-color)', color: 'var(--text-dim)' }
                        }>
                        <div className="flex-1 min-w-0">
                          <p className="text-[8px] font-black uppercase truncate">{ind.name}</p>
                          <p className="text-[7px] opacity-60 font-bold truncate">{ind.sub}</p>
                        </div>
                        {active && <CheckCircle2 size={10} style={{ color: ind.color, flexShrink: 0 }} />}
                      </button>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* ── Analyze Button ─────────────────────────────────────────────────── */}
      <button onClick={fetchAnalysis} disabled={loading || selectedIndicators.length === 0}
        className="w-full py-3.5 rounded-2xl text-sm font-black transition-all hover:opacity-90 hover:scale-[1.01] disabled:opacity-50 active:scale-[0.99] flex items-center justify-center gap-2"
        style={{ background: 'var(--accent)', color: '#000' }}>
        {loading
          ? <><RefreshCw size={15} className="animate-spin" /> Menganalisa {style.toUpperCase()} · {styleTFs.join('/')}...</>
          : <><Zap size={15} /> Analisa AI — {pair} · {style} · {selectedIndicators.length} indikator · 3 Kredit</>}
      </button>

      {/* ── RESULTS ────────────────────────────────────────────────────────── */}
      {result && !result.error && (
        <div className="space-y-4 animate-fade-up">

          {/* ── Bias Banner ──────────────────────────────────────────────── */}
          <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
            <div className="relative overflow-hidden p-5 flex items-center gap-4 border-b border-[var(--border-color)]"
              style={isBuy
                ? { borderColor: 'rgba(16,185,129,0.3)', background: 'rgba(16,185,129,0.04)' }
                : isSell
                ? { borderColor: 'rgba(239,68,68,0.3)', background: 'rgba(239,68,68,0.04)' }
                : { borderColor: 'var(--border-color)', background: 'var(--bg-card)' }
              }>
              <div className="absolute inset-0 opacity-5 pointer-events-none"
                style={{ background: isBuy ? 'radial-gradient(circle at left, #10b981, transparent)' : isSell ? 'radial-gradient(circle at left, #ef4444, transparent)' : 'none' }} />
              <div className="relative">
                {isBuy  ? <TrendingUp  size={36} className="text-green-400" />
                 : isSell? <TrendingDown size={36} className="text-red-400"   />
                         : <Activity    size={36} className="text-[var(--text-dim)]" />}
              </div>
              <div className="relative flex-1">
                <p className="text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">AI Bias Signal · {pair}</p>
                <p className={`text-4xl font-black font-mono leading-none ${isBuy ? 'text-green-400' : isSell ? 'text-red-400' : 'text-[var(--text-dim)]'}`}>
                  {bias}
                </p>
                {result.confidence != null && (
                  <p className="text-[10px] text-[var(--text-dim)] mt-1">
                    TA Confidence: <span className="font-mono font-bold text-[var(--text-secondary)]">{result.confidence}%</span>
                  </p>
                )}
              </div>
              {result.setup_type && result.setup_type !== 'Unknown' && (
                <div className="relative shrink-0 flex flex-col items-end gap-1">
                  <span className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-wider">Setup</span>
                  <span className="text-[10px] font-black px-2.5 py-1 rounded-lg bg-purple-400/15 text-purple-400 border border-purple-400/30">
                    {result.setup_type}
                  </span>
                </div>
              )}
            </div>

            {/* Confluence + tags */}
            <div className="px-5 py-4 space-y-3">
              {result.confluence_score != null && <ConfluenceBar score={result.confluence_score} />}
              <div className="flex flex-wrap gap-1.5 pt-1">
                {result.current_price && (
                  <Tag label={`${result.current_price} Live`} color="text-[var(--accent)]" bg="bg-[var(--accent)]/10" border="border-[var(--accent)]/20" icon={Activity} />
                )}
                {result.candle_count && (
                  <Tag label={`${result.candle_count} candles`} color="text-[var(--text-dim)]" bg="bg-[var(--bg-hover)]" border="border-[var(--border-color)]" />
                )}
                {result.smc_available
                  ? <Tag label="SMC Engine ✓" color="text-purple-400" bg="bg-purple-400/10" border="border-purple-400/25" icon={Cpu} />
                  : <Tag label="SMC offline"  color="text-[var(--text-dim)]" bg="bg-[var(--bg-hover)]" border="border-[var(--border-color)]" />
                }
                <Tag label={`Style: ${style}`} color="text-[var(--accent)]" bg="bg-[var(--accent)]/10" border="border-[var(--accent)]/20" />
              </div>
            </div>
          </div>

          {/* ── Summary Gauges (TradingView-style) ───────────────────────── */}
          <div>
            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Signal Summary</p>
            <div className="grid grid-cols-3 gap-2">
              <SummaryGauge label="Moving Avg"  buy={maCount.buy}  neutral={maCount.neutral}  sell={maCount.sell} />
              <SummaryGauge label="Oscillators" buy={oscCount.buy} neutral={oscCount.neutral} sell={oscCount.sell} />
              <SummaryGauge label="Overall"     buy={allCount.buy} neutral={allCount.neutral} sell={allCount.sell} />
            </div>
          </div>

          {/* ── Multi-TF Breakdown ──────────────────────────────────────── */}
          {mtfResults && Object.keys(mtfResults).length > 0 && (
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-[var(--border-color)] flex items-center gap-2"
                style={{ background: 'rgba(245,166,35,0.03)' }}>
                <BarChart2 size={12} className="text-[var(--accent)]" />
                <span className="text-[9px] font-black text-[var(--accent)] uppercase tracking-wider">Multi-Timeframe Breakdown</span>
              </div>
              <div className="p-4 grid grid-cols-2 sm:grid-cols-4 gap-2">
                {Object.entries(mtfResults).map(([tf, data]) => {
                  const tfBias = data?.bias || data?.signal || 'NEUTRAL';
                  const isB = SIGNAL_BUY.has(tfBias.toUpperCase());
                  const isS = SIGNAL_SELL.has(tfBias.toUpperCase());
                  return (
                    <div key={tf} className="rounded-xl p-3 border text-center"
                      style={isB ? { background:'rgba(16,185,129,0.06)', borderColor:'rgba(16,185,129,0.3)' }
                            : isS ? { background:'rgba(239,68,68,0.06)',  borderColor:'rgba(239,68,68,0.3)'  }
                            : { background:'var(--bg-panel)', borderColor:'var(--border-color)' }}>
                      <p className="text-[8px] font-black text-[var(--text-dim)] uppercase mb-1">{tf}</p>
                      <p className={`text-[11px] font-black font-mono ${isB ? 'text-emerald-400' : isS ? 'text-red-400' : 'text-[var(--text-dim)]'}`}>
                        {tfBias}
                      </p>
                      {data?.confluence != null && (
                        <p className="text-[7px] text-[var(--text-dim)] mt-0.5 font-mono">{data.confluence}%</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Moving Averages Table ─────────────────────────────────────── */}
          {Object.keys(maSigs).length > 0 && (
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-[var(--border-color)] flex items-center gap-2"
                style={{ background: 'rgba(245,166,35,0.03)' }}>
                <span className="text-sm">📈</span>
                <span className="text-[9px] font-black text-[var(--text-secondary)] uppercase tracking-wider flex-1">Moving Averages</span>
                <span className={`text-[8px] font-black px-2 py-0.5 rounded font-mono ${
                  maCount.buy > maCount.sell ? 'text-emerald-400 bg-emerald-400/10' :
                  maCount.sell > maCount.buy ? 'text-red-400 bg-red-400/10' :
                  'text-[var(--text-dim)] bg-[var(--bg-hover)]'
                }`}>{maCount.buy}B · {maCount.neutral}N · {maCount.sell}S</span>
              </div>
              <div className="p-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5">
                {Object.entries(maSigs).map(([key, val]) => {
                  if (!val || typeof val !== 'object') return null;
                  const sig = val.signal || val.action || '';
                  const meta = ALL_INDICATORS.find(d => d.key === key.toLowerCase());
                  const { bg, border } = sigBg(sig);
                  return (
                    <div key={key} className="rounded-xl p-3 border"
                      style={{ background: bg, borderColor: border }}>
                      <p className="text-[7px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-1">
                        {meta?.name || key}
                      </p>
                      <p className={`text-[10px] font-black font-mono ${sigClass(sig)}`}>{sig || '-'}</p>
                      {val.value !== undefined && (
                        <p className="text-[8px] text-[var(--text-dim)] mt-0.5 font-mono">
                          {typeof val.value === 'number' ? val.value.toFixed(4) : val.value}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Oscillators Table ─────────────────────────────────────────── */}
          {Object.keys(oscSigs).length > 0 && (
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-[var(--border-color)] flex items-center gap-2"
                style={{ background: 'rgba(245,166,35,0.03)' }}>
                <span className="text-sm">📊</span>
                <span className="text-[9px] font-black text-[var(--text-secondary)] uppercase tracking-wider flex-1">Oscillators</span>
                <span className={`text-[8px] font-black px-2 py-0.5 rounded font-mono ${
                  oscCount.buy > oscCount.sell ? 'text-emerald-400 bg-emerald-400/10' :
                  oscCount.sell > oscCount.buy ? 'text-red-400 bg-red-400/10' :
                  'text-[var(--text-dim)] bg-[var(--bg-hover)]'
                }`}>{oscCount.buy}B · {oscCount.neutral}N · {oscCount.sell}S</span>
              </div>
              <div className="p-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-1.5">
                {Object.entries(oscSigs).map(([key, val]) => {
                  if (!val || typeof val !== 'object') return null;
                  const sig = val.signal || val.action || '';
                  const meta = ALL_INDICATORS.find(d => d.key === key.toLowerCase());
                  const { bg, border } = sigBg(sig);
                  return (
                    <div key={key} className="rounded-xl p-3 border"
                      style={{ background: bg, borderColor: border }}>
                      <p className="text-[7px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-1">
                        {meta?.name || key}
                      </p>
                      <p className={`text-[10px] font-black font-mono ${sigClass(sig)}`}>{sig || '-'}</p>
                      {val.value !== undefined && (
                        <p className="text-[8px] text-[var(--text-dim)] mt-0.5 font-mono">
                          {typeof val.value === 'number' ? val.value.toFixed(2) : val.value}
                        </p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* ── Pivot Points ──────────────────────────────────────────────── */}
          {(pivotClassic || pivotFib) && (
            <div className="bg-[var(--bg-card)] border border-yellow-400/20 rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-yellow-400/15 flex items-center gap-2"
                style={{ background: 'rgba(245,166,35,0.04)' }}>
                <span className="text-sm">🎯</span>
                <span className="text-[9px] font-black text-yellow-400 uppercase tracking-wider">Pivot Points</span>
                <span className="ml-auto text-[8px] font-black text-[var(--text-dim)]">Support · Resistance</span>
              </div>
              <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                {pivotClassic && (
                  <div className="space-y-1.5">
                    <p className="text-[8px] font-black uppercase tracking-wider text-yellow-400 mb-2">Classic Pivots</p>
                    {['R3','R2','R1','Pivot','S1','S2','S3'].map(k => (
                      <PivotRow key={k} label={k} value={pivotClassic[k.toLowerCase()] ?? pivotClassic[k]} />
                    ))}
                  </div>
                )}
                {pivotFib && (
                  <div className="space-y-1.5">
                    <p className="text-[8px] font-black uppercase tracking-wider text-yellow-400 mb-2">Fibonacci Pivots</p>
                    {['R3','R2','R1','Pivot','S1','S2','S3'].map(k => (
                      <PivotRow key={k} label={k} value={pivotFib[k.toLowerCase()] ?? pivotFib[k]} />
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── SMC Engine ───────────────────────────────────────────────── */}
          {hasSMC && (
            <div className="bg-[var(--bg-card)] border border-purple-400/20 rounded-2xl overflow-hidden">
              <div className="px-5 py-3 border-b border-purple-400/15 flex items-center gap-2"
                style={{ background: 'rgba(168,85,247,0.04)' }}>
                <Cpu size={12} className="text-purple-400" />
                <span className="text-[9px] font-black text-purple-400 uppercase tracking-wider">Smart Money Concept (SMC Engine)</span>
                <span className="ml-auto text-[8px] font-black px-2 py-0.5 rounded bg-purple-400/10 text-purple-400 border border-purple-400/20">
                  Score {smc.smc_score || 0}/100
                </span>
              </div>
              <div className="p-4 space-y-3">
                <div className="flex flex-wrap gap-2">
                  {smc.bias && (
                    <div className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border ${
                      smc.bias === 'BULLISH' ? 'bg-emerald-400/10 border-emerald-400/25 text-emerald-400'
                      : smc.bias === 'BEARISH' ? 'bg-red-400/10 border-red-400/25 text-red-400'
                      : 'bg-[var(--bg-panel)] border-[var(--border-color)] text-[var(--text-dim)]'
                    }`}>
                      {smc.bias === 'BULLISH' ? <TrendingUp size={11} /> : smc.bias === 'BEARISH' ? <TrendingDown size={11} /> : <Activity size={11} />}
                      <span className="text-[9px] font-black uppercase">{smc.bias} Bias</span>
                    </div>
                  )}
                  {smc.bos && (
                    <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border bg-emerald-400/10 border-emerald-400/25">
                      <CheckCircle2 size={10} className="text-emerald-400" />
                      <span className="text-[9px] font-black text-emerald-400">BOS Detected</span>
                    </div>
                  )}
                  {smc.choch && (
                    <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border bg-orange-400/10 border-orange-400/25">
                      <AlertTriangle size={10} className="text-orange-400" />
                      <span className="text-[9px] font-black text-orange-400">CHoCH Detected</span>
                    </div>
                  )}
                  {smc.ote_zone && (
                    <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border bg-yellow-400/10 border-yellow-400/25">
                      <Crosshair size={10} className="text-yellow-400" />
                      <span className="text-[9px] font-black text-yellow-400">OTE Zone {smc.ote_type}</span>
                    </div>
                  )}
                  {smc.kill_zone && (
                    <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border bg-red-400/10 border-red-400/25">
                      <Clock size={10} className="text-red-400" />
                      <span className="text-[9px] font-black text-red-400">Kill Zone Active</span>
                    </div>
                  )}
                  {smc.amd_phase && (
                    <div className="flex items-center gap-1.5 px-3 py-2 rounded-xl border bg-[var(--bg-panel)] border-[var(--border-color)]">
                      <Cpu size={10} className="text-[var(--accent)]" />
                      <span className="text-[7px] font-black text-[var(--text-dim)] uppercase">AMD</span>
                      <span className="text-[9px] font-black text-[var(--accent)]">{smc.amd_phase}</span>
                    </div>
                  )}
                </div>

                <div className="grid grid-cols-3 sm:grid-cols-5 gap-2">
                  {[
                    { label: 'Order Blocks', value: smc.order_blocks?.length || 0, suffix: ' OB' },
                    { label: 'FVG Count',    value: smc.fvg_count ?? '-', suffix: '' },
                    { label: 'Liq Pools',    value: smc.liquidity_pools ?? '-', suffix: '' },
                    { label: 'SMC Signal',   value: smc.smc_action || 'WAIT', isText: true },
                    { label: 'Session',      value: smc.session || '-', isText: true },
                  ].map((item, i) => (
                    <div key={i} className="bg-[var(--bg-panel)] rounded-xl p-2.5 text-center border border-[var(--border-color)]">
                      <p className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-wider mb-1">{item.label}</p>
                      <p className={`text-[11px] font-black font-mono ${
                        item.isText
                          ? item.value === 'BUY' ? 'text-emerald-400'
                          : item.value === 'SELL' ? 'text-red-400'
                          : 'text-[var(--accent)]'
                          : 'text-[var(--text-primary)]'
                      }`}>{item.value}{item.suffix || ''}</p>
                    </div>
                  ))}
                </div>

                {(smc.smc_entry || smc.smc_sl || smc.smc_tp) && (
                  <div className="grid grid-cols-3 gap-2 pt-1">
                    {[
                      { label: 'SMC Entry', value: smc.smc_entry, cls: 'text-[var(--text-primary)]' },
                      { label: 'SMC SL',    value: smc.smc_sl,    cls: 'text-red-400' },
                      { label: 'SMC TP',    value: smc.smc_tp,    cls: 'text-emerald-400' },
                    ].map((f, i) => f.value && (
                      <div key={i} className="bg-[var(--bg-panel)] rounded-lg p-2 border border-[var(--border-color)]">
                        <p className="text-[7px] font-black text-[var(--text-dim)] uppercase">{f.label}</p>
                        <p className={`text-[10px] font-black font-mono ${f.cls}`}>
                          {typeof f.value === 'number' ? f.value.toFixed(2) : f.value}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* ── AI Interpretation ─────────────────────────────────────────── */}
          {(result.ai_interpretation || result.summary) && (
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
              <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">
                🤖 Analisa AI — Confluence Logic
              </p>
              <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                {result.ai_interpretation || result.summary}
              </p>
            </div>
          )}

          {/* ── Remaining signals (Trend/Vol/Other) ───────────────────────── */}
          {(() => {
            const extra = Object.entries(signals).filter(([k]) =>
              k !== 'SMC' &&
              !k.startsWith('PIVOT') &&
              !maKeys.has(k) &&
              !oscKeys.has(k)
            );
            if (!extra.length) return null;
            return (
              <div>
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Trend & Volatility Indicators</p>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                  {extra.map(([key, val]) => {
                    if (!val || typeof val !== 'object') return null;
                    const sig = val.signal || val.action || '';
                    const meta = ALL_INDICATORS.find(d => d.key === key.toLowerCase());
                    const { bg, border } = sigBg(sig);
                    return (
                      <div key={key} className="rounded-xl p-3 border"
                        style={{ background: bg, borderColor: border }}>
                        <p className="text-[7px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-1">
                          {meta?.name || key}
                        </p>
                        <p className={`text-[11px] font-black font-mono ${sigClass(sig)}`}>{sig || '-'}</p>
                        {val.value !== undefined && (
                          <p className="text-[8px] text-[var(--text-dim)] mt-0.5 font-mono">
                            {typeof val.value === 'number' ? val.value.toFixed(2) : val.value}
                          </p>
                        )}
                        {val.atr !== undefined && (
                          <p className="text-[7px] text-[var(--text-dim)] font-mono">ATR: {typeof val.atr === 'number' ? val.atr.toFixed(4) : val.atr}</p>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}
        </div>
      )}

      {/* ── Error ────────────────────────────────────────────────────────────── */}
      {result?.error && (
        <div className="rounded-xl p-4 border animate-fade-up"
          style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.25)' }}>
          <p className="text-xs font-black text-red-400 mb-1">⚠️ Gagal Memuat Analisa</p>
          <p className="text-[10px] text-red-400/70">{result.message}</p>
          <p className="text-[9px] text-[var(--text-dim)] mt-2">
            Pastikan EA MT5 aktif dan mengirim data ke gas-mt5-websocket
          </p>
        </div>
      )}
    </div>
  );
}
