import React, { useState, useEffect } from 'react';
import { Droplet, TrendingUp, TrendingDown, RefreshCw, Activity } from 'lucide-react';
import { callAIFeature } from '../services/api';
import PairSelector from './PairSelector';

export default function LiquidityView() {
    const [pair, setPair] = useState('XAUUSD');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const load = async (p) => {
        setLoading(true);
        setError('');
        try {
            const res = await callAIFeature('fundamental', { pair: p, timeframe: 'H4', focus: 'liquidity' });
            setResult(res);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Gagal memuat data likuiditas. Pastikan EA MT5 aktif.');
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(pair); }, [pair]);

    // Normalize response
    const levels = result?.liquidity_levels || result?.key_levels || result?.levels || result?.zones || [];
    const clusters = result?.clusters || result?.liquidity_clusters || result?.order_blocks || [];
    const heatmap = result?.heatmap || result?.volume_profile || result?.liquidity_heatmap || [];
    const summary = result?.summary || result?.analysis || result?.ai_summary || '';

    const getLevelColor = (type) => {
        if (!type) return 'var(--text-dim)';
        const t = type.toUpperCase();
        if (t.includes('BSL') || t.includes('BUY') || t.includes('SUP') || t === 'OB_BULL') return 'var(--success)';
        if (t.includes('SSL') || t.includes('SELL') || t.includes('RES') || t === 'OB_BEAR') return 'var(--danger)';
        if (t === 'SPOT' || t === 'FVG') return 'var(--accent)';
        return 'var(--text-dim)';
    };

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                    <Droplet size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Peta Likuiditas</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Buy/Sell-Side Liquidity · Order Flow · Cluster Analysis · 5 cr</p>
                    </div>
                </div>
                <div className="flex gap-2 items-center">
                    <PairSelector value={pair} onChange={setPair} label="" />
                    <button onClick={() => load(pair)} disabled={loading}
                        className="flex items-center gap-2 bg-[var(--accent)] text-black px-4 py-2 rounded-lg text-xs font-black hover:opacity-90 transition-opacity disabled:opacity-50">
                        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="rounded-xl p-3 border" style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.2)' }}>
                    <p className="text-xs font-black text-red-400">⚠️ {error}</p>
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Price Level Map */}
                <div className="space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Level Kunci · {pair}</p>
                    {loading ? (
                        <div className="space-y-2">
                            {[...Array(7)].map((_, i) => (
                                <div key={i} className="h-14 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] animate-pulse" />
                            ))}
                        </div>
                    ) : levels.length > 0 ? (
                        <div className="relative">
                            <div className="flex items-center gap-2 mb-2">
                                <TrendingUp size={12} className="text-[var(--success)]" />
                                <span className="text-[9px] font-black text-[var(--success)] uppercase">Buy-Side Liquidity (Target Harga Naik)</span>
                            </div>
                            <div className="space-y-2">
                                {levels.map((lv, i) => {
                                    const color = lv.color || getLevelColor(lv.type);
                                    const vol = lv.vol || lv.volume || lv.strength || 50;
                                    return (
                                        <div key={i} className={`relative flex items-center gap-3 p-3 rounded-xl border transition-all hover:opacity-80 ${(lv.type || '').toUpperCase() === 'SPOT' ? 'bg-[var(--accent)]/5 border-[var(--accent)]/50' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                                            <div className="absolute left-0 top-0 bottom-0 rounded-xl opacity-10 transition-all"
                                                style={{ width: `${vol}%`, backgroundColor: color }} />
                                            <div className="w-10 h-8 rounded-lg flex items-center justify-center text-[8px] font-black shrink-0 z-10"
                                                style={{ backgroundColor: `${color}20`, color }}>{lv.type || '—'}</div>
                                            <div className="flex-1 z-10">
                                                <p className="text-[10px] font-bold text-[var(--text-primary)]">{lv.label || lv.description || lv.type}</p>
                                                <p className="text-xs font-black" style={{ color }}>{lv.price || lv.level || '—'}</p>
                                            </div>
                                            <div className="text-right z-10">
                                                <p className="text-[8px] font-bold text-[var(--text-dim)]">{lv.tf || lv.timeframe || '—'}</p>
                                                <p className="text-[9px] font-black" style={{ color }}>{vol}% vol</p>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                            <div className="flex items-center gap-2 mt-2">
                                <TrendingDown size={12} className="text-[var(--danger)]" />
                                <span className="text-[9px] font-black text-[var(--danger)] uppercase">Sell-Side Liquidity (Target Harga Turun)</span>
                            </div>
                        </div>
                    ) : (
                        <div className="flex items-center justify-center py-16 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl">
                            <div className="text-center">
                                <Droplet size={28} className="mx-auto mb-2 opacity-20 text-[var(--text-dim)]" />
                                <p className="text-xs font-bold text-[var(--text-dim)]">Koneksi EA MT5 untuk melihat level likuiditas</p>
                            </div>
                        </div>
                    )}
                </div>

                {/* Heatmap + Clusters */}
                <div className="space-y-6">
                    {/* Liquidity Heatmap */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Heatmap Volume Likuiditas</p>
                        <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            {loading ? (
                                <div className="h-28 bg-[var(--bg-panel)] rounded animate-pulse" />
                            ) : heatmap.length > 0 ? (
                                <div className="flex gap-1 items-end h-28">
                                    {heatmap.map((h, i) => {
                                        const isSpot = (h.price || '').toUpperCase() === 'SPOT';
                                        const isAbove = i < Math.floor(heatmap.length / 2);
                                        const color = isSpot ? 'var(--accent)' : isAbove ? 'var(--success)' : 'var(--danger)';
                                        const vol = h.vol || h.volume || h.value || 50;
                                        return (
                                            <div key={i} className="flex-1 flex flex-col items-center gap-1">
                                                <div className="w-full rounded-sm" style={{
                                                    height: `${vol}%`, backgroundColor: color,
                                                    opacity: isSpot ? 1 : 0.6 + vol / 250
                                                }} />
                                                <span className="text-[var(--text-dim)] font-bold" style={{ writingMode: 'vertical-rl', fontSize: '6px' }}>{h.price || h.label || '—'}</span>
                                            </div>
                                        );
                                    })}
                                </div>
                            ) : (
                                <div className="flex items-center justify-center h-28 text-[var(--text-dim)]">
                                    <p className="text-[10px] font-bold">Heatmap akan muncul setelah analisa</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Liquidity Clusters */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Kluster Likuiditas Utama</p>
                        {loading ? (
                            <div className="space-y-2">
                                {[...Array(4)].map((_, i) => (
                                    <div key={i} className="h-14 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] animate-pulse" />
                                ))}
                            </div>
                        ) : clusters.length > 0 ? (
                            <div className="space-y-2">
                                {clusters.map((c, i) => {
                                    const cType = (c.type || c.direction || '').toLowerCase();
                                    const isBuy = cType.includes('buy') || cType.includes('bull') || cType === 'bsl';
                                    const isSell = cType.includes('sell') || cType.includes('bear') || cType === 'ssl';
                                    const strength = c.strength || c.confidence || c.score || 50;
                                    return (
                                        <div key={i} className={`p-3 rounded-xl border flex items-center gap-3 ${isBuy ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : isSell ? 'bg-[var(--bg-card)] border-[var(--danger)]/20' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                                            <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${isBuy ? 'bg-[var(--success)]/10' : isSell ? 'bg-[var(--danger)]/10' : 'bg-[var(--bg-hover)]'}`}>
                                                {isBuy ? <TrendingUp size={14} className="text-[var(--success)]" /> : <TrendingDown size={14} className="text-[var(--danger)]" />}
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-xs font-black text-[var(--text-primary)]">{c.zone || c.label || c.type}</p>
                                                <p className="text-[9px] text-[var(--text-dim)]">{c.range || c.price_range || '—'} {c.vol ? `· ${c.vol}` : ''}</p>
                                                <div className="h-1 bg-[var(--bg-hover)] rounded-full mt-1.5">
                                                    <div className="h-1 rounded-full" style={{
                                                        width: `${strength}%`,
                                                        backgroundColor: isBuy ? 'var(--success)' : isSell ? 'var(--danger)' : 'var(--text-dim)'
                                                    }} />
                                                </div>
                                            </div>
                                            <span className="text-xs font-black shrink-0" style={{ color: isBuy ? 'var(--success)' : isSell ? 'var(--danger)' : 'var(--text-dim)' }}>{strength}%</span>
                                        </div>
                                    );
                                })}
                            </div>
                        ) : (
                            <div className="flex items-center justify-center py-8 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl">
                                <div className="text-center">
                                    <Activity size={22} className="mx-auto mb-2 opacity-20 text-[var(--text-dim)]" />
                                    <p className="text-[10px] font-bold text-[var(--text-dim)]">Kluster akan muncul setelah analisa</p>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* AI Summary */}
            {summary && (
                <div className="bg-[var(--bg-card)] border border-[var(--accent)]/20 rounded-xl p-5">
                    <p className="text-[10px] font-black text-[var(--accent)] uppercase tracking-widest mb-2">AI Liquidity Analysis</p>
                    <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{summary}</p>
                </div>
            )}
        </div>
    );
}
