import React, { useState } from 'react';
import { Layers, RefreshCw, CheckCircle, XCircle, TrendingUp, TrendingDown, Minus, Zap, BarChart2, Globe, Brain, Cpu, Clock, Crosshair, AlertTriangle } from 'lucide-react';
import { callAIFeature } from '../services/api';
import { PAIRS as ALL_PAIRS } from '../constants';
import PairSelector from './PairSelector';
import StyleSelector, { STYLE_MATRIX } from './StyleSelector';

function ScoreBar({ label, score, color, icon: Icon }) {
    return (
        <div className="space-y-2">
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <Icon size={12} className={color} />
                    <span className="text-xs font-bold text-[var(--text-secondary)]">{label}</span>
                </div>
                <span className={`text-sm font-black font-mono ${color}`}>{score}</span>
            </div>
            <div className="h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                <div className={`h-full rounded-full transition-all duration-700 ${score >= 70 ? 'bg-green-400' : score >= 40 ? 'bg-yellow-400' : 'bg-red-400'}`}
                    style={{ width: `${score}%` }} />
            </div>
        </div>
    );
}

function ConfluenceMeter({ score }) {
    const color = score >= 70 ? '#4ade80' : score >= 40 ? '#facc15' : '#f87171';
    const label = score >= 70 ? 'KUAT' : score >= 40 ? 'MODERAT' : 'LEMAH';
    const r = 55, c = 2 * Math.PI * r;
    const filled = (score / 100) * c;
    return (
        <div className="flex flex-col items-center gap-3">
            <svg width="140" height="140" viewBox="0 0 140 140">
                <circle cx="70" cy="70" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="10" />
                <circle cx="70" cy="70" r={r} fill="none" stroke={color} strokeWidth="10"
                    strokeDasharray={`${filled} ${c}`} strokeLinecap="round"
                    transform="rotate(-90 70 70)" style={{ transition: 'stroke-dasharray 1s ease' }} />
                <text x="70" y="65" textAnchor="middle" fill={color} fontSize="28" fontWeight="bold">{score}</text>
                <text x="70" y="82" textAnchor="middle" fill={color} fontSize="10" fontWeight="bold">{label}</text>
            </svg>
            <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Confluence Score</p>
        </div>
    );
}


export default function HybridSystemView() {
    const [pair, setPair] = useState('XAUUSD');
    const [style, setStyle] = useState('intraday');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const primaryTF = STYLE_MATRIX[style]?.tfs[2] || 'H1';

    const handleAnalyze = async () => {
        setError('');
        setLoading(true);
        try {
            const res = await callAIFeature('hybrid', { pair, style, timeframe: primaryTF });
            setResult(res);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Gagal memuat analisa. Pastikan EA MT5 aktif.');
        } finally {
            setLoading(false);
        }
    };

    const recColor = result?.recommendation === 'BUY' ? 'text-green-400' : result?.recommendation === 'SELL' ? 'text-red-400' : 'text-yellow-400';

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-6 max-w-4xl mx-auto space-y-5">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center">
                    <Layers size={20} className="text-yellow-400" />
                </div>
                <div>
                    <h2 className="text-lg font-black text-[var(--text-primary)]">Hybrid System AI</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">8 cr / analisa · TA + FA + Sentiment</p>
                </div>
            </div>

            {/* Controls */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5 space-y-4">
                <div className="grid grid-cols-1 gap-4">
                    <PairSelector value={pair} onChange={setPair} label="Pair / Aset" />
                </div>
                {/* Style Selector */}
                <StyleSelector value={style} onChange={setStyle} showMatrix={true} />
                <button onClick={handleAnalyze} disabled={loading}
                    className="w-full bg-[var(--accent)] text-black font-black text-sm py-3 rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2">
                    {loading ? <RefreshCw size={14} className="animate-spin" /> : <Layers size={14} />}
                    {loading ? 'Menganalisa Hybrid AI...' : `Analisa Hybrid — ${pair} · ${style} (8 cr)`}
                </button>
            </div>

            {error && <p className="text-xs text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">{error}</p>}

            {result && (
                <div className="space-y-4">
                    {/* Confluence Score */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6">
                        <div className="flex flex-col md:flex-row items-center gap-8">
                            <ConfluenceMeter score={result.confluence_score} />
                            <div className="flex-1 space-y-4 w-full">
                                <ScoreBar label="Technical Analysis" score={result.ta_score} color="text-blue-400" icon={BarChart2} />
                                <ScoreBar label="Fundamental" score={result.fa_score} color="text-purple-400" icon={Globe} />
                                <ScoreBar label="Sentiment" score={result.sentiment_score} color="text-orange-400" icon={Brain} />
                                {result.smc_score != null && (
                                    <ScoreBar label="SMC Structure" score={result.smc_score} color="text-violet-400" icon={Cpu} />
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Signal breakdown */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                        <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-4">Breakdown Sinyal</p>
                        <div className="space-y-3">
                            {result.signals?.map((s, i) => {
                                const isUp = s.signal === 'BUY', isDown = s.signal === 'SELL';
                                return (
                                    <div key={i} className="flex items-start gap-3 p-3 bg-[var(--bg-panel)] rounded-xl">
                                        <div className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 ${isUp ? 'bg-green-400/10' : isDown ? 'bg-red-400/10' : 'bg-yellow-400/10'}`}>
                                            {isUp ? <TrendingUp size={14} className="text-green-400" /> : isDown ? <TrendingDown size={14} className="text-red-400" /> : <Minus size={14} className="text-yellow-400" />}
                                        </div>
                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center justify-between mb-1">
                                                <span className="text-xs font-black text-[var(--text-primary)]">{s.source}</span>
                                                <span className={`text-[9px] font-black px-2 py-0.5 rounded uppercase ${isUp ? 'bg-green-400/20 text-green-400' : isDown ? 'bg-red-400/20 text-red-400' : 'bg-yellow-400/20 text-yellow-400'}`}>{s.signal}</span>
                                            </div>
                                            <p className="text-[10px] text-[var(--text-dim)]">{s.detail}</p>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* SMC Engine Detail */}
                    {result.smc_available && result.smc_data && (
                        <div className="bg-[var(--bg-card)] border border-purple-400/20 rounded-2xl overflow-hidden">
                            <div className="px-5 py-3 border-b border-purple-400/15 flex items-center gap-2"
                                style={{ background: 'rgba(168,85,247,0.04)' }}>
                                <Cpu size={12} className="text-purple-400" />
                                <span className="text-[9px] font-black text-purple-400 uppercase tracking-wider">Smart Money Concept (SMC Engine)</span>
                                <span className="ml-auto text-[8px] font-black px-2 py-0.5 rounded bg-purple-400/10 text-purple-400 border border-purple-400/20">
                                    Score {result.smc_data.smc_score || 0}/100
                                </span>
                            </div>
                            <div className="p-4 flex flex-wrap gap-2">
                                {result.smc_data.bias && result.smc_data.bias !== 'NEUTRAL' && (
                                    <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border text-[9px] font-black ${result.smc_data.bias === 'BULLISH' ? 'bg-emerald-400/10 border-emerald-400/25 text-emerald-400' : 'bg-red-400/10 border-red-400/25 text-red-400'}`}>
                                        {result.smc_data.bias === 'BULLISH' ? <TrendingUp size={9} /> : <TrendingDown size={9} />}
                                        {result.smc_data.bias}
                                    </span>
                                )}
                                {result.smc_data.bos && <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border bg-emerald-400/10 border-emerald-400/25 text-[9px] font-black text-emerald-400"><CheckCircle size={9} /> BOS</span>}
                                {result.smc_data.choch && <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border bg-orange-400/10 border-orange-400/25 text-[9px] font-black text-orange-400"><AlertTriangle size={9} /> CHoCH</span>}
                                {result.smc_data.ote_zone && <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border bg-yellow-400/10 border-yellow-400/25 text-[9px] font-black text-yellow-400"><Crosshair size={9} /> OTE Zone</span>}
                                {result.smc_data.kill_zone && <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border bg-red-400/10 border-red-400/25 text-[9px] font-black text-red-400"><Clock size={9} /> Kill Zone</span>}
                                {result.smc_data.amd_phase && (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border bg-[var(--bg-panel)] border-[var(--border-color)] text-[9px] font-black">
                                        <Cpu size={9} className="text-[var(--accent)]" />
                                        <span className="text-[var(--text-dim)]">AMD:</span>
                                        <span className="text-[var(--accent)]">{result.smc_data.amd_phase}</span>
                                    </span>
                                )}
                                {result.smc_data.session && (
                                    <span className="inline-flex items-center gap-1 px-3 py-1.5 rounded-lg border bg-blue-400/10 border-blue-400/25 text-[9px] font-black text-blue-400">
                                        🕐 {result.smc_data.session}
                                    </span>
                                )}
                                {result.setup_type && result.setup_type !== 'Unknown' && (
                                    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg border bg-purple-400/10 border-purple-400/25 text-[9px] font-black text-purple-400">
                                        <Crosshair size={9} /> {result.setup_type}
                                    </span>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Trade setup */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                        <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-4 flex items-center gap-2">
                            <Zap size={11} /> Trade Setup — {result.pair} {result.timeframe}
                        </p>
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
                            {[
                                { label: 'Entry', value: result.entry?.toFixed(2) },
                                { label: 'Stop Loss', value: result.sl?.toFixed(2), color: 'text-red-400' },
                                { label: 'TP1', value: result.tp1?.toFixed(2), color: 'text-green-400' },
                                { label: 'TP2', value: result.tp2?.toFixed(2), color: 'text-green-400' },
                            ].map((f, i) => (
                                <div key={i} className="bg-[var(--bg-panel)] rounded-xl p-3 text-center">
                                    <p className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1">{f.label}</p>
                                    <p className={`text-sm font-black font-mono ${f.color || 'text-[var(--text-primary)]'}`}>{f.value || '-'}</p>
                                </div>
                            ))}
                        </div>
                        <div className="flex items-center justify-between">
                            <span className={`text-xl font-black ${recColor}`}>{result.recommendation}</span>
                            <span className="text-xs font-bold text-[var(--text-dim)]">RR: {result.rr}</span>
                        </div>
                    </div>

                    {/* AI Decision */}
                    <div className="bg-[var(--accent)]/5 border border-[var(--accent)]/20 rounded-2xl p-5">
                        <p className="text-[10px] font-black text-[var(--accent)] uppercase tracking-widest mb-2 flex items-center gap-2">
                            <Zap size={11} /> AI Decision
                        </p>
                        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{result.ai_decision}</p>
                    </div>
                </div>
            )}
        </div>
    );
}
