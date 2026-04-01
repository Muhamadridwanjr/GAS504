import React, { useState, useEffect, useCallback, useRef } from 'react';
import {
  Users, CreditCard, BarChart2, Mail, Shield, Activity,
  MessageSquare, RefreshCw, Search, Check, X, Send,
  AlertCircle, Settings, Database, Zap, Crown,
  ChevronDown, ChevronUp, Eye, EyeOff, Trash2,
  Bell, TrendingUp, DollarSign, Clock, CheckCircle,
  XCircle, AlertTriangle, Server, Copy, ExternalLink,
  TrendingDown, ArrowUp, ArrowDown
} from 'lucide-react';

const API = '/web/api/v1';
const MONO = "'JetBrains Mono','Fira Mono','Courier New',monospace";
const ACCENT = '#facc15';

const getHeaders = () => ({
  'Content-Type': 'application/json',
  Authorization: `Bearer ${localStorage.getItem('gas-token') || ''}`,
});

const apiFetch = async (path, opts = {}) => {
  const res = await fetch(`${API}${path}`, { headers: getHeaders(), ...opts });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
};

// ─── Theme tokens ─────────────────────────────────────────────────────────────
function buildTokens(theme) {
  if (theme === 'light') {
    return {
      bg: '#f1f5f9',
      bgCard: '#ffffff',
      bgPanel: '#f8fafc',
      bgHover: 'rgba(0,0,0,0.02)',
      border: 'rgba(0,0,0,0.08)',
      borderAccent: 'rgba(250,204,21,0.3)',
      text: '#0f172a',
      textDim: 'rgba(15,23,42,0.4)',
      textMid: 'rgba(15,23,42,0.6)',
      tableHead: 'rgba(0,0,0,0.03)',
      inputBg: 'rgba(0,0,0,0.04)',
    };
  }
  return {
    bg: '#080c14',
    bgCard: '#0f1520',
    bgPanel: '#0a0f1a',
    bgHover: 'rgba(255,255,255,0.03)',
    border: 'rgba(255,255,255,0.07)',
    borderAccent: 'rgba(250,204,21,0.25)',
    text: '#e2e8f0',
    textDim: 'rgba(226,232,240,0.4)',
    textMid: 'rgba(226,232,240,0.65)',
    tableHead: 'rgba(255,255,255,0.04)',
    inputBg: 'rgba(255,255,255,0.04)',
  };
}

// ─── SVG Chart Components ──────────────────────────────────────────────────────
const PLAN_COLORS = {
  ultimate: '#a78bfa',
  premium: '#f472b6',
  plus: '#60a5fa',
  essential: '#34d399',
  free: '#6b7280',
};

function PlanDonut({ plans }) {
  const entries = Object.entries(plans || {});
  const total = entries.reduce((s, [, v]) => s + v, 0);
  if (total === 0) return (
    <svg width={80} height={80} viewBox="0 0 80 80">
      <circle cx={40} cy={40} r={28} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth={10} />
    </svg>
  );

  const r = 28;
  const cx = 40;
  const cy = 40;
  const circumference = 2 * Math.PI * r;
  let offset = 0;

  const segments = entries.map(([plan, count]) => {
    const pct = count / total;
    const dash = pct * circumference;
    const gap = circumference - dash;
    const rotation = offset * 360 - 90;
    offset += pct;
    return { plan, count, dash, gap, rotation, color: PLAN_COLORS[plan] || '#6b7280' };
  });

  return (
    <svg width={80} height={80} viewBox="0 0 80 80">
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="rgba(255,255,255,0.04)" strokeWidth={10} />
      {segments.map((s) => (
        <circle
          key={s.plan}
          cx={cx} cy={cy} r={r}
          fill="none"
          stroke={s.color}
          strokeWidth={10}
          strokeDasharray={`${s.dash} ${s.gap}`}
          strokeDashoffset={0}
          transform={`rotate(${s.rotation} ${cx} ${cy})`}
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
      ))}
      <text x={cx} y={cy + 4} textAnchor="middle" fill="#facc15"
        style={{ fontSize: 11, fontFamily: MONO, fontWeight: 700 }}>
        {total}
      </text>
    </svg>
  );
}

function PlanBars({ plans, T }) {
  const entries = Object.entries(plans || {});
  const max = Math.max(...entries.map(([, v]) => v), 1);
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 6, flex: 1 }}>
      {entries.map(([plan, count]) => {
        const pct = (count / max) * 100;
        const color = PLAN_COLORS[plan] || '#6b7280';
        return (
          <div key={plan} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <span style={{ width: 60, fontSize: 10, fontFamily: MONO, color: T.textMid, textTransform: 'capitalize', textAlign: 'right' }}>
              {plan}
            </span>
            <div style={{ flex: 1, height: 8, background: T.inputBg, borderRadius: 4, overflow: 'hidden' }}>
              <div style={{
                width: `${pct}%`, height: '100%', borderRadius: 4,
                background: color, transition: 'width 0.6s ease',
              }} />
            </div>
            <span style={{ width: 24, fontSize: 10, fontFamily: MONO, color, textAlign: 'right' }}>{count}</span>
          </div>
        );
      })}
    </div>
  );
}

function Sparkline({ data = [], color = ACCENT, width = 80, height = 28 }) {
  if (!data || data.length < 2) return <svg width={width} height={height} />;
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;
  const padY = 3;
  const pts = data.map((v, i) => {
    const x = (i / (data.length - 1)) * width;
    const y = height - padY - ((v - min) / range) * (height - padY * 2);
    return `${x},${y}`;
  }).join(' ');
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      <polyline points={pts} fill="none" stroke={color} strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
    </svg>
  );
}

function MiniBarChart({ data = [], color = ACCENT, width = 120, height = 40, T }) {
  if (!data || data.length === 0) return <svg width={width} height={height} />;
  const max = Math.max(...data, 1);
  const n = data.length;
  const gap = 2;
  const barW = (width - gap * (n - 1)) / n;
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      {data.map((v, i) => {
        const bh = Math.max(2, (v / max) * (height - 2));
        const x = i * (barW + gap);
        const y = height - bh;
        return (
          <rect key={i} x={x} y={y} width={barW} height={bh} rx={2}
            fill={color} fillOpacity={0.7 + 0.3 * (v / max)} />
        );
      })}
    </svg>
  );
}

// ─── Shared UI Primitives ─────────────────────────────────────────────────────
function TBadge({ color = 'yellow', children }) {
  const map = {
    yellow: { bg: 'rgba(250,204,21,0.12)', border: 'rgba(250,204,21,0.3)', text: '#facc15' },
    green:  { bg: 'rgba(52,211,153,0.10)', border: 'rgba(52,211,153,0.3)', text: '#34d399' },
    red:    { bg: 'rgba(248,113,113,0.10)', border: 'rgba(248,113,113,0.3)', text: '#f87171' },
    blue:   { bg: 'rgba(96,165,250,0.10)', border: 'rgba(96,165,250,0.3)', text: '#60a5fa' },
    purple: { bg: 'rgba(167,139,250,0.10)', border: 'rgba(167,139,250,0.3)', text: '#a78bfa' },
    gray:   { bg: 'rgba(107,114,128,0.12)', border: 'rgba(107,114,128,0.25)', text: '#9ca3af' },
    pink:   { bg: 'rgba(244,114,182,0.10)', border: 'rgba(244,114,182,0.3)', text: '#f472b6' },
  };
  const c = map[color] || map.gray;
  return (
    <span style={{
      display: 'inline-flex', alignItems: 'center', gap: 4,
      background: c.bg, border: `1px solid ${c.border}`, color: c.text,
      fontSize: 9, fontWeight: 700, letterSpacing: '0.06em',
      padding: '2px 7px', borderRadius: 99, textTransform: 'uppercase',
      fontFamily: MONO,
    }}>
      {children}
    </span>
  );
}

function TChip({ status }) {
  const map = {
    completed:  { color: 'green',  label: 'Completed' },
    pending:    { color: 'yellow', label: 'Pending' },
    expired:    { color: 'gray',   label: 'Expired' },
    open:       { color: 'blue',   label: 'Open' },
    replied:    { color: 'green',  label: 'Replied' },
    ai_replied: { color: 'purple', label: 'AI' },
    healthy:    { color: 'green',  label: 'Healthy' },
    degraded:   { color: 'yellow', label: 'Degraded' },
    error:      { color: 'red',    label: 'Error' },
    unknown:    { color: 'gray',   label: 'Unknown' },
  };
  const s = map[status] || { color: 'gray', label: status };
  return <TBadge color={s.color}>{s.color === 'green' ? '● ' : s.color === 'red' ? '● ' : ''}{s.label}</TBadge>;
}

function TBtn({ onClick, children, variant = 'yellow', size = 'sm', loading, disabled, style = {} }) {
  const variants = {
    yellow: { background: ACCENT, color: '#000', border: 'none' },
    red:    { background: 'rgba(239,68,68,0.15)', color: '#f87171', border: '1px solid rgba(239,68,68,0.3)' },
    green:  { background: 'rgba(52,211,153,0.12)', color: '#34d399', border: '1px solid rgba(52,211,153,0.3)' },
    ghost:  { background: 'rgba(255,255,255,0.04)', color: 'rgba(226,232,240,0.65)', border: '1px solid rgba(255,255,255,0.08)' },
  };
  const v = variants[variant] || variants.ghost;
  const pad = size === 'sm' ? '5px 12px' : '8px 18px';
  const fz = size === 'sm' ? 11 : 13;
  return (
    <button
      onClick={onClick}
      disabled={disabled || loading}
      style={{
        display: 'inline-flex', alignItems: 'center', gap: 5,
        padding: pad, borderRadius: 8, fontSize: fz, fontWeight: 700,
        cursor: (disabled || loading) ? 'not-allowed' : 'pointer',
        opacity: (disabled || loading) ? 0.5 : 1,
        transition: 'all 0.15s', fontFamily: 'inherit',
        ...v, ...style,
      }}
    >
      {loading && <RefreshCw size={11} className="animate-spin" />}
      {children}
    </button>
  );
}

function TInput({ value, onChange, placeholder, type = 'text', T, style = {} }) {
  return (
    <input
      type={type}
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={placeholder}
      style={{
        background: T.inputBg,
        border: `1px solid ${T.border}`,
        borderRadius: 8,
        padding: '8px 12px',
        fontSize: 13,
        color: T.text,
        width: '100%',
        outline: 'none',
        fontFamily: 'inherit',
        boxSizing: 'border-box',
        ...style,
      }}
      onFocus={e => { e.target.style.borderColor = 'rgba(250,204,21,0.5)'; }}
      onBlur={e => { e.target.style.borderColor = T.border; }}
    />
  );
}

function SectionHdr({ title, sub, icon: Icon, action, T }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 16 }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <div style={{
          width: 32, height: 32, borderRadius: 8,
          background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.2)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon size={14} style={{ color: ACCENT }} />
        </div>
        <div>
          <div style={{ fontSize: 12, fontWeight: 800, color: T.text, letterSpacing: '-0.01em' }}>{title}</div>
          {sub && <div style={{ fontSize: 10, color: T.textDim, marginTop: 1 }}>{sub}</div>}
        </div>
      </div>
      {action}
    </div>
  );
}

function StatCard({ icon: Icon, label, value, sub, color = ACCENT, spark, T }) {
  return (
    <div style={{
      background: T.bgCard, border: `1px solid ${T.border}`,
      borderRadius: 16, padding: 20, display: 'flex', flexDirection: 'column', gap: 8,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 10, fontWeight: 700, color: T.textDim, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
          {label}
        </span>
        <div style={{
          width: 30, height: 30, borderRadius: 8, flexShrink: 0,
          background: `${color}15`, border: `1px solid ${color}25`,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <Icon size={13} style={{ color }} />
        </div>
      </div>
      <div style={{ fontSize: 26, fontWeight: 900, color, fontFamily: MONO, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 10, color: T.textDim }}>{sub}</div>}
      {spark && (
        <div style={{ position: 'absolute', bottom: 12, right: 16, opacity: 0.6 }}>
          <Sparkline data={spark} color={color} width={72} height={22} />
        </div>
      )}
    </div>
  );
}

// ─── Tab: DASHBOARD ────────────────────────────────────────────────────────────
function DashboardTab({ T }) {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [s, h] = await Promise.all([
        apiFetch('/admin/stats'),
        apiFetch('/admin/health'),
      ]);
      setStats(s);
      setHealth(h);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: 180, color: ACCENT }}>
      <RefreshCw size={22} className="animate-spin" />
    </div>
  );

  const planColor = (p) => {
    const map = { ultimate: 'purple', premium: 'pink', plus: 'blue', essential: 'green', free: 'gray' };
    return map[p] || 'gray';
  };

  const actionTagColor = (action = '') => {
    if (action.includes('payment') || action.includes('credit')) return '#34d399';
    if (action.includes('broadcast') || action.includes('email')) return '#60a5fa';
    if (action.includes('admin')) return '#a78bfa';
    return ACCENT;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
      {/* 4 Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: 12 }}>
        <StatCard icon={Users}       label="Total Users"    value={stats?.total_users || 0}                 sub="Registered accounts"      color={ACCENT}     spark={[3,5,4,7,6,9,8]}   T={T} />
        <StatCard icon={DollarSign}  label="Revenue USDT"   value={`$${stats?.total_revenue_usdt || 0}`}    sub="All completed payments"   color="#10b981"     spark={[2,4,3,6,5,8,7]}   T={T} />
        <StatCard icon={CreditCard}  label="Payments Done"  value={stats?.completed_payments || 0}          sub="ERC20 confirmed"          color="#60a5fa"     spark={[1,3,2,5,4,7,6]}   T={T} />
        <StatCard icon={MessageSquare} label="Open Tickets" value={stats?.open_support_tickets || 0}        sub="Need response"            color="#f472b6"     spark={[4,3,5,2,6,3,4]}   T={T} />
      </div>

      {/* Plan Distribution */}
      <div style={{ background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 16, padding: 20 }}>
        <SectionHdr title="Plan Distribution" sub="Active user plan breakdown" icon={Crown} T={T} />
        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <div style={{ flexShrink: 0 }}>
            <PlanDonut plans={stats?.plans || {}} />
          </div>
          <PlanBars plans={stats?.plans || {}} T={T} />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
            {Object.entries(stats?.plans || {}).map(([plan, count]) => (
              <div key={plan} style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <div style={{ width: 8, height: 8, borderRadius: '50%', background: PLAN_COLORS[plan] || '#6b7280', flexShrink: 0 }} />
                <span style={{ fontSize: 10, color: T.textMid, textTransform: 'capitalize', minWidth: 58 }}>{plan}</span>
                <span style={{ fontSize: 10, fontFamily: MONO, fontWeight: 700, color: PLAN_COLORS[plan] || '#6b7280' }}>{count}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Service Health */}
      <div style={{ background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 16, padding: 20 }}>
        <SectionHdr title="Service Health" sub="Live status check" icon={Server} T={T}
          action={<TBtn onClick={load} variant="ghost" size="sm"><RefreshCw size={11} />Refresh</TBtn>} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {health?.services && Object.entries(health.services).map(([name, svc]) => {
            const ok = svc.status === 'healthy';
            return (
              <div key={name} style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '10px 14px', background: T.bgPanel,
                border: `1px solid ${T.border}`, borderRadius: 10,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{
                    width: 8, height: 8, borderRadius: '50%',
                    background: ok ? '#34d399' : '#f87171',
                    boxShadow: `0 0 6px ${ok ? '#34d39960' : '#f8717160'}`,
                  }} className={ok ? 'animate-pulse' : ''} />
                  <span style={{ fontSize: 12, fontWeight: 700, color: T.text }}>{name.replace(/_/g, ' ')}</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 10, fontFamily: MONO, color: T.textDim }}>
                    {svc.url?.replace(/https?:\/\/[^/]+/, '') || ''}
                  </span>
                  <TChip status={ok ? 'healthy' : 'error'} />
                  <div style={{ width: 48, height: 4, background: T.inputBg, borderRadius: 2, overflow: 'hidden' }}>
                    <div style={{
                      height: '100%', borderRadius: 2, background: ok ? '#34d399' : '#f87171',
                      width: ok ? `${60 + Math.random() * 35}%` : '20%',
                    }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Platform Overview 2x2 grid */}
      <div style={{ background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 16, padding: 20 }}>
        <SectionHdr title="Platform Overview" sub="Key metrics snapshot" icon={BarChart2} T={T} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
          {[
            { label: 'Active Users (30d)', value: stats?.active_users_30d ?? '—', color: ACCENT, trend: 'up' },
            { label: 'Avg Credits/User', value: stats?.avg_credits ?? '—', color: '#60a5fa', trend: 'up' },
            { label: 'Avg XP/User', value: stats?.avg_xp ?? '—', color: '#34d399', trend: 'up' },
            { label: 'Pending TX', value: stats?.pending || 0, color: '#f472b6', trend: 'down' },
          ].map(m => (
            <div key={m.label} style={{
              background: T.bgPanel, border: `1px solid ${T.border}`,
              borderRadius: 10, padding: '12px 14px',
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            }}>
              <div>
                <div style={{ fontSize: 10, color: T.textDim, marginBottom: 4 }}>{m.label}</div>
                <div style={{ fontSize: 18, fontWeight: 800, fontFamily: MONO, color: m.color }}>{m.value}</div>
              </div>
              <div style={{ opacity: 0.5 }}>
                {m.trend === 'up'
                  ? <ArrowUp size={16} style={{ color: '#34d399' }} />
                  : <ArrowDown size={16} style={{ color: '#f87171' }} />}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Activity Log — terminal stream */}
      <div style={{ background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 16, overflow: 'hidden' }}>
        <div style={{
          padding: '10px 16px', background: T.bgPanel, borderBottom: `1px solid ${T.border}`,
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#34d399' }} className="animate-pulse" />
          <span style={{ fontSize: 10, fontFamily: MONO, color: T.textDim }}>GAS Admin Activity Stream</span>
          <SectionHdr title="" sub="" icon={() => null} T={T} action={null} />
        </div>
        <div style={{ padding: 14 }}>
          <div style={{ fontSize: 12, fontWeight: 800, color: T.text, marginBottom: 10 }}>Recent Activity</div>
          <div style={{ maxHeight: 240, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 1 }}>
            {(stats?.recent_logs || []).length === 0 && (
              <p style={{ fontSize: 11, color: T.textDim, textAlign: 'center', padding: '20px 0' }}>No recent activity</p>
            )}
            {(stats?.recent_logs || []).map((log, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 10, padding: '5px 8px',
                borderRadius: 6, transition: 'background 0.15s',
              }}
                onMouseEnter={e => e.currentTarget.style.background = T.bgHover}
                onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
              >
                <span style={{ width: 6, height: 6, borderRadius: '50%', background: actionTagColor(log.action), flexShrink: 0 }} />
                <span style={{ fontSize: 10, fontFamily: MONO, fontWeight: 700, color: actionTagColor(log.action), flexShrink: 0, minWidth: 120 }}>
                  {log.action}
                </span>
                <span style={{ fontSize: 10, color: T.textMid, flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                  {log.detail}
                </span>
                <span style={{ fontSize: 9, fontFamily: MONO, color: T.textDim, flexShrink: 0 }}>
                  {new Date(log.ts).toLocaleTimeString('id-ID')}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Tab: USERS ────────────────────────────────────────────────────────────────
function UsersTab({ T }) {
  const [users, setUsers]     = useState([]);
  const [total, setTotal]     = useState(0);
  const [search, setSearch]   = useState('');
  const [loading, setLoading] = useState(false);
  const [editUser, setEditUser] = useState(null);
  const [editPlan, setEditPlan] = useState('');
  const [editCredits, setEditCredits] = useState('');
  const [saving, setSaving]   = useState(false);
  const [msg, setMsg]         = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await apiFetch(`/admin/users?search=${encodeURIComponent(search)}&limit=100`);
      setUsers(d.users || []);
      setTotal(d.total || 0);
    } catch (e) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setLoading(false);
    }
  }, [search]);

  useEffect(() => { load(); }, []);

  const planColorKey = { ultimate: 'purple', premium: 'pink', plus: 'blue', essential: 'green', free: 'gray' };
  const planGradient = {
    ultimate: 'linear-gradient(135deg,#a78bfa,#7c3aed)',
    premium:  'linear-gradient(135deg,#f472b6,#db2777)',
    plus:     'linear-gradient(135deg,#60a5fa,#2563eb)',
    essential:'linear-gradient(135deg,#34d399,#059669)',
    free:     'linear-gradient(135deg,#6b7280,#374151)',
  };

  const openEdit = (u) => {
    setEditUser(u);
    setEditPlan(u.plan || 'free');
    setEditCredits(String(u.credits || 0));
    setMsg('');
  };

  const saveUser = async () => {
    if (!editUser) return;
    setSaving(true);
    try {
      await apiFetch(`/admin/users/${editUser.id}/set-plan`, {
        method: 'POST',
        body: JSON.stringify({ plan: editPlan, credits: parseInt(editCredits) || 0 }),
      });
      setMsg('Saved successfully!');
      load();
      setTimeout(() => { setEditUser(null); setMsg(''); }, 1500);
    } catch (e) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setSaving(false);
    }
  };

  const toggleActive = async (u) => {
    try {
      await apiFetch(`/admin/users/${u.id}/toggle-active`, { method: 'POST' });
      load();
    } catch (e) {
      setMsg(`Error: ${e.message}`);
    }
  };

  const thStyle = {
    padding: '10px 14px', fontSize: 9, fontWeight: 700,
    color: T.textDim, textTransform: 'uppercase', letterSpacing: '0.07em',
    background: T.tableHead, textAlign: 'left', borderBottom: `1px solid ${T.border}`,
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Search bar */}
      <div style={{ display: 'flex', gap: 8 }}>
        <div style={{ flex: 1, position: 'relative' }}>
          <Search size={13} style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: T.textDim }} />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && load()}
            placeholder="Search username / email..."
            style={{
              width: '100%', boxSizing: 'border-box',
              background: T.inputBg, border: `1px solid ${T.border}`,
              borderRadius: 8, paddingLeft: 34, paddingRight: 12, paddingTop: 8, paddingBottom: 8,
              fontSize: 12, color: T.text, outline: 'none', fontFamily: 'inherit',
            }}
            onFocus={e => e.target.style.borderColor = 'rgba(250,204,21,0.5)'}
            onBlur={e => e.target.style.borderColor = T.border}
          />
        </div>
        <TBtn onClick={load} loading={loading} variant="ghost" size="sm"><RefreshCw size={11} />Refresh</TBtn>
      </div>

      <div style={{ fontSize: 10, color: T.textDim }}>{total} total users</div>

      {msg && (
        <div style={{ padding: '10px 14px', background: 'rgba(250,204,21,0.08)', border: '1px solid rgba(250,204,21,0.25)', borderRadius: 8, fontSize: 12, color: ACCENT }}>
          {msg}
        </div>
      )}

      {/* Table */}
      <div style={{ background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 14, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
            <thead>
              <tr>
                <th style={thStyle}>User</th>
                <th style={thStyle}>Email</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Plan</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Credits</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>XP</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Status</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '30px', color: T.textDim }}>
                    <RefreshCw size={15} className="animate-spin" style={{ display: 'inline', marginRight: 6 }} />
                    Loading...
                  </td>
                </tr>
              )}
              {!loading && users.map((u, idx) => (
                <tr key={u.id}
                  style={{ borderBottom: `1px solid ${T.border}`, transition: 'background 0.12s' }}
                  onMouseEnter={e => e.currentTarget.style.background = T.bgHover}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '10px 14px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{
                        width: 28, height: 28, borderRadius: '50%', flexShrink: 0,
                        background: planGradient[u.plan] || planGradient.free,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 9, fontWeight: 900, color: '#fff',
                      }}>
                        {(u.username || u.email || 'U').slice(0, 2).toUpperCase()}
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, color: T.text }}>{u.username || '—'}</div>
                        {u.full_name && <div style={{ fontSize: 9, color: T.textDim }}>{u.full_name}</div>}
                        {u.role === 'admin' && <TBadge color="red">ADMIN</TBadge>}
                      </div>
                    </div>
                  </td>
                  <td style={{ padding: '10px 14px', fontFamily: MONO, fontSize: 10, color: T.textMid }}>{u.email || '—'}</td>
                  <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                    <TBadge color={planColorKey[u.plan] || 'gray'}>
                      <span style={{ width: 5, height: 5, borderRadius: '50%', background: PLAN_COLORS[u.plan] || '#6b7280', display: 'inline-block', marginRight: 3 }} />
                      {(u.plan || 'free').toUpperCase()}
                    </TBadge>
                  </td>
                  <td style={{ padding: '10px 14px', textAlign: 'center', fontFamily: MONO, fontWeight: 700, color: ACCENT }}>{u.credits || 0}</td>
                  <td style={{ padding: '10px 14px', textAlign: 'center', fontFamily: MONO, color: '#60a5fa' }}>{u.xp || 0}</td>
                  <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                    <TChip status={u.is_active ? 'completed' : 'error'} />
                  </td>
                  <td style={{ padding: '10px 14px', textAlign: 'center' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 4 }}>
                      <TBtn onClick={() => openEdit(u)} variant="ghost" size="sm">Edit</TBtn>
                      <TBtn onClick={() => toggleActive(u)} variant={u.is_active ? 'red' : 'green'} size="sm">
                        {u.is_active ? <X size={10} /> : <Check size={10} />}
                      </TBtn>
                    </div>
                  </td>
                </tr>
              ))}
              {!loading && users.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '30px', color: T.textDim, fontSize: 12 }}>
                    No users found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Edit modal */}
      {editUser && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 500, display: 'flex',
          alignItems: 'center', justifyContent: 'center',
          background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)', padding: 16,
        }}>
          <div style={{
            background: T.bgCard, border: `1px solid ${T.borderAccent}`,
            borderRadius: 20, padding: 24, width: '100%', maxWidth: 400,
            boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
              <div>
                <div style={{ fontSize: 13, fontWeight: 800, color: T.text }}>Edit User</div>
                <div style={{ fontSize: 10, color: T.textDim, fontFamily: MONO }}>@{editUser.username}</div>
              </div>
              <button onClick={() => setEditUser(null)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: T.textDim, padding: 4 }}>
                <X size={15} />
              </button>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
              <div>
                <label style={{ fontSize: 10, fontWeight: 700, color: T.textDim, display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Plan</label>
                <select
                  value={editPlan}
                  onChange={e => setEditPlan(e.target.value)}
                  style={{
                    width: '100%', background: T.inputBg, border: `1px solid ${T.border}`,
                    borderRadius: 8, padding: '8px 12px', fontSize: 13, color: T.text,
                    outline: 'none', fontFamily: 'inherit',
                  }}
                >
                  {['free', 'essential', 'plus', 'premium', 'ultimate'].map(p => (
                    <option key={p} value={p}>{p.charAt(0).toUpperCase() + p.slice(1)}</option>
                  ))}
                </select>
              </div>
              <div>
                <label style={{ fontSize: 10, fontWeight: 700, color: T.textDim, display: 'block', marginBottom: 6, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Credits</label>
                <TInput value={editCredits} onChange={setEditCredits} placeholder="Credits" type="number" T={T} />
              </div>
              {msg && (
                <div style={{ fontSize: 12, color: msg.includes('Error') ? '#f87171' : '#34d399', fontWeight: 600 }}>{msg}</div>
              )}
              <div style={{ display: 'flex', gap: 8, paddingTop: 4 }}>
                <TBtn onClick={saveUser} loading={saving} style={{ flex: 1 }}>Save Changes</TBtn>
                <TBtn onClick={() => setEditUser(null)} variant="ghost">Cancel</TBtn>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Tab: PAYMENTS ─────────────────────────────────────────────────────────────
function PaymentsTab({ T }) {
  const [data, setData]       = useState({ payments: [], total: 0, completed: 0, pending: 0 });
  const [filter, setFilter]   = useState('');
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await apiFetch(`/admin/payments?limit=100${filter ? `&status_filter=${filter}` : ''}`);
      setData(d);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => { load(); }, [filter]);

  const copyTx = (hash) => { navigator.clipboard.writeText(hash); };

  const thStyle = {
    padding: '10px 14px', fontSize: 9, fontWeight: 700,
    color: T.textDim, textTransform: 'uppercase', letterSpacing: '0.07em',
    background: T.tableHead, textAlign: 'left', borderBottom: `1px solid ${T.border}`,
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      {/* Stat cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <StatCard icon={CheckCircle} label="Completed" value={data.completed} color="#10b981" spark={[2,4,3,6,5,8,7]} T={T} />
        <StatCard icon={Clock}       label="Pending"   value={data.pending}   color={ACCENT}   spark={[3,2,5,3,4,2,3]} T={T} />
        <StatCard icon={Database}    label="Total"     value={data.total}     color="#60a5fa"  spark={[4,6,5,8,7,9,8]} T={T} />
      </div>

      {/* Filter pills */}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
        {['', 'completed', 'pending', 'expired'].map(f => (
          <TBtn key={f} onClick={() => setFilter(f)} variant={filter === f ? 'yellow' : 'ghost'} size="sm">
            {f || 'All'}
          </TBtn>
        ))}
        <TBtn onClick={load} loading={loading} variant="ghost" size="sm" style={{ marginLeft: 'auto' }}>
          <RefreshCw size={11} />Refresh
        </TBtn>
      </div>

      {/* Table */}
      <div style={{ background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 14, overflow: 'hidden' }}>
        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 11 }}>
            <thead>
              <tr>
                <th style={thStyle}>Order ID</th>
                <th style={thStyle}>User</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Package</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>USDT</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Credits</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>Status</th>
                <th style={{ ...thStyle, textAlign: 'center' }}>TX</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: 30, color: T.textDim }}>
                    <RefreshCw size={15} className="animate-spin" style={{ display: 'inline' }} />
                  </td>
                </tr>
              )}
              {!loading && data.payments.map((p, i) => (
                <tr key={i}
                  style={{ borderBottom: `1px solid ${T.border}` }}
                  onMouseEnter={e => e.currentTarget.style.background = T.bgHover}
                  onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                >
                  <td style={{ padding: '9px 14px' }}>
                    <code style={{ fontSize: 10, color: ACCENT, fontFamily: MONO }}>{p.order_id}</code>
                  </td>
                  <td style={{ padding: '9px 14px', fontFamily: MONO, fontSize: 10, color: T.textMid }}>
                    {p.user_id?.slice(0, 12)}...
                  </td>
                  <td style={{ padding: '9px 14px', textAlign: 'center', color: T.text }}>{p.label}</td>
                  <td style={{ padding: '9px 14px', textAlign: 'center', fontFamily: MONO, fontWeight: 700, color: '#34d399' }}>{p.amount_usdt}</td>
                  <td style={{ padding: '9px 14px', textAlign: 'center', fontFamily: MONO, color: ACCENT }}>{p.credits}</td>
                  <td style={{ padding: '9px 14px', textAlign: 'center' }}><TChip status={p.status} /></td>
                  <td style={{ padding: '9px 14px', textAlign: 'center' }}>
                    {p.tx_hash ? (
                      <button onClick={() => copyTx(p.tx_hash)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#60a5fa', padding: 4 }}>
                        <Copy size={12} />
                      </button>
                    ) : <span style={{ color: T.textDim }}>—</span>}
                  </td>
                </tr>
              ))}
              {!loading && data.payments.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: 30, color: T.textDim, fontSize: 12 }}>
                    No payment data found
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

// ─── Tab: SUPPORT ──────────────────────────────────────────────────────────────
function SupportTab({ T }) {
  const [data, setData]       = useState({ tickets: [], total: 0, open: 0 });
  const [loading, setLoading] = useState(false);
  const [selected, setSelected] = useState(null);
  const [reply, setReply]     = useState('');
  const [sending, setSending] = useState(false);
  const [msg, setMsg]         = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await apiFetch('/admin/support?limit=100');
      setData(d);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, []);

  const sendReply = async () => {
    if (!reply.trim() || !selected) return;
    setSending(true);
    setMsg('');
    try {
      await apiFetch(`/admin/support/${selected.ticket_id}/reply`, {
        method: 'POST',
        body: JSON.stringify({ reply }),
      });
      setMsg('Reply sent!');
      setReply('');
      load();
      setTimeout(() => { setSelected(null); setMsg(''); }, 1500);
    } catch (e) {
      setMsg(`Error: ${e.message}`);
    } finally {
      setSending(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <StatCard icon={MessageSquare} label="Total Tickets" value={data.total} color={ACCENT}  spark={[2,3,2,4,3,5,4]} T={T} />
        <StatCard icon={AlertCircle}   label="Open"          value={data.open}  color="#f87171" spark={[3,4,3,5,2,4,3]} T={T} />
        <StatCard icon={CheckCircle}   label="Replied"       value={data.replied || 0} color="#34d399" spark={[1,2,3,4,3,5,4]} T={T} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 12, fontWeight: 800, color: T.text }}>Support Tickets</span>
        <TBtn onClick={load} loading={loading} variant="ghost" size="sm"><RefreshCw size={11} />Refresh</TBtn>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {data.tickets.map((t, i) => {
          const open = selected?.ticket_id === t.ticket_id;
          return (
            <div key={i}
              style={{
                background: T.bgCard,
                border: `1px solid ${open ? T.borderAccent : T.border}`,
                borderRadius: 14, overflow: 'hidden',
                transition: 'border-color 0.2s',
              }}
            >
              {/* Ticket header */}
              <div
                style={{ padding: '12px 16px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12 }}
                onClick={() => setSelected(open ? null : t)}
              >
                <div style={{
                  width: 36, height: 36, borderRadius: 10, flexShrink: 0,
                  background: t.status === 'open' ? 'rgba(96,165,250,0.12)' : 'rgba(52,211,153,0.10)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <MessageSquare size={14} style={{ color: t.status === 'open' ? '#60a5fa' : '#34d399' }} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: 3 }}>
                    <span style={{ fontSize: 9, fontFamily: MONO, color: ACCENT }}>{t.ticket_id}</span>
                    <TChip status={t.status} />
                  </div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: T.text, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {t.subject}
                  </div>
                  <div style={{ fontSize: 10, color: T.textDim, marginTop: 2 }}>
                    {t.name} · {t.email} · {new Date(t.created_at * 1000).toLocaleString('id-ID')}
                  </div>
                </div>
                <div style={{ color: T.textDim, flexShrink: 0 }}>
                  {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </div>
              </div>

              {/* Expanded body */}
              {open && (
                <div style={{ padding: '0 16px 16px', borderTop: `1px solid ${T.border}` }}
                  onClick={e => e.stopPropagation()}
                >
                  {/* Original message */}
                  <div style={{ background: T.bgPanel, borderLeft: `3px solid ${T.textDim}`, borderRadius: '0 8px 8px 0', padding: '10px 14px', margin: '12px 0 10px' }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: T.textDim, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 6 }}>Original Message</div>
                    <p style={{ fontSize: 12, color: T.textMid, lineHeight: 1.6 }}>{t.message}</p>
                  </div>

                  {/* AI Reply */}
                  {t.ai_reply && (
                    <div style={{ background: 'rgba(250,204,21,0.05)', borderLeft: `3px solid ${ACCENT}`, borderRadius: '0 8px 8px 0', padding: '10px 14px', marginBottom: 10 }}>
                      <div style={{ fontSize: 9, fontWeight: 700, color: ACCENT, textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 6 }}>AI Reply</div>
                      <p style={{ fontSize: 12, color: T.textMid, lineHeight: 1.6 }}>{t.ai_reply}</p>
                    </div>
                  )}

                  {/* Manual reply box */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                    <div style={{ fontSize: 9, fontWeight: 700, color: T.textDim, textTransform: 'uppercase', letterSpacing: '0.07em' }}>Send Manual Reply</div>
                    <textarea
                      value={reply}
                      onChange={e => setReply(e.target.value)}
                      placeholder="Write your reply..."
                      rows={3}
                      style={{
                        width: '100%', boxSizing: 'border-box',
                        background: T.inputBg, border: `1px solid ${T.border}`,
                        borderRadius: 8, padding: '8px 12px', fontSize: 12,
                        color: T.text, outline: 'none', fontFamily: 'inherit', resize: 'none',
                      }}
                      onFocus={e => e.target.style.borderColor = 'rgba(250,204,21,0.5)'}
                      onBlur={e => e.target.style.borderColor = T.border}
                    />
                    {msg && (
                      <div style={{ fontSize: 12, color: msg.includes('Error') ? '#f87171' : '#34d399', fontWeight: 600 }}>{msg}</div>
                    )}
                    <TBtn onClick={sendReply} loading={sending} size="sm">
                      <Send size={11} />Send Reply + Email
                    </TBtn>
                  </div>
                </div>
              )}
            </div>
          );
        })}
        {!loading && data.tickets.length === 0 && (
          <div style={{ textAlign: 'center', padding: '48px 0', color: T.textDim }}>
            <MessageSquare size={30} style={{ opacity: 0.3, display: 'block', margin: '0 auto 8px' }} />
            <p style={{ fontSize: 12 }}>No support tickets yet</p>
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Tab: EMAIL ────────────────────────────────────────────────────────────────
function EmailTab({ T }) {
  const [toEmail, setToEmail]     = useState('');
  const [emailType, setEmailType] = useState('test');
  const [loading, setLoading]     = useState(false);
  const [result, setResult]       = useState(null);

  const [broadcast, setBroadcast] = useState({ subject: '', message: '', target: 'all' });
  const [bLoading, setBLoading]   = useState(false);
  const [bResult, setBResult]     = useState(null);

  const sendTest = async () => {
    if (!toEmail) return;
    setLoading(true);
    setResult(null);
    try {
      const d = await apiFetch('/admin/email/test', {
        method: 'POST',
        body: JSON.stringify({ to_email: toEmail, email_type: emailType }),
      });
      setResult({ ok: true, msg: d.message });
    } catch (e) {
      setResult({ ok: false, msg: e.message });
    } finally {
      setLoading(false);
    }
  };

  const sendBroadcast = async () => {
    if (!broadcast.subject || !broadcast.message) return;
    if (!window.confirm(`Send broadcast to all "${broadcast.target}" plan users?`)) return;
    setBLoading(true);
    setBResult(null);
    try {
      const d = await apiFetch('/admin/broadcast', {
        method: 'POST',
        body: JSON.stringify({
          subject: broadcast.subject,
          message: broadcast.message,
          target_plan: broadcast.target,
        }),
      });
      setBResult({ ok: true, msg: d.message });
    } catch (e) {
      setBResult({ ok: false, msg: e.message });
    } finally {
      setBLoading(false);
    }
  };

  const emailTypes = [
    { id: 'test',    label: 'Generic Test' },
    { id: 'welcome', label: 'Welcome Email' },
    { id: 'invoice', label: 'Invoice' },
    { id: 'payment', label: 'Payment Confirmed' },
  ];

  const cardStyle = { background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 16, padding: 20 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* SMTP Info */}
      <div style={cardStyle}>
        <SectionHdr title="SMTP Configuration" sub="Brevo SMTP settings" icon={Settings} T={T} />
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
          {[
            ['Server',  'smtp-relay.brevo.com'],
            ['Port',    '587 (TLS)'],
            ['Login',   'a4f504001@smtp-brevo.com'],
            ['From',    'billing@gasstrategyai.xyz'],
            ['Support', 'support@gasstrategyai.xyz'],
            ['Status',  'Configured'],
          ].map(([k, v]) => (
            <div key={k} style={{ background: T.bgPanel, border: `1px solid ${T.border}`, borderRadius: 8, padding: '10px 12px' }}>
              <div style={{ fontSize: 9, color: T.textDim, marginBottom: 4, textTransform: 'uppercase', letterSpacing: '0.06em' }}>{k}</div>
              <div style={{ fontSize: 11, fontFamily: MONO, fontWeight: 700, color: k === 'Status' ? '#34d399' : T.text }}>{v}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Test Email */}
      <div style={cardStyle}>
        <SectionHdr title="Test Send Email" sub="Verify SMTP by sending a test email" icon={Mail} T={T} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <TInput value={toEmail} onChange={setToEmail} placeholder="Destination email address..." T={T} />
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {emailTypes.map(t => (
              <TBtn key={t.id} onClick={() => setEmailType(t.id)} variant={emailType === t.id ? 'yellow' : 'ghost'} size="sm">
                {t.label}
              </TBtn>
            ))}
          </div>
          <TBtn onClick={sendTest} loading={loading} size="sm">
            <Send size={11} />Send Test Email
          </TBtn>
          {result && (
            <div style={{
              padding: '10px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
              background: result.ok ? 'rgba(52,211,153,0.08)' : 'rgba(248,113,113,0.08)',
              border: `1px solid ${result.ok ? 'rgba(52,211,153,0.25)' : 'rgba(248,113,113,0.25)'}`,
              color: result.ok ? '#34d399' : '#f87171',
            }}>
              {result.ok ? '✓' : '✗'} {result.msg}
            </div>
          )}
        </div>
      </div>

      {/* Broadcast */}
      <div style={cardStyle}>
        <SectionHdr title="Broadcast Email" sub="Send announcement to all users" icon={Bell} T={T} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          <TInput value={broadcast.subject} onChange={v => setBroadcast(p => ({ ...p, subject: v }))} placeholder="Announcement subject..." T={T} />
          <textarea
            value={broadcast.message}
            onChange={e => setBroadcast(p => ({ ...p, message: e.target.value }))}
            placeholder="Announcement message..."
            rows={4}
            style={{
              width: '100%', boxSizing: 'border-box',
              background: T.inputBg, border: `1px solid ${T.border}`,
              borderRadius: 8, padding: '8px 12px', fontSize: 12,
              color: T.text, outline: 'none', fontFamily: 'inherit', resize: 'vertical',
            }}
            onFocus={e => e.target.style.borderColor = 'rgba(250,204,21,0.5)'}
            onBlur={e => e.target.style.borderColor = T.border}
          />
          <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: 10, color: T.textDim }}>Target:</span>
            {['all', 'free', 'essential', 'plus', 'premium', 'ultimate'].map(t => (
              <TBtn key={t} onClick={() => setBroadcast(p => ({ ...p, target: t }))} variant={broadcast.target === t ? 'yellow' : 'ghost'} size="sm">
                {t}
              </TBtn>
            ))}
          </div>
          <TBtn onClick={sendBroadcast} loading={bLoading} variant="red" size="sm">
            <Bell size={11} />Send Broadcast
          </TBtn>
          {bResult && (
            <div style={{
              padding: '10px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
              background: bResult.ok ? 'rgba(52,211,153,0.08)' : 'rgba(248,113,113,0.08)',
              border: `1px solid ${bResult.ok ? 'rgba(52,211,153,0.25)' : 'rgba(248,113,113,0.25)'}`,
              color: bResult.ok ? '#34d399' : '#f87171',
            }}>
              {bResult.ok ? '✓' : '✗'} {bResult.msg}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ─── Tab: LOGS ─────────────────────────────────────────────────────────────────
function LogsTab({ T }) {
  const [data, setData]         = useState({ activity_logs: [], total_logs: 0, processed_tx_count: 0 });
  const [loading, setLoading]   = useState(false);
  const [clearing, setClearing] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await apiFetch('/admin/logs?limit=100');
      setData(d);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, []);

  const clearLogs = async () => {
    if (!window.confirm('Delete all activity logs?')) return;
    setClearing(true);
    try {
      await apiFetch('/admin/logs', { method: 'DELETE' });
      load();
    } finally {
      setClearing(false);
    }
  };

  const actionColor = (action = '') => {
    if (action.includes('payment') || action.includes('credit')) return '#34d399';
    if (action.includes('broadcast') || action.includes('email')) return '#60a5fa';
    if (action.includes('admin')) return '#a78bfa';
    return ACCENT;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
        <StatCard icon={Activity}   label="Total Log Entries" value={data.total_logs}          color={ACCENT}    spark={[4,6,5,8,7,9,8]} T={T} />
        <StatCard icon={CreditCard} label="Processed TX"      value={data.processed_tx_count}  color="#10b981"   spark={[2,3,4,5,4,6,5]} sub="ERC20 confirmed" T={T} />
      </div>

      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <span style={{ fontSize: 12, fontWeight: 800, color: T.text }}>Activity Log</span>
        <div style={{ display: 'flex', gap: 6 }}>
          <TBtn onClick={load} loading={loading} variant="ghost" size="sm"><RefreshCw size={11} />Refresh</TBtn>
          <TBtn onClick={clearLogs} loading={clearing} variant="red" size="sm"><Trash2 size={11} />Clear</TBtn>
        </div>
      </div>

      {/* Terminal stream */}
      <div style={{ background: '#050810', border: `1px solid ${T.border}`, borderRadius: 14, overflow: 'hidden' }}>
        {/* Terminal header bar */}
        <div style={{
          padding: '8px 14px', background: 'rgba(255,255,255,0.03)',
          borderBottom: `1px solid ${T.border}`,
          display: 'flex', alignItems: 'center', gap: 8,
        }}>
          <div style={{ display: 'flex', gap: 5 }}>
            {['#f87171', '#fbbf24', '#34d399'].map(c => (
              <div key={c} style={{ width: 8, height: 8, borderRadius: '50%', background: c, opacity: 0.7 }} />
            ))}
          </div>
          <span style={{ fontSize: 10, fontFamily: MONO, color: 'rgba(255,255,255,0.2)', marginLeft: 4 }}>
            gas-admin-activity-stream
          </span>
          <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: 5 }}>
            <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#34d399' }} className="animate-pulse" />
            <span style={{ fontSize: 9, fontFamily: MONO, color: 'rgba(255,255,255,0.2)' }}>LIVE</span>
          </div>
        </div>
        <div style={{ maxHeight: 480, overflowY: 'auto', padding: '10px 4px', display: 'flex', flexDirection: 'column', gap: 1 }}>
          {data.activity_logs.length === 0 && (
            <p style={{ textAlign: 'center', padding: '30px 0', fontFamily: MONO, fontSize: 11, color: 'rgba(255,255,255,0.15)' }}>
              ~ no log entries ~
            </p>
          )}
          {data.activity_logs.map((log, i) => (
            <div key={i}
              style={{ display: 'flex', gap: 10, padding: '4px 14px', borderRadius: 4, transition: 'background 0.1s' }}
              onMouseEnter={e => e.currentTarget.style.background = 'rgba(255,255,255,0.03)'}
              onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
            >
              <span style={{ width: 56, fontSize: 10, fontFamily: MONO, color: 'rgba(255,255,255,0.2)', textAlign: 'right', flexShrink: 0 }}>
                {new Date(log.ts).toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
              </span>
              <span style={{ width: 5, height: 5, borderRadius: '50%', background: actionColor(log.action), alignSelf: 'center', flexShrink: 0, marginTop: 1 }} />
              <span style={{ fontSize: 10, fontFamily: MONO, fontWeight: 700, color: actionColor(log.action), flexShrink: 0, minWidth: 120 }}>
                {log.action}
              </span>
              <span style={{ fontSize: 10, fontFamily: MONO, color: 'rgba(226,232,240,0.55)', flex: 1, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                {log.detail}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Tab: AI CONFIG ────────────────────────────────────────────────────────────
function AIConfigTab({ T }) {
  const cardStyle = { background: T.bgCard, border: `1px solid ${T.border}`, borderRadius: 16, padding: 20 };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      <div style={cardStyle}>
        <SectionHdr title="Kimi AI Moonshot" sub="AI engine for support & analysis" icon={Zap} T={T} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {[
            {
              label: 'Support AI Key',
              desc: 'Used for auto-reply support tickets',
              key: 'sk-oqNr...H10',
              model: 'moonshot-v1-8k',
              status: 'Active',
            },
            {
              label: 'Analysis AI Key',
              desc: 'Used for AI trading analysis features',
              key: 'sk-4wPb...YN',
              model: 'moonshot-v1-8k',
              status: 'Active',
            },
          ].map((item, i) => (
            <div key={i} style={{ background: T.bgPanel, border: `1px solid ${T.border}`, borderRadius: 12, padding: 16 }}>
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 12 }}>
                <div>
                  <div style={{ fontSize: 12, fontWeight: 700, color: T.text, marginBottom: 2 }}>{item.label}</div>
                  <div style={{ fontSize: 10, color: T.textDim }}>{item.desc}</div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                  <div style={{ width: 7, height: 7, borderRadius: '50%', background: '#34d399' }} className="animate-pulse" />
                  <TBadge color="green">{item.status}</TBadge>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                <div style={{ background: T.bg, border: `1px solid ${T.border}`, borderRadius: 8, padding: '8px 10px' }}>
                  <div style={{ fontSize: 9, color: T.textDim, marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.06em' }}>API Key</div>
                  <div style={{ fontSize: 11, fontFamily: MONO, color: ACCENT }}>{item.key}</div>
                </div>
                <div style={{ background: T.bg, border: `1px solid ${T.border}`, borderRadius: 8, padding: '8px 10px' }}>
                  <div style={{ fontSize: 9, color: T.textDim, marginBottom: 3, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Model</div>
                  <div style={{ fontSize: 11, fontFamily: MONO, color: '#60a5fa' }}>{item.model}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div style={cardStyle}>
        <SectionHdr title="ERC20 Payment Config" sub="USDT payment wallet configuration" icon={CreditCard} T={T} />
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
          {[
            { label: 'Wallet Address', value: '0xf8ef68F41B609B06210ebe7d045FA111F2034518', color: ACCENT },
            { label: 'USDT Contract',  value: '0xdAC17F958D2ee523a2206206994597C13D831ec7', color: '#60a5fa' },
            { label: 'Network',        value: 'Ethereum (ERC-20)',                          color: '#34d399' },
            { label: 'Etherscan Key',  value: 'QQX...2IKE (configured)',                    color: '#a78bfa' },
            { label: 'Poll Interval',  value: 'Every 60 seconds',                           color: T.textMid },
          ].map(({ label, value, color }) => (
            <div key={label} style={{
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
              padding: '10px 14px', background: T.bgPanel, border: `1px solid ${T.border}`, borderRadius: 8,
            }}>
              <span style={{ fontSize: 11, color: T.textDim }}>{label}</span>
              <span style={{ fontSize: 10, fontFamily: MONO, fontWeight: 700, color }}>{value}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── TABS CONFIG ───────────────────────────────────────────────────────────────
const TABS = [
  { id: 'dashboard', label: 'Dashboard', icon: BarChart2 },
  { id: 'users',     label: 'Users',     icon: Users },
  { id: 'payments',  label: 'Payments',  icon: CreditCard },
  { id: 'support',   label: 'Support',   icon: MessageSquare },
  { id: 'email',     label: 'Email',     icon: Mail },
  { id: 'logs',      label: 'Logs',      icon: Activity },
  { id: 'ai',        label: 'AI Config', icon: Zap },
];

// ─── Main AdminPanelView ───────────────────────────────────────────────────────
export default function AdminPanelView() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [theme, setTheme]         = useState('dark');

  useEffect(() => {
    const saved = localStorage.getItem('gas-theme') || 'dark';
    setTheme(saved);
    document.documentElement.setAttribute('data-theme', saved);
  }, []);

  const T = buildTokens(theme);

  // Responsive: detect mobile
  const [isMobile, setIsMobile] = useState(window.innerWidth < 768);
  useEffect(() => {
    const fn = () => setIsMobile(window.innerWidth < 768);
    window.addEventListener('resize', fn);
    return () => window.removeEventListener('resize', fn);
  }, []);

  const renderTab = () => {
    switch (activeTab) {
      case 'dashboard': return <DashboardTab T={T} />;
      case 'users':     return <UsersTab T={T} />;
      case 'payments':  return <PaymentsTab T={T} />;
      case 'support':   return <SupportTab T={T} />;
      case 'email':     return <EmailTab T={T} />;
      case 'logs':      return <LogsTab T={T} />;
      case 'ai':        return <AIConfigTab T={T} />;
      default:          return null;
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%', background: T.bg, color: T.text, position: 'relative' }}>
      {/* Gold top accent line */}
      <div style={{ height: 3, background: 'linear-gradient(90deg, #facc15, #f59e0b, #facc15)', flexShrink: 0 }} />

      {/* Header */}
      <div style={{
        padding: '14px 20px', borderBottom: `1px solid ${T.border}`,
        display: 'flex', alignItems: 'center', gap: 12, flexShrink: 0,
        background: T.bgCard,
      }}>
        <div style={{
          width: 38, height: 38, background: 'linear-gradient(135deg,#facc15,#f59e0b)',
          borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center',
          boxShadow: '0 4px 14px rgba(250,204,21,0.25)', flexShrink: 0,
        }}>
          <Shield size={17} style={{ color: '#000' }} />
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 900, color: T.text, letterSpacing: '-0.02em' }}>Admin Panel</div>
          <div style={{ fontSize: 10, color: T.textDim }}>Golden AI Strategy · Management Console</div>
        </div>
        <div style={{ marginLeft: 'auto' }}>
          <TBadge color="red">ADMIN ACCESS</TBadge>
        </div>
      </div>

      {/* Body: sidebar + content */}
      <div style={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* LEFT SIDEBAR (desktop) */}
        {!isMobile && (
          <div style={{
            width: 200, flexShrink: 0, background: T.bgCard,
            borderRight: `1px solid ${T.border}`,
            padding: '12px 8px', display: 'flex', flexDirection: 'column', gap: 2,
            overflowY: 'auto',
          }}>
            <div style={{ fontSize: 9, fontWeight: 700, color: T.textDim, textTransform: 'uppercase', letterSpacing: '0.1em', padding: '4px 10px 8px' }}>
              Navigation
            </div>
            {TABS.map(t => {
              const Icon = t.icon;
              const active = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '9px 12px', borderRadius: 10, cursor: 'pointer',
                    background: active ? ACCENT : 'transparent',
                    color: active ? '#000' : T.textMid,
                    border: 'none', textAlign: 'left', fontSize: 12, fontWeight: active ? 700 : 500,
                    transition: 'all 0.15s', fontFamily: 'inherit',
                  }}
                  onMouseEnter={e => { if (!active) e.currentTarget.style.background = T.bgHover; }}
                  onMouseLeave={e => { if (!active) e.currentTarget.style.background = 'transparent'; }}
                >
                  <Icon size={14} style={{ flexShrink: 0 }} />
                  {t.label}
                </button>
              );
            })}
          </div>
        )}

        {/* MOBILE TOP TAB ROW */}
        {isMobile && (
          <div style={{
            position: 'absolute', top: 3 + 55, left: 0, right: 0,
            display: 'flex', gap: 4, overflowX: 'auto', padding: '8px 12px',
            background: T.bgCard, borderBottom: `1px solid ${T.border}`, zIndex: 10,
            flexShrink: 0,
          }}>
            {TABS.map(t => {
              const Icon = t.icon;
              const active = activeTab === t.id;
              return (
                <button
                  key={t.id}
                  onClick={() => setActiveTab(t.id)}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 5, whiteSpace: 'nowrap',
                    padding: '6px 12px', borderRadius: 20, cursor: 'pointer',
                    background: active ? ACCENT : T.inputBg,
                    color: active ? '#000' : T.textMid,
                    border: `1px solid ${active ? ACCENT : T.border}`,
                    fontSize: 11, fontWeight: active ? 700 : 500, fontFamily: 'inherit',
                    transition: 'all 0.15s',
                  }}
                >
                  <Icon size={11} />
                  {t.label}
                </button>
              );
            })}
          </div>
        )}

        {/* CONTENT */}
        <div style={{
          flex: 1, overflowY: 'auto', padding: 20,
          marginTop: isMobile ? 50 : 0,
        }}>
          {renderTab()}
        </div>
      </div>
    </div>
  );
}
