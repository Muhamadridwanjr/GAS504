import React from 'react';

export default function PortfolioView() {
    const stats = [
        { label: 'Saldo', value: '$18,410.50', sub: 'Total Ekuitas Aktif' },
        { label: 'P&L Hari Ini', value: '+$420.00', sub: '+2.34% vs Kemarin', green: true },
        { label: 'Win Rate', value: '72.5%', sub: 'Dari 1,240 Total Trade' },
        { label: 'Drawdown', value: '-4.2%', sub: 'Maksimal Drawdown', red: true },
    ];

    const trades = [
        { t: '11:20:41', a: 'XAUUSD', act: 'BUY', p: '2031.50', l: '0.10', pl: '+$84.00', up: true },
        { t: '11:13:41', a: 'BTCUSD', act: 'SELL', p: '64105.00', l: '0.01', pl: '-$32.00', up: false },
        { t: '11:06:41', a: 'NVDA', act: 'BUY', p: '175.49', l: '10', pl: '+$62.00', up: true },
        { t: '10:52:41', a: 'EURUSD', act: 'BUY', p: '1.0851', l: '0.50', pl: '+$31.00', up: true },
        { t: '09:14:22', a: 'XAUUSD', act: 'SELL', p: '2040.10', l: '0.10', pl: '-$12.50', up: false },
    ];

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
            <h2 className="text-2xl font-display font-black text-[var(--text-primary)] uppercase">Portofolio Akun</h2>

            <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
                {stats.map((s, i) => (
                    <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-6">
                        <p className="text-[10px] text-[var(--text-dim)] font-bold uppercase tracking-widest mb-2">{s.label}</p>
                        <p className={`text-3xl font-black font-mono mb-1 ${s.green ? 'text-[var(--success)]' : s.red ? 'text-[var(--danger)]' : 'text-[var(--text-primary)]'}`}>{s.value}</p>
                        <p className="text-[10px] text-[var(--text-dim)] font-bold">{s.sub}</p>
                    </div>
                ))}
            </div>

            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden mt-6">
                <div className="px-6 py-4 border-b border-[var(--border-color)] flex items-center justify-between bg-[var(--bg-panel)]">
                    <span className="text-xs font-black uppercase text-[var(--text-secondary)] tracking-widest">Riwayat Trade</span>
                    <button className="text-[10px] font-bold text-[var(--accent)] hover:underline">Export CSV</button>
                </div>
                <div className="overflow-x-auto scrollbar-none">
                    <table className="w-full text-xs">
                        <thead>
                            <tr className="text-[var(--text-dim)] border-b border-[var(--border-color)] bg-[var(--bg-card)]">
                                {['Waktu', 'Aset', 'Aksi', 'Harga Entry', 'Ukuran (Lot)', 'P&L'].map(h => (
                                    <th key={h} className="px-6 py-3 text-left font-bold uppercase tracking-wider">{h}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {trades.map((r, i) => (
                                <tr key={i} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors cursor-pointer">
                                    <td className="px-6 py-4 text-[var(--text-dim)] font-mono">{r.t}</td>
                                    <td className="px-6 py-4 font-bold text-[var(--text-primary)]">{r.a}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 rounded text-[9px] font-black tracking-widest ${r.up ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>
                                            {r.act}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 font-mono text-[var(--text-secondary)]">{r.p}</td>
                                    <td className="px-6 py-4 font-mono text-[var(--text-dim)]">{r.l}</td>
                                    <td className={`px-6 py-4 font-mono font-bold ${r.up ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>{r.pl}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
