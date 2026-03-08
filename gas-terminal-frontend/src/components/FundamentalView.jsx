import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import {
    RefreshCw, TrendingUp, TrendingDown, Minus,
    Globe, Clock, AlertTriangle, ChevronRight, Activity,
    Zap, BarChart2
} from 'lucide-react';

// ─── ASSET CATEGORY TABS ─────────────────────────────────────────────────────
const CATEGORIES = [
    { id: 'all',     label: 'All',         assets: null },
    { id: 'gold',    label: 'Gold (XAU)',  assets: ['XAUUSD'] },
    { id: 'oil',     label: 'Oil',         assets: ['XTIUSD', 'XBRUSD'] },
    { id: 'silver',  label: 'Silver',      assets: ['XAGUSD'] },
    { id: 'eurusd',  label: 'EUR/USD',     assets: ['EURUSD'] },
    { id: 'usdjpy',  label: 'USD/JPY',     assets: ['USDJPY'] },
    { id: 'gbpusd',  label: 'GBP/USD',     assets: ['GBPUSD'] },
    { id: 'indices', label: 'Indices',     assets: ['SPX', 'NDQ', 'DJI', 'VIX', 'DXY'] },
    { id: 'crypto',  label: 'Crypto',      assets: ['BTCUSD', 'ETHUSD'] },
];

// ─── IMPACT CONFIG ───────────────────────────────────────────────────────────
const IMPACT = {
    VERY_HIGH: { label: 'Sangat Tinggi', color: '#ef4444', bg: 'rgba(239,68,68,0.12)', dot: '#ef4444' },
    HIGH:      { label: 'Tinggi',         color: '#f97316', bg: 'rgba(249,115,22,0.12)', dot: '#f97316' },
    MEDIUM:    { label: 'Sedang',         color: '#eab308', bg: 'rgba(234,179,8,0.12)',  dot: '#eab308' },
    LOW:       { label: 'Rendah',         color: '#6b7280', bg: 'rgba(107,114,128,0.1)', dot: '#6b7280' },
};

// ─── SPARKLINE (pure SVG) ────────────────────────────────────────────────────
function Sparkline({ history, color = '#fac815' }) {
    if (!history || history.length < 2) {
        return <div className="w-full h-10 flex items-center justify-center text-[9px] text-[var(--text-dim)]">No data</div>;
    }
    const vals = history.map(h => h.value);
    const min = Math.min(...vals);
    const max = Math.max(...vals);
    const range = max - min || 1;
    const w = 100, h = 36;
    const pts = vals.map((v, i) => {
        const x = (i / (vals.length - 1)) * w;
        const y = h - ((v - min) / range) * (h - 4) - 2;
        return `${x.toFixed(1)},${y.toFixed(1)}`;
    }).join(' ');
    const last = vals[vals.length - 1];
    const prev = vals[vals.length - 2];
    const lineColor = last >= prev ? '#10b981' : '#ef4444';

    return (
        <svg viewBox={`0 0 ${w} ${h}`} className="w-full" style={{ height: 36 }} preserveAspectRatio="none">
            <polyline points={pts} fill="none" stroke={lineColor} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
            <circle cx={parseFloat(pts.split(' ').pop().split(',')[0])} cy={parseFloat(pts.split(' ').pop().split(',')[1])} r="2.5" fill={lineColor} />
        </svg>
    );
}

// ─── INDICATOR CARD ──────────────────────────────────────────────────────────
function IndicatorCard({ ind, expanded, onToggle }) {
    const imp = IMPACT[ind.impact] || IMPACT.MEDIUM;
    const hasActual = ind.actual !== null && ind.actual !== undefined;
    const change = hasActual && ind.previous != null ? ind.actual - ind.previous : null;
    const isUp = change !== null ? change > 0 : null;

    return (
        <div
            className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden cursor-pointer hover:border-[var(--accent)]/40 transition-all"
            onClick={onToggle}
        >
            {/* Card Header */}
            <div className="p-4">
                <div className="flex items-start justify-between gap-2 mb-3">
                    <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                            {/* Tier badge */}
                            <span className="text-[8px] font-black px-1.5 py-0.5 rounded bg-[var(--bg-panel)] text-[var(--text-dim)] border border-[var(--border-color)] uppercase tracking-widest">
                                T{ind.tier}
                            </span>
                            {/* Region */}
                            <span className="text-[9px] font-bold text-[var(--text-dim)] flex items-center gap-1">
                                <Globe size={9} />{ind.region}
                            </span>
                        </div>
                        <p className="text-[11px] font-black text-[var(--text-primary)] leading-tight">{ind.label}</p>
                    </div>

                    {/* Impact badge */}
                    <span className="shrink-0 text-[8px] font-black px-2 py-1 rounded-lg uppercase tracking-wider"
                        style={{ background: imp.bg, color: imp.color }}>
                        <span className="inline-block w-1.5 h-1.5 rounded-full mr-1" style={{ background: imp.dot }} />
                        {imp.label}
                    </span>
                </div>

                {/* Values row */}
                <div className="flex items-end justify-between">
                    <div>
                        {hasActual ? (
                            <div className="flex items-baseline gap-2">
                                <span className="text-2xl font-black font-mono text-[var(--text-primary)]">
                                    {ind.actual?.toFixed(2)}{ind.unit}
                                </span>
                                {change !== null && (
                                    <span className={`text-xs font-black flex items-center gap-0.5 ${isUp ? 'text-[var(--success)]' : change < 0 ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'}`}>
                                        {isUp ? <TrendingUp size={11} /> : change < 0 ? <TrendingDown size={11} /> : <Minus size={11} />}
                                        {change > 0 ? '+' : ''}{change.toFixed(2)}
                                    </span>
                                )}
                            </div>
                        ) : (
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full border-2 border-[var(--accent)] border-t-transparent animate-spin" />
                                <span className="text-xs text-[var(--text-dim)]">Loading...</span>
                            </div>
                        )}
                        {ind.previous != null && (
                            <p className="text-[10px] text-[var(--text-dim)] mt-0.5">
                                Prev: <span className="font-mono">{ind.previous?.toFixed(2)}{ind.unit}</span>
                                {ind.forecast != null && (
                                    <span className="ml-2">· Forecast: <span className="font-mono text-[var(--accent)]">{ind.forecast?.toFixed(2)}{ind.unit}</span></span>
                                )}
                            </p>
                        )}
                    </div>

                    {/* Mini sparkline */}
                    <div className="w-24 ml-3">
                        <Sparkline history={ind.history} />
                    </div>
                </div>

                {/* Period + status */}
                <div className="flex items-center justify-between mt-2">
                    <span className="text-[9px] text-[var(--text-dim)] flex items-center gap-1">
                        <Clock size={9} />{ind.period}
                    </span>
                    <span className={`text-[9px] font-black flex items-center gap-1 ${ind.status === 'loading' ? 'text-[var(--text-dim)]' : 'text-[var(--success)]'}`}>
                        <div className={`w-1.5 h-1.5 rounded-full ${ind.status === 'loading' ? 'bg-[var(--text-dim)]' : 'bg-[var(--success)] animate-pulse'}`} />
                        {ind.status === 'loading' ? 'Mengambil data...' : 'Updated'}
                    </span>
                </div>
            </div>

            {/* Affected assets */}
            <div className="px-4 py-2 border-t border-[var(--border-color)] bg-[var(--bg-panel)]/40 flex flex-wrap gap-1">
                {ind.assets.map(a => (
                    <span key={a} className="text-[9px] font-black px-1.5 py-0.5 rounded bg-[var(--bg-hover)] text-[var(--text-dim)] border border-[var(--border-color)]">
                        {a}
                    </span>
                ))}
            </div>

            {/* Expanded: AI Notes */}
            {expanded && ind.ai_notes && (
                <div className="px-4 py-3 border-t border-[var(--border-color)] bg-[var(--accent)]/5">
                    <div className="flex items-start gap-2">
                        <Zap size={12} className="text-[var(--accent)] mt-0.5 shrink-0" />
                        <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{ind.ai_notes}</p>
                    </div>
                </div>
            )}
        </div>
    );
}

// ─── IMPACT LEGEND ───────────────────────────────────────────────────────────
function ImpactLegend() {
    return (
        <div className="flex items-center gap-3 flex-wrap">
            {Object.entries(IMPACT).map(([k, v]) => (
                <div key={k} className="flex items-center gap-1.5">
                    <div className="w-2 h-2 rounded-full" style={{ background: v.dot }} />
                    <span className="text-[9px] font-bold text-[var(--text-dim)]">{v.label}</span>
                </div>
            ))}
        </div>
    );
}

// ─── SUMMARY STATS BAR ────────────────────────────────────────────────────────
function SummaryBar({ indicators }) {
    const total = indicators.length;
    const loaded = indicators.filter(i => i.actual != null).length;
    const vhigh = indicators.filter(i => i.impact === 'VERY_HIGH').length;
    const high = indicators.filter(i => i.impact === 'HIGH').length;
    const bullish = indicators.filter(i => {
        if (i.actual == null || i.previous == null) return false;
        return i.actual > i.previous;
    }).length;
    const bearish = indicators.filter(i => {
        if (i.actual == null || i.previous == null) return false;
        return i.actual < i.previous;
    }).length;

    return (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            {[
                { label: 'Total Indikator', value: total, color: 'text-[var(--text-primary)]' },
                { label: 'Data Loaded', value: `${loaded}/${total}`, color: 'text-[var(--success)]' },
                { label: 'Tier 1', value: vhigh + high, color: 'text-[var(--danger)]' },
                { label: 'Bullish Signal', value: bullish, color: 'text-[var(--success)]' },
                { label: 'Bearish Signal', value: bearish, color: 'text-[var(--danger)]' },
            ].map((s, i) => (
                <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-3">
                    <p className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1">{s.label}</p>
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
    const [activeCategory, setActiveCategory] = useState('all');
    const [expandedKey, setExpandedKey] = useState(null);
    const [refreshing, setRefreshing] = useState(false);
    const [lastUpdated, setLastUpdated] = useState('');

    const fetchData = useCallback(async () => {
        try {
            setError('');
            const res = await axios.get('/terminal/fundamental/macro', { timeout: 15000 });
            setData(res.data);
            if (res.data.last_updated) {
                const d = new Date(res.data.last_updated);
                setLastUpdated(d.toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' }));
            }
        } catch (e) {
            setError('Gagal mengambil data makro. Pastikan fundamental service berjalan.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchData(); }, [fetchData]);

    const handleRefresh = async () => {
        setRefreshing(true);
        try {
            await axios.post('/terminal/fundamental/refresh', {}, { timeout: 10000 });
            // Give scraper 10s head start then reload
            setTimeout(() => {
                fetchData();
                setRefreshing(false);
            }, 10000);
        } catch {
            setRefreshing(false);
        }
    };

    const indicators = data?.indicators || [];
    const activeCat = CATEGORIES.find(c => c.id === activeCategory);
    const filtered = activeCat?.assets
        ? indicators.filter(ind => ind.assets.some(a => activeCat.assets.includes(a)))
        : indicators;

    // Sort: VERY_HIGH first, then HIGH, then loaded first
    const sorted = [...filtered].sort((a, b) => {
        const impOrder = { VERY_HIGH: 0, HIGH: 1, MEDIUM: 2, LOW: 3 };
        const ia = impOrder[a.impact] ?? 9;
        const ib = impOrder[b.impact] ?? 9;
        if (ia !== ib) return ia - ib;
        const la = a.actual != null ? 0 : 1;
        const lb = b.actual != null ? 0 : 1;
        return la - lb;
    });

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-8 max-w-7xl mx-auto space-y-5">

            {/* ── HEADER ── */}
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h2 className="text-2xl font-display font-black uppercase flex items-center gap-2">
                        <Activity size={22} className="text-[var(--accent)]" />
                        Fundamental Macro
                    </h2>
                    <p className="text-[11px] text-[var(--text-dim)] font-bold mt-0.5">
                        Data dari Trading Economics via tedata · {lastUpdated ? `Diperbarui ${lastUpdated}` : 'Memuat...'}
                    </p>
                </div>
                <div className="flex items-center gap-3">
                    <ImpactLegend />
                    <button
                        onClick={handleRefresh}
                        disabled={refreshing}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg border border-[var(--border-color)] text-[10px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all disabled:opacity-50"
                    >
                        <RefreshCw size={12} className={refreshing ? 'animate-spin' : ''} />
                        {refreshing ? 'Scraping TE...' : 'Refresh Data'}
                    </button>
                </div>
            </div>

            {/* ── SUMMARY BAR ── */}
            {!loading && <SummaryBar indicators={indicators} />}

            {/* ── CATEGORY TABS ── */}
            <div className="flex gap-1 overflow-x-auto scrollbar-none bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1">
                {CATEGORIES.map(cat => (
                    <button key={cat.id} onClick={() => setActiveCategory(cat.id)}
                        className={`px-3 py-2 rounded-lg text-[10px] font-black whitespace-nowrap transition-all ${activeCategory === cat.id ? 'bg-[var(--accent)] text-black shadow' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                        {cat.label}
                        {cat.assets && (
                            <span className="ml-1 opacity-60">
                                ({(data?.indicators || []).filter(i => i.assets.some(a => cat.assets.includes(a))).length})
                            </span>
                        )}
                    </button>
                ))}
            </div>

            {/* ── ERROR ── */}
            {error && (
                <div className="bg-[var(--danger)]/10 border border-[var(--danger)]/20 rounded-xl p-4 flex items-center gap-3">
                    <AlertTriangle size={16} className="text-[var(--danger)] shrink-0" />
                    <div>
                        <p className="text-xs font-black text-[var(--danger)]">Connection Error</p>
                        <p className="text-[10px] text-[var(--text-dim)] mt-0.5">{error}</p>
                    </div>
                </div>
            )}

            {/* ── LOADING SKELETON ── */}
            {loading && (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                    {[...Array(9)].map((_, i) => (
                        <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4 animate-pulse">
                            <div className="h-3 bg-[var(--bg-panel)] rounded w-3/4 mb-3" />
                            <div className="h-7 bg-[var(--bg-panel)] rounded w-1/2 mb-2" />
                            <div className="h-2 bg-[var(--bg-panel)] rounded w-full" />
                        </div>
                    ))}
                </div>
            )}

            {/* ── INDICATOR GRID ── */}
            {!loading && sorted.length > 0 && (
                <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
                    {sorted.map(ind => (
                        <IndicatorCard
                            key={ind.key}
                            ind={ind}
                            expanded={expandedKey === ind.key}
                            onToggle={() => setExpandedKey(expandedKey === ind.key ? null : ind.key)}
                        />
                    ))}
                </div>
            )}

            {!loading && sorted.length === 0 && !error && (
                <div className="text-center py-16 text-[var(--text-dim)]">
                    <BarChart2 size={32} className="mx-auto mb-3 opacity-30" />
                    <p className="text-sm font-bold">Tidak ada indikator untuk kategori ini</p>
                </div>
            )}

            {/* ── TE URL REFERENCE ── */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-3">
                    Trading Economics Data Sources
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-h-48 overflow-y-auto scrollbar-none">
                    {Object.entries({
                        'US CPI': 'tradingeconomics.com/united-states/inflation-cpi',
                        'US Core CPI': 'tradingeconomics.com/united-states/core-inflation-rate',
                        'Non-Farm Payrolls': 'tradingeconomics.com/united-states/non-farm-payrolls',
                        'Fed Rate': 'tradingeconomics.com/united-states/interest-rate',
                        'US 10Y Yield': 'tradingeconomics.com/united-states/government-bond-yield',
                        'EIA Crude': 'tradingeconomics.com/united-states/crude-oil-stocks-change',
                        'US Mfg PMI': 'tradingeconomics.com/united-states/manufacturing-pmi',
                        'Industrial Prod': 'tradingeconomics.com/united-states/industrial-production',
                        'US GDP': 'tradingeconomics.com/united-states/gdp-growth',
                        'EU CPI': 'tradingeconomics.com/euro-area/inflation-cpi',
                        'ECB Rate': 'tradingeconomics.com/euro-area/interest-rate',
                        'EU GDP': 'tradingeconomics.com/euro-area/gdp-growth',
                        'EU Mfg PMI': 'tradingeconomics.com/euro-area/manufacturing-pmi',
                        'BOJ Rate': 'tradingeconomics.com/japan/interest-rate',
                        'UK CPI': 'tradingeconomics.com/united-kingdom/inflation-cpi',
                        'BOE Rate': 'tradingeconomics.com/united-kingdom/interest-rate',
                        'China PMI': 'tradingeconomics.com/china/manufacturing-pmi',
                        'Global PMI': 'tradingeconomics.com/world/manufacturing-pmi',
                    }).map(([label, url]) => (
                        <div key={label} className="flex items-center gap-2 text-[9px]">
                            <ChevronRight size={9} className="text-[var(--accent)] shrink-0" />
                            <span className="font-black text-[var(--text-dim)] w-28 shrink-0">{label}</span>
                            <span className="text-[var(--text-dim)] font-mono truncate opacity-60">{url}</span>
                        </div>
                    ))}
                </div>
                <p className="text-[9px] text-[var(--text-dim)] mt-3 opacity-60">
                    Scraped via tedata (github.com/HelloThereMatey/tedata) · highcharts_api method · Firefox headless
                </p>
            </div>
        </div>
    );
}
