import React from 'react';

export default function CalendarView({ events }) {
    const fallbackEvents = [
        { date: 'Mar 6', name: 'ADP Non-Farm Employment', impact: 'HIGH', time: '13:15' },
        { date: 'Mar 7', name: 'US Unemployment Claims', impact: 'MEDIUM', time: '13:30' },
        { date: 'Mar 8', name: 'Non-Farm Payrolls', impact: 'HIGH', time: '13:30' },
        { date: 'Mar 12', name: 'CPI Month over Month', impact: 'HIGH', time: '13:30' },
        { date: 'Mar 19', name: 'FOMC Statement', impact: 'HIGH', time: '18:00' },
    ];

    const displayEvents = events?.length ? events : fallbackEvents;

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-5xl mx-auto">
            <h2 className="text-2xl font-display font-black text-[var(--text-primary)] uppercase">Kalender Ekonomi</h2>
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                <table className="w-full text-xs">
                    <thead><tr className="text-[var(--text-dim)] border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                        {['Tanggal', 'Waktu', 'Event', 'Impact'].map(h => <th key={h} className="px-6 py-3.5 text-left font-bold uppercase tracking-wider">{h}</th>)}
                    </tr></thead>
                    <tbody>
                        {displayEvents.map((e, i) => (
                            <tr key={i} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors">
                                <td className="px-6 py-4 text-[var(--text-dim)] font-mono">{e.date}</td>
                                <td className="px-6 py-4 text-[var(--text-dim)] font-mono">{e.time}</td>
                                <td className="px-6 py-4 font-bold text-[var(--text-primary)]">{e.name}</td>
                                <td className="px-6 py-4">
                                    <span className={`px-2.5 py-1 rounded text-[9px] font-black tracking-widest ${e.impact === 'HIGH' ? 'bg-[var(--danger)]/10 text-[var(--danger)]' : 'bg-[var(--accent)]/10 text-[var(--accent)]'}`}>{e.impact}</span>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
