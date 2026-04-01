import React, { useState, useEffect } from 'react';
import { BrainCircuit, TrendingUp, TrendingDown, Minus, RefreshCw } from 'lucide-react';
import { callAIFeature } from '../services/api';
import PairSelector from './PairSelector';

const TIMEFRAMES = ['M5', 'M15', 'M30', 'H1', 'H4', 'D1'];

function BiasIcon({ bias }) {
    if (bias === 'BUY') return <TrendingUp size={14} className="text-[var(--success)]" />;
    if (bias === 'SELL') return <TrendingDown size={14} className="text-[var(--danger)]" />;
    return <Minus size={14} className="text-[var(--text-dim)]" />;
}

function StrengthBar({ value, bias }) {
    const color = bias === 'BUY' ? 'var(--success)' : bias === 'SELL' ? 'var(--danger)' : 'var(--text-dim)';
    return (
        <div className="w-full bg-[var(--bg-hover)] rounded-full h-1.5">
            <div className="h-1.5 rounded-full transition-all duration-500" style={{ width: `${value || 0}%`, backgroundColor: color }} />
        </div>
    );
}

export default function MultiTFView() {
    const [selectedPair, setSelectedPair] = useState('XAUUSD');
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const load = async () => {
        setLoading(true);
        setError('');
        try {
            const res = await callAIFeature('technical', { pair: selectedPair, timeframe: 'multi' });
            setResult(res);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Gagal memuat analisa. Pastikan EA MT5 aktif.');
            setResult(null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { load(); }, [selectedPair]);

    // Normalize multi-TF data from API response
    const tfData = result?.timeframes || result?.tf_analysis || result?.multi_tf || result?.timeframe_data || {};
    const smcZones = result?.smc_zones || result?.zones || result?.key_levels || [];
    const overallBias = result?.bias || result?.recommendation || result?.signal?.type || result?.overall_bias || 'NEUTRAL';
    const signal = result?.signal || null;

    const bullCount = TIMEFRAMES.filter(tf => (tfData[tf]?.bias || tfData[tf]?.signal || '').includes('BUY')).length;
    const bearCount = TIMEFRAMES.filter(tf => (tfData[tf]?.bias || tfData[tf]?.signal || '').includes('SELL')).length;
    const hasTfData = Object.keys(tfData).length > 0;

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
                    <PairSelector value={selectedPair} onChange={setSelectedPair} label="" />
                    <button onClick={load} disabled={loading}
                        className="flex items-center gap-2 bg-[var(--accent)] text-black px-4 py-2 rounded-lg text-xs font-black hover:opacity-90 transition-opacity disabled:opacity-50">
                        <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                        Analisa
                    </button>
                </div>
            </div>

            {error && (
                <div className="rounded-xl p-3 border" style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.2)' }}>
                    <p className="text-xs font-black text-red-400">⚠️ {error}</p>
                </div>
            )}

            {/* Overall Bias Card */}
            <div className={`p-5 rounded-xl border flex items-center gap-6 ${overallBias === 'BUY' ? 'bg-[var(--success)]/5 border-[var(--success)]/30' : overallBias === 'SELL' ? 'bg-[var(--danger)]/5 border-[var(--danger)]/30' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                <div className={`p-4 rounded-xl ${overallBias === 'BUY' ? 'bg-[var(--success)]/10' : overallBias === 'SELL' ? 'bg-[var(--danger)]/10' : 'bg-[var(--bg-panel)]'}`}>
                    {overallBias === 'BUY' ? <TrendingUp size={32} className="text-[var(--success)]" /> : overallBias === 'SELL' ? <TrendingDown size={32} className="text-[var(--danger)]" /> : <Minus size={32} className="text-[var(--text-dim)]" />}
                </div>
                <div>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold mb-1">Bias Keseluruhan · {selectedPair}</p>
                    <p className={`text-3xl font-display font-black ${overallBias === 'BUY' ? 'text-[var(--success)]' : overallBias === 'SELL' ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'}`}>
                        {loading ? '...' : overallBias}
                    </p>
                    {hasTfData && (
                        <p className="text-xs text-[var(--text-dim)] mt-1">{bullCount}/{TIMEFRAMES.length} TF Bullish · {bearCount}/{TIMEFRAMES.length} TF Bearish</p>
                    )}
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
            {loading ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                    {TIMEFRAMES.map(tf => (
                        <div key={tf} className="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)] animate-pulse">
                            <div className="text-[10px] font-black text-[var(--text-dim)] uppercase mb-3">{tf}</div>
                            <div className="h-3 bg-[var(--bg-panel)] rounded mb-2" />
                            <div className="h-1.5 bg-[var(--bg-panel)] rounded" />
                        </div>
                    ))}
                </div>
            ) : hasTfData ? (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                    {TIMEFRAMES.map(tf => {
                        const d = tfData[tf] || {};
                        const bias = d.bias || d.signal || d.recommendation || 'NEUTRAL';
                        const strength = d.strength || d.confidence || d.score || 0;
                        const rsi = d.rsi || d.rsi_value || '—';
                        const ema = d.ema || d.ema_position || '—';
                        const macd = d.macd || d.macd_signal || '—';
                        return (
                            <div key={tf} className={`p-4 rounded-xl border ${bias === 'BUY' ? 'bg-[var(--bg-card)] border-[var(--success)]/20' : bias === 'SELL' ? 'bg-[var(--bg-card)] border-[var(--danger)]/20' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                                <div className="flex items-center justify-between mb-3">
                                    <span className="text-[10px] font-black text-[var(--text-dim)] uppercase">{tf}</span>
                                    <BiasIcon bias={bias} />
                                </div>
                                <p className={`text-sm font-black mb-2 ${bias === 'BUY' ? 'text-[var(--success)]' : bias === 'SELL' ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'}`}>{bias}</p>
                                <StrengthBar value={strength} bias={bias} />
                                <p className="text-[9px] text-[var(--text-dim)] mt-2">{strength}% strength</p>
                                <div className="mt-3 space-y-1">
                                    <div className="flex justify-between text-[9px]">
                                        <span className="text-[var(--text-dim)]">RSI</span>
                                        <span className="font-bold text-[var(--text-secondary)]">{rsi}</span>
                                    </div>
                                    <div className="flex justify-between text-[9px]">
                                        <span className="text-[var(--text-dim)]">EMA</span>
                                        <span className="font-bold text-[var(--text-secondary)]">{ema}</span>
                                    </div>
                                    <div className="flex justify-between text-[9px]">
                                        <span className="text-[var(--text-dim)]">MACD</span>
                                        <span className="font-bold text-[var(--text-secondary)]">{macd}</span>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            ) : (
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
                    {TIMEFRAMES.map(tf => (
                        <div key={tf} className="p-4 rounded-xl border border-[var(--border-color)] bg-[var(--bg-card)]">
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-[10px] font-black text-[var(--text-dim)] uppercase">{tf}</span>
                                <Minus size={14} className="text-[var(--text-dim)] opacity-30" />
                            </div>
                            <p className="text-sm font-black mb-2 text-[var(--text-dim)]">—</p>
                            <StrengthBar value={0} bias="NEUTRAL" />
                            <p className="text-[9px] text-[var(--text-dim)] mt-2">Klik Analisa</p>
                        </div>
                    ))}
                </div>
            )}

            {/* SMC Zones */}
            <div>
                <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Zona Smart Money · {selectedPair}</p>
                {smcZones.length > 0 ? (
                    <div className="space-y-2">
                        {smcZones.map((z, i) => {
                            const color = z.color || (z.type?.includes('BUY') || z.type === 'OB' || z.type === 'BSL' || z.type === 'BOS' ? 'var(--success)' : z.type === 'SSL' || z.type === 'OB_BEAR' ? 'var(--danger)' : 'var(--accent)');
                            return (
                                <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-[var(--text-dim)] transition-all">
                                    <div className="w-10 h-10 rounded-lg flex items-center justify-center font-black text-[10px] shrink-0" style={{ backgroundColor: `${color}15`, color }}>{z.type}</div>
                                    <div className="flex-1 min-w-0">
                                        <p className="text-xs font-bold text-[var(--text-primary)]">{z.label || z.description || z.type}</p>
                                        <p className="text-[10px] text-[var(--text-dim)]">{z.price || z.level || z.range || '—'}</p>
                                    </div>
                                    <span className="text-[8px] font-bold px-2 py-1 rounded uppercase" style={{ backgroundColor: `${color}15`, color }}>{z.status || z.state || '—'}</span>
                                    <span className="text-[9px] text-[var(--text-dim)] font-bold w-8 text-right">{z.tf || z.timeframe || '—'}</span>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="flex items-center justify-center py-10 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl text-[var(--text-dim)]">
                        <div className="text-center">
                            <BrainCircuit size={24} className="mx-auto mb-2 opacity-20" />
                            <p className="text-xs font-bold">{loading ? 'Memuat zona SMC...' : 'Klik Analisa untuk memuat zona Smart Money'}</p>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
