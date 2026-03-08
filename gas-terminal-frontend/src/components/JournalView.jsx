import React, { useState } from 'react';
import { BookOpen, Plus, TrendingUp, TrendingDown, BarChart2, Award, X } from 'lucide-react';

const INITIAL_TRADES = [
    { id: 1, pair: 'XAUUSD', type: 'BUY', entry: 3285.00, exit: 3318.50, sl: 3270.00, lot: 0.1, result: 'WIN', pnl: 335, date: '2025-03-07', notes: 'SMC Order Block + FVG confluence H4. Perfect entry.' },
    { id: 2, pair: 'EURUSD', type: 'SELL', entry: 1.1080, exit: 1.1045, sl: 1.1100, lot: 0.5, result: 'WIN', pnl: 175, date: '2025-03-06', notes: 'Bearish OB pada H1, konfluensi dengan resistance D1.' },
    { id: 3, pair: 'BTCUSD', type: 'BUY', entry: 67200, exit: 66800, sl: 66500, lot: 0.01, result: 'LOSS', pnl: -40, date: '2025-03-05', notes: 'Premature entry, seharusnya tunggu retest.' },
    { id: 4, pair: 'XAUUSD', type: 'BUY', entry: 3260.00, exit: 3285.00, sl: 3248.00, lot: 0.2, result: 'WIN', pnl: 500, date: '2025-03-04', notes: 'Bullish OB D1 tervalidasi, target BSL tercapai.' },
    { id: 5, pair: 'GBPUSD', type: 'SELL', entry: 1.2940, exit: 1.2985, sl: 1.2960, lot: 0.3, result: 'LOSS', pnl: -135, date: '2025-03-03', notes: 'Stop hit oleh news. Hindari trade saat high impact news.' },
];

const EMPTY_FORM = { pair: 'XAUUSD', type: 'BUY', entry: '', exit: '', sl: '', lot: '0.1', date: '', notes: '' };

export default function JournalView() {
    const [trades, setTrades] = useState(INITIAL_TRADES);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState(EMPTY_FORM);

    const totalPnl = trades.reduce((s, t) => s + t.pnl, 0);
    const wins = trades.filter(t => t.result === 'WIN');
    const losses = trades.filter(t => t.result === 'LOSS');
    const winRate = trades.length ? ((wins.length / trades.length) * 100).toFixed(1) : 0;
    const avgWin = wins.length ? (wins.reduce((s, t) => s + t.pnl, 0) / wins.length).toFixed(0) : 0;
    const avgLoss = losses.length ? (Math.abs(losses.reduce((s, t) => s + t.pnl, 0)) / losses.length).toFixed(0) : 0;

    const addTrade = () => {
        if (!form.entry || !form.exit) return;
        const pnl = (parseFloat(form.exit) - parseFloat(form.entry)) * (form.type === 'BUY' ? 1 : -1) * parseFloat(form.lot) * 100;
        setTrades(prev => [{
            id: Date.now(), ...form,
            entry: parseFloat(form.entry), exit: parseFloat(form.exit), sl: parseFloat(form.sl), lot: parseFloat(form.lot),
            pnl: Math.round(pnl), result: pnl >= 0 ? 'WIN' : 'LOSS'
        }, ...prev]);
        setForm(EMPTY_FORM);
        setShowForm(false);
    };

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <BookOpen size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Jurnal Trading</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Rekap, Analisa & Evaluasi Performa Trading</p>
                    </div>
                </div>
                <button onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 bg-[var(--accent)] text-black font-black px-4 py-2 rounded-lg text-xs hover:opacity-90 transition-opacity">
                    <Plus size={14} /> Catat Trade
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {[
                    { label: 'Total P&L', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl}`, color: totalPnl >= 0 ? 'var(--success)' : 'var(--danger)' },
                    { label: 'Win Rate', value: `${winRate}%`, color: 'var(--success)' },
                    { label: 'Total Trade', value: trades.length, color: 'var(--accent)' },
                    { label: 'Avg Win', value: `$${avgWin}`, color: 'var(--success)' },
                    { label: 'Avg Loss', value: `-$${avgLoss}`, color: 'var(--danger)' },
                ].map((s, i) => (
                    <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] text-center">
                        <p className="text-xl font-display font-black" style={{ color: s.color }}>{s.value}</p>
                        <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mt-0.5">{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Add Trade Form */}
            {showForm && (
                <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--accent)]/30 space-y-4">
                    <div className="flex items-center justify-between">
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)]">Catat Trade Baru</p>
                        <button onClick={() => setShowForm(false)}><X size={16} className="text-[var(--text-dim)]" /></button>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {[
                            { label: 'Pair', key: 'pair', type: 'select', opts: ['XAUUSD', 'BTCUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'ETHUSD', 'XAGUSD'] },
                            { label: 'Arah', key: 'type', type: 'select', opts: ['BUY', 'SELL'] },
                            { label: 'Tanggal', key: 'date', type: 'date' },
                            { label: 'Lot Size', key: 'lot', type: 'number', placeholder: '0.1' },
                            { label: 'Entry', key: 'entry', type: 'number', placeholder: '3300.00' },
                            { label: 'Exit', key: 'exit', type: 'number', placeholder: '3320.00' },
                            { label: 'Stop Loss', key: 'sl', type: 'number', placeholder: '3280.00' },
                        ].map(f => (
                            <div key={f.key}>
                                <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">{f.label}</label>
                                {f.type === 'select' ? (
                                    <select value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                                        {f.opts.map(o => <option key={o}>{o}</option>)}
                                    </select>
                                ) : (
                                    <input type={f.type} value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                                        placeholder={f.placeholder}
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
                                )}
                            </div>
                        ))}
                    </div>
                    <div>
                        <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">Catatan / Alasan Entry</label>
                        <textarea value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} rows={2} placeholder="Tuliskan analisa, alasan entry, dan pelajaran dari trade ini..."
                            className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)] resize-none" />
                    </div>
                    <div className="flex justify-end gap-2">
                        <button onClick={() => setShowForm(false)} className="text-xs font-bold text-[var(--text-dim)]">Batal</button>
                        <button onClick={addTrade} className="px-4 py-2 bg-[var(--accent)] text-black font-black rounded-lg text-xs hover:opacity-90 transition-opacity">Simpan Trade</button>
                    </div>
                </div>
            )}

            {/* Trade List */}
            <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Riwayat Trade</p>
                {trades.map(t => (
                    <div key={t.id} className={`p-4 rounded-xl border ${t.result === 'WIN' ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : 'bg-[var(--bg-card)] border-[var(--danger)]/20'}`}>
                        <div className="flex items-start gap-4">
                            <div className={`p-2.5 rounded-xl ${t.result === 'WIN' ? 'bg-[var(--success)]/10' : 'bg-[var(--danger)]/10'}`}>
                                {t.result === 'WIN' ? <TrendingUp size={18} className="text-[var(--success)]" /> : <TrendingDown size={18} className="text-[var(--danger)]" />}
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex flex-wrap items-center gap-2 mb-1">
                                    <span className="text-sm font-black text-[var(--text-primary)]">{t.pair}</span>
                                    <span className={`text-[8px] font-black px-2 py-0.5 rounded ${t.type === 'BUY' ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>{t.type}</span>
                                    <span className="text-[8px] text-[var(--text-dim)]">{t.date}</span>
                                    <span className="text-[8px] text-[var(--text-dim)]">Lot: {t.lot}</span>
                                </div>
                                <div className="flex gap-4 text-[9px] text-[var(--text-dim)] mb-2">
                                    <span>Entry: <strong className="text-[var(--text-secondary)]">{t.entry}</strong></span>
                                    <span>Exit: <strong className="text-[var(--text-secondary)]">{t.exit}</strong></span>
                                    <span>SL: <strong className="text-[var(--text-secondary)]">{t.sl}</strong></span>
                                </div>
                                {t.notes && <p className="text-[9px] text-[var(--text-dim)] italic">"{t.notes}"</p>}
                            </div>
                            <div className="text-right shrink-0">
                                <p className={`text-lg font-display font-black ${t.pnl >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                    {t.pnl >= 0 ? '+' : ''}${Math.abs(t.pnl)}
                                </p>
                                <span className={`text-[8px] font-black px-2 py-0.5 rounded ${t.result === 'WIN' ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>{t.result}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
