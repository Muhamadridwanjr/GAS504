import React, { useState } from 'react';
import { Activity, Play, TrendingUp, TrendingDown, BarChart2, Award, RefreshCw } from 'lucide-react';
import { PAIRS } from '../constants';
import { callAIFeature } from '../services/api';
import PairSelector from './PairSelector';

const TF_OPTIONS = ['M15', 'H1', 'H4', 'D1'];
const LOOKBACK_OPTIONS = [
    { label: '100 Candles', value: 100 },
    { label: '200 Candles', value: 200 },
    { label: '300 Candles', value: 300 },
    { label: '500 Candles', value: 500 },
];
const RR_OPTIONS = ['1.5', '2.0', '2.5', '3.0', '4.0'];

export default function BacktestView() {
    const [pair, setPair] = useState('XAUUSD');
    const [timeframe, setTimeframe] = useState('H1');
    const [lookback, setLookback] = useState(300);
    const [rrRatio, setRrRatio] = useState('2.0');
    const [running, setRunning] = useState(false);
    const [results, setResults] = useState(null);
    const [error, setError] = useState(null);

    const run = async () => {
        setRunning(true);
        setResults(null);
        setError(null);
        try {
            const res = await callAIFeature('backtesting', {
                pair,
                timeframe,
                lookback,
                rr_ratio: parseFloat(rrRatio),
            });
            setResults(res);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Backtest gagal. Pastikan EA MT5 aktif dan mengirim data historis.');
        } finally {
            setRunning(false);
        }
    };

    // Normalize result fields from any response shape
    const r = results || {};
    const totalTrades   = r.total_trades   ?? r.totalTrades   ?? 0;
    const winRate       = r.win_rate       ?? r.winRate       ?? 0;
    const profitFactor  = r.profit_factor  ?? r.profitFactor  ?? 0;
    const netProfit     = r.net_profit     ?? r.netProfit     ?? r.profit ?? 0;
    const maxDrawdown   = r.max_drawdown   ?? r.maxDrawdown   ?? 0;
    const avgRR         = r.avg_rr         ?? r.avgRR         ?? r.average_rr ?? 0;
    const avgWin        = r.avg_win        ?? r.avgWin        ?? 0;
    const avgLoss       = r.avg_loss       ?? r.avgLoss       ?? 0;
    const sharpe        = r.sharpe         ?? r.sharpe_ratio  ?? 0;
    const equityCurve   = r.equity_curve   ?? r.equity        ?? [];
    const monthlyReturns = r.monthly_returns ?? r.monthly ?? [];
    const aiSummary     = r.ai_summary     ?? r.summary       ?? r.analysis ?? '';

    const maxEq = equityCurve.length > 1 ? Math.max(...equityCurve.map(p => typeof p === 'object' ? (p.value || p.equity || 0) : p)) : 0;
    const minEq = equityCurve.length > 1 ? Math.min(...equityCurve.map(p => typeof p === 'object' ? (p.value || p.equity || 0) : p)) : 0;
    const eqValues = equityCurve.map(p => typeof p === 'object' ? (p.value || p.equity || 0) : p);
    const maxMonth = monthlyReturns.length > 0 ? Math.max(...monthlyReturns.map(m => Math.abs(typeof m === 'object' ? (m.pct || m.return || m.p || 0) : m))) : 1;

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Activity size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Mesin Backtest</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">AI Backtest Historis Real dari MT5 · 20 Kredit</p>
                </div>
                <span className="text-[8px] bg-[var(--accent)] text-black font-black px-2 py-0.5 rounded uppercase ml-2">Ultimate</span>
            </div>

            {/* Config Panel */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Pair */}
                <PairSelector value={pair} onChange={setPair} label="Pair / Aset" />

                {/* Timeframe */}
                <div>
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Timeframe</p>
                    <div className="flex gap-1 flex-wrap">
                        {TF_OPTIONS.map(tf => (
                            <button key={tf} onClick={() => setTimeframe(tf)}
                                className={`px-3 py-2 rounded-xl text-[10px] font-black border transition-all ${timeframe === tf
                                    ? 'bg-[var(--accent)] text-black border-[var(--accent)]'
                                    : 'bg-[var(--bg-panel)] text-[var(--text-dim)] border-[var(--border-color)] hover:text-[var(--text-primary)]'}`}>
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Lookback */}
                <div>
                    <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Jumlah Candle</p>
                    <div className="flex gap-1 flex-wrap">
                        {LOOKBACK_OPTIONS.map(o => (
                            <button key={o.value} onClick={() => setLookback(o.value)}
                                className={`px-2.5 py-2 rounded-xl text-[9px] font-black border transition-all ${lookback === o.value
                                    ? 'bg-[var(--accent)] text-black border-[var(--accent)]'
                                    : 'bg-[var(--bg-panel)] text-[var(--text-dim)] border-[var(--border-color)] hover:text-[var(--text-primary)]'}`}>
                                {o.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* R:R + Run */}
                <div className="space-y-3">
                    <div>
                        <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">Target R:R Ratio</p>
                        <div className="flex gap-1 flex-wrap">
                            {RR_OPTIONS.map(rr => (
                                <button key={rr} onClick={() => setRrRatio(rr)}
                                    className={`px-2.5 py-2 rounded-xl text-[9px] font-black border transition-all ${rrRatio === rr
                                        ? 'bg-[var(--accent)] text-black border-[var(--accent)]'
                                        : 'bg-[var(--bg-panel)] text-[var(--text-dim)] border-[var(--border-color)]'}`}>
                                    {rr}
                                </button>
                            ))}
                        </div>
                    </div>
                    <button onClick={run} disabled={running}
                        className="w-full flex items-center justify-center gap-2 font-black px-4 py-2.5 rounded-xl text-xs disabled:opacity-50 transition-all hover:scale-[1.02]"
                        style={{ background: running ? 'var(--bg-panel)' : 'var(--grad-gold)', color: running ? 'var(--text-dim)' : '#000', border: running ? '1px solid var(--border-color)' : 'none' }}>
                        {running ? (
                            <><RefreshCw size={12} className="animate-spin" /> AI Memproses...</>
                        ) : (
                            <><Play size={12} /> Jalankan Backtest · 20cr</>
                        )}
                    </button>
                </div>
            </div>

            {/* Progress bar */}
            {running && (
                <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--accent)]/30">
                    <div className="flex justify-between text-[10px] font-bold mb-2">
                        <span className="text-[var(--text-dim)]">AI menganalisa {lookback} candle {pair} {timeframe}...</span>
                        <span className="text-[var(--accent)]">Memproses...</span>
                    </div>
                    <div className="h-1.5 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                        <div className="h-full bg-[var(--accent)] rounded-full animate-pulse w-3/4" />
                    </div>
                </div>
            )}

            {/* Error */}
            {error && (
                <div className="rounded-xl p-4 border" style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.25)' }}>
                    <p className="text-xs font-black text-red-400">⚠️ {error}</p>
                    <p className="text-[9px] text-red-400/70 mt-1">Pastikan EA MT5 aktif dan mengirim data historis ke gas-strategy-core.</p>
                </div>
            )}

            {/* Results */}
            {results && (
                <>
                    {/* AI Summary */}
                    {aiSummary && (
                        <div className="rounded-xl p-4 border" style={{ background: 'rgba(250,200,21,0.03)', borderColor: 'rgba(250,200,21,0.15)' }}>
                            <p className="text-[9px] font-black uppercase tracking-widest mb-2" style={{ color: '#fac815' }}>🤖 AI Backtest Summary</p>
                            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{aiSummary}</p>
                        </div>
                    )}

                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        {[
                            { label: 'Win Rate',       value: `${Number(winRate).toFixed(1)}%`,          icon: <Award size={16} />,      color: 'var(--success)' },
                            { label: 'Profit Factor',  value: Number(profitFactor).toFixed(2),            icon: <TrendingUp size={16} />, color: 'var(--success)' },
                            { label: 'Net Profit',     value: `$${Number(netProfit).toLocaleString()}`,   icon: <TrendingUp size={16} />, color: 'var(--success)' },
                            { label: 'Max Drawdown',   value: `${Number(maxDrawdown).toFixed(1)}%`,       icon: <TrendingDown size={16} />, color: 'var(--danger)' },
                            { label: 'Total Trade',    value: totalTrades,                                icon: <BarChart2 size={16} />,  color: 'var(--accent)' },
                            { label: 'Avg R:R',        value: `1:${Number(avgRR).toFixed(2)}`,            icon: <Activity size={16} />,   color: 'var(--accent)' },
                            { label: 'Avg Win',        value: `$${Number(avgWin).toFixed(0)}`,            icon: <TrendingUp size={16} />, color: 'var(--success)' },
                            { label: 'Sharpe Ratio',   value: Number(sharpe).toFixed(2),                  icon: <Award size={16} />,      color: 'var(--accent)' },
                        ].map((s, i) => (
                            <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                <div className="flex justify-between items-start mb-2">
                                    <p className="text-[9px] uppercase tracking-wider text-[var(--text-dim)] font-bold">{s.label}</p>
                                    <span style={{ color: s.color }}>{s.icon}</span>
                                </div>
                                <p className="text-xl font-display font-black" style={{ color: s.color }}>{s.value}</p>
                            </div>
                        ))}
                    </div>

                    {/* Equity Curve */}
                    {eqValues.length > 1 && (
                        <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Equity Curve · {pair} {timeframe}</p>
                            <div className="relative h-32">
                                <svg className="w-full h-full" viewBox={`0 0 ${eqValues.length - 1} 100`} preserveAspectRatio="none">
                                    <defs>
                                        <linearGradient id="eq-grad-real" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="var(--success)" stopOpacity="0.3" />
                                            <stop offset="100%" stopColor="var(--success)" stopOpacity="0" />
                                        </linearGradient>
                                    </defs>
                                    <path
                                        d={`M ${eqValues.map((v, i) => `${i},${100 - ((v - minEq) / (maxEq - minEq || 1)) * 90}`).join(' L ')} L ${eqValues.length - 1},100 L 0,100 Z`}
                                        fill="url(#eq-grad-real)" />
                                    <path
                                        d={`M ${eqValues.map((v, i) => `${i},${100 - ((v - minEq) / (maxEq - minEq || 1)) * 90}`).join(' L ')}`}
                                        fill="none" stroke="var(--success)" strokeWidth="0.5" />
                                </svg>
                            </div>
                            <div className="flex justify-between text-[9px] text-[var(--text-dim)] font-bold mt-2">
                                <span>${eqValues[0]?.toLocaleString()}</span>
                                <span className="text-[var(--success)]">${eqValues[eqValues.length - 1]?.toLocaleString()}</span>
                            </div>
                        </div>
                    )}

                    {/* Monthly Returns */}
                    {monthlyReturns.length > 0 && (
                        <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Return Bulanan (%)</p>
                            <div className="flex items-end gap-1 h-20">
                                {monthlyReturns.map((m, idx) => {
                                    const val = typeof m === 'object' ? (m.pct || m.return || m.p || 0) : m;
                                    const label = typeof m === 'object' ? (m.month || m.m || idx + 1) : idx + 1;
                                    const isPos = val >= 0;
                                    const h = Math.abs(val) / (maxMonth || 1) * 100;
                                    return (
                                        <div key={idx} className="flex-1 flex flex-col items-center gap-1" title={`${label}: ${val}%`}>
                                            <div className="relative w-full flex items-end justify-center h-16">
                                                <div className="w-full rounded-sm transition-all"
                                                    style={{ height: `${h}%`, backgroundColor: isPos ? 'var(--success)' : 'var(--danger)', opacity: 0.8 }} />
                                            </div>
                                            <span className="text-[7px] text-[var(--text-dim)] font-bold truncate w-full text-center">{label}</span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    )}

                    {/* Trade list */}
                    {(r.trades || r.trade_list || []).length > 0 && (
                        <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Sample Trades</p>
                            <div className="overflow-x-auto">
                                <table className="w-full text-[10px]">
                                    <thead>
                                        <tr className="border-b border-[var(--border-color)] text-[var(--text-dim)] font-black uppercase">
                                            <th className="px-3 py-2 text-left">Arah</th>
                                            <th className="px-3 py-2 text-right">Entry</th>
                                            <th className="px-3 py-2 text-right">Exit</th>
                                            <th className="px-3 py-2 text-right">P&L</th>
                                            <th className="px-3 py-2 text-right">R:R</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(r.trades || r.trade_list || []).slice(0, 10).map((t, i) => {
                                            const pnl = t.pnl ?? t.profit ?? 0;
                                            return (
                                                <tr key={i} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)]">
                                                    <td className="px-3 py-2"><span className={`font-black ${t.direction?.includes('BUY') || t.type?.includes('BUY') ? 'text-green-400' : 'text-red-400'}`}>{t.direction || t.type || '—'}</span></td>
                                                    <td className="px-3 py-2 text-right font-mono text-[var(--text-secondary)]">{t.entry || '—'}</td>
                                                    <td className="px-3 py-2 text-right font-mono text-[var(--text-secondary)]">{t.exit || t.exit_price || '—'}</td>
                                                    <td className={`px-3 py-2 text-right font-black font-mono ${pnl >= 0 ? 'text-green-400' : 'text-red-400'}`}>{pnl >= 0 ? '+' : ''}${Number(pnl).toFixed(2)}</td>
                                                    <td className="px-3 py-2 text-right font-mono text-[var(--accent)]">{t.rr || t.r_multiple ? `1:${Number(t.rr || t.r_multiple).toFixed(1)}` : '—'}</td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}

            {!results && !running && !error && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <Activity size={40} className="text-[var(--text-dim)] mb-4 opacity-30" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Pilih pair, timeframe & candle count, lalu klik Jalankan Backtest</p>
                    <p className="text-[10px] text-[var(--text-dim)] mt-1">AI akan menganalisa data historis real dari MT5 EA · 20 Kredit</p>
                </div>
            )}
        </div>
    );
}
