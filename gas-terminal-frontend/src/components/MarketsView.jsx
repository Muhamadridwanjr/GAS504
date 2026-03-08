import React, { useState } from 'react';
import Sparkline from './Sparkline';
import { ChevronUp, ChevronDown, BarChart3 } from 'lucide-react';
import TradingViewChart from './TradingViewChart';
import TradingViewWidget from './TradingViewWidget';
import StaticChart from './StaticChart';

export default function MarketsView({ pairs, prices, directions, onSelect, activePair, theme, chartPair }) {
    const [tab, setTab] = useState('All');
    const [timeframe, setTimeframe] = useState('15m');
    const [chartMode, setChartMode] = useState('interactive'); // 'interactive' or 'expert'

    const selectedPairData = pairs.find(p => p.symbol === activePair) || pairs[0];
    const curPrice = prices[activePair] || selectedPairData?.base || 0;

    return (
        <div className="h-full flex flex-col p-2 md:p-3 space-y-3 overflow-hidden bg-[var(--bg-main)]">
            {/* Top Stat Bar */}
            <div className="flex items-center justify-between px-4 py-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-lg shadow-sm">
                <div className="flex items-center gap-4">
                    <div className="flex flex-col">
                        <span className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Active Market</span>
                        <div className="flex items-center gap-2">
                            <span className="text-lg font-black text-[var(--text-primary)]">{activePair}</span>
                            <span className={`text-xs font-mono font-bold ${directions[activePair] === 'up' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                {curPrice.toFixed(selectedPairData?.type === 'Forex' ? 4 : 2)}
                            </span>
                        </div>
                    </div>
                    <div className="h-8 w-px bg-[var(--border-color)] hidden md:block" />
                    <div className="hidden md:flex flex-col">
                        <span className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">24h Change</span>
                        <span className={`text-xs font-mono font-bold ${(curPrice - selectedPairData?.base) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                            {((curPrice - selectedPairData?.base) / selectedPairData?.base * 100).toFixed(2)}%
                        </span>
                    </div>
                </div>
                <div className="flex items-center gap-4">
                    <div className="flex items-center gap-1 bg-[var(--bg-panel)] p-1 rounded-lg border border-[var(--border-color)] mr-2">
                        <button
                            onClick={() => setChartMode('interactive')}
                            className={`text-[9px] px-2 py-1 rounded transition-all font-black uppercase ${chartMode === 'interactive' ? 'bg-[var(--accent)] text-black' : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)]'}`}
                        >
                            Interactive
                        </button>
                        <button
                            onClick={() => setChartMode('expert')}
                            className={`text-[9px] px-2 py-1 rounded transition-all font-black uppercase ${chartMode === 'expert' ? 'bg-[var(--accent)] text-black' : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)]'}`}
                        >
                            Expert
                        </button>
                    </div>
                    <div className="flex items-center gap-2 bg-[var(--bg-panel)] p-1 rounded-lg border border-[var(--border-color)]">
                        {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
                            <button
                                key={tf}
                                onClick={() => setTimeframe(tf)}
                                className={`text-[9px] px-2.5 py-1.5 rounded transition-all font-black uppercase ${tf === timeframe ? 'bg-[var(--accent)] text-black shadow-lg' : 'text-[var(--text-dim)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'}`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
            {/* Main Terminal Grid */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-[280px_1fr_300px] gap-3 min-h-0">

                {/* Left Pane: Market List */}
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl flex flex-col overflow-hidden shadow-xl">
                    <div className="flex border-b border-[var(--border-color)] bg-[var(--bg-panel)]/50">
                        {['All', 'Forex', 'Crypto'].map(t => (
                            <button key={t} onClick={() => setTab(t)}
                                className={`flex-1 py-3 text-[10px] font-black uppercase tracking-widest transition-all ${tab === t ? 'text-[var(--accent)] bg-[var(--bg-hover)] border-b-2 border-[var(--accent)]' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                                {t}
                            </button>
                        ))}
                    </div>
                    <div className="flex-1 overflow-y-auto scrollbar-none divide-y divide-[var(--border-color)]">
                        {pairs.filter(p => tab === 'All' || p.type === tab).map(p => {
                            const cur = prices[p.symbol] || p.price || p.base;
                            const isUp = (cur - p.base) >= 0;
                            const isActive = activePair === p.symbol;
                            return (
                                <div key={p.symbol} onClick={() => onSelect(p.symbol)}
                                    className={`px-4 py-3 cursor-pointer transition-all hover:bg-[var(--bg-hover)] group ${isActive ? 'bg-[var(--accent-soft)] border-l-2 border-[var(--accent)]' : ''}`}>
                                    <div className="flex justify-between items-start mb-1">
                                        <span className={`text-xs font-black ${isActive ? 'text-[var(--accent)]' : 'text-[var(--text-primary)]'}`}>{p.symbol}</span>
                                        <span className={`text-[11px] font-mono font-bold ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                            {cur.toFixed(p.type === 'Forex' ? 4 : 2)}
                                        </span>
                                    </div>
                                    <div className="flex justify-between items-center">
                                        <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase tracking-tight">{p.name || p.type}</span>
                                        <div className="w-12 h-4 opacity-50 group-hover:opacity-100 transition-opacity">
                                            <Sparkline data={p.trend || [50, 50, 50, 50, 50, 50, 50]} color={isUp ? 'var(--success)' : 'var(--danger)'} width={48} height={16} />
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Center Pane: Chart */}
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-2xl flex flex-col relative">
                    <div className="absolute top-4 left-4 z-10 pointer-events-none opacity-20">
                        <span className="text-4xl font-black text-[var(--text-dim)] uppercase tracking-[0.2em]">{activePair}</span>
                    </div>
                    <div className="flex-1 min-h-0 bg-[var(--bg-panel)]/20">
                        {chartMode === 'interactive' ? (
                            <TradingViewWidget pair={selectedPairData} theme={theme} />
                        ) : (
                            <StaticChart pair={selectedPairData} theme={theme} timeframe={timeframe.toUpperCase()} />
                        )}
                    </div>

                    {/* Bottom Area of Center Pane (Optional Activity) */}
                    <div className="h-32 border-t border-[var(--border-color)] bg-[var(--bg-panel)] flex gap-4 p-4 overflow-x-auto scrollbar-none">
                        <div className="flex-1 min-w-[200px] bg-[var(--bg-card)] rounded-lg border border-[var(--border-color)] p-3 flex flex-col justify-between">
                            <span className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">AI Prediction</span>
                            <div className="flex items-end justify-between">
                                <span className="text-xl font-black text-[var(--success)]">STRONGBUY</span>
                                <span className="text-[10px] text-[var(--text-dim)]">Confidence: 94%</span>
                            </div>
                        </div>
                        <div className="flex-1 min-w-[200px] bg-[var(--bg-card)] rounded-lg border border-[var(--border-color)] p-3 flex flex-col justify-between">
                            <span className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">Market Phase</span>
                            <div className="flex items-end justify-between">
                                <span className="text-xl font-black text-[var(--accent)]">ACCUMULATION</span>
                                <span className="text-[10px] text-[var(--text-dim)]">Volume: High</span>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Right Pane: Stats & Info */}
                <div className="hidden lg:flex flex-col gap-3">
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5 shadow-xl flex-1">
                        <div className="flex items-center gap-2 mb-6">
                            <BarChart3 size={14} className="text-[var(--accent)]" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-primary)]">Trade Statistics</span>
                        </div>
                        <div className="space-y-4">
                            {[
                                { label: 'High 24h', value: (curPrice * 1.002).toFixed(selectedPairData?.type === 'Forex' ? 4 : 2), color: 'var(--success)' },
                                { label: 'Low 24h', value: (curPrice * 0.998).toFixed(selectedPairData?.type === 'Forex' ? 4 : 2), color: 'var(--danger)' },
                                { label: 'Volume', value: '1.24B', color: 'var(--text-primary)' },
                                { label: 'Volatility', value: '1.45%', color: 'var(--accent)' },
                            ].map((s, i) => (
                                <div key={i} className="flex flex-col gap-1 border-b border-[var(--border-color)] pb-3 last:border-0">
                                    <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase">{s.label}</span>
                                    <span className="text-sm font-mono font-black" style={{ color: s.color }}>{s.value}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-[var(--bg-card)] border border-l-4 border-l-[var(--accent)] border-[var(--border-color)] rounded-xl p-5 shadow-inner bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-hover)]">
                        <span className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)] mb-2 block">Terminal Log</span>
                        <div className="font-mono text-[9px] text-[var(--text-dim)] space-y-1">
                            <p>[{new Date().toLocaleTimeString()}] <span className="text-[var(--text-secondary)]">Feed connected</span></p>
                            <p>[{new Date().toLocaleTimeString()}] <span className="text-[var(--success)]">Subscribed to {activePair}</span></p>
                            <p>[{new Date().toLocaleTimeString()}] <span className="text-[var(--text-dim)]">Analyzing liquidity...</span></p>
                        </div>
                    </div>
                </div>

            </div>
        </div>
    );
}

