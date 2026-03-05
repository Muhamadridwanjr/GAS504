import React from 'react';
import { ShieldAlert } from 'lucide-react';

export default function MacroSidebar({ macroData, aiAnalysis }) {
    return (
        <div className="space-y-6">
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-4 block">Fundamental Makro</span>
                {macroData && macroData.map((m, i) => (
                    <div key={i} className="flex justify-between items-center py-3 border-b border-[var(--border-color)] last:border-0 last:pb-0 text-xs">
                        <span className="text-[var(--text-secondary)] font-bold">{m.title}</span>
                        <div className="text-right">
                            <span className="font-mono font-bold text-[var(--text-primary)] mr-3">{m.value}</span>
                            <span className={`text-[9px] font-black tracking-wider ${m.impact === 'HIGH' ? 'text-[var(--danger)]' : 'text-[var(--accent)]'}`}>{m.bias}</span>
                        </div>
                    </div>
                ))}
            </div>
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                <div className="flex items-center justify-between mb-4">
                    <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Logika AI</span>
                    <div className="flex items-center gap-1.5 text-[10px] text-[var(--success)] font-bold">
                        <div className="w-1.5 h-1.5 bg-[var(--success)] rounded-full pulse-dot" />
                        LIVE
                    </div>
                </div>
                <p className={`text-2xl font-display font-black mb-4 ${aiAnalysis?.trend === 'BULLISH' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                    {aiAnalysis?.trend || 'ANALYZING...'}
                </p>
                <div className="space-y-2">
                    {aiAnalysis?.logic && aiAnalysis.logic.map((l, i) => (
                        <div key={i} className="flex items-start gap-3 text-[11px] p-3 rounded-lg bg-[var(--bg-hover)] border border-[var(--border-color)]">
                            <ShieldAlert size={12} className="text-[var(--accent)] shrink-0 mt-0.5" />
                            <span className="text-[var(--text-secondary)] leading-relaxed">{l}</span>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
