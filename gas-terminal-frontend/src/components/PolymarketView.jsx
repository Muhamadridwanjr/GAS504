import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  TrendingUp, TrendingDown, RefreshCw, Search,
  Brain, Zap, BarChart2, Clock, Target, ChevronDown, ChevronUp,
  Activity, AlertCircle, Globe, Bitcoin, DollarSign, Layers,
  Star, Award, Cpu, Flame
} from 'lucide-react';
import AutoSignalPanel from './AutoSignalPanel';
import MarketAnalysisPanel from './MarketAnalysisPanel';

const MODELS = ['claude', 'gpt', 'gemini', 'grok'];
const MODEL_META = {
  claude:  { label: 'Claude',  color: '#f59e0b', weight: 1.3, specialty: 'Accuracy' },
  gpt:     { label: 'GPT',     color: '#10b981', weight: 1.2, specialty: 'Context'  },
  gemini:  { label: 'Gemini',  color: '#3b82f6', weight: 1.0, specialty: 'Structure'},
  grok:    { label: 'Grok',    color: '#f43f5e', weight: 0.8, specialty: 'Momentum' },
};

const CATEGORIES = [
  { id: 'all',       label: 'All Markets',    icon: Globe,      color: '#6366f1' },
  { id: 'crypto',    label: 'Crypto',          icon: Bitcoin,    color: '#f59e0b' },
  { id: 'forex',     label: 'Forex & Gold',    icon: DollarSign, color: '#10b981' },
  { id: 'macro',     label: 'Macro',           icon: TrendingUp, color: '#3b82f6' },
  { id: 'intraday',  label: 'Intraday',        icon: Zap,        color: '#f43f5e' },
  { id: 'technical', label: 'Technical/SMC',   icon: Layers,     color: '#8b5cf6' },
];

const SIGNAL_CFG = {
  'STRONG BUY YES': { bg: 'rgba(16,185,129,0.2)',  color: '#10b981', border: 'rgba(16,185,129,0.4)', icon: '🔥' },
  'BUY YES':        { bg: 'rgba(16,185,129,0.12)', color: '#34d399', border: 'rgba(16,185,129,0.3)', icon: '✅' },
  'WEAK YES':       { bg: 'rgba(16,185,129,0.07)', color: '#6ee7b7', border: 'rgba(16,185,129,0.2)', icon: '🟢' },
  'NO TRADE':       { bg: 'rgba(100,116,139,0.1)', color: '#94a3b8', border: 'rgba(100,116,139,0.2)',icon: '⚪' },
  'WEAK NO':        { bg: 'rgba(244,63,94,0.07)',  color: '#fda4af', border: 'rgba(244,63,94,0.2)',  icon: '🔴' },
  'BUY NO':         { bg: 'rgba(244,63,94,0.12)',  color: '#fb7185', border: 'rgba(244,63,94,0.3)',  icon: '❌' },
  'STRONG BUY NO':  { bg: 'rgba(244,63,94,0.2)',   color: '#f43f5e', border: 'rgba(244,63,94,0.4)',  icon: '💥' },
};

const EVENT_TYPE_CFG = {
  price_target: { label: 'Price Target', color: '#f59e0b' },
  pct_move:     { label: '% Move',       color: '#10b981' },
  structure:    { label: 'Structure',    color: '#8b5cf6' },
  time_based:   { label: 'Time-Based',   color: '#3b82f6' },
};

// ── Probability Bar ───────────────────────────────────────────────────────────
function ProbBar({ yes, no, compact = false }) {
  const h = compact ? 'h-1.5' : 'h-2.5';
  return (
    <div className={`w-full ${h} rounded-full overflow-hidden bg-[rgba(255,255,255,0.06)] flex gap-0.5`}>
      <div className={`${h} transition-all duration-700`}
        style={{ width: `${yes}%`, background: 'linear-gradient(90deg,#059669,#10b981)' }} />
      <div className={`${h} transition-all duration-700`}
        style={{ width: `${no}%`, background: 'linear-gradient(90deg,#e11d48,#f43f5e)' }} />
    </div>
  );
}

// ── Signal Badge ──────────────────────────────────────────────────────────────
function SignalBadge({ signal, size = 'sm' }) {
  const cfg = SIGNAL_CFG[signal] || SIGNAL_CFG['NO TRADE'];
  const px = size === 'xs' ? 'px-1.5 py-0.5 text-[9px]' : size === 'lg' ? 'px-3 py-1 text-xs' : 'px-2 py-0.5 text-[10px]';
  return (
    <span className={`inline-flex items-center gap-1 rounded-full font-black ${px} whitespace-nowrap`}
      style={{ background: cfg.bg, color: cfg.color, border: `1px solid ${cfg.border}` }}>
      {cfg.icon} {signal}
    </span>
  );
}

// ── Confidence Arc SVG ────────────────────────────────────────────────────────
function ConfArc({ pct, color = '#10b981', size = 48 }) {
  const r = (size - 10) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.07)" strokeWidth="5" />
      <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="5"
        strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
        style={{ transition: 'stroke-dasharray 0.8s ease', filter: `drop-shadow(0 0 4px ${color}80)` }} />
      <text x={size/2} y={size/2} textAnchor="middle" dominantBaseline="middle"
        style={{ transform: `rotate(90deg) translate(0,0)`, transformOrigin: `${size/2}px ${size/2}px`,
          fill: color, fontSize: size > 44 ? 11 : 9, fontWeight: 800 }}>
        {pct}%
      </text>
    </svg>
  );
}

// ── Source Badge ──────────────────────────────────────────────────────────────
function SourceBadge({ source }) {
  return source === 'polymarket' ? (
    <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-[rgba(99,102,241,0.15)] text-[#818cf8] border border-[rgba(99,102,241,0.2)]">
      Polymarket
    </span>
  ) : (
    <span className="px-1.5 py-0.5 rounded text-[8px] font-bold bg-[rgba(16,185,129,0.15)] text-[#34d399] border border-[rgba(16,185,129,0.2)]">
      GAS Generated
    </span>
  );
}

// ── Agent Weight Bar ──────────────────────────────────────────────────────────
function AgentRow({ agent, maxWeight = 1.3 }) {
  const meta = MODEL_META[agent.model] || { label: agent.model, color: '#6366f1', weight: 1.0, specialty: '' };
  const barPct = (meta.weight / maxWeight) * 100;
  return (
    <div className="py-2 border-b border-[rgba(255,255,255,0.05)] last:border-0">
      <div className="flex items-center gap-2 mb-1">
        <div className="w-12 text-[10px] font-black" style={{ color: meta.color }}>{meta.label}</div>
        <div className="text-[8px] text-[var(--text-dim)] flex-1">{meta.specialty} · w{meta.weight}</div>
        <SignalBadge signal={agent.signal_strength || agent.action} size="xs" />
        <ConfArc pct={Math.round(agent.confidence)} color={meta.color} size={34} />
      </div>
      <div className="flex items-center gap-2">
        <div className="flex-1">
          <ProbBar yes={agent.yes} no={agent.no} compact />
          <div className="flex justify-between text-[9px] mt-0.5">
            <span style={{ color: '#10b981' }} className="font-bold">YES {agent.yes}%</span>
            <span style={{ color: '#f43f5e' }} className="font-bold">NO {agent.no}%</span>
          </div>
        </div>
        {/* Weight indicator */}
        <div className="w-12">
          <div className="h-1 rounded-full bg-[rgba(255,255,255,0.06)] overflow-hidden">
            <div className="h-1 rounded-full" style={{ width: `${barPct}%`, background: meta.color }} />
          </div>
          <div className="text-[8px] text-center mt-0.5" style={{ color: meta.color }}>×{meta.weight}</div>
        </div>
      </div>
    </div>
  );
}

// ── Market Card ───────────────────────────────────────────────────────────────
function MarketCard({ market, onPredict, predicting, prediction, compact = false }) {
  const [expanded, setExpanded] = useState(false);
  const catCfg = CATEGORIES.find(c => c.id === market.category) || CATEGORIES[0];
  const CatIcon = catCfg.icon;
  const etCfg = EVENT_TYPE_CFG[market.event_type] || null;
  const hasSignal = !!prediction?.signal;
  const consensus = prediction?.consensus;
  const sigCfg = consensus ? (SIGNAL_CFG[consensus.signal_strength || consensus.action] || SIGNAL_CFG['NO TRADE']) : null;

  return (
    <div className={`rounded-2xl border transition-all duration-200 overflow-hidden
      ${hasSignal && sigCfg
        ? `border-[${sigCfg.border}] bg-[rgba(255,255,255,0.04)]`
        : 'border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.02)] hover:border-[rgba(255,255,255,0.14)] hover:bg-[rgba(255,255,255,0.04)]'
      }`}
      style={hasSignal && sigCfg ? { borderColor: sigCfg.border } : {}}>
      <div className="p-4">
        {/* Top row: category + source + event type */}
        <div className="flex items-center gap-1.5 mb-2 flex-wrap">
          <div className="w-5 h-5 rounded-md flex items-center justify-center"
            style={{ background: `${catCfg.color}18`, border: `1px solid ${catCfg.color}35` }}>
            <CatIcon size={10} style={{ color: catCfg.color }} />
          </div>
          <span className="text-[9px] font-bold uppercase tracking-wide" style={{ color: catCfg.color }}>
            {catCfg.label}
          </span>
          {market.pair && <span className="text-[9px] text-[var(--text-dim)]">· {market.pair}</span>}
          <div className="ml-auto flex items-center gap-1">
            {etCfg && (
              <span className="px-1.5 py-0.5 rounded text-[8px] font-bold"
                style={{ background: `${etCfg.color}15`, color: etCfg.color, border: `1px solid ${etCfg.color}30` }}>
                {etCfg.label}
              </span>
            )}
            <SourceBadge source={market.source || 'gas'} />
          </div>
        </div>

        {/* Question */}
        <p className="text-[12px] font-semibold text-[var(--text-primary)] leading-snug mb-3">
          {market.question}
        </p>

        {/* Market price bar */}
        <div className="mb-3">
          <div className="flex justify-between text-[10px] mb-1">
            <span className="font-black text-[#10b981]">YES {Math.round(market.yes_price * 100)}%</span>
            <span className="font-black text-[#f43f5e]">NO {Math.round(market.no_price * 100)}%</span>
          </div>
          <ProbBar yes={market.yes_price * 100} no={market.no_price * 100} />
          <div className="flex items-center gap-3 mt-1.5 text-[9px] text-[var(--text-dim)]">
            {market.volume > 0 && (
              <span className="flex items-center gap-1">
                <BarChart2 size={8} />
                ${market.volume > 1e6 ? `${(market.volume/1e6).toFixed(1)}M` : market.volume > 1e3 ? `${(market.volume/1e3).toFixed(0)}K` : market.volume.toFixed(0)}
              </span>
            )}
            {market.end_date && (
              <span className="flex items-center gap-1">
                <Clock size={8} />
                {new Date(market.end_date).toLocaleDateString('en', { month:'short', day:'numeric' })}
              </span>
            )}
          </div>
        </div>

        {/* GAS Signal result */}
        {hasSignal && prediction.signal && (
          <div className="rounded-xl p-3 mb-2.5 border"
            style={{ background: 'rgba(99,102,241,0.07)', borderColor: 'rgba(99,102,241,0.22)' }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold text-[#818cf8] flex items-center gap-1">
                <Brain size={10} /> GAS Signal
              </span>
              <SignalBadge signal={prediction.signal.signal_strength || prediction.signal.action} />
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <ProbBar yes={prediction.signal.yes} no={prediction.signal.no} />
                <div className="flex justify-between text-[9px] mt-1">
                  <span className="text-[#10b981] font-bold">YES {prediction.signal.yes}%</span>
                  <span className="text-[#f43f5e] font-bold">NO {prediction.signal.no}%</span>
                </div>
              </div>
              <ConfArc pct={Math.round(prediction.signal.confidence)} color="#818cf8" size={42} />
            </div>
            {prediction.signal.reasoning && (
              <p className="text-[9px] text-[var(--text-dim)] mt-2 leading-relaxed">
                "{prediction.signal.reasoning}"
              </p>
            )}
          </div>
        )}

        {/* Consensus */}
        {consensus && (
          <div className="rounded-xl p-3 mb-2.5 border"
            style={{ background: sigCfg ? sigCfg.bg : 'rgba(16,185,129,0.06)', borderColor: sigCfg ? sigCfg.border : 'rgba(16,185,129,0.2)' }}>
            <div className="flex items-center justify-between mb-2">
              <span className="text-[10px] font-bold flex items-center gap-1"
                style={{ color: sigCfg ? sigCfg.color : '#10b981' }}>
                <Target size={10} /> Weighted Consensus
              </span>
              <SignalBadge signal={consensus.signal_strength || consensus.action} size="sm" />
            </div>
            <div className="flex items-center gap-3">
              <div className="flex-1">
                <ProbBar yes={consensus.yes} no={consensus.no} />
                <div className="flex justify-between text-[9px] mt-1 text-[var(--text-dim)]">
                  <span>YES {consensus.majority_yes} model · NO {consensus.majority_no} model</span>
                  <span className="text-white font-bold">{consensus.confidence}% conf</span>
                </div>
              </div>
              <ConfArc pct={Math.round(consensus.confidence)}
                color={sigCfg ? sigCfg.color : '#10b981'} size={42} />
            </div>
          </div>
        )}

        {/* Agent breakdown toggle */}
        {prediction?.agents?.length > 0 && (
          <>
            <button onClick={() => setExpanded(!expanded)}
              className="w-full flex items-center justify-between text-[10px] text-[var(--text-dim)] hover:text-[var(--text-primary)] py-1.5 transition-colors">
              <span className="flex items-center gap-1"><Cpu size={9} /> {prediction.agents.length} AI Agents</span>
              {expanded ? <ChevronUp size={10} /> : <ChevronDown size={10} />}
            </button>
            {expanded && (
              <div className="mt-1 rounded-xl p-2 bg-[rgba(255,255,255,0.03)] border border-[rgba(255,255,255,0.06)]">
                {prediction.agents.map(a => <AgentRow key={a.model} agent={a} />)}
              </div>
            )}
          </>
        )}

        {/* Predict button */}
        <button onClick={() => onPredict(market)} disabled={predicting}
          className="mt-3 w-full py-2.5 rounded-xl text-[11px] font-bold transition-all duration-200 disabled:opacity-50 active:scale-95"
          style={{
            background: hasSignal
              ? 'linear-gradient(135deg,rgba(99,102,241,0.12),rgba(139,92,246,0.12))'
              : 'linear-gradient(135deg,#6366f1,#8b5cf6)',
            color: hasSignal ? '#818cf8' : '#fff',
            border: hasSignal ? '1px solid rgba(99,102,241,0.3)' : 'none',
          }}>
          {predicting
            ? <span className="flex items-center justify-center gap-2"><RefreshCw size={11} className="animate-spin" /> Analyzing...</span>
            : hasSignal ? '🔄 Re-analyze' : '🧠 GAS Predict'}
        </button>
      </div>
    </div>
  );
}

// ── Top 5 Daily Picks ─────────────────────────────────────────────────────────
function Top5Panel({ onPredict, predicting, predictions }) {
  const [picks, setPicks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/terminal/polymarket/top5', {
      headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
    })
      .then(r => r.ok ? r.json() : null)
      .then(d => { if (d) setPicks(d.picks || []); })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <div className="flex gap-3 overflow-x-auto pb-2">
      {Array.from({length:5}).map((_,i) => (
        <div key={i} className="flex-shrink-0 w-56 h-28 rounded-xl bg-[rgba(255,255,255,0.04)] animate-pulse border border-[rgba(255,255,255,0.06)]" />
      ))}
    </div>
  );

  if (!picks.length) return null;

  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <Flame size={14} className="text-[#f59e0b]" />
        <span className="text-xs font-black text-[var(--text-primary)]">Today's Top Picks</span>
        <span className="text-[9px] text-[var(--text-dim)]">· 5 highest-confidence events</span>
      </div>
      <div className="flex gap-3 overflow-x-auto pb-2 scrollbar-none">
        {picks.map((p, i) => {
          const pred = predictions[p.event_id];
          const consensus = pred?.consensus;
          const sigCfg = consensus ? (SIGNAL_CFG[consensus.signal_strength || consensus.action] || SIGNAL_CFG['NO TRADE']) : null;
          return (
            <div key={p.event_id}
              className="flex-shrink-0 w-60 rounded-xl p-3 border transition-all"
              style={{
                background: sigCfg ? sigCfg.bg : 'rgba(255,255,255,0.04)',
                borderColor: sigCfg ? sigCfg.border : 'rgba(255,255,255,0.1)',
              }}>
              <div className="flex items-center gap-1.5 mb-1.5">
                <span className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-black bg-[rgba(99,102,241,0.2)] text-[#818cf8]">
                  {i + 1}
                </span>
                <span className="text-[9px] text-[var(--text-dim)]">{p.pair || p.category}</span>
                {consensus && (
                  <div className="ml-auto"><SignalBadge signal={consensus.signal_strength || consensus.action} size="xs" /></div>
                )}
              </div>
              <p className="text-[11px] font-semibold text-[var(--text-primary)] line-clamp-2 mb-2 leading-snug">
                {p.question}
              </p>
              <ProbBar yes={p.yes_price * 100} no={p.no_price * 100} compact />
              <div className="flex justify-between text-[9px] mt-1 mb-2">
                <span className="text-[#10b981] font-bold">YES {Math.round(p.yes_price*100)}%</span>
                <span className="text-[#f43f5e] font-bold">NO {Math.round(p.no_price*100)}%</span>
              </div>
              <button onClick={() => onPredict(p)} disabled={predicting[p.event_id]}
                className="w-full py-1.5 rounded-lg text-[10px] font-bold transition-colors"
                style={{
                  background: pred ? 'rgba(99,102,241,0.15)' : 'linear-gradient(135deg,#6366f1,#8b5cf6)',
                  color: pred ? '#818cf8' : '#fff',
                  border: pred ? '1px solid rgba(99,102,241,0.3)' : 'none',
                }}>
                {predicting[p.event_id] ? '...' : pred ? '🔄 Re-analyze' : '🧠 Predict'}
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}

// ── Analytics Panel ───────────────────────────────────────────────────────────
function AnalyticsPanel({ analytics, history }) {
  if (!analytics || analytics.total_predictions === 0) return (
    <div className="flex flex-col items-center justify-center py-16 text-[var(--text-dim)]">
      <BarChart2 size={32} className="mb-3 opacity-40" />
      <p className="text-sm">No prediction data yet.</p>
      <p className="text-xs mt-1">Run predictions to see analytics here.</p>
    </div>
  );

  return (
    <div className="space-y-5">
      {/* KPIs */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        {[
          { label: 'Total Predictions', value: analytics.total_predictions,          icon: Target,      color: '#6366f1' },
          { label: 'Avg Confidence',    value: `${analytics.recent_confidence_avg}%`, icon: Activity,    color: '#10b981' },
          { label: 'Strong Buy YES',    value: analytics.by_signal_strength?.['STRONG BUY YES'] || 0, icon: Flame, color: '#f59e0b' },
          { label: 'No Trade',         value: analytics.by_action?.['NO TRADE'] || 0, icon: Award,      color: '#94a3b8' },
        ].map(k => {
          const Icon = k.icon;
          return (
            <div key={k.label} className="rounded-xl p-3 border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)]">
              <div className="flex items-center gap-2 mb-1">
                <Icon size={12} style={{ color: k.color }} />
                <span className="text-[9px] text-[var(--text-dim)] uppercase tracking-wide">{k.label}</span>
              </div>
              <div className="text-2xl font-black" style={{ color: k.color }}>{k.value}</div>
            </div>
          );
        })}
      </div>

      {/* Signal strength breakdown */}
      {Object.keys(analytics.by_signal_strength || {}).length > 0 && (
        <div className="rounded-xl p-4 border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)]">
          <div className="text-xs font-bold mb-3 text-[var(--text-secondary)]">Signal Distribution</div>
          <div className="space-y-2">
            {Object.entries(analytics.by_signal_strength).sort((a,b) => b[1]-a[1]).map(([sig, cnt]) => {
              const cfg = SIGNAL_CFG[sig] || SIGNAL_CFG['NO TRADE'];
              const pct = Math.round((cnt / analytics.total_predictions) * 100);
              return (
                <div key={sig} className="flex items-center gap-2">
                  <div className="w-28 text-[9px] font-bold" style={{ color: cfg.color }}>{cfg.icon} {sig}</div>
                  <div className="flex-1 h-2 rounded-full bg-[rgba(255,255,255,0.06)] overflow-hidden">
                    <div className="h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%`, background: cfg.color }} />
                  </div>
                  <div className="w-6 text-right text-[9px] font-bold text-[var(--text-secondary)]">{cnt}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Category breakdown */}
      {Object.keys(analytics.by_category || {}).length > 0 && (
        <div className="rounded-xl p-4 border border-[rgba(255,255,255,0.08)] bg-[rgba(255,255,255,0.03)]">
          <div className="text-xs font-bold mb-3 text-[var(--text-secondary)]">By Category</div>
          <div className="space-y-2">
            {Object.entries(analytics.by_category).sort((a,b) => b[1]-a[1]).map(([cat, count]) => {
              const catCfg = CATEGORIES.find(c => c.id === cat) || { color: '#6366f1', label: cat };
              const pct = Math.round((count / analytics.total_predictions) * 100);
              return (
                <div key={cat} className="flex items-center gap-2">
                  <div className="w-24 text-[9px] text-[var(--text-dim)] capitalize">{catCfg.label || cat}</div>
                  <div className="flex-1 h-2 rounded-full bg-[rgba(255,255,255,0.06)] overflow-hidden">
                    <div className="h-2 rounded-full" style={{ width: `${pct}%`, background: catCfg.color }} />
                  </div>
                  <div className="w-6 text-right text-[9px] font-bold text-[var(--text-secondary)]">{count}</div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* History table */}
      {history.length > 0 && (
        <div className="rounded-xl border border-[rgba(255,255,255,0.08)] overflow-hidden">
          <div className="px-4 py-2.5 border-b border-[rgba(255,255,255,0.08)] text-xs font-bold text-[var(--text-secondary)]">
            Recent Predictions
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-[10px]">
              <thead>
                <tr className="border-b border-[rgba(255,255,255,0.06)]">
                  {['Question','Pair','Signal','YES%','Confidence','Time'].map(h => (
                    <th key={h} className="px-3 py-2 text-left font-bold text-[var(--text-dim)] whitespace-nowrap">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {history.slice(0,15).map((h, i) => (
                  <tr key={i} className="border-b border-[rgba(255,255,255,0.04)] hover:bg-[rgba(255,255,255,0.02)]">
                    <td className="px-3 py-2 max-w-[180px] truncate text-[var(--text-primary)]">{h.question}</td>
                    <td className="px-3 py-2 text-[var(--text-dim)]">{h.pair || '–'}</td>
                    <td className="px-3 py-2"><SignalBadge signal={h.signal_strength || h.action} size="xs" /></td>
                    <td className="px-3 py-2 font-bold" style={{ color: h.yes >= 60 ? '#10b981' : h.yes <= 40 ? '#f43f5e' : '#94a3b8' }}>{h.yes}%</td>
                    <td className="px-3 py-2 text-[var(--text-secondary)]">{h.confidence}%</td>
                    <td className="px-3 py-2 text-[var(--text-dim)]">{new Date(h.timestamp).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}

const TABS = [
  { id:'Overview',   icon:'fa-solid fa-gauge-high',      label:'Overview' },
  { id:'Signals',    icon:'fa-solid fa-network-wired',    label:'Signals' },
  { id:'Technical',  icon:'fa-solid fa-chart-area',       label:'Technical' },
  { id:'Data',       icon:'fa-solid fa-table',             label:'Data' },
  { id:'AI Insight', icon:'fa-solid fa-brain',             label:'AI Insight' },
];

// ── Main View ─────────────────────────────────────────────────────────────────
export default function PolymarketView() {
  const [gasTab, setGasTab] = useState('Overview');
  const [mode, setMode] = useState('manual');
  const [activeTab, setActiveTab] = useState('markets');
  const [activeCategory, setActiveCategory] = useState('all');
  const [markets, setMarkets] = useState([]);
  const [loadingMarkets, setLoadingMarkets] = useState(true);
  const [search, setSearch] = useState('');
  const [predictions, setPredictions] = useState({});
  const [predicting, setPredicting] = useState({});
  const [analytics, setAnalytics] = useState(null);
  const [history, setHistory] = useState([]);
  const [error, setError] = useState(null);
  const [sources, setSources] = useState({ polymarket: 0, gas_generated: 0 });
  const [creditsInfo, setCreditsInfo] = useState(null); // {has_access, credits_balance, credit_costs}
  const [predictError, setPredictError] = useState(null);
  const searchTimer = useRef(null);

  const loadMarkets = useCallback(async (category = activeCategory, q = search) => {
    setLoadingMarkets(true);
    setError(null);
    try {
      const params = new URLSearchParams({ category, limit: 40 });
      if (q) params.set('search', q);
      const res = await fetch(`/terminal/polymarket/markets?${params}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setMarkets(data.markets || []);
      setSources(data.sources || { polymarket: 0, gas_generated: 0 });
    } catch (e) {
      setError(e.message);
      setMarkets([]);
    } finally {
      setLoadingMarkets(false);
    }
  }, [activeCategory, search]);

  const loadAnalytics = useCallback(async () => {
    try {
      const [aRes, hRes] = await Promise.all([
        fetch('/terminal/polymarket/analytics', { headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` } }),
        fetch('/terminal/polymarket/history?limit=20', { headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` } }),
      ]);
      if (aRes.ok) setAnalytics(await aRes.json());
      if (hRes.ok) { const d = await hRes.json(); setHistory(d.history || []); }
    } catch (_) {}
  }, []);

  // Load credits info on mount
  useEffect(() => {
    fetch('/web/api/v1/polymarket/credits-info', {
      headers: { Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
    }).then(r => r.ok ? r.json() : null).then(d => { if (d) setCreditsInfo(d); }).catch(() => {});
  }, []);

  useEffect(() => { loadMarkets(activeCategory, ''); }, [activeCategory]);
  useEffect(() => { if (activeTab === 'analytics') loadAnalytics(); }, [activeTab]);

  const handleSearch = (val) => {
    setSearch(val);
    clearTimeout(searchTimer.current);
    searchTimer.current = setTimeout(() => loadMarkets(activeCategory, val), 500);
  };

  const handlePredict = async (market) => {
    setPredicting(p => ({ ...p, [market.event_id]: true }));
    setPredictError(null);
    try {
      // Route through web-backend for credit deduction + plan gate
      const res = await fetch('/web/api/v1/polymarket/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${localStorage.getItem('gas-token')}` },
        body: JSON.stringify({
          event_id: market.event_id,
          question: market.question,
          category: market.category,
          yes_price: market.yes_price,
          no_price: market.no_price,
          pair: market.pair,
          models: MODELS,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setPredictions(p => ({ ...p, [market.event_id]: data }));
        // Update credits balance
        if (data.credits_remaining !== undefined) {
          setCreditsInfo(prev => prev ? { ...prev, credits_balance: data.credits_remaining } : prev);
        }
      } else {
        const err = await res.json().catch(() => ({}));
        setPredictError(err.detail || `Error ${res.status}`);
      }
    } catch (e) {
      setPredictError('Connection error');
    }
    setPredicting(p => ({ ...p, [market.event_id]: false }));
  };

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
            <h4>📊 Gamma API Data</h4>
            <p className="ai-insight-text">Live prediction market data from Gamma/Polymarket API — market probabilities, trade activity, orderbook (CLOB), and volume analysis.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">Gamma API Live</span>
              <span className="ai-badge">CLOB Orderbook</span>
              <span className="ai-badge">Trade Activity</span>
            </div>
          </div>
        </div>
      )}

      {gasTab === 'AI Insight' && (
        <div className="space-y-4 p-4">
          <div className="ai-insight-card">
            <h4>🧠 Prediction Market AI</h4>
            <p className="ai-insight-text">Multi-AI voting system analyzes crowd sentiment, odds movement, and edge detection to generate YES/NO signals with probability scoring.</p>
            <div className="ai-badge-row">
              <span className="ai-badge ai-badge--gold">Multi-AI Voting</span>
              <span className="ai-badge ai-badge--green">Edge Detection</span>
              <span className="ai-badge">Crowd Sentiment</span>
            </div>
          </div>
        </div>
      )}

      {(gasTab === 'Overview' || gasTab === 'Signals' || gasTab === 'Technical') && (<>
      {/* Mode Tabs */}
      <div className="flex gap-1 p-1 mx-4 mt-3 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)]">
        {[
          { id: 'auto',     label: '🔮 AI Predict',  desc: 'Auto Forecast' },
          { id: 'manual',   label: '🎯 Events',      desc: 'Browse & Analyze' },
          { id: 'analysis', label: '📊 Consensus',   desc: 'AI Agreement' },
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
          <AutoSignalPanel market="poly" planDepth="essential" />
        </div>
      )}

      {mode === 'analysis' && (
        <div className="space-y-3 p-4 flex-1 overflow-y-auto">
          <MarketAnalysisPanel market="poly" planDepth="essential" />
        </div>
      )}

      {mode === 'manual' && (<>
      {/* Header */}
      <div className="px-6 pt-5 pb-4 border-b border-[rgba(255,255,255,0.07)]">
        <div className="flex items-center justify-between mb-1">
          <div>
            <h1 className="text-xl font-black flex items-center gap-2">
              <span className="w-8 h-8 rounded-xl flex items-center justify-center text-base"
                style={{ background: 'linear-gradient(135deg,#6366f1,#8b5cf6)' }}>🔮</span>
              Polymarket Signal AI
            </h1>
            <p className="text-xs text-[var(--text-dim)] mt-0.5">
              Live prediction markets · 4-model weighted consensus · YES/NO probability signals
            </p>
          </div>
          <div className="flex items-center gap-2">
            {/* Credits info */}
            {creditsInfo && (
              <div className="text-right text-[9px]">
                {creditsInfo.has_access ? (
                  <>
                    <div className="text-[#10b981] font-bold">{creditsInfo.credits_balance} cr</div>
                    <div className="text-[var(--text-dim)]">8cr/predict</div>
                  </>
                ) : (
                  <div className="px-2 py-1 rounded-lg text-[9px] font-bold bg-[rgba(244,63,94,0.15)] text-[#f43f5e] border border-[rgba(244,63,94,0.3)]">
                    ⚠️ Ultra plan required
                  </div>
                )}
              </div>
            )}
            <div className="text-right text-[9px] text-[var(--text-dim)]">
              <div><span className="text-[#818cf8] font-bold">{sources.polymarket}</span> Polymarket</div>
              <div><span className="text-[#34d399] font-bold">{sources.gas_generated}</span> GAS</div>
            </div>
            <button onClick={() => loadMarkets(activeCategory, search)}
              className="p-2 rounded-lg border border-[rgba(255,255,255,0.1)] hover:bg-[rgba(255,255,255,0.05)] transition-colors">
              <RefreshCw size={13} className={loadingMarkets ? 'animate-spin text-[#6366f1]' : 'text-[var(--text-dim)]'} />
            </button>
          </div>
        </div>
        {/* Tabs */}
        <div className="flex gap-1 mt-3">
          {[{ id:'markets', label:'🌐 Markets' }, { id:'analytics', label:'📊 Analytics' }].map(t => (
            <button key={t.id} onClick={() => setActiveTab(t.id)}
              className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                activeTab === t.id
                  ? 'bg-[rgba(99,102,241,0.18)] text-[#818cf8] border border-[rgba(99,102,241,0.3)]'
                  : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
              }`}>{t.label}</button>
          ))}
        </div>
      </div>

      {/* Predict error banner */}
      {predictError && (
        <div className="mx-6 mt-3 px-4 py-2.5 rounded-xl text-xs font-bold flex items-center justify-between"
          style={{ background: 'rgba(244,63,94,0.12)', color: '#f43f5e', border: '1px solid rgba(244,63,94,0.3)' }}>
          <span>⚠️ {predictError}</span>
          <button onClick={() => setPredictError(null)} className="opacity-60 hover:opacity-100 text-lg leading-none">×</button>
        </div>
      )}

      {activeTab === 'markets' && (
        <>
          {/* Category + search */}
          <div className="px-6 py-3 border-b border-[rgba(255,255,255,0.05)] space-y-2.5">
            <div className="relative">
              <Search size={12} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--text-dim)]" />
              <input type="text" value={search} onChange={e => handleSearch(e.target.value)}
                placeholder="Search: BTC, gold, EURUSD, breakout..."
                className="w-full pl-8 pr-3 py-2 rounded-xl text-xs bg-[rgba(255,255,255,0.05)] border border-[rgba(255,255,255,0.08)] focus:border-[rgba(99,102,241,0.5)] focus:outline-none placeholder-[var(--text-dim)] text-[var(--text-primary)]" />
            </div>
            <div className="flex gap-2 overflow-x-auto scrollbar-none pb-0.5">
              {CATEGORIES.map(cat => {
                const Icon = cat.icon;
                const active = activeCategory === cat.id;
                return (
                  <button key={cat.id} onClick={() => setActiveCategory(cat.id)}
                    className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-[10px] font-bold whitespace-nowrap flex-shrink-0 transition-all"
                    style={{
                      background: active ? `${cat.color}1a` : 'rgba(255,255,255,0.04)',
                      color: active ? cat.color : 'var(--text-dim)',
                      border: active ? `1px solid ${cat.color}45` : '1px solid rgba(255,255,255,0.06)',
                    }}>
                    <Icon size={9} />{cat.label}
                  </button>
                );
              })}
            </div>
          </div>

          <div className="flex-1 overflow-y-auto scrollbar-thin">
            <div className="px-5 pt-4 pb-2">
              <Top5Panel onPredict={handlePredict} predicting={predicting} predictions={predictions} />
            </div>
            <div className="px-5 pb-5">
              {/* Market count */}
              {!loadingMarkets && !error && markets.length > 0 && (
                <div className="text-[10px] text-[var(--text-dim)] mb-3 flex items-center gap-2">
                  <span className="font-bold text-[var(--text-secondary)]">{markets.length} markets</span>
                  <span>·</span>
                  <span className="text-[#818cf8]">{sources.polymarket} live</span>
                  <span>+</span>
                  <span className="text-[#34d399]">{sources.gas_generated} generated</span>
                </div>
              )}
              {loadingMarkets ? (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {Array.from({length:6}).map((_,i) => (
                    <div key={i} className="rounded-2xl border border-[rgba(255,255,255,0.06)] bg-[rgba(255,255,255,0.02)] h-44 animate-pulse" />
                  ))}
                </div>
              ) : error ? (
                <div className="flex flex-col items-center justify-center py-16 text-[var(--text-dim)]">
                  <AlertCircle size={28} className="mb-3 text-[#f43f5e]" />
                  <p className="text-sm font-bold text-[#f43f5e]">Failed to load markets</p>
                  <p className="text-xs mt-1">{error}</p>
                  <button onClick={() => loadMarkets(activeCategory, search)}
                    className="mt-4 px-4 py-2 rounded-xl text-xs font-bold bg-[rgba(99,102,241,0.2)] text-[#818cf8] border border-[rgba(99,102,241,0.3)]">
                    Try Again
                  </button>
                </div>
              ) : markets.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-16 text-[var(--text-dim)]">
                  <Globe size={28} className="mb-3 opacity-40" />
                  <p className="text-sm">No markets found</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                  {markets.map(m => (
                    <MarketCard key={m.event_id} market={m}
                      onPredict={handlePredict}
                      predicting={!!predicting[m.event_id]}
                      prediction={predictions[m.event_id] || null} />
                  ))}
                </div>
              )}
            </div>
          </div>
        </>
      )}

      {activeTab === 'analytics' && (
        <div className="flex-1 overflow-y-auto p-5 scrollbar-thin">
          <AnalyticsPanel analytics={analytics} history={history} />
        </div>
      )}
      </>)}
      </>)}
    </div>
  );
}
