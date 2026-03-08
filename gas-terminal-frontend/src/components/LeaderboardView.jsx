import React, { useState } from 'react';
import { Trophy, TrendingUp, TrendingDown, Crown, Medal, Award } from 'lucide-react';

const PERIODS = ['Minggu Ini', 'Bulan Ini', 'All Time'];

const LEADERBOARD = [
    { rank: 1, name: 'ProTrader_X', avatar: 'PX', country: '🇮🇩', pnl: 12480, winRate: 78.4, trades: 142, badge: 'Legendary', streak: 12 },
    { rank: 2, name: 'GoldHunter99', avatar: 'GH', country: '🇲🇾', pnl: 9840, winRate: 74.1, trades: 98, badge: 'Master', streak: 8 },
    { rank: 3, name: 'SMC_King', avatar: 'SK', country: '🇸🇬', pnl: 8230, winRate: 71.2, trades: 86, badge: 'Diamond', streak: 5 },
    { rank: 4, name: 'EliteTrader_Z', avatar: 'EZ', country: '🇮🇩', pnl: 6750, winRate: 68.9, trades: 74, badge: 'Platinum', streak: 3 },
    { rank: 5, name: 'QuantMaster', avatar: 'QM', country: '🇵🇭', pnl: 5980, winRate: 66.3, trades: 91, badge: 'Gold', streak: 7 },
    { rank: 6, name: 'TradingNinja', avatar: 'TN', country: '🇮🇩', pnl: 5210, winRate: 65.0, trades: 63, badge: 'Gold', streak: 2 },
    { rank: 7, name: 'ForexPhoenix', avatar: 'FP', country: '🇹🇭', pnl: 4890, winRate: 63.7, trades: 58, badge: 'Silver', streak: 4 },
    { rank: 8, name: 'CryptoSurfer', avatar: 'CS', country: '🇮🇩', pnl: 4120, winRate: 61.4, trades: 77, badge: 'Silver', streak: 1 },
    { rank: 9, name: 'GoldenEagle', avatar: 'GE', country: '🇲🇾', pnl: 3750, winRate: 60.2, trades: 52, badge: 'Bronze', streak: 0 },
    { rank: 10, name: 'MarketWizard', avatar: 'MW', country: '🇸🇬', pnl: 3280, winRate: 58.9, trades: 45, badge: 'Bronze', streak: 0 },
];

const BADGE_COLORS = {
    Legendary: { bg: 'from-yellow-400 to-amber-600', text: 'text-amber-900', icon: <Crown size={10} /> },
    Master: { bg: 'from-purple-400 to-purple-600', text: 'text-purple-100', icon: <Trophy size={10} /> },
    Diamond: { bg: 'from-cyan-400 to-blue-500', text: 'text-blue-100', icon: <Trophy size={10} /> },
    Platinum: { bg: 'from-slate-300 to-slate-500', text: 'text-slate-900', icon: <Medal size={10} /> },
    Gold: { bg: 'from-yellow-500 to-yellow-700', text: 'text-yellow-100', icon: <Medal size={10} /> },
    Silver: { bg: 'from-gray-300 to-gray-500', text: 'text-gray-900', icon: <Medal size={10} /> },
    Bronze: { bg: 'from-amber-600 to-amber-800', text: 'text-amber-100', icon: <Award size={10} /> },
};

const RANK_ICON = {
    1: <Crown size={16} className="text-yellow-400" />,
    2: <Trophy size={16} className="text-slate-400" />,
    3: <Trophy size={16} className="text-amber-700" />,
};

// My rank mock
const MY_RANK = { rank: 38, name: 'Kamu', avatar: 'ME', country: '🇮🇩', pnl: 1240, winRate: 58.3, trades: 24, badge: 'Silver', streak: 2 };

export default function LeaderboardView() {
    const [period, setPeriod] = useState('Bulan Ini');

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
                <div className="flex gap-1">
                    {PERIODS.map(p => (
                        <button key={p} onClick={() => setPeriod(p)}
                            className={`px-3 py-1.5 rounded-lg text-[9px] font-black uppercase transition-all ${period === p ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-dim)]'}`}>
                            {p}
                        </button>
                    ))}
                </div>
            </div>

            {/* Top 3 Podium */}
            <div className="grid grid-cols-3 gap-3">
                {[LEADERBOARD[1], LEADERBOARD[0], LEADERBOARD[2]].map((t, i) => {
                    const podiumRank = [2, 1, 3][i];
                    const heights = ['h-24', 'h-32', 'h-20'];
                    const badge = BADGE_COLORS[t.badge];
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
                                <p className="text-xs font-display font-black text-[var(--success)]">+${t.pnl.toLocaleString()}</p>
                            </div>
                            <div className={`w-full ${heights[i]} bg-gradient-to-t ${i === 1 ? 'from-yellow-400/20 to-yellow-400/5 border-t-2 border-yellow-400' : i === 0 ? 'from-slate-400/10 to-transparent border-t-2 border-slate-400' : 'from-amber-700/10 to-transparent border-t-2 border-amber-700'} rounded-t-lg flex items-center justify-center`}>
                                <span className="text-2xl font-display font-black text-[var(--text-dim)]">#{podiumRank}</span>
                            </div>
                        </div>
                    );
                })}
            </div>

            {/* Full Table */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                                {['#', 'Trader', 'Badge', 'P&L', 'Win Rate', 'Trades', 'Streak'].map(h => (
                                    <th key={h} className="px-4 py-3 text-left text-[9px] font-black uppercase tracking-wider text-[var(--text-dim)]">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {LEADERBOARD.map(t => {
                                const badge = BADGE_COLORS[t.badge];
                                return (
                                    <tr key={t.rank} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors">
                                        <td className="px-4 py-3">
                                            <div className="flex items-center">{RANK_ICON[t.rank] || <span className="font-black text-[var(--text-dim)]">#{t.rank}</span>}</div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-2">
                                                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-yellow-400 to-yellow-600 flex items-center justify-center text-[8px] font-black text-black shrink-0">{t.avatar}</div>
                                                <div>
                                                    <p className="font-black text-[var(--text-primary)]">{t.name}</p>
                                                    <p className="text-[8px] text-[var(--text-dim)]">{t.country}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className={`text-[8px] font-black px-2 py-0.5 rounded bg-gradient-to-r ${badge.bg} ${badge.text}`}>{t.badge}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <span className="font-black text-[var(--success)]">+${t.pnl.toLocaleString()}</span>
                                        </td>
                                        <td className="px-4 py-3">
                                            <div className="flex items-center gap-2">
                                                <div className="w-12 h-1.5 bg-[var(--bg-hover)] rounded-full">
                                                    <div className="h-1.5 bg-[var(--success)] rounded-full" style={{ width: `${t.winRate}%` }} />
                                                </div>
                                                <span className="text-[var(--text-secondary)] font-bold">{t.winRate}%</span>
                                            </div>
                                        </td>
                                        <td className="px-4 py-3 text-[var(--text-dim)] font-bold">{t.trades}</td>
                                        <td className="px-4 py-3">
                                            {t.streak > 0 ? (
                                                <span className="text-[8px] font-black px-2 py-0.5 rounded bg-[var(--success)]/10 text-[var(--success)]">🔥 {t.streak} Win</span>
                                            ) : (
                                                <span className="text-[8px] text-[var(--text-dim)]">-</span>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* My Rank */}
            <div className="p-4 rounded-xl bg-[var(--accent)]/5 border border-[var(--accent)]/30 flex items-center gap-4">
                <div className="w-9 h-9 rounded-full bg-[var(--accent)] flex items-center justify-center text-[10px] font-black text-black">{MY_RANK.avatar}</div>
                <div className="flex-1">
                    <p className="text-[10px] text-[var(--text-dim)] font-bold uppercase">Posisi Kamu</p>
                    <p className="text-sm font-black text-[var(--text-primary)]">Rank #{MY_RANK.rank} · {MY_RANK.name}</p>
                </div>
                <div className="text-right">
                    <p className="text-sm font-display font-black text-[var(--success)]">+${MY_RANK.pnl.toLocaleString()}</p>
                    <p className="text-[9px] text-[var(--text-dim)]">{MY_RANK.winRate}% WR · {MY_RANK.trades} trades</p>
                </div>
            </div>
        </div>
    );
}
