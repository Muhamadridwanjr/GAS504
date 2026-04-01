import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
    RefreshCw, TrendingUp, TrendingDown, Minus,
    Globe, Clock, AlertTriangle, Activity,
    Zap, ChevronDown, ChevronRight, BarChart2
} from 'lucide-react';
import { fetchMacro } from '../services/api';

// ─── CONSTANTS ───────────────────────────────────────────────────────────────

const REGION_FLAGS = {
    USA: '🇺🇸', EU: '🇪🇺', UK: '🇬🇧', EUR: '🇪🇺',
    JPN: '🇯🇵', CHN: '🇨🇳', AUS: '🇦🇺', CAN: '🇨🇦',
    CHF: '🇨🇭', NZL: '🇳🇿', GLOBAL: '🌍',
};
const getFlag = (r) => REGION_FLAGS[r?.toUpperCase()] || '🌐';

const IMPACT_CFG = {
    VERY_HIGH: { label: 'VERY HIGH', color: '#ef4444', bg: 'rgba(239,68,68,0.12)', border: 'rgba(239,68,68,0.3)', dot: '#ef4444' },
    HIGH:      { label: 'HIGH',      color: '#f97316', bg: 'rgba(249,115,22,0.12)', border: 'rgba(249,115,22,0.3)', dot: '#f97316' },
    MEDIUM:    { label: 'MED',       color: '#eab308', bg: 'rgba(234,179,8,0.12)',  border: 'rgba(234,179,8,0.3)',  dot: '#eab308' },
    LOW:       { label: 'LOW',       color: '#6b7280', bg: 'rgba(107,114,128,0.10)',border: 'rgba(107,114,128,0.2)',dot: '#6b7280' },
};
const getImpact = (imp) => IMPACT_CFG[imp?.toUpperCase()] || IMPACT_CFG.LOW;

const TIER_CFG = {
    1: { label: 'T1', color: '#fac815', bg: 'rgba(250,200,21,0.15)', border: 'rgba(250,200,21,0.3)' },
    2: { label: 'T2', color: '#3b82f6', bg: 'rgba(59,130,246,0.15)', border: 'rgba(59,130,246,0.3)' },
    3: { label: 'T3', color: '#6b7280', bg: 'rgba(107,114,128,0.10)',border: 'rgba(107,114,128,0.2)' },
};
const getTier = (t) => TIER_CFG[t] || TIER_CFG[3];

const ASSET_TABS = [
    { id: 'all',    label: 'All',         assets: null },
    { id: 'xauusd', label: 'XAUUSD',      assets: ['XAUUSD', 'XAU'] },
    { id: 'eurusd', label: 'EURUSD',      assets: ['EURUSD', 'EUR'] },
    { id: 'gbpusd', label: 'GBPUSD',      assets: ['GBPUSD', 'GBP'] },
    { id: 'usdjpy', label: 'USDJPY',      assets: ['USDJPY', 'JPY'] },
    { id: 'dxy',    label: 'DXY',         assets: ['DXY'] },
];

const REGION_FILTERS = ['ALL', 'USA', 'EU', 'UK', 'JPN', 'CHN', 'AUS'];

const MAIN_TABS = ['Macro', 'Fundamental', 'COT', 'Macro Notes'];

// ─── HELPERS ─────────────────────────────────────────────────────────────────

const fmtVal = (v, unit) => {
    if (v === null || v === undefined) return '—';
    const n = parseFloat(v);
    if (isNaN(n)) return String(v);
    return `${n % 1 !== 0 ? n.toFixed(2) : n}${unit || ''}`;
};

const fmtChange = (actual, previous, unit) => {
    if (actual == null || previous == null) return null;
    const a = parseFloat(actual);
    const p = parseFloat(previous);
    if (isNaN(a) || isNaN(p)) return null;
    const diff = a - p;
    return { diff, isUp: diff > 0, isDown: diff < 0, text: `${diff > 0 ? '▲+' : diff < 0 ? '▼' : ''}${diff.toFixed(2)}${unit || ''}` };
};

// ─── SKELETON ROWS ────────────────────────────────────────────────────────────

function SkeletonRows({ count = 8 }) {
    return Array.from({ length: count }).map((_, i) => (
        <tr key={i} className="border-b border-[var(--border-color)] animate-pulse">
            {[80, 180, 40, 80, 80, 80, 60, 160, 200].map((w, j) => (
                <td key={j} className="px-3 py-3">
                    <div className="h-3 rounded bg-[var(--bg-panel)]" style={{ width: `${w}px`, maxWidth: '100%' }} />
                </td>
            ))}
        </tr>
    ));
}

// ─── MACRO TABLE ROW ─────────────────────────────────────────────────────────

function MacroRow({ ind, expanded, onToggle, index }) {
    const imp = getImpact(ind.impact);
    const tier = getTier(ind.tier);
    const chg = fmtChange(ind.actual, ind.previous, ind.unit);
    const isPending = ind.actual === null || ind.actual === undefined;

    return (
        <>
            <tr
                onClick={onToggle}
                className={`border-b border-[var(--border-color)] cursor-pointer transition-colors
                    ${index % 2 === 0 ? '' : 'bg-white/[0.01]'}
                    hover:bg-[var(--bg-hover)]
                    ${expanded ? 'bg-[var(--bg-hover)]' : ''}
                `}
            >
                {/* Region */}
                <td className="px-3 py-2.5 whitespace-nowrap">
                    <div className="flex items-center gap-1.5">
                        <span className="text-sm">{getFlag(ind.region)}</span>
                        <span className="text-[10px] font-bold text-[var(--text-dim)] font-mono">{ind.region}</span>
                    </div>
                </td>

                {/* Indicator */}
                <td className="px-3 py-2.5">
                    <div className="flex items-center gap-1.5">
                        {expanded
                            ? <ChevronDown size={10} className="shrink-0 text-[var(--accent)]" />
                            : <ChevronRight size={10} className="shrink-0 text-[var(--text-dim)]" />
                        }
                        <span className="text-[11px] font-semibold text-[var(--text-primary)] leading-tight">{ind.label}</span>
                    </div>
                </td>

                {/* Tier */}
                <td className="px-3 py-2.5 text-center">
                    <span className="text-[9px] font-black px-1.5 py-0.5 rounded border font-mono"
                        style={{ color: tier.color, background: tier.bg, borderColor: tier.border }}>
                        {tier.label}
                    </span>
                </td>

                {/* Actual */}
                <td className={`px-3 py-2.5 text-right font-mono text-[11px] font-bold ${
                    isPending ? 'text-[var(--text-dim)]' :
                    chg?.isUp ? 'text-green-400' : chg?.isDown ? 'text-red-400' : 'text-[var(--text-primary)]'
                }`}>
                    {isPending
                        ? <span className="flex items-center justify-end gap-1"><div className="w-2 h-2 rounded-full bg-[var(--text-dim)] animate-pulse" />Pending</span>
                        : fmtVal(ind.actual, ind.unit)
                    }
                </td>

                {/* Previous */}
                <td className="px-3 py-2.5 text-right font-mono text-[11px] text-[var(--text-dim)]">
                    {fmtVal(ind.previous, ind.unit)}
                </td>

                {/* Change */}
                <td className={`px-3 py-2.5 text-right font-mono text-[10px] font-bold ${
                    chg?.isUp ? 'text-green-400' : chg?.isDown ? 'text-red-400' : 'text-[var(--text-dim)]'
                }`}>
                    {chg ? chg.text : '—'}
                </td>

                {/* Impact */}
                <td className="px-3 py-2.5 text-center">
                    <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border"
                        style={{ color: imp.color, background: imp.bg, borderColor: imp.border }}>
                        <span className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: imp.dot }} />
                        {imp.label}
                    </span>
                </td>

                {/* Affects */}
                <td className="px-3 py-2.5">
                    <div className="flex flex-wrap gap-1">
                        {(ind.assets || []).slice(0, 4).map(a => (
                            <span key={a} className="text-[8px] font-mono px-1 py-0.5 rounded border text-[var(--text-dim)]"
                                style={{ background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }}>
                                {a}
                            </span>
                        ))}
                    </div>
                </td>

                {/* AI Note preview */}
                <td className="px-3 py-2.5 max-w-[220px]">
                    <p className="text-[9px] text-[var(--text-dim)] truncate leading-relaxed">
                        {ind.ai_notes || '—'}
                    </p>
                </td>
            </tr>

            {/* Expanded AI Notes */}
            {expanded && ind.ai_notes && (
                <tr className="border-b border-[var(--border-color)]">
                    <td colSpan={9} className="px-0 py-0">
                        <div className="mx-3 mb-2 mt-0.5 rounded-lg p-3 flex items-start gap-2 border"
                            style={{ background: 'rgba(250,200,21,0.04)', borderColor: 'rgba(250,200,21,0.15)' }}>
                            <Zap size={12} className="text-[var(--accent)] mt-0.5 shrink-0" />
                            <div>
                                <p className="text-[8px] font-black uppercase tracking-widest text-[var(--accent)] mb-1">AI Notes</p>
                                <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{ind.ai_notes}</p>
                                {ind.period && (
                                    <p className="text-[8px] text-[var(--text-dim)] mt-1 flex items-center gap-1">
                                        <Clock size={8} /> Period: {ind.period}
                                        {ind.scraped_at && <span className="ml-2 opacity-60">· Scraped: {new Date(ind.scraped_at).toLocaleString('id-ID')}</span>}
                                    </p>
                                )}
                            </div>
                        </div>
                    </td>
                </tr>
            )}
        </>
    );
}

// ─── MACRO TABLE ─────────────────────────────────────────────────────────────

function MacroTable({ indicators, loading }) {
    const [expandedKey, setExpandedKey] = useState(null);

    const sorted = [...indicators].sort((a, b) => {
        const tierOrder = { 1: 0, 2: 1, 3: 2 };
        const ta = tierOrder[a.tier] ?? 9;
        const tb = tierOrder[b.tier] ?? 9;
        if (ta !== tb) return ta - tb;
        const impOrder = { VERY_HIGH: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
        const ia = impOrder[a.impact?.toUpperCase()] ?? 9;
        const ib = impOrder[b.impact?.toUpperCase()] ?? 9;
        if (ia !== ib) return ia - ib;
        return (a.region || '').localeCompare(b.region || '');
    });

    return (
        <div className="rounded-xl border border-[var(--border-color)] overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-[11px] border-collapse min-w-[900px]">
                    <thead>
                        <tr className="bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                            {['Region', 'Indicator', 'Tier', 'Actual', 'Previous', 'Change', 'Impact', 'Affects', 'AI Note'].map((h, i) => (
                                <th key={h} className={`px-3 py-2.5 text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] ${
                                    i >= 3 && i <= 5 ? 'text-right' : i === 6 || i === 2 ? 'text-center' : 'text-left'
                                }`}>{h}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {loading
                            ? <SkeletonRows count={8} />
                            : sorted.length === 0
                                ? (
                                    <tr>
                                        <td colSpan={9} className="py-16 text-center text-[var(--text-dim)]">
                                            <BarChart2 size={28} className="mx-auto mb-2 opacity-30" />
                                            <p className="text-xs font-bold">No indicators found</p>
                                        </td>
                                    </tr>
                                )
                                : sorted.map((ind, i) => (
                                    <MacroRow
                                        key={ind.key || i}
                                        ind={ind}
                                        index={i}
                                        expanded={expandedKey === (ind.key || i)}
                                        onToggle={() => setExpandedKey(expandedKey === (ind.key || i) ? null : (ind.key || i))}
                                    />
                                ))
                        }
                    </tbody>
                </table>
            </div>
        </div>
    );
}

// ─── FUNDAMENTAL TAB (grouped by asset) ──────────────────────────────────────

function FundamentalTab({ indicators, loading }) {
    const [activeAsset, setActiveAsset] = useState('all');

    const assetTab = ASSET_TABS.find(t => t.id === activeAsset);
    const filtered = assetTab?.assets
        ? indicators.filter(ind => (ind.assets || []).some(a =>
            assetTab.assets.some(ta => a.toUpperCase().includes(ta.toUpperCase()))
          ))
        : indicators;

    const counts = ASSET_TABS.map(t => {
        if (!t.assets) return { ...t, count: indicators.length };
        const cnt = indicators.filter(ind => (ind.assets || []).some(a =>
            t.assets.some(ta => a.toUpperCase().includes(ta.toUpperCase()))
        )).length;
        return { ...t, count: cnt };
    });

    return (
        <div className="space-y-4">
            {/* Asset sub-tabs */}
            <div className="flex gap-1 overflow-x-auto scrollbar-none bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-1">
                {counts.map(t => (
                    <button key={t.id} onClick={() => setActiveAsset(t.id)}
                        className={`px-3 py-2 rounded-lg text-[10px] font-black whitespace-nowrap transition-all flex items-center gap-1 ${
                            activeAsset === t.id
                                ? 'bg-[var(--accent)] text-black shadow'
                                : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                        }`}>
                        {t.label}
                        <span className={`text-[8px] px-1 py-0.5 rounded ${activeAsset === t.id ? 'bg-black/20' : 'bg-[var(--bg-card)]'}`}>
                            {t.count}
                        </span>
                    </button>
                ))}
            </div>
            <MacroTable indicators={filtered} loading={loading} />
        </div>
    );
}

// ─── COT TAB ─────────────────────────────────────────────────────────────────

function COTTab() {
    return (
        <div className="rounded-xl border border-[var(--border-color)] p-12 text-center bg-[var(--bg-card)]">
            <div className="text-5xl mb-4">📊</div>
            <h3 className="text-sm font-black text-[var(--text-primary)] mb-2">COT Report — Coming Soon</h3>
            <p className="text-[10px] text-[var(--text-dim)] max-w-sm mx-auto leading-relaxed">
                Commitments of Traders (CFTC) data will show net positioning for major currencies and commodities.
                Integration with CFTC data feed is in progress.
            </p>
            <div className="mt-6 flex flex-wrap justify-center gap-2">
                {['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'AUDUSD'].map(p => (
                    <span key={p} className="text-[9px] font-mono px-2 py-1 rounded border text-[var(--text-dim)]"
                        style={{ background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }}>
                        {p}
                    </span>
                ))}
            </div>
        </div>
    );
}

// ─── SUMMARY STATS ────────────────────────────────────────────────────────────

function SummaryStats({ indicators }) {
    const loaded = indicators.filter(i => i.actual != null).length;
    const t1 = indicators.filter(i => i.tier === 1 || i.tier === '1').length;
    const bullish = indicators.filter(i => i.actual != null && i.previous != null && parseFloat(i.actual) > parseFloat(i.previous)).length;
    const bearish = indicators.filter(i => i.actual != null && i.previous != null && parseFloat(i.actual) < parseFloat(i.previous)).length;

    return (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {[
                { label: 'Total', value: indicators.length, color: 'text-[var(--text-primary)]' },
                { label: 'Data Loaded', value: `${loaded}/${indicators.length}`, color: 'text-green-400' },
                { label: 'Tier 1', value: t1, color: 'text-[var(--accent)]' },
                { label: 'Bullish', value: bullish, color: 'text-green-400' },
                { label: 'Bearish', value: bearish, color: 'text-red-400' },
            ].map((s, i) => (
                <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-3">
                    <p className="text-[8px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1">{s.label}</p>
                    <p className={`text-xl font-black font-mono ${s.color}`}>{s.value}</p>
                </div>
            ))}
        </div>
    );
}

// ─── MAIN VIEW ───────────────────────────────────────────────────────────────

export default function FundamentalView() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [refreshing, setRefreshing] = useState(false);
    const [lastUpdated, setLastUpdated] = useState('');
    const [activeTab, setActiveTab] = useState('Macro');
    const [regionFilter, setRegionFilter] = useState('ALL');
    const [manualContent, setManualContent] = useState('');
    const [manualLoading, setManualLoading] = useState(false);

    const loadData = useCallback(async () => {
        try {
            setError('');
            const res = await fetchMacro();
            setData(res);
            if (res.last_updated) {
                setLastUpdated(new Date(res.last_updated).toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }));
            }
        } catch (e) {
            const status = e?.response?.status;
            setError(
                status === 401 ? 'Session expired. Please refresh.' :
                status === 404 ? 'Endpoint not found. Check fundamental-service.' :
                'Failed to fetch macro data. Ensure fundamental-service is running.'
            );
        } finally {
            setLoading(false);
        }
    }, []);

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            const token = localStorage.getItem('gas-token') || '';
            await axios.post('/terminal/fundamental/refresh', {}, {
                timeout: 10000,
                headers: { Authorization: `Bearer ${token}` }
            });
            setTimeout(() => { loadData(); setRefreshing(false); }, 8000);
        } catch {
            setTimeout(() => { loadData(); setRefreshing(false); }, 3000);
        }
    };

    useEffect(() => { loadData(); }, [loadData]);

    useEffect(() => {
        setManualLoading(true);
        fetch('/terminal/content/fundamental.md')
            .then(r => r.json())
            .then(d => setManualContent(d.content || ''))
            .catch(() => setManualContent(''))
            .finally(() => setManualLoading(false));
    }, []);

    const indicators = data?.indicators || [];
    const regionFiltered = regionFilter === 'ALL'
        ? indicators
        : indicators.filter(ind => ind.region?.toUpperCase() === regionFilter);

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-8 max-w-[1400px] mx-auto space-y-4">

            {/* ── HEADER ── */}
            <div className="flex items-start justify-between flex-wrap gap-3">
                <div>
                    <h2 className="text-xl font-display font-black uppercase flex items-center gap-2">
                        <Activity size={20} className="text-[var(--accent)]" />
                        Fundamental & Macro Data
                    </h2>
                    <p className="text-[10px] text-[var(--text-dim)] font-mono mt-0.5">
                        Trading Economics · {lastUpdated ? `Updated: ${lastUpdated}` : 'Loading...'}
                    </p>
                </div>
                <div className="flex items-center gap-2 flex-wrap">
                    {/* Region filter */}
                    <div className="flex bg-[var(--bg-panel)] rounded-lg p-0.5 border border-[var(--border-color)] gap-0.5">
                        {REGION_FILTERS.map(r => (
                            <button key={r} onClick={() => setRegionFilter(r)}
                                className={`px-2.5 py-1.5 rounded-md text-[9px] font-black transition-all ${
                                    regionFilter === r
                                        ? 'bg-[var(--accent)] text-black'
                                        : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                                }`}>
                                {getFlag(r)} {r}
                            </button>
                        ))}
                    </div>
                    <button onClick={handleRefresh} disabled={refreshing}
                        className="flex items-center gap-1.5 px-3 py-2 rounded-lg border border-[var(--border-color)] text-[10px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all disabled:opacity-50">
                        <RefreshCw size={11} className={refreshing ? 'animate-spin' : ''} />
                        {refreshing ? 'Refreshing...' : 'Refresh'}
                    </button>
                </div>
            </div>

            {/* ── SUMMARY ── */}
            {!loading && indicators.length > 0 && <SummaryStats indicators={indicators} />}

            {/* ── MAIN TABS ── */}
            <div className="flex gap-1 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1 w-fit">
                {MAIN_TABS.map(t => (
                    <button key={t} onClick={() => setActiveTab(t)}
                        className={`px-4 py-2 rounded-lg text-[10px] font-black transition-all ${
                            activeTab === t
                                ? 'bg-[var(--accent)] text-black shadow'
                                : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                        }`}>
                        {t}
                    </button>
                ))}
            </div>

            {/* ── ERROR ── */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
                    <AlertTriangle size={16} className="text-red-400 shrink-0" />
                    <div className="flex-1">
                        <p className="text-xs font-black text-red-400">Connection Error</p>
                        <p className="text-[10px] text-[var(--text-dim)] mt-0.5">{error}</p>
                    </div>
                    <button onClick={loadData} className="text-[9px] font-black px-3 py-1.5 rounded-lg border border-red-500/30 text-red-400 hover:bg-red-500/10 transition-all">
                        Retry
                    </button>
                </div>
            )}

            {/* ── TAB CONTENT ── */}
            {activeTab === 'Macro' && <MacroTable indicators={regionFiltered} loading={loading} />}
            {activeTab === 'Fundamental' && <FundamentalTab indicators={regionFiltered} loading={loading} />}
            {activeTab === 'COT' && <COTTab />}
            {activeTab === 'Macro Notes' && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                    {manualLoading ? (
                        <div className="text-center py-12 text-[var(--text-dim)] text-sm">Memuat data...</div>
                    ) : (
                        <div className="prose-gas space-y-4">
                            {manualContent.split('\n').map((line, i) => {
                                const trimmed = line.trim();
                                if (!trimmed || trimmed.startsWith('<!--')) return null;
                                if (trimmed.startsWith('## ')) return (
                                    <div key={i} className="pt-4 pb-1 border-b border-[var(--border-color)]">
                                        <h2 className="text-base font-black text-[var(--text-primary)]">{trimmed.slice(3)}</h2>
                                    </div>
                                );
                                if (trimmed.startsWith('### ')) return (
                                    <h3 key={i} className="text-sm font-bold text-[var(--accent)] mt-3">{trimmed.slice(4)}</h3>
                                );
                                if (trimmed.startsWith('---')) return <hr key={i} className="border-[var(--border-color)] my-3" />;
                                if (trimmed.startsWith('- ')) {
                                    const text = trimmed.slice(2).replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--text-primary)">$1</strong>');
                                    return <p key={i} className="text-xs text-[var(--text-secondary)] pl-3 border-l-2 border-[var(--border-subtle)] py-0.5 leading-relaxed" dangerouslySetInnerHTML={{ __html: `• ${text}` }} />;
                                }
                                if (trimmed.startsWith('*')) return <p key={i} className="text-[10px] text-[var(--text-dim)] italic mt-4">{trimmed.replace(/^\*+|\*+$/g, '')}</p>;
                                return <p key={i} className="text-xs text-[var(--text-secondary)] leading-relaxed">{trimmed}</p>;
                            })}
                        </div>
                    )}
                    <div className="mt-6 flex items-center justify-between">
                        <p className="text-[10px] text-[var(--text-dim)]">Data dari file fundamental.md — update via Content Editor</p>
                        <a href="/editor" target="_blank" className="text-[10px] text-[var(--accent)] hover:underline font-bold">Edit ↗</a>
                    </div>
                </div>
            )}

            {/* ── LEGEND ── */}
            {!loading && (
                <div className="flex items-center gap-4 flex-wrap text-[9px] text-[var(--text-dim)]">
                    <span className="font-black uppercase tracking-widest">Impact:</span>
                    {Object.entries(IMPACT_CFG).map(([k, v]) => (
                        <span key={k} className="flex items-center gap-1">
                            <span className="w-2 h-2 rounded-full" style={{ background: v.dot }} />
                            {v.label}
                        </span>
                    ))}
                    <span className="ml-4 font-black uppercase tracking-widest">Tier:</span>
                    {Object.entries(TIER_CFG).map(([k, v]) => (
                        <span key={k} className="flex items-center gap-1 font-mono px-1.5 py-0.5 rounded border"
                            style={{ color: v.color, background: v.bg, borderColor: v.border }}>
                            {v.label}
                        </span>
                    ))}
                    <span className="ml-auto font-mono opacity-60">Click any row to expand AI notes</span>
                </div>
            )}
        </div>
    );
}
