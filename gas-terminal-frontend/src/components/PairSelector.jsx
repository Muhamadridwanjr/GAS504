/**
 * PairSelector — Luxury pair selector. Replaces all <select> dropdowns.
 * Shows selected pair as a pill chip. Click opens a searchable modal grid.
 */
import React, { useState, useRef, useEffect } from 'react';
import { PAIRS } from '../constants';

/* Group pairs by type */
const GROUPS = PAIRS.reduce((acc, p) => {
    const key = p.type || 'Other';
    if (!acc[key]) acc[key] = [];
    acc[key].push(p);
    return acc;
}, {});

const TYPE_EMOJI = {
    Crypto:     '₿',
    Forex:      '💱',
    Commodity:  '🥇',
    Commodities:'🥇',
    Index:      '📈',
    Indices:    '📈',
    Futures:    '🔮',
    Other:      '🔷',
};

const POPULAR = ['XAUUSD', 'EURUSD', 'BTCUSD', 'USDJPY', 'GBPUSD', 'ETHUSD', 'XTIUSD', 'AUDUSD', 'USDCAD', 'XAGUSD'];

export default function PairSelector({ value, onChange, label = 'Pair', className = '' }) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState('');
    const [activeTab, setActiveTab] = useState('Popular');
    const modalRef = useRef(null);
    const inputRef = useRef(null);

    const selectedPair = PAIRS.find(p => p.symbol === value);

    // Close on outside click
    useEffect(() => {
        const handler = e => {
            if (modalRef.current && !modalRef.current.contains(e.target)) {
                setOpen(false);
                setSearch('');
            }
        };
        if (open) {
            document.addEventListener('mousedown', handler);
            setTimeout(() => inputRef.current?.focus(), 50);
        }
        return () => document.removeEventListener('mousedown', handler);
    }, [open]);

    // Filter
    const tabs = ['Popular', ...Object.keys(GROUPS)];
    const filteredPairs = search.trim()
        ? PAIRS.filter(p =>
            p.symbol.toLowerCase().includes(search.toLowerCase()) ||
            (p.name || '').toLowerCase().includes(search.toLowerCase())
          )
        : activeTab === 'Popular'
            ? POPULAR.map(sym => PAIRS.find(p => p.symbol === sym)).filter(Boolean)
            : (GROUPS[activeTab] || []);

    const handleSelect = (sym) => {
        onChange(sym);
        setOpen(false);
        setSearch('');
    };

    return (
        <div className={`relative ${className}`}>
            {label && (
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-2">{label}</p>
            )}

            {/* Trigger button */}
            <button
                onClick={() => setOpen(o => !o)}
                className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl border transition-all hover:border-[var(--accent)]/40 focus:outline-none focus:border-[var(--accent)]/60 group"
                style={{ background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }}
            >
                <div className="flex-1 flex items-center gap-2 min-w-0">
                    <span className="text-base leading-none">{TYPE_EMOJI[selectedPair?.type] || '💱'}</span>
                    <div className="min-w-0">
                        <span className="text-sm font-black text-[var(--text-primary)] block truncate">{value}</span>
                        {selectedPair?.name && (
                            <span className="text-[9px] text-[var(--text-dim)] block truncate">{selectedPair.name}</span>
                        )}
                    </div>
                </div>
                <svg className={`shrink-0 w-4 h-4 text-[var(--text-dim)] transition-transform ${open ? 'rotate-180' : ''}`}
                    viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M6 9l6 6 6-6" />
                </svg>
            </button>

            {/* Modal overlay */}
            {open && (
                <div className="fixed inset-0 z-[999] flex items-end sm:items-center justify-center p-4 sm:p-6"
                    style={{ background: 'rgba(0,0,0,0.7)', backdropFilter: 'blur(8px)' }}>
                    <div ref={modalRef}
                        className="w-full max-w-lg rounded-2xl border animate-scale-in overflow-hidden"
                        style={{ background: 'var(--bg-elevated)', borderColor: 'var(--border-color)', boxShadow: '0 24px 80px rgba(0,0,0,0.8)' }}>

                        {/* Modal header */}
                        <div className="px-4 pt-4 pb-3 border-b" style={{ borderColor: 'var(--border-subtle)' }}>
                            <div className="flex items-center justify-between mb-3">
                                <p className="text-sm font-black text-[var(--text-primary)]">Pilih Pair / Aset</p>
                                <button onClick={() => { setOpen(false); setSearch(''); }}
                                    className="w-7 h-7 rounded-lg flex items-center justify-center text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all text-sm">
                                    ✕
                                </button>
                            </div>
                            {/* Search */}
                            <div className="flex items-center gap-2 px-3 py-2 rounded-xl border transition-colors focus-within:border-[var(--accent)]/50"
                                style={{ background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }}>
                                <span className="text-[var(--text-dim)] text-sm">🔍</span>
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={search}
                                    onChange={e => setSearch(e.target.value)}
                                    placeholder="Ketik simbol atau nama..."
                                    className="bg-transparent text-xs text-[var(--text-primary)] outline-none w-full placeholder:text-[var(--text-dim)]"
                                />
                                {search && <button onClick={() => setSearch('')} className="text-[var(--text-dim)] text-xs">✕</button>}
                            </div>
                        </div>

                        {/* Tabs */}
                        {!search && (
                            <div className="flex gap-1 px-3 py-2 overflow-x-auto scrollbar-none border-b" style={{ borderColor: 'var(--border-subtle)' }}>
                                {tabs.map(tab => (
                                    <button key={tab} onClick={() => setActiveTab(tab)}
                                        className="shrink-0 px-3 py-1.5 rounded-lg text-[10px] font-bold transition-all"
                                        style={activeTab === tab
                                            ? { background: 'var(--accent-soft)', color: 'var(--accent)', border: '1px solid rgba(250,200,21,0.25)' }
                                            : { color: 'var(--text-dim)', border: '1px solid transparent' }
                                        }>
                                        {TYPE_EMOJI[tab] || '⭐'} {tab}
                                    </button>
                                ))}
                            </div>
                        )}

                        {/* Pair grid */}
                        <div className="p-3 max-h-72 overflow-y-auto scrollbar-none">
                            {filteredPairs.length === 0 ? (
                                <div className="py-8 text-center text-[var(--text-dim)] text-xs">Tidak ditemukan</div>
                            ) : (
                                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                                    {filteredPairs.map(p => (
                                        <button key={p.symbol} onClick={() => handleSelect(p.symbol)}
                                            className="flex items-center gap-2 px-3 py-2.5 rounded-xl border transition-all hover:-translate-y-0.5 text-left"
                                            style={p.symbol === value
                                                ? { background: 'var(--accent-soft)', borderColor: 'rgba(250,200,21,0.35)', boxShadow: '0 0 8px rgba(250,200,21,0.15)' }
                                                : { background: 'var(--bg-panel)', borderColor: 'var(--border-color)' }
                                            }
                                            onMouseEnter={e => { if (p.symbol !== value) e.currentTarget.style.borderColor = 'rgba(250,200,21,0.25)'; }}
                                            onMouseLeave={e => { if (p.symbol !== value) e.currentTarget.style.borderColor = 'var(--border-color)'; }}
                                        >
                                            <span className="text-base leading-none">{TYPE_EMOJI[p.type] || '💱'}</span>
                                            <div className="min-w-0">
                                                <p className="text-[11px] font-black truncate"
                                                    style={{ color: p.symbol === value ? 'var(--accent)' : 'var(--text-primary)' }}>
                                                    {p.symbol}
                                                </p>
                                                <p className="text-[8px] text-[var(--text-dim)] truncate">{p.type}</p>
                                            </div>
                                            {p.symbol === value && <span className="ml-auto text-[var(--accent)] text-xs">✓</span>}
                                        </button>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
