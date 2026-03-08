import React, { useState, useMemo } from 'react';
import { ShieldCheck, AlertTriangle, TrendingUp, TrendingDown, Calculator } from 'lucide-react';
import { PAIRS } from '../constants';

const RISK_RULES = [
    { label: 'Risiko Per Trade', value: '1-2%', status: 'ok', detail: 'Jangan risiko lebih dari 2% modal per posisi' },
    { label: 'Max Drawdown Harian', value: '5%', status: 'ok', detail: 'Hentikan trading jika drawdown harian mencapai 5%' },
    { label: 'Rasio Risk:Reward', value: '≥ 1:2', status: 'ok', detail: 'Minimal target 2x dari risiko yang diambil' },
    { label: 'Max Posisi Terbuka', value: '3 Lot', status: 'warning', detail: 'Jangan buka lebih dari 3 posisi secara bersamaan' },
    { label: 'Korelasi Aset', value: 'Cek', status: 'warning', detail: 'Hindari posisi pada aset yang berkorelasi tinggi' },
];

export default function RiskManagerView() {
    const [balance, setBalance] = useState('10000');
    const [riskPct, setRiskPct] = useState('1');
    const [entry, setEntry] = useState('');
    const [sl, setSl] = useState('');
    const [pair, setPair] = useState('XAUUSD');
    const [direction, setDirection] = useState('BUY');

    const selectedPair = PAIRS.find(p => p.symbol === pair) || PAIRS[0];

    const calc = useMemo(() => {
        const bal = parseFloat(balance) || 0;
        const riskAmt = bal * (parseFloat(riskPct) / 100);
        const entryV = parseFloat(entry);
        const slV = parseFloat(sl);

        if (!entryV || !slV || entryV === slV) return null;

        const slPips = Math.abs(entryV - slV);
        const pipValue = selectedPair.type === 'Forex' ? 10 : 1;
        const lotSize = riskAmt / (slPips * pipValue * (selectedPair.type === 'Forex' ? 10000 : 1));
        const tp1 = direction === 'BUY' ? entryV + slPips * 2 : entryV - slPips * 2;
        const tp2 = direction === 'BUY' ? entryV + slPips * 3 : entryV - slPips * 3;

        return {
            riskAmt: riskAmt.toFixed(2),
            slPips: slPips.toFixed(selectedPair.type === 'Forex' ? 4 : 2),
            lotSize: Math.max(0.01, lotSize).toFixed(2),
            tp1: tp1.toFixed(selectedPair.type === 'Forex' ? 4 : 2),
            tp2: tp2.toFixed(selectedPair.type === 'Forex' ? 4 : 2),
            rewardTP1: (riskAmt * 2).toFixed(2),
            rewardTP2: (riskAmt * 3).toFixed(2),
        };
    }, [balance, riskPct, entry, sl, pair, direction]);

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <ShieldCheck size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Manajemen Risiko</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Kalkulator Posisi & Aturan Risiko Pro</p>
                </div>
                <span className="text-[8px] bg-[var(--accent)] text-black font-black px-2 py-0.5 rounded uppercase ml-2">Pro</span>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Calculator */}
                <div className="space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Kalkulator Ukuran Posisi</p>
                    <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1">Modal Akun (USD)</label>
                                <input type="number" value={balance} onChange={e => setBalance(e.target.value)}
                                    className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]"
                                    placeholder="10000" />
                            </div>
                            <div>
                                <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1">Risiko (%)</label>
                                <div className="relative">
                                    <input type="number" value={riskPct} onChange={e => setRiskPct(e.target.value)} min="0.1" max="10" step="0.1"
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)] pr-8" />
                                    <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-[var(--text-dim)] font-bold">%</span>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1">Pair</label>
                                <select value={pair} onChange={e => setPair(e.target.value)}
                                    className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
                                    {PAIRS.map(p => <option key={p.symbol} value={p.symbol}>{p.symbol}</option>)}
                                </select>
                            </div>
                            <div>
                                <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1">Arah</label>
                                <div className="flex gap-2">
                                    {['BUY', 'SELL'].map(d => (
                                        <button key={d} onClick={() => setDirection(d)}
                                            className={`flex-1 py-2.5 rounded-lg text-xs font-black transition-all ${direction === d ? (d === 'BUY' ? 'bg-[var(--success)] text-white' : 'bg-[var(--danger)] text-white') : 'bg-[var(--bg-panel)] text-[var(--text-dim)] border border-[var(--border-color)]'}`}>
                                            {d === 'BUY' ? <span className="flex items-center justify-center gap-1"><TrendingUp size={12} />{d}</span> : <span className="flex items-center justify-center gap-1"><TrendingDown size={12} />{d}</span>}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1">Harga Entry</label>
                                <input type="number" value={entry} onChange={e => setEntry(e.target.value)} step="0.0001"
                                    className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]"
                                    placeholder={selectedPair?.base?.toFixed(2) || '3300.00'} />
                            </div>
                            <div>
                                <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1">Stop Loss</label>
                                <input type="number" value={sl} onChange={e => setSl(e.target.value)} step="0.0001"
                                    className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm font-bold text-[var(--text-danger)] outline-none focus:border-[var(--danger)]"
                                    placeholder="3280.00" />
                            </div>
                        </div>

                        {/* Result */}
                        {calc ? (
                            <div className="mt-2 p-4 rounded-xl bg-[var(--bg-panel)] border border-[var(--accent)]/30 space-y-3">
                                <div className="flex items-center gap-2 mb-3">
                                    <Calculator size={14} className="text-[var(--accent)]" />
                                    <span className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)]">Hasil Kalkulasi</span>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    {[
                                        { label: 'Ukuran Lot', value: calc.lotSize, color: 'var(--accent)' },
                                        { label: 'Risiko ($)', value: `$${calc.riskAmt}`, color: 'var(--danger)' },
                                        { label: 'SL Distance', value: calc.slPips, color: 'var(--text-secondary)' },
                                        { label: 'TP1 (1:2)', value: calc.tp1, color: 'var(--success)' },
                                        { label: 'TP2 (1:3)', value: calc.tp2, color: 'var(--success)' },
                                        { label: 'Reward TP1', value: `$${calc.rewardTP1}`, color: 'var(--success)' },
                                    ].map((r, i) => (
                                        <div key={i} className="flex justify-between items-center">
                                            <span className="text-[9px] text-[var(--text-dim)] font-bold">{r.label}</span>
                                            <span className="text-sm font-black" style={{ color: r.color }}>{r.value}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        ) : (
                            <div className="p-4 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)] text-center">
                                <p className="text-[10px] text-[var(--text-dim)]">Masukkan harga entry dan stop loss untuk kalkulasi</p>
                            </div>
                        )}
                    </div>
                </div>

                {/* Risk Rules */}
                <div className="space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Aturan Manajemen Risiko</p>
                    <div className="space-y-3">
                        {RISK_RULES.map((rule, i) => (
                            <div key={i} className={`p-4 rounded-xl border flex items-start gap-3 ${rule.status === 'ok' ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : 'bg-[var(--bg-card)] border-[var(--accent)]/20'}`}>
                                <div className={`mt-0.5 p-1.5 rounded-lg ${rule.status === 'ok' ? 'bg-[var(--success)]/10' : 'bg-[var(--accent)]/10'}`}>
                                    {rule.status === 'ok'
                                        ? <ShieldCheck size={14} className="text-[var(--success)]" />
                                        : <AlertTriangle size={14} className="text-[var(--accent)]" />}
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex justify-between items-center mb-1">
                                        <p className="text-xs font-bold text-[var(--text-primary)]">{rule.label}</p>
                                        <span className={`text-[9px] font-black px-2 py-0.5 rounded ${rule.status === 'ok' ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--accent)]/10 text-[var(--accent)]'}`}>{rule.value}</span>
                                    </div>
                                    <p className="text-[10px] text-[var(--text-dim)]">{rule.detail}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Daily Risk Meter */}
                    <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Risiko Hari Ini</p>
                        {[
                            { label: 'Digunakan', pct: 1.2, color: 'var(--success)' },
                            { label: 'Tersisa', pct: 3.8, color: 'var(--text-dim)' },
                        ].map((r, i) => (
                            <div key={i} className="mb-3">
                                <div className="flex justify-between text-[9px] font-bold mb-1">
                                    <span className="text-[var(--text-dim)]">{r.label}</span>
                                    <span style={{ color: r.color }}>{r.pct}%</span>
                                </div>
                                <div className="h-2 bg-[var(--bg-hover)] rounded-full">
                                    <div className="h-2 rounded-full" style={{ width: `${(r.pct / 5) * 100}%`, backgroundColor: r.color }} />
                                </div>
                            </div>
                        ))}
                        <p className="text-[9px] text-[var(--text-dim)] mt-2">Batas harian: 5% dari modal akun</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
