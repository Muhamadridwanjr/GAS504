import React, { useState, useEffect } from 'react';
import { Newspaper, RefreshCw, Calendar, TrendingUp, TrendingDown, Minus, Zap, Globe, Clock } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { callAIFeature } from '../services/api';

const BIAS_MAP = {
    bullish: { label: 'Bullish', color: 'text-green-400', bg: 'bg-green-400/10', border: 'border-green-400/20', icon: TrendingUp },
    bearish: { label: 'Bearish', color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/20', icon: TrendingDown },
    neutral: { label: 'Netral', color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/20', icon: Minus },
};


function ImpactBadge({ level }) {
    const map = { HIGH: 'bg-red-400/20 text-red-400', MEDIUM: 'bg-yellow-400/20 text-yellow-400', LOW: 'bg-gray-400/20 text-gray-400' };
    return <span className={`text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-wider ${map[level] || map.LOW}`}>{level}</span>;
}

export default function MarketBriefingView() {
    const { user } = useAuth();
    const [briefing, setBriefing] = useState(null);
    const [loading, setLoading] = useState(false);
    const [type, setType] = useState('daily');
    const [error, setError] = useState('');
    const [analysisContent, setAnalysisContent] = useState('');
    const [analysisLoading, setAnalysisLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('ai'); // 'ai' | 'weekly'

    const fetchBriefing = async () => {
        setError('');
        setLoading(true);
        try {
            const res = await callAIFeature('briefing', { type });
            setBriefing(res);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Gagal memuat briefing. Pastikan gas-strategy-core aktif.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => { fetchBriefing(); }, [type]);

    useEffect(() => {
        setAnalysisLoading(true);
        fetch('/terminal/content/analysis.md')
            .then(r => r.json())
            .then(d => setAnalysisContent(d.content || ''))
            .catch(() => setAnalysisContent(''))
            .finally(() => setAnalysisLoading(false));
    }, []);

    const biasInfo = briefing ? (BIAS_MAP[briefing.market_bias] || BIAS_MAP.neutral) : null;

    return (
        <div className="flex flex-col h-full overflow-hidden">
            {/* Tab switcher */}
            <div className="shrink-0 flex items-center gap-1 px-4 pt-4 pb-0">
                <button
                    onClick={() => setActiveTab('ai')}
                    className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'ai' ? 'bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/20' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}
                >🤖 AI Briefing</button>
                <button
                    onClick={() => setActiveTab('weekly')}
                    className={`px-4 py-1.5 rounded-lg text-xs font-bold transition-all ${activeTab === 'weekly' ? 'bg-[var(--accent-soft)] text-[var(--accent)] border border-[var(--accent)]/20' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}
                >📋 Weekly Brief</button>
            </div>

            {activeTab === 'ai' && (
                <div className="p-4 md:p-6 pb-24 md:pb-6 max-w-4xl mx-auto space-y-5 overflow-y-auto flex-1">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-xl bg-blue-400/10 border border-blue-400/20 flex items-center justify-center">
                                <Newspaper size={20} className="text-blue-400" />
                            </div>
                            <div>
                                <h2 className="text-lg font-black text-[var(--text-primary)]">AI Market Briefing</h2>
                                <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">10 cr / briefing · Premium+</p>
                            </div>
                        </div>
                        <button onClick={fetchBriefing} disabled={loading}
                            className="flex items-center gap-2 px-4 py-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-lg text-xs font-bold text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:border-[var(--text-dim)] transition-all disabled:opacity-50">
                            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
                            Refresh
                        </button>
                    </div>

                    {/* Type tabs */}
                    <div className="flex gap-2">
                        {['daily', 'weekly'].map(t => (
                            <button key={t} onClick={() => setType(t)}
                                className={`px-5 py-2 rounded-lg text-xs font-black uppercase tracking-wider transition-all ${type === t
                                    ? 'bg-[var(--accent)] text-black'
                                    : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--text-dim)]'}`}>
                                {t === 'daily' ? '📅 Harian' : '📊 Mingguan'}
                            </button>
                        ))}
                    </div>

                    {loading && (
                        <div className="flex flex-col items-center justify-center py-20 gap-3">
                            <div className="animate-spin rounded-full h-10 w-10 border-2 border-blue-400 border-t-transparent" />
                            <p className="text-xs text-[var(--text-dim)] font-bold">AI sedang menganalisa kondisi pasar...</p>
                        </div>
                    )}

                    {error && <p className="text-xs text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">{error}</p>}

                    {!loading && briefing && (
                        <div className="space-y-4">
                            {/* Hero card */}
                            <div className="bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-panel)] border border-[var(--border-color)] rounded-2xl p-6">
                                <div className="flex items-start justify-between gap-4 mb-4">
                                    <div className="flex-1">
                                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                                            <Clock size={11} className="text-[var(--text-dim)]" />
                                            <span className="text-[10px] text-[var(--text-dim)] font-bold">{briefing.date}</span>
                                            {briefing.time && <span className="text-[10px] text-[var(--accent)] font-black">· {briefing.time}</span>}
                                            {briefing.type === 'weekly' && <span className="text-[10px] bg-blue-400/15 text-blue-400 border border-blue-400/20 font-black px-2 py-0.5 rounded-full uppercase tracking-wider">Mingguan</span>}
                                            {briefing.type === 'daily' && <span className="text-[10px] bg-yellow-400/15 text-[var(--accent)] border border-yellow-400/20 font-black px-2 py-0.5 rounded-full uppercase tracking-wider">Harian</span>}
                                        </div>
                                        <h3 className="text-xl font-black text-[var(--text-primary)] leading-tight">{briefing.headline}</h3>
                                    </div>
                                    {biasInfo && (
                                        <div className={`shrink-0 flex flex-col items-center gap-1 px-4 py-3 rounded-xl border ${biasInfo.bg} ${biasInfo.border}`}>
                                            <biasInfo.icon size={18} className={biasInfo.color} />
                                            <span className={`text-[10px] font-black ${biasInfo.color}`}>{biasInfo.label}</span>
                                        </div>
                                    )}
                                </div>
                                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{briefing.macro_summary}</p>
                            </div>

                            {/* Key Events */}
                            {briefing.key_events?.length > 0 && (
                                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                                    <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <Calendar size={11} /> Event Penting Hari Ini
                                    </p>
                                    <div className="space-y-3">
                                        {briefing.key_events.map((ev, i) => (
                                            <div key={i} className="flex items-center gap-4 py-2 border-b border-[var(--border-color)] last:border-0">
                                                <span className="text-[10px] font-mono text-[var(--text-dim)] w-20 shrink-0">{ev.time}</span>
                                                <span className="text-xs font-bold text-[var(--text-primary)] flex-1">{ev.event}</span>
                                                <ImpactBadge level={ev.impact} />
                                                <div className="hidden sm:flex items-center gap-3 text-[10px] text-[var(--text-dim)] font-mono">
                                                    <span>F: {ev.forecast}</span>
                                                    <span>P: {ev.prev}</span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            {/* Pairs Outlook */}
                            {briefing.pairs_outlook?.length > 0 && (
                                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                                    <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-4 flex items-center gap-2">
                                        <Globe size={11} /> Outlook per Pair
                                    </p>
                                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                                        {briefing.pairs_outlook.map((p, i) => {
                                            const b = BIAS_MAP[p.bias] || BIAS_MAP.neutral;
                                            return (
                                                <div key={i} className={`rounded-xl border p-4 ${b.bg} ${b.border}`}>
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="text-xs font-black text-[var(--text-primary)]">{p.pair}</span>
                                                        <span className={`text-[9px] font-black uppercase ${b.color}`}>{b.label}</span>
                                                    </div>
                                                    <p className="text-[10px] text-[var(--text-dim)] leading-relaxed">{p.note}</p>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>
                            )}

                            {/* Smart Money View */}
                            <div className="bg-[var(--bg-card)] border border-[var(--accent)]/20 rounded-2xl p-5">
                                <p className="text-[10px] font-black text-[var(--accent)] uppercase tracking-widest mb-3 flex items-center gap-2">
                                    <Zap size={11} /> Smart Money View
                                </p>
                                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{briefing.smart_money_view}</p>
                            </div>

                            {/* Trading Advice */}
                            <div className="bg-green-400/5 border border-green-400/20 rounded-2xl p-5">
                                <p className="text-[10px] font-black text-green-400 uppercase tracking-widest mb-3">💡 Saran Trading AI</p>
                                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{briefing.trading_advice}</p>
                            </div>

                            <p className="text-[10px] text-[var(--text-dim)] text-center">
                                Dibuat oleh AI · {briefing.credit_cost} cr digunakan
                                {briefing.time && ` · ${briefing.time}`}
                                {briefing.from_cache && ' · dari cache'}
                            </p>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'weekly' && (
                <div className="p-4 md:p-6 pb-20 space-y-4 overflow-y-auto flex-1">
                    <div className="flex items-center justify-between mb-2">
                        <h2 className="text-lg font-black text-[var(--text-primary)] uppercase tracking-tight">📋 Weekly Market Brief</h2>
                        <a href="/editor" target="_blank" className="text-[10px] text-[var(--accent)] hover:underline font-bold">Edit ↗</a>
                    </div>
                    {analysisLoading ? (
                        <div className="text-center py-16 text-[var(--text-dim)] text-sm">Memuat analisis...</div>
                    ) : (
                        <div className="space-y-2">
                            {analysisContent.split('\n').map((line, i) => {
                                const trimmed = line.trim();
                                if (!trimmed || trimmed.startsWith('<!--')) return null;
                                if (trimmed.startsWith('## ')) return (
                                    <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-3 mt-4">
                                        <h2 className="text-sm font-black text-[var(--text-primary)] uppercase tracking-tight">{trimmed.slice(3)}</h2>
                                    </div>
                                );
                                if (trimmed.startsWith('### ')) return (
                                    <h3 key={i} className="text-xs font-bold text-[var(--accent)] pt-3 pb-1 border-b border-[var(--border-subtle)]">{trimmed.slice(4)}</h3>
                                );
                                if (trimmed.startsWith('---')) return <hr key={i} className="border-[var(--border-color)] my-2" />;
                                if (trimmed.startsWith('|')) {
                                    const cols = trimmed.split('|').filter(c => c.trim() && !c.trim().match(/^[-\s]+$/));
                                    if (cols.length === 0) return null;
                                    return (
                                        <div key={i} className="flex gap-2 text-[10px] font-mono border-b border-[var(--border-subtle)] py-1.5 px-1 hover:bg-[var(--bg-hover)] rounded">
                                            {cols.map((c, j) => <span key={j} className={`flex-1 ${j===1 ? (c.includes('🟢') ? 'text-[var(--success)]' : c.includes('🔴') ? 'text-[var(--danger)]' : 'text-[var(--text-primary)]') : 'text-[var(--text-secondary)]'}`}>{c.trim()}</span>)}
                                        </div>
                                    );
                                }
                                if (trimmed.startsWith('- ')) {
                                    const text = trimmed.slice(2).replace(/\*\*(.+?)\*\*/g, '<strong style="color:var(--text-primary)">$1</strong>');
                                    return <p key={i} className="text-xs text-[var(--text-secondary)] pl-3 border-l-2 border-[var(--border-subtle)] py-0.5 leading-relaxed" dangerouslySetInnerHTML={{ __html: `• ${text}` }} />;
                                }
                                if (trimmed.startsWith('*')) return <p key={i} className="text-[10px] text-[var(--text-dim)] italic">{trimmed.replace(/^\*+|\*+$/g, '')}</p>;
                                return <p key={i} className="text-xs text-[var(--text-secondary)] leading-relaxed">{trimmed}</p>;
                            })}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
