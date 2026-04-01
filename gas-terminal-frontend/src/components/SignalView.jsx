import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Zap, Target, TrendingUp, TrendingDown, Minus,
  RefreshCw, ScanLine, Brain, Shield, AlertTriangle,
  Crosshair, BookOpen, Activity, Clock, Lock,
  Cpu, Sparkles, BarChart3, Search, ChevronDown,
} from 'lucide-react';
import TradingViewWidget from './TradingViewWidget';
import { callAIFeature } from '../services/api';
import StyleSelector, { STYLE_MATRIX } from './StyleSelector';

// ── Pair Emoji Map ─────────────────────────────────────────────────────────────
const PAIR_EMOJI = {
  // Forex Majors
  'EURUSD':'🇪🇺', 'GBPUSD':'🇬🇧', 'USDJPY':'🇯🇵', 'USDCHF':'🇨🇭',
  'AUDUSD':'🇦🇺', 'NZDUSD':'🇳🇿', 'USDCAD':'🇨🇦',
  // Forex Crosses
  'GBPJPY':'🏯', 'EURJPY':'⛩️', 'EURGBP':'🇪🇺', 'CADJPY':'🍁',
  'AUDJPY':'🦘', 'GBPCHF':'🏔️', 'EURCHF':'🏔️', 'AUDCAD':'🌊',
  // Metals & Commodities
  'XAUUSD':'🥇', 'XAGUSD':'🥈', 'XPTUSD':'⚪', 'USOIL':'🛢️',
  'UKOIL':'🛢️', 'NGAS':'🔥',
  // Indices
  'US30':'🏛️', 'NAS100':'💻', 'US500':'📊', 'UK100':'🎡',
  'GER40':'🇩🇪', 'JPN225':'🗾', 'AUS200':'🦘', 'STOXX50':'🇪🇺',
  // Crypto
  'BTC/USDT':'₿', 'ETH/USDT':'💎', 'BNB/USDT':'🔶', 'SOL/USDT':'☀️',
  'XRP/USDT':'🌊', 'ADA/USDT':'🔵', 'AVAX/USDT':'🔺', 'DOGE/USDT':'🐕',
  'LINK/USDT':'🔗', 'DOT/USDT':'⚫', 'MATIC/USDT':'🔷', 'LTC/USDT':'🪙',
  'SHIB/USDT':'🐶', 'TRX/USDT':'⚡', 'TON/USDT':'💫', 'ARB/USDT':'🌐',
  'OP/USDT':'🔴', 'APT/USDT':'🔮', 'SUI/USDT':'💠', 'INJ/USDT':'💉',
  'FET/USDT':'🤖', 'RNDR/USDT':'🎨', 'WLD/USDT':'🌍', 'PEPE/USDT':'🐸',
};

// Custom SVG icons per pair (file must be in /public/)
const PAIR_SVG = {
  'GBPUSD': '/GBPUSD_bg.svg',
  'USDJPY': '/usdjpy.svg',
};

export function getPairEmoji(symbol) {
  return PAIR_EMOJI[symbol] || (symbol?.includes('/') ? '🪙' : '💱');
}

export function PairIcon({ symbol, size = 20, className = '' }) {
  const svg = PAIR_SVG[symbol];
  if (svg) {
    return <img src={svg} alt={symbol} width={size} height={size} className={`inline-block object-contain ${className}`} />;
  }
  return <span className={className}>{getPairEmoji(symbol)}</span>;
}

// ── Scannable pairs list ───────────────────────────────────────────────────────
const SCAN_PAIRS = [
  // Forex & Commodities
  { symbol:'XAUUSD', name:'Gold', type:'Commodity' },
  { symbol:'EURUSD', name:'Euro / Dollar', type:'Forex' },
  { symbol:'GBPUSD', name:'Pound / Dollar', type:'Forex' },
  { symbol:'USDJPY', name:'Dollar / Yen', type:'Forex' },
  { symbol:'GBPJPY', name:'Pound / Yen', type:'Forex' },
  { symbol:'XAGUSD', name:'Silver', type:'Commodity' },
  { symbol:'AUDUSD', name:'Aussie / Dollar', type:'Forex' },
  { symbol:'USDCAD', name:'Dollar / CAD', type:'Forex' },
  { symbol:'NZDUSD', name:'NZD / Dollar', type:'Forex' },
  { symbol:'USDCHF', name:'Dollar / CHF', type:'Forex' },
  { symbol:'EURJPY', name:'Euro / Yen', type:'Forex' },
  { symbol:'EURGBP', name:'Euro / Pound', type:'Forex' },
  { symbol:'US30', name:'Dow Jones', type:'Index' },
  { symbol:'NAS100', name:'Nasdaq 100', type:'Index' },
  { symbol:'US500', name:'S&P 500', type:'Index' },
  // Crypto
  { symbol:'BTC/USDT', name:'Bitcoin', type:'Crypto' },
  { symbol:'ETH/USDT', name:'Ethereum', type:'Crypto' },
  { symbol:'SOL/USDT', name:'Solana', type:'Crypto' },
  { symbol:'BNB/USDT', name:'BNB', type:'Crypto' },
  { symbol:'XRP/USDT', name:'Ripple', type:'Crypto' },
  { symbol:'ADA/USDT', name:'Cardano', type:'Crypto' },
  { symbol:'AVAX/USDT', name:'Avalanche', type:'Crypto' },
  { symbol:'DOGE/USDT', name:'Dogecoin', type:'Crypto' },
  { symbol:'LINK/USDT', name:'Chainlink', type:'Crypto' },
  { symbol:'DOT/USDT', name:'Polkadot', type:'Crypto' },
  { symbol:'ARB/USDT', name:'Arbitrum', type:'Crypto' },
  { symbol:'OP/USDT', name:'Optimism', type:'Crypto' },
  { symbol:'INJ/USDT', name:'Injective', type:'Crypto' },
];

const TYPE_COLOR = {
  Forex:'text-blue-400 bg-blue-400/10',
  Commodity:'text-yellow-400 bg-yellow-400/10',
  Index:'text-purple-400 bg-purple-400/10',
  Crypto:'text-emerald-400 bg-emerald-400/10',
};

// ── Model tiers ────────────────────────────────────────────────────────────────
// Model tiers — synced with plan spec update18fiture_v1.01.md
const MODEL_TIERS = [
  { id:'basic',    label:'GAS Basic',    sub:'DeepSeek V3 · 1cr',        badge:'V3',    minPlan:'essential', sigCr:1,  scanCr:5,
    accent:'text-blue-400',   bg:'bg-blue-400/10',   border:'border-blue-400/30',   icon:Cpu },
  { id:'advanced', label:'GAS Advanced', sub:'Gemini Flash 1.5 · 2cr',   badge:'FLASH', minPlan:'plus',      sigCr:2,  scanCr:8,
    accent:'text-purple-400', bg:'bg-purple-400/10', border:'border-purple-400/30', icon:Brain },
  { id:'pro',      label:'GAS Pro',      sub:'Claude Haiku 4.5 · 3cr',   badge:'HAIKU', minPlan:'premium',   sigCr:3,  scanCr:12,
    accent:'text-emerald-400',bg:'bg-emerald-400/10',border:'border-emerald-400/30',icon:Sparkles },
  { id:'ultra',    label:'GAS Ultra',    sub:'Claude Sonnet 4.6 · 5cr',  badge:'SONNET',minPlan:'ultimate',  sigCr:5,  scanCr:18,
    accent:'text-amber-400',  bg:'bg-amber-400/10',  border:'border-amber-400/30',  icon:Zap },
  { id:'gpt',      label:'GAS GPT',      sub:'GPT-4o · 5cr',             badge:'GPT',   minPlan:'ultimate',  sigCr:5,  scanCr:18,
    accent:'text-teal-400',   bg:'bg-teal-400/10',   border:'border-teal-400/30',   icon:Zap },
  { id:'agent',    label:'GAS Agent',    sub:'Claude Opus 4.6 · 10cr',   badge:'AGENT', minPlan:'ultra',     sigCr:10, scanCr:25,
    accent:'text-rose-400',   bg:'bg-rose-400/10',   border:'border-rose-400/30',   icon:Brain },
];

const PLAN_ORDER = ['essential','plus','premium','ultimate','ultra'];
const PLAN_LABEL = { essential:'Essential', plus:'Plus', premium:'Premium', ultimate:'Ultimate', ultra:'Ultra' };

function planUnlocks(userPlan, minPlan) {
  return PLAN_ORDER.indexOf(userPlan) >= PLAN_ORDER.indexOf(minPlan);
}

// ── Order meta ─────────────────────────────────────────────────────────────────
const ORDER_META = {
  'BUY NOW':   { color:'text-emerald-400', bg:'bg-emerald-400/15', border:'border-emerald-400/40', icon:Zap },
  'SELL NOW':  { color:'text-red-400',     bg:'bg-red-400/15',     border:'border-red-400/40',     icon:Zap },
  'BUY LIMIT': { color:'text-emerald-300', bg:'bg-emerald-400/8',  border:'border-emerald-400/25', icon:TrendingUp },
  'SELL LIMIT':{ color:'text-red-300',     bg:'bg-red-400/8',      border:'border-red-400/25',     icon:TrendingDown },
  'BUY STOP':  { color:'text-cyan-400',    bg:'bg-cyan-400/10',    border:'border-cyan-400/30',    icon:TrendingUp },
  'SELL STOP': { color:'text-orange-400',  bg:'bg-orange-400/10',  border:'border-orange-400/30',  icon:TrendingDown },
  'WAIT':      { color:'text-yellow-400',  bg:'bg-yellow-400/10',  border:'border-yellow-400/30',  icon:Minus },
  'NEUTRAL':   { color:'text-[var(--text-dim)]', bg:'bg-[var(--bg-hover)]', border:'border-[var(--border-color)]', icon:Minus },
};

const GRADE_META = {
  'A+':{ color:'text-yellow-300',  bg:'bg-yellow-400/15'  },
  'A': { color:'text-emerald-300', bg:'bg-emerald-400/15' },
  'B': { color:'text-blue-300',    bg:'bg-blue-400/15'    },
  'C': { color:'text-[var(--text-dim)]', bg:'bg-[var(--bg-hover)]' },
};

// ── Small helpers ──────────────────────────────────────────────────────────────

function ProbabilityRing({ value = 0, size = 44 }) {
  const r = 16, circ = 2 * Math.PI * r;
  const fill = circ * (1 - value / 100);
  const color = value >= 70 ? '#34d399' : value >= 50 ? '#facc15' : '#f87171';
  return (
    <svg width={size} height={size} viewBox="0 0 36 36" className="shrink-0">
      <circle cx="18" cy="18" r={r} fill="none" stroke="currentColor" strokeWidth="2.5" className="text-[var(--bg-hover)]" />
      <circle cx="18" cy="18" r={r} fill="none" stroke={color} strokeWidth="2.5"
        strokeDasharray={circ} strokeDashoffset={fill}
        strokeLinecap="round" transform="rotate(-90 18 18)" />
      <text x="18" y="18" textAnchor="middle" dominantBaseline="central" fontSize="7" fontWeight="900" fill={color}>
        {value}%
      </text>
    </svg>
  );
}

function PriceLevel({ label, value, colorClass, precision = 5 }) {
  if (value == null) return (
    <div className="flex-1 min-w-0 rounded-lg p-2 bg-[var(--bg-panel)] border border-[var(--border-color)] opacity-30">
      <div className="text-[8px] font-bold text-[var(--text-dim)] uppercase">{label}</div>
      <div className="text-[9px] font-mono font-black text-[var(--text-dim)]">—</div>
    </div>
  );
  const fmt = typeof value === 'number' ? value.toFixed(precision) : value;
  return (
    <div className="flex-1 min-w-0 rounded-lg p-2 bg-[var(--bg-panel)] border border-[var(--border-color)]">
      <div className="text-[8px] font-bold text-[var(--text-dim)] uppercase mb-0.5">{label}</div>
      <div className={`text-[10px] font-mono font-black truncate ${colorClass}`}>{fmt}</div>
    </div>
  );
}

function SignalBadge({ orderType, size = 'sm' }) {
  const meta = ORDER_META[orderType] || ORDER_META['NEUTRAL'];
  const Icon = meta.icon;
  const textSize = size === 'lg' ? 'text-[11px]' : 'text-[9px]';
  const px = size === 'lg' ? 'px-3 py-1.5' : 'px-2 py-1';
  return (
    <span className={`inline-flex items-center gap-1.5 font-black uppercase tracking-wide ${textSize} ${px} rounded-lg border ${meta.color} ${meta.bg} ${meta.border}`}>
      <Icon size={size === 'lg' ? 12 : 9} />
      {orderType || 'WAIT'}
    </span>
  );
}

// ── Pair Picker Dropdown ───────────────────────────────────────────────────────

function PairPicker({ value, onChange }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState('');
  const ref = useRef(null);

  useEffect(() => {
    function handle(e) { if (ref.current && !ref.current.contains(e.target)) setOpen(false); }
    document.addEventListener('mousedown', handle);
    return () => document.removeEventListener('mousedown', handle);
  }, []);

  const filtered = SCAN_PAIRS.filter(p =>
    p.symbol.toLowerCase().includes(search.toLowerCase()) ||
    p.name.toLowerCase().includes(search.toLowerCase())
  );

  const selected = SCAN_PAIRS.find(p => p.symbol === value) || SCAN_PAIRS[0];

  return (
    <div className="relative" ref={ref}>
      <button onClick={() => setOpen(o => !o)}
        className="flex items-center gap-2 px-3 py-2.5 rounded-xl border border-[var(--border-color)] bg-[var(--bg-panel)] hover:border-[var(--accent)]/40 transition-all min-w-[180px]">
        <PairIcon symbol={selected.symbol} size={20} className="text-lg leading-none" />
        <div className="flex-1 text-left">
          <div className="text-[11px] font-black text-[var(--text-primary)]">{selected.symbol}</div>
          <div className="text-[8px] text-[var(--text-dim)] font-bold">{selected.name}</div>
        </div>
        <ChevronDown size={11} className={`text-[var(--text-dim)] transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>

      {open && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl shadow-2xl z-50 overflow-hidden">
          {/* Search */}
          <div className="p-2 border-b border-[var(--border-color)]">
            <div className="flex items-center gap-2 px-2 py-1.5 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)]">
              <Search size={10} className="text-[var(--text-dim)]" />
              <input autoFocus value={search} onChange={e => setSearch(e.target.value)}
                placeholder="Cari pair..."
                className="flex-1 bg-transparent text-[10px] font-bold text-[var(--text-primary)] placeholder:text-[var(--text-dim)] outline-none" />
            </div>
          </div>
          {/* List */}
          <div className="max-h-64 overflow-y-auto">
            {filtered.length === 0 && (
              <div className="px-3 py-4 text-center text-[9px] text-[var(--text-dim)]">Pair tidak ditemukan</div>
            )}
            {filtered.map(p => (
              <button key={p.symbol} onClick={() => { onChange(p.symbol); setOpen(false); setSearch(''); }}
                className={`w-full flex items-center gap-2 px-3 py-2 text-left hover:bg-[var(--bg-hover)] transition-colors ${p.symbol === value ? 'bg-[var(--bg-hover)]' : ''}`}>
                <PairIcon symbol={p.symbol} size={18} className="w-6 text-center" />
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] font-black text-[var(--text-primary)]">{p.symbol}</div>
                  <div className="text-[8px] text-[var(--text-dim)] font-bold">{p.name}</div>
                </div>
                <span className={`text-[7px] font-black px-1.5 py-0.5 rounded ${TYPE_COLOR[p.type] || 'text-[var(--text-dim)]'}`}>
                  {p.type}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Model Cards Row ────────────────────────────────────────────────────────────

function ModelCards({ selected, onSelect, userPlan, mode = 'signal' }) {
  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
      {MODEL_TIERS.map(tier => {
        const unlocked = planUnlocks(userPlan, tier.minPlan);
        const isSelected = selected === tier.id;
        const Icon = tier.icon;
        const cost = mode === 'signal' ? tier.sigCr : tier.scanCr;
        return (
          <button key={tier.id} disabled={!unlocked}
            onClick={() => unlocked && onSelect(tier.id)}
            className={`relative flex flex-col gap-1.5 p-3 rounded-xl border transition-all text-left ${
              isSelected
                ? `${tier.bg} ${tier.border} ring-1 ring-current/30 shadow-md`
                : unlocked
                  ? 'border-[var(--border-color)] hover:border-[var(--accent)]/30 hover:bg-[var(--bg-hover)]'
                  : 'border-[var(--border-color)] opacity-40 cursor-not-allowed'
            }`}>
            {/* Lock overlay */}
            {!unlocked && (
              <div className="absolute top-2 right-2">
                <Lock size={9} className="text-[var(--text-dim)]" />
              </div>
            )}
            {/* Icon + badge */}
            <div className="flex items-center gap-1.5">
              <div className={`p-1.5 rounded-lg ${tier.bg}`}>
                {unlocked
                  ? <Icon size={12} className={tier.accent} />
                  : <Lock size={12} className="text-[var(--text-dim)]" />}
              </div>
              <span className={`text-[7px] font-black px-1.5 py-0.5 rounded ${tier.bg} ${tier.accent}`}>
                {tier.badge}
              </span>
            </div>
            {/* Label */}
            <div>
              <div className={`text-[9px] font-black ${isSelected ? tier.accent : 'text-[var(--text-primary)]'}`}>
                {tier.label}
              </div>
              <div className="text-[7px] text-[var(--text-dim)] font-bold">{tier.sub}</div>
            </div>
            {/* Credit cost */}
            <div className="flex items-center justify-between mt-0.5">
              <span className={`text-[10px] font-black ${isSelected ? tier.accent : 'text-[var(--text-primary)]'}`}>
                {cost}cr
              </span>
              {!unlocked && (
                <span className="text-[6px] font-black px-1 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-dim)] border border-[var(--border-color)]">
                  {PLAN_LABEL[tier.minPlan]}+
                </span>
              )}
              {isSelected && unlocked && (
                <div className={`w-1.5 h-1.5 rounded-full ${tier.accent.replace('text-','bg-')}`} />
              )}
            </div>
          </button>
        );
      })}
    </div>
  );
}

// ── Full Signal Card ───────────────────────────────────────────────────────────

function FullSignalCard({ signal, loading, pair, modelTier, onRefresh }) {
  const tierMeta = MODEL_TIERS.find(m => m.id === modelTier) || MODEL_TIERS[0];

  if (loading) {
    return (
      <div className={`bg-[var(--bg-card)] border ${tierMeta.border} rounded-2xl p-6 flex flex-col items-center justify-center gap-3 min-h-[140px]`}>
        <RefreshCw size={20} className={`animate-spin ${tierMeta.accent}`} />
        <div className="text-center">
          <p className="text-xs font-black text-[var(--text-primary)]">{tierMeta.sub} sedang menganalisa {pair}</p>
          <p className="text-[9px] text-[var(--text-dim)] mt-0.5">RSI → MACD → EMA → ADX → {tierMeta.label}</p>
        </div>
      </div>
    );
  }

  if (!signal) {
    return (
      <div className="bg-[var(--bg-card)] border border-dashed border-[var(--border-color)] rounded-2xl p-8 flex flex-col items-center justify-center gap-3">
        <div className="text-4xl"><PairIcon symbol={pair} size={40} /></div>
        <div className="text-center">
          <p className="text-sm font-black text-[var(--text-primary)]">Siap Analisa {pair}</p>
          <p className="text-xs text-[var(--text-dim)] mt-1">Pilih model AI dan klik <span className="text-[var(--accent)] font-black">Generate Signal</span></p>
        </div>
      </div>
    );
  }

  const orderType = signal.order_type || signal.type || signal.action || 'WAIT';
  const meta = ORDER_META[orderType] || ORDER_META['NEUTRAL'];
  const grade = signal.grade || 'C';
  const gradeMeta = GRADE_META[grade] || GRADE_META['C'];
  const probability = signal.probability ?? signal.confidence ?? 0;
  const prec = pair.includes('JPY') ? 3 : (pair.includes('XAU') || pair.includes('US30') || pair.includes('NAS')) ? 2 : 5;
  const modelLabel = signal.model || tierMeta.label;

  return (
    <div className={`bg-[var(--bg-card)] border rounded-2xl overflow-hidden shadow-[var(--card-shadow)] ${meta.border}`}>
      {/* Header */}
      <div className={`px-5 py-3 flex items-center justify-between ${meta.bg} border-b ${meta.border}`}>
        <div className="flex items-center gap-2 flex-wrap">
          <PairIcon symbol={pair} size={22} className="text-xl leading-none" />
          <span className="text-sm font-black text-[var(--text-primary)]">{pair}</span>
          <SignalBadge orderType={orderType} size="lg" />
          <span className={`text-[8px] font-black px-2 py-0.5 rounded ${gradeMeta.bg} ${gradeMeta.color}`}>Grade {grade}</span>
          <span className={`text-[8px] font-black px-2 py-0.5 rounded border ${tierMeta.bg} ${tierMeta.accent} ${tierMeta.border}`}>
            🤖 {modelLabel}
          </span>
        </div>
        <div className="flex items-center gap-2">
          {signal.session && (
            <div className="flex items-center gap-1 text-[9px] text-[var(--text-dim)] font-bold">
              <Clock size={9} /> {signal.session}
            </div>
          )}
          <button onClick={onRefresh} className="p-1.5 rounded-lg hover:bg-[var(--bg-hover)] transition" title="Refresh">
            <RefreshCw size={11} className="text-[var(--text-dim)]" />
          </button>
        </div>
      </div>

      <div className="p-5 space-y-4">
        {/* Probability ring + Price levels */}
        <div className="flex items-start gap-4">
          <div className="flex flex-col items-center gap-1 shrink-0">
            <ProbabilityRing value={probability} size={56} />
            <span className="text-[7px] font-black text-[var(--text-dim)] uppercase">Probabilitas</span>
          </div>
          <div className="flex-1 grid grid-cols-2 sm:grid-cols-5 gap-2">
            <PriceLevel label="Entry"    value={signal.entry} colorClass="text-[var(--text-primary)]" precision={prec} />
            <PriceLevel label="Stop Loss" value={signal.sl}   colorClass="text-[var(--danger)]"      precision={prec} />
            <PriceLevel label="TP 1"     value={signal.tp1}  colorClass="text-[var(--success)]"      precision={prec} />
            <PriceLevel label="TP 2"     value={signal.tp2}  colorClass="text-emerald-300"           precision={prec} />
            <PriceLevel label="TP 3"     value={signal.tp3}  colorClass="text-emerald-200"           precision={prec} />
          </div>
        </div>

        {/* Meta row */}
        {(signal.rr || signal.key_levels?.resistance) && (
          <div className="flex flex-wrap items-center gap-2">
            {signal.rr && signal.rr !== 'N/A' && (
              <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)]">
                <Target size={9} className="text-[var(--accent)]" />
                <span className="text-[9px] font-black text-[var(--text-primary)]">RR {signal.rr}</span>
              </div>
            )}
            {signal.key_levels?.support != null && (
              <div className="flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)]">
                <Shield size={9} className="text-[var(--text-dim)]" />
                <span className="text-[9px] font-black text-[var(--text-dim)]">
                  S: {signal.key_levels.support?.toFixed(prec)} · R: {signal.key_levels.resistance?.toFixed(prec)}
                </span>
              </div>
            )}
          </div>
        )}

        {/* Trigger */}
        {signal.trigger && (
          <div className="flex items-start gap-2 p-3 rounded-xl bg-[var(--accent)]/5 border border-[var(--accent)]/20">
            <Crosshair size={12} className="text-[var(--accent)] shrink-0 mt-0.5" />
            <div>
              <div className="text-[7px] font-black text-[var(--accent)] uppercase tracking-wider mb-0.5">Trigger Signal</div>
              <p className="text-[11px] font-semibold text-[var(--text-secondary)] leading-relaxed">{signal.trigger}</p>
            </div>
          </div>
        )}

        {/* Reasoning + Trading Plan */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {signal.reasoning && (
            <div className="flex items-start gap-2 p-3 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)]">
              <Brain size={12} className="text-purple-400 shrink-0 mt-0.5" />
              <div>
                <div className="text-[7px] font-black text-purple-400 uppercase tracking-wider mb-0.5">AI Reasoning</div>
                <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{signal.reasoning}</p>
              </div>
            </div>
          )}
          {signal.trading_plan && (
            <div className="flex items-start gap-2 p-3 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)]">
              <BookOpen size={12} className="text-blue-400 shrink-0 mt-0.5" />
              <div>
                <div className="text-[7px] font-black text-blue-400 uppercase tracking-wider mb-0.5">Trading Plan</div>
                <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{signal.trading_plan}</p>
              </div>
            </div>
          )}
        </div>

        {/* SMC Context Row */}
        {signal.smc_available && (
          <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-panel)] p-3 space-y-2">
            <div className="flex items-center gap-1.5 mb-1">
              <Activity size={10} className="text-purple-400" />
              <span className="text-[8px] font-black text-purple-400 uppercase tracking-wider">Smart Money Context (SMC Engine)</span>
            </div>
            <div className="flex flex-wrap gap-2">
              {/* Confluence Score */}
              {signal.confluence_score != null && (
                <div className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <span className="text-[7px] font-black text-[var(--text-dim)] uppercase">Confluence</span>
                  <span className={`text-[11px] font-black font-mono ${signal.confluence_score >= 70 ? 'text-emerald-400' : signal.confluence_score >= 50 ? 'text-yellow-400' : 'text-red-400'}`}>
                    {signal.confluence_score}/100
                  </span>
                  <div className="w-12 h-1 rounded-full bg-[var(--bg-hover)] overflow-hidden">
                    <div className={`h-full rounded-full ${signal.confluence_score >= 70 ? 'bg-emerald-400' : signal.confluence_score >= 50 ? 'bg-yellow-400' : 'bg-red-400'}`}
                      style={{width: `${signal.confluence_score}%`}} />
                  </div>
                </div>
              )}
              {/* Setup Type */}
              {signal.setup_type && signal.setup_type !== 'Unknown' && (
                <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-purple-400/10 border border-purple-400/25">
                  <Crosshair size={9} className="text-purple-400" />
                  <span className="text-[9px] font-black text-purple-400">{signal.setup_type}</span>
                </div>
              )}
              {/* SMC Bias */}
              {signal.smc_bias && signal.smc_bias !== 'NEUTRAL' && (
                <div className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg border ${signal.smc_bias === 'BULLISH' ? 'bg-emerald-400/10 border-emerald-400/25 text-emerald-400' : 'bg-red-400/10 border-red-400/25 text-red-400'}`}>
                  {signal.smc_bias === 'BULLISH' ? <TrendingUp size={9} /> : <TrendingDown size={9} />}
                  <span className="text-[9px] font-black">{signal.smc_bias}</span>
                </div>
              )}
              {/* Kill Zone */}
              {signal.kill_zone && (
                <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-red-400/10 border border-red-400/25">
                  <Clock size={9} className="text-red-400" />
                  <span className="text-[9px] font-black text-red-400">Kill Zone</span>
                </div>
              )}
              {/* AMD Phase */}
              {signal.amd_phase && (
                <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <Cpu size={9} className="text-[var(--accent)]" />
                  <span className="text-[7px] font-black text-[var(--text-dim)] uppercase">AMD</span>
                  <span className="text-[9px] font-black text-[var(--accent)]">{signal.amd_phase}</span>
                </div>
              )}
              {/* SMC Score */}
              {signal.smc_score != null && (
                <div className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]">
                  <span className="text-[7px] font-black text-[var(--text-dim)] uppercase">SMC</span>
                  <span className={`text-[9px] font-black font-mono ${signal.smc_score >= 60 ? 'text-emerald-400' : 'text-[var(--text-dim)]'}`}>
                    {signal.smc_score}/100
                  </span>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Invalidation */}
        {signal.invalidation && (
          <div className="flex items-center gap-2 p-2 rounded-lg bg-[var(--danger)]/5 border border-[var(--danger)]/15">
            <AlertTriangle size={10} className="text-[var(--danger)] shrink-0" />
            <span className="text-[9px] text-[var(--danger)]/80 font-semibold">{signal.invalidation}</span>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Data flow legend ───────────────────────────────────────────────────────────
function DataFlowLegend({ tierMeta }) {
  return (
    <div className="flex flex-wrap items-center gap-1 text-[8px] text-[var(--text-dim)]">
      <span className="font-black text-[var(--text-dim)] uppercase tracking-wider">Alur:</span>
      {[
        ['MT5/Binance','bg-blue-400/10 text-blue-300'],
        ['OHLC 200 bar','bg-[var(--bg-hover)]'],
        ['Indicator Engine','bg-[var(--bg-hover)] text-[var(--text-secondary)]'],
        ['SMC Engine','bg-purple-400/10 text-purple-400'],
        ['Feature Builder','bg-[var(--accent)]/10 text-[var(--accent)]'],
        [tierMeta.sub, `${tierMeta.bg} ${tierMeta.accent}`],
        ['Signal','bg-emerald-400/10 text-emerald-400'],
      ].map(([label, cls], i) => (
        <React.Fragment key={i}>
          <span className={`px-1.5 py-0.5 rounded font-bold ${cls}`}>{label}</span>
          {i < 6 && <span className="text-[var(--text-dim)]">→</span>}
        </React.Fragment>
      ))}
    </div>
  );
}

// ── Main SignalView ────────────────────────────────────────────────────────────

export default function SignalView({ chartPair, prices, onSelect, activePair, pairs, theme, signal: propSignal }) {
  const [style, setStyle]       = useState('scalping');
  const [modelTier, setModelTier] = useState('basic');
  const [userPlan, setUserPlan] = useState('essential');

  // Resolve TF from style
  const styleTFs = STYLE_MATRIX[style]?.tfs || ['H4','H1','M15','M5'];
  const primaryTF = styleTFs[2] || 'M15'; // Setup TF

  // Chart signal (for active chart pair)
  const [chartSignal, setChartSignal] = useState(null);
  const [chartLoading, setChartLoading] = useState(false);

  // Scanner: single pair
  const [scanPair, setScanPair] = useState('XAUUSD');
  const [scanStyle, setScanStyle] = useState('scalping');
  const [scanModel, setScanModel] = useState('basic');
  const [scanResult, setScanResult] = useState(null);
  const [scanLoading, setScanLoading] = useState(false);
  const scanTF = STYLE_MATRIX[scanStyle]?.tfs[2] || 'M15';

  const pairData = pairs.find(p => p.symbol === chartPair.symbol) || chartPair;
  const curPrice = prices[chartPair.symbol] || pairData.base;
  const prec = pairData.type === 'Forex' ? 5 : curPrice < 1 ? 4 : 2;
  const chartTierMeta = MODEL_TIERS.find(m => m.id === modelTier) || MODEL_TIERS[0];
  const scanTierMeta  = MODEL_TIERS.find(m => m.id === scanModel) || MODEL_TIERS[0];

  const displaySignal = chartSignal || propSignal;
  const orderType = displaySignal?.order_type || displaySignal?.type || displaySignal?.action || 'WAIT';
  const orderMeta = ORDER_META[orderType] || ORDER_META['WAIT'];

  // Fetch user plan on mount
  useEffect(() => {
    fetch('/web/api/v1/analysis/signal/models', {
      headers: { Authorization: `Bearer ${localStorage.getItem('gas-token') || ''}` },
    })
      .then(r => r.json())
      .then(d => { if (d.user_plan) setUserPlan(d.user_plan); })
      .catch(() => {});
  }, []);

  // Generate chart signal (manual)
  const generateChartSignal = useCallback(async () => {
    setChartLoading(true);
    setChartSignal(null);
    try {
      const res = await callAIFeature('signal', {
        pair: chartPair.symbol,
        style,
        timeframe: primaryTF,
        model_tier: modelTier,
      });
      setChartSignal(res);
    } catch { setChartSignal(null); }
    finally { setChartLoading(false); }
  }, [chartPair.symbol, style, primaryTF, modelTier]);

  // Run single pair scan
  const runScan = useCallback(async () => {
    setScanLoading(true);
    setScanResult(null);
    try {
      const res = await callAIFeature('signal', {
        pair: scanPair,
        style: scanStyle,
        timeframe: scanTF,
        model_tier: scanModel,
      });
      setScanResult(res);
    } catch { setScanResult(null); }
    finally { setScanLoading(false); }
  }, [scanPair, scanStyle, scanTF, scanModel]);

  // Reset chart signal when pair/style/model changes
  useEffect(() => { setChartSignal(null); }, [chartPair.symbol, style, modelTier]);

  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6">

      {/* ── SECTION 1: Chart Signal ─────────────────────────────────────── */}
      <div className="space-y-4">
        {/* Section label */}
        <div className="flex items-center gap-2">
          <BarChart3 size={14} className="text-[var(--accent)]" />
          <h2 className="text-xs font-black text-[var(--text-primary)] uppercase tracking-widest">Signal AI — {chartPair.symbol}</h2>
          <span className="text-[8px] px-2 py-0.5 bg-[var(--accent)]/10 text-[var(--accent)] rounded-full font-black">Active Chart</span>
        </div>

        {/* Chart */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden shadow-[var(--card-shadow)]" style={{height:420}}>
          <div className="flex items-center justify-between px-4 py-2.5 border-b border-[var(--border-color)] bg-[var(--bg-panel)]/50 shrink-0 gap-3 flex-wrap">
            <div className="flex items-center gap-2">
              <PairIcon symbol={chartPair.symbol} size={26} className="text-2xl leading-none" />
              <div>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-black text-[var(--text-primary)] uppercase">{chartPair.symbol}</span>
                  <SignalBadge orderType={orderType} />
                  <span className="text-xs font-mono font-black text-[var(--text-primary)]">{curPrice.toFixed(prec)}</span>
                </div>
                <span className="text-[8px] text-[var(--text-dim)] font-bold uppercase tracking-widest">{chartPair.name}</span>
              </div>
            </div>
            {/* Style TF Badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg">
              <span className="text-[8px] font-black text-[var(--text-dim)] uppercase">Style:</span>
              <span className="text-[9px] font-black text-[var(--accent)]">{style}</span>
              <span className="text-[8px] text-[var(--text-dim)]">·</span>
              <span className="text-[9px] font-mono font-black text-[var(--text-secondary)]">{styleTFs.join('→')}</span>
            </div>
          </div>
          <div style={{height:'calc(100% - 52px)'}}>
            <TradingViewWidget pair={chartPair} theme={theme} />
          </div>
        </div>

        {/* Style selector + Model selector + Generate button */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4 space-y-4">
          {/* Style selector */}
          <StyleSelector value={style} onChange={s => { setStyle(s); setChartSignal(null); }} showMatrix={true} />

          <div className="border-t border-[var(--border-color)] pt-3 flex items-center justify-between">
            <div>
              <p className="text-[10px] font-black text-[var(--text-primary)] uppercase tracking-wider">Pilih Model AI</p>
              <p className="text-[8px] text-[var(--text-dim)]">Plan kamu: <span className="font-black text-[var(--accent)]">{PLAN_LABEL[userPlan] || userPlan}</span></p>
            </div>
            <button onClick={generateChartSignal} disabled={chartLoading}
              className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-[11px] font-black border transition-all hover:scale-105 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed ${chartTierMeta.bg} ${chartTierMeta.border} ${chartTierMeta.accent}`}>
              {chartLoading
                ? <><RefreshCw size={13} className="animate-spin" /> Menganalisa...</>
                : <><Zap size={13} /> Generate Signal · {chartTierMeta.sigCr}cr</>}
            </button>
          </div>
          <ModelCards selected={modelTier} onSelect={setModelTier} userPlan={userPlan} mode="signal" />
          <DataFlowLegend tierMeta={chartTierMeta} />
        </div>

        {/* Signal result card */}
        <FullSignalCard
          signal={displaySignal}
          loading={chartLoading}
          pair={chartPair.symbol}
          modelTier={modelTier}
          onRefresh={generateChartSignal}
        />
      </div>

      {/* ── SECTION 2: Single Pair Scanner ──────────────────────────────── */}
      <div className="space-y-4">
        {/* Section label */}
        <div className="flex items-center gap-2 pt-2 border-t border-[var(--border-color)]">
          <ScanLine size={14} className="text-[var(--accent)]" />
          <h2 className="text-xs font-black text-[var(--text-primary)] uppercase tracking-widest">Single Pair AI Scanner</h2>
          <span className="text-[8px] px-2 py-0.5 bg-purple-400/10 text-purple-400 rounded-full font-black">Pilih pair bebas</span>
        </div>

        {/* Scanner controls */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4 space-y-4">
          {/* Style selector */}
          <StyleSelector value={scanStyle} onChange={s => { setScanStyle(s); setScanResult(null); }} showMatrix={true} />

          {/* Row 1: Pair picker + Scan button */}
          <div className="flex flex-wrap items-center gap-3 border-t border-[var(--border-color)] pt-3">
            {/* Pair picker */}
            <PairPicker value={scanPair} onChange={p => { setScanPair(p); setScanResult(null); }} />

            {/* Active TF badge */}
            <div className="flex items-center gap-1.5 px-2.5 py-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
              <span className="text-[8px] font-black text-[var(--text-dim)] uppercase">TF:</span>
              <span className="text-[9px] font-black text-[var(--accent)] font-mono">{scanTF}</span>
            </div>

            {/* Scan button */}
            <button onClick={runScan} disabled={scanLoading}
              className={`ml-auto flex items-center gap-2 px-5 py-2.5 rounded-xl text-[11px] font-black border transition-all hover:scale-105 active:scale-95 disabled:opacity-60 disabled:cursor-not-allowed ${scanTierMeta.bg} ${scanTierMeta.border} ${scanTierMeta.accent}`}>
              {scanLoading
                ? <><RefreshCw size={13} className="animate-spin" /> Scanning...</>
                : <><ScanLine size={13} /> Scan {scanPair} · {scanStyle} · {scanTierMeta.scanCr}cr</>}
            </button>
          </div>

          {/* Row 2: Model cards */}
          <div>
            <p className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-wider mb-2">Model AI Scanner</p>
            <ModelCards selected={scanModel} onSelect={setScanModel} userPlan={userPlan} mode="scanner" />
          </div>
          <DataFlowLegend tierMeta={scanTierMeta} />
        </div>

        {/* Scan result */}
        <FullSignalCard
          signal={scanResult}
          loading={scanLoading}
          pair={scanPair}
          modelTier={scanModel}
          onRefresh={runScan}
        />
      </div>
    </div>
  );
}
