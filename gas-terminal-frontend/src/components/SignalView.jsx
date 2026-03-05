import React from 'react';
import { Clock, Copy, Share2, Zap, BarChart3, Info } from 'lucide-react';
import TradingViewChart from './TradingViewChart';
import PriceBox from './PriceBox';
import MacroSidebar from './MacroSidebar';
import AIBloombergTerminal from './AIBloombergTerminal';

export default function SignalView({ signal, isNew, timer, chartPair, prices, onSelect, activePair, pairs, macroData, aiAnalysis, theme }) {
    if (!signal) return null;
    const isBuy = signal.type === 'BUY';
    const pairData = pairs.find(p => p.symbol === chartPair.symbol) || chartPair;
    const curPrice = prices[chartPair.symbol] || pairData.base;

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 transition-colors">
            {/* Pair Quick Selector */}
            <div className="flex gap-3 overflow-x-auto scrollbar-none pb-2">
                {pairs.map(p => {
                    const cur = prices[p.symbol] || p.price || p.base;
                    const chg = ((cur - p.base) / p.base * 100);
                    const isUp = chg >= 0;
                    return (
                        <button key={p.symbol} onClick={() => onSelect(p.symbol)}
                            className={`shrink-0 flex flex-col px-4 py-2.5 rounded-xl border text-left transition-all ${activePair === p.symbol ? 'bg-[var(--accent-soft)] border-[var(--accent)]/40 text-[var(--accent)] shadow-[0_8px_16px_rgba(0,0,0,0.1)] scale-[1.02]' : 'bg-[var(--bg-card)] border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--text-secondary)]'}`}>
                            <span className="text-[11px] font-black uppercase tracking-wider">{p.symbol}</span>
                            <span className={`text-[10px] font-mono mt-0.5 font-bold ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{isUp ? '+' : ''}{chg.toFixed(2)}%</span>
                        </button>
                    );
                })}
            </div>

            <div className="grid xl:grid-cols-[1fr_380px] gap-6">
                {/* Left: Chart + Signal */}
                <div className="space-y-6">
                    {/* Pro Chart Panel - REDESIGNED */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl overflow-hidden shadow-[var(--card-shadow)] flex flex-col lg:flex-row h-[500px]">
                        <div className="flex-1 flex flex-col border-r border-[var(--border-color)]">
                            <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-color)] bg-[var(--bg-panel)]/50">
                                <div className="flex items-center gap-4">
                                    <div className="flex flex-col">
                                        <div className="flex items-center gap-2">
                                            <span className="text-sm font-black text-[var(--text-primary)] uppercase tracking-tighter">{chartPair.symbol}</span>
                                            <span className="text-[10px] px-1.5 py-0.5 bg-[var(--bg-hover)] text-[var(--text-dim)] rounded font-bold">CFD</span>
                                        </div>
                                        <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase tracking-widest">{chartPair.name}</span>
                                    </div>
                                    <div className="h-8 w-px bg-[var(--border-color)] mx-1"></div>
                                    <div className="flex flex-col">
                                        <span className={`text-xl font-mono font-black ${isUpFromBase(prices, chartPair) ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                            {curPrice.toFixed(pairData.type === 'Forex' ? 4 : 2)}
                                        </span>
                                        <div className="flex items-center gap-1 opacity-80">
                                            <BarChart3 size={10} className="text-[var(--text-dim)]" />
                                            <span className="text-[8px] font-bold text-[var(--text-dim)] uppercase">Real-time Feed</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="hidden sm:flex items-center gap-1.5 bg-[var(--bg-panel)] p-1 rounded-lg border border-[var(--border-color)]">
                                    {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
                                        <button key={tf} className={`text-[9px] px-3 py-1.5 rounded-md transition-all font-black uppercase ${tf === '15m' ? 'bg-[var(--accent)] text-black shadow-md' : 'text-[var(--text-dim)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'}`}>{tf}</button>
                                    ))}
                                </div>
                            </div>
                            <div className="flex-1 p-0 relative min-h-[300px]">
                                <TradingViewChart pair={chartPair} currentPrice={curPrice} theme={theme} />
                            </div>
                        </div>

                        {/* Integrated AI Terminal / Bloomberg Style */}
                        <div className="w-full lg:w-[280px] xl:w-[320px] bg-[var(--bg-panel)] flex flex-col shrink-0">
                            <AIBloombergTerminal />
                        </div>
                    </div>

                    {/* Pro Signal Card */}
                    <div className={`bg-[var(--bg-card)] border rounded-2xl p-8 transition-all duration-500 relative overflow-hidden shadow-[var(--card-shadow)] ${isNew ? 'border-[var(--accent)]/40 ring-1 ring-[var(--accent)]/20' : 'border-[var(--border-color)]'}`}>
                        <div className={`absolute -top-24 -right-24 w-80 h-80 blur-[130px] opacity-20 pointer-events-none ${isBuy ? 'bg-[var(--success)]' : 'bg-[var(--danger)]'}`}></div>

                        <div className="flex items-start justify-between mb-8 relative z-10">
                            <div>
                                <div className="flex items-center gap-3 mb-3">
                                    <span className={`text-[10px] font-black px-3 py-1.5 rounded-lg uppercase tracking-[0.2em] shadow-sm ${isBuy ? 'bg-[var(--success)]/10 text-[var(--success)] border border-[var(--success)]/20' : 'bg-[var(--danger)]/10 text-[var(--danger)] border border-[var(--danger)]/20'}`}>
                                        {signal.level} SETUP
                                    </span>
                                    <div className="flex items-center gap-2 text-[9px] text-[var(--success)] font-black uppercase tracking-widest">
                                        <div className="w-2 h-2 bg-[var(--success)] rounded-full pulse-dot shadow-[0_0_8px_var(--success)]" />LIVE
                                    </div>
                                </div>
                                <h2 className="text-4xl font-display font-black text-[var(--text-primary)] tracking-tighter uppercase">{signal.pair}</h2>
                                <div className="flex items-center gap-2 mt-2">
                                    <Clock size={12} className="text-[var(--text-dim)]" />
                                    <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">{signal.timestamp || new Date().toLocaleTimeString()} · GRADE {signal.grade}</p>
                                </div>
                            </div>
                            <div className={`px-8 py-5 rounded-2xl text-2xl font-black shadow-2xl border-b-4 flex flex-col items-center justify-center min-w-[120px] ${isBuy ? 'bg-[var(--success)] text-white border-emerald-600' : 'bg-[var(--danger)] text-white border-red-600'}`}>
                                {signal.type}
                                <span className="text-[9px] opacity-70 font-bold uppercase tracking-widest mt-1">{isBuy ? 'High Prob' : 'Low Prob'}</span>
                            </div>
                        </div>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-5 mb-8 relative z-10">
                            <PriceBox label="Entry Level" value={signal.entry} />
                            <PriceBox label="Stop Loss" value={signal.sl} color={isBuy ? 'red' : 'green'} />
                            <PriceBox label="Take Profit 1" value={signal.tp1} color={isBuy ? 'green' : 'red'} />
                            <PriceBox label="Take Profit 2" value={signal.tp2} color={isBuy ? 'green' : 'red'} highlight />
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-5 mb-8 relative z-10">
                            <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-5 shadow-inner">
                                <div className="flex justify-between items-center mb-3">
                                    <div className="flex items-center gap-2">
                                        <Info size={12} className="text-[var(--text-dim)]" />
                                        <p className="text-[10px] text-[var(--text-secondary)] font-black uppercase tracking-widest">Akurasi AI</p>
                                    </div>
                                    <span className={`text-base font-black ${isBuy ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{signal.confidence * 10}%</span>
                                </div>
                                <div className="h-2.5 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                                    <div className={`h-full rounded-full transition-all duration-1000 ${isBuy ? 'bg-[var(--success)] shadow-[0_0_15px_var(--success)]' : 'bg-[var(--danger)] shadow-[0_0_15px_var(--danger)]'}`} style={{ width: `${signal.confidence * 10}%` }} />
                                </div>
                            </div>
                            <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-5 flex justify-between items-center shadow-inner">
                                <div>
                                    <p className="text-[10px] text-[var(--text-secondary)] font-black uppercase tracking-widest mb-1.5">Berlaku Dalam</p>
                                    <div className="flex items-center gap-2.5">
                                        <Clock size={16} className="text-[var(--accent)]" />
                                        <span className="font-mono font-black text-[var(--accent)] text-2xl tracking-tight">{timer}s</span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] text-[var(--text-secondary)] font-black uppercase tracking-widest mb-1.5">R:R Rasio</p>
                                    <span className="font-mono font-black text-[var(--text-primary)] text-xl italic">{signal.rr}</span>
                                </div>
                            </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 relative z-10">
                            <button className="flex items-center justify-center gap-2 py-4 rounded-xl bg-[var(--bg-hover)] border border-[var(--border-color)] text-xs font-black uppercase tracking-widest text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] transition-all">
                                <Copy size={16} /> Salin Level
                            </button>
                            <button className="flex items-center justify-center gap-2 py-4 rounded-xl bg-[var(--bg-hover)] border border-[var(--border-color)] text-xs font-black uppercase tracking-widest text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-panel)] transition-all">
                                <Share2 size={16} /> Bagikan
                            </button>
                            <button className={`flex items-center justify-center gap-3 py-4 rounded-xl text-base font-black uppercase tracking-widest transition-all shadow-[0_10px_20px_rgba(0,0,0,0.2)] hover:-translate-y-1 active:translate-y-0 ${isBuy ? 'bg-[var(--success)] text-white hover:bg-emerald-400' : 'bg-[var(--danger)] text-white hover:bg-red-400'}`}>
                                <Zap size={18} className="fill-current" /> Eksekusi Instan
                            </button>
                        </div>
                    </div>
                </div>

                {/* Right: Market Summary */}
                <div className="hidden xl:block space-y-6">
                    <MacroSidebar macroData={macroData} aiAnalysis={aiAnalysis} />
                </div>
            </div>
        </div>
    );
}

function isUpFromBase(prices, pair) {
    const cur = prices[pair.symbol] || pair.base;
    return cur >= pair.base;
}
