import React from 'react';

export default function EmptyView({ icon, label, sub }) {
    return (
        <div className="flex flex-col items-center justify-center h-[60vh] text-center p-8">
            <div className="text-[var(--border-color)] mb-6 scale-150">{icon}</div>
            <p className="font-display font-black text-[var(--text-dim)] text-xl uppercase tracking-widest">{label}</p>
            <p className="text-xs text-[var(--text-dim)] mt-2 font-bold">{sub}</p>
        </div>
    );
}
