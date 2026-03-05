import React from 'react';

export default function PriceBox({ label, value, color, highlight }) {
    const cls = color === 'green' ? 'text-[var(--success)]' : color === 'red' ? 'text-[var(--danger)]' : 'text-[var(--text-primary)]';
    return (
        <div className={`bg-[var(--bg-panel)] rounded-xl p-4 border transition-all ${highlight ? 'border-[var(--accent)]/30 shadow-[0_0_20px_var(--accent-soft)]' : 'border-[var(--border-color)]'}`}>
            <p className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-[0.2em] mb-2">{label}</p>
            <p className={`font-mono font-black text-xl ${cls}`}>{value}</p>
        </div>
    );
}
