import React, { useState, useMemo } from 'react';
import { Zap, BarChart3, Target, TrendingUp, TrendingDown, Minus, Eye } from 'lucide-react';
import TradingViewWidget from './TradingViewWidget';

// ─────────────────────────────────────────────────────────
// Config: order types & trading styles
// ─────────────────────────────────────────────────────────
const ORDER_TYPES = ['WAIT', 'SEE', 'BUY NOW', 'SELL NOW', 'BUY LIMIT', 'SELL LIMIT', 'BUY STOP', 'SELL STOP'];
const STYLES = ['SCALPING', 'INTRADAY', 'SWING'];

const ORDER_META = {
  'WAIT': { color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/30', icon: Minus },
  'SEE': { color: 'text-blue-400', bg: 'bg-blue-400/10', border: 'border-blue-400/30', icon: Eye },
  'BUY NOW': { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/30', icon: Zap },
  'SELL NOW': { color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/30', icon: Zap },
  'BUY LIMIT': { color: 'text-emerald-300', bg: 'bg-emerald-400/8', border: 'border-emerald-400/20', icon: TrendingUp },
  'SELL LIMIT': { color: 'text-red-300', bg: 'bg-red-400/8', border: 'border-red-400/20', icon: TrendingDown },
  'BUY STOP': { color: 'text-cyan-400', bg: 'bg-cyan-400/10', border: 'border-cyan-400/30', icon: TrendingUp },
  'SELL STOP': { color: 'text-orange-400', bg: 'bg-orange-400/10', border: 'border-orange-400/30', icon: TrendingDown },
};

const STYLE_META = {
  'SCALPING': { color: 'text-purple-400', bg: 'bg-purple-400/10', label: 'SCP' },
  'INTRADAY': { color: 'text-amber-400', bg: 'bg-amber-400/10', label: 'INT' },
  'SWING': { color: 'text-indigo-400', bg: 'bg-indigo-400/10', label: 'SWG' },
};

// ─────────────────────────────────────────────────────────
// Deterministic signal generator per pair
// Changes every 5 minutes so it feels "live"
// ─────────────────────────────────────────────────────────
function seedRand(seed) {
  let s = seed;
  return () => {
    s = (s * 1664525 + 1013904223) & 0xffffffff;
    return (s >>> 0) / 0xffffffff;
  };
}

function generatePairSignal(pair, currentPrice) {
  const slot = Math.floor(Date.now() / 300000); // 5-min slot
  const seed = [...(pair.symbol + slot)].reduce((a, c) => a + c.charCodeAt(0), 0);
  const rand = seedRand(seed);

  const price = currentPrice || pair.base;
  const isForex = pair.type === 'Forex';
  const prec = isForex ? 5 : 2;

  // Probability distribution: WAIT/SEE more common than immediate signals
  const roll = rand();
  let orderType;
  if (roll < 0.18) orderType = 'WAIT';
  else if (roll < 0.30) orderType = 'SEE';
  else if (roll < 0.42) orderType = 'BUY NOW';
  else if (roll < 0.54) orderType = 'SELL NOW';
  else if (roll < 0.64) orderType = 'BUY LIMIT';
  else if (roll < 0.74) orderType = 'SELL LIMIT';
  else if (roll < 0.84) orderType = 'BUY STOP';
  else orderType = 'SELL STOP';

  // Style
  const styleRoll = rand();
  const style = styleRoll < 0.4 ? 'SCALPING' : styleRoll < 0.75 ? 'INTRADAY' : 'SWING';

  // ATR estimate
  const atr = price * (isForex ? 0.0008 : 0.008);

  // Compute levels
  const isBuy = orderType.includes('BUY');
  const isSell = orderType.includes('SELL');
  const isNow = orderType.endsWith('NOW');
  const isLimit = orderType.endsWith('LIMIT');
  const isStop = orderType.endsWith('STOP');

  let entry, sl, tp1, tp2;

  if (isNow) {
    entry = price;
  } else if (isLimit) {
    entry = isBuy
      ? +(price - atr * (0.5 + rand() * 0.5)).toFixed(prec)
      : +(price + atr * (0.5 + rand() * 0.5)).toFixed(prec);
  } else if (isStop) {
    entry = isBuy
      ? +(price + atr * (0.5 + rand() * 0.5)).toFixed(prec)
      : +(price - atr * (0.5 + rand() * 0.5)).toFixed(prec);
  } else {
    entry = 0;
  }

  const hasLevels = entry > 0;
  if (hasLevels) {
    const rrMultiplier = style === 'SCALPING' ? 1.5 : style === 'INTRADAY' ? 2.5 : 4.0;
    const slDist = atr * (0.8 + rand() * 0.5);
    const tpDist = slDist * rrMultiplier;

    if (isBuy) {
      sl = +(entry - slDist).toFixed(prec);
      tp1 = +(entry + tpDist * 0.6).toFixed(prec);
      tp2 = +(entry + tpDist).toFixed(prec);
    } else {
      sl = +(entry + slDist).toFixed(prec);
      tp1 = +(entry - tpDist * 0.6).toFixed(prec);
      tp2 = +(entry - tpDist).toFixed(prec);
    }
  }

  const rr = style === 'SCALPING' ? '1:1.5' : style === 'INTRADAY' ? '1:2.5' : '1:4.0';
  const conf = Math.floor(45 + rand() * 50);
  const grade = conf >= 80 ? 'A+' : conf >= 70 ? 'A' : conf >= 60 ? 'B+' : 'B';

  return { orderType, style, entry, sl, tp1, tp2, rr, conf, grade, hasLevels };
}

// ─────────────────────────────────────────────────────────
// Mini signal card (per-pair grid)
// ─────────────────────────────────────────────────────────
function PairSignalCard({ pair, currentPrice, onClick, isActive }) {
  const sig = useMemo(() => generatePairSignal(pair, currentPrice), [pair.symbol, currentPrice]);
  const meta = ORDER_META[sig.orderType] || ORDER_META['WAIT'];
  const smeta = STYLE_META[sig.style];
  const Icon = meta.icon;
  const prec = pair.type === 'Forex' ? 5 : 2;
  const price = currentPrice || pair.base;
  const chg = ((price - pair.base) / pair.base * 100);
  const isUp = chg >= 0;
  const isActionable = !['WAIT', 'SEE'].includes(sig.orderType);
  const isBuy = sig.orderType.includes('BUY');

  return (
    <button
      onClick={() => onClick(pair.symbol)}
      className={`w-full text-left bg-[var(--bg-card)] border rounded-xl p-4 transition-all hover:scale-[1.01] hover:shadow-lg ${isActive
        ? 'border-[var(--accent)]/50 ring-1 ring-[var(--accent)]/20 shadow-[0_0_20px_rgba(250,204,21,0.08)]'
        : 'border-[var(--border-color)] hover:border-[var(--text-dim)]/50'
        }`}
    >
      {/* Row 1: pair name + price */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-black text-[var(--text-primary)] tracking-tight">{pair.symbol}</span>
            {isActive && <span className="text-[8px] px-1.5 py-0.5 bg-[var(--accent)]/15 text-[var(--accent)] rounded font-black uppercase">Active</span>}
          </div>
          <span className="text-[9px] text-[var(--text-dim)] font-bold">{pair.name}</span>
        </div>
        <div className="text-right">
          <div className={`text-sm font-mono font-black ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {price.toFixed(prec)}
          </div>
          <div className={`text-[9px] font-bold font-mono ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
            {isUp ? '+' : ''}{chg.toFixed(2)}%
          </div>
        </div>
      </div>

      {/* Row 2: order type badge + style badge */}
      <div className="flex items-center gap-2 mb-3">
        <span className={`flex items-center gap-1.5 text-[10px] font-black px-2.5 py-1.5 rounded-lg border uppercase tracking-wide ${meta.color} ${meta.bg} ${meta.border}`}>
          <Icon size={10} className={isActionable ? 'animate-pulse' : ''} />
          {sig.orderType}
        </span>
        <span className={`text-[9px] font-black px-2 py-1.5 rounded-lg uppercase tracking-wider ${smeta.color} ${smeta.bg}`}>
          {smeta.label}
        </span>
        <span className="ml-auto text-[9px] font-black text-[var(--text-dim)] uppercase">{sig.grade}</span>
      </div>

      {/* Row 3: levels (if actionable) */}
      {isActionable && sig.hasLevels ? (
        <div className="grid grid-cols-4 gap-1.5">
          {[
            { l: 'Entry', v: sig.entry },
            { l: 'SL', v: sig.sl, danger: true },
            { l: 'TP1', v: sig.tp1, ok: true },
            { l: 'TP2', v: sig.tp2, ok: true, highlight: true },
          ].map(({ l, v, danger, ok, highlight }) => (
            <div key={l} className={`rounded-lg p-1.5 text-center ${highlight ? 'bg-[var(--accent)]/8 border border-[var(--accent)]/20' : 'bg-[var(--bg-panel)]'}`}>
              <div className="text-[7px] font-bold text-[var(--text-dim)] uppercase mb-0.5">{l}</div>
              <div className={`text-[9px] font-mono font-black leading-tight ${danger ? 'text-[var(--danger)]' : ok ? 'text-[var(--success)]' : 'text-[var(--text-primary)]'
                }`}>{v}</div>
            </div>
          ))}
        </div>
      ) : (
        <div className="flex items-center justify-between">
          <div className={`text-[9px] font-bold ${meta.color}`}>
            {sig.orderType === 'WAIT' ? 'Menunggu setup valid...' : 'Observasi pergerakan harga'}
          </div>
          {/* Confidence mini bar */}
          <div className="flex items-center gap-1.5">
            <div className="w-16 h-1.5 bg-[var(--bg-hover)] rounded-full overflow-hidden">
              <div
                className={`h-full rounded-full ${sig.conf >= 70 ? 'bg-[var(--success)]' : sig.conf >= 55 ? 'bg-yellow-400' : 'bg-[var(--text-dim)]'}`}
                style={{ width: `${sig.conf}%` }}
              />
            </div>
            <span className="text-[8px] font-bold text-[var(--text-dim)]">{sig.conf}%</span>
          </div>
        </div>
      )}

      {/* Row 4: bottom meta */}
      {isActionable && sig.hasLevels && (
        <div className="flex items-center justify-between mt-2.5 pt-2.5 border-t border-[var(--border-color)]">
          <div className="flex items-center gap-1.5">
            <div className={`w-1.5 h-1.5 rounded-full ${isActionable ? 'bg-[var(--success)] animate-pulse' : 'bg-[var(--text-dim)]'}`} />
            <span className="text-[8px] font-bold text-[var(--text-dim)] uppercase">{sig.style}</span>
          </div>
          <span className="text-[8px] font-mono font-black text-[var(--accent)]">RR {sig.rr}</span>
        </div>
      )}
    </button>
  );
}

// ─────────────────────────────────────────────────────────
// Style filter tab
// ─────────────────────────────────────────────────────────
function StyleTab({ active, label, color, bg, onClick }) {
  return (
    <button
      onClick={onClick}
      className={`text-[9px] font-black px-3 py-1.5 rounded-lg uppercase tracking-widest transition-all ${active ? `${bg} ${color} ring-1 ring-current/30` : 'text-[var(--text-dim)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
        }`}
    >
      {label}
    </button>
  );
}

// ─────────────────────────────────────────────────────────
// Main SignalView
// ─────────────────────────────────────────────────────────
export default function SignalView({ signal, isNew, timer, chartPair, prices, onSelect, activePair, pairs, macroData, aiAnalysis, theme }) {
  const [timeframe, setTimeframe] = useState('15m');
  const [styleFilter, setStyleFilter] = useState('ALL');
  const [typeFilter, setTypeFilter] = useState('ALL');

  const pairData = pairs.find(p => p.symbol === chartPair.symbol) || chartPair;
  const curPrice = prices[chartPair.symbol] || pairData.base;

  // Active pair's deterministic signal (used when no real signal)
  const activeSig = useMemo(
    () => generatePairSignal(pairData, curPrice),
    [pairData.symbol, curPrice]
  );

  // Merge real API signal with generated signal
  const displaySignal = signal || {
    pair: chartPair.symbol,
    type: activeSig.orderType.includes('BUY') ? 'BUY' : activeSig.orderType.includes('SELL') ? 'SELL' : 'WAIT',
    orderType: activeSig.orderType,
    style: activeSig.style,
    grade: activeSig.grade,
    level: activeSig.orderType,
    entry: activeSig.entry || curPrice,
    sl: activeSig.sl || curPrice,
    tp1: activeSig.tp1 || curPrice,
    tp2: activeSig.tp2 || curPrice,
    confidence: activeSig.conf,
    rr: activeSig.rr,
    timestamp: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
  };

  const orderType = displaySignal.orderType || displaySignal.level || 'WAIT';
  const tradingStyle = displaySignal.style || activeSig.style;
  const isBuy = displaySignal.type === 'BUY' || orderType.includes('BUY');
  const isActionable = !['WAIT', 'SEE'].includes(orderType);
  const orderMeta = ORDER_META[orderType] || ORDER_META['WAIT'];
  const styleMeta = STYLE_META[tradingStyle] || STYLE_META['INTRADAY'];

  // Filter pairs for grid
  const filteredPairs = useMemo(() => {
    if (styleFilter === 'ALL' && typeFilter === 'ALL') return pairs;
    return pairs.filter(p => {
      const sig = generatePairSignal(p, prices[p.symbol] || p.base);
      const styleOk = styleFilter === 'ALL' || sig.style === styleFilter;
      const typeGroup = typeFilter === 'ALL' ? true
        : typeFilter === 'BUY' ? sig.orderType.includes('BUY')
          : typeFilter === 'SELL' ? sig.orderType.includes('SELL')
            : typeFilter === 'WAIT' ? ['WAIT', 'SEE'].includes(sig.orderType)
              : true;
      return styleOk && typeGroup;
    });
  }, [pairs, prices, styleFilter, typeFilter]);

  return (
    <div className="p-4 md:p-6 space-y-5 pb-24 md:pb-6">

      {/* ── Chart Panel ─────────────────────────────────── */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden shadow-[var(--card-shadow)] flex flex-col h-[700px]">
        {/* Chart header */}
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[var(--border-color)] bg-[var(--bg-panel)]/50 shrink-0">
          <div className="flex items-center gap-4">
            <div className="flex flex-col">
              <div className="flex items-center gap-2">
                <span className="text-sm font-black text-[var(--text-primary)] uppercase tracking-tighter">{chartPair.symbol}</span>
                <span className="text-[9px] px-1.5 py-0.5 bg-[var(--bg-hover)] text-[var(--text-dim)] rounded font-bold">CFD</span>
                {/* signal badge in chart header */}
                <span className={`text-[9px] px-2 py-0.5 rounded-md font-black uppercase tracking-wider ${orderMeta.color} ${orderMeta.bg} border ${orderMeta.border}`}>
                  {orderType}
                </span>
              </div>
              <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase tracking-widest">{chartPair.name}</span>
            </div>
            <div className="h-7 w-px bg-[var(--border-color)]" />
            <div className="flex flex-col">
              <span className={`text-xl font-mono font-black ${isUpFromBase(prices, chartPair) ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                {curPrice.toFixed(pairData.type === 'Forex' ? 4 : 2)}
              </span>
              <div className="flex items-center gap-1 opacity-70">
                <BarChart3 size={9} className="text-[var(--text-dim)]" />
                <span className="text-[8px] font-bold text-[var(--text-dim)] uppercase">Real-time</span>
              </div>
            </div>
          </div>
          {/* Timeframe switcher */}
          <div className="hidden sm:flex items-center gap-1 bg-[var(--bg-panel)] p-1 rounded-lg border border-[var(--border-color)]">
            {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
              <button
                key={tf}
                onClick={() => setTimeframe(tf)}
                className={`text-[9px] px-2.5 py-1.5 rounded-md transition-all font-black uppercase ${tf === timeframe
                  ? 'bg-[var(--accent)] text-black shadow-sm'
                  : 'text-[var(--text-dim)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'
                  }`}
              >
                {tf}
              </button>
            ))}
          </div>
        </div>
        {/* Chart body */}
        <div className="flex-1">
          <TradingViewWidget pair={chartPair} theme={theme} />
        </div>
      </div>

      {/* ── All Pairs Signal Dashboard ───────────────────── */}
      <div>
        {/* Section header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Target size={16} className="text-[var(--accent)]" />
            <h3 className="text-sm font-black text-[var(--text-primary)] uppercase tracking-wider">Signal Semua Pair</h3>
            <span className="text-[9px] px-2 py-1 bg-[var(--accent)]/10 text-[var(--accent)] rounded-md font-black">
              {filteredPairs.length} PAIR
            </span>
          </div>
          {/* Live indicator */}
          <div className="flex items-center gap-1.5">
            <div className="w-1.5 h-1.5 bg-[var(--success)] rounded-full animate-pulse" />
            <span className="text-[9px] font-bold text-[var(--text-dim)] uppercase">Auto Refresh 5m</span>
          </div>
        </div>

        {/* Filter bar */}
        <div className="flex flex-wrap gap-2 mb-4">
          {/* Style filters */}
          <div className="flex items-center gap-1.5 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1.5">
            <span className="text-[8px] font-black text-[var(--text-dim)] uppercase px-1.5">Style</span>
            {['ALL', 'SCALPING', 'INTRADAY', 'SWING'].map(s => (
              <StyleTab
                key={s}
                active={styleFilter === s}
                label={s === 'ALL' ? 'All' : STYLE_META[s]?.label || s}
                color={s === 'ALL' ? 'text-[var(--text-primary)]' : STYLE_META[s]?.color || ''}
                bg={s === 'ALL' ? 'bg-[var(--bg-hover)]' : STYLE_META[s]?.bg || ''}
                onClick={() => setStyleFilter(s)}
              />
            ))}
          </div>
          {/* Type filters */}
          <div className="flex items-center gap-1.5 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1.5">
            <span className="text-[8px] font-black text-[var(--text-dim)] uppercase px-1.5">Arah</span>
            {[
              { key: 'ALL', label: 'All', color: 'text-[var(--text-primary)]', bg: 'bg-[var(--bg-hover)]' },
              { key: 'BUY', label: 'Buy', color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
              { key: 'SELL', label: 'Sell', color: 'text-red-400', bg: 'bg-red-400/10' },
              { key: 'WAIT', label: 'Wait', color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
            ].map(({ key, label, color, bg }) => (
              <StyleTab key={key} active={typeFilter === key} label={label} color={color} bg={bg} onClick={() => setTypeFilter(key)} />
            ))}
          </div>
        </div>

        {/* Signal grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-3">
          {filteredPairs.map(p => (
            <PairSignalCard
              key={p.symbol}
              pair={p}
              currentPrice={prices[p.symbol]}
              onClick={onSelect}
              isActive={p.symbol === activePair}
            />
          ))}
        </div>

        {filteredPairs.length === 0 && (
          <div className="text-center py-12 text-[var(--text-dim)]">
            <Target size={32} className="mx-auto mb-3 opacity-30" />
            <p className="text-sm font-bold">Tidak ada pair yang cocok dengan filter ini</p>
          </div>
        )}
      </div>
    </div>
  );
}

function isUpFromBase(prices, pair) {
  const cur = prices[pair.symbol] || pair.base;
  return cur >= pair.base;
}
