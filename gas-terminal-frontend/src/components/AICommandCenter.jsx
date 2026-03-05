import React from 'react';
import { MORE_CATEGORIES } from '../constants';

export default function AICommandCenter({ onSelect }) {
    return (
        <div className="p-4 md:p-6 space-y-8 pb-24 md:pb-6 max-w-7xl mx-auto">
            <div>
                <h2 className="text-2xl font-display font-black text-[var(--text-primary)] uppercase">Pusat Komando AI</h2>
                <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest mt-1 font-bold">Suite Alat Trading Kelas Pro</p>
            </div>

            {MORE_CATEGORIES.map((cat, idx) => (
                <div key={idx} className="space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] px-1">{cat.title}</p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
                        {cat.items.map(item => (
                            <button key={item.id} onClick={() => onSelect(item.id)}
                                className={`p-5 rounded-xl border text-left transition-all hover:-translate-y-1 ${cat.highlight ? 'bg-[var(--bg-panel)] border-[var(--accent)]/30 hover:border-[var(--accent)] shadow-[var(--card-shadow)]' : 'bg-[var(--bg-card)] border-[var(--border-color)] hover:border-[var(--text-dim)] hover:bg-[var(--bg-hover)]'}`}>
                                <div className="flex justify-between items-start mb-4">
                                    <div className={`p-2.5 rounded-lg ${cat.highlight ? 'bg-[var(--accent-soft)] text-[var(--accent)]' : 'bg-[var(--bg-hover)] text-[var(--text-dim)]'}`}>
                                        <item.icon size={20} />
                                    </div>
                                    {item.pro && <span className="text-[8px] bg-[var(--accent)] text-black font-black px-2 py-0.5 rounded uppercase tracking-wider">Pro</span>}
                                </div>
                                <span className={`text-xs font-bold block mb-1 ${cat.highlight ? 'text-[var(--text-primary)]' : 'text-[var(--text-secondary)]'}`}>{item.label}</span>
                                <span className="text-[10px] text-[var(--text-dim)]">Akses modul {item.label.toLowerCase()}</span>
                            </button>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    );
}
