import React, { useState } from 'react';
import {
  Zap, BrainCircuit, Activity, ShieldCheck, Filter, Calendar, BarChart2, Droplet,
  Bell, Bot, Webhook, BookOpen, Users, Trophy, CreditCard, Layers, Brain,
  Newspaper, TrendingDown, ScanLine, GraduationCap, Building2, Link,
  Sparkles, ArrowRight, Lock, Star, TrendingUp, Cpu, Globe, Shield,
  ChevronRight, Flame, Crown, Gem, Rocket, Zap as Lightning
} from 'lucide-react';

/* ─── Feature metadata ────────────────────────────────────────────────────── */
const FEATURES = {
  signal:      { emoji: '⚡', desc: 'AI signal generator real-time dari data MT5 + SMC analysis',  color: '#3b82f6', gradient: 'from-blue-600 to-blue-400',    bg: 'rgba(59,130,246,0.12)' },
  technical:   { emoji: '📊', desc: 'Analisa RSI, MACD, ADX, BB, EMA otomatis multi-indikator',    color: '#6366f1', gradient: 'from-indigo-600 to-blue-500',   bg: 'rgba(99,102,241,0.12)' },
  alerts:      { emoji: '🔔', desc: 'Smart alert harga & level kritis, push notifikasi instan',     color: '#f59e0b', gradient: 'from-amber-500 to-yellow-400',  bg: 'rgba(245,158,11,0.12)' },
  session:     { emoji: '🕐', desc: 'Optimizer sesi London, NY, Tokyo — kapan waktu entry terbaik', color: '#14b8a6', gradient: 'from-teal-500 to-cyan-400',    bg: 'rgba(20,184,166,0.12)' },
  correlation: { emoji: '🔗', desc: 'Track korelasi antar pair — hindari over-exposure portfolio',  color: '#8b5cf6', gradient: 'from-violet-600 to-purple-400', bg: 'rgba(139,92,246,0.12)' },
  screener:    { emoji: '🔭', desc: 'Scan 100+ simbol sekaligus, temukan setup terbaik serentak',   color: '#fac815', gradient: 'from-yellow-500 to-amber-400',  bg: 'rgba(250,200,21,0.12)' },
  fundamental: { emoji: '🌍', desc: 'GDP, CPI, Fed Rate, NFP — macro AI analysis 24 indikator',    color: '#10b981', gradient: 'from-emerald-600 to-teal-400',  bg: 'rgba(16,185,129,0.12)' },
  calendars:   { emoji: '📅', desc: 'Kalender ekonomi FXStreet + AI analysis dampak pasar harian',  color: '#06b6d4', gradient: 'from-cyan-600 to-blue-400',     bg: 'rgba(6,182,212,0.12)' },
  sentiment:   { emoji: '🧠', desc: 'Sentiment pasar dari news, COT data, fear & greed index',      color: '#a855f7', gradient: 'from-purple-600 to-violet-400', bg: 'rgba(168,85,247,0.12)' },
  briefing:    { emoji: '📰', desc: 'Daily AI market briefing — ringkasan macro + outlook intraday', color: '#f97316', gradient: 'from-orange-600 to-amber-400',  bg: 'rgba(249,115,22,0.12)' },
  hybrid:      { emoji: '⚡', desc: 'Konfluensi TA + FA + Sentiment — 3-layer signal power',         color: '#ec4899', gradient: 'from-pink-600 to-rose-400',    bg: 'rgba(236,72,153,0.12)' },
  risk_manager:{ emoji: '🛡️', desc: 'Hitung lot size, R:R, max drawdown, position sizing otomatis', color: '#22c55e', gradient: 'from-green-600 to-emerald-400', bg: 'rgba(34,197,94,0.12)' },
  drawdown:    { emoji: '📉', desc: 'Strategi recovery drawdown — martingale vs averaging AI',       color: '#ef4444', gradient: 'from-red-600 to-rose-400',     bg: 'rgba(239,68,68,0.12)' },
  ai_backtest: { emoji: '🔬', desc: 'Backtest strategi custom dengan AI analysis 1-5 tahun data',   color: '#fac815', gradient: 'from-yellow-500 to-orange-400', bg: 'rgba(250,200,21,0.12)' },
  psychology:  { emoji: '🧘', desc: 'Deteksi emosi trading, fear/greed scoring, mental coaching',    color: '#8b5cf6', gradient: 'from-violet-600 to-purple-400', bg: 'rgba(139,92,246,0.12)' },
  journal:     { emoji: '📓', desc: 'AI trade journal — catat, analisa, pelajari pola trading-mu',   color: '#06b6d4', gradient: 'from-cyan-500 to-blue-400',    bg: 'rgba(6,182,212,0.12)' },
  mentor:      { emoji: '👨‍🏫', desc: 'AI mentor personal — jawab setiap pertanyaan trading 24/7',    color: '#fac815', gradient: 'from-yellow-500 to-amber-400',  bg: 'rgba(250,200,21,0.15)' },
  propfirm:    { emoji: '🏢', desc: 'Strategi pass prop firm challenge FTMO, MyForexFunds, dll',     color: '#f97316', gradient: 'from-orange-500 to-red-400',    bg: 'rgba(249,115,22,0.12)' },
};

const PLAN_STYLE = {
  'Essential+': { label: 'Essential', color: '#60a5fa', bg: 'rgba(59,130,246,0.12)', border: 'rgba(59,130,246,0.3)',  dot: '#3b82f6' },
  'Plus+':      { label: 'Plus',      color: '#a78bfa', bg: 'rgba(139,92,246,0.12)', border: 'rgba(139,92,246,0.3)', dot: '#8b5cf6' },
  'Premium+':   { label: 'Premium',   color: '#fb923c', bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.3)', dot: '#f97316' },
  'Ultimate':   { label: 'Ultimate',  color: '#fac815', bg: 'rgba(250,200,21,0.12)', border: 'rgba(250,200,21,0.35)', dot: '#fac815' },
};

const CATEGORIES = [
  {
    id: 'technical',
    icon: BarChart2,
    emoji: '📊',
    title: 'Technical Analysis',
    subtitle: 'Real-time market structure detection',
    gradient: 'from-blue-600/20 to-indigo-600/10',
    accent: '#3b82f6',
    items: [
      { id: 'signal',    label: 'Signal AI',         credit: 3,  plan: 'Essential+' },
      { id: 'technical', label: 'Technical Analysis', credit: 3,  plan: 'Essential+' },
      { id: 'alerts',    label: 'Smart Alert',        credit: 1,  plan: 'Essential+' },
      { id: 'session',   label: 'Session Optimizer',  credit: 1,  plan: 'Essential+' },
    ]
  },
  {
    id: 'advanced',
    icon: ScanLine,
    emoji: '🔭',
    title: 'Advanced Scanner',
    subtitle: 'Multi-symbol intelligence engine',
    gradient: 'from-violet-600/20 to-purple-600/10',
    accent: '#8b5cf6',
    items: [
      { id: 'correlation', label: 'Correlation Tracker',  credit: 3,  plan: 'Plus+' },
      { id: 'screener',    label: 'Multi-Symbol Scanner', credit: 15, plan: 'Ultimate' },
    ]
  },
  {
    id: 'fundamental',
    icon: Globe,
    emoji: '🌍',
    title: 'Fundamental Analysis',
    subtitle: 'Macro economy · Global data intelligence',
    gradient: 'from-emerald-600/20 to-teal-600/10',
    accent: '#10b981',
    items: [
      { id: 'fundamental', label: 'Fundamental AI',       credit: 5,  plan: 'Plus+' },
      { id: 'calendars',   label: 'Economic Calendar AI', credit: 4,  plan: 'Plus+' },
      { id: 'sentiment',   label: 'Sentiment Market AI',  credit: 5,  plan: 'Plus+' },
      { id: 'briefing',    label: 'AI Market Briefing',   credit: 10, plan: 'Premium+' },
    ]
  },
  {
    id: 'hybrid',
    icon: Layers,
    emoji: '⚡',
    title: 'Hybrid & Risk System',
    subtitle: 'AI confluence · Risk automation engine',
    gradient: 'from-pink-600/20 to-rose-600/10',
    accent: '#ec4899',
    items: [
      { id: 'hybrid',       label: 'Hybrid System AI',  credit: 8,  plan: 'Premium+' },
      { id: 'risk_manager', label: 'Risk Manager AI',   credit: 3,  plan: 'Plus+' },
      { id: 'drawdown',     label: 'Drawdown Recovery', credit: 5,  plan: 'Premium+' },
      { id: 'ai_backtest',  label: 'AI Backtesting',    credit: 20, plan: 'Ultimate' },
    ]
  },
  {
    id: 'psychology',
    icon: Brain,
    emoji: '🧠',
    title: 'Psychology & Growth',
    subtitle: 'Mental edge · AI coaching · Mastery path',
    gradient: 'from-violet-600/20 to-fuchsia-600/10',
    accent: '#a855f7',
    items: [
      { id: 'psychology', label: 'Psychology Coach AI',  credit: 5,  plan: 'Premium+' },
      { id: 'journal',    label: 'AI Trade Journal',     credit: 8,  plan: 'Premium+' },
      { id: 'mentor',     label: 'AI Mentor Mode',       credit: 10, plan: 'Ultimate' },
      { id: 'propfirm',   label: 'Prop Firm Assistant',  credit: 8,  plan: 'Premium+' },
    ]
  },
  {
    id: 'platform',
    icon: Cpu,
    emoji: '🛠️',
    title: 'Platform & Community',
    subtitle: 'Tools · Automation · VIP network',
    gradient: 'from-gray-600/20 to-slate-600/10',
    accent: '#6b7280',
    items: [
      { id: 'telegram',    label: 'Bot Telegram',    credit: null, plan: null },
      { id: 'webhook',     label: 'API / Webhook',   credit: null, plan: null },
      { id: 'forum',       label: 'Forum VIP',       credit: null, plan: null },
      { id: 'leaderboard', label: 'Leaderboard',     credit: null, plan: null },
      { id: 'pricing',     label: 'Upgrade Plan',    credit: null, plan: null },
    ]
  },
];

/* ─── Stat Pill ──────────────────────────────────────────────────────────── */
function StatPill({ emoji, value, label, color }) {
  return (
    <div className="flex flex-col items-center gap-1 px-5 py-3 rounded-2xl border"
      style={{ background: `${color}0d`, borderColor: `${color}25` }}>
      <span className="text-xl leading-none">{emoji}</span>
      <span className="text-lg font-bold font-mono leading-none" style={{ color }}>{value}</span>
      <span className="text-[9px] font-bold uppercase tracking-widest text-[var(--text-dim)]">{label}</span>
    </div>
  );
}

/* ─── Feature Card ───────────────────────────────────────────────────────── */
function FeatureCard({ item, catAccent, onSelect, idx }) {
  const meta = FEATURES[item.id] || {};
  const plan = PLAN_STYLE[item.plan] || {};
  const isLocked = !!item.plan && item.plan !== 'Essential+';

  return (
    <button
      onClick={() => onSelect(item.id)}
      className="card-shine group relative w-full text-left rounded-2xl border transition-all duration-300 hover:-translate-y-1.5 focus:outline-none overflow-hidden"
      style={{
        background: 'var(--bg-card)',
        borderColor: 'var(--border-color)',
        animationDelay: `${idx * 0.04}s`,
      }}
      onMouseEnter={e => {
        e.currentTarget.style.borderColor = `${meta.color || catAccent}50`;
        e.currentTarget.style.boxShadow = `0 12px 40px rgba(0,0,0,0.5), 0 0 0 1px ${meta.color || catAccent}30`;
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'var(--border-color)';
        e.currentTarget.style.boxShadow = 'none';
      }}
    >
      {/* Top gradient line */}
      <div className="absolute top-0 left-0 right-0 h-[2px] opacity-0 group-hover:opacity-100 transition-opacity duration-300"
        style={{ background: `linear-gradient(90deg, transparent, ${meta.color || catAccent}, transparent)` }} />

      <div className="p-4 flex flex-col gap-3">
        {/* Header row */}
        <div className="flex items-start justify-between gap-2">
          {/* Icon */}
          <div className="relative shrink-0">
            <div className="w-11 h-11 rounded-xl flex items-center justify-center text-xl transition-transform duration-300 group-hover:scale-110"
              style={{ background: meta.bg || 'var(--bg-hover)' }}>
              {meta.emoji || '✨'}
            </div>
          </div>

          {/* Plan badge + credit */}
          <div className="flex flex-col items-end gap-1.5">
            {item.plan && (
              <span className="text-[8px] font-black uppercase tracking-wider px-2 py-0.5 rounded-full"
                style={{ background: plan.bg, color: plan.color, border: `1px solid ${plan.border}` }}>
                {plan.label}
              </span>
            )}
            {item.credit && (
              <span className="text-[9px] font-bold text-[var(--text-dim)] flex items-center gap-0.5">
                🪙 <span className="font-mono">{item.credit}</span>
              </span>
            )}
          </div>
        </div>

        {/* Feature name */}
        <div>
          <h3 className="text-[13px] font-bold text-[var(--text-primary)] leading-tight mb-1 group-hover:text-white transition-colors">
            {item.label}
          </h3>
          <p className="text-[10px] text-[var(--text-dim)] leading-relaxed line-clamp-2">
            {meta.desc || 'Fitur AI trading canggih'}
          </p>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between pt-1 border-t" style={{ borderColor: 'var(--border-subtle)' }}>
          <div className="flex items-center gap-1">
            <div className="w-1.5 h-1.5 rounded-full animate-pulse"
              style={{ background: meta.color || '#10b981' }} />
            <span className="text-[8px] font-bold text-[var(--text-dim)] uppercase tracking-wider">
              {item.credit ? 'AI Powered' : 'Free Access'}
            </span>
          </div>
          <div className="flex items-center gap-1 text-[var(--text-dim)] group-hover:text-[var(--accent)] transition-colors">
            <span className="text-[9px] font-bold">Buka</span>
            <ChevronRight size={11} />
          </div>
        </div>
      </div>
    </button>
  );
}

/* ─── Category Section ───────────────────────────────────────────────────── */
function CategorySection({ cat, onSelect, delay = 0 }) {
  const CatIcon = cat.icon;
  return (
    <div className="space-y-4 animate-fade-up" style={{ animationDelay: `${delay}s` }}>
      {/* Category Header */}
      <div className="flex items-center gap-3">
        <div className="relative flex items-center gap-3 flex-1">
          {/* Icon */}
          <div className="w-9 h-9 rounded-xl flex items-center justify-center shrink-0"
            style={{ background: `${cat.accent}18`, border: `1px solid ${cat.accent}30` }}>
            <CatIcon size={16} style={{ color: cat.accent }} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-[11px] font-black uppercase tracking-widest text-[var(--text-primary)]">
                {cat.emoji} {cat.title}
              </span>
              <span className="text-[8px] font-bold px-1.5 py-0.5 rounded-full"
                style={{ background: `${cat.accent}15`, color: cat.accent, border: `1px solid ${cat.accent}25` }}>
                {cat.items.length} fitur
              </span>
            </div>
            <p className="text-[9px] text-[var(--text-dim)] mt-0.5 font-medium">{cat.subtitle}</p>
          </div>
        </div>
        {/* Divider line */}
        <div className="hidden sm:block flex-1 h-px" style={{ background: `linear-gradient(90deg, ${cat.accent}30, transparent)` }} />
      </div>

      {/* Cards grid */}
      <div className={`grid gap-3 ${cat.items.length === 2 ? 'grid-cols-1 sm:grid-cols-2' : 'grid-cols-1 sm:grid-cols-2 lg:grid-cols-4'}`}>
        {cat.items.map((item, i) => (
          <FeatureCard key={item.id} item={item} catAccent={cat.accent} onSelect={onSelect} idx={i} />
        ))}
      </div>
    </div>
  );
}

/* ─── Main Component ─────────────────────────────────────────────────────── */
export default function AICommandCenter({ onSelect }) {
  const [search, setSearch] = useState('');

  const filteredCategories = search.trim()
    ? CATEGORIES.map(cat => ({
        ...cat,
        items: cat.items.filter(item =>
          item.label.toLowerCase().includes(search.toLowerCase()) ||
          (FEATURES[item.id]?.desc || '').toLowerCase().includes(search.toLowerCase())
        )
      })).filter(cat => cat.items.length > 0)
    : CATEGORIES;

  const totalItems = CATEGORIES.reduce((a, c) => a + c.items.length, 0);

  return (
    <div className="min-h-full pb-20 md:pb-6">

      {/* ── Hero Header ─────────────────────────────────────────────────── */}
      <div className="relative overflow-hidden px-4 md:px-8 pt-8 pb-6">
        {/* Background glow */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[600px] h-[200px] opacity-10 pointer-events-none"
          style={{ background: 'radial-gradient(ellipse, #fac815 0%, transparent 70%)' }} />

        <div className="relative z-10 max-w-7xl mx-auto">
          {/* Title row */}
          <div className="flex items-start justify-between flex-wrap gap-4 mb-6">
            <div>
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center animate-glow"
                  style={{ background: 'rgba(250,200,21,0.12)', border: '1px solid rgba(250,200,21,0.3)' }}>
                  <Sparkles size={16} style={{ color: '#fac815' }} />
                </div>
                <span className="text-[9px] font-black uppercase tracking-[0.25em] text-[var(--text-dim)]">
                  Golden AI Strategy · AI Command Center
                </span>
              </div>
              <h1 className="font-display text-3xl md:text-4xl font-black text-[var(--text-primary)] leading-none">
                Pusat Komando{' '}
                <span className="text-gradient-gold">AI</span>
              </h1>
              <p className="text-sm text-[var(--text-dim)] mt-2 font-medium">
                {totalItems} fitur AI kelas institutional · 4 tier plan · Powered by DeepSeek + Claude
              </p>
            </div>

            {/* Search box */}
            <div className="flex items-center gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-3 py-2 w-full sm:w-56 focus-within:border-[var(--accent)]/50 transition-colors">
              <span className="text-[var(--text-dim)]">🔍</span>
              <input
                type="text"
                value={search}
                onChange={e => setSearch(e.target.value)}
                placeholder="Cari fitur AI..."
                className="bg-transparent text-xs text-[var(--text-primary)] outline-none w-full placeholder:text-[var(--text-dim)]"
              />
              {search && (
                <button onClick={() => setSearch('')} className="text-[var(--text-dim)] hover:text-[var(--text-primary)] text-xs">✕</button>
              )}
            </div>
          </div>

          {/* Stats pills */}
          <div className="flex flex-wrap gap-3">
            <StatPill emoji="⚡" value="18"   label="Fitur AI"    color="#fac815" />
            <StatPill emoji="🎯" value="4"    label="Tier Plan"   color="#8b5cf6" />
            <StatPill emoji="🤖" value="24/7" label="AI Active"   color="#10b981" />
            <StatPill emoji="🔒" value="SSL"  label="Secured"     color="#3b82f6" />
            <StatPill emoji="🏆" value="Pro"  label="Grade Tools" color="#f97316" />
          </div>

          {/* Gold divider */}
          <div className="divider-gold mt-6" />
        </div>
      </div>

      {/* ── Plan Legend ─────────────────────────────────────────────────── */}
      <div className="px-4 md:px-8 mb-6">
        <div className="max-w-7xl mx-auto flex flex-wrap items-center gap-2">
          <span className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mr-1">Plan Tier:</span>
          {Object.entries(PLAN_STYLE).map(([key, s]) => (
            <span key={key} className="flex items-center gap-1.5 text-[9px] font-bold px-2.5 py-1 rounded-full"
              style={{ background: s.bg, color: s.color, border: `1px solid ${s.border}` }}>
              <span className="w-1.5 h-1.5 rounded-full" style={{ background: s.dot }} />
              {s.label}
            </span>
          ))}
          <span className="text-[9px] text-[var(--text-dim)] ml-auto hidden sm:block">
            🪙 = Kredit per eksekusi
          </span>
        </div>
      </div>

      {/* ── Feature Categories ───────────────────────────────────────────── */}
      <div className="px-4 md:px-8 space-y-8 max-w-7xl mx-auto">
        {filteredCategories.length === 0 ? (
          <div className="py-20 flex flex-col items-center gap-3 text-center">
            <span className="text-5xl">🔍</span>
            <p className="text-lg font-bold text-[var(--text-secondary)]">Fitur tidak ditemukan</p>
            <p className="text-xs text-[var(--text-dim)]">Coba kata kunci lain</p>
          </div>
        ) : (
          filteredCategories.map((cat, i) => (
            <CategorySection
              key={cat.id}
              cat={cat}
              onSelect={id => onSelect(id === 'ai_signal' ? 'signal' : id)}
              delay={i * 0.06}
            />
          ))
        )}
      </div>

      {/* ── Bottom CTA ──────────────────────────────────────────────────── */}
      <div className="px-4 md:px-8 mt-12 mb-6 max-w-7xl mx-auto">
        <div className="relative overflow-hidden rounded-2xl p-6 text-center"
          style={{ background: 'linear-gradient(135deg, rgba(250,200,21,0.08) 0%, rgba(139,92,246,0.05) 100%)', border: '1px solid rgba(250,200,21,0.15)' }}>
          <div className="absolute inset-0 opacity-5"
            style={{ background: 'radial-gradient(circle at 50% 0%, #fac815 0%, transparent 60%)' }} />
          <div className="relative z-10">
            <Crown size={24} className="mx-auto mb-3 text-[var(--accent)]" />
            <p className="text-base font-black text-[var(--text-primary)] mb-1">Unlock Ultimate Plan</p>
            <p className="text-[11px] text-[var(--text-dim)] mb-4">Akses semua 18 fitur AI + unlimited kredit + priority AI models</p>
            <button onClick={() => onSelect('pricing')}
              className="inline-flex items-center gap-2 px-6 py-2.5 rounded-xl text-xs font-black text-black transition-all hover:scale-105 hover:shadow-[var(--accent-glow)]"
              style={{ background: 'var(--grad-gold)' }}>
              <Crown size={13} />
              Lihat Semua Plan
              <ArrowRight size={13} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
