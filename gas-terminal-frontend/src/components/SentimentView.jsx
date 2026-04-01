import React, { useState, useEffect, useCallback } from 'react';
import { BarChart2, TrendingUp, TrendingDown, RefreshCw, Newspaper, Globe, Brain } from 'lucide-react';
import { callAIFeature } from '../services/api';
import PairSelector from './PairSelector';

function FearGreedGauge({ value }) {
    const angle = -135 + (value / 100) * 270;
    const color = value < 25 ? '#ef4444' : value < 45 ? '#f97316' : value < 55 ? '#eab308' : value < 75 ? '#22c55e' : '#16a34a';
    const label = value < 25 ? 'Extreme Fear' : value < 45 ? 'Fear' : value < 55 ? 'Neutral' : value < 75 ? 'Greed' : 'Extreme Greed';
    return (
        <div className="flex flex-col items-center">
            <div className="relative w-40 h-20 overflow-hidden">
                <svg viewBox="0 0 100 50" className="w-full">
                    <path d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke="var(--bg-hover)" strokeWidth="8" />
                    {[
                        { color: '#ef4444' }, { color: '#f97316' },
                        { color: '#22c55e' }, { color: '#16a34a' },
                    ].map((seg, i) => (
                        <path key={i} d="M 10 50 A 40 40 0 0 1 90 50" fill="none" stroke={seg.color} strokeWidth="8" strokeOpacity="0.3" />
                    ))}
                    <line x1="50" y1="50"
                        x2={50 + 35 * Math.cos((angle - 90) * Math.PI / 180)}
                        y2={50 + 35 * Math.sin((angle - 90) * Math.PI / 180)}
                        stroke={color} strokeWidth="2" strokeLinecap="round" />
                    <circle cx="50" cy="50" r="3" fill={color} />
                </svg>
            </div>
            <p className="text-2xl font-display font-black mt-1" style={{ color }}>{value}</p>
            <p className="text-xs font-bold" style={{ color }}>{label}</p>
        </div>
    );
}

export default function SentimentView() {
    const [pair, setPair] = useState('XAUUSD');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const fetchSentiment = useCallback(async (p) => {
        setLoading(true);
        setError(null);
        try {
            const data = await callAIFeature('sentiment', { pair: p });
            setResult(data);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Gagal memuat data sentimen.');
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => { fetchSentiment(pair); }, [pair, fetchSentiment]);

    // Extract fields defensively from any response shape
    const fearGreed = result?.fear_greed_index ?? result?.fear_greed ?? result?.overall_sentiment ?? 50;
    const cot = result?.cot_data || result?.institutional_positions || [];
    const retail = result?.retail_sentiment || result?.retail_positions || [];
    const globalRisk = result?.global_risk || result?.risk_metrics || null;
    const newsItems = result?.news_sentiment || result?.news || [];
    const aiSummary = result?.ai_summary || result?.summary || result?.analysis || null;
    const regime = result?.market_regime || result?.regime || null;

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div className="flex items-center gap-2">
                    <BarChart2 size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Sentimen Pasar</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Real-time AI Sentiment · COT · Fear/Greed · 5 Kredit</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className="w-44">
                        <PairSelector value={pair} onChange={p => setPair(p)} label="" />
                    </div>
                    <button
                        onClick={() => fetchSentiment(pair)}
                        disabled={loading}
                        className="flex items-center gap-2 bg-[var(--bg-card)] border border-[var(--border-color)] px-3 py-2 rounded-lg text-xs font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors disabled:opacity-50">
                        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                        {loading ? 'Loading...' : 'Refresh · 5cr'}
                    </button>
                </div>
            </div>

            {/* Error */}
            {error && (
                <div className="rounded-xl p-4 border" style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.25)' }}>
                    <p className="text-xs font-black text-red-400">⚠️ {error}</p>
                    <p className="text-[9px] text-red-400/70 mt-1">Pastikan gas-strategy-core running dan MT5 EA terhubung.</p>
                </div>
            )}

            {/* Loading Skeleton */}
            {loading && !result && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {[1,2,3].map(i => (
                        <div key={i} className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] h-48 flex items-center justify-center">
                            <div className="flex flex-col items-center gap-3">
                                <Brain size={20} className="text-[var(--accent)] animate-pulse" />
                                <p className="text-[9px] text-[var(--text-dim)] font-mono animate-pulse">Memuat AI sentimen...</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {result && (
                <>
                    {/* AI Summary Banner */}
                    {(aiSummary || regime) && (
                        <div className="rounded-xl p-4 border" style={{ background: 'rgba(250,200,21,0.03)', borderColor: 'rgba(250,200,21,0.15)' }}>
                            <div className="flex items-start gap-3">
                                <Brain size={14} style={{ color: '#fac815' }} className="mt-0.5 shrink-0" />
                                <div>
                                    {regime && <p className="text-[9px] font-black uppercase tracking-widest mb-1" style={{ color: '#fac815' }}>Market Regime: {regime}</p>}
                                    {aiSummary && <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{aiSummary}</p>}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Top Row */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {/* Fear & Greed */}
                        <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex flex-col items-center">
                            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Fear & Greed Index</p>
                            <FearGreedGauge value={typeof fearGreed === 'number' ? fearGreed : 50} />
                            <p className="text-[9px] text-[var(--text-dim)] mt-3 text-center">
                                {result?.fear_greed_source || 'Sumber: AI sentiment analysis · real-time'}
                            </p>
                        </div>

                        {/* Global Risk */}
                        <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Kondisi Risiko Global</p>
                            <div className="space-y-3">
                                {globalRisk ? (
                                    Object.entries(globalRisk).map(([key, val], i) => {
                                        const pct = typeof val === 'number' ? Math.round(val) : parseInt(val) || 50;
                                        const label = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
                                        const isUp = pct >= 50;
                                        return (
                                            <div key={i}>
                                                <div className="flex justify-between text-[9px] font-bold mb-1">
                                                    <span className="flex items-center gap-1" style={{ color: isUp ? 'var(--success)' : 'var(--danger)' }}>
                                                        {isUp ? <TrendingUp size={10} /> : <TrendingDown size={10} />}
                                                        {label}
                                                    </span>
                                                    <span style={{ color: isUp ? 'var(--success)' : 'var(--danger)' }}>{pct}%</span>
                                                </div>
                                                <div className="h-1.5 bg-[var(--bg-hover)] rounded-full">
                                                    <div className="h-1.5 rounded-full transition-all duration-700"
                                                        style={{ width: `${pct}%`, backgroundColor: isUp ? 'var(--success)' : 'var(--danger)' }} />
                                                </div>
                                            </div>
                                        );
                                    })
                                ) : (
                                    [
                                        { label: 'Risk-On', pct: result?.risk_on_pct || 50, color: 'var(--success)', icon: <TrendingUp size={10} /> },
                                        { label: 'Risk-Off', pct: result?.risk_off_pct || 50, color: 'var(--danger)', icon: <TrendingDown size={10} /> },
                                        { label: 'Safe Haven', pct: result?.safe_haven_pct || 50, color: 'var(--accent)', icon: <Globe size={10} /> },
                                        { label: 'Volatility', pct: result?.volatility_pct || 40, color: 'var(--text-dim)', icon: <BarChart2 size={10} /> },
                                    ].map((r, i) => (
                                        <div key={i}>
                                            <div className="flex justify-between text-[9px] font-bold mb-1">
                                                <span className="flex items-center gap-1" style={{ color: r.color }}>{r.icon}{r.label}</span>
                                                <span style={{ color: r.color }}>{r.pct}%</span>
                                            </div>
                                            <div className="h-1.5 bg-[var(--bg-hover)] rounded-full">
                                                <div className="h-1.5 rounded-full transition-all duration-700"
                                                    style={{ width: `${r.pct}%`, backgroundColor: r.color }} />
                                            </div>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>

                        {/* Pair Sentiment */}
                        <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Sentimen {pair}</p>
                            <div className="space-y-2">
                                {[
                                    { label: 'Bias',         val: result?.bias || result?.signal || result?.recommendation || '—' },
                                    { label: 'Strength',     val: result?.strength || result?.signal_strength || '—' },
                                    { label: 'Trend',        val: result?.trend || result?.market_trend || '—' },
                                    { label: 'AI Score',     val: result?.score != null ? `${result.score}/100` : (result?.sentiment_score != null ? `${result.sentiment_score}/100` : '—') },
                                    { label: 'Confidence',   val: result?.confidence != null ? `${result.confidence}%` : '—' },
                                ].map(({ label, val }) => (
                                    <div key={label} className="flex items-center justify-between p-2 rounded-lg bg-[var(--bg-panel)]">
                                        <p className="text-[9px] font-bold text-[var(--text-dim)] uppercase">{label}</p>
                                        <span className={`text-[10px] font-black font-mono ${
                                            String(val).includes('BUY') || String(val).includes('BULL') ? 'text-green-400' :
                                            String(val).includes('SELL') || String(val).includes('BEAR') ? 'text-red-400' :
                                            'text-[var(--accent)]'
                                        }`}>{val}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* COT Report */}
                    {cot.length > 0 && (
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">COT Report · Posisi Institusi</p>
                            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                                {cot.map((d, i) => {
                                    const asset = d.asset || d.symbol || d.pair || '';
                                    const longPct = d.long_pct ?? d.longPct ?? d.long ?? 50;
                                    const shortPct = d.short_pct ?? d.shortPct ?? d.short ?? (100 - longPct);
                                    const bias = d.bias || (longPct > shortPct ? 'BULLISH' : longPct < shortPct ? 'BEARISH' : 'NEUTRAL');
                                    const net = d.net || (longPct > shortPct ? `+${longPct - shortPct}%` : `${longPct - shortPct}%`);
                                    return (
                                        <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                            <div className="flex justify-between items-center mb-3">
                                                <span className="text-xs font-black text-[var(--text-primary)]">{asset}</span>
                                                <span className={`text-[8px] font-black px-2 py-0.5 rounded ${bias === 'BULLISH' ? 'bg-[var(--success)]/10 text-[var(--success)]' : bias === 'BEARISH' ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>{bias}</span>
                                            </div>
                                            <div className="h-4 flex rounded-full overflow-hidden mb-2">
                                                <div className="bg-[var(--success)] transition-all" style={{ width: `${longPct}%` }} />
                                                <div className="bg-[var(--danger)] transition-all" style={{ width: `${shortPct}%` }} />
                                            </div>
                                            <div className="flex justify-between text-[9px] font-bold">
                                                <span className="text-[var(--success)]">Long {longPct}%</span>
                                                <span className="text-[var(--text-dim)]">Net {net}</span>
                                                <span className="text-[var(--danger)]">Short {shortPct}%</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Retail Sentiment */}
                    {retail.length > 0 && (
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Sentimen Retail (Contrarian)</p>
                            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                                {retail.map((r, i) => {
                                    const p = r.pair || r.symbol || r.asset || '';
                                    const longs = r.longs ?? r.long_pct ?? r.long ?? 50;
                                    const shorts = r.shorts ?? r.short_pct ?? r.short ?? (100 - longs);
                                    return (
                                        <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                            <p className="text-xs font-black text-[var(--text-primary)] mb-3">{p}</p>
                                            <div className="relative h-20 w-20 mx-auto">
                                                <svg viewBox="0 0 36 36" className="w-full h-full -rotate-90">
                                                    <circle cx="18" cy="18" r="15.9" fill="transparent" stroke="var(--danger)" strokeWidth="3"
                                                        strokeDasharray={`${shorts} ${100 - shorts}`} strokeDashoffset="0" />
                                                    <circle cx="18" cy="18" r="15.9" fill="transparent" stroke="var(--success)" strokeWidth="3"
                                                        strokeDasharray={`${longs} ${100 - longs}`} strokeDashoffset={`-${shorts}`} />
                                                </svg>
                                                <div className="absolute inset-0 flex items-center justify-center">
                                                    <span className="text-xs font-black text-[var(--success)]">{longs}%</span>
                                                </div>
                                            </div>
                                            <div className="flex justify-between mt-2 text-[8px] font-bold">
                                                <span className="text-[var(--success)]">Long {longs}%</span>
                                                <span className="text-[var(--danger)]">Short {shorts}%</span>
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* News Sentiment */}
                    {newsItems.length > 0 && (
                        <div>
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Analisa Sentimen Berita</p>
                            <div className="space-y-2">
                                {newsItems.map((n, i) => {
                                    const text = typeof n === 'string' ? n : n.title || n.headline || JSON.stringify(n);
                                    const sentiment = (typeof n === 'object' && n.sentiment) || '';
                                    const isBull = sentiment === 'BULLISH' || text.includes('📈') || text.includes('naik') || text.includes('rally') || text.includes('surge');
                                    const isBear = sentiment === 'BEARISH' || text.includes('📉') || text.includes('turun') || text.includes('drop') || text.includes('fall');
                                    return (
                                        <div key={i} className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                            <div className={`p-1.5 rounded-lg ${isBull ? 'bg-[var(--success)]/10' : isBear ? 'bg-[var(--danger)]/10' : 'bg-[var(--bg-hover)]'}`}>
                                                <Newspaper size={12} className={isBull ? 'text-[var(--success)]' : isBear ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'} />
                                            </div>
                                            <p className="flex-1 text-[10px] text-[var(--text-secondary)] font-bold">{text}</p>
                                            <span className={`text-[8px] font-black px-2 py-0.5 rounded shrink-0 ${isBull ? 'bg-[var(--success)]/10 text-[var(--success)]' : isBear ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>
                                                {isBull ? 'BULLISH' : isBear ? 'BEARISH' : 'NEUTRAL'}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Empty state if no result and not loading */}
            {!result && !loading && !error && (
                <div className="text-center py-20">
                    <BarChart2 size={40} className="mx-auto mb-4 text-[var(--text-dim)]" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Klik Refresh untuk memuat analisa sentimen real-time</p>
                </div>
            )}
        </div>
    );
}
