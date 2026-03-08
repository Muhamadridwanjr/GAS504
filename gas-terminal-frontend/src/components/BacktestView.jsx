import React, { useState } from 'react';
import { Activity, Play, TrendingUp, TrendingDown, BarChart2, Award } from 'lucide-react';
import { PAIRS } from '../constants';

const STRATEGIES = [
    'SMC Order Block', 'EMA Crossover', 'RSI Divergence', 'MACD Momentum',
    'Breakout + Retest', 'Supply & Demand', 'Fibonacci Retracement', 'ICT Killzone',
];

const MOCK_RESULTS = {
    totalTrades: 248,
    winRate: 71.4,
    profitFactor: 2.38,
    netProfit: 12_480,
    maxDrawdown: 8.2,
    avgRR: 1.87,
    avgWin: 142.5,
    avgLoss: -76.2,
    sharpe: 1.94,
    bestMonth: 'Nov 2024',
    worstMonth: 'Aug 2024',
};

const EQUITY_CURVE = [
    10000, 10220, 10180, 10560, 10430, 10820, 11100, 10920, 11350, 11680,
    11520, 11940, 12300, 12120, 12480,
];

const MONTHLY = [
    { m: 'Jan', p: 3.2 }, { m: 'Feb', p: -1.4 }, { m: 'Mar', p: 5.8 }, { m: 'Apr', p: 2.1 },
    { m: 'Mei', p: 4.7 }, { m: 'Jun', p: -0.8 }, { m: 'Jul', p: 6.3 }, { m: 'Agt', p: -2.1 },
    { m: 'Sep', p: 3.9 }, { m: 'Okt', p: 5.2 }, { m: 'Nov', p: 7.8 }, { m: 'Des', p: 4.1 },
];

const MAX_EQ = Math.max(...EQUITY_CURVE);
const MIN_EQ = Math.min(...EQUITY_CURVE);

export default function BacktestView() {
    const [pair, setPair] = useState('XAUUSD');
    const [strategy, setStrategy] = useState(STRATEGIES[0]);
    const [period, setPeriod] = useState('12');
    const [running, setRunning] = useState(false);
    const [results, setResults] = useState(null);

    const run = () => {
        setRunning(true);
        setResults(null);
        setTimeout(() => {
            const r = { ...MOCK_RESULTS };
            r.totalTrades = Math.round(MOCK_RESULTS.totalTrades * (0.8 + Math.random() * 0.4));
            r.winRate = +(MOCK_RESULTS.winRate * (0.9 + Math.random() * 0.2)).toFixed(1);
            r.profitFactor = +(MOCK_RESULTS.profitFactor * (0.85 + Math.random() * 0.3)).toFixed(2);
            r.netProfit = Math.round(MOCK_RESULTS.netProfit * (0.8 + Math.random() * 0.4));
            setResults(r);
            setRunning(false);
        }, 2200);
    };

    const maxMonth = Math.max(...MONTHLY.map(m => Math.abs(m.p)));

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Activity size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Mesin Backtest</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Uji Strategi Trading Secara Historis</p>
                </div>
                <span className="text-[8px] bg-[var(--accent)] text-black font-black px-2 py-0.5 rounded uppercase ml-2">Pro</span>
            </div>

            {/* Config Panel */}
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
                <div className="space-y-1">
                    <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Pair</label>
                    <select value={pair} onChange={e => setPair(e.target.value)}
                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
                        {PAIRS.map(p => <option key={p.symbol} value={p.symbol}>{p.symbol}</option>)}
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Strategi</label>
                    <select value={strategy} onChange={e => setStrategy(e.target.value)}
                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
                        {STRATEGIES.map(s => <option key={s}>{s}</option>)}
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Periode (Bulan)</label>
                    <select value={period} onChange={e => setPeriod(e.target.value)}
                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]">
                        {['3', '6', '12', '24', '36'].map(p => <option key={p}>{p}</option>)}
                    </select>
                </div>
                <div className="space-y-1">
                    <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">&nbsp;</label>
                    <button onClick={run} disabled={running}
                        className="w-full flex items-center justify-center gap-2 bg-[var(--accent)] text-black font-black px-4 py-2.5 rounded-lg text-xs hover:opacity-90 transition-opacity disabled:opacity-50">
                        {running ? (
                            <>
                                <div className="w-3 h-3 border-2 border-black border-t-transparent rounded-full animate-spin" />
                                Running...
                            </>
                        ) : (
                            <><Play size={12} /> Jalankan Backtest</>
                        )}
                    </button>
                </div>
            </div>

            {/* Progress Bar */}
            {running && (
                <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--accent)]/30">
                    <div className="flex justify-between text-[10px] font-bold mb-2">
                        <span className="text-[var(--text-dim)]">Memproses {pair} · {strategy}</span>
                        <span className="text-[var(--accent)]">AI Analyzing...</span>
                    </div>
                    <div className="h-1.5 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                        <div className="h-full bg-[var(--accent)] rounded-full animate-pulse" style={{ width: '60%' }} />
                    </div>
                </div>
            )}

            {/* Results */}
            {results && (
                <>
                    {/* Stats Grid */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-4 gap-3">
                        {[
                            { label: 'Win Rate', value: `${results.winRate}%`, icon: <Award size={16} />, color: 'var(--success)', good: true },
                            { label: 'Profit Factor', value: results.profitFactor, icon: <TrendingUp size={16} />, color: 'var(--success)', good: true },
                            { label: 'Net Profit', value: `$${results.netProfit.toLocaleString()}`, icon: <TrendingUp size={16} />, color: 'var(--success)', good: true },
                            { label: 'Max Drawdown', value: `${results.maxDrawdown}%`, icon: <TrendingDown size={16} />, color: 'var(--danger)', good: false },
                            { label: 'Total Trade', value: results.totalTrades, icon: <BarChart2 size={16} />, color: 'var(--accent)', good: true },
                            { label: 'Avg R:R', value: `1:${results.avgRR}`, icon: <Activity size={16} />, color: 'var(--accent)', good: true },
                            { label: 'Avg Win', value: `$${results.avgWin}`, icon: <TrendingUp size={16} />, color: 'var(--success)', good: true },
                            { label: 'Sharpe Ratio', value: results.sharpe, icon: <Award size={16} />, color: 'var(--accent)', good: true },
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
                    <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Equity Curve · {pair}</p>
                        <div className="relative h-32">
                            <svg className="w-full h-full" viewBox={`0 0 ${EQUITY_CURVE.length - 1} 100`} preserveAspectRatio="none">
                                <defs>
                                    <linearGradient id="eq-grad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="var(--success)" stopOpacity="0.3" />
                                        <stop offset="100%" stopColor="var(--success)" stopOpacity="0" />
                                    </linearGradient>
                                </defs>
                                <path
                                    d={`M ${EQUITY_CURVE.map((v, i) => `${i},${100 - ((v - MIN_EQ) / (MAX_EQ - MIN_EQ)) * 90}`).join(' L ')} L ${EQUITY_CURVE.length - 1},100 L 0,100 Z`}
                                    fill="url(#eq-grad)"
                                />
                                <path
                                    d={`M ${EQUITY_CURVE.map((v, i) => `${i},${100 - ((v - MIN_EQ) / (MAX_EQ - MIN_EQ)) * 90}`).join(' L ')}`}
                                    fill="none" stroke="var(--success)" strokeWidth="0.5"
                                />
                            </svg>
                        </div>
                        <div className="flex justify-between text-[9px] text-[var(--text-dim)] font-bold mt-2">
                            <span>${EQUITY_CURVE[0].toLocaleString()}</span>
                            <span className="text-[var(--success)]">${EQUITY_CURVE[EQUITY_CURVE.length - 1].toLocaleString()}</span>
                        </div>
                    </div>

                    {/* Monthly Returns */}
                    <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                        <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Return Bulanan (%)</p>
                        <div className="flex items-end gap-1 h-20">
                            {MONTHLY.map((m) => {
                                const isPos = m.p >= 0;
                                const h = Math.abs(m.p) / maxMonth * 100;
                                return (
                                    <div key={m.m} className="flex-1 flex flex-col items-center gap-1">
                                        <div className="relative w-full flex items-end justify-center h-16">
                                            <div className="w-full rounded-sm transition-all"
                                                style={{
                                                    height: `${h}%`,
                                                    backgroundColor: isPos ? 'var(--success)' : 'var(--danger)',
                                                    opacity: 0.8
                                                }} />
                                        </div>
                                        <span className="text-[7px] text-[var(--text-dim)] font-bold">{m.m}</span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </>
            )}

            {!results && !running && (
                <div className="flex flex-col items-center justify-center py-20 text-center">
                    <Activity size={40} className="text-[var(--text-dim)] mb-4" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Pilih pair & strategi, lalu klik Jalankan Backtest</p>
                    <p className="text-[10px] text-[var(--text-dim)] mt-1">AI akan menganalisa data historis secara otomatis</p>
                </div>
            )}
        </div>
    );
}
