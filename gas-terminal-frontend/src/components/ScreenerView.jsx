import React, { useState, useMemo } from 'react';
import { Filter, TrendingUp, TrendingDown, Search, ScanLine, RefreshCw } from 'lucide-react';
import { PAIRS } from '../constants';
import { callAIFeature } from '../services/api';
import StyleSelector, { STYLE_MATRIX } from './StyleSelector';

const TYPES = ['Semua', 'Forex', 'Crypto', 'Commodity', 'Index'];

export default function ScreenerView() {
    const [filterType, setFilterType] = useState('Semua');
    const [filterSignal, setFilterSignal] = useState('Semua');
    const [search, setSearch] = useState('');
    const [sortBy, setSortBy] = useState('confidence');
    const [style, setStyle] = useState('intraday');
    const [minConfluence, setMinConfluence] = useState(60);
    const [data, setData] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [scanned, setScanned] = useState(false);

    // Resolve primary TF from style
    const styleTFs = STYLE_MATRIX[style]?.tfs || ['D1','H4','H1','M15'];
    const primaryTF = styleTFs[2] || 'H1';

    const runScan = async () => {
        setLoading(true);
        setError(null);
        try {
            const targetPairs = filterType === 'Semua'
                ? PAIRS.map(p => p.symbol)
                : PAIRS.filter(p => p.type === filterType).map(p => p.symbol);
            const res = await callAIFeature('scanner', {
                pairs: targetPairs,
                style,
                timeframe: primaryTF,
                min_confluence: minConfluence,
            });
            // Normalize response — scanner may return { results: [...] } or { opportunities: [...] } or array
            let rows = res?.results || res?.opportunities || res?.signals || res?.data || [];
            if (!Array.isArray(rows)) rows = [];
            // Merge with PAIRS metadata for display
            const enriched = rows.map(r => {
                const meta = PAIRS.find(p => p.symbol === (r.pair || r.symbol)) || {};
                return {
                    symbol: r.pair || r.symbol || meta.symbol || '',
                    name:   meta.name || r.name || '',
                    type:   meta.type || r.type || 'Other',
                    signal: r.signal || r.action || r.recommendation || 'NEUTRAL',
                    grade:  r.grade || r.rating || (r.confidence >= 80 ? 'A+' : r.confidence >= 70 ? 'A' : r.confidence >= 60 ? 'B+' : 'B'),
                    confidence: r.confidence || r.score || r.confluence || 0,
                    rsi:    r.rsi || r.rsi_value || 50,
                    trend:  r.trend || r.market_trend || (r.signal?.includes('BUY') ? 'BULLISH' : r.signal?.includes('SELL') ? 'BEARISH' : 'NEUTRAL'),
                    volume: r.volume || r.volume_label || '—',
                    change24h: r.change_24h ?? r.change24h ?? r.pct_change ?? 0,
                    entry:  r.entry || null,
                    sl:     r.sl || r.stop_loss || null,
                    tp:     r.tp1 || r.take_profit || null,
                };
            });
            setData(enriched);
            setScanned(true);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Scanner gagal. Pastikan EA MT5 aktif.');
        } finally {
            setLoading(false);
        }
    };

    const filtered = useMemo(() => {
        let d = [...data];
        if (filterType !== 'Semua') d = d.filter(p => p.type === filterType);
        if (filterSignal !== 'Semua') d = d.filter(p => p.signal === filterSignal || p.signal?.includes(filterSignal));
        if (search) d = d.filter(p => p.symbol?.includes(search.toUpperCase()) || p.name?.toLowerCase().includes(search.toLowerCase()));
        d.sort((a, b) => (b[sortBy] || 0) - (a[sortBy] || 0));
        return d;
    }, [data, filterType, filterSignal, search, sortBy]);

    const buyCount  = filtered.filter(d => d.signal?.includes('BUY')).length;
    const sellCount = filtered.filter(d => d.signal?.includes('SELL')).length;
    const neutCount = filtered.filter(d => !d.signal?.includes('BUY') && !d.signal?.includes('SELL')).length;

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Filter size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Screener Aset</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">AI Multi-Pair Scanner · Data Real dari MT5 · 15 Kredit</p>
                </div>
            </div>

            {/* Scan Config */}
            <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] space-y-4">
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Konfigurasi Scan</p>
                {/* Style Selector */}
                <StyleSelector value={style} onChange={s => { setStyle(s); setScanned(false); }} showMatrix={true} />

                <div className="flex flex-wrap gap-3 items-end border-t border-[var(--border-color)] pt-3">
                    {/* Min Confluence */}
                    <div>
                        <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mb-1.5">Min Confluence: {minConfluence}%</p>
                        <input type="range" min={40} max={90} value={minConfluence} onChange={e => setMinConfluence(+e.target.value)}
                            className="w-32 accent-[var(--accent)]" />
                    </div>
                    {/* Market type filter */}
                    <div>
                        <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mb-1.5">Market</p>
                        <div className="flex gap-1">
                            {TYPES.map(t => (
                                <button key={t} onClick={() => setFilterType(t)}
                                    className={`px-3 py-1.5 rounded-lg text-[9px] font-black transition-all ${filterType === t ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                    {/* Run Button */}
                    <button
                        onClick={runScan}
                        disabled={loading}
                        className="ml-auto flex items-center gap-2 px-5 py-2.5 rounded-xl font-black text-sm transition-all hover:scale-[1.02] disabled:opacity-50"
                        style={{ background: loading ? 'var(--bg-panel)' : 'var(--grad-gold)', color: loading ? 'var(--text-dim)' : '#000', border: loading ? '1px solid var(--border-color)' : 'none' }}>
                        {loading
                            ? <><RefreshCw size={14} className="animate-spin" /> Scanning AI...</>
                            : <><ScanLine size={14} /> Scan {filterType === 'Semua' ? 'Semua Pair' : filterType} · {style} · 15 Kredit</>
                        }
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="rounded-xl p-4 border" style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.25)' }}>
                    <p className="text-xs font-black text-red-400">⚠️ {error}</p>
                    <p className="text-[9px] text-red-400/70 mt-1">Pastikan EA MT5 aktif dan gas-strategy-core running.</p>
                </div>
            )}

            {/* Results */}
            {scanned && !loading && data.length > 0 && (
                <>
                    {/* Search + signal filter */}
                    <div className="flex flex-wrap gap-3 items-center">
                        <div className="flex items-center gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 w-48">
                            <Search size={12} className="text-[var(--text-dim)]" />
                            <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Cari pair..."
                                className="bg-transparent text-xs font-bold text-[var(--text-primary)] outline-none w-full placeholder:text-[var(--text-dim)]" />
                        </div>
                        <div className="flex gap-1">
                            {['Semua', 'BUY', 'SELL', 'NEUTRAL'].map(s => (
                                <button key={s} onClick={() => setFilterSignal(s)}
                                    className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${filterSignal === s ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                                    {s}
                                </button>
                            ))}
                        </div>
                        <select value={sortBy} onChange={e => setSortBy(e.target.value)}
                            className="ml-auto bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                            <option value="confidence">Sort: Confidence</option>
                            <option value="rsi">Sort: RSI</option>
                            <option value="change24h">Sort: Change 24h</option>
                        </select>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-3 gap-3">
                        {[
                            { label: 'BUY Setup', count: buyCount, color: 'var(--success)', Icon: TrendingUp },
                            { label: 'SELL Setup', count: sellCount, color: 'var(--danger)', Icon: TrendingDown },
                            { label: 'NEUTRAL', count: neutCount, color: 'var(--text-dim)', Icon: Filter },
                        ].map(({ label, count, color, Icon }) => (
                            <div key={label} className="p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center gap-3">
                                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ backgroundColor: `${color}15` }}>
                                    <Icon size={14} style={{ color }} />
                                </div>
                                <div>
                                    <p className="text-lg font-display font-black" style={{ color }}>{count}</p>
                                    <p className="text-[8px] text-[var(--text-dim)] font-bold uppercase">{label}</p>
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
                                        {['Pair', 'Tipe', 'Sinyal', 'Grade', 'Confidence', 'RSI', 'Trend', 'Volume', 'Change 24h', 'Entry / SL / TP'].map(h => (
                                            <th key={h} className="px-4 py-3 text-left text-[9px] font-black uppercase tracking-wider text-[var(--text-dim)]">{h}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {filtered.map((row, i) => (
                                        <tr key={i} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors cursor-pointer">
                                            <td className="px-4 py-3">
                                                <p className="font-black text-[var(--text-primary)]">{row.symbol}</p>
                                                <p className="text-[9px] text-[var(--text-dim)]">{row.name}</p>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="text-[9px] bg-[var(--bg-hover)] px-2 py-0.5 rounded font-bold text-[var(--text-dim)]">{row.type}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`text-[9px] font-black px-2 py-0.5 rounded ${row.signal?.includes('BUY') ? 'bg-[var(--success)]/10 text-[var(--success)]' : row.signal?.includes('SELL') ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>
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
                                                <span className={`text-[9px] font-black ${row.trend === 'BULLISH' ? 'text-[var(--success)]' : row.trend === 'BEARISH' ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'}`}>{row.trend}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="text-[9px] text-[var(--text-dim)] font-bold">{row.volume}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`font-bold ${row.change24h >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                    {row.change24h >= 0 ? '+' : ''}{Number(row.change24h).toFixed(2)}%
                                                </span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="text-[8px] font-mono text-[var(--text-dim)] space-y-0.5">
                                                    {row.entry && <p>E: <span className="text-[var(--text-primary)]">{row.entry}</span></p>}
                                                    {row.sl && <p>SL: <span className="text-red-400">{row.sl}</span></p>}
                                                    {row.tp && <p>TP: <span className="text-green-400">{row.tp}</span></p>}
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}

            {/* Empty / initial state */}
            {!scanned && !loading && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <ScanLine size={48} className="text-[var(--text-dim)] mb-4 opacity-30" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Konfigurasi filter lalu klik "Scan Pair"</p>
                    <p className="text-[10px] text-[var(--text-dim)] mt-1">AI akan men-scan semua pair yang dipilih secara real-time dari MT5 · 15 Kredit</p>
                </div>
            )}

            {scanned && !loading && data.length === 0 && (
                <div className="flex flex-col items-center justify-center py-16 text-center">
                    <Filter size={32} className="text-[var(--text-dim)] mb-3 opacity-30" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Tidak ada pair yang memenuhi min confluence {minConfluence}%</p>
                    <p className="text-[10px] text-[var(--text-dim)] mt-1">Coba turunkan min confluence atau ganti timeframe</p>
                </div>
            )}
        </div>
    );
}
