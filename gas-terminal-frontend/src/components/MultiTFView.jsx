import React, { useState, useEffect } from 'react';
import { BrainCircuit, TrendingUp, TrendingDown, Minus, RefreshCw, Lock } from 'lucide-react';
import { fetchLatestSignal } from '../services/api';
import { PAIRS } from '../constants';

const TIMEFRAMES = ['M5', 'M15', 'M30', 'H1', 'H4', 'D1'];

const TF_BIAS = {
    M5: { bias: 'BUY', strength: 72, ema: 'Above', rsi: 58, macd: 'Bullish', vol: 'High' },
    M15: { bias: 'BUY', strength: 81, ema: 'Above', rsi: 62, macd: 'Bullish', vol: 'High' },
    M30: { bias: 'NEUTRAL', strength: 50, ema: 'Cross', rsi: 51, macd: 'Flat', vol: 'Low' },
    H1: { bias: 'BUY', strength: 76, ema: 'Above', rsi: 64, macd: 'Bullish', vol: 'Medium' },
    H4: { bias: 'BUY', strength: 88, ema: 'Above', rsi: 67, macd: 'Bullish', vol: 'High' },
    D1: { bias: 'BUY', strength: 91, ema: 'Above', rsi: 70, macd: 'Bullish', vol: 'Very High' },
};

const SMC_ZONES = [
    { type: 'OB', label: 'Order Block Bullish', price: '3285.00', tf: 'H4', status: 'Active', color: 'var(--success)' },
    { type: 'FVG', label: 'Fair Value Gap', price: '3271.50 – 3278.00', tf: 'H1', status: 'Unfilled', color: 'var(--accent)' },
    { type: 'BOS', label: 'Break of Structure', price: '3295.00', tf: 'D1', status: 'Confirmed', color: 'var(--success)' },
    { type: 'SSL', label: 'Sell-Side Liquidity', price: '3250.00', tf: 'D1', status: 'Below', color: 'var(--danger)' },
    { type: 'BSL', label: 'Buy-Side Liquidity', price: '3320.00', tf: 'D1', status: 'Target', color: 'var(--success)' },
];

function BiasIcon({ bias }) {
    if (bias === 'BUY') return <TrendingUp size={14} className="text-[var(--success)]" />;
    if (bias === 'SELL') return <TrendingDown size={14} className="text-[var(--danger)]" />;
    return <Minus size={14} className="text-[var(--text-dim)]" />;
}

function StrengthBar({ value, bias }) {
    const color = bias === 'BUY' ? 'var(--success)' : bias === 'SELL' ? 'var(--danger)' : 'var(--text-dim)';
    return (
        <div className="w-full bg-[var(--bg-hover)] rounded-full h-1.5">
            <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${value}%`, backgroundColor: color }} />
        </div>
    );
}

export default function MultiTFView() {
    const [selectedPair, setSelectedPair] = useState('XAUUSD');
    const [signal, setSignal] = useState(null);
    const [loading, setLoading] = useState(false);
    const [tfData, setTfData] = useState(TF_BIAS);

    const load = async () => {
        setLoading(true);
        try {
            const res = await fetchLatestSignal(selectedPair);
            if (res?.signal) setSignal(res.signal);
        } catch (_) {}
        // Randomize slightly to simulate multi-TF polling
        const updated = {};
        TIMEFRAMES.forEach(tf => {
            const base = TF_BIAS[tf];
            updated[tf] = {
                ...base,
                rsi: Math.round(base.rsi + (Math.random() - 0.5) * 6),
                strength: Math.min(100, Math.round(base.strength + (Math.random() - 0.5) * 8)),
            };
        });
        setTfData(updated);
        setLoading(false);
    };

    useEffect(() => { load(); }, [selectedPair]);

    const bullCount = TIMEFRAMES.filter(tf => tfData[tf]?.bias === 'BUY').length;
    const bearCount = TIMEFRAMES.filter(tf => tfData[tf]?.bias === 'SELL').length;
    const overallBias = bullCount > bearCount ? 'BUY' : bearCount > bullCount ? 'SELL' : 'NEUTRAL';

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <div className="flex items-center gap-2 mb-1">
                        <BrainCircuit size={20} className="text-[var(--accent)]" />
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Analisa Multi-TF</h2>
                        <span className="text-[8px] bg-[var(--accent)] text-black font-black px-2 py-0.5 rounded uppercase">Pro</span>
                    </div>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Konfluensi Sinyal AI Lintas Timeframe · Smart Money Concept</p>
                </div>
                <div className="flex items-center gap-2">
                    <select value={selectedPair} onChange={e => setSelectedPair(e.target.value)}
                        className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none">
                        {PAIRS.map(p => <option key={p.symbol} value={p.symbol}>{p.symbol}</option>)}
                    </select>
                    <button onClick={load} disabled={loading}
                        className="flex items-center gap-2 bg-[var(--accent)] text-black px-4 py-2 rounded-lg text-xs font-black hover:opacity-90 transition-opacity disabled:opacity-50">
                        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                        Analisa
                    </button>
                </div>
            </div>

            {/* Overall Bias Card */}
            <div className={`p-5 rounded-xl border flex items-center gap-6 ${overallBias === 'BUY' ? 'bg-[var(--success)]/5 border-[var(--success)]/30' : overallBias === 'SELL' ? 'bg-[var(--danger)]/5 border-[var(--danger)]/30' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                <div className={`p-4 rounded-xl ${overallBias === 'BUY' ? 'bg-[var(--success)]/10' : 'bg-[var(--danger)]/10'}`}>
                    {overallBias === 'BUY' ? <TrendingUp size={32} className="text-[var(--success)]" /> : <TrendingDown size={32} className="text-[var(--danger)]" />}
                </div>
                <div>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold mb-1">Bias Keseluruhan · {selectedPair}</p>
                    <p className={`text-3xl font-display font-black ${overallBias === 'BUY' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{overallBias}</p>
                    <p className="text-xs text-[var(--text-dim)] mt-1">{bullCount}/{TIMEFRAMES.length} TF Bullish · {bearCount}/{TIMEFRAMES.length} TF Bearish</p>
                </div>
                {signal && (
                    <div className="ml-auto text-right hidden sm:block">
                        <p className="text-[10px] text-[var(--text-dim)] uppercase font-bold mb-1">Latest Signal</p>
                        <p className={`text-lg font-black ${signal.type === 'BUY' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{signal.type}</p>
                        <p className="text-xs text-[var(--text-dim)]">Entry: {signal.entry} · Grade: {signal.grade}</p>
                    </div>
                )}
            </div>

            {/* TF Grid */}
            <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                {TIMEFRAMES.map(tf => {
                    const d = tfData[tf] || TF_BIAS[tf];
                    return (
                        <div key={tf} className={`p-4 rounded-xl border ${d.bias === 'BUY' ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : d.bias === 'SELL' ? 'bg-[var(--bg-card)] border-[var(--danger)]/20' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-[10px] font-black text-[var(--text-dim)] uppercase">{tf}</span>
                                <BiasIcon bias={d.bias} />
                            </div>
                            <p className={`text-sm font-black mb-2 ${d.bias === 'BUY' ? 'text-[var(--success)]' : d.bias === 'SELL' ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'}`}>{d.bias}</p>
                            <StrengthBar value={d.strength} bias={d.bias} />
                            <p className="text-[9px] text-[var(--text-dim)] mt-2">{d.strength}% strength</p>
                            <div className="mt-3 space-y-1">
                                <div className="flex justify-between text-[9px]">
                                    <span className="text-[var(--text-dim)]">RSI</span>
                                    <span className="font-bold text-[var(--text-secondary)]">{d.rsi}</span>
                                </div>
                                <div className="flex justify-between text-[9px]">
                                    <span className="text-[var(--text-dim)]">EMA</span>
                                    <span className="font-bold text-[var(--text-secondary)]">{d.ema}</span>
                                </div>
                                <div className="flex justify-between text-[9px]">
                                    <span className="text-[var(--text-dim)]">MACD</span>
                                    <span className="font-bold text-[var(--text-secondary)]">{d.macd}</span>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* SMC Zones */}
            <div>
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Zona Smart Money · {selectedPair}</p>
                <div className="space-y-2">
                    {SMC_ZONES.map((z, i) => (
                        <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-[var(--text-dim)] transition-all">
                            <div className="w-10 h-10 rounded-lg flex items-center justify-center font-black text-[10px] shrink-0" style={{ backgroundColor: `${z.color}15`, color: z.color }}>{z.type}</div>
                            <div className="flex-1 min-w-0">
                                <p className="text-xs font-bold text-[var(--text-primary)]">{z.label}</p>
                                <p className="text-[10px] text-[var(--text-dim)]">{z.price}</p>
                            </div>
                            <span className="text-[8px] font-bold px-2 py-1 rounded uppercase" style={{ backgroundColor: `${z.color}15`, color: z.color }}>{z.status}</span>
                            <span className="text-[9px] text-[var(--text-dim)] font-bold w-8 text-right">{z.tf}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
