import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { BookOpen, Plus, TrendingUp, TrendingDown, Brain, RefreshCw, X, Trash2 } from 'lucide-react';
import { callAIFeature } from '../services/api';

const WEB_API = '/web/api/v1';
const getHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('gas-token') || ''}` });

const EMPTY_FORM = {
    pair: 'XAUUSD', direction: 'BUY',
    entry_price: '', exit_price: '', sl: '', tp: '', lot: '0.1',
    emotion: 'calm', notes: '', session: '', tags: [],
};

export default function JournalView() {
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const [aiReview, setAiReview] = useState(null);
    const [aiLoading, setAiLoading] = useState(false);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState(EMPTY_FORM);
    const [saving, setSaving] = useState(false);

    const fetchEntries = useCallback(async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${WEB_API}/journal/`, { headers: getHeaders() });
            setEntries(res.data?.entries || []);
        } catch {
            setEntries([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchEntries(); }, [fetchEntries]);

    const fetchAIReview = async () => {
        setAiLoading(true);
        setAiReview(null);
        try {
            const res = await callAIFeature('journal', {});
            const summary = res?.result?.summary || res?.analysis || res?.review || res?.insights || res?.message || JSON.stringify(res);
            setAiReview(summary);
        } catch (err) {
            setAiReview('⚠️ ' + (err?.response?.data?.detail || 'Gagal memuat AI review.'));
        } finally {
            setAiLoading(false);
        }
    };

    const addTrade = async () => {
        if (!form.entry_price) return;
        setSaving(true);
        try {
            const body = {
                ...form,
                entry_price: parseFloat(form.entry_price) || null,
                exit_price: parseFloat(form.exit_price) || null,
                sl: parseFloat(form.sl) || null,
                tp: parseFloat(form.tp) || null,
                lot: parseFloat(form.lot) || null,
            };
            await axios.post(`${WEB_API}/journal/`, body, { headers: getHeaders() });
            setForm(EMPTY_FORM);
            setShowForm(false);
            await fetchEntries();
        } catch (err) {
            alert('Gagal simpan: ' + (err?.response?.data?.detail || err.message));
        } finally {
            setSaving(false);
        }
    };

    const deleteTrade = async (id) => {
        if (!window.confirm('Hapus entri jurnal ini?')) return;
        try {
            await axios.delete(`${WEB_API}/journal/${id}`, { headers: getHeaders() });
            setEntries(prev => prev.filter(e => e.id !== id));
        } catch (err) {
            alert('Gagal hapus: ' + (err?.response?.data?.detail || err.message));
        }
    };

    // Compute stats from entries
    const entryPnls = entries.map(e => parseFloat(e.pnl) || 0);
    const totalPnl = entryPnls.reduce((s, v) => s + v, 0);
    const wins = entries.filter(e => (parseFloat(e.pnl) || 0) >= 0);
    const losses = entries.filter(e => (parseFloat(e.pnl) || 0) < 0);
    const winRate = entries.length ? ((wins.length / entries.length) * 100).toFixed(1) : 0;
    const avgWin = wins.length ? (wins.reduce((s, e) => s + (parseFloat(e.pnl) || 0), 0) / wins.length).toFixed(0) : 0;
    const avgLoss = losses.length ? (Math.abs(losses.reduce((s, e) => s + (parseFloat(e.pnl) || 0), 0)) / losses.length).toFixed(0) : 0;

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
                <div className="flex items-center gap-2">
                    <button
                        onClick={fetchAIReview}
                        disabled={aiLoading || entries.length === 0}
                        className="flex items-center gap-2 bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)] font-black px-3 py-2 rounded-lg text-xs hover:text-[var(--text-primary)] transition disabled:opacity-40">
                        {aiLoading ? <RefreshCw size={12} className="animate-spin" /> : <Brain size={12} />}
                        AI Review · 8cr
                    </button>
                    <button
                        onClick={fetchEntries}
                        className="p-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-lg hover:border-[var(--accent)] transition">
                        <RefreshCw size={12} className={`text-[var(--text-dim)] ${loading ? 'animate-spin' : ''}`} />
                    </button>
                    <button onClick={() => setShowForm(!showForm)}
                        className="flex items-center gap-2 bg-[var(--accent)] text-black font-black px-4 py-2 rounded-lg text-xs hover:opacity-90 transition-opacity">
                        <Plus size={14} /> Catat Trade
                    </button>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
                {[
                    { label: 'Total P&L', value: `${totalPnl >= 0 ? '+' : ''}$${totalPnl.toFixed(0)}`, color: totalPnl >= 0 ? 'var(--success)' : 'var(--danger)' },
                    { label: 'Win Rate', value: `${winRate}%`, color: 'var(--success)' },
                    { label: 'Total Trade', value: entries.length, color: 'var(--accent)' },
                    { label: 'Avg Win', value: `$${avgWin}`, color: 'var(--success)' },
                    { label: 'Avg Loss', value: `-$${avgLoss}`, color: 'var(--danger)' },
                ].map((s, i) => (
                    <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] text-center">
                        <p className="text-xl font-display font-black" style={{ color: s.color }}>{s.value}</p>
                        <p className="text-[8px] font-black uppercase text-[var(--text-dim)] mt-0.5">{s.label}</p>
                    </div>
                ))}
            </div>

            {/* AI Review Panel */}
            {(aiReview || aiLoading) && (
                <div className="rounded-xl p-4 border" style={{ background: 'rgba(250,200,21,0.03)', borderColor: 'rgba(250,200,21,0.15)' }}>
                    <div className="flex items-center gap-2 mb-2">
                        <Brain size={13} style={{ color: '#fac815' }} />
                        <p className="text-[9px] font-black uppercase tracking-widest" style={{ color: '#fac815' }}>AI Journal Review · DeepSeek</p>
                    </div>
                    {aiLoading
                        ? <p className="text-[9px] text-[var(--text-dim)] animate-pulse font-mono">AI sedang menganalisa jurnal trading Anda...</p>
                        : <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{aiReview}</p>
                    }
                </div>
            )}

            {/* Empty state */}
            {!loading && entries.length === 0 && (
                <div className="text-center py-12">
                    <BookOpen size={36} className="mx-auto mb-3 text-[var(--text-dim)] opacity-30" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Jurnal masih kosong</p>
                    <p className="text-[10px] text-[var(--text-dim)] mt-1">Klik "Catat Trade" untuk mulai mencatat riwayat trading Anda</p>
                </div>
            )}

            {loading && (
                <div className="flex items-center justify-center py-8 gap-2 text-[var(--text-dim)]">
                    <RefreshCw size={14} className="animate-spin" />
                    <span className="text-xs">Memuat jurnal...</span>
                </div>
            )}

            {/* Add Trade Form */}
            {showForm && (
                <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--accent)]/30 space-y-4">
                    <div className="flex items-center justify-between">
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)]">Catat Trade Baru</p>
                        <button onClick={() => setShowForm(false)}><X size={16} className="text-[var(--text-dim)]" /></button>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {[
                            { label: 'Pair', key: 'pair', type: 'select', opts: ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'XAGUSD', 'AUDUSD', 'GBPJPY', 'NAS100', 'US500', 'WTI', 'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT'] },
                            { label: 'Arah', key: 'direction', type: 'select', opts: ['BUY', 'SELL'] },
                            { label: 'Emosi', key: 'emotion', type: 'select', opts: ['calm', 'confident', 'nervous', 'fearful', 'greedy', 'fomo', 'revenge'] },
                            { label: 'Session', key: 'session', type: 'select', opts: ['', 'Asian', 'London', 'New York', 'Overlap'] },
                            { label: 'Lot Size', key: 'lot', type: 'number', placeholder: '0.1' },
                            { label: 'Entry', key: 'entry_price', type: 'number', placeholder: '3300.00' },
                            { label: 'Exit', key: 'exit_price', type: 'number', placeholder: '3320.00' },
                            { label: 'Stop Loss', key: 'sl', type: 'number', placeholder: '3280.00' },
                            { label: 'Take Profit', key: 'tp', type: 'number', placeholder: '3350.00' },
                        ].map(f => (
                            <div key={f.key}>
                                <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">{f.label}</label>
                                {f.type === 'select' ? (
                                    <select value={form[f.key]} onChange={e => setForm(p => ({ ...p, [f.key]: e.target.value }))}
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                                        {f.opts.map(o => <option key={o} value={o}>{o || '—'}</option>)}
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
                        <textarea value={form.notes} onChange={e => setForm(p => ({ ...p, notes: e.target.value }))} rows={2}
                            placeholder="Tuliskan analisa, alasan entry, dan pelajaran dari trade ini..."
                            className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)] resize-none" />
                    </div>
                    <div className="flex justify-end gap-2">
                        <button onClick={() => setShowForm(false)} className="text-xs font-bold text-[var(--text-dim)]">Batal</button>
                        <button onClick={addTrade} disabled={saving || !form.entry_price}
                            className="px-4 py-2 bg-[var(--accent)] text-black font-black rounded-lg text-xs hover:opacity-90 transition-opacity disabled:opacity-50">
                            {saving ? 'Menyimpan...' : 'Simpan Trade'}
                        </button>
                    </div>
                </div>
            )}

            {/* Trade List */}
            {entries.length > 0 && (
                <div className="space-y-3">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Riwayat Trade ({entries.length})</p>
                    {entries.map(e => {
                        const pnl = parseFloat(e.pnl) || 0;
                        const isWin = pnl >= 0;
                        const entryP = parseFloat(e.entry_price) || 0;
                        const exitP = parseFloat(e.exit_price) || 0;
                        return (
                            <div key={e.id} className={`p-4 rounded-xl border ${isWin ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : 'bg-[var(--bg-card)] border-[var(--danger)]/20'}`}>
                                <div className="flex items-start gap-4">
                                    <div className={`p-2.5 rounded-xl ${isWin ? 'bg-[var(--success)]/10' : 'bg-[var(--danger)]/10'}`}>
                                        {isWin ? <TrendingUp size={18} className="text-[var(--success)]" /> : <TrendingDown size={18} className="text-[var(--danger)]" />}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="flex flex-wrap items-center gap-2 mb-1">
                                            <span className="text-sm font-black text-[var(--text-primary)]">{e.pair}</span>
                                            <span className={`text-[8px] font-black px-2 py-0.5 rounded ${e.direction === 'BUY' ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>{e.direction}</span>
                                            {e.emotion && <span className="text-[8px] text-[var(--text-dim)] bg-[var(--bg-panel)] px-2 py-0.5 rounded">😌 {e.emotion}</span>}
                                            {e.session && <span className="text-[8px] text-[var(--text-dim)]">📍 {e.session}</span>}
                                            <span className="text-[8px] text-[var(--text-dim)] ml-auto">{e.created_at ? new Date(e.created_at).toLocaleDateString('id-ID') : ''}</span>
                                        </div>
                                        <div className="flex gap-4 text-[9px] text-[var(--text-dim)] mb-2">
                                            {entryP > 0 && <span>Entry: <strong className="text-[var(--text-secondary)]">{entryP}</strong></span>}
                                            {exitP > 0 && <span>Exit: <strong className="text-[var(--text-secondary)]">{exitP}</strong></span>}
                                            {e.sl && <span>SL: <strong className="text-[var(--text-secondary)]">{e.sl}</strong></span>}
                                            {e.lot && <span>Lot: <strong className="text-[var(--text-secondary)]">{e.lot}</strong></span>}
                                        </div>
                                        {e.notes && <p className="text-[9px] text-[var(--text-dim)] italic">"{e.notes}"</p>}
                                        {e.source === 'mt5-ea' && (
                                            <span className="text-[8px] bg-blue-500/10 text-blue-400 px-2 py-0.5 rounded mt-1 inline-block">🤖 MT5 Auto-log #{e.ticket}</span>
                                        )}
                                    </div>
                                    <div className="flex flex-col items-end gap-2 shrink-0">
                                        <div className="text-right">
                                            {pnl !== 0 && (
                                                <p className={`text-lg font-display font-black ${isWin ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                    {isWin ? '+' : ''}${Math.abs(pnl).toFixed(0)}
                                                </p>
                                            )}
                                        </div>
                                        <button onClick={() => deleteTrade(e.id)}
                                            className="p-1.5 rounded-lg text-[var(--text-dim)] hover:text-[var(--danger)] hover:bg-[var(--danger)]/10 transition">
                                            <Trash2 size={12} />
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
}
