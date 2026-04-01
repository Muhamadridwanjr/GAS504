import React, { useState, useEffect, useCallback } from 'react';
import { Bell, Plus, Trash2, ToggleLeft, ToggleRight, CheckCircle2, Clock, AlertTriangle } from 'lucide-react';
import { PAIRS } from '../constants';

const CONDITIONS = ['Harga ≥', 'Harga ≤', 'Crossing Up', 'Crossing Down', 'RSI ≥ 70', 'RSI ≤ 30'];
const CHANNELS = ['Push', 'Push + Telegram', 'Push + Email', 'Semua'];

const STORAGE_KEY = 'gas-price-alerts';

function loadAlerts() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function saveAlerts(alerts) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(alerts));
}

export default function AlertsView({ prices = {} }) {
    const [alerts, setAlerts] = useState(loadAlerts);
    const [showForm, setShowForm] = useState(false);
    const [form, setForm] = useState({ pair: 'XAUUSD', condition: 'Harga ≥', price: '', channel: 'Push + Telegram' });
    const [triggered, setTriggered] = useState([]);

    // Persist to localStorage whenever alerts change
    useEffect(() => {
        saveAlerts(alerts);
    }, [alerts]);

    // Check price alerts against live prices
    useEffect(() => {
        if (!prices || Object.keys(prices).length === 0) return;
        const newlyTriggered = [];

        setAlerts(prev => prev.map(alert => {
            if (!alert.active || alert.triggered) return alert;
            const livePrice = prices[alert.pair];
            if (!livePrice) return alert;

            const targetPrice = parseFloat(alert.price);
            let hit = false;
            if (alert.condition === 'Harga ≥' && livePrice >= targetPrice) hit = true;
            if (alert.condition === 'Harga ≤' && livePrice <= targetPrice) hit = true;

            if (hit) {
                newlyTriggered.push(alert);
                return { ...alert, triggered: true, triggered_at: new Date().toLocaleTimeString('id-ID'), triggered_price: livePrice };
            }
            return alert;
        }));

        if (newlyTriggered.length > 0) {
            setTriggered(prev => [...newlyTriggered, ...prev].slice(0, 10));
        }
    }, [prices]);

    const addAlert = () => {
        if (!form.price) return;
        const newAlert = {
            id: Date.now(),
            ...form,
            active: true,
            triggered: false,
            triggered_at: null,
            triggered_price: null,
            created_at: new Date().toLocaleDateString('id-ID'),
        };
        setAlerts(prev => [newAlert, ...prev]);
        setForm({ pair: 'XAUUSD', condition: 'Harga ≥', price: '', channel: 'Push + Telegram' });
        setShowForm(false);
    };

    const toggle = (id) => setAlerts(prev => prev.map(a => a.id === id ? { ...a, active: !a.active, triggered: false } : a));
    const remove = (id) => setAlerts(prev => prev.filter(a => a.id !== id));
    const resetAlert = (id) => setAlerts(prev => prev.map(a => a.id === id ? { ...a, triggered: false, triggered_at: null } : a));

    const activeCount = alerts.filter(a => a.active && !a.triggered).length;
    const triggeredCount = alerts.filter(a => a.triggered).length;

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Bell size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Smart Alert</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">
                            Monitor harga real-time · {activeCount} aktif
                        </p>
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
                    { label: 'Monitoring', value: activeCount, color: 'var(--success, #22c55e)' },
                    { label: 'Triggered', value: triggeredCount, color: triggeredCount > 0 ? '#f59e0b' : 'var(--text-dim)' },
                ].map((s, i) => (
                    <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] text-center">
                        <p className="text-2xl font-display font-black" style={{ color: s.color }}>{s.value}</p>
                        <p className="text-[8px] font-black uppercase text-[var(--text-dim)]">{s.label}</p>
                    </div>
                ))}
            </div>

            {/* Live price reference */}
            {Object.keys(prices).length > 0 && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4">
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">Harga Live (dari EA MT5)</p>
                    <div className="flex flex-wrap gap-3">
                        {Object.entries(prices).slice(0, 8).map(([sym, price]) => (
                            <div key={sym} className="flex items-center gap-1.5">
                                <span className="text-[9px] font-black text-[var(--text-dim)]">{sym}</span>
                                <span className="text-[10px] font-black text-[var(--accent)] font-mono">{typeof price === 'number' ? price.toFixed(sym.includes('JPY') ? 3 : 5) : price}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

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
                            <label className="text-[8px] font-black uppercase text-[var(--text-dim)] block mb-1">
                                Harga Target {form.pair in prices && <span className="text-[var(--accent)]">(live: {Number(prices[form.pair]).toFixed(2)})</span>}
                            </label>
                            <input value={form.price} onChange={e => setForm(f => ({ ...f, price: e.target.value }))}
                                placeholder="e.g. 3350.00"
                                type="number" step="0.01"
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
                        <button onClick={addAlert} disabled={!form.price}
                            className="px-4 py-2 bg-[var(--accent)] text-black font-black rounded-lg text-xs hover:opacity-90 disabled:opacity-40 transition-opacity">
                            Simpan Alert
                        </button>
                    </div>
                </div>
            )}

            {/* Alert List */}
            <div className="space-y-3">
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Daftar Alert</p>

                {alerts.length === 0 && (
                    <div className="text-center py-16 border border-dashed border-[var(--border-color)] rounded-xl">
                        <Bell size={32} className="text-[var(--text-dim)] mx-auto mb-3 opacity-40" />
                        <p className="text-sm font-bold text-[var(--text-dim)]">Belum ada alert</p>
                        <p className="text-[10px] text-[var(--text-dim)] mt-1">Klik tombol <strong>Alert Baru</strong> di atas untuk membuat alert harga</p>
                        <p className="text-[9px] text-[var(--text-dim)] mt-1 opacity-60">Alert tersimpan otomatis di browser</p>
                    </div>
                )}

                {alerts.map(a => {
                    const livePrice = prices[a.pair];
                    const target = parseFloat(a.price);
                    const diff = livePrice ? Math.abs(livePrice - target) : null;
                    const diffPct = livePrice ? ((Math.abs(livePrice - target) / target) * 100).toFixed(2) : null;
                    const isClose = diff !== null && diffPct < 0.5;

                    return (
                        <div key={a.id} className={`p-4 rounded-xl border flex items-center gap-4 transition-all ${
                            a.triggered ? 'bg-yellow-500/5 border-yellow-500/40'
                            : isClose && a.active ? 'bg-orange-500/5 border-orange-500/30'
                            : a.active ? 'bg-[var(--bg-card)] border-[var(--border-color)]'
                            : 'bg-[var(--bg-card)] border-[var(--border-color)] opacity-50'
                        }`}>
                            <div className={`p-2.5 rounded-lg ${a.triggered ? 'bg-yellow-500/20' : a.active ? 'bg-[var(--accent)]/10' : 'bg-[var(--bg-hover)]'}`}>
                                {a.triggered
                                    ? <CheckCircle2 size={16} className="text-yellow-400" />
                                    : isClose && a.active
                                        ? <AlertTriangle size={16} className="text-orange-400" />
                                        : <Bell size={16} className={a.active ? 'text-[var(--accent)]' : 'text-[var(--text-dim)]'} />
                                }
                            </div>
                            <div className="flex-1 min-w-0">
                                <div className="flex items-center gap-2 flex-wrap mb-0.5">
                                    <span className="text-xs font-black text-[var(--text-primary)]">{a.pair}</span>
                                    <span className="text-[9px] text-[var(--text-dim)] font-bold">{a.condition} {a.price}</span>
                                    {a.triggered && (
                                        <span className="text-[8px] bg-yellow-500/20 text-yellow-400 font-black px-2 py-0.5 rounded border border-yellow-500/30">
                                            Triggered {a.triggered_at} @ {a.triggered_price}
                                        </span>
                                    )}
                                    {isClose && a.active && !a.triggered && (
                                        <span className="text-[8px] bg-orange-500/20 text-orange-400 font-black px-2 py-0.5 rounded border border-orange-500/30">
                                            Dekat! {diffPct}%
                                        </span>
                                    )}
                                </div>
                                <div className="flex items-center gap-2">
                                    <p className="text-[9px] text-[var(--text-dim)]">{a.channel}</p>
                                    {livePrice && (
                                        <p className="text-[9px] text-[var(--text-dim)]">
                                            · Live: <span className="text-[var(--accent)] font-black">{typeof livePrice === 'number' ? livePrice.toFixed(a.pair.includes('JPY') ? 3 : 5) : livePrice}</span>
                                        </p>
                                    )}
                                </div>
                            </div>
                            <div className="flex items-center gap-2 shrink-0">
                                {a.triggered && (
                                    <button onClick={() => resetAlert(a.id)}
                                        className="text-[8px] font-black text-yellow-400 border border-yellow-400/30 px-2 py-1 rounded hover:bg-yellow-400/10 transition-colors">
                                        Reset
                                    </button>
                                )}
                                <button onClick={() => toggle(a.id)} className="text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors">
                                    {a.active ? <ToggleRight size={22} className="text-[var(--success, #22c55e)]" /> : <ToggleLeft size={22} />}
                                </button>
                                <button onClick={() => remove(a.id)} className="text-[var(--text-dim)] hover:text-red-400 transition-colors">
                                    <Trash2 size={16} />
                                </button>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Help note */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4">
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Cara Kerja Alert</p>
                <ul className="space-y-1">
                    {[
                        'Alert tersimpan di browser (tidak hilang saat refresh)',
                        'Harga live dari EA MT5 via WebSocket — pastikan EA berjalan',
                        'Alert Triggered otomatis saat kondisi terpenuhi',
                        'Notifikasi Telegram — setup di halaman Telegram Bot',
                    ].map((t, i) => (
                        <li key={i} className="text-[9px] text-[var(--text-dim)] flex items-start gap-2">
                            <span className="text-[var(--accent)] mt-0.5">·</span> {t}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}
