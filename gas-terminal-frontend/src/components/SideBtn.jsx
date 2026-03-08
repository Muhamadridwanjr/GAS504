import React from 'react';

export default function SideBtn({ icon: Icon, label, id, active, onClick, collapsed }) {
    return (
        <button onClick={() => onClick(id)}
            className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg transition-all relative group ${active ? 'bg-[var(--bg-hover)] text-[var(--accent)]' : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-secondary)]'}`}>
            {active && <div className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-1 bg-[var(--accent)] rounded-r" />}
            <Icon size={18} className={`shrink-0 ${active ? 'text-[var(--accent)]' : ''} ${collapsed ? 'mx-auto' : 'mx-auto xl:mx-0'}`} />
            {!collapsed && <span className="hidden xl:block text-[11px] font-bold tracking-wider truncate">{label}</span>}
        </button>
    );
}
