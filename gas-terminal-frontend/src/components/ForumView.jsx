import React, { useState } from 'react';
import { Users, MessageCircle, ThumbsUp, Pin, Lock, Search, Plus, Crown } from 'lucide-react';

const CATEGORIES = ['Semua', 'Sinyal AI', 'Analisa Market', 'EA & Otomatisasi', 'Q&A', 'Pengumuman'];

const THREADS = [
    {
        id: 1, pinned: true, category: 'Pengumuman', title: '🔥 Update GAS v4.2 — Fitur Multi-TF & Risk Manager Baru!',
        author: 'GAS Admin', avatar: 'GA', role: 'admin', time: '2 jam lalu',
        replies: 47, likes: 203, views: 1240, preview: 'Kami dengan bangga memperkenalkan update terbesar GAS v4.2...'
    },
    {
        id: 2, pinned: true, category: 'Sinyal AI', title: 'XAUUSD Analisa Mingguan — AI Proyeksikan Target $3350+',
        author: 'Trader_Mas', avatar: 'TM', role: 'pro', time: '5 jam lalu',
        replies: 23, likes: 89, views: 542, preview: 'Berdasarkan konfluensi multi-TF dan COT report terbaru, bias bullish masih sangat kuat...'
    },
    {
        id: 3, category: 'EA & Otomatisasi', title: 'Tips Setting EA GAS di VPS — Latency Optimal < 5ms',
        author: 'DevTrader99', avatar: 'DT', role: 'pro', time: '1 hari lalu',
        replies: 15, likes: 64, views: 389, preview: 'Setelah 3 bulan eksperimen, ini setting VPS yang memberikan hasil terbaik...'
    },
    {
        id: 4, category: 'Analisa Market', title: 'DXY Melemah = Peluang Emas? Analisa Korelasi lengkap',
        author: 'GoldAnalyst', avatar: 'GA', role: 'member', time: '1 hari lalu',
        replies: 8, likes: 41, views: 218, preview: 'Korelasi DXY vs XAUUSD secara historis sekitar -0.85. Ketika DXY...'
    },
    {
        id: 5, category: 'Q&A', title: 'Cara Setting Webhook ke n8n untuk Auto Alert Telegram?',
        author: 'NewbieTrader', avatar: 'NT', role: 'member', time: '2 hari lalu',
        replies: 12, likes: 28, views: 176, preview: 'Halo semua, saya sudah setup webhook tapi masih error 401...'
    },
    {
        id: 6, category: 'Sinyal AI', title: 'Strategi SMC + GAS Signal — Win Rate 74% di XAUUSD',
        author: 'ProTrader_X', avatar: 'PX', role: 'pro', time: '3 hari lalu',
        replies: 31, likes: 127, views: 672, preview: 'Setelah 6 bulan live trading dengan kombinasi SMC dan sinyal GAS AI...'
    },
];

const ROLE_BADGE = {
    admin: { label: 'Admin', cls: 'bg-[var(--accent)] text-black' },
    pro: { label: 'Pro', cls: 'bg-purple-500/20 text-purple-400' },
    member: { label: 'Member', cls: 'bg-[var(--bg-hover)] text-[var(--text-dim)]' },
};

export default function ForumView() {
    const [cat, setCat] = useState('Semua');
    const [search, setSearch] = useState('');

    const filtered = THREADS.filter(t =>
        (cat === 'Semua' || t.category === cat) &&
        (!search || t.title.toLowerCase().includes(search.toLowerCase()))
    );

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-5xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                    <Users size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Forum VIP</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Komunitas Eksklusif GAS Pro Traders</p>
                    </div>
                    <Crown size={16} className="text-[var(--accent)] ml-1" />
                </div>
                <button className="flex items-center gap-2 bg-[var(--accent)] text-black font-black px-4 py-2 rounded-lg text-xs hover:opacity-90 transition-opacity">
                    <Plus size={14} /> Buat Thread
                </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 sm:grid-cols-4 gap-3">
                {[
                    { label: 'Member Aktif', value: '2,847', icon: <Users size={14} /> },
                    { label: 'Thread', value: '1,203', icon: <MessageCircle size={14} /> },
                    { label: 'Online Kini', value: '142', icon: <div className="w-2 h-2 rounded-full bg-[var(--success)]" /> },
                    { label: 'Pro Members', value: '891', icon: <Crown size={14} /> },
                ].map((s, i) => (
                    <div key={i} className="p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] flex items-center gap-3">
                        <div className="text-[var(--accent)]">{s.icon}</div>
                        <div>
                            <p className="text-sm font-display font-black text-[var(--text-primary)]">{s.value}</p>
                            <p className="text-[7px] font-black uppercase text-[var(--text-dim)]">{s.label}</p>
                        </div>
                    </div>
                ))}
            </div>

            {/* Filter + Search */}
            <div className="flex flex-wrap gap-3 items-center">
                <div className="flex items-center gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 flex-1 min-w-48">
                    <Search size={12} className="text-[var(--text-dim)]" />
                    <input value={search} onChange={e => setSearch(e.target.value)} placeholder="Cari thread..."
                        className="bg-transparent text-xs font-bold text-[var(--text-primary)] outline-none w-full placeholder:text-[var(--text-dim)]" />
                </div>
                <div className="flex flex-wrap gap-1">
                    {CATEGORIES.map(c => (
                        <button key={c} onClick={() => setCat(c)}
                            className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${cat === c ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)]'}`}>
                            {c}
                        </button>
                    ))}
                </div>
            </div>

            {/* Thread List */}
            <div className="space-y-3">
                {filtered.map(t => {
                    const badge = ROLE_BADGE[t.role];
                    return (
                        <div key={t.id} className={`p-4 rounded-xl border transition-all hover:border-[var(--text-dim)] cursor-pointer ${t.pinned ? 'bg-[var(--accent)]/5 border-[var(--accent)]/20' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                            <div className="flex items-start gap-3">
                                {/* Avatar */}
                                <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 flex items-center justify-center text-[9px] font-black text-black shrink-0">
                                    {t.avatar}
                                </div>

                                <div className="flex-1 min-w-0">
                                    {/* Title row */}
                                    <div className="flex flex-wrap items-center gap-2 mb-1">
                                        {t.pinned && <Pin size={10} className="text-[var(--accent)] shrink-0" />}
                                        <span className="text-[8px] bg-[var(--bg-hover)] text-[var(--text-dim)] font-black px-2 py-0.5 rounded uppercase">{t.category}</span>
                                    </div>
                                    <p className="text-sm font-bold text-[var(--text-primary)] mb-1 leading-tight">{t.title}</p>
                                    <p className="text-[9px] text-[var(--text-dim)] mb-2 line-clamp-1">{t.preview}</p>

                                    {/* Meta */}
                                    <div className="flex flex-wrap items-center gap-3 text-[8px] text-[var(--text-dim)]">
                                        <div className="flex items-center gap-1">
                                            <span className="font-bold text-[var(--text-secondary)]">{t.author}</span>
                                            <span className={`px-1.5 py-0.5 rounded font-black ${badge.cls}`}>{badge.label}</span>
                                        </div>
                                        <span>{t.time}</span>
                                        <div className="flex items-center gap-1"><MessageCircle size={9} />{t.replies}</div>
                                        <div className="flex items-center gap-1"><ThumbsUp size={9} />{t.likes}</div>
                                        <span>{t.views} views</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* VIP CTA */}
            <div className="p-5 rounded-xl bg-gradient-to-r from-[var(--accent)]/10 to-purple-500/10 border border-[var(--accent)]/30 text-center">
                <Crown size={24} className="text-[var(--accent)] mx-auto mb-2" />
                <p className="text-sm font-black text-[var(--text-primary)] mb-1">Upgrade ke Pro untuk Akses Forum VIP Penuh</p>
                <p className="text-[10px] text-[var(--text-dim)] mb-3">Chat langsung dengan expert trader, akses signal private & group eksklusif</p>
                <button className="bg-[var(--accent)] text-black font-black px-6 py-2 rounded-lg text-xs hover:opacity-90 transition-opacity">
                    Upgrade Sekarang
                </button>
            </div>
        </div>
    );
}
