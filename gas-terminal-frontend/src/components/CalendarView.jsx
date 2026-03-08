import React, { useEffect, useState, useCallback } from 'react';
import { fetchCalendar } from '../services/api';

// ── Helpers ─────────────────────────────────────────────────────────────────

const pad = (n) => String(n).padStart(2, '0');

const toISOLocal = (date) =>
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T00:00:00`;

const toISOLocalEnd = (date) =>
    `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T23:59:59`;

const addDays = (date, n) => {
    const d = new Date(date);
    d.setDate(d.getDate() + n);
    return d;
};

const getDateRange = (tab) => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    switch (tab) {
        case 'Yesterday':
            return { from: toISOLocal(addDays(today, -1)), to: toISOLocalEnd(addDays(today, -1)) };
        case 'Today':
            return { from: toISOLocal(today), to: toISOLocalEnd(today) };
        case 'Tomorrow':
            return { from: toISOLocal(addDays(today, 1)), to: toISOLocalEnd(addDays(today, 1)) };
        case 'This Week':
            return { from: toISOLocal(addDays(today, -1)), to: toISOLocalEnd(addDays(today, 6)) };
        default:
            return { from: toISOLocal(today), to: toISOLocalEnd(today) };
    }
};

const FLAGS = {
    USA: '🇺🇸', USD: '🇺🇸', EUR: '🇪🇺', JPY: '🇯🇵', GBP: '🇬🇧',
    AUD: '🇦🇺', CAD: '🇨🇦', CHF: '🇨🇭', NZD: '🇳🇿', CNY: '🇨🇳',
    CNH: '🇨🇳', KRW: '🇰🇷', SGD: '🇸🇬', HKD: '🇭🇰', MXN: '🇲🇽',
    ZAR: '🇿🇦', BRL: '🇧🇷', INR: '🇮🇳', SEK: '🇸🇪', NOK: '🇳🇴',
    DKK: '🇩🇰', PLN: '🇵🇱', TRY: '🇹🇷', RUB: '🇷🇺',
};

const getFlag = (country) => FLAGS[country?.toUpperCase()] || '🌐';

const IMPACT_CFG = {
    high:   { label: 'HIGH',   icon: '🔴', bar: 'bg-red-500',    text: 'text-red-400',    badge: 'bg-red-500/15 text-red-400 border border-red-500/30' },
    medium: { label: 'MED',    icon: '🟡', bar: 'bg-yellow-400', text: 'text-yellow-400', badge: 'bg-yellow-400/15 text-yellow-400 border border-yellow-400/30' },
    low:    { label: 'LOW',    icon: '⚪', bar: 'bg-gray-500',   text: 'text-gray-400',   badge: 'bg-gray-500/10 text-gray-400 border border-gray-500/20' },
};

const getImpact = (imp) => IMPACT_CFG[imp?.toLowerCase()] || IMPACT_CFG.low;

const formatTime = (utcStr) => {
    try {
        const d = new Date(utcStr);
        // Convert UTC → WIB (GMT+7)
        const wib = new Date(d.getTime() + 7 * 3600 * 1000);
        return `${pad(wib.getUTCHours())}:${pad(wib.getUTCMinutes())}`;
    } catch { return '--:--'; }
};

const formatDateHeader = (utcStr) => {
    try {
        const d = new Date(utcStr);
        const wib = new Date(d.getTime() + 7 * 3600 * 1000);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        const todayWib = new Date(today.getTime() + 7 * 3600 * 1000);
        const eventDay = new Date(wib.getUTCFullYear(), wib.getUTCMonth(), wib.getUTCDate());
        const todayDay = new Date(todayWib.getUTCFullYear(), todayWib.getUTCMonth(), todayWib.getUTCDate());
        const diff = Math.round((eventDay - todayDay) / 86400000);

        const dayNames = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
        const monthNames = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];
        const dayStr = `${dayNames[wib.getUTCDay()]}, ${wib.getUTCDate()} ${monthNames[wib.getUTCMonth()]} ${wib.getUTCFullYear()}`;

        let label = '';
        let emoji = '';
        if (diff === -1) { label = 'KEMARIN'; emoji = '⏮️'; }
        else if (diff === 0) { label = 'HARI INI'; emoji = '📅'; }
        else if (diff === 1) { label = 'BESOK'; emoji = '⏭️'; }
        else if (diff > 1)  { label = `+${diff} HARI`; emoji = '📆'; }

        return { dayStr, label, emoji };
    } catch { return { dayStr: utcStr, label: '', emoji: '📅' }; }
};

const groupByDate = (events) => {
    const groups = {};
    events.forEach(e => {
        const d = new Date(e.time_utc);
        const wib = new Date(d.getTime() + 7 * 3600 * 1000);
        const key = `${wib.getUTCFullYear()}-${pad(wib.getUTCMonth() + 1)}-${pad(wib.getUTCDate())}`;
        if (!groups[key]) groups[key] = [];
        groups[key].push(e);
    });
    return Object.entries(groups).sort(([a], [b]) => a.localeCompare(b));
};

const fmtVal = (val, unit) => {
    if (val === null || val === undefined) return <span className="text-[var(--text-dim)]">—</span>;
    return `${val}${unit || ''}`;
};

// ── Tabs ────────────────────────────────────────────────────────────────────

const TABS = ['Yesterday', 'Today', 'Tomorrow', 'This Week'];
const TAB_LABELS = { Yesterday: '⏮ Kemarin', Today: '📅 Hari Ini', Tomorrow: '⏭ Besok', 'This Week': '🗓 Minggu Ini' };
const TAB_FILTERS = ['ALL', 'HIGH', 'MEDIUM', 'LOW'];

// ── Component ────────────────────────────────────────────────────────────────

export default function CalendarView() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('Today');
    const [impFilter, setImpFilter] = useState('ALL');
    const [lastUpdated, setLastUpdated] = useState(null);

    const loadData = useCallback(async (tab) => {
        setLoading(true);
        setEvents([]);
        try {
            const { from, to } = getDateRange(tab);
            const res = await fetchCalendar({ from_date: from, to_date: to, limit: 200 });
            setEvents(res.data || []);
            setLastUpdated(new Date());
        } catch (err) {
            console.error('Calendar fetch failed:', err);
            setEvents([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { loadData(activeTab); }, [activeTab, loadData]);

    const filtered = impFilter === 'ALL'
        ? events
        : events.filter(e => e.importance?.toLowerCase() === impFilter.toLowerCase());

    const grouped = groupByDate(filtered);

    const highCount = events.filter(e => e.importance?.toLowerCase() === 'high').length;
    const medCount  = events.filter(e => e.importance?.toLowerCase() === 'medium').length;

    return (
        <div className="p-4 md:p-6 space-y-4 pb-24 md:pb-6 max-w-6xl mx-auto text-[var(--text-primary)]">

            {/* ── Header ── */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                <div>
                    <h2 className="text-2xl font-display font-black uppercase tracking-tighter flex items-center gap-2">
                        📊 Economic Calendar
                    </h2>
                    <p className="text-[10px] text-[var(--text-dim)] font-mono mt-0.5">
                        Waktu ditampilkan dalam WIB (GMT+7) · {events.length} event
                        {highCount > 0 && <span className="text-red-400 ml-2">🔴 {highCount} High Impact</span>}
                        {medCount > 0  && <span className="text-yellow-400 ml-1">🟡 {medCount} Medium</span>}
                    </p>
                </div>
                <button
                    onClick={() => loadData(activeTab)}
                    className="text-[10px] font-mono px-3 py-1.5 rounded-lg border border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition flex items-center gap-1.5"
                >
                    🔄 Refresh
                </button>
            </div>

            {/* ── Tab Navigation ── */}
            <div className="flex flex-col sm:flex-row gap-2">
                <div className="flex bg-[var(--bg-panel)] rounded-xl p-1 border border-[var(--border-color)] text-[11px] font-bold gap-1 flex-wrap">
                    {TABS.map(t => (
                        <button
                            key={t}
                            onClick={() => setActiveTab(t)}
                            className={`px-3 py-2 rounded-lg transition-all font-mono ${
                                t === activeTab
                                    ? 'bg-[var(--accent)] text-white shadow-lg shadow-[var(--accent)]/20'
                                    : 'hover:bg-[var(--bg-hover)] text-[var(--text-dim)]'
                            }`}
                        >
                            {TAB_LABELS[t]}
                        </button>
                    ))}
                </div>

                {/* Impact Filter */}
                <div className="flex bg-[var(--bg-panel)] rounded-xl p-1 border border-[var(--border-color)] text-[10px] font-bold gap-1">
                    {TAB_FILTERS.map(f => (
                        <button
                            key={f}
                            onClick={() => setImpFilter(f)}
                            className={`px-3 py-2 rounded-lg transition-all font-mono ${
                                f === impFilter
                                    ? 'bg-[var(--bg-hover)] text-[var(--text-primary)]'
                                    : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'
                            }`}
                        >
                            {f === 'HIGH' ? '🔴' : f === 'MEDIUM' ? '🟡' : f === 'LOW' ? '⚪' : '✦'} {f}
                        </button>
                    ))}
                </div>
            </div>

            {/* ── Content ── */}
            <div className="space-y-4">
                {loading ? (
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-20 text-center">
                        <div className="flex flex-col items-center gap-4">
                            <div className="w-12 h-12 border-4 border-t-[var(--accent)] border-[var(--border-color)] rounded-full animate-spin"></div>
                            <p className="font-mono text-sm text-[var(--text-dim)] animate-pulse">
                                📡 Sinkronisasi data ekonomi global...
                            </p>
                        </div>
                    </div>
                ) : grouped.length === 0 ? (
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-16 text-center">
                        <div className="text-5xl mb-4">📭</div>
                        <p className="text-[var(--text-dim)] font-mono text-sm">Tidak ada event untuk periode ini.</p>
                        <p className="text-[10px] text-[var(--text-dim)] mt-2">
                            Coba trigger ingest: <code className="bg-[var(--bg-hover)] px-1 rounded">POST /ingest/run</code>
                        </p>
                    </div>
                ) : (
                    grouped.map(([dateKey, dayEvents]) => {
                        const { dayStr, label, emoji } = formatDateHeader(dayEvents[0].time_utc);
                        const dayHigh = dayEvents.filter(e => e.importance?.toLowerCase() === 'high').length;
                        return (
                            <div key={dateKey} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-lg">
                                {/* Date Header */}
                                <div className="px-4 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center justify-between">
                                    <div className="flex items-center gap-2">
                                        <span className="text-lg">{emoji}</span>
                                        <div>
                                            <span className="font-mono font-bold text-[var(--text-primary)] text-sm">{dayStr}</span>
                                            {label && (
                                                <span className={`ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full font-mono ${
                                                    label === 'HARI INI'
                                                        ? 'bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/30'
                                                        : 'bg-[var(--bg-hover)] text-[var(--text-dim)] border border-[var(--border-color)]'
                                                }`}>
                                                    {label}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2 text-[10px] font-mono text-[var(--text-dim)]">
                                        {dayHigh > 0 && <span className="text-red-400">🔴 {dayHigh} High</span>}
                                        <span>{dayEvents.length} events</span>
                                    </div>
                                </div>

                                {/* Table */}
                                <div className="overflow-x-auto">
                                    <table className="w-full text-[11px] border-collapse min-w-[700px]">
                                        <thead>
                                            <tr className="text-[var(--text-dim)] border-b border-[var(--border-color)] font-mono text-[10px]">
                                                <th className="px-4 py-2.5 text-left w-16">⏱ WIB</th>
                                                <th className="px-4 py-2.5 text-left w-20">🌍 Mata Uang</th>
                                                <th className="px-4 py-2.5 text-left">📋 Event</th>
                                                <th className="px-4 py-2.5 text-center w-20">⚡ Impact</th>
                                                <th className="px-4 py-2.5 text-right w-20">✅ Aktual</th>
                                                <th className="px-4 py-2.5 text-right w-20">🎯 Forecast</th>
                                                <th className="px-4 py-2.5 text-right w-20">📌 Previous</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {dayEvents
                                                .slice()
                                                .sort((a, b) => new Date(a.time_utc) - new Date(b.time_utc))
                                                .map((e, i) => {
                                                    const imp = getImpact(e.importance);
                                                    const isHigh = e.importance?.toLowerCase() === 'high';
                                                    const actualBetter = e.actual_value !== null && e.forecast_value !== null && e.actual_value > e.forecast_value;
                                                    const actualWorse  = e.actual_value !== null && e.forecast_value !== null && e.actual_value < e.forecast_value;
                                                    return (
                                                        <tr
                                                            key={i}
                                                            className={`border-b border-[var(--border-color)] transition-all hover:bg-[var(--bg-hover)] ${
                                                                isHigh ? 'bg-red-500/3' : ''
                                                            }`}
                                                        >
                                                            <td className="px-4 py-3 font-mono text-[var(--text-dim)] whitespace-nowrap">
                                                                {formatTime(e.time_utc)}
                                                            </td>
                                                            <td className="px-4 py-3 whitespace-nowrap">
                                                                <div className="flex items-center gap-1.5">
                                                                    <span className="text-base">{getFlag(e.country)}</span>
                                                                    <span className="font-bold font-mono text-[10px]">{e.country}</span>
                                                                </div>
                                                            </td>
                                                            <td className="px-4 py-3">
                                                                <span className={`font-medium ${isHigh ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>
                                                                    {isHigh && <span className="mr-1">⚠️</span>}
                                                                    {e.title}
                                                                </span>
                                                            </td>
                                                            <td className="px-4 py-3 text-center">
                                                                <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[9px] font-bold font-mono ${imp.badge}`}>
                                                                    {imp.icon} {imp.label}
                                                                </span>
                                                            </td>
                                                            <td className={`px-4 py-3 text-right font-bold font-mono ${
                                                                actualBetter ? 'text-green-400' :
                                                                actualWorse  ? 'text-red-400' :
                                                                'text-[var(--text-primary)]'
                                                            }`}>
                                                                {e.actual_value !== null && e.actual_value !== undefined ? (
                                                                    <span className="flex items-center justify-end gap-1">
                                                                        {actualBetter && '▲'}
                                                                        {actualWorse  && '▼'}
                                                                        {e.actual_value}{e.unit || ''}
                                                                    </span>
                                                                ) : <span className="text-[var(--text-dim)]">—</span>}
                                                            </td>
                                                            <td className="px-4 py-3 text-right font-mono text-[var(--text-dim)]">
                                                                {e.forecast_value !== null && e.forecast_value !== undefined
                                                                    ? `${e.forecast_value}${e.unit || ''}`
                                                                    : <span>—</span>}
                                                            </td>
                                                            <td className="px-4 py-3 text-right font-mono text-[var(--text-dim)]">
                                                                {e.previous_value !== null && e.previous_value !== undefined
                                                                    ? `${e.previous_value}${e.unit || ''}`
                                                                    : <span>—</span>}
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        );
                    })
                )}
            </div>

            {/* ── Footer ── */}
            <div className="text-[9px] text-[var(--text-dim)] flex items-center justify-between font-mono pt-1">
                <div className="flex items-center gap-3">
                    <span>📡 Sumber: FXStreet via ecocal</span>
                    {lastUpdated && (
                        <span>🕐 Update: {lastUpdated.toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })}</span>
                    )}
                    {events.length === 0 && !loading && (
                        <span className="text-[var(--danger)] animate-pulse">⚠️ Data sedang sinkronisasi dari provider global...</span>
                    )}
                </div>
                <span>🕐 Sekarang: {new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit', second: '2-digit' })} WIB</span>
            </div>
        </div>
    );
}
