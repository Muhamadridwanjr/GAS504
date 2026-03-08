import React, { useState } from 'react';
import { Droplet, TrendingUp, TrendingDown, RefreshCw } from 'lucide-react';
import { PAIRS } from '../constants';

const genLevels = (base, type) => {
    const isForex = type === 'Forex';
    const prec = isForex ? 4 : 2;
    const step = isForex ? 0.002 : 5;
    return [
        { price: +(base + step * 6).toFixed(prec), type: 'BSL', label: 'Buy-Side Liquidity', vol: 92, tf: 'D1', color: 'var(--success)' },
        { price: +(base + step * 4).toFixed(prec), type: 'OB', label: 'Order Block Bearish', vol: 67, tf: 'H4', color: 'var(--danger)' },
        { price: +(base + step * 2).toFixed(prec), type: 'RES', label: 'Resistance Level', vol: 78, tf: 'H1', color: 'var(--danger)' },
        { price: +(base).toFixed(prec), type: 'SPOT', label: 'Harga Saat Ini', vol: 100, tf: '--', color: 'var(--accent)' },
        { price: +(base - step * 2).toFixed(prec), type: 'SUP', label: 'Support Level', vol: 82, tf: 'H1', color: 'var(--success)' },
        { price: +(base - step * 4).toFixed(prec), type: 'OB', label: 'Order Block Bullish', vol: 71, tf: 'H4', color: 'var(--success)' },
        { price: +(base - step * 6).toFixed(prec), type: 'SSL', label: 'Sell-Side Liquidity', vol: 88, tf: 'D1', color: 'var(--danger)' },
    ];
};

const HEATMAP_DATA = [
    { price: '+3.0%', vol: 45 }, { price: '+2.5%', vol: 62 }, { price: '+2.0%', vol: 38 },
    { price: '+1.5%', vol: 71 }, { price: '+1.0%', vol: 88 }, { price: '+0.5%', vol: 55 },
    { price: 'SPOT', vol: 100 }, { price: '-0.5%', vol: 60 }, { price: '-1.0%', vol: 92 },
    { price: '-1.5%', vol: 76 }, { price: '-2.0%', vol: 44 }, { price: '-2.5%', vol: 58 },
    { price: '-3.0%', vol: 39 },
];

const CLUSTER_DATA = [
    { zone: 'Mega BSL', range: '+2.8% ~ +3.2%', vol: '$4.2B', type: 'buy', strength: 94 },
    { zone: 'BSL Utama', range: '+1.8% ~ +2.0%', vol: '$2.8B', type: 'buy', strength: 78 },
    { zone: 'Void Zone', range: '+0.3% ~ +0.7%', vol: '$0.4B', type: 'neutral', strength: 30 },
    { zone: 'SSL Utama', range: '-1.8% ~ -2.2%', vol: '$3.1B', type: 'sell', strength: 86 },
    { zone: 'Mega SSL', range: '-2.8% ~ -3.2%', vol: '$5.0B', type: 'sell', strength: 97 },
];

export default function LiquidityView() {
    const [pair, setPair] = useState('XAUUSD');
    const selectedPair = PAIRS.find(p => p.symbol === pair) || PAIRS[0];
    const levels = genLevels(selectedPair.base, selectedPair.type);

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                    <Droplet size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Peta Likuiditas</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Buy/Sell-Side Liquidity · Order Flow · Cluster Analysis</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <select value={pair} onChange={e => setPair(e.target.value)}
                        className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                        {PAIRS.map(p => <option key={p.symbol} value={p.symbol}>{p.symbol}</option>)}
                    </select>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Price Level Map */}
                <div className="space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Level Kunci · {pair}</p>
                    <div className="relative">
                        {/* BSL Arrow */}
                        <div className="flex items-center gap-2 mb-2">
                            <TrendingUp size={12} className="text-[var(--success)]" />
                            <span className="text-[9px] font-black text-[var(--success)] uppercase">Buy-Side Liquidity (Target Harga Naik)</span>
                        </div>
                        <div className="space-y-2">
                            {levels.map((lv, i) => (
                                <div key={i} className={`relative flex items-center gap-3 p-3 rounded-xl border transition-all hover:opacity-80 ${lv.type === 'SPOT' ? 'bg-[var(--accent)]/5 border-[var(--accent)]/50' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                                    {/* Volume bar background */}
                                    <div className="absolute left-0 top-0 bottom-0 rounded-xl opacity-10 transition-all"
                                        style={{ width: `${lv.vol}%`, backgroundColor: lv.color }} />
                                    <div className="w-10 h-8 rounded-lg flex items-center justify-center text-[8px] font-black shrink-0 z-10"
                                        style={{ backgroundColor: `${lv.color}20`, color: lv.color }}>{lv.type}</div>
                                    <div className="flex-1 z-10">
                                        <p className="text-[10px] font-bold text-[var(--text-primary)]">{lv.label}</p>
                                        <p className="text-xs font-black" style={{ color: lv.color }}>{lv.price}</p>
                                    </div>
                                    <div className="text-right z-10">
                                        <p className="text-[8px] font-bold text-[var(--text-dim)]">{lv.tf}</p>
                                        <p className="text-[9px] font-black" style={{ color: lv.color }}>{lv.vol}% vol</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                        <div className="flex items-center gap-2 mt-2">
                            <TrendingDown size={12} className="text-[var(--danger)]" />
                            <span className="text-[9px] font-black text-[var(--danger)] uppercase">Sell-Side Liquidity (Target Harga Turun)</span>
                        </div>
                    </div>
                </div>

                {/* Heatmap + Clusters */}
                <div className="space-y-6">
                    {/* Liquidity Heatmap */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Heatmap Volume Likuiditas</p>
                        <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <div className="flex gap-1 items-end h-28">
                                {HEATMAP_DATA.map((h, i) => {
                                    const isSpot = h.price === 'SPOT';
                                    const isAbove = i < 6;
                                    const color = isSpot ? 'var(--accent)' : isAbove ? 'var(--success)' : 'var(--danger)';
                                    return (
                                        <div key={i} className="flex-1 flex flex-col items-center gap-1">
                                            <div className="w-full rounded-sm" style={{
                                                height: `${h.vol}%`,
                                                backgroundColor: color,
                                                opacity: isSpot ? 1 : 0.6 + h.vol / 250
                                            }} />
                                            <span className="text-[6px] text-[var(--text-dim)] font-bold" style={{ writingMode: 'vertical-rl', fontSize: '6px' }}>{h.price}</span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    </div>

                    {/* Liquidity Clusters */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Kluster Likuiditas Utama</p>
                        <div className="space-y-2">
                            {CLUSTER_DATA.map((c, i) => (
                                <div key={i} className={`p-3 rounded-xl border flex items-center gap-3 ${c.type === 'buy' ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : c.type === 'sell' ? 'bg-[var(--bg-card)] border-[var(--danger)]/20' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${c.type === 'buy' ? 'bg-[var(--success)]/10' : c.type === 'sell' ? 'bg-[var(--danger)]/10' : 'bg-[var(--bg-hover)]'}`}>
                                        {c.type === 'buy' ? <TrendingUp size={14} className="text-[var(--success)]" /> : <TrendingDown size={14} className="text-[var(--danger)]" />}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-black text-[var(--text-primary)]">{c.zone}</p>
                                        <p className="text-[9px] text-[var(--text-dim)]">{c.range} · {c.vol}</p>
                                        <div className="h-1 bg-[var(--bg-hover)] rounded-full mt-1.5">
                                            <div className="h-1 rounded-full" style={{
                                                width: `${c.strength}%`,
                                                backgroundColor: c.type === 'buy' ? 'var(--success)' : c.type === 'sell' ? 'var(--danger)' : 'var(--text-dim)'
                                            }} />
                                        </div>
                                    </div>
                                    <span className="text-xs font-black shrink-0" style={{ color: c.type === 'buy' ? 'var(--success)' : c.type === 'sell' ? 'var(--danger)' : 'var(--text-dim)' }}>{c.strength}%</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
