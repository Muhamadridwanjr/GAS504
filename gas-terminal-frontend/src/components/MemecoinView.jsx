import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  TrendingUp, TrendingDown, RefreshCw, Search, Zap,
  Shield, AlertTriangle, Skull, BarChart2, Clock,
  ChevronDown, ChevronUp, ExternalLink, Activity,
  Flame, Target, Cpu, Globe, AlertCircle
} from 'lucide-react';
import AutoSignalPanel from './AutoSignalPanel';
import MarketAnalysisPanel from './MarketAnalysisPanel';

// ── Constants ────────────────────────────────────────────────────────────────
const CHAINS = [
  { id: 'all',       label: 'All Chains', color: '#6366f1', short: 'ALL' },
  { id: 'solana',    label: 'Solana',     color: '#9945ff', short: 'SOL' },
  { id: 'ethereum',  label: 'Ethereum',   color: '#627eea', short: 'ETH' },
  { id: 'base',      label: 'Base',       color: '#0052ff', short: 'BASE' },
  { id: 'bsc',       label: 'BSC',        color: '#f0b90b', short: 'BSC' },
  { id: 'arbitrum',  label: 'Arbitrum',   color: '#28a0f0', short: 'ARB' },
  { id: 'avalanche', label: 'Avalanche',  color: '#e84142', short: 'AVAX' },
  { id: 'polygon',   label: 'Polygon',    color: '#8247e5', short: 'MATIC' },
  { id: 'tron',      label: 'Tron',       color: '#ff0013', short: 'TRX' },
  { id: 'sui',       label: 'Sui',        color: '#4da2ff', short: 'SUI' },
];

const SIGNAL_CFG = {
  'BUY EARLY':    { bg: 'rgba(16,185,129,0.2)',   color: '#10b981', border: 'rgba(16,185,129,0.4)',  icon: '🔥', glow: '0 0 20px rgba(16,185,129,0.3)'  },
  'BUY MOMENTUM': { bg: 'rgba(99,102,241,0.15)',  color: '#818cf8', border: 'rgba(99,102,241,0.35)', icon: '🚀', glow: '0 0 16px rgba(99,102,241,0.25)' },
  'WEAK TREND':   { bg: 'rgba(245,158,11,0.12)',  color: '#fbbf24', border: 'rgba(245,158,11,0.3)',  icon: '📊', glow: 'none' },
  'AVOID':        { bg: 'rgba(249,115,22,0.12)',  color: '#fb923c', border: 'rgba(249,115,22,0.3)',  icon: '⚠️', glow: 'none' },
  'EXIT NOW':     { bg: 'rgba(244,63,94,0.15)',   color: '#f43f5e', border: 'rgba(244,63,94,0.35)',  icon: '🚨', glow: 'none' },
  'DANGER':       { bg: 'rgba(100,10,10,0.3)',    color: '#ef4444', border: 'rgba(239,68,68,0.5)',   icon: '💀', glow: '0 0 12px rgba(239,68,68,0.2)'  },
};

const RISK_CFG = {
  'LOW':     { color: '#10b981', icon: Shield },
  'MEDIUM':  { color: '#f59e0b', icon: AlertTriangle },
  'HIGH':    { color: '#f97316', icon: AlertTriangle },
  'EXTREME': { color: '#ef4444', icon: Skull },
};

const MODEL_META = {
  claude:  { label: 'Claude',  color: '#f59e0b', specialty: 'Rug Detection'  },
  gpt:     { label: 'GPT',     color: '#10b981', specialty: 'Volume'         },
  gemini:  { label: 'Gemini',  color: '#3b82f6', specialty: 'Trend'          },
  grok:    { label: 'Grok',    color: '#f43f5e', specialty: 'Momentum'       },
};

// ── Helpers ──────────────────────────────────────────────────────────────────
const fmt = {
  price: (p) => {
    if (!p) return '$0';
    if (p < 0.000001) return `$${p.toExponential(2)}`;
    if (p < 0.001)    return `$${p.toFixed(6)}`;
    if (p < 1)        return `$${p.toFixed(4)}`;
    return `$${p.toLocaleString('en', { maximumFractionDigits: 2 })}`;
  },
  usd: (v) => {
    if (!v) return '$0';
    if (v >= 1e6) return `$${(v/1e6).toFixed(1)}M`;
    if (v >= 1e3) return `$${(v/1e3).toFixed(0)}K`;
    return `$${v.toFixed(0)}`;
  },
  pct: (v) => `${v > 0 ? '+' : ''}${v?.toFixed(1) ?? '0.0'}%`,
  age: (m) => {
    if (m < 60)   return `${Math.round(m)}m`;
    if (m < 1440) return `${Math.round(m/60)}h`;
    return `${Math.round(m/1440)}d`;
  },
};

// ── Token Logo ────────────────────────────────────────────────────────────────
function TokenLogo({ token, size = 32 }) {
  const [imgErr, setImgErr] = useState(false);
  const chainCfg = CHAINS.find(c => c.id === token.chain) || CHAINS[0];
  const logoUrl = token.logo_url || (token.token_address
    ? `https://dd.dexscreener.com/ds-data/tokens/${token.chain}/${token.token_address}/logo.png`
    : null);
  const initials = (token.symbol || '?').slice(0, 2).toUpperCase();

  if (logoUrl && !imgErr) {
    return (
      <div className="relative flex-shrink-0" style={{ width: size, height: size }}>
        <img src={logoUrl} alt={token.symbol} onError={() => setImgErr(true)}
          className="rounded-full object-cover w-full h-full"
          style={{ border: `1.5px solid ${chainCfg.color}40` }} />
        <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full flex items-center justify-center text-[5px] font-black"
          style={{ background: chainCfg.color, color: '#fff', fontSize: '5px' }}>
          {chainCfg.short.slice(0, 1)}
        </div>
      </div>
    );
  }
  return (
    <div className="relative flex-shrink-0 rounded-full flex items-center justify-center font-black"
      style={{ width: size, height: size, background: `${chainCfg.color}22`, border: `1.5px solid ${chainCfg.color}40`, color: chainCfg.color, fontSize: size * 0.34 }}>
      {initials}
      <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full flex items-center justify-center"
        style={{ background: chainCfg.color, fontSize: '5px', color: '#fff', fontWeight: 900 }}>
        {chainCfg.short.slice(0, 1)}
      </div>
    </div>
  );
}

// ── List Row (Dexscreener style) ───────────────────────────────────────────────
function TokenRowList({ token, onAnalyze, analyzing, signal, rank }) {
  const chainCfg = CHAINS.find(c => c.id === token.chain) || CHAINS[0];
  const finalSig = signal?.signal || token.signal;
  const sigCfg = SIGNAL_CFG[finalSig] || SIGNAL_CFG['AVOID'];
  const hasSignal = !!signal;

  return (
    <tr className="border-b border-[rgba(255,255,255,0.05)] hover:bg-[rgba(255,255,255,0.03)] transition-colors group">
      {/* Rank */}
      <td className="px-3 py-2.5 text-[10px] text-[var(--text-dim)] font-mono w-8">{rank}</td>
      {/* Token */}
      <td className="px-2 py-2">
        <div className="flex items-center gap-2">
          <TokenLogo token={token} size={28} />
          <div>
            <div className="text-[11px] font-black text-[var(--text-primary)] leading-none">{token.symbol}</div>
            <div className="text-[8px] text-[var(--text-dim)] leading-none mt-0.5 max-w-[80px] truncate">{token.name}</div>
          </div>
        </div>
      </td>
      {/* Chain */}
      <td className="px-2 py-2 hidden sm:table-cell">
        <span className="text-[9px] font-bold px-1.5 py-0.5 rounded" style={{ background: `${chainCfg.color}20`, color: chainCfg.color }}>
          {chainCfg.short}
        </span>
      </td>
      {/* Price */}
      <td className="px-2 py-2 text-right">
        <span className="text-[11px] font-black font-mono text-[var(--text-primary)]">{fmt.price(token.price_usd)}</span>
      </td>
      {/* 5m */}
      <td className={`px-2 py-2 text-right text-[10px] font-bold ${token.price_change_5m >= 0 ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
        {fmt.pct(token.price_change_5m)}
      </td>
      {/* 1h */}
      <td className={`px-2 py-2 text-right text-[10px] font-bold ${token.price_change_1h >= 0 ? 'text-[#10b981]' : 'text-[#f43f5e]'}`}>
        {fmt.pct(token.price_change_1h)}
      </td>
      {/* Liquidity */}
      <td className="px-2 py-2 text-right text-[10px] font-mono text-[var(--text-secondary)] hidden md:table-cell">
        {fmt.usd(token.liquidity_usd)}
      </td>
      {/* Vol 1h */}
      <td className="px-2 py-2 text-right text-[10px] font-mono text-[var(--text-secondary)] hidden lg:table-cell">
        {fmt.usd(token.volume_1h)}
      </td>
      {/* Mcap */}
      <td className="px-2 py-2 text-right text-[10px] font-mono text-[var(--text-secondary)] hidden lg:table-cell">
        {token.market_cap ? fmt.usd(token.market_cap) : '—'}
      </td>
      {/* Age */}
      <td className="px-2 py-2 text-right text-[10px] text-[var(--text-dim)] hidden xl:table-cell">
        {fmt.age(token.age_minutes)}
      </td>
      {/* Signal */}
      <td className="px-2 py-2 text-center">
        {hasSignal
          ? <SignalBadge signal={finalSig} size="xs" />
          : <span className="text-[9px] text-[var(--text-dim)] hidden group-hover:inline">—</span>
        }
      </td>
      {/* Score */}
      <td className="px-2 py-2 text-right">
        <span className="text-[10px] font-black font-mono" style={{
          color: (signal?.score || token.score) >= 70 ? '#10b981' : (signal?.score || token.score) >= 50 ? '#f59e0b' : '#ef4444'
        }}>{signal?.score || token.score}</span>
      </td>
      {/* Analyze */}
      <td className="px-2 py-2">
        <button onClick={() => onAnalyze(token)} disabled={analyzing}
          className="px-2 py-1 rounded-lg text-[9px] font-bold transition-all disabled:opacity-40 whitespace-nowrap"
          style={{ background: hasSignal ? 'rgba(99,102,241,0.1)' : 'rgba(99,102,241,0.2)', color: '#818cf8', border: '1px solid rgba(99,102,241,0.3)' }}>
          {analyzing ? '...' : hasSignal ? '↻ 5cr' : '🧠 5cr'}
        </button>
      </td>
    </tr>
  );
}

// ── Signal Badge ──────────────────────────────────────────────────────────────
function SignalBadge({ signal, size = 'sm' }) {
  const cfg = SIGNAL_CFG[signal] || SIGNAL_CFG['AVOID'];
  const px = size === 'lg' ? 'px-3 py-1.5 text-xs' : size === 'xs' ? 'px-1.5 py-0.5 text-[9px]' : 'px-2 py-0.5 text-[10px]';
  return (
    <span className={`inline-flex items-center gap-1 rounded-full font-black ${px} whitespace-nowrap`}
      style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}`, boxShadow: cfg.glow }}>
      {cfg.icon} {signal}
    </span>
  );
}

// ── Risk Badge ────────────────────────────────────────────────────────────────
function RiskBadge({ risk }) {
  const cfg = RISK_CFG[risk] || RISK_CFG['HIGH'];
  const Icon = cfg.icon;
  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border"
      style={{ color: cfg.color, borderColor: `${cfg.color}40`, background: `${cfg.color}12` }}>
      <Icon size={8} /> {risk}
    </span>
  );
}

// ── Score Ring ────────────────────────────────────────────────────────────────
function ScoreRing({ score, size = 52 }) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  const color = score >= 70 ? '#10b981' : score >= 50 ? '#f59e0b' : score >= 35 ? '#f97316' : '#ef4444';
  return (
    <div className="relative flex items-center justify-center" style={{ width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)', position: 'absolute' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="5" />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="5"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.8s ease', filter: `drop-shadow(0 0 4px ${color}80)` }} />
      </svg>
      <div className="text-center z-10">
        <div className="text-xs font-black leading-none" style={{ color }}>{score}</div>
        <div className="text-[8px] text-[var(--text-dim)] leading-none">score</div>
      </div>
    </div>
  );
}

// ── Rug Panel ─────────────────────────────────────────────────────────────────
function RugPanel({ rug }) {
  const levelColor = rug.level === 'SAFE' ? '#10b981' : rug.level === 'RISKY' ? '#f59e0b' : '#ef4444';
  const levelIcon  = rug.level === 'SAFE' ? '✅' : rug.level === 'RISKY' ? '⚠️' : '🔴';
  return (
    <div className="rounded-xl p-3 border"
      style={{ background: `${levelColor}0d`, borderColor: `${levelColor}30` }}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-[10px] font-bold flex items-center gap-1" style={{ color: levelColor }}>
          <Shield size={10} /> Rug Detection
        </span>
        <span className="text-[10px] font-black" style={{ color: levelColor }}>
          {levelIcon} {rug.level} · {rug.score}/100
        </span>
      </div>
      {rug.flags?.length > 0 && (
        <div className="space-y-1">
          {rug.flags.slice(0, 3).map((f, i) => (
            <div key={i} className="text-[9px] text-[#f43f5e] flex items-start gap-1">
              <span>•</span><span>{f}</span>
            </div>
          ))}
        </div>
      )}
      {(!rug.flags || rug.flags.length === 0) && (
        <div className="text-[9px] text-[#10b981]">No red flags detected</div>
      )}
    </div>
  );
}

// ── Agent Row ─────────────────────────────────────────────────────────────────
function AgentRow({ agent }) {
  const meta = MODEL_META[agent.model] || { label: agent.model, color: '#6366f1', specialty: '' };
  const sigCfg = SIGNAL_CFG[agent.signal] || SIGNAL_CFG['AVOID'];
  return (
    <div className="py-2 border-b border-[rgba(255,255,255,0.05)] last:border-0">
      <div className="flex items-center gap-2">
        <div className="w-12 text-[10px] font-black" style={{ color: meta.color }}>{meta.label}</div>
        <div className="text-[8px] text-[var(--text-dim)] flex-1">{meta.specialty} · ×{agent.weight}</div>
        <SignalBadge signal={agent.signal} size="xs" />
        <div className="w-8 text-right text-[10px] font-bold" style={{ color: sigCfg.color }}>{agent.score}</div>
      </div>
      {agent.reasoning && (
        <div className="text-[8px] text-[var(--text-dim)] mt-0.5 ml-14 leading-relaxed italic line-clamp-1">
          {agent.reasoning}
        </div>
      )}
    </div>
  );
}

// ── Token Card ────────────────────────────────────────────────────────────────
function TokenCard({ token, onAnalyze, analyzing, signal }) {
  const [expanded, setExpanded] = useState(false);
  const chainCfg = CHAINS.find(c => c.id === token.chain) || CHAINS[0];
  const sigCfg   = SIGNAL_CFG[token.signal] || SIGNAL_CFG['AVOID'];
  const hasSignal = !!signal;
  const finalSig = signal?.signal || token.signal;
  const finalCfg = SIGNAL_CFG[finalSig] || sigCfg;

  return (
    <div className="rounded-2xl border transition-all duration-200 overflow-hidden"
      style={{
        background: hasSignal ? finalCfg.bg : 'rgba(255,255,255,0.025)',
        borderColor: hasSignal ? finalCfg.border : 'rgba(255,255,255,0.09)',
        boxShadow: hasSignal ? finalCfg.glow : 'none',
      }}>
      <div className="p-4">
        {/* Header row */}
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            {/* Chain badge */}
            <div className="w-6 h-6 rounded-full flex items-center justify-center text-[9px] font-black"
              style={{ background: `${chainCfg.color}20`, color: chainCfg.color, border: `1px solid ${chainCfg.color}40` }}>
              {token.chain.slice(0,1).toUpperCase()}
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="text-sm font-black text-[var(--text-primary)]">{token.symbol}</span>
                <span className="text-[9px] text-[var(--text-dim)]">{token.chain}</span>
              </div>
              <div className="text-[9px] text-[var(--text-dim)] max-w-[120px] truncate">{token.name}</div>
            </div>
          </div>
          <div className="flex flex-col items-end gap-1">
            <SignalBadge signal={finalSig} size="sm" />
            <RiskBadge risk={signal?.risk || token.risk} />
          </div>
        </div>

        {/* Score + price row */}
        <div className="flex items-center gap-3 mb-3">
          <ScoreRing score={signal?.score || token.score} />
          <div className="flex-1">
            <div className="text-base font-black text-[var(--text-primary)]">{fmt.price(token.price_usd)}</div>
            <div className="flex items-center gap-2 text-[10px] mt-0.5">
              <span className={token.price_change_1h >= 0 ? 'text-[#10b981] font-bold' : 'text-[#f43f5e] font-bold'}>
                {token.price_change_1h >= 0 ? <TrendingUp size={9} className="inline" /> : <TrendingDown size={9} className="inline" />}
                {' '}{fmt.pct(token.price_change_1h)} 1h
              </span>
              <span className={token.price_change_5m >= 0 ? 'text-[#10b981]' : 'text-[#f43f5e]'}>
                {fmt.pct(token.price_change_5m)} 5m
              </span>
            </div>
          </div>
          {/* DEX link */}
          {token.dex_url && (
            <a href={token.dex_url} target="_blank" rel="noopener noreferrer"
              className="p-1.5 rounded-lg border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.08)] transition-colors">
              <ExternalLink size={11} className="text-[var(--text-dim)]" />
            </a>
          )}
        </div>

        {/* Metrics grid */}
        <div className="grid grid-cols-3 gap-2 mb-3">
          {[
            { label: 'Liquidity', value: fmt.usd(token.liquidity_usd), icon: Activity },
            { label: 'Vol 1h',    value: fmt.usd(token.volume_1h),     icon: BarChart2 },
            { label: 'Age',       value: fmt.age(token.age_minutes),   icon: Clock },
          ].map(m => {
            const Icon = m.icon;
            return (
              <div key={m.label} className="rounded-lg p-2 bg-[rgba(255,255,255,0.04)] border border-[rgba(255,255,255,0.06)]">
                <div className="text-[8px] text-[var(--text-dim)] flex items-center gap-1 mb-0.5">
                  <Icon size={7} />{m.label}
                </div>
                <div className="text-[10px] font-bold text-[var(--text-primary)]">{m.value}</div>
              </div>
            );
          })}
        </div>

        {/* Buy pressure bar */}
        <div className="mb-3">
          <div className="flex justify-between text-[9px] mb-1">
            <span className="text-[#10b981] font-bold">BUY {Math.round(token.buy_pressure * 100)}%</span>
            <span className="text-[#f43f5e] font-bold">SELL {Math.round((1 - token.buy_pressure) * 100)}%</span>
          </div>
          <div className="h-1.5 rounded-full overflow-hidden bg-[rgba(255,255,255,0.06)] flex">
            <div className="h-1.5 rounded-l-full transition-all duration-500"
              style={{ width: `${token.buy_pressure * 100}%`, background: 'linear-gradient(90deg,#059669,#10b981)' }} />
            <div className="h-1.5 rounded-r-full"
              style={{ width: `${(1 - token.buy_pressure) * 100}%`, background: 'linear-gradient(90deg,#e11d48,#f43f5e)' }} />
          </div>
          <div className="flex justify-between text-[8px] mt-0.5 text-[var(--text-dim)]">
            <span>{token.buys_1h || 0} buys</span>
            <span>{token.sells_1h || 0} sells</span>
          </div>
        </div>

        {/* AI Analysis result */}
        {hasSignal && (
          <>
            <RugPanel rug={signal.rug} />
            {signal.agents?.length > 0 && (
              <div className="mt-3">
                <button onClick={() => setExpanded(!expanded)}
                  className="w-full flex items-center justify-between text-[10px] text-[var(--text-dim)] hover:text-[var(--text-primary)] py-1.5 transition-colors">
                  <span className="flex items-center gap-1"><Cpu size={9} /> AI Agents ({signal.agents.length}) · {signal.consensus_signal}</span>
                  {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
                </button>
                {expanded && (
                  <div className="rounded-xl p-2 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.06)]">
                    {signal.agents.map(a => <AgentRow key={a.model} agent={a} />)}
                  </div>
                )}
              </div>
            )}
          </>
        )}

        {/* Analyze button */}
        <button onClick={() => onAnalyze(token)} disabled={analyzing}
          className="mt-3 w-full py-2.5 rounded-xl text-[11px] font-bold transition-all duration-200 disabled:opacity-50 active:scale-95"
          style={{
            background: hasSignal
              ? 'linear-gradient(135deg,rgba(99,102,241,0.12),rgba(139,92,246,0.12))'
              : 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            color: hasSignal ? '#818cf8' : '#fff',
            border: hasSignal ? '1px solid rgba(99,102,241,0.3)' : 'none',
          }}>
          {analyzing
            ? <span className="flex items-center justify-center gap-2"><RefreshCw size={11} className="animate-spin" /> Analyzing...</span>
            : hasSignal ? '🔄 Re-analyze (5cr)' : '🧠 AI Analyze (5cr)'}
        </button>
      </div>
    </div>
  );
}

// ── Stats Panel ───────────────────────────────────────────────────────────────
function StatsPanel({ stats }) {
  if (!stats || stats.total_signals === 0) return (
    <div className="flex flex-col items-center justify-center py-16 text-[var(--text-dim)]">
      <BarChart2 size={32} className="mb-3 opacity-40" />
      <p className="text-sm">No analysis data yet. Start analyzing tokens!</p>
    </div>
  );
  return (
    <div className="space-y-5">
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'Total Signals',  value: stats.total_signals,                    color: '#6366f1' },
          { label: 'BUY EARLY',      value: stats.by_signal?.['BUY EARLY'] || 0,    color: '#10b981' },
          { label: 'DANGER',         value: stats.by_signal?.['DANGER'] || 0,       color: '#ef4444' },
          { label: 'AVOID',          value: stats.by_signal?.['AVOID'] || 0,        color: '#f97316' },
        ].map(k => (
          <div key={k.label} className="rounded-xl p-3 border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)]">
            <div className="text-[9px] text-[var(--text-dim)] uppercase tracking-wide mb-1">{k.label}</div>
            <div className="text-2xl font-black" style={{ color: k.color }}>{k.value}</div>
          </div>
        ))}
      </div>
      {Object.keys(stats.by_signal || {}).length > 0 && (
        <div className="rounded-xl p-4 border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)]">
          <div className="text-xs font-bold mb-3 text-[var(--text-secondary)]">Signal Distribution</div>
          <div className="space-y-2">
            {Object.entries(stats.by_signal).sort((a,b) => b[1]-a[1]).map(([sig, cnt]) => {
              const cfg = SIGNAL_CFG[sig] || {};
              const pct = Math.round((cnt / stats.total_signals) * 100);
              return (
                <div key={sig} className="flex items-center gap-2">
                  <div className="w-28 text-[9px] font-bold" style={{ color: cfg.color || '#94a3b8' }}>
                    {cfg.icon} {sig}
                  </div>
                  <div className="flex-1 h-2 rounded-full bg-[rgba(255,255,255,0.06)] overflow-hidden">
                    <div className="h-2 rounded-full" style={{ width: `${pct}%`, background: cfg.color || '#6366f1' }} />
                  </div>
                  <div className="w-8 text-right text-[9px] text-[var(--text-secondary)] font-bold">{cnt}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}
      {Object.keys(stats.by_chain || {}).length > 0 && (
        <div className="rounded-xl p-4 border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)]">
          <div className="text-xs font-bold mb-3 text-[var(--text-secondary)]">By Chain</div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(stats.by_chain).map(([chain, cnt]) => {
              const c = CHAINS.find(x => x.id === chain) || { color: '#6366f1', label: chain };
              return (
                <div key={chain} className="px-3 py-1.5 rounded-xl text-[10px] font-bold border"
                  style={{ background: `${c.color}15`, color: c.color, borderColor: `${c.color}35` }}>
                  {c.label}: {cnt}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

const REFRESH_INTERVAL = 15; // seconds

const TABS = [
  { id:'Overview',   icon:'fa-solid fa-gauge-high',   label:'Overview' },
  { id:'Signals',    icon:'fa-solid fa-rocket',        label:'Signals' },
  { id:'Technical',  icon:'fa-solid fa-chart-area',    label:'Technical' },
  { id:'Data',       icon:'fa-solid fa-table',          label:'Data' },
  { id:'AI Insight', icon:'fa-solid fa-brain',          label:'AI Insight' },
];

// ── Main View ─────────────────────────────────────────────────────────────────
export default function MemecoinView() {
  const [gasTab, setGasTab] = useState('Overview');
  const [mode, setMode] = useState('manual');
  const [activeTab,     setActiveTab]     = useState('scan');
  const [activeChain,   setActiveChain]   = useState('all');
  const [quickFilter,   setQuickFilter]   = useState('trending'); // trending | new | hot
  const [viewMode,      setViewMode]      = useState('list');     // list | card
  const [tokens,        setTokens]        = useState([]);
  const [loading,       setLoading]       = useState(true);
  const [signals,       setSignals]       = useState({});   // token_address → signal
  const [analyzing,     setAnalyzing]     = useState({});
  const [search,        setSearch]        = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [searching,     setSearching]     = useState(false);
  const [creditsInfo,   setCreditsInfo]   = useState(null);
  const [stats,         setStats]         = useState(null);
  const [error,         setError]         = useState(null);
  const [analyzeError,  setAnalyzeError]  = useState(null);
  const [autoRefresh,   setAutoRefresh]   = useState(true);
  const [countdown,     setCountdown]     = useState(REFRESH_INTERVAL);
  const searchTimer = useRef(null);
  const refreshTimer = useRef(null);
  const countdownTimer = useRef(null);

  const loadTrending = useCallback(async (chain = activeChain) => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`/terminal/memecoin/trending?chain=${chain}&limit=30`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const d = await res.json();
      setTokens(d.tokens || []);
    } catch (e) {
      setError(e.message);
      setTokens([]);
    } finally {
      setLoading(false);
    }
  }, [activeChain]);

  const loadCreditsInfo = useCallback(async () => {
    try {
      const r = await fetch('/web/api/v1/memecoin/credits-info', {
        headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
      });
      if (r.ok) setCreditsInfo(await r.json());
    } catch (_) {}
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const r = await fetch('/terminal/memecoin/stats', {
        headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
      });
      if (r.ok) setStats(await r.json());
    } catch (_) {}
  }, []);

  useEffect(() => { loadTrending(activeChain); }, [activeChain]);
  useEffect(() => { loadCreditsInfo(); }, []);
  useEffect(() => { if (activeTab === 'stats') loadStats(); }, [activeTab]);

  // Auto-refresh every 15s with countdown
  useEffect(() => {
    clearInterval(refreshTimer.current);
    clearInterval(countdownTimer.current);
    if (autoRefresh) {
      setCountdown(REFRESH_INTERVAL);
      refreshTimer.current = setInterval(() => {
        loadTrending(activeChain);
        setCountdown(REFRESH_INTERVAL);
      }, REFRESH_INTERVAL * 1000);
      countdownTimer.current = setInterval(() => {
        setCountdown(c => c > 0 ? c - 1 : REFRESH_INTERVAL);
      }, 1000);
    }
    return () => {
      clearInterval(refreshTimer.current);
      clearInterval(countdownTimer.current);
    };
  }, [autoRefresh, activeChain]);

  const handleSearch = (val) => {
    setSearch(val);
    clearTimeout(searchTimer.current);
    if (!val.trim()) { setSearchResults(null); return; }
    searchTimer.current = setTimeout(async () => {
      setSearching(true);
      try {
        const r = await fetch(`/terminal/memecoin/search?q=${encodeURIComponent(val)}&limit=15`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
        });
        if (r.ok) { const d = await r.json(); setSearchResults(d.tokens || []); }
      } catch (_) {}
      setSearching(false);
    }, 500);
  };

  const handleAnalyze = async (token) => {
    setAnalyzing(a => ({ ...a, [token.token_address]: true }));
    setAnalyzeError(null);
    try {
      const res = await fetch('/web/api/v1/memecoin/signal', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
        body: JSON.stringify({ ...token }),
      });
      if (res.ok) {
        const data = await res.json();
        setSignals(s => ({ ...s, [token.token_address]: data }));
        if (data.credits_remaining !== undefined)
          setCreditsInfo(p => p ? { ...p, credits_balance: data.credits_remaining } : p);
      } else {
        const err = await res.json().catch(() => ({}));
        setAnalyzeError(err.detail || `Error ${res.status}`);
      }
    } catch (e) { setAnalyzeError('Connection error'); }
    setAnalyzing(a => ({ ...a, [token.token_address]: false }));
  };

  const displayTokens = searchResults !== null ? searchResults : tokens;

  return (
    <div className="flex flex-col h-full bg-[var(--bg-primary)] text-[var(--text-primary)]">
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
            <h4>📊 Dexscreener Data</h4>
            <p className="ai-insight-text">Live memecoin data from Dexscreener API — liquidity pools, holder distribution, volume spikes, and smart wallet tracking. Data refreshes every 60 seconds.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">Dexscreener API</span>
              <span className="ai-badge">Solana</span>
              <span className="ai-badge">BSC</span>
              <span className="ai-badge">Base</span>
            </div>
          </div>
        </div>
      )}

      {gasTab === 'AI Insight' && (
        <div className="space-y-4 p-4">
          <div className="ai-insight-card">
            <h4>🧠 Memecoin AI Intelligence</h4>
            <p className="ai-insight-text">AI tracks smart wallet movements, early gem detection, narrative momentum, and rug probability scores. High-risk tokens are flagged automatically.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">Smart Wallet Tracking</span>
              <span className="ai-badge ai-badge--green">Early Gem Detection</span>
              <span className="ai-badge ai-badge--red">Rug Score Active</span>
            </div>
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            {[
              { label:'Pump Probability', value:'Scanning...', icon:'🚀' },
              { label:'Rug Score',        value:'Analyzing...', icon:'💀' },
              { label:'Smart Wallets',    value:'Tracking...', icon:'👛' },
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

      {(gasTab === 'Overview' || gasTab === 'Signals' || gasTab === 'Technical') && (<>
      {/* Mode Tabs */}
      <div className="flex gap-1 p-1 mx-4 mt-3 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)]">
        {[
          { id: 'auto',     label: '🔥 Early Signal', desc: 'Pump Detection' },
          { id: 'manual',   label: '🎯 Scanner',      desc: 'On Demand' },
          { id: 'analysis', label: '☠️ Risk Intel',   desc: 'Rug Check' },
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
        <div className="space-y-3 p-4 flex-1 overflow-y-auto">
          <AutoSignalPanel market="meme" planDepth="essential" />
        </div>
      )}

      {mode === 'analysis' && (
        <div className="space-y-3 p-4 flex-1 overflow-y-auto">
          <MarketAnalysisPanel market="meme" planDepth="essential" />
        </div>
      )}

      {mode === 'manual' && (<>
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-[rgba(255,255,255,0.07)]">
        <div className="flex items-center justify-between mb-1">
          <div>
            <h1 className="text-xl font-black flex items-center gap-2">
              <span className="w-8 h-8 rounded-xl flex items-center justify-center text-base"
                style={{ background: 'linear-gradient(135deg,#9945ff,#f43f5e)' }}>🎰</span>
              Memecoin Signal AI
              <span className="px-2 py-0.5 rounded-full text-[9px] font-black bg-[rgba(244,63,94,0.2)] text-[#f43f5e] border border-[rgba(244,63,94,0.3)]">
                HIGH RISK
              </span>
            </h1>
            <p className="text-xs text-[var(--text-dim)] mt-0.5">
              Live Dexscreener scanner · Anti-rug detection · 4-model AI signal
            </p>
          </div>
          <div className="flex items-center gap-2">
            {creditsInfo && (
              <div className="text-right text-[9px]">
                {creditsInfo.has_access ? (
                  <><div className="text-[#10b981] font-bold">{creditsInfo.credits_balance} cr</div>
                    <div className="text-[var(--text-dim)]">5cr/signal</div></>
                ) : (
                  <div className="px-2 py-1 rounded-lg text-[9px] font-bold bg-[rgba(244,63,94,0.15)] text-[#f43f5e] border border-[rgba(244,63,94,0.3)]">
                    ⚠️ Premium+
                  </div>
                )}
              </div>
            )}
            {/* View mode toggle */}
            <div className="flex border border-[rgba(255,255,255,0.1)] rounded-lg overflow-hidden">
              <button onClick={() => setViewMode('list')}
                className={`px-2 py-1.5 text-[9px] font-bold transition-colors ${viewMode === 'list' ? 'bg-[rgba(153,69,255,0.25)] text-[#b47fff]' : 'text-[var(--text-dim)]'}`}>
                ≡ List
              </button>
              <button onClick={() => setViewMode('card')}
                className={`px-2 py-1.5 text-[9px] font-bold transition-colors ${viewMode === 'card' ? 'bg-[rgba(153,69,255,0.25)] text-[#b47fff]' : 'text-[var(--text-dim)]'}`}>
                ⊞ Card
              </button>
            </div>
            <button onClick={() => setAutoRefresh(a => !a)}
              className={`px-2 py-1.5 rounded-lg border text-[9px] font-bold transition-colors ${autoRefresh ? 'border-[rgba(16,185,129,0.4)] text-[#10b981] bg-[rgba(16,185,129,0.1)]' : 'border-[rgba(255,255,255,0.1)] text-[var(--text-dim)]'}`}>
              {autoRefresh ? `⟳ ${countdown}s` : 'AUTO'}
            </button>
            <button onClick={() => { loadTrending(activeChain); setCountdown(REFRESH_INTERVAL); }}
              className="p-2 rounded-lg border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.05)] transition-colors">
              <RefreshCw size={13} className={loading ? 'animate-spin text-[#6366f1]' : 'text-[var(--text-dim)]'} />
            </button>
          </div>
        </div>
        {/* Tabs */}
        <div className="flex gap-1 mt-3">
          {[{ id:'scan', label:'🔍 Scanner' }, { id:'stats', label:'📊 Stats' }].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === t.id
                  ? 'bg-[rgba(153,69,255,0.18)] text-[#b47fff] border border-[rgba(153,69,255,0.3)]'
                  : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
              }`}>{t.label}</button>
          ))}
        </div>
      </div>

      {/* Error banner */}
      {analyzeError && (
        <div className="mx-6 mt-3 px-4 py-2.5 rounded-xl text-xs font-bold flex items-center justify-between"
          style={{ background: 'rgba(244,63,94,0.12)', color: '#f43f5e', border: '1px solid rgba(244,63,94,0.3)' }}>
          <span>⚠️ {analyzeError}</span>
          <button onClick={() => setAnalyzeError(null)} className="opacity-60 hover:opacity-100 ml-3 text-lg leading-none">×</button>
        </div>
      )}

      {activeTab === 'scan' && (
        <>
          {/* Filters */}
          <div className="px-6 py-3 border-b border-[rgba(255,255,255,0.05)] space-y-2.5">
            {/* Search */}
            <div className="relative">
              <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-dim)]" />
              <input type="text" value={search} onChange={e => handleSearch(e.target.value)}
                placeholder="Search token: PEPE, DOGE, BONK..."
                className="w-full pl-8 pr-3 py-2 rounded-xl text-xs bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.08)] focus:border-[rgba(153,69,255,0.5)] focus:outline-none placeholder-[var(--text-dim)] text-[var(--text-primary)]" />
              {searching && <RefreshCw size={11} className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin text-[#9945ff]" />}
            </div>
            {/* Chain filter */}
            <div className="flex gap-2 overflow-x-auto scrollbar-none pb-0.5">
              {CHAINS.map(ch => (
                <button key={ch.id} onClick={() => { setActiveChain(ch.id); setSearchResults(null); setSearch(''); }}
                  className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-[10px] font-bold whitespace-nowrap flex-shrink-0 transition-all"
                  style={{
                    background: activeChain === ch.id ? `${ch.color}1a` : 'rgba(255,255,255,0.04)',
                    color: activeChain === ch.id ? ch.color : 'var(--text-dim)',
                    border: activeChain === ch.id ? `1px solid ${ch.color}45` : '1px solid rgba(255,255,255,0.06)',
                  }}>
                  {ch.label}
                </button>
              ))}
            </div>
          </div>

          {/* Disclaimer */}
          <div className="mx-6 mt-3 px-3 py-2 rounded-xl text-[9px] flex items-start gap-2"
            style={{ background: 'rgba(244,63,94,0.08)', border: '1px solid rgba(244,63,94,0.2)', color: '#fda4af' }}>
            <AlertTriangle size={10} className="flex-shrink-0 mt-0.5" />
            <span><b>HIGH RISK WARNING:</b> Memecoin trading is extremely risky. 90% of tokens are scams. Only use with money you can afford to lose completely. This is NOT financial advice.</span>
          </div>

          {/* Quick filter bar */}
          <div className="px-6 py-2 border-b border-[rgba(255,255,255,0.05)] flex items-center gap-2">
            {[
              { id: 'trending', label: '🔥 Trending' },
              { id: 'new',      label: '🆕 New Pairs' },
              { id: 'hot',      label: '⚡ Hot (High Vol)' },
            ].map(f => (
              <button key={f.id} onClick={() => setQuickFilter(f.id)}
                className={`px-3 py-1 rounded-lg text-[10px] font-bold transition-all ${
                  quickFilter === f.id
                    ? 'bg-[rgba(153,69,255,0.2)] text-[#b47fff] border border-[rgba(153,69,255,0.3)]'
                    : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                }`}>
                {f.label}
              </button>
            ))}
            <div className="ml-auto flex items-center gap-1.5 text-[9px] text-[var(--text-dim)]">
              <span className="w-1.5 h-1.5 rounded-full bg-[#10b981] animate-pulse" />
              <span>Live · {displayTokens.length} tokens</span>
            </div>
          </div>

          {/* Token list/grid */}
          <div className="flex-1 overflow-y-auto scrollbar-thin">
            {loading ? (
              <div className="p-4 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                {Array.from({length:6}).map((_,i) => (
                  <div key={i} className="rounded-2xl border border-[rgba(255,255,255,0.06)] bg-[rgba(255,255,255,0.02)] h-64 animate-pulse" />
                ))}
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center py-16 text-[var(--text-dim)]">
                <AlertCircle size={28} className="mb-3 text-[#f43f5e]" />
                <p className="text-sm font-bold text-[#f43f5e]">Failed to load tokens</p>
                <p className="text-xs mt-1">{error}</p>
                <button onClick={() => loadTrending(activeChain)}
                  className="mt-4 px-4 py-2 rounded-xl text-xs font-bold bg-[rgba(153,69,255,0.2)] text-[#b47fff] border border-[rgba(153,69,255,0.3)]">
                  Retry
                </button>
              </div>
            ) : displayTokens.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-16 text-[var(--text-dim)]">
                <Zap size={28} className="mb-3 opacity-40" />
                <p className="text-sm">No tokens found</p>
                <p className="text-xs mt-1">Try a different chain or search term</p>
              </div>
            ) : viewMode === 'list' ? (
              /* ── Dexscreener-style list view ─────────────────────────── */
              <div className="overflow-x-auto">
                <table className="w-full border-collapse min-w-[700px]">
                  <thead>
                    <tr className="border-b border-[rgba(255,255,255,0.06)] bg-[rgba(255,255,255,0.02)] sticky top-0 z-10">
                      <th className="px-3 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] w-8">#</th>
                      <th className="px-2 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Token</th>
                      <th className="px-2 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] hidden sm:table-cell">Chain</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Price</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">5m</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">1h</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] hidden md:table-cell">Liquidity</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] hidden lg:table-cell">Vol 1h</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] hidden lg:table-cell">Mcap</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] hidden xl:table-cell">Age</th>
                      <th className="px-2 py-2.5 text-center text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Signal</th>
                      <th className="px-2 py-2.5 text-right text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Score</th>
                      <th className="px-2 py-2.5 text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">AI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {displayTokens.map((t, i) => (
                      <TokenRowList
                        key={t.token_address}
                        token={t}
                        rank={i + 1}
                        onAnalyze={handleAnalyze}
                        analyzing={!!analyzing[t.token_address]}
                        signal={signals[t.token_address] || null}
                      />
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              /* ── Card grid view ───────────────────────────────────────── */
              <div className="p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {displayTokens.map(t => (
                    <TokenCard
                      key={t.token_address}
                      token={t}
                      onAnalyze={handleAnalyze}
                      analyzing={!!analyzing[t.token_address]}
                      signal={signals[t.token_address] || null}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </>
      )}

      {activeTab === 'stats' && (
        <div className="flex-1 overflow-y-auto p-5 scrollbar-thin">
          <StatsPanel stats={stats} />
        </div>
      )}
      </>)}
      </>)}
    </div>
  );
}
