import React from 'react';

export default function SettingsView({ preferences, onSave }) {
    const prefs = preferences || {
        notifications: true, sound: true, autoRefresh: true, darkMode: true
    };

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-2xl mx-auto">
            <h2 className="text-2xl font-display font-black text-[var(--text-primary)] uppercase">Pengaturan Terminal</h2>
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl divide-y divide-[var(--border-color)]">
                {[
                    { key: 'notifications', label: 'Notifikasi Sinyal Push', sub: 'Terima notifikasi di browser/HP saat sinyal baru' },
                    { key: 'sound', label: 'Audio Alert System', sub: 'Mainkan suara (ping) saat sinyal HOT masuk' },
                    { key: 'autoRefresh', label: 'Auto Refresh Data Feed', sub: 'Refresh harga real-time via WebSocket' },
                    { key: 'darkMode', label: 'Mode Gelap Ekstrem', sub: 'Gunakan palet warna High-Contrast Pro Terminal' },
                ].map((s, i) => (
                    <div key={i} className="flex items-center justify-between px-6 py-5">
                        <div>
                            <p className="text-sm font-bold text-[var(--text-primary)] mb-1">{s.label}</p>
                            <p className="text-[10px] text-[var(--text-dim)]">{s.sub}</p>
                        </div>
                        <div
                            onClick={() => onSave({ ...prefs, [s.key]: !prefs[s.key] })}
                            className={`w-10 h-5 rounded-full relative transition-colors cursor-pointer ${prefs[s.key] ? 'bg-[var(--accent)]' : 'bg-[var(--bg-hover)]'}`}
                        >
                            <div className={`absolute top-1 w-3 h-3 rounded-full bg-black transition-all ${prefs[s.key] ? 'left-6' : 'left-1'}`} />
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
