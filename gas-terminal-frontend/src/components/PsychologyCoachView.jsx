import React, { useState } from 'react';
import { Brain, AlertTriangle, TrendingDown, Flame, Zap, CheckCircle, XCircle, RefreshCw, BarChart2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { callAIFeature } from '../services/api';

const EMOTION_LABELS = {
    calm:      { label: 'Tenang', color: 'text-green-400', bg: 'bg-green-400/10', border: 'border-green-400/30' },
    nervous:   { label: 'Gugup', color: 'text-yellow-400', bg: 'bg-yellow-400/10', border: 'border-yellow-400/30' },
    fomo:      { label: 'FOMO', color: 'text-orange-400', bg: 'bg-orange-400/10', border: 'border-orange-400/30' },
    revenge:   { label: 'Revenge', color: 'text-red-400', bg: 'bg-red-400/10', border: 'border-red-400/30' },
    greedy:    { label: 'Serakah', color: 'text-purple-400', bg: 'bg-purple-400/10', border: 'border-purple-400/30' },
};

const RISK_OPTIONS = [
    { id: 'fomo', label: '📈 FOMO — takut ketinggalan momen' },
    { id: 'revenge', label: '😤 Revenge trade setelah loss' },
    { id: 'oversize', label: '💣 Oversize lot — modal terlalu besar' },
    { id: 'noplan', label: '🎲 Entry tanpa trading plan' },
    { id: 'greedy', label: '💰 TP terlalu jauh / tidak mau cut' },
];

function ScoreRing({ score }) {
    const color = score >= 70 ? '#4ade80' : score >= 40 ? '#facc15' : '#f87171';
    const r = 38, c = 2 * Math.PI * r;
    const filled = (score / 100) * c;
    return (
        <svg width="100" height="100" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(255,255,255,0.05)" strokeWidth="8" />
            <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
                strokeDasharray={`${filled} ${c}`} strokeLinecap="round"
                transform="rotate(-90 50 50)" style={{ transition: 'stroke-dasharray 0.8s ease' }} />
            <text x="50" y="55" textAnchor="middle" fill={color} fontSize="20" fontWeight="bold">{score}</text>
        </svg>
    );
}

export default function PsychologyCoachView() {
    const { user } = useAuth();
    const [step, setStep] = useState('check'); // check | result
    const [selectedRisks, setSelectedRisks] = useState([]);
    const [currentEmotion, setCurrentEmotion] = useState('');
    const [recentPnL, setRecentPnL] = useState('');
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState('');

    const toggleRisk = (id) => {
        setSelectedRisks(prev =>
            prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]
        );
    };

    const handleAnalyze = async () => {
        if (!currentEmotion) { setError('Pilih kondisi emosi kamu dulu.'); return; }
        setError('');
        setLoading(true);
        try {
            const res = await callAIFeature('psychology', {
                emotion: currentEmotion,
                risks: selectedRisks,
                recent_pnl: recentPnL,
            });
            setResult(res);
            setStep('result');
        } catch (err) {
            setError(err?.response?.data?.detail || 'Analisa gagal. Coba lagi.');
        } finally {
            setLoading(false);
        }
    };

    const reset = () => { setStep('check'); setResult(null); setSelectedRisks([]); setCurrentEmotion(''); setRecentPnL(''); };

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-6 max-w-3xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-purple-400/10 border border-purple-400/20 flex items-center justify-center">
                    <Brain size={20} className="text-purple-400" />
                </div>
                <div>
                    <h2 className="text-lg font-black text-[var(--text-primary)]">Psychology Coach AI</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">5 cr / analisa · Premium+</p>
                </div>
            </div>

            {step === 'check' && (
                <div className="space-y-5">
                    {/* Emotion selector */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                        <p className="text-xs font-black text-[var(--text-dim)] uppercase tracking-widest mb-4">Bagaimana kondisi emosi kamu sekarang?</p>
                        <div className="flex flex-wrap gap-2">
                            {Object.entries(EMOTION_LABELS).map(([k, v]) => (
                                <button key={k} onClick={() => setCurrentEmotion(k)}
                                    className={`px-4 py-2 rounded-xl border text-xs font-bold transition-all ${currentEmotion === k
                                        ? `${v.bg} ${v.border} ${v.color}`
                                        : 'bg-[var(--bg-panel)] border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--text-dim)]'
                                    }`}>
                                    {v.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Risk checklist */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                        <p className="text-xs font-black text-[var(--text-dim)] uppercase tracking-widest mb-4">Deteksi perilaku berbahaya (pilih yang relevan)</p>
                        <div className="space-y-2">
                            {RISK_OPTIONS.map(r => (
                                <button key={r.id} onClick={() => toggleRisk(r.id)}
                                    className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl border text-sm font-bold transition-all text-left ${selectedRisks.includes(r.id)
                                        ? 'bg-red-400/10 border-red-400/30 text-red-400'
                                        : 'bg-[var(--bg-panel)] border-[var(--border-color)] text-[var(--text-secondary)] hover:border-[var(--text-dim)]'
                                    }`}>
                                    <div className={`w-4 h-4 rounded border flex items-center justify-center shrink-0 ${selectedRisks.includes(r.id) ? 'border-red-400 bg-red-400/20' : 'border-[var(--border-color)]'}`}>
                                        {selectedRisks.includes(r.id) && <CheckCircle size={10} className="text-red-400" />}
                                    </div>
                                    {r.label}
                                </button>
                            ))}
                        </div>
                    </div>

                    {/* Recent PnL */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                        <p className="text-xs font-black text-[var(--text-dim)] uppercase tracking-widest mb-3">PnL terakhir (opsional)</p>
                        <input type="text" value={recentPnL} onChange={e => setRecentPnL(e.target.value)}
                            placeholder="Contoh: -$120 atau +$340"
                            className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]" />
                    </div>

                    {error && <p className="text-xs text-red-400 bg-red-400/10 border border-red-400/20 rounded-lg px-3 py-2">{error}</p>}

                    <button onClick={handleAnalyze} disabled={loading}
                        className="w-full bg-purple-500 hover:bg-purple-400 text-white font-black text-sm py-3 rounded-xl transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2">
                        {loading ? <RefreshCw size={14} className="animate-spin" /> : <Brain size={14} />}
                        {loading ? 'Menganalisa...' : 'Analisa Psikologi (5 cr)'}
                    </button>
                </div>
            )}

            {step === 'result' && result && (
                <div className="space-y-5">
                    {/* Score */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 flex flex-col items-center gap-4">
                        <ScoreRing score={result.emotion_score ?? 72} />
                        <div className="text-center">
                            <p className="text-xs font-black text-[var(--text-dim)] uppercase tracking-widest mb-1">Emotion Score</p>
                            <p className={`text-sm font-bold ${result.emotion_score >= 70 ? 'text-green-400' : result.emotion_score >= 40 ? 'text-yellow-400' : 'text-red-400'}`}>
                                {result.emotion_score >= 70 ? '✅ Kondisi Trading Bagus' : result.emotion_score >= 40 ? '⚠️ Hati-hati — Level Waspada' : '🚫 Jangan Trade Dulu!'}
                            </p>
                        </div>
                    </div>

                    {/* Detected risks */}
                    {result.detected_risks?.length > 0 && (
                        <div className="bg-red-400/5 border border-red-400/20 rounded-2xl p-5">
                            <p className="text-xs font-black text-red-400 uppercase tracking-widest mb-3 flex items-center gap-2">
                                <AlertTriangle size={12} /> Risiko Terdeteksi
                            </p>
                            <div className="space-y-2">
                                {result.detected_risks.map((r, i) => (
                                    <div key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                        <XCircle size={12} className="text-red-400 mt-0.5 shrink-0" />
                                        {r}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Mindset check */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5">
                        <p className="text-xs font-black text-[var(--text-dim)] uppercase tracking-widest mb-3 flex items-center gap-2">
                            <Brain size={12} /> Mindset Check AI
                        </p>
                        <p className="text-sm text-[var(--text-secondary)] leading-relaxed">{result.mindset_advice || 'Pastikan kamu trade sesuai plan. Ikuti rule, bukan emosi.'}</p>
                    </div>

                    {/* Action plan */}
                    {result.action_plan?.length > 0 && (
                        <div className="bg-green-400/5 border border-green-400/20 rounded-2xl p-5">
                            <p className="text-xs font-black text-green-400 uppercase tracking-widest mb-3">Action Plan</p>
                            <div className="space-y-2">
                                {result.action_plan.map((a, i) => (
                                    <div key={i} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                                        <CheckCircle size={12} className="text-green-400 mt-0.5 shrink-0" />
                                        {a}
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Entry verdict */}
                    <div className={`rounded-2xl p-5 border ${result.safe_to_trade ? 'bg-green-400/10 border-green-400/30' : 'bg-red-400/10 border-red-400/30'}`}>
                        <div className="flex items-center gap-3">
                            {result.safe_to_trade
                                ? <CheckCircle size={20} className="text-green-400" />
                                : <XCircle size={20} className="text-red-400" />}
                            <div>
                                <p className={`text-sm font-black ${result.safe_to_trade ? 'text-green-400' : 'text-red-400'}`}>
                                    {result.safe_to_trade ? 'Aman untuk entry ✅' : 'Tunda trading dulu 🚫'}
                                </p>
                                <p className="text-xs text-[var(--text-dim)]">{result.verdict_reason}</p>
                            </div>
                        </div>
                    </div>

                    <button onClick={reset}
                        className="w-full border border-[var(--border-color)] text-[var(--text-secondary)] font-bold text-sm py-3 rounded-xl hover:bg-[var(--bg-hover)] transition-colors flex items-center justify-center gap-2">
                        <RefreshCw size={14} /> Analisa Ulang
                    </button>
                </div>
            )}
        </div>
    );
}
