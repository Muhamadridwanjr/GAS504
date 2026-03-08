import React, { useState } from 'react';
import { Bell, Plus, Trash2, ToggleLeft, ToggleRight, TrendingUp, TrendingDown } from 'lucide-react';
import { PAIRS } from '../constants';

const INITIAL_ALERTS = [
    { id: 1, pair: 'XAUUSD', condition: 'Harga ≥', price: '3350.00', channel: 'Push + Telegram', active: true, triggered: false },
    { id: 2, pair: 'BTCUSD', condition: 'Harga ≤', price: '60000.00', channel: 'Push', active: true, triggered: false },
    { id: 3, pair: 'EURUSD', condition: 'Harga ≥', price: '1.1200', channel: 'Push + Email', active: false, triggered: true },
];

const CONDITIONS = ['Harga ≥', 'Harga ≤', 'Crossing Up', 'Crossing Down', 'RSI ≥ 70', 'RSI ≤ 30'];
const CHANNELS = ['Push', 'Push + Telegram', 'Push + Email', 'Semua'];

export default function AlertsView() {
    const [alerts, setAlerts] = useState(INITIAL_ALERTS);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ pair: 'XAUUSD', condition: 'Harga ≥', price: '', channel: 'Push + Telegram' });

    const addAlert = () => {
        if (!form.price) return;
        setAlerts(prev => [...prev, { id: Date.now(), ...form, active: true, triggered: false }]);
        setForm({ pair: 'XAUUSD', condition: 'Harga ≥', price: '', channel: 'Push + Telegram' });
        setShowForm(false);
    };

    const toggle = (id) => setAlerts(prev => prev.map(a => a.id === id ? { ...a, active: !a.active } : a));
    const remove = (id) => setAlerts(prev => prev.filter(a => a.id !== id));

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Bell size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Peringatan Harga</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Custom Alert Harga, RSI, & Kondisi Market</p>
                    </div>
                </div>
                <button onClick={() => setShowForm(!showForm)}
                    className="flex items-center gap-2 bg-[var(--accent)] text-black font-black px-4 py-2 rounded-lg text-xs hover:opacity-90 transition-opacity">
                    <Plus size={14} />
                    Alert Baru
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-3">
                {[
                    { label: 'Total Alert', value: alerts.length, color: 'var(--accent)' },
                    { label: 'Aktif', value: alerts.filter(a => a.active).length, color: 'var(--success)' },
                    { label: 'Triggered', value: alerts.filter(a => a.triggered).length, color: 'var(--text-dim)' },
                ].map((s, i) => (
                    <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] text-center">
                        <p className="text-2xl font-display font-black" style={{ color: s.color }}>{s.value}</p>
                        <p className="text-[8px] font-black uppercase text-[var(--text-dim)]">{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Form */}
            {showForm && (
                <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--accent)]/30 space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)]">Buat Alert Baru</p>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <div>
                            <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">Pair</label>
                            <select value={form.pair} onChange={e => setForm(f => ({ ...f, pair: e.target.value }))}
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                                {PAIRS.map(p => <option key={p.symbol} value={p.symbol}>{p.symbol}</option>)}
                            </select>
                        </div>
                        <div>
                            <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">Kondisi</label>
                            <select value={form.condition} onChange={e => setForm(f => ({ ...f, condition: e.target.value }))}
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                                {CONDITIONS.map(c => <option key={c}>{c}</option>)}
                            </select>
                        </div>
                        <div>
                            <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">Harga / Nilai</label>
                            <input value={form.price} onChange={e => setForm(f => ({ ...f, price: e.target.value }))}
                                placeholder="3350.00"
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
                        </div>
                        <div>
                            <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">Channel</label>
                            <select value={form.channel} onChange={e => setForm(f => ({ ...f, channel: e.target.value }))}
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                                {CHANNELS.map(c => <option key={c}>{c}</option>)}
                            </select>
                        </div>
                    </div>
                    <div className="flex gap-2 justify-end">
                        <button onClick={() => setShowForm(false)} className="px-4 py-2 text-xs font-bold text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">Batal</button>
                        <button onClick={addAlert} className="px-4 py-2 bg-[var(--accent)] text-black font-black rounded-lg text-xs hover:opacity-90 transition-opacity">Simpan Alert</button>
                    </div>
                </div>
            )}

            {/* Alert List */}
            <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Daftar Alert</p>
                {alerts.length === 0 && (
                    <div className="text-center py-16">
                        <Bell size={32} className="text-[var(--text-dim)] mx-auto mb-3" />
                        <p className="text-sm font-bold text-[var(--text-dim)]">Belum ada alert. Buat alert baru di atas.</p>
                    </div>
                )}
                {alerts.map(a => (
                    <div key={a.id} className={`p-4 rounded-xl border flex items-center gap-4 transition-all ${a.active ? 'bg-[var(--bg-card)] border-[var(--border-color)]' : 'bg-[var(--bg-card)] border-[var(--border-color)] opacity-50'}`}>
                        <div className={`p-2.5 rounded-lg ${a.active ? 'bg-[var(--accent)]/10' : 'bg-[var(--bg-hover)]'}`}>
                            <Bell size={16} className={a.active ? 'text-[var(--accent)]' : 'text-[var(--text-dim)]'} />
                        </div>
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-0.5">
                                <span className="text-xs font-black text-[var(--text-primary)]">{a.pair}</span>
                                <span className="text-[9px] text-[var(--text-dim)] font-bold">{a.condition} {a.price}</span>
                                {a.triggered && <span className="text-[8px] bg-[var(--text-dim)]/10 text-[var(--text-dim)] font-black px-2 py-0.5 rounded">Triggered</span>}
                            </div>
                            <p className="text-[9px] text-[var(--text-dim)]">{a.channel}</p>
                        </div>
                        <button onClick={() => toggle(a.id)} className="text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors">
                            {a.active ? <ToggleRight size={22} className="text-[var(--success)]" /> : <ToggleLeft size={22} />}
                        </button>
                        <button onClick={() => remove(a.id)} className="text-[var(--text-dim)] hover:text-[var(--danger)] transition-colors">
                            <Trash2 size={16} />
                        </button>
                    </div>
                ))}
            </div>
        </div>
    );
}
