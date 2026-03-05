import React from 'react';
import { Zap } from 'lucide-react';

export default function LoadingScreen() {
    return (
        <div className="min-h-screen bg-[var(--bg-main)] flex flex-col items-center justify-center gap-8">
            <div className="w-16 h-16 rounded-2xl bg-[var(--accent-soft)] border border-[var(--accent)]/20 flex items-center justify-center pulse-dot shadow-[0_0_30px_rgba(250,204,21,0.1)]">
                <Zap size={28} className="text-[var(--accent)] fill-current" />
            </div>
            <div className="space-y-3 w-64 text-center">
                <div className="h-1 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                    <div className="h-full bg-[var(--accent)] loading-bar" />
                </div>
                <p className="text-[10px] font-bold text-[var(--text-dim)] uppercase tracking-[0.5em]">Memuat Mesin v3.0 Pro</p>
            </div>
        </div>
    );
}
