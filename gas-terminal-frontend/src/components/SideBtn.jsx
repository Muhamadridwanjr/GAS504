import React from 'react';

export default function SideBtn({ icon: Icon, label, id, active, onClick, collapsed, badge }) {
    return (
        <button
            onClick={() => onClick(id)}
            title={collapsed ? label : undefined}
            className={`
                relative w-full flex items-center gap-2.5 px-2.5 py-2.5 rounded-xl
                transition-all duration-200 group
                ${active
                    ? 'bg-[var(--accent-soft)] text-[var(--accent)]'
                    : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-secondary)]'
                }
            `}
        >
            {/* Active indicator bar */}
            {active && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] bg-[var(--accent)] rounded-r-full shadow-[0_0_8px_rgba(250,200,21,0.6)]" />
            )}

            {/* Icon with background when active */}
            <div className={`
                shrink-0 w-7 h-7 rounded-lg flex items-center justify-center transition-all duration-200
                ${collapsed ? 'mx-auto' : 'mx-auto xl:mx-0'}
                ${active ? 'bg-[var(--accent)]/15' : 'group-hover:bg-[var(--bg-panel)]'}
            `}>
                <Icon
                    size={15}
                    className={`transition-colors ${active ? 'text-[var(--accent)]' : 'text-current'}`}
                />
            </div>

            {/* Label */}
            {!collapsed && (
                <span className="hidden xl:block text-[11px] font-bold tracking-wide truncate flex-1 text-left">
                    {label}
                </span>
            )}

            {/* Optional badge */}
            {!collapsed && badge && (
                <span className="hidden xl:flex shrink-0 text-[7px] font-black px-1 py-0.5 rounded bg-[var(--accent)] text-black">
                    {badge}
                </span>
            )}
        </button>
    );
}
