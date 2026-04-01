import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Bot, Zap, Play, Pause, RefreshCw, TrendingUp, TrendingDown,
  Activity, Shield, CheckCircle2, AlertTriangle, Cpu, Trophy,
  Radio, Plus, Trash2, Settings, BarChart2, Clock, Target,
} from 'lucide-react';
import axios from 'axios';
import PairSelector from './PairSelector';
import StyleSelector, { STYLE_MATRIX } from './StyleSelector';

const WEB = '/web/api/v1';
const gh  = () => ({ Authorization: `Bearer ${localStorage.getItem('gas-token') || ''}` });

// ── AI Model registry ─────────────────────────────────────────────────────────
const AI_MODELS = [
  { id: 'claude', name: 'Claude Sonnet 4.6', short: 'Claude', role: 'High Accuracy',      provider: 'Anthropic', credits: 2, color: '#f97316', emoji: '🟠', accuracy: 94, speed: 'Med' },
  { id: 'gpt',    name: 'GPT-5.4',           short: 'GPT',    role: 'General Reasoning',   provider: 'OpenAI',    credits: 2, color: '#10b981', emoji: '🟢', accuracy: 91, speed: 'Med' },
  { id: 'gemini', name: 'Gemini Pro 3.1',    short: 'Gemini', role: 'Structure Analysis',  provider: 'Google',    credits: 1, color: '#3b82f6', emoji: '🔵', accuracy: 88, speed: 'Fast' },
  { id: 'grok',   name: 'Grok 4.2',          short: 'Grok',   role: 'Fast Momentum',       provider: 'xAI',       credits: 1, color: '#a855f7', emoji: '🟣', accuracy: 86, speed: 'Fast' },
];

const STATUS_CFG = {
  ACTIVE:   { color: 'text-emerald-400', bg: 'bg-emerald-400/10', border: 'border-emerald-400/30', dot: 'bg-emerald-400' },
  COOLDOWN: { color: 'text-yellow-400',  bg: 'bg-yellow-400/10',  border: 'border-yellow-400/30',  dot: 'bg-yellow-400' },
  DISABLED: { color: 'text-red-400',     bg: 'bg-red-400/10',     border: 'border-red-400/30',     dot: 'bg-red-400' },
  RUNNING:  { color: 'text-blue-400',    bg: 'bg-blue-400/10',    border: 'border-blue-400/30',    dot: 'bg-blue-400 animate-pulse' },
};

// ── Tiny helpers ──────────────────────────────────────────────────────────────
const sigColor = s => s === 'BUY' ? 'text-emerald-400' : s === 'SELL' ? 'text-red-400' : s === 'NO TRADE' ? 'text-[var(--text-dim)]' : 'text-yellow-400';
const sigBg    = s => s === 'BUY' ? 'bg-emerald-400/10 border-emerald-400/30' : s === 'SELL' ? 'bg-red-400/10 border-red-400/30' : 'bg-[var(--bg-hover)] border-[var(--border-color)]';
const fmtPnL   = v => v == null ? '--' : `${v >= 0 ? '+' : ''}${Number(v).toFixed(2)}$`;
const MODEL    = id => AI_MODELS.find(m => m.id === id) || AI_MODELS[0];

// ── Status badge ─────────────────────────────────────────────────────────────
function StatusBadge({ status }) {
  const c = STATUS_CFG[status] || STATUS_CFG.COOLDOWN;
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full border text-[8px] font-black uppercase ${c.color} ${c.bg} ${c.border}`}>
      <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${c.dot}`} />{status}
    </span>
  );
}

// ─────────────────────── POWER BI CHART COMPONENTS ───────────────────────────

/** Equity Curve — SVG area chart */
function EquityCurve({ data = [], height = 110 }) {
  if (!data.length) return <EmptyChart label="No equity data yet" />;
  const vals = data.map(d => d.v);
  const min  = Math.min(...vals);
  const max  = Math.max(...vals);
  const rng  = max - min || 1;
  const W = 480, H = height - 24;
  const pts = data.map((d, i) => {
    const x = (i / (data.length - 1)) * W;
    const y = H - ((d.v - min) / rng) * H;
    return `${x},${y}`;
  });
  const area = `M0,${H} L${pts.join(' L')} L${W},${H} Z`;
  const line = `M${pts.join(' L')}`;
  const last = vals[vals.length - 1];
  const isPos = last >= 0;
  const color = isPos ? '#10b981' : '#ef4444';

  return (
    <div className="relative">
      <svg width="100%" viewBox={`0 0 ${W} ${height}`} preserveAspectRatio="none" style={{ display: 'block' }}>
        <defs>
          <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.35" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>
        {/* Grid lines */}
        {[0.25, 0.5, 0.75].map(r => (
          <line key={r} x1={0} y1={r * H} x2={W} y2={r * H} stroke="rgba(255,255,255,0.04)" strokeWidth={1} />
        ))}
        {/* Zero line */}
        {min < 0 && max > 0 && (
          <line x1={0} y1={H - ((-min) / rng) * H} x2={W} y2={H - ((-min) / rng) * H}
            stroke="rgba(255,255,255,0.15)" strokeWidth={1} strokeDasharray="4,4" />
        )}
        <path d={area} fill="url(#eqGrad)" />
        <path d={line} fill="none" stroke={color} strokeWidth={2} strokeLinejoin="round" />
        {/* Last value dot */}
        <circle cx={(data.length-1)/(data.length-1)*W} cy={H - ((last-min)/rng)*H} r={4} fill={color} />
      </svg>
      <div className="absolute top-0 right-0 flex items-center gap-1">
        <span className={`text-[10px] font-black font-mono ${isPos ? 'text-emerald-400' : 'text-red-400'}`}>{fmtPnL(last)}</span>
      </div>
      <div className="absolute bottom-0 left-0 right-0 flex justify-between px-1">
        {data.filter((_,i) => i === 0 || i === Math.floor(data.length/2) || i === data.length-1).map((d,i) => (
          <span key={i} className="text-[7px] text-[var(--text-dim)] font-mono">{d.t?.slice(5) || ''}</span>
        ))}
      </div>
    </div>
  );
}

/** Donut / Ring chart for win rate */
function DonutChart({ pct = 0, size = 96, label = '', color = '#10b981' }) {
  const r = (size - 16) / 2;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} style={{ transform: 'rotate(-90deg)' }}>
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={10} />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth={10}
          strokeDasharray={`${dash} ${circ - dash}`} strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.8s ease' }} />
        <text x={size/2} y={size/2 + 6} textAnchor="middle" fontSize={16} fontWeight={900}
          fill="currentColor" style={{ transform: `rotate(90deg) translate(0, -${size}px)`, transformOrigin: `${size/2}px ${size/2}px`, fill: color }}>
        </text>
      </svg>
      <div className="text-center -mt-1">
        <p className="text-lg font-black font-mono" style={{ color }}>{pct}%</p>
        <p className="text-[8px] text-[var(--text-dim)] uppercase tracking-wider font-bold">{label}</p>
      </div>
    </div>
  );
}

/** Vertical bar chart (confidence distribution / model runs) */
function VBarChart({ data = {}, color = '#3b82f6', height = 80 }) {
  if (!Object.keys(data).length) return <EmptyChart label="No distribution data" />;
  const entries = Object.entries(data).sort((a,b) => a[0].localeCompare(b[0]));
  const maxVal  = Math.max(...entries.map(([,v]) => v), 1);
  return (
    <div className="flex items-end gap-1 h-full" style={{ height }}>
      {entries.map(([k, v], i) => (
        <div key={i} className="flex flex-col items-center gap-0.5 flex-1 min-w-0">
          <span className="text-[7px] font-mono text-[var(--text-dim)]">{v}</span>
          <div className="w-full rounded-t-sm transition-all duration-500"
            style={{ height: `${(v / maxVal) * (height - 20)}px`, background: color, opacity: 0.8 + (i * 0.02) }} />
          <span className="text-[6px] text-[var(--text-dim)] truncate w-full text-center font-mono">{k.split('-')[0]}</span>
        </div>
      ))}
    </div>
  );
}

/** Horizontal bar chart (model comparison) */
function HBarChart({ data = {}, colors = {}, maxLabel = '' }) {
  if (!Object.keys(data).length) return <EmptyChart label="No model data" />;
  const maxVal = Math.max(...Object.values(data).map(d => d.runs || d || 0), 1);
  return (
    <div className="space-y-2">
      {Object.entries(data).map(([k, v]) => {
        const val   = typeof v === 'object' ? v.runs : v;
        const conf  = typeof v === 'object' ? v.avg_conf : null;
        const model = AI_MODELS.find(m => m.id === k);
        const color = model?.color || '#94a3b8';
        return (
          <div key={k} className="space-y-0.5">
            <div className="flex items-center justify-between">
              <span className="text-[8px] font-black text-[var(--text-secondary)]">{model?.short || k}</span>
              <span className="text-[8px] font-mono text-[var(--text-dim)]">
                {val} runs{conf ? ` · ${conf}% conf` : ''}
              </span>
            </div>
            <div className="h-1.5 bg-[var(--bg-hover)] rounded-full overflow-hidden">
              <div className="h-full rounded-full transition-all duration-700"
                style={{ width: `${(val / maxVal) * 100}%`, background: color }} />
            </div>
          </div>
        );
      })}
    </div>
  );
}

/** Pair heatmap bars */
function PairBars({ data = {} }) {
  if (!Object.keys(data).length) return <EmptyChart label="No pair data" />;
  const max = Math.max(...Object.values(data).map(d => d.runs || 0), 1);
  return (
    <div className="space-y-1.5">
      {Object.entries(data).slice(0, 8).map(([pair, s]) => (
        <div key={pair} className="flex items-center gap-2">
          <span className="text-[8px] font-black text-[var(--text-secondary)] w-14 shrink-0">{pair.replace('/', '')}</span>
          <div className="flex-1 h-2 bg-[var(--bg-hover)] rounded-full overflow-hidden">
            <div className="h-full rounded-full transition-all duration-700"
              style={{ width: `${(s.runs / max) * 100}%`, background: `linear-gradient(90deg, #f59e0b, #f97316)` }} />
          </div>
          <span className="text-[7px] font-mono text-[var(--text-dim)] w-8 text-right">{s.runs}r</span>
        </div>
      ))}
    </div>
  );
}

/** Sparkline inline mini chart */
function Sparkline({ values = [], color = '#10b981', width = 60, height = 22 }) {
  if (values.length < 2) return null;
  const min = Math.min(...values), max = Math.max(...values);
  const rng = max - min || 1;
  const W = width, H = height;
  const pts = values.map((v, i) => `${(i / (values.length-1)) * W},${H - ((v-min)/rng) * H}`);
  return (
    <svg width={W} height={H} className="shrink-0">
      <polyline points={pts.join(' ')} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" />
    </svg>
  );
}

/** KPI Card — Power BI style */
function KPICard({ label, value, sub, color = '#facc15', spark = [], icon: Icon, trend }) {
  return (
    <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-3 flex flex-col gap-1 hover:border-opacity-80 transition-all">
      <div className="flex items-center justify-between">
        <p className="text-[7px] font-black uppercase tracking-widest text-[var(--text-dim)]">{label}</p>
        {Icon && <Icon size={11} style={{ color, opacity: 0.7 }} />}
      </div>
      <div className="flex items-end gap-2">
        <p className="text-xl font-black font-mono leading-none" style={{ color }}>{value}</p>
        {spark.length > 1 && <Sparkline values={spark} color={color} />}
      </div>
      {sub && (
        <div className="flex items-center gap-1">
          {trend !== undefined && (
            <span className={`text-[8px] font-black ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {trend >= 0 ? '▲' : '▼'}{Math.abs(trend)}%
            </span>
          )}
          <p className="text-[8px] text-[var(--text-dim)] font-bold">{sub}</p>
        </div>
      )}
    </div>
  );
}

function EmptyChart({ label }) {
  return (
    <div className="flex items-center justify-center h-16 text-[8px] text-[var(--text-dim)] font-bold uppercase tracking-wider">
      {label}
    </div>
  );
}

function SectionHeader({ title, sub }) {
  return (
    <div className="flex items-center gap-2 mb-3">
      <div className="h-px flex-1 bg-[var(--border-color)]" />
      <div className="text-center">
        <p className="text-[8px] font-black uppercase tracking-widest text-[var(--accent)]">{title}</p>
        {sub && <p className="text-[7px] text-[var(--text-dim)]">{sub}</p>}
      </div>
      <div className="h-px flex-1 bg-[var(--border-color)]" />
    </div>
  );
}

// ── Agent card ────────────────────────────────────────────────────────────────
function AgentCard({ agent, onRun, onToggle, onDelete, isRunning }) {
  const model = MODEL(agent.model_id);
  return (
    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden transition-all hover:border-opacity-70"
      style={agent.status === 'ACTIVE' ? { borderColor: `${model.color}40` } : {}}>
      <div className="px-4 py-2.5 border-b border-[var(--border-color)] flex items-center gap-2"
        style={{ background: `${model.color}08` }}>
        <span className="text-base">{model.emoji}</span>
        <div className="flex-1 min-w-0">
          <p className="text-[10px] font-black text-[var(--text-primary)] truncate">{agent.name}</p>
          <p className="text-[7px] text-[var(--text-dim)]">{model.name} · {agent.pair} · {agent.style}</p>
        </div>
        <StatusBadge status={agent.status} />
      </div>
      <div className="p-3 space-y-2">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[7px] text-[var(--text-dim)] uppercase font-black mb-0.5">Signal</p>
            <span className={`text-[10px] font-black px-2 py-0.5 rounded border ${sigBg(agent.last_signal)}`}>
              {agent.last_signal || 'WAIT'}
            </span>
          </div>
          <div className="text-right">
            <p className="text-[7px] text-[var(--text-dim)] uppercase font-black mb-0.5">Conf</p>
            <p className="text-lg font-black font-mono" style={{ color: model.color }}>{agent.confidence ?? '--'}%</p>
          </div>
          <div className="text-right">
            <p className="text-[7px] text-[var(--text-dim)] uppercase font-black mb-0.5">PnL</p>
            <p className={`text-[11px] font-black font-mono ${(agent.pnl||0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {fmtPnL(agent.pnl)}
            </p>
          </div>
        </div>
        {/* Mini stats */}
        <div className="grid grid-cols-3 gap-1">
          {[
            { l: 'Win%',   v: `${agent.winrate ?? 0}%`,  ok: (agent.winrate ?? 0) >= 50 },
            { l: 'Trades', v: agent.trades ?? 0,          ok: true },
            { l: 'Wins',   v: agent.wins ?? 0,            ok: true },
          ].map((s, i) => (
            <div key={i} className="bg-[var(--bg-panel)] rounded-lg p-1.5 text-center border border-[var(--border-color)]">
              <p className="text-[6px] font-black text-[var(--text-dim)] uppercase">{s.l}</p>
              <p className={`text-[9px] font-black font-mono ${s.ok ? 'text-[var(--text-primary)]' : 'text-red-400'}`}>{s.v}</p>
            </div>
          ))}
        </div>
        {/* Entry/SL/TP */}
        {agent.entry && (
          <div className="grid grid-cols-3 gap-1">
            {[['Entry', agent.entry, 'text-[var(--text-primary)]'], ['SL', agent.sl, 'text-red-400'], ['TP', agent.tp, 'text-emerald-400']].map(([l,v,c]) => (
              <div key={l} className="bg-[var(--bg-panel)] rounded-lg p-1.5 border border-[var(--border-color)]">
                <p className="text-[6px] font-black text-[var(--text-dim)] uppercase">{l}</p>
                <p className={`text-[8px] font-black font-mono ${c}`}>{v ? Number(v).toFixed(2) : '--'}</p>
              </div>
            ))}
          </div>
        )}
        <div className="flex gap-1.5">
          <button onClick={() => onRun(agent)} disabled={isRunning || agent.status === 'DISABLED'}
            className="flex-1 py-1.5 rounded-lg text-[8px] font-black flex items-center justify-center gap-1 transition-all hover:opacity-90 disabled:opacity-40"
            style={{ background: isRunning ? 'var(--bg-hover)' : `${model.color}20`, color: model.color, border: `1px solid ${model.color}30` }}>
            {isRunning ? <RefreshCw size={9} className="animate-spin" /> : <Zap size={9} />}
            {isRunning ? 'Running' : 'Run'}
          </button>
          <button onClick={() => onToggle(agent.id)}
            className="px-2 py-1.5 rounded-lg text-[8px] font-black transition-all hover:bg-[var(--bg-hover)]"
            style={{ border: '1px solid var(--border-color)', color: 'var(--text-dim)' }}>
            {agent.status === 'ACTIVE' ? <Pause size={9} /> : <Play size={9} />}
          </button>
          <button onClick={() => onDelete(agent.id)}
            className="px-2 py-1.5 rounded-lg text-[8px] font-black text-red-400 hover:bg-red-400/10 transition-all"
            style={{ border: '1px solid rgba(239,68,68,0.2)' }}>
            <Trash2 size={9} />
          </button>
        </div>
      </div>
    </div>
  );
}

// ── Create Agent Modal ────────────────────────────────────────────────────────
function CreateAgentModal({ onClose, onCreate }) {
  const [form, setForm] = useState({ name: '', model_id: 'claude', style: 'scalping', pair: 'XAUUSD', min_confidence: 70, max_trades: 2 });
  const [loading, setLoading] = useState(false);
  const submit = async () => {
    if (!form.name.trim()) return;
    setLoading(true);
    try {
      const r = await axios.post(`${WEB}/agent/agents`, form, { headers: gh() });
      onCreate(r.data.agent);
      onClose();
    } catch (e) {
      alert(e?.response?.data?.detail || 'Failed to create agent');
    } finally { setLoading(false); }
  };
  return (
    <div className="fixed inset-0 z-[300] flex items-center justify-center p-4" style={{ background: 'rgba(0,0,0,0.7)' }}>
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl w-full max-w-md p-5 space-y-4">
        <div className="flex items-center gap-2">
          <Bot size={16} className="text-purple-400" />
          <p className="font-black text-[var(--text-primary)]">Create New Agent</p>
        </div>
        <input value={form.name} onChange={e => setForm(p => ({...p, name: e.target.value}))}
          placeholder="Agent name (e.g. Claude Scalper Gold)"
          className="w-full px-3 py-2 rounded-xl border text-xs bg-[var(--bg-panel)] border-[var(--border-color)] text-[var(--text-primary)] placeholder:text-[var(--text-dim)] outline-none focus:border-purple-400/50" />
        <div className="grid grid-cols-2 gap-3">
          <div>
            <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mb-1.5">AI Model</p>
            <div className="space-y-1">
              {AI_MODELS.map(m => (
                <button key={m.id} onClick={() => setForm(p => ({...p, model_id: m.id}))}
                  className="w-full flex items-center gap-2 px-2.5 py-1.5 rounded-lg border text-left transition-all"
                  style={form.model_id === m.id ? { background: `${m.color}15`, borderColor: `${m.color}50` } : { background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }}>
                  <span className="text-sm">{m.emoji}</span>
                  <div>
                    <p className="text-[8px] font-black" style={{ color: form.model_id === m.id ? m.color : 'var(--text-primary)' }}>{m.short}</p>
                    <p className="text-[7px] text-[var(--text-dim)]">{m.credits}cr · {m.accuracy}% acc</p>
                  </div>
                  {form.model_id === m.id && <CheckCircle2 size={10} style={{ color: m.color }} className="ml-auto" />}
                </button>
              ))}
            </div>
          </div>
          <div className="space-y-3">
            <div>
              <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mb-1.5">Style</p>
              {['scalping','intraday','swing'].map(s => (
                <button key={s} onClick={() => setForm(p => ({...p, style: s}))}
                  className="block w-full text-left px-2.5 py-1.5 rounded-lg text-[8px] font-black capitalize mb-1 transition-all"
                  style={form.style === s ? { background: 'var(--accent)', color: '#000' } : { background: 'var(--bg-panel)', border: '1px solid var(--border-color)', color: 'var(--text-dim)' }}>
                  {s}
                </button>
              ))}
            </div>
            <div>
              <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mb-1.5">Min Confidence</p>
              <div className="flex items-center gap-2">
                <input type="range" min={50} max={95} step={5} value={form.min_confidence}
                  onChange={e => setForm(p => ({...p, min_confidence: +e.target.value}))}
                  className="flex-1 accent-yellow-400" />
                <span className="text-[10px] font-black font-mono text-[var(--accent)] w-6">{form.min_confidence}</span>
              </div>
            </div>
          </div>
        </div>
        <PairSelector value={form.pair} onChange={v => setForm(p => ({...p, pair: v}))} label="Trading Pair" />
        <div className="flex gap-2">
          <button onClick={onClose} className="flex-1 py-2 rounded-xl text-[10px] font-black border border-[var(--border-color)] text-[var(--text-dim)] hover:bg-[var(--bg-hover)] transition-all">Cancel</button>
          <button onClick={submit} disabled={loading || !form.name.trim()}
            className="flex-1 py-2 rounded-xl text-[10px] font-black disabled:opacity-50 transition-all hover:opacity-90"
            style={{ background: 'var(--accent)', color: '#000' }}>
            {loading ? 'Creating...' : 'Create Agent'}
          </button>
        </div>
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
//  MAIN COMPONENT
// ─────────────────────────────────────────────────────────────────────────────
const TABS = ['execute', 'lab', 'performance', 'config'];
const TAB_LABELS = { execute: '⚡ Execute', lab: '🧪 Lab', performance: '📊 Performance', config: '⚙️ Config' };

export default function AIAgentView() {
  const [tab, setTab]           = useState('execute');
  const [pair, setPair]         = useState('XAUUSD');
  const [style, setStyle]       = useState('scalping');
  const [modelId, setModelId]   = useState('claude');
  const [minConf, setMinConf]   = useState(70);
  const [maxTrades, setMaxTrades] = useState(2);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [agents, setAgents]     = useState([]);
  const [agentsLoading, setAgentsLoading] = useState(true);
  const [runningId, setRunningId] = useState(null);
  const [labRunning, setLabRunning] = useState(false);
  const [labResults, setLabResults] = useState([]);
  const [perfData, setPerfData] = useState(null);
  const [perfLoading, setPerfLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);

  const selectedModel = AI_MODELS.find(m => m.id === modelId) || AI_MODELS[0];
  const styleTFs      = STYLE_MATRIX[style]?.tfs || ['H4','H1','M15','M5'];
  const triggerTF     = styleTFs[styleTFs.length - 1];

  // ── Fetch agents on mount ────────────────────────────────────────────────────
  const fetchAgents = useCallback(async () => {
    setAgentsLoading(true);
    try {
      const r = await axios.get(`${WEB}/agent/agents`, { headers: gh() });
      setAgents(r.data.agents || []);
    } catch { setAgents([]); }
    finally { setAgentsLoading(false); }
  }, []);

  // ── Fetch performance data ──────────────────────────────────────────────────
  const fetchPerformance = useCallback(async () => {
    setPerfLoading(true);
    try {
      const r = await axios.get(`${WEB}/agent/performance`, { headers: gh() });
      setPerfData(r.data);
      setAgents(r.data.agents || []);
    } catch { setPerfData(null); }
    finally { setPerfLoading(false); }
  }, []);

  useEffect(() => { fetchAgents(); }, [fetchAgents]);
  useEffect(() => { if (tab === 'performance') fetchPerformance(); }, [tab, fetchPerformance]);

  // ── Run single agent ─────────────────────────────────────────────────────────
  const runAgent = async (agentOrNull) => {
    const ag = agentOrNull;
    const isLabRun = !!ag?.id;
    if (!isLabRun) setLoading(true);
    setRunningId(ag?.id || 'solo');
    if (!isLabRun) setResult(null);
    try {
      const r = await axios.post(`${WEB}/agent/run`, {
        agent_id: ag?.id || null,
        pair: ag?.pair || pair,
        style: ag?.style || style,
        model: ag?.model_id || modelId,
        min_confidence: ag?.min_confidence || minConf,
        max_trades: ag?.max_trades || maxTrades,
        timeframe: triggerTF,
        timeframes: styleTFs,
      }, { headers: gh() });
      if (!isLabRun) setResult(r.data);
      if (isLabRun) {
        setAgents(prev => prev.map(a =>
          a.id === ag.id ? { ...a, last_signal: r.data.signal, confidence: r.data.confidence, entry: r.data.entry, sl: r.data.sl, tp: Array.isArray(r.data.tp) ? r.data.tp[0] : r.data.tp } : a
        ));
      }
      return r.data;
    } catch (e) {
      const err = { error: true, message: e?.response?.data?.detail || 'Agent call failed.' };
      if (!isLabRun) setResult(err);
      return err;
    } finally {
      if (!isLabRun) setLoading(false);
      setRunningId(null);
    }
  };

  const toggleAgent = async (id) => {
    try {
      const r = await axios.patch(`${WEB}/agent/agents/${id}/toggle`, {}, { headers: gh() });
      setAgents(r.data.agents || []);
    } catch {}
  };

  const deleteAgent = async (id) => {
    if (!confirm('Delete this agent?')) return;
    try {
      const r = await axios.delete(`${WEB}/agent/agents/${id}`, { headers: gh() });
      setAgents(r.data.agents || []);
    } catch {}
  };

  const runAllLab = async () => {
    setLabRunning(true);
    setLabResults([]);
    const res = [];
    for (const ag of agents.filter(a => a.status !== 'DISABLED')) {
      const r = await runAgent(ag);
      res.push({ ...ag, result: r });
    }
    setLabResults(res);
    setLabRunning(false);
  };

  const bias    = result?.signal;
  const isBuy   = bias === 'BUY';
  const isSell  = bias === 'SELL';
  const noTrade = bias === 'NO TRADE';

  const stats = perfData?.stats || {};
  const winRate = stats.total_signals > 0
    ? Math.round((stats.buy_signals + stats.sell_signals) / stats.total_runs * 100)
    : 0;
  const equitySpark = (perfData?.equity_curve || []).slice(-10).map(d => d.v);

  return (
    <div className="p-4 md:p-6 space-y-4 pb-24 md:pb-6 max-w-6xl mx-auto">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center text-lg shrink-0"
          style={{ background: 'rgba(168,85,247,0.12)', border: '1px solid rgba(168,85,247,0.25)' }}>🤖</div>
        <div className="flex-1">
          <h2 className="text-lg font-display font-black text-[var(--text-primary)] leading-tight">AI Agent Trading System</h2>
          <p className="text-[9px] text-[var(--text-dim)] uppercase tracking-widest font-bold mt-0.5">
            Multi-Model · Auto Signal · Lifecycle · EA Integration
          </p>
        </div>
        <span className="text-[8px] font-black px-2.5 py-1 rounded-full"
          style={{ background: 'rgba(244,63,94,0.12)', color: '#fb7185', border: '1px solid rgba(244,63,94,0.25)' }}>
          Ultra Ultimate
        </span>
      </div>

      {/* Flow */}
      <div className="flex flex-wrap items-center gap-1 px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
        <span className="text-[7px] font-black text-[var(--text-dim)] uppercase shrink-0">Flow:</span>
        {[['MT5 Data','text-blue-400 bg-blue-400/10'],['GAS Engine','text-[var(--accent)] bg-[var(--accent)]/10'],['Quant Filter','text-yellow-400 bg-yellow-400/10'],['AI Agent','text-purple-400 bg-purple-400/10'],['Signal','text-emerald-400 bg-emerald-400/10'],['EA Execute','text-blue-400 bg-blue-400/10'],['DB Track','text-[var(--text-dim)] bg-[var(--bg-hover)]']].map(([l,c],i,a) => (
          <React.Fragment key={i}>
            <span className={`text-[7px] font-black px-1.5 py-0.5 rounded ${c}`}>{l}</span>
            {i < a.length-1 && <span className="text-[var(--text-dim)] text-[8px]">→</span>}
          </React.Fragment>
        ))}
      </div>

      {/* Global mini KPIs */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <KPICard label="Active Agents"  value={agents.filter(a=>a.status==='ACTIVE').length} sub={`of ${agents.length} total`} color="#a855f7" icon={Bot} />
        <KPICard label="Total Runs"     value={stats.total_runs || 0} sub="all time" color="#3b82f6" icon={Radio} spark={equitySpark} />
        <KPICard label="Signal Rate"    value={`${stats.total_runs ? Math.round((stats.total_signals||0)/stats.total_runs*100) : 0}%`} sub="BUY+SELL / total" color="#f59e0b" icon={Target} />
        <KPICard label="Avg Confidence" value={`${stats.avg_confidence || 0}%`} sub="across all runs" color="#10b981" icon={Activity} />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl overflow-x-auto scrollbar-none">
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            className="flex-1 min-w-max py-2 px-3 rounded-lg text-[9px] font-black uppercase tracking-wider transition-all"
            style={tab === t ? { background: 'var(--accent)', color: '#000' } : { color: 'var(--text-dim)' }}>
            {TAB_LABELS[t]}
          </button>
        ))}
      </div>

      {/* ══════════════════════════ EXECUTE TAB ══════════════════════════ */}
      {tab === 'execute' && (
        <div className="space-y-4">
          {/* Model picker */}
          <div>
            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Pilih AI Model</p>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {AI_MODELS.map(m => (
                <button key={m.id} onClick={() => setModelId(m.id)}
                  className="p-3 rounded-xl border text-left transition-all hover:scale-[1.02]"
                  style={modelId === m.id ? { background: `${m.color}15`, borderColor: `${m.color}50` } : { background: 'var(--bg-card)', borderColor: 'var(--border-color)' }}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-lg">{m.emoji}</span>
                    {modelId === m.id && <CheckCircle2 size={10} style={{ color: m.color }} className="ml-auto" />}
                  </div>
                  <p className="text-[9px] font-black" style={{ color: modelId === m.id ? m.color : 'var(--text-primary)' }}>{m.short}</p>
                  <p className="text-[7px] text-[var(--text-dim)]">{m.role}</p>
                  <div className="flex justify-between mt-1">
                    <span className="text-[6px] text-[var(--text-dim)]">{m.speed} · {m.accuracy}%</span>
                    <span className="text-[7px] font-black" style={{ color: m.color }}>{m.credits}cr</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Pair + TF display */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <PairSelector value={pair} onChange={setPair} label="Pair" />
            <div>
              <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Trigger TF</p>
              <div className="flex items-center gap-2 px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
                <span className="text-[10px] font-black font-mono mr-auto" style={{ color: selectedModel.color }}>{triggerTF}</span>
                {styleTFs.map(tf => (
                  <span key={tf} className="text-[7px] px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-dim)] font-black">{tf}</span>
                ))}
              </div>
            </div>
          </div>
          <StyleSelector value={style} onChange={setStyle} showMatrix compact />

          {/* Rules */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1.5">Min Confidence</p>
              <div className="flex items-center gap-2 px-3 py-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
                <input type="range" min={50} max={95} step={5} value={minConf}
                  onChange={e => setMinConf(+e.target.value)} className="flex-1 accent-yellow-400" />
                <span className="text-[11px] font-black font-mono text-[var(--accent)] w-6">{minConf}</span>
              </div>
            </div>
            <div>
              <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1.5">Max Trades</p>
              <div className="flex gap-1.5">
                {[1,2,3,5].map(n => (
                  <button key={n} onClick={() => setMaxTrades(n)}
                    className="flex-1 py-2 rounded-xl text-[10px] font-black transition-all"
                    style={maxTrades === n ? { background: selectedModel.color, color: '#000' } : { background: 'var(--bg-panel)', border: '1px solid var(--border-color)', color: 'var(--text-dim)' }}>
                    {n}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <button onClick={() => runAgent(null)} disabled={loading}
            className="w-full py-3.5 rounded-2xl text-sm font-black flex items-center justify-center gap-2 transition-all hover:opacity-90 disabled:opacity-50"
            style={{ background: selectedModel.color, color: '#000' }}>
            {loading
              ? <><RefreshCw size={15} className="animate-spin" /> Agent {selectedModel.short} analysing...</>
              : <><Zap size={15} /> Run {selectedModel.short} — {pair} · {style} · {selectedModel.credits}cr</>}
          </button>

          {result && !result.error && (
            <div className="space-y-3 animate-fade-up">
              <div className="rounded-2xl border overflow-hidden"
                style={isBuy ? { background:'rgba(16,185,129,0.05)', borderColor:'rgba(16,185,129,0.3)' }
                      : isSell ? { background:'rgba(239,68,68,0.05)', borderColor:'rgba(239,68,68,0.3)' }
                      : { background:'var(--bg-panel)', borderColor:'var(--border-color)' }}>
                <div className="p-5 flex items-center gap-4">
                  <div>{isBuy ? <TrendingUp size={40} className="text-emerald-400" /> : isSell ? <TrendingDown size={40} className="text-red-400" /> : noTrade ? <Shield size={40} className="text-[var(--text-dim)]" /> : <Activity size={40} className="text-yellow-400" />}</div>
                  <div className="flex-1">
                    <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-1">{selectedModel.emoji} {selectedModel.name} Signal</p>
                    <p className={`text-5xl font-black font-mono leading-none ${sigColor(bias)}`}>{bias}</p>
                    {noTrade && <p className="text-[10px] text-[var(--text-dim)] mt-1">Confidence {result.confidence}% below {minConf}% threshold</p>}
                  </div>
                  {result.confidence != null && (
                    <div className="text-right">
                      <p className="text-[8px] text-[var(--text-dim)] uppercase font-black mb-1">Confidence</p>
                      <p className="text-3xl font-black font-mono" style={{ color: selectedModel.color }}>{result.confidence}%</p>
                    </div>
                  )}
                </div>
                {(result.entry || result.sl || result.tp) && (
                  <div className="grid grid-cols-3 gap-3 px-5 pb-5">
                    {[['Entry', result.entry, 'text-[var(--text-primary)]'],
                      ['SL', result.sl, 'text-red-400'],
                      ['TP', Array.isArray(result.tp) ? result.tp[0] : result.tp, 'text-emerald-400']
                    ].map(([l,v,c]) => v && (
                      <div key={l} className="bg-[var(--bg-card)] rounded-xl p-3 border border-[var(--border-color)]">
                        <p className="text-[7px] font-black text-[var(--text-dim)] uppercase mb-1">{l}</p>
                        <p className={`text-sm font-black font-mono ${c}`}>{typeof v === 'number' ? v.toFixed(2) : v}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
              {result.reasoning && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4">
                  <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-2">🤖 Agent Reasoning</p>
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{result.reasoning}</p>
                </div>
              )}
            </div>
          )}
          {result?.error && (
            <div className="rounded-xl p-4 border" style={{ background:'rgba(239,68,68,0.05)', borderColor:'rgba(239,68,68,0.25)' }}>
              <p className="text-xs font-black text-red-400 mb-1">⚠️ Agent Error</p>
              <p className="text-[10px] text-red-400/70">{result.message}</p>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════ LAB TAB ══════════════════════════ */}
      {tab === 'lab' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Agent Lab</p>
              <p className="text-[8px] text-[var(--text-dim)] mt-0.5">Run all agents in parallel, compare consensus</p>
            </div>
            <div className="flex gap-2">
              <button onClick={() => setShowCreate(true)}
                className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-[9px] font-black border border-[var(--border-color)] text-[var(--text-dim)] hover:bg-[var(--bg-hover)] transition-all">
                <Plus size={11} /> New Agent
              </button>
              <button onClick={runAllLab} disabled={labRunning || !agents.length}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-[9px] font-black transition-all disabled:opacity-50"
                style={{ background: 'var(--accent)', color: '#000' }}>
                {labRunning ? <><RefreshCw size={11} className="animate-spin" /> Running...</> : <><Radio size={11} /> Run All</>}
              </button>
            </div>
          </div>

          {/* Consensus summary */}
          {labResults.length > 0 && (() => {
            const buys  = labResults.filter(r => r.result?.signal === 'BUY').length;
            const sells = labResults.filter(r => r.result?.signal === 'SELL').length;
            const neutral = labResults.length - buys - sells;
            const con = buys > sells ? 'BUY' : sells > buys ? 'SELL' : 'NEUTRAL';
            return (
              <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4 space-y-3">
                <div className="flex items-center gap-4">
                  <div>
                    <p className="text-[7px] font-black text-[var(--text-dim)] uppercase mb-1">Multi-Agent Consensus</p>
                    <span className={`text-xl font-black font-mono ${sigColor(con)}`}>{con}</span>
                  </div>
                  <div className="flex gap-3 ml-auto">
                    {[['BUY', buys, 'text-emerald-400'], ['SELL', sells, 'text-red-400'], ['N/A', neutral, 'text-[var(--text-dim)]']].map(([l,n,c]) => (
                      <div key={l} className="text-center">
                        <p className={`text-base font-black font-mono ${c}`}>{n}</p>
                        <p className="text-[7px] text-[var(--text-dim)] font-black">{l}</p>
                      </div>
                    ))}
                  </div>
                </div>
                <div className="space-y-1.5">
                  {labResults.map((ag, i) => {
                    const m = MODEL(ag.model_id);
                    return (
                      <div key={i} className="flex items-center gap-2 px-3 py-2 rounded-xl border border-[var(--border-color)] bg-[var(--bg-panel)]">
                        <span className="text-sm">{m.emoji}</span>
                        <span className="text-[8px] font-black text-[var(--text-secondary)] w-24 truncate">{ag.name}</span>
                        <span className="text-[7px] text-[var(--text-dim)] flex-1">{ag.pair} · {ag.style}</span>
                        <span className={`text-[9px] font-black px-2 py-0.5 rounded border ${sigBg(ag.result?.signal)}`}>{ag.result?.signal || 'ERR'}</span>
                        {ag.result?.confidence != null && (
                          <span className="text-[8px] font-mono w-8 text-right font-black" style={{ color: m.color }}>{ag.result.confidence}%</span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })()}

          {agentsLoading ? (
            <div className="flex items-center justify-center h-32 text-[var(--text-dim)]"><RefreshCw size={20} className="animate-spin" /></div>
          ) : agents.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-40 gap-3">
              <Bot size={32} className="text-[var(--text-dim)]" />
              <p className="text-[10px] text-[var(--text-dim)] font-bold">No agents yet</p>
              <button onClick={() => setShowCreate(true)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-[10px] font-black transition-all"
                style={{ background: 'var(--accent)', color: '#000' }}>
                <Plus size={12} /> Create First Agent
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {agents.map(ag => (
                <AgentCard key={ag.id} agent={ag}
                  onRun={runAgent} onToggle={toggleAgent} onDelete={deleteAgent}
                  isRunning={runningId === ag.id} />
              ))}
              <button onClick={() => setShowCreate(true)}
                className="border-2 border-dashed border-[var(--border-color)] rounded-2xl p-6 flex flex-col items-center gap-2 text-[var(--text-dim)] hover:border-purple-400/40 hover:text-purple-400 transition-all">
                <Plus size={20} />
                <span className="text-[9px] font-black uppercase">Add Agent</span>
              </button>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════ PERFORMANCE TAB (Power BI) ══════════════════════════ */}
      {tab === 'performance' && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Performance Dashboard</p>
              <p className="text-[8px] text-[var(--text-dim)] mt-0.5">Real-time data from your agent runs</p>
            </div>
            <button onClick={fetchPerformance} disabled={perfLoading}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[8px] font-black border border-[var(--border-color)] text-[var(--text-dim)] hover:bg-[var(--bg-hover)] transition-all disabled:opacity-50">
              <RefreshCw size={10} className={perfLoading ? 'animate-spin' : ''} /> Refresh
            </button>
          </div>

          {perfLoading ? (
            <div className="flex items-center justify-center h-48"><RefreshCw size={24} className="animate-spin text-[var(--text-dim)]" /></div>
          ) : !perfData || !perfData.stats?.total_runs ? (
            /* Empty state */
            <div className="flex flex-col items-center justify-center gap-4 py-16">
              <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-3xl"
                style={{ background: 'rgba(168,85,247,0.1)', border: '1px solid rgba(168,85,247,0.2)' }}>📊</div>
              <div className="text-center">
                <p className="text-sm font-black text-[var(--text-primary)]">No performance data yet</p>
                <p className="text-[10px] text-[var(--text-dim)] mt-1">Run your first agent to see Power BI analytics appear here</p>
              </div>
              <button onClick={() => setTab('execute')}
                className="flex items-center gap-2 px-5 py-2.5 rounded-xl text-[10px] font-black transition-all"
                style={{ background: 'var(--accent)', color: '#000' }}>
                <Zap size={12} /> Run First Agent
              </button>
            </div>
          ) : (
            <div className="space-y-4">

              {/* ── KPI Row ─────────────────────────────────────────────────── */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                <KPICard label="Total Runs"      value={stats.total_runs}     sub="agent executions"  color="#3b82f6" icon={Activity}  spark={equitySpark} />
                <KPICard label="Signal Rate"     value={`${stats.total_runs ? Math.round(stats.total_signals/stats.total_runs*100) : 0}%`} sub={`${stats.total_signals} signals`} color="#f59e0b" icon={Radio} />
                <KPICard label="Avg Confidence"  value={`${stats.avg_confidence}%`} sub="mean conf score" color="#10b981" icon={Target} />
                <KPICard label="BUY vs SELL"     value={`${stats.buy_signals}B / ${stats.sell_signals}S`} sub={`${stats.no_trade} no-trade`} color="#a855f7" icon={BarChart2} />
              </div>

              {/* ── Equity Curve + Win Rate Donut ──────────────────────────── */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                <div className="sm:col-span-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)]">Equity Curve (Proxy)</p>
                    <span className="text-[7px] font-black px-2 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-dim)]">last {perfData.equity_curve?.length || 0} runs</span>
                  </div>
                  <EquityCurve data={perfData.equity_curve || []} height={120} />
                </div>
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4 flex flex-col items-center justify-center gap-2">
                  <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)]">Signal Distribution</p>
                  <DonutChart
                    pct={stats.total_runs ? Math.round(stats.total_signals / stats.total_runs * 100) : 0}
                    size={100}
                    label="Signal Rate"
                    color="#10b981"
                  />
                  <div className="grid grid-cols-2 gap-2 w-full">
                    <div className="text-center p-2 rounded-lg bg-emerald-400/10 border border-emerald-400/20">
                      <p className="text-lg font-black font-mono text-emerald-400">{stats.buy_signals}</p>
                      <p className="text-[7px] text-[var(--text-dim)] font-black">BUY</p>
                    </div>
                    <div className="text-center p-2 rounded-lg bg-red-400/10 border border-red-400/20">
                      <p className="text-lg font-black font-mono text-red-400">{stats.sell_signals}</p>
                      <p className="text-[7px] text-[var(--text-dim)] font-black">SELL</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* ── Model Performance + Pair Activity ──────────────────────── */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4">
                  <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-3">Model Performance</p>
                  {Object.keys(perfData.model_stats || {}).length > 0 ? (
                    <HBarChart data={perfData.model_stats || {}} />
                  ) : <EmptyChart label="Run agents to see model stats" />}
                </div>
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4">
                  <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-3">Pair Activity</p>
                  <PairBars data={perfData.pair_stats || {}} />
                </div>
              </div>

              {/* ── Confidence Distribution ─────────────────────────────────── */}
              {Object.keys(perfData.confidence_dist || {}).length > 0 && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-4">
                  <div className="flex items-center justify-between mb-3">
                    <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)]">Confidence Distribution</p>
                    <span className="text-[7px] text-[var(--text-dim)] font-bold">Histogram · 5% buckets</span>
                  </div>
                  <VBarChart data={perfData.confidence_dist || {}} color="#3b82f6" height={90} />
                </div>
              )}

              {/* ── Agent Leaderboard ───────────────────────────────────────── */}
              {agents.length > 0 && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
                  <div className="px-4 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)] flex items-center gap-2">
                    <Trophy size={11} className="text-yellow-400" />
                    <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-secondary)]">Agent Leaderboard</p>
                  </div>
                  {/* Header */}
                  <div className="grid grid-cols-7 px-4 py-2 border-b border-[var(--border-color)] bg-[var(--bg-panel)]/60">
                    {['Agent','Model','Style','Win%','Trades','PnL','Status'].map(h => (
                      <p key={h} className="text-[7px] font-black uppercase tracking-wider text-[var(--text-dim)]">{h}</p>
                    ))}
                  </div>
                  {agents.sort((a,b) => (b.pnl||0) - (a.pnl||0)).map((ag, i) => {
                    const m = MODEL(ag.model_id);
                    return (
                      <div key={ag.id} className="grid grid-cols-7 px-4 py-2.5 border-b border-[var(--border-color)] items-center hover:bg-[var(--bg-hover)] transition-colors">
                        <div className="flex items-center gap-1.5">
                          {i === 0 && <Trophy size={9} className="text-yellow-400 shrink-0" />}
                          <span className="text-[8px] font-black truncate">{ag.name}</span>
                        </div>
                        <span className="text-[8px] font-bold" style={{ color: m.color }}>{m.short}</span>
                        <span className="text-[7px] text-[var(--text-dim)] capitalize">{ag.style}</span>
                        <span className={`text-[8px] font-black font-mono ${(ag.winrate||0)>=50 ? 'text-emerald-400' : 'text-red-400'}`}>{ag.winrate||0}%</span>
                        <span className="text-[7px] font-mono text-[var(--text-secondary)]">{ag.trades||0}</span>
                        <span className={`text-[8px] font-black font-mono ${(ag.pnl||0)>=0 ? 'text-emerald-400' : 'text-red-400'}`}>{fmtPnL(ag.pnl)}</span>
                        <StatusBadge status={ag.status} />
                      </div>
                    );
                  })}
                </div>
              )}

              {/* ── Recent History ──────────────────────────────────────────── */}
              {(perfData.history || []).length > 0 && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden">
                  <div className="px-4 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)] flex items-center gap-2">
                    <Clock size={11} className="text-[var(--accent)]" />
                    <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-secondary)]">Recent Runs</p>
                  </div>
                  <div className="divide-y divide-[var(--border-color)]">
                    {perfData.history.slice(0, 12).map((h, i) => {
                      const m = MODEL(h.model);
                      return (
                        <div key={i} className="grid grid-cols-6 px-4 py-2 items-center hover:bg-[var(--bg-hover)] transition-colors">
                          <span className="text-[7px] font-mono text-[var(--text-dim)]">{h.timestamp?.slice(0,16).replace('T',' ') || '--'}</span>
                          <span className="text-[8px] font-bold" style={{ color: m.color }}>{m.short}</span>
                          <span className="text-[7px] text-[var(--text-dim)]">{h.pair}</span>
                          <span className={`text-[8px] font-black px-1.5 py-0.5 rounded border text-center ${sigBg(h.signal)}`}>{h.signal}</span>
                          <span className="text-[7px] font-mono text-center text-[var(--text-dim)]">{h.confidence != null ? `${h.confidence}%` : '--'}</span>
                          <span className={`text-[7px] font-black ${h.outcome === 'WIN' ? 'text-emerald-400' : h.outcome === 'LOSS' ? 'text-red-400' : 'text-[var(--text-dim)]'}`}>{h.outcome || '--'}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* ── Auto-Disable Rules ──────────────────────────────────────── */}
              <div className="bg-[var(--bg-card)] border border-red-400/15 rounded-xl p-4">
                <p className="text-[8px] font-black uppercase tracking-wider text-red-400 mb-3 flex items-center gap-1.5">
                  <Shield size={10} /> Auto-Disable Rules (Active)
                </p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
                  {[
                    { r: 'WR < 40%',    d: 'After 5+ trades', color: 'text-red-400' },
                    { r: 'DD > 8%',     d: '24h cooldown',    color: 'text-orange-400' },
                    { r: 'Max Trades',  d: 'Pause session',   color: 'text-yellow-400' },
                    { r: 'Low Conf',    d: `< ${minConf}% skip`, color: 'text-blue-400' },
                  ].map((r, i) => (
                    <div key={i} className="flex gap-2 p-2 bg-[var(--bg-panel)] rounded-lg border border-[var(--border-color)]">
                      <AlertTriangle size={9} className={`${r.color} shrink-0 mt-0.5`} />
                      <div>
                        <p className={`text-[8px] font-black ${r.color}`}>{r.r}</p>
                        <p className="text-[7px] text-[var(--text-dim)]">{r.d}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* ══════════════════════════ CONFIG TAB ══════════════════════════ */}
      {tab === 'config' && (
        <div className="space-y-4">
          <div>
            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">YAML Config Preview</p>
            <div className="bg-[#0a0d14] border border-[var(--border-color)] rounded-xl p-4 font-mono text-[8px] space-y-0.5">
              {[
                [`name: gas_${selectedModel.short.toLowerCase()}_${style}`, 'text-yellow-400'],
                [`model: ${selectedModel.provider.toLowerCase()}/${selectedModel.name.toLowerCase().replace(/ /g,'.')}`, 'text-yellow-400'],
                [`style: ${style}`, 'text-yellow-400'],
                [`pair: ${pair}`, 'text-yellow-400'],
                ['', ''],
                ['rules:', 'text-blue-400'],
                [`  min_confidence: ${minConf}`, 'text-[var(--text-secondary)]'],
                [`  max_trades: ${maxTrades}`, 'text-[var(--text-secondary)]'],
                ['  avoid_ranging: true', 'text-[var(--text-secondary)]'],
                ['', ''],
                ['timeframes:', 'text-blue-400'],
                [`  trigger: ${triggerTF}`, 'text-[var(--text-secondary)]'],
                [`  trend: ${styleTFs[0]}`, 'text-[var(--text-secondary)]'],
                ['', ''],
                ['output:', 'text-blue-400'],
                ['  signal: BUY | SELL | NO TRADE', 'text-emerald-400'],
                ['  entry: float', 'text-emerald-400'],
                ['  sl: float', 'text-emerald-400'],
                ['  tp: [float, float]', 'text-emerald-400'],
                ['  confidence: int (0-100)', 'text-emerald-400'],
              ].map(([l, c], i) => <div key={i} className={c || 'text-[var(--text-dim)]'}>{l || '\u00A0'}</div>)}
            </div>
          </div>

          <div className="bg-[var(--bg-card)] border border-blue-400/20 rounded-xl p-4">
            <p className="text-[8px] font-black uppercase tracking-wider text-blue-400 mb-3 flex items-center gap-1.5"><Cpu size={10} /> EA MT5 Files</p>
            <div className="grid grid-cols-2 gap-2">
              {AI_MODELS.map(m => (
                <div key={m.id} className="flex items-center gap-2 p-2.5 bg-[var(--bg-panel)] rounded-xl border border-[var(--border-color)]">
                  <span className="text-base">{m.emoji}</span>
                  <div className="flex-1 min-w-0">
                    <p className="text-[8px] font-black text-[var(--text-primary)]">GAS_Agent_{m.short}.mq5</p>
                    <p className="text-[7px] text-[var(--text-dim)]">{m.name} · MAGIC {20260001 + AI_MODELS.indexOf(m)}</p>
                  </div>
                  <CheckCircle2 size={10} style={{ color: m.color }} />
                </div>
              ))}
            </div>
            <p className="text-[7px] text-[var(--text-dim)] mt-2 leading-relaxed">
              Download EA dari panel ini, pasang di MetaTrader 5, isi JWT token dan Agent ID dari dashboard. EA akan polling signal setiap 15 detik.
            </p>
          </div>

          <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4">
            <p className="text-[8px] font-black uppercase tracking-wider text-[var(--text-dim)] mb-3">API Endpoints</p>
            <div className="space-y-1.5 font-mono">
              {[
                ['POST', '/web/api/v1/agent/run',              'Run agent signal (5cr)'],
                ['GET',  '/web/api/v1/agent/agents',           'List your agents'],
                ['POST', '/web/api/v1/agent/agents',           'Create agent'],
                ['GET',  '/web/api/v1/agent/performance',      'Performance stats'],
                ['GET',  '/web/api/v1/agent/history',          'Run history'],
                ['POST', '/web/api/v1/agent/trade/close',      'Record WIN/LOSS'],
              ].map(([method, path, desc], i) => (
                <div key={i} className="flex items-center gap-2 text-[7px]">
                  <span className={`px-1.5 py-0.5 rounded font-black ${method === 'GET' ? 'bg-blue-400/15 text-blue-400' : 'bg-emerald-400/15 text-emerald-400'}`}>{method}</span>
                  <span className="text-[var(--text-secondary)] flex-1">{path}</span>
                  <span className="text-[var(--text-dim)]">{desc}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {showCreate && <CreateAgentModal onClose={() => setShowCreate(false)} onCreate={ag => { setAgents(prev => [...prev, ag]); }} />}
    </div>
  );
}
