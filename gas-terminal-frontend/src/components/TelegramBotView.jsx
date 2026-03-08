import React, { useState } from 'react';
import { Bot, Copy, CheckCircle, Settings, Send, Bell, Zap } from 'lucide-react';

const BOT_COMMANDS = [
    { cmd: '/signal', desc: 'Dapatkan sinyal AI terbaru untuk semua pair aktif' },
    { cmd: '/signal XAUUSD', desc: 'Sinyal AI untuk pair tertentu (contoh: XAUUSD)' },
    { cmd: '/price BTCUSD', desc: 'Cek harga realtime sebuah pair' },
    { cmd: '/summary', desc: 'Ringkasan pasar & analisa AI hari ini' },
    { cmd: '/calendar', desc: 'Jadwal event ekonomi penting minggu ini' },
    { cmd: '/status', desc: 'Status koneksi & info akun Anda' },
    { cmd: '/help', desc: 'Tampilkan semua perintah tersedia' },
];

const NOTIF_OPTIONS = [
    { id: 'signal', label: 'Sinyal AI Baru', desc: 'Notifikasi setiap ada sinyal AI masuk', defaultOn: true },
    { id: 'price_alert', label: 'Peringatan Harga', desc: 'Alert saat harga menyentuh target', defaultOn: true },
    { id: 'news', label: 'Berita High Impact', desc: 'Berita ekonomi berdampak tinggi', defaultOn: false },
    { id: 'daily', label: 'Laporan Harian', desc: 'Ringkasan trading setiap hari pukul 08:00', defaultOn: false },
    { id: 'signal_confirm', desc: 'Konfirmasi sinyal yang dieksekusi EA', label: 'Konfirmasi EA', defaultOn: true },
];

export default function TelegramBotView() {
    const [token] = useState('GAS_BOT_XXXXXXXXXXX');
    const [chatId, setChatId] = useState('');
    const [copied, setCopied] = useState(false);
    const [connected, setConnected] = useState(false);
    const [notifs, setNotifs] = useState(() => Object.fromEntries(NOTIF_OPTIONS.map(o => [o.id, o.defaultOn])));
    const [testSending, setTestSending] = useState(false);

    const copy = () => {
        navigator.clipboard.writeText(token).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    };

    const connect = () => {
        if (!chatId) return;
        setConnected(true);
    };

    const sendTest = () => {
        setTestSending(true);
        setTimeout(() => setTestSending(false), 1800);
    };

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Bot size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">Bot Telegram</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Notifikasi & Perintah AI via Telegram</p>
                </div>
            </div>

            {/* Status Banner */}
            <div className={`p-4 rounded-xl border flex items-center gap-4 ${connected ? 'bg-[var(--success)]/5 border-[var(--success)]/30' : 'bg-[var(--bg-card)] border-[var(--border-color)]'}`}>
                <div className={`p-3 rounded-xl ${connected ? 'bg-[var(--success)]/10' : 'bg-[var(--bg-hover)]'}`}>
                    <Bot size={24} className={connected ? 'text-[var(--success)]' : 'text-[var(--text-dim)]'} />
                </div>
                <div>
                    <p className="text-sm font-black text-[var(--text-primary)]">{connected ? '@GoldenAIStrategy_bot' : 'Bot Telegram Belum Terhubung'}</p>
                    <p className="text-[10px] text-[var(--text-dim)]">{connected ? 'Bot aktif · Chat ID terdaftar · Siap menerima perintah' : 'Hubungkan bot Telegram Anda untuk menerima notifikasi sinyal'}</p>
                </div>
                <div className={`ml-auto w-2.5 h-2.5 rounded-full ${connected ? 'bg-[var(--success)]' : 'bg-[var(--text-dim)]'}`} />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Setup Steps */}
                <div className="space-y-4">
                    <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Cara Menghubungkan Bot</p>

                    <div className="space-y-3">
                        {[
                            {
                                step: '1', title: 'Buka Bot Telegram',
                                content: (
                                    <a href="#" className="flex items-center gap-2 px-3 py-2 bg-[var(--bg-panel)] rounded-lg text-xs font-bold text-[var(--accent)] hover:opacity-80 transition-opacity">
                                        <Bot size={14} /> @GoldenAIStrategy_bot
                                    </a>
                                )
                            },
                            {
                                step: '2', title: 'Kirim token ini ke bot',
                                content: (
                                    <div className="flex items-center gap-2">
                                        <code className="flex-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-[10px] font-mono text-[var(--accent)] truncate">{token}</code>
                                        <button onClick={copy} className="shrink-0 p-2 bg-[var(--bg-hover)] rounded-lg hover:bg-[var(--accent)]/10 transition-colors">
                                            {copied ? <CheckCircle size={14} className="text-[var(--success)]" /> : <Copy size={14} className="text-[var(--text-dim)]" />}
                                        </button>
                                    </div>
                                )
                            },
                            {
                                step: '3', title: 'Masukkan Chat ID Anda',
                                content: (
                                    <div className="flex gap-2">
                                        <input value={chatId} onChange={e => setChatId(e.target.value)} placeholder="Contoh: 123456789"
                                            className="flex-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
                                        <button onClick={connect}
                                            className="px-3 py-2 bg-[var(--accent)] text-black font-black rounded-lg text-xs hover:opacity-90 transition-opacity">
                                            Hubungkan
                                        </button>
                                    </div>
                                )
                            },
                        ].map((s, i) => (
                            <div key={i} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                <div className="flex items-center gap-3 mb-3">
                                    <span className="w-6 h-6 rounded-full bg-[var(--accent)] text-black text-[10px] font-black flex items-center justify-center shrink-0">{s.step}</span>
                                    <p className="text-xs font-bold text-[var(--text-primary)]">{s.title}</p>
                                </div>
                                {s.content}
                            </div>
                        ))}

                        {connected && (
                            <button onClick={sendTest} disabled={testSending}
                                className="w-full flex items-center justify-center gap-2 bg-[var(--bg-card)] border border-[var(--success)]/30 text-[var(--success)] font-black px-4 py-3 rounded-xl text-xs hover:bg-[var(--success)]/5 transition-all disabled:opacity-50">
                                {testSending ? (
                                    <><div className="w-3 h-3 border-2 border-[var(--success)] border-t-transparent rounded-full animate-spin" />Mengirim...</>
                                ) : (
                                    <><Send size={14} />Kirim Pesan Test</>
                                )}
                            </button>
                        )}
                    </div>
                </div>

                {/* Notifications & Commands */}
                <div className="space-y-6">
                    {/* Notification Settings */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Pengaturan Notifikasi</p>
                        <div className="space-y-2">
                            {NOTIF_OPTIONS.map(o => (
                                <div key={o.id} className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                                    <div className="flex-1">
                                        <p className="text-xs font-bold text-[var(--text-primary)]">{o.label}</p>
                                        <p className="text-[9px] text-[var(--text-dim)]">{o.desc}</p>
                                    </div>
                                    <button onClick={() => setNotifs(n => ({ ...n, [o.id]: !n[o.id] }))}
                                        className={`relative w-10 h-5 rounded-full transition-colors shrink-0 ${notifs[o.id] ? 'bg-[var(--success)]' : 'bg-[var(--bg-hover)]'}`}>
                                        <div className={`absolute top-0.5 w-4 h-4 bg-white rounded-full shadow transition-transform ${notifs[o.id] ? 'translate-x-5' : 'translate-x-0.5'}`} />
                                    </button>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Commands */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-4">Perintah Bot Tersedia</p>
                        <div className="space-y-1.5">
                            {BOT_COMMANDS.map((c, i) => (
                                <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)] hover:border-[var(--text-dim)] transition-all">
                                    <code className="text-[10px] font-mono font-black text-[var(--accent)] shrink-0 mt-0.5">{c.cmd}</code>
                                    <p className="text-[9px] text-[var(--text-dim)]">{c.desc}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
