import React, { useState } from 'react';
import Sparkline from './Sparkline';
import { ChevronUp, ChevronDown } from 'lucide-react';

export default function MarketsView({ pairs, prices, directions, onSelect, activePair }) {
    const [tab, setTab] = useState('Aktif');

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6">
            <div className="flex justify-between items-end">
                <div>
                    <h2 className="text-2xl font-display font-black text-white uppercase">Market Hub</h2>
                    <p className="text-[10px] text-[#555] uppercase tracking-widest mt-1">Data Feed Real-time</p>
                </div>
            </div>

            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-[var(--card-shadow)]">
                <div className="flex items-center gap-0 border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                    {['Aktif', 'Top Gainer', 'Top Loser', 'Kripto', 'Forex'].map(t => (
                        <button key={t} onClick={() => setTab(t)}
                            className={`px-6 py-3.5 text-xs font-black border-b-2 transition-all ${tab === t ? 'border-[var(--accent)] text-[var(--accent)] bg-[var(--bg-hover)]' : 'border-transparent text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>{t}</button>
                    ))}
                </div>
                <div className="overflow-x-auto scrollbar-none">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="text-[var(--text-dim)] border-b border-[var(--border-color)] bg-[var(--bg-card)]">
                                <th className="text-left px-5 py-4 font-black uppercase tracking-[0.2em]">Simbol</th>
                                <th className="text-right px-5 py-4 font-black uppercase tracking-[0.2em]">Harga</th>
                                <th className="text-right px-5 py-4 font-black uppercase tracking-[0.2em]">Perubahan</th>
                                <th className="text-right px-5 py-4 font-black uppercase tracking-[0.2em]">%</th>
                                <th className="text-right px-5 py-4 font-black uppercase tracking-[0.2em] hidden sm:table-cell">Tren 24J</th>
                            </tr>
                        </thead>
                        <tbody>
                            {pairs.map(p => {
                                const cur = prices[p.symbol] || p.price || p.base;
                                const chg = cur - p.base;
                                const pct = (chg / p.base * 100);
                                const isUp = pct >= 0;
                                const dir = directions[p.symbol];
                                return (
                                    <tr key={p.symbol} onClick={() => onSelect(p.symbol)}
                                        className={`border-b border-[var(--border-color)] cursor-pointer transition-colors ${activePair === p.symbol ? 'bg-[var(--accent-soft)]' : 'hover:bg-[var(--bg-hover)]'}`}>
                                        <td className="px-5 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-9 h-9 rounded-lg bg-[var(--bg-hover)] flex items-center justify-center text-[10px] font-black text-[var(--text-dim)] border border-[var(--border-color)]">{p.symbol.slice(0, 2)}</div>
                                                <div>
                                                    <p className="font-black text-[var(--text-primary)] text-sm tracking-tight">{p.symbol}</p>
                                                    <p className="text-[9px] text-[var(--text-dim)] font-black uppercase mt-0.5 tracking-widest">{p.name || p.type}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className={`px-5 py-4 text-right font-mono font-black text-sm transition-colors ${dir === 'up' ? 'text-[var(--success)]' : dir === 'down' ? 'text-[var(--danger)]' : 'text-[var(--text-primary)]'}`}>
                                            {cur.toFixed(p.type === 'Forex' ? 4 : 2)}
                                        </td>
                                        <td className={`px-5 py-4 text-right font-mono font-bold ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                            {isUp ? '+' : ''}{chg.toFixed(p.type === 'Forex' ? 4 : 2)}
                                        </td>
                                        <td className={`px-5 py-4 text-right font-mono font-black ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                            <div className="flex items-center justify-end gap-1">
                                                {isUp ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
                                                {Math.abs(pct).toFixed(2)}%
                                            </div>
                                        </td>
                                        <td className="px-5 py-4 text-right hidden sm:table-cell">
                                            <Sparkline data={p.trend || [50, 50, 50, 50, 50, 50, 50, 50, 50, 50]} color={isUp ? 'var(--success)' : 'var(--danger)'} width={80} height={28} />
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
