import React, { useState, useMemo } from 'react';
import { Filter, TrendingUp, TrendingDown, Search } from 'lucide-react';
import { PAIRS } from '../constants';

const SIGNALS = ['BUY', 'SELL', 'NEUTRAL'];
const GRADES = ['A+', 'A', 'B+', 'B'];
const TYPES = ['Semua', 'Forex', 'Crypto', 'Commodity', 'Index'];

const SCREENER_DATA = PAIRS.map(p => ({
    ...p,
    signal: SIGNALS[Math.floor(Math.random() * SIGNALS.length)],
    grade: GRADES[Math.floor(Math.random() * GRADES.length)],
    confidence: Math.floor(Math.random() * 30) + 65,
    rsi: Math.floor(Math.random() * 40) + 35,
    trend: Math.random() > 0.5 ? 'BULLISH' : 'BEARISH',
    volume: ['Low', 'Medium', 'High', 'Very High'][Math.floor(Math.random() * 4)],
    change24h: +(Math.random() * 4 - 2).toFixed(2),
}));

export default function ScreenerView() {
    const [filterType, setFilterType] = useState('Semua');
    const [filterSignal, setFilterSignal] = useState('Semua');
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState('confidence');
    const [data] = useState(SCREENER_DATA);

    const filtered = useMemo(() => {
        let d = [...data];
        if (filterType !== 'Semua') d = d.filter(p => p.type === filterType);
        if (filterSignal !== 'Semua') d = d.filter(p => p.signal === filterSignal);
        if (search) d = d.filter(p => p.symbol.includes(search.toUpperCase()) || p.name.toLowerCase().includes(search.toLowerCase()));
        d.sort((a, b) => b[sortBy] - a[sortBy] || 0);
        return d;
    }, [data, filterType, filterSignal, search, sortBy]);

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Filter size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Screener Aset</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Filter & Scan Peluang Trading Terbaik</p>
                </div>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap gap-3 items-center">
                <div className="flex items-center gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 w-48">
                    <Search size={12} className="text-[var(--text-dim)]" />
                    <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Cari pair..."
                        className="bg-transparent text-xs font-bold text-[var(--text-primary)] outline-none w-full placeholder:text-[var(--text-dim)]" />
                </div>
                <div className="flex gap-1">
                    {TYPES.map(t => (
                        <button key={t} onClick={() => setFilterType(t)}
                            className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${filterType === t ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                            {t}
                        </button>
                    ))}
                </div>
                <div className="flex gap-1">
                    {['Semua', ...SIGNALS].map(s => (
                        <button key={s} onClick={() => setFilterSignal(s)}
                            className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${filterSignal === s ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                            {s}
                        </button>
                    ))}
                </div>
                <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                    className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none ml-auto">
                    <option value="confidence">Sort: Confidence</option>
                    <option value="rsi">Sort: RSI</option>
                    <option value="change24h">Sort: Change 24h</option>
                </select>
            </div>

            {/* Stats Bar */}
            <div className="grid grid-cols-3 sm:grid-cols-3 gap-3">
                {[
                    { label: 'BUY Setup', count: filtered.filter(d => d.signal === 'BUY').length, color: 'var(--success)' },
                    { label: 'SELL Setup', count: filtered.filter(d => d.signal === 'SELL').length, color: 'var(--danger)' },
                    { label: 'NEUTRAL', count: filtered.filter(d => d.signal === 'NEUTRAL').length, color: 'var(--text-dim)' },
                ].map((s, i) => (
                    <div key={i} className="p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${s.color}15` }}>
                            {s.label === 'BUY Setup' ? <TrendingUp size={14} style={{ color: s.color }} /> : <TrendingDown size={14} style={{ color: s.color }} />}
                        </div>
                        <div>
                            <p className="text-lg font-display font-black" style={{ color: s.color }}>{s.count}</p>
                            <p className="text-[8px] text-[var(--text-dim)] font-bold uppercase">{s.label}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Table */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                                {['Pair', 'Tipe', 'Sinyal', 'Grade', 'Confidence', 'RSI', 'Trend', 'Volume', 'Change 24h'].map(h => (
                                    <th key={h} className="px-4 py-3 text-left text-[9px] font-black uppercase tracking-wider text-[var(--text-dim)]">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {filtered.map((row, i) => (
                                <tr key={row.symbol} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors cursor-pointer">
                                    <td className="px-4 py-3">
                                        <div>
                                            <p className="font-black text-[var(--text-primary)]">{row.symbol}</p>
                                            <p className="text-[9px] text-[var(--text-dim)]">{row.name}</p>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="text-[9px] bg-[var(--bg-hover)] px-2 py-0.5 rounded font-bold text-[var(--text-dim)]">{row.type}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`text-[9px] font-black px-2 py-0.5 rounded ${row.signal === 'BUY' ? 'bg-[var(--success)]/10 text-[var(--success)]' : row.signal === 'SELL' ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>
                                            {row.signal}
                                        </span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="font-black text-[var(--accent)]">{row.grade}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-2">
                                            <div className="w-16 h-1.5 bg-[var(--bg-hover)] rounded-full">
                                                <div className="h-1.5 rounded-full bg-[var(--accent)]" style={{ width: `${row.confidence}%` }} />
                                            </div>
                                            <span className="font-bold text-[var(--text-secondary)]">{row.confidence}%</span>
                                        </div>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`font-bold ${row.rsi > 70 ? 'text-[var(--danger)]' : row.rsi < 30 ? 'text-[var(--success)]' : 'text-[var(--text-secondary)]'}`}>{row.rsi}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`text-[9px] font-black ${row.trend === 'BULLISH' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{row.trend}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className="text-[9px] text-[var(--text-dim)] font-bold">{row.volume}</span>
                                    </td>
                                    <td className="px-4 py-3">
                                        <span className={`font-bold ${row.change24h >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                            {row.change24h >= 0 ? '+' : ''}{row.change24h}%
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
