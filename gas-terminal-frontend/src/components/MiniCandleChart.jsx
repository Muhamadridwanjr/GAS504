import React, { useState, useEffect } from 'react';
import { fetchChartData } from '../services/api';

export default function MiniCandleChart({ pair }) {
    const [candles, setCandles] = useState([]);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const res = await fetchChartData(pair.symbol, 'M15', 40);
                if (res && res.data && res.data.length > 0) {
                    setCandles(res.data);
                }
            } catch (err) {
                console.error("Failed to fetch history for", pair.symbol);
            }
        };
        loadHistory();
    }, [pair.symbol]);

    // Fallback while loading
    if (!candles || candles.length === 0) {
        return <div className="w-full h-full flex items-center justify-center text-[10px] text-[#555] font-bold tracking-widest uppercase">Memuat Chart...</div>;
    }
    const allVals = candles.flatMap(c => [c.high, c.low]);
    const min = Math.min(...allVals), max = Math.max(...allVals);
    const range = max - min || 1;
    const W = 600, H = 160, pad = 4;
    const cw = W / candles.length;

    const toY = (v) => H - pad - ((v - min) / range) * (H - pad * 2);

    return (
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-full" preserveAspectRatio="none">
            {candles.map((c, i) => {
                const x = i * cw + cw / 2;
                const isUp = c.close >= c.open;
                const col = isUp ? '#10b981' : '#ef4444';
                const bodyTop = toY(Math.max(c.open, c.close));
                const bodyBot = toY(Math.min(c.open, c.close));
                const bodyH = Math.max(bodyBot - bodyTop, 1);
                return (
                    <g key={i}>
                        <line x1={x} y1={toY(c.high)} x2={x} y2={toY(c.low)} stroke={col} strokeWidth="0.8" opacity="0.7" />
                        <rect x={x - cw * 0.35} y={bodyTop} width={cw * 0.7} height={bodyH} fill={col} opacity="0.9" rx="0.5" />
                    </g>
                );
            })}
        </svg>
    );
}
