/**
 * LeftFeaturePanel — left panel in the main dashboard
 * Shows: Admin badge, 18 feature shortcuts (top, scrollable), AI Mentor Chat (bottom, collapsible)
 */
import React, { useState } from 'react';
import {
    Zap, BarChart2, Brain, Layers, Newspaper, Shield, Activity,
    BookOpen, ScanLine, GraduationCap, Building2, Link, Calendar,
    Droplet, TrendingDown, ShieldCheck, Crown, Lock, ChevronDown, ChevronUp,
    MessageSquare, Globe, TrendingUp
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import AIBloombergTerminal from './AIBloombergTerminal';

// All 18 features — icon + label + plan gate
const QUICK_FEATURES = [
    // Tier 1 — Essential (always visible)
    { id: 'signal',      icon: Zap,          label: 'Signal AI',        plan: 'essential', color: 'text-yellow-400',  bg: 'bg-yellow-400/10' },
    { id: 'technical',   icon: BarChart2,     label: 'Technical AI',     plan: 'essential', color: 'text-blue-400',    bg: 'bg-blue-400/10' },
    { id: 'alerts',      icon: Zap,          label: 'Smart Alert',       plan: 'essential', color: 'text-orange-400',  bg: 'bg-orange-400/10' },
    { id: 'session',     icon: Calendar,      label: 'Session',          plan: 'essential', color: 'text-cyan-400',    bg: 'bg-cyan-400/10' },
    // Tier 2 — Plus
    { id: 'fundamental', icon: Activity,      label: 'Fundamental',      plan: 'plus',     color: 'text-purple-400',  bg: 'bg-purple-400/10' },
    { id: 'sentiment',   icon: Droplet,       label: 'Sentiment',        plan: 'plus',     color: 'text-pink-400',    bg: 'bg-pink-400/10' },
    { id: 'calendars',   icon: Calendar,      label: 'Calendar AI',      plan: 'plus',     color: 'text-green-400',   bg: 'bg-green-400/10' },
    { id: 'correlation', icon: Link,          label: 'Correlation',      plan: 'plus',     color: 'text-indigo-400',  bg: 'bg-indigo-400/10' },
    { id: 'risk_manager',icon: ShieldCheck,   label: 'Risk Manager',     plan: 'plus',     color: 'text-red-400',     bg: 'bg-red-400/10' },
    // Tier 3 — Premium
    { id: 'hybrid',      icon: Layers,        label: 'Hybrid System',    plan: 'premium',  color: 'text-yellow-300',  bg: 'bg-yellow-300/10' },
    { id: 'briefing',    icon: Newspaper,     label: 'Briefing',         plan: 'premium',  color: 'text-blue-300',    bg: 'bg-blue-300/10' },
    { id: 'psychology',  icon: Brain,         label: 'Psychology',       plan: 'premium',  color: 'text-violet-400',  bg: 'bg-violet-400/10' },
    { id: 'journal',     icon: BookOpen,      label: 'Trade Journal',    plan: 'premium',  color: 'text-teal-400',    bg: 'bg-teal-400/10' },
    { id: 'drawdown',    icon: TrendingDown,  label: 'DD Recovery',      plan: 'premium',  color: 'text-red-300',     bg: 'bg-red-300/10' },
    { id: 'propfirm',    icon: Building2,     label: 'Prop Firm',        plan: 'premium',  color: 'text-amber-400',   bg: 'bg-amber-400/10' },
    // Tier 4 — Ultimate
    { id: 'screener',    icon: ScanLine,      label: 'Scanner',          plan: 'ultimate', color: 'text-lime-400',    bg: 'bg-lime-400/10' },
    { id: 'ai_backtest', icon: Activity,      label: 'Backtesting',      plan: 'ultimate', color: 'text-emerald-400', bg: 'bg-emerald-400/10' },
    { id: 'mentor',      icon: GraduationCap, label: 'Mentor Mode',      plan: 'ultimate', color: 'text-sky-400',     bg: 'bg-sky-400/10' },
];

const PLAN_ORDER = ['essential', 'plus', 'premium', 'ultimate'];
const planLevel = (p) => PLAN_ORDER.indexOf(p);

const PLAN_BADGE = {
    essential: { label: 'Essential', color: 'text-gray-400',   bg: 'bg-gray-400/10' },
    plus:      { label: 'Plus+',     color: 'text-blue-400',   bg: 'bg-blue-400/10' },
    premium:   { label: 'Premium+',  color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
    ultimate:  { label: 'Ultimate',  color: 'text-purple-400', bg: 'bg-purple-400/10' },
};

function FeatureShortcut({ feature, accessible, onClick }) {
    const Icon = feature.icon;
    return (
        <button
            onClick={() => accessible && onClick(feature.id)}
            title={accessible ? feature.label : `Butuh plan ${feature.plan}`}
            className={`relative flex flex-col items-center gap-1 p-2 rounded-xl border transition-all group
                ${accessible
                    ? `border-[var(--border-color)] hover:border-[var(--accent)]/40 hover:bg-[var(--bg-hover)] cursor-pointer`
                    : 'border-[var(--border-color)]/30 opacity-40 cursor-not-allowed'
                }`}
        >
            <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${accessible ? feature.bg : 'bg-[var(--bg-panel)]'}`}>
                {accessible
                    ? <Icon size={13} className={feature.color} />
                    : <Lock size={10} className="text-[var(--text-dim)]" />
                }
            </div>
            <span className="text-[8px] font-bold text-[var(--text-dim)] leading-tight text-center">{feature.label}</span>
        </button>
    );
}

export default function LeftFeaturePanel({ onNavigate }) {
    const { user, isAdmin, userPlan, canAccess } = useAuth();
    const [showAll, setShowAll] = useState(false);

    const planBadge = PLAN_BADGE[isAdmin ? 'ultimate' : userPlan] || PLAN_BADGE.essential;
    const visibleFeatures = showAll ? QUICK_FEATURES : QUICK_FEATURES.slice(0, 9);

    return (
        <div className="flex flex-col h-full bg-[var(--bg-card)] overflow-hidden">

            {/* ── User / Plan strip ─────────────────────────────────────────── */}
            <div className="shrink-0 px-3 py-2 border-b border-[var(--border-color)] bg-[var(--bg-panel)] flex items-center justify-between gap-2">
                <div className="flex items-center gap-2 min-w-0">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 flex items-center justify-center text-[9px] font-black text-black shrink-0">
                        {user?.full_name?.[0] || user?.username?.[0]?.toUpperCase() || 'G'}
                    </div>
                    <div className="min-w-0">
                        <p className="text-[10px] font-black text-[var(--text-primary)] truncate">
                            {user?.full_name || user?.username || 'Trader'}
                            {isAdmin && <span className="ml-1 text-[8px] bg-red-500 text-white px-1 py-0.5 rounded font-black">ADMIN</span>}
                        </p>
                        <p className="text-[8px] text-[var(--text-dim)] truncate">{user?.email || ''}</p>
                    </div>
                </div>
                <div className={`shrink-0 px-2 py-1 rounded text-[8px] font-black border ${planBadge.bg} ${planBadge.color} border-current/20`}>
                    {isAdmin ? '👑 ADMIN' : planBadge.label}
                </div>
            </div>

            {/* ── Feature shortcuts grid ────────────────────────────────────── */}
            <div className="shrink-0 border-b border-[var(--border-color)] px-2 pt-2 pb-2">
                <div className="flex items-center justify-between mb-2 px-1">
                    <span className="text-[8px] font-black text-[var(--text-dim)] uppercase tracking-widest">18 Fitur AI</span>
                    <button
                        onClick={() => setShowAll(v => !v)}
                        className="text-[8px] font-bold text-[var(--accent)] hover:underline"
                    >
                        {showAll ? 'Sembunyikan' : 'Lihat semua'}
                    </button>
                </div>
                <div className="grid grid-cols-3 gap-1.5">
                    {visibleFeatures.map(f => (
                        <FeatureShortcut
                            key={f.id}
                            feature={f}
                            accessible={canAccess ? canAccess(f.id) : planLevel(userPlan) >= planLevel(f.plan)}
                            onClick={onNavigate}
                        />
                    ))}
                </div>
                {!showAll && !isAdmin && userPlan !== 'ultimate' && (
                    <button
                        onClick={() => onNavigate('pricing')}
                        className="mt-2 w-full text-center text-[8px] font-black text-[var(--accent)] bg-[var(--accent)]/5 border border-[var(--accent)]/20 rounded-lg py-1.5 hover:bg-[var(--accent)]/10 transition-colors flex items-center justify-center gap-1"
                    >
                        <Crown size={9} /> Upgrade Plan — Unlock semua 18 fitur
                    </button>
                )}
            </div>

            {/* ── AI Mentor Chat (fills remaining space) ────────────────────── */}
            <div className="flex-1 min-h-0">
                <AIBloombergTerminal isFullHeight={true} />
            </div>
        </div>
    );
}
