import React, { useState, useEffect } from 'react';
import { BarChart2, TrendingUp, TrendingDown, RefreshCw, Newspaper, Globe } from 'lucide-react';
import { MACRO_DATA, NEWS_FEED, PAIRS } from '../constants';

const FEAR_GREED = 68; // 0-100

const COT_DATA = [
    { asset: 'XAUUSD', longPct: 74, shortPct: 26, net: '+48%', bias: 'BULLISH' },
    { asset: 'EURUSD', longPct: 52, shortPct: 48, net: '+4%', bias: 'NEUTRAL' },
    { asset: 'GBPUSD', longPct: 61, shortPct: 39, net: '+22%', bias: 'BULLISH' },
    { asset: 'BTCUSD', longPct: 58, shortPct: 42, net: '+16%', bias: 'BULLISH' },
    { asset: 'USDJPY', longPct: 38, shortPct: 62, net: '-24%', bias: 'BEARISH' },
    { asset: 'ETHUSD', longPct: 55, shortPct: 45, net: '+10%', bias: 'BULLISH' },
];

const RETAIL_SENTIMENT = [
    { pair: 'XAUUSD', longs: 71, shorts: 29 },
    { pair: 'BTCUSD', longs: 64, shorts: 36 },
    { pair: 'EURUSD', longs: 48, shorts: 52 },
    { pair: 'GBPUSD', longs: 55, shorts: 45 },
];

function FearGreedGauge({ value }) {
    const angle = -135 + (value / 100) * 270;
    const color = value < 25 ? '#ef4444' : value < 45 ? '#f97316' : value < 55 ? '#eab308' : value < 75 ? '#22c55e' : '#16a34a';
    const label = value < 25 ? 'Extreme Fear' : value < 45 ? 'Fear' : value < 55 ? 'Neutral' : value < 75 ? 'Greed' : 'Extreme Greed';

    return (
        <div className="flex flex-col items-center">
            <div className="relative w-40 h-20 overflow-hidden">
                <svg viewBox="0 0 100 50" className="w-full">
                    {/* Background arc */}
                    <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="var(--bg-hover)" strokeWidth="8" />
                    {/* Colored arc */}
                    {[
                        { from: -135, to: -67.5, color: '#ef4444' },
                        { from: -67.5, to: 0, color: '#f97316' },
                        { from: 0, to: 67.5, color: '#22c55e' },
                        { from: 67.5, to: 135, color: '#16a34a' },
                    ].map((seg, i) => (
                        <path key={i} d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke={seg.color} strokeWidth="8" strokeOpacity="0.3" />
                    ))}
                    {/* Needle */}
                    <line
                        x1="50" y1="50"
                        x2={50 + 35 * Math.cos((angle - 90) * Math.PI / 180)}
                        y2={50 + 35 * Math.sin((angle - 90) * Math.PI / 180)}
                        stroke={color} strokeWidth="2" strokeLinecap="round"
                    />
                    <circle cx="50" cy="50" r="3" fill={color} />
                </svg>
            </div>
            <p className="text-2xl font-display font-black mt-1" style={{ color }}>{value}</p>
            <p className="text-xs font-bold" style={{ color }}>{label}</p>
        </div>
    );
}

export default function SentimentView() {
    const [macro] = useState(MACRO_DATA);
    const [news] = useState(NEWS_FEED);
    const [loading, setLoading] = useState(false);

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <BarChart2 size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Sentimen Pasar</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Analisa Sentimen Retail, COT & Fear/Greed</p>
                    </div>
                </div>
                <button className="flex items-center gap-2 bg-[var(--bg-card)] border border-[var(--border-color)] px-3 py-2 rounded-lg text-xs font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">
                    <RefreshCw size={12} />
                    Update
                </button>
            </div>

            {/* Top Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Fear & Greed */}
                <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex flex-col items-center">
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Fear & Greed Index</p>
                    <FearGreedGauge value={FEAR_GREED} />
                    <p className="text-[9px] text-[var(--text-dim)] mt-3 text-center">Indeks pasar crypto global — data realtime dari alternatif.me</p>
                </div>

                {/* Global Risk */}
                <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Kondisi Risiko Global</p>
                    <div className="space-y-3">
                        {[
                            { label: 'Risk-On Assets', pct: 62, color: 'var(--success)', icon: <TrendingUp size={12} /> },
                            { label: 'Risk-Off Assets', pct: 38, color: 'var(--danger)', icon: <TrendingDown size={12} /> },
                            { label: 'Safe Haven Demand', pct: 74, color: 'var(--accent)', icon: <Globe size={12} /> },
                            { label: 'Market Volatility', pct: 45, color: 'var(--text-dim)', icon: <BarChart2 size={12} /> },
                        ].map((r, i) => (
                            <div key={i}>
                                <div className="flex justify-between text-[9px] font-bold mb-1">
                                    <span className="flex items-center gap-1" style={{ color: r.color }}>{r.icon}{r.label}</span>
                                    <span style={{ color: r.color }}>{r.pct}%</span>
                                </div>
                                <div className="h-1.5 bg-[var(--bg-hover)] rounded-full">
                                    <div className="h-1.5 rounded-full" style={{ width: `${r.pct}%`, backgroundColor: r.color }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Macro */}
                <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Data Makro Utama</p>
                    <div className="space-y-2">
                        {macro.map((m, i) => (
                            <div key={i} className="flex items-center gap-2 p-2 rounded-lg bg-[var(--bg-panel)]">
                                <div className="flex-1 min-w-0">
                                    <p className="text-[9px] font-bold text-[var(--text-primary)] truncate">{m.title}</p>
                                    <p className="text-[8px] text-[var(--text-dim)]">{m.bias}</p>
                                </div>
                                <span className="text-xs font-black text-[var(--accent)] shrink-0">{m.value}</span>
                                <span className={`text-[7px] font-black px-1.5 py-0.5 rounded shrink-0 ${m.impact === 'HIGH' ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--accent)]/10 text-[var(--accent)]'}`}>{m.impact}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* COT Report */}
            <div>
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">COT Report · Posisi Institusi</p>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                    {COT_DATA.map((d, i) => (
                        <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <div className="flex justify-between items-center mb-3">
                                <span className="text-xs font-black text-[var(--text-primary)]">{d.asset}</span>
                                <span className={`text-[8px] font-black px-2 py-0.5 rounded ${d.bias === 'BULLISH' ? 'bg-[var(--success)]/10 text-[var(--success)]' : d.bias === 'BEARISH' ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>{d.bias}</span>
                            </div>
                            <div className="h-4 flex rounded-full overflow-hidden mb-2">
                                <div className="bg-[var(--success)] transition-all" style={{ width: `${d.longPct}%` }} />
                                <div className="bg-[var(--danger)] transition-all" style={{ width: `${d.shortPct}%` }} />
                            </div>
                            <div className="flex justify-between text-[9px] font-bold">
                                <span className="text-[var(--success)]">Long {d.longPct}%</span>
                                <span className="text-[var(--text-dim)]">Net {d.net}</span>
                                <span className="text-[var(--danger)]">Short {d.shortPct}%</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Retail Sentiment */}
            <div>
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Sentimen Retail (Contrarian)</p>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {RETAIL_SENTIMENT.map((r, i) => (
                        <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <p className="text-xs font-black text-[var(--text-primary)] mb-3">{r.pair}</p>
                            <div className="relative h-20 w-20 mx-auto">
                                <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                                    <circle cx="18" cy="18" r="15.9" fill="transparent" stroke="var(--danger)" strokeWidth="3"
                                        strokeDasharray={`${r.shorts} ${100 - r.shorts}`} strokeDashoffset="0" />
                                    <circle cx="18" cy="18" r="15.9" fill="transparent" stroke="var(--success)" strokeWidth="3"
                                        strokeDasharray={`${r.longs} ${100 - r.longs}`} strokeDashoffset={`-${r.shorts}`} />
                                </svg>
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <span className="text-xs font-black text-[var(--success)]">{r.longs}%</span>
                                </div>
                            </div>
                            <div className="flex justify-between mt-2 text-[8px] font-bold">
                                <span className="text-[var(--success)]">Long {r.longs}%</span>
                                <span className="text-[var(--danger)]">Short {r.shorts}%</span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* News Sentiment */}
            <div>
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Analisa Sentimen Berita</p>
                <div className="space-y-2">
                    {news.map((n, i) => {
                        const text = typeof n === 'string' ? n : n.title || n;
                        const isBull = text.includes('📈') || text.includes('reli') || text.includes('melonjak') || text.includes('tembus');
                        return (
                            <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                <div className={`p-1.5 rounded-lg ${isBull ? 'bg-[var(--success)]/10' : 'bg-[var(--danger)]/10'}`}>
                                    <Newspaper size={12} className={isBull ? 'text-[var(--success)]' : 'text-[var(--danger)]'} />
                                </div>
                                <p className="flex-1 text-[10px] text-[var(--text-secondary)] font-bold">{text}</p>
                                <span className={`text-[8px] font-black px-2 py-0.5 rounded shrink-0 ${isBull ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>
                                    {isBull ? 'BULLISH' : 'BEARISH'}
                                </span>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
}
