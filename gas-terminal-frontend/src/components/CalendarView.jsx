import React, { useEffect, useState, useCallback, useRef } from 'react';
import { RefreshCw, Brain, ExternalLink, AlertTriangle } from 'lucide-react';
import { fetchCalendar, fetchCalendarAnalysis, fetchNews } from '../services/api';

// ── Helpers ──────────────────────────────────────────────────────────────────

const pad = (n) => String(n).padStart(2, '0');
const WIB_OFFSET_MS = 7 * 3600 * 1000;

const wibDayToUTC = (date, endOfDay = false) => {
    const wibMidnight = new Date(date.getFullYear(), date.getMonth(), date.getDate(), 0, 0, 0);
    const utcStart = new Date(wibMidnight.getTime() - WIB_OFFSET_MS);
    if (endOfDay) {
        return new Date(utcStart.getTime() + 24 * 3600 * 1000 - 1000).toISOString().replace('Z', '');
    }
    return utcStart.toISOString().replace('Z', '');
};

const addDays = (date, n) => { const d = new Date(date); d.setDate(d.getDate() + n); return d; };

const getDateRange = (tab) => {
    const today = new Date(); today.setHours(0, 0, 0, 0);
    switch (tab) {
        case 'Yesterday':  return { from: wibDayToUTC(addDays(today, -1)), to: wibDayToUTC(addDays(today, -1), true) };
        case 'Today':      return { from: wibDayToUTC(today), to: wibDayToUTC(today, true) };
        case 'Tomorrow':   return { from: wibDayToUTC(addDays(today, 1)), to: wibDayToUTC(addDays(today, 1), true) };
        case 'This Week':  return { from: wibDayToUTC(addDays(today, -1)), to: wibDayToUTC(addDays(today, 7), true) };
        case 'This Month': {
            const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
            const lastDay  = new Date(today.getFullYear(), today.getMonth() + 1, 0);
            return { from: wibDayToUTC(firstDay), to: wibDayToUTC(lastDay, true) };
        }
        default:           return { from: wibDayToUTC(today), to: wibDayToUTC(today, true) };
    }
};

const FLAGS = {
    USA:'🇺🇸', USD:'🇺🇸', EUR:'🇪🇺', JPY:'🇯🇵', GBP:'🇬🇧',
    AUD:'🇦🇺', CAD:'🇨🇦', CHF:'🇨🇭', NZD:'🇳🇿', CNY:'🇨🇳',
    CNH:'🇨🇳', KRW:'🇰🇷', SGD:'🇸🇬', HKD:'🇭🇰', MXN:'🇲🇽',
};
const getFlag = (c) => FLAGS[c?.toUpperCase()] || '🌐';

const IMPACT_CFG = {
    high:   { label: 'HIGH',  color: '#ef4444', bg: 'rgba(239,68,68,0.12)',  border: 'rgba(239,68,68,0.3)' },
    medium: { label: 'MED',   color: '#eab308', bg: 'rgba(234,179,8,0.12)',  border: 'rgba(234,179,8,0.3)' },
    low:    { label: 'LOW',   color: '#6b7280', bg: 'rgba(107,114,128,0.1)', border: 'rgba(107,114,128,0.2)' },
};
const getImpact = (imp) => IMPACT_CFG[imp?.toLowerCase()] || IMPACT_CFG.low;

const formatTime = (utcStr) => {
    try {
        const d = new Date(utcStr);
        const wib = new Date(d.getTime() + WIB_OFFSET_MS);
        return `${pad(wib.getUTCHours())}:${pad(wib.getUTCMinutes())}`;
    } catch { return '--:--'; }
};

const formatDateHeader = (utcStr) => {
    try {
        const d = new Date(utcStr);
        const wib = new Date(d.getTime() + WIB_OFFSET_MS);
        const today = new Date(); today.setHours(0, 0, 0, 0);
        const todayWib = new Date(today.getTime() + WIB_OFFSET_MS);
        const eventDay = new Date(wib.getUTCFullYear(), wib.getUTCMonth(), wib.getUTCDate());
        const todayDay = new Date(todayWib.getUTCFullYear(), todayWib.getUTCMonth(), todayWib.getUTCDate());
        const diff = Math.round((eventDay - todayDay) / 86400000);
        const dayNames = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
        const monthNames = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
        const dayStr = `${dayNames[wib.getUTCDay()]}, ${wib.getUTCDate()} ${monthNames[wib.getUTCMonth()]} ${wib.getUTCFullYear()}`;
        let label = ''; let emoji = '📆';
        if (diff === -1)      { label = 'KEMARIN'; emoji = '⏮️'; }
        else if (diff === 0)  { label = 'HARI INI'; emoji = '📅'; }
        else if (diff === 1)  { label = 'BESOK';    emoji = '⏭️'; }
        else if (diff > 1)    { label = `+${diff} HARI`; }
        return { dayStr, label, emoji };
    } catch { return { dayStr: utcStr, label: '', emoji: '📅' }; }
};

const groupByDate = (events) => {
    const groups = {};
    events.forEach(e => {
        const d = new Date(e.time_utc);
        const wib = new Date(d.getTime() + WIB_OFFSET_MS);
        const key = `${wib.getUTCFullYear()}-${pad(wib.getUTCMonth()+1)}-${pad(wib.getUTCDate())}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push(e);
    });
    return Object.entries(groups).sort(([a],[b]) => a.localeCompare(b));
};

const formatRelativeTime = (publishedAt) => {
    try {
        const d = new Date(publishedAt);
        const now = new Date();
        const diffMs = now - d;
        const diffMin = Math.floor(diffMs / 60000);
        if (diffMin < 1) return 'baru saja';
        if (diffMin < 60) return `${diffMin} menit lalu`;
        const diffHr = Math.floor(diffMin / 60);
        if (diffHr < 24) return `${diffHr} jam lalu`;
        return `${Math.floor(diffHr / 24)} hari lalu`;
    } catch { return '—'; }
};

const isFresh = (publishedAt) => {
    try {
        return (new Date() - new Date(publishedAt)) < 10 * 60 * 1000;
    } catch { return false; }
};

const getSurprise = (actual, forecast) => {
    if (actual === null || actual === undefined || forecast === null || forecast === undefined) return null;
    const diff = parseFloat(actual) - parseFloat(forecast);
    if (Math.abs(diff) < 0.0001) return { label: '= Match', color: 'text-[var(--text-dim)]', bg: 'bg-gray-500/10' };
    if (diff > 0) return { label: '✅ Better', color: 'text-green-400', bg: 'bg-green-500/10' };
    return { label: '❌ Miss', color: 'text-red-400', bg: 'bg-red-500/10' };
};

const SOURCE_COLORS = {
    reuters:   { bg: 'rgba(249,115,22,0.15)', color: '#f97316', border: 'rgba(249,115,22,0.3)' },
    bloomberg: { bg: 'rgba(59,130,246,0.15)', color: '#3b82f6', border: 'rgba(59,130,246,0.3)' },
    cnbc:      { bg: 'rgba(239,68,68,0.15)',  color: '#ef4444', border: 'rgba(239,68,68,0.3)' },
    'financial times': { bg: 'rgba(250,200,21,0.15)', color: '#fac815', border: 'rgba(250,200,21,0.3)' },
    ft:        { bg: 'rgba(250,200,21,0.15)', color: '#fac815', border: 'rgba(250,200,21,0.3)' },
};
const getSourceStyle = (src) => SOURCE_COLORS[(src || '').toLowerCase()] || { bg: 'rgba(107,114,128,0.1)', color: '#9ca3af', border: 'rgba(107,114,128,0.2)' };

const extractNewsTags = (title, source) => {
    const tags = [];
    const t = title.toLowerCase();
    if (t.includes('fed') || t.includes('federal')) tags.push('FED');
    if (t.includes('usd') || t.includes('dollar')) tags.push('USD');
    if (t.includes('gold') || t.includes('emas') || t.includes('xau')) tags.push('GOLD');
    if (t.includes('oil') || t.includes('minyak')) tags.push('OIL');
    if (t.includes('rate') || t.includes('suku bunga')) tags.push('RATE');
    if (t.includes('inflation') || t.includes('inflasi') || t.includes('cpi')) tags.push('CPI');
    if (t.includes('eur') || t.includes('ecb')) tags.push('EUR');
    if (t.includes('btc') || t.includes('bitcoin') || t.includes('crypto')) tags.push('CRYPTO');
    return tags.slice(0, 3);
};

// ── Skeleton Rows ──────────────────────────────────────────────────────────

function SkeletonCalRows({ count = 6 }) {
    return Array.from({ length: count }).map((_, i) => (
        <tr key={i} className="border-b border-[var(--border-color)] animate-pulse">
            {[60, 40, 50, 200, 60, 70, 70, 70, 80].map((w, j) => (
                <td key={j} className="px-3 py-3">
                    <div className="h-3 rounded bg-[var(--bg-panel)]" style={{ width: `${w}px`, maxWidth: '100%' }} />
                </td>
            ))}
        </tr>
    ));
}

function SkeletonNewsRows({ count = 6 }) {
    return Array.from({ length: count }).map((_, i) => (
        <tr key={i} className="border-b border-[var(--border-color)] animate-pulse">
            {[90, 80, 300, 100].map((w, j) => (
                <td key={j} className="px-3 py-3">
                    <div className="h-3 rounded bg-[var(--bg-panel)]" style={{ width: `${w}px`, maxWidth: '100%' }} />
                </td>
            ))}
        </tr>
    ));
}

// ── Calendar Event Row ────────────────────────────────────────────────────────

function EventRow({ event, index }) {
    const imp = getImpact(event.importance);
    const isHigh = event.importance?.toLowerCase() === 'high';
    const surprise = getSurprise(event.actual_value, event.forecast_value);
    const isPending = event.actual_value === null || event.actual_value === undefined;

    return (
        <tr className={`border-b border-[var(--border-color)] transition-colors
            ${index % 2 === 0 ? '' : 'bg-white/[0.01]'}
            hover:bg-[var(--bg-hover)]
            ${isHigh ? 'bg-red-500/[0.015]' : ''}
        `}>
            {/* WIB Time */}
            <td className="px-3 py-2.5 font-mono text-[11px] text-[var(--text-dim)] whitespace-nowrap">
                {formatTime(event.time_utc)}
            </td>

            {/* Flag */}
            <td className="px-2 py-2.5 text-center whitespace-nowrap">
                <span className="text-base leading-none">{getFlag(event.country)}</span>
            </td>

            {/* Currency */}
            <td className="px-2 py-2.5 whitespace-nowrap">
                <span className="text-[10px] font-bold font-mono text-[var(--text-secondary)]">{event.country}</span>
            </td>

            {/* Event */}
            <td className="px-3 py-2.5">
                <span className={`text-[11px] font-medium leading-tight ${isHigh ? 'text-[var(--text-primary)] font-semibold' : 'text-[var(--text-secondary)]'}`}>
                    {isHigh && <span className="mr-1 text-[10px]">⚠️</span>}
                    {event.title}
                </span>
            </td>

            {/* Impact */}
            <td className="px-3 py-2.5 text-center">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border"
                    style={{ color: imp.color, background: imp.bg, borderColor: imp.border }}>
                    {imp.label}
                </span>
            </td>

            {/* Forecast */}
            <td className="px-3 py-2.5 text-right font-mono text-[11px] text-[var(--accent)] hidden sm:table-cell">
                {event.forecast_value !== null && event.forecast_value !== undefined
                    ? `${event.forecast_value}${event.unit || ''}` : <span className="text-[var(--text-dim)]">—</span>}
            </td>

            {/* Previous */}
            <td className="px-3 py-2.5 text-right font-mono text-[11px] text-[var(--text-dim)] hidden sm:table-cell">
                {event.previous_value !== null && event.previous_value !== undefined
                    ? `${event.previous_value}${event.unit || ''}` : <span>—</span>}
            </td>

            {/* Actual */}
            <td className={`px-3 py-2.5 text-right font-mono text-[11px] font-bold ${
                surprise?.label === '✅ Better' ? 'text-green-400' :
                surprise?.label === '❌ Miss' ? 'text-red-400' :
                'text-[var(--text-primary)]'
            }`}>
                {isPending
                    ? <span className="text-[var(--text-dim)] text-[10px]">Pending</span>
                    : `${event.actual_value}${event.unit || ''}`
                }
            </td>

            {/* Surprise */}
            <td className="px-3 py-2.5 text-center">
                {surprise ? (
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${surprise.bg} ${surprise.color}`}>
                        {surprise.label}
                    </span>
                ) : (
                    <span className="text-[var(--text-dim)] text-[10px]">—</span>
                )}
            </td>
        </tr>
    );
}

// ── Calendar Tab ──────────────────────────────────────────────────────────────

const DATE_TABS = ['Yesterday', 'Today', 'Tomorrow', 'This Week', 'This Month'];
const DATE_LABELS = { Yesterday: '⏮ Kemarin', Today: '📅 Hari Ini', Tomorrow: '⏭ Besok', 'This Week': '🗓 Minggu Ini', 'This Month': '📆 Bulan Ini' };
const IMPACT_FILTERS = ['ALL', 'HIGH', 'MEDIUM', 'LOW'];
const CURRENCY_FILTERS = ['ALL', 'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD'];

function CalendarTab() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeDate, setActiveDate] = useState('This Week');
    const [impFilter, setImpFilter] = useState('ALL');
    const [currFilter, setCurrFilter] = useState('ALL');
    const [lastUpdated, setLastUpdated] = useState(null);

    const loadData = useCallback(async (tab) => {
        setLoading(true); setError('');
        try {
            const { from, to } = getDateRange(tab);
            const res = await fetchCalendar({ from_date: from, to_date: to, limit: 200 });
            setEvents(res.data || []);
            setLastUpdated(new Date());
        } catch (e) {
            setError('Failed to load calendar events.');
            setEvents([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { loadData(activeDate); }, [activeDate, loadData]);

    let filtered = events;
    if (impFilter !== 'ALL') filtered = filtered.filter(e => e.importance?.toLowerCase() === impFilter.toLowerCase());
    if (currFilter !== 'ALL') filtered = filtered.filter(e => e.country?.toUpperCase() === currFilter);

    const grouped = groupByDate(filtered);
    const highCount = events.filter(e => e.importance?.toLowerCase() === 'high').length;

    return (
        <div className="space-y-3">
            {/* Control bar */}
            <div className="flex flex-col sm:flex-row gap-2 flex-wrap">
                {/* Date tabs */}
                <div className="flex bg-[var(--bg-panel)] rounded-xl p-1 border border-[var(--border-color)] gap-0.5">
                    {DATE_TABS.map(t => (
                        <button key={t} onClick={() => setActiveDate(t)}
                            className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all font-mono ${
                                t === activeDate
                                    ? 'bg-[var(--accent)] text-black shadow'
                                    : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                            }`}>
                            {DATE_LABELS[t]}
                        </button>
                    ))}
                </div>

                {/* Impact filter */}
                <div className="flex bg-[var(--bg-panel)] rounded-xl p-1 border border-[var(--border-color)] gap-0.5">
                    {IMPACT_FILTERS.map(f => (
                        <button key={f} onClick={() => setImpFilter(f)}
                            className={`px-2.5 py-1.5 rounded-lg text-[9px] font-black transition-all ${
                                f === impFilter
                                    ? 'bg-[var(--bg-hover)] text-[var(--text-primary)]'
                                    : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                            }`}>
                            {f === 'HIGH' ? '🔴' : f === 'MEDIUM' ? '🟡' : f === 'LOW' ? '⚪' : '✦'} {f}
                        </button>
                    ))}
                </div>

                {/* Currency filter */}
                <div className="flex bg-[var(--bg-panel)] rounded-xl p-1 border border-[var(--border-color)] gap-0.5 overflow-x-auto scrollbar-none">
                    {CURRENCY_FILTERS.map(c => (
                        <button key={c} onClick={() => setCurrFilter(c)}
                            className={`px-2.5 py-1.5 rounded-lg text-[9px] font-black transition-all flex items-center gap-1 whitespace-nowrap ${
                                c === currFilter
                                    ? 'bg-[var(--accent)] text-black shadow'
                                    : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                            }`}>
                            {c !== 'ALL' && <span className="text-[10px]">{getFlag(c)}</span>}
                            {c}
                        </button>
                    ))}
                </div>

                <button onClick={() => loadData(activeDate)}
                    className="ml-auto flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[var(--border-color)] text-[10px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all">
                    <RefreshCw size={11} className={loading ? 'animate-spin' : ''} />
                    Refresh
                </button>
            </div>

            {/* Stats */}
            {!loading && events.length > 0 && (
                <div className="flex items-center gap-3 text-[9px] font-mono text-[var(--text-dim)]">
                    <span>{events.length} events</span>
                    {highCount > 0 && <span className="text-red-400 font-black">🔴 {highCount} High Impact</span>}
                    {lastUpdated && <span className="opacity-60">Updated: {lastUpdated.toLocaleTimeString('id-ID')}</span>}
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
                    <AlertTriangle size={14} className="text-red-400 shrink-0" />
                    <p className="text-[10px] text-red-400">{error}</p>
                    <button onClick={() => loadData(activeDate)} className="ml-auto text-[9px] px-2 py-1 rounded border border-red-500/30 text-red-400 hover:bg-red-500/10">Retry</button>
                </div>
            )}

            {/* Groups */}
            {!loading && grouped.length === 0 && !error && (
                <div className="rounded-xl border border-[var(--border-color)] p-16 text-center bg-[var(--bg-card)]">
                    <div className="text-4xl mb-3">📭</div>
                    <p className="text-sm font-bold text-[var(--text-dim)]">Tidak ada event untuk periode ini</p>
                </div>
            )}

            {grouped.map(([dateKey, dayEvents]) => {
                const { dayStr, label, emoji } = formatDateHeader(dayEvents[0].time_utc);
                const dayHigh = dayEvents.filter(e => e.importance?.toLowerCase() === 'high').length;
                const sortedDay = [...dayEvents].sort((a, b) => new Date(a.time_utc) - new Date(b.time_utc));

                return (
                    <div key={dateKey} className="rounded-xl border border-[var(--border-color)] overflow-hidden">
                        {/* Date header */}
                        <div className="px-4 py-2.5 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <span>{emoji}</span>
                                <span className="font-mono font-bold text-[var(--text-primary)] text-[12px]">{dayStr}</span>
                                {label && (
                                    <span className={`text-[9px] font-black px-2 py-0.5 rounded-full font-mono border ${
                                        label === 'HARI INI'
                                            ? 'bg-[var(--accent)]/20 text-[var(--accent)] border-[var(--accent)]/30'
                                            : 'bg-[var(--bg-hover)] text-[var(--text-dim)] border-[var(--border-color)]'
                                    }`}>{label}</span>
                                )}
                            </div>
                            <div className="flex items-center gap-2 text-[9px] font-mono text-[var(--text-dim)]">
                                {dayHigh > 0 && <span className="text-red-400 font-black">🔴 {dayHigh} High</span>}
                                <span>{dayEvents.length} events</span>
                            </div>
                        </div>

                        {/* Table */}
                        <div className="overflow-x-auto">
                            <table className="w-full text-[11px] border-collapse min-w-[700px]">
                                <thead>
                                    <tr className="bg-[var(--bg-panel)]/60 border-b border-[var(--border-color)] text-[var(--text-dim)]">
                                        <th className="px-3 py-2 text-left text-[9px] font-black uppercase tracking-widest w-16">Waktu WIB</th>
                                        <th className="px-2 py-2 text-center text-[9px] font-black uppercase tracking-widest w-8">Flag</th>
                                        <th className="px-2 py-2 text-left text-[9px] font-black uppercase tracking-widest w-14">Mata Uang</th>
                                        <th className="px-3 py-2 text-left text-[9px] font-black uppercase tracking-widest">Event</th>
                                        <th className="px-3 py-2 text-center text-[9px] font-black uppercase tracking-widest w-20">Impact</th>
                                        <th className="px-3 py-2 text-right text-[9px] font-black uppercase tracking-widest w-20 hidden sm:table-cell">Forecast</th>
                                        <th className="px-3 py-2 text-right text-[9px] font-black uppercase tracking-widest w-20 hidden sm:table-cell">Previous</th>
                                        <th className="px-3 py-2 text-right text-[9px] font-black uppercase tracking-widest w-20">Actual</th>
                                        <th className="px-3 py-2 text-center text-[9px] font-black uppercase tracking-widest w-24">Surprise</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading
                                        ? <SkeletonCalRows count={5} />
                                        : sortedDay.map((e, i) => <EventRow key={i} event={e} index={i} />)
                                    }
                                </tbody>
                            </table>
                        </div>
                    </div>
                );
            })}

            {/* Loading placeholder when no groups yet */}
            {loading && grouped.length === 0 && (
                <div className="rounded-xl border border-[var(--border-color)] overflow-hidden">
                    <div className="px-4 py-2.5 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center gap-2 animate-pulse">
                        <div className="h-3 w-32 rounded bg-[var(--bg-card)]" />
                        <div className="h-3 w-16 rounded bg-[var(--bg-card)] ml-2" />
                    </div>
                    <table className="w-full text-[11px] border-collapse min-w-[700px]">
                        <tbody><SkeletonCalRows count={6} /></tbody>
                    </table>
                </div>
            )}
        </div>
    );
}

// ── Breaking News Tab ─────────────────────────────────────────────────────────

function NewsRow({ news, index }) {
    const srcStyle = getSourceStyle(news.source);
    const fresh = isFresh(news.published_at);
    const tags = extractNewsTags(news.title || '', news.source);

    return (
        <tr
            onClick={() => news.url && window.open(news.url, '_blank', 'noopener')}
            className={`border-b border-[var(--border-color)] transition-colors cursor-pointer
                ${index % 2 === 0 ? '' : 'bg-white/[0.01]'}
                hover:bg-[var(--bg-hover)]
            `}
        >
            {/* Time */}
            <td className="px-3 py-2.5 whitespace-nowrap">
                <div className="flex items-center gap-1.5">
                    {fresh && (
                        <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse shrink-0" />
                    )}
                    <span className="text-[10px] font-mono text-[var(--text-dim)]">
                        {formatRelativeTime(news.published_at)}
                    </span>
                </div>
            </td>

            {/* Source */}
            <td className="px-3 py-2.5 whitespace-nowrap">
                <span className="text-[9px] font-bold px-2 py-0.5 rounded border"
                    style={{ color: srcStyle.color, background: srcStyle.bg, borderColor: srcStyle.border }}>
                    {news.source || 'Unknown'}
                </span>
            </td>

            {/* Headline */}
            <td className="px-3 py-2.5">
                <div className="flex items-start gap-1.5">
                    <span className="text-[11px] text-[var(--text-primary)] leading-relaxed font-medium">
                        {fresh && <span className="mr-1">🔥</span>}
                        {news.title}
                    </span>
                    {news.url && <ExternalLink size={10} className="text-[var(--text-dim)] shrink-0 mt-0.5" />}
                </div>
                {news.summary && (
                    <p className="text-[9px] text-[var(--text-dim)] mt-0.5 leading-relaxed line-clamp-1">{news.summary}</p>
                )}
            </td>

            {/* Tags */}
            <td className="px-3 py-2.5 whitespace-nowrap">
                <div className="flex gap-1 flex-wrap">
                    {tags.length > 0 ? tags.map(tag => (
                        <span key={tag} className="text-[8px] font-mono font-bold px-1.5 py-0.5 rounded border text-[var(--accent)]"
                            style={{ background: 'rgba(250,200,21,0.08)', borderColor: 'rgba(250,200,21,0.2)' }}>
                            {tag}
                        </span>
                    )) : <span className="text-[var(--text-dim)] text-[9px]">—</span>}
                </div>
            </td>
        </tr>
    );
}

function NewsTab() {
    const [news, setNews] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [lastRefresh, setLastRefresh] = useState(null);
    const intervalRef = useRef(null);

    const loadNews = useCallback(async () => {
        try {
            setError('');
            const res = await fetchNews();
            setNews(res.news || []);
            setLastRefresh(new Date());
        } catch (e) {
            setError('Failed to load news.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        loadNews();
        intervalRef.current = setInterval(loadNews, 60000);
        return () => clearInterval(intervalRef.current);
    }, [loadNews]);

    const freshCount = news.filter(n => isFresh(n.published_at)).length;

    return (
        <div className="space-y-3">
            {/* Header bar */}
            <div className="flex items-center justify-between flex-wrap gap-2">
                <div className="flex items-center gap-3 text-[9px] font-mono text-[var(--text-dim)]">
                    <span>{news.length} articles</span>
                    {freshCount > 0 && (
                        <span className="flex items-center gap-1 text-green-400 font-black">
                            <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                            {freshCount} fresh (&lt;10 min)
                        </span>
                    )}
                    {lastRefresh && <span className="opacity-60">Auto-refresh: 60s · {lastRefresh.toLocaleTimeString('id-ID')}</span>}
                </div>
                <button onClick={loadNews}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[var(--border-color)] text-[9px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all">
                    <RefreshCw size={10} className={loading ? 'animate-spin' : ''} />
                    Refresh Now
                </button>
            </div>

            {/* Error */}
            {error && (
                <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
                    <AlertTriangle size={14} className="text-red-400 shrink-0" />
                    <p className="text-[10px] text-red-400">{error}</p>
                    <button onClick={loadNews} className="ml-auto text-[9px] px-2 py-1 rounded border border-red-500/30 text-red-400 hover:bg-red-500/10">Retry</button>
                </div>
            )}

            {/* Table */}
            <div className="rounded-xl border border-[var(--border-color)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-[11px] border-collapse min-w-[600px]">
                        <thead>
                            <tr className="bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                                <th className="px-3 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] w-28">Waktu</th>
                                <th className="px-3 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] w-28">Sumber</th>
                                <th className="px-3 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Headline</th>
                                <th className="px-3 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] w-28">Tags</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading
                                ? <SkeletonNewsRows count={8} />
                                : news.length === 0
                                    ? (
                                        <tr>
                                            <td colSpan={4} className="py-16 text-center text-[var(--text-dim)]">
                                                <div className="text-4xl mb-3">📭</div>
                                                <p className="text-sm font-bold">No news available</p>
                                            </td>
                                        </tr>
                                    )
                                    : news.map((n, i) => <NewsRow key={i} news={n} index={i} />)
                            }
                        </tbody>
                    </table>
                </div>
            </div>

            <p className="text-[8px] text-[var(--text-dim)] font-mono opacity-60">
                Auto-refreshes every 60 seconds · Click any row to open source article · 🔥 = fresh news (&lt;10 min)
            </p>
        </div>
    );
}

// ── AI Analysis Tab ───────────────────────────────────────────────────────────

function CurrencyCard({ currency, score }) {
    const isStrong = score >= 65;
    const isWeak   = score <= 35;
    return (
        <div className="rounded-xl p-3 border text-center"
            style={isStrong
                ? { background: 'rgba(16,185,129,0.08)', borderColor: 'rgba(16,185,129,0.25)' }
                : isWeak
                ? { background: 'rgba(239,68,68,0.08)', borderColor: 'rgba(239,68,68,0.25)' }
                : { background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }
            }>
            <p className="text-[11px] font-black flex items-center justify-center gap-1">
                <span>{getFlag(currency)}</span> {currency}
            </p>
            <p className={`text-2xl font-black font-mono leading-none mt-1 ${isStrong ? 'text-green-400' : isWeak ? 'text-red-400' : 'text-[var(--text-secondary)]'}`}>
                {Math.round(score)}
            </p>
            <div className="w-full h-1.5 rounded-full mt-2 overflow-hidden" style={{ background: 'rgba(255,255,255,0.06)' }}>
                <div className="h-full rounded-full transition-all duration-700"
                    style={{ width: `${Math.round(score)}%`, background: isStrong ? '#10b981' : isWeak ? '#ef4444' : '#fac815' }} />
            </div>
            <p className={`text-[8px] font-bold mt-1.5 ${isStrong ? 'text-green-400' : isWeak ? 'text-red-400' : 'text-[var(--text-dim)]'}`}>
                {isStrong ? 'BULLISH' : isWeak ? 'BEARISH' : 'NEUTRAL'}
            </p>
        </div>
    );
}

function AIAnalysisTab() {
    const [aiData, setAiData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    const loadAI = useCallback(async () => {
        setLoading(true); setError('');
        try {
            const res = await fetchCalendarAnalysis();
            if (res?.status === 'ok' && res.data) setAiData(res.data);
            else setAiData(null);
        } catch {
            setError('Failed to load AI analysis.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { loadAI(); }, [loadAI]);

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20 gap-3">
                <Brain size={18} style={{ color: '#fac815' }} className="animate-pulse" />
                <p className="text-[11px] text-[var(--text-dim)] font-mono animate-pulse">Loading AI currency analysis...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 flex items-center gap-3">
                <AlertTriangle size={14} className="text-red-400 shrink-0" />
                <p className="text-[10px] text-red-400">{error}</p>
                <button onClick={loadAI} className="ml-auto text-[9px] px-2 py-1 rounded border border-red-500/30 text-red-400">Retry</button>
            </div>
        );
    }

    if (!aiData) {
        return (
            <div className="rounded-xl border border-[var(--border-color)] p-16 text-center bg-[var(--bg-card)]">
                <Brain size={28} className="mx-auto mb-3 opacity-30" style={{ color: '#fac815' }} />
                <p className="text-sm font-bold text-[var(--text-dim)]">No AI analysis data available</p>
                <p className="text-[9px] text-[var(--text-dim)] mt-1 opacity-60">Calendar analysis requires recent events to be ingested</p>
                <button onClick={loadAI} className="mt-4 text-[10px] px-4 py-2 rounded-lg border border-[var(--border-color)] text-[var(--text-dim)] hover:bg-[var(--bg-hover)] transition-all">
                    Retry
                </button>
            </div>
        );
    }

    const sentimentEntries = Object.entries(aiData.currency_sentiment || {}).sort(([,a],[,b]) => b - a);
    const priorityEvents = Array.isArray(aiData.priority_events) ? aiData.priority_events : [];

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="rounded-xl border p-4 flex items-center gap-3"
                style={{ background: 'rgba(250,200,21,0.04)', borderColor: 'rgba(250,200,21,0.2)' }}>
                <Brain size={18} style={{ color: '#fac815' }} />
                <div>
                    <p className="text-[11px] font-black text-[var(--text-primary)]">AI Calendar Analysis</p>
                    <p className="text-[9px] text-[var(--text-dim)] font-mono">
                        {aiData.market_regime && <span className="text-[var(--accent)] mr-2">Regime: {aiData.market_regime}</span>}
                        Based on upcoming economic events
                    </p>
                </div>
            </div>

            {/* Currency sentiment grid */}
            {sentimentEntries.length > 0 && (
                <div>
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">
                        Currency Sentiment Scores
                    </p>
                    <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-6 gap-2">
                        {sentimentEntries.map(([cur, score]) => (
                            <CurrencyCard key={cur} currency={cur} score={score} />
                        ))}
                    </div>
                </div>
            )}

            {/* Risk-ON / Risk-OFF */}
            {(aiData.risk_on_currencies?.length > 0 || aiData.risk_off_currencies?.length > 0) && (
                <div className="rounded-xl border border-[var(--border-color)] p-4 grid grid-cols-1 sm:grid-cols-2 gap-4">
                    {aiData.risk_on_currencies?.length > 0 && (
                        <div>
                            <p className="text-[9px] font-black uppercase tracking-widest text-green-400 mb-2">Risk-ON Currencies</p>
                            <div className="flex flex-wrap gap-1.5">
                                {aiData.risk_on_currencies.map(c => (
                                    <span key={c} className="text-[10px] font-mono font-bold px-2 py-1 rounded border text-green-400"
                                        style={{ background: 'rgba(16,185,129,0.1)', borderColor: 'rgba(16,185,129,0.25)' }}>
                                        {getFlag(c)} {c}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                    {aiData.risk_off_currencies?.length > 0 && (
                        <div>
                            <p className="text-[9px] font-black uppercase tracking-widest text-red-400 mb-2">Risk-OFF Currencies</p>
                            <div className="flex flex-wrap gap-1.5">
                                {aiData.risk_off_currencies.map(c => (
                                    <span key={c} className="text-[10px] font-mono font-bold px-2 py-1 rounded border text-red-400"
                                        style={{ background: 'rgba(239,68,68,0.1)', borderColor: 'rgba(239,68,68,0.25)' }}>
                                        {getFlag(c)} {c}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Priority events */}
            {priorityEvents.length > 0 && (
                <div>
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">
                        Priority Events This Week
                    </p>
                    <div className="rounded-xl border border-[var(--border-color)] overflow-hidden">
                        <table className="w-full text-[11px] border-collapse">
                            <thead>
                                <tr className="bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                                    {['Currency', 'Event', 'Impact', 'Expected Reaction'].map(h => (
                                        <th key={h} className="px-3 py-2 text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] text-left">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {priorityEvents.map((ev, i) => {
                                    const imp = getImpact(ev.importance || ev.impact);
                                    return (
                                        <tr key={i} className={`border-b border-[var(--border-color)] ${i % 2 === 0 ? '' : 'bg-white/[0.01]'}`}>
                                            <td className="px-3 py-2.5">
                                                <span className="flex items-center gap-1 text-[10px] font-bold">
                                                    {getFlag(ev.currency || ev.country)} {ev.currency || ev.country}
                                                </span>
                                            </td>
                                            <td className="px-3 py-2.5 text-[11px] text-[var(--text-secondary)]">{ev.event || ev.title}</td>
                                            <td className="px-3 py-2.5">
                                                <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold border"
                                                    style={{ color: imp.color, background: imp.bg, borderColor: imp.border }}>
                                                    {imp.label}
                                                </span>
                                            </td>
                                            <td className="px-3 py-2.5 text-[9px] text-[var(--text-dim)]">
                                                {ev.expected_reaction || ev.reaction || '—'}
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Refresh */}
            <div className="flex justify-end">
                <button onClick={loadAI}
                    className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl border border-[var(--border-color)] text-[9px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all">
                    <RefreshCw size={10} />
                    Refresh Analysis
                </button>
            </div>
        </div>
    );
}

// ── Main Component ────────────────────────────────────────────────────────────

const MAIN_TABS = [
    { id: 'calendar', label: '📊 Kalender' },
    { id: 'news',     label: '📰 Breaking News' },
    { id: 'ai',       label: '🤖 AI Analysis' },
];

export default function CalendarView() {
    const [activeTab, setActiveTab] = useState('calendar');

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-8 max-w-[1400px] mx-auto space-y-4">

            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-2">
                <div>
                    <h2 className="text-xl font-display font-black uppercase flex items-center gap-2">
                        📊 Economic Calendar
                    </h2>
                    <p className="text-[10px] text-[var(--text-dim)] font-mono mt-0.5">
                        WIB (GMT+7) · FXStreet via ecocal · Real-time market events
                    </p>
                </div>
            </div>

            {/* Main tabs */}
            <div className="flex gap-1 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1 w-fit">
                {MAIN_TABS.map(t => (
                    <button key={t.id} onClick={() => setActiveTab(t.id)}
                        className={`px-4 py-2 rounded-lg text-[10px] font-black transition-all ${
                            activeTab === t.id
                                ? 'bg-[var(--accent)] text-black shadow'
                                : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                        }`}>
                        {t.label}
                    </button>
                ))}
            </div>

            {/* Tab content */}
            {activeTab === 'calendar' && <CalendarTab />}
            {activeTab === 'news'     && <NewsTab />}
            {activeTab === 'ai'       && <AIAnalysisTab />}
        </div>
    );
}
