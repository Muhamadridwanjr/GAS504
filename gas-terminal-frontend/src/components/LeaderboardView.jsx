import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Trophy, Crown, Medal, Award, RefreshCw } from 'lucide-react';

const WEB_API = '/web/api/v1';
const getHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('gas-token') || ''}` });

const PERIODS = ['All Time', 'Bulan Ini', 'Minggu Ini'];
const PERIOD_MAP = { 'All Time': 'all', 'Bulan Ini': 'month', 'Minggu Ini': 'week' };

const BADGE_COLORS = {
    Legendary: { bg: 'from-yellow-400 to-amber-600', text: 'text-amber-900' },
    Master:    { bg: 'from-purple-400 to-purple-600', text: 'text-purple-100' },
    Diamond:   { bg: 'from-cyan-400 to-blue-500',    text: 'text-blue-100' },
    Platinum:  { bg: 'from-slate-300 to-slate-500',  text: 'text-slate-900' },
    Gold:      { bg: 'from-yellow-500 to-yellow-700', text: 'text-yellow-100' },
    Silver:    { bg: 'from-gray-300 to-gray-500',    text: 'text-gray-900' },
    Bronze:    { bg: 'from-amber-600 to-amber-800',  text: 'text-amber-100' },
};

const RANK_ICON = {
    1: <Crown size={16} className="text-yellow-400" />,
    2: <Trophy size={16} className="text-slate-400" />,
    3: <Trophy size={16} className="text-amber-700" />,
};

export default function LeaderboardView() {
    const [period, setPeriod] = useState('All Time');
    const [data, setData] = useState({ leaderboard: [], my_rank: null, total: 0 });
    const [loading, setLoading] = useState(true);

    const fetchLeaderboard = useCallback(async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${WEB_API}/leaderboard`, {
                params: { period: PERIOD_MAP[period], limit: 10 },
                headers: getHeaders(),
            });
            setData(res.data);
        } catch {
            setData({ leaderboard: [], my_rank: null, total: 0 });
        } finally {
            setLoading(false);
        }
    }, [period]);

    useEffect(() => { fetchLeaderboard(); }, [fetchLeaderboard]);

    const board = data.leaderboard || [];
    const myRank = data.my_rank;
    const top3 = board.slice(0, 3);

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div className="flex items-center gap-2">
                    <Trophy size={20} className="text-[var(--accent)]" />
                    <div>
                        <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Papan Peringkat</h2>
                        <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Top Traders GAS Ecosystem</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex gap-1">
                        {PERIODS.map(p => (
                            <button key={p} onClick={() => setPeriod(p)}
                                className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${period === p ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)]'}`}>
                                {p}
                            </button>
                        ))}
                    </div>
                    <button onClick={fetchLeaderboard}
                        className="p-1.5 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-lg hover:border-[var(--accent)] transition">
                        <RefreshCw size={12} className={`text-[var(--text-dim)] ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </div>

            {/* Loading state */}
            {loading && (
                <div className="flex items-center justify-center py-12 gap-2 text-[var(--text-dim)]">
                    <RefreshCw size={16} className="animate-spin" />
                    <span className="text-sm">Memuat leaderboard...</span>
                </div>
            )}

            {/* Empty state */}
            {!loading && board.length === 0 && (
                <div className="text-center py-16">
                    <Trophy size={40} className="mx-auto mb-3 text-[var(--text-dim)] opacity-20" />
                    <p className="text-sm font-bold text-[var(--text-dim)]">Leaderboard masih kosong</p>
                    <p className="text-[10px] text-[var(--text-dim)] mt-1">Mulai catat trade di Jurnal untuk masuk peringkat!</p>
                </div>
            )}

            {/* Top 3 Podium */}
            {!loading && top3.length >= 3 && (
                <div className="grid grid-cols-3 gap-3">
                    {[top3[1], top3[0], top3[2]].map((t, i) => {
                        const podiumRank = [2, 1, 3][i];
                        const heights = ['h-24', 'h-32', 'h-20'];
                        if (!t) return <div key={i} />;
                        return (
                            <div key={t.rank} className={`flex flex-col items-center justify-end ${i === 1 ? 'order-2' : i === 0 ? 'order-1' : 'order-3'}`}>
                                <div className="text-center mb-2">
                                    <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 flex items-center justify-center text-xs font-black text-black mx-auto mb-1 shadow-lg">
                                        {t.avatar}
                                    </div>
                                    <div className="flex items-center justify-center gap-1 mb-0.5">
                                        {RANK_ICON[podiumRank]}
                                    </div>
                                    <p className="text-[9px] font-black text-[var(--text-primary)]">{t.name}</p>
                                    <p className="text-xs font-display font-black text-[var(--success)]">
                                        {t.pnl >= 0 ? '+' : ''}${t.pnl.toLocaleString()}
                                    </p>
                                </div>
                                <div className={`w-full ${heights[i]} bg-gradient-to-t ${
                                    i === 1 ? 'from-yellow-400/20 to-yellow-400/5 border-t-2 border-yellow-400'
                                    : i === 0 ? 'from-slate-400/10 to-transparent border-t-2 border-slate-400'
                                    : 'from-amber-700/10 to-transparent border-t-2 border-amber-700'
                                } rounded-t-lg flex items-center justify-center`}>
                                    <span className="text-2xl font-display font-black text-[var(--text-dim)]">#{podiumRank}</span>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}

            {/* Full Table */}
            {!loading && board.length > 0 && (
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-xs">
                            <thead>
                                <tr className="border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                                    {['#', 'Trader', 'Badge', 'P&L', 'Win Rate', 'Trades', 'Level'].map(h => (
                                        <th key={h} className="px-4 py-3 text-left text-[9px] font-black uppercase tracking-wider text-[var(--text-dim)]">{h}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {board.map(t => {
                                    const badge = BADGE_COLORS[t.badge] || BADGE_COLORS.Bronze;
                                    return (
                                        <tr key={t.rank} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors">
                                            <td className="px-4 py-3">
                                                <div className="flex items-center">{RANK_ICON[t.rank] || <span className="font-black text-[var(--text-dim)]">#{t.rank}</span>}</div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 flex items-center justify-center text-[8px] font-black text-black shrink-0">{t.avatar}</div>
                                                    <p className="font-black text-[var(--text-primary)]">{t.name}</p>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`text-[8px] font-black px-2 py-0.5 rounded bg-gradient-to-r ${badge.bg} ${badge.text}`}>{t.badge}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className={`font-black ${t.pnl >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                    {t.pnl >= 0 ? '+' : ''}${Math.abs(t.pnl).toLocaleString()}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <div className="flex items-center gap-2">
                                                    <div className="w-12 h-1.5 bg-[var(--bg-hover)] rounded-full">
                                                        <div className="h-1.5 bg-[var(--success)] rounded-full" style={{ width: `${t.win_rate}%` }} />
                                                    </div>
                                                    <span className="text-[var(--text-secondary)] font-bold">{t.win_rate}%</span>
                                                </div>
                                            </td>
                                            <td className="px-4 py-3 text-[var(--text-dim)] font-bold">{t.trades}</td>
                                            <td className="px-4 py-3">
                                                <span className="text-[8px] font-black px-2 py-0.5 rounded bg-[var(--accent)]/10 text-[var(--accent)]">Lv.{t.level}</span>
                                            </td>
                                        </tr>
                                    );
                                })}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* My Rank */}
            {myRank && (
                <div className="p-4 rounded-xl bg-[var(--accent)]/5 border border-[var(--accent)]/30 flex items-center gap-4">
                    <div className="w-9 h-9 rounded-full bg-[var(--accent)] flex items-center justify-center text-[10px] font-black text-black">
                        {myRank.name?.slice(0, 2).toUpperCase()}
                    </div>
                    <div className="flex-1">
                        <p className="text-[10px] text-[var(--text-dim)] font-bold uppercase">Posisi Kamu</p>
                        <p className="text-sm font-black text-[var(--text-primary)]">
                            Rank #{myRank.rank} dari {myRank.total_users} · {myRank.name}
                        </p>
                    </div>
                    <div className="text-right">
                        <p className={`text-sm font-display font-black ${myRank.pnl >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                            {myRank.pnl >= 0 ? '+' : ''}${Math.abs(myRank.pnl).toLocaleString()}
                        </p>
                        <p className="text-[9px] text-[var(--text-dim)]">{myRank.trades} trades · Lv.{myRank.level}</p>
                    </div>
                </div>
            )}
        </div>
    );
}
