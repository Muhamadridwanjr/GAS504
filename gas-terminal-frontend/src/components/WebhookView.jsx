import React, { useState } from 'react';
import { Webhook, Copy, CheckCircle, Plus, Trash2, Eye, EyeOff, RefreshCw } from 'lucide-react';

const API_KEY = 'gas_live_sk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx';
const EVENTS = ['signal.new', 'signal.confirm', 'price.alert', 'trade.journal', 'ea.heartbeat', 'ea.context'];

const WEBHOOK_LOGS = [
    { ts: '14:32:01', event: 'signal.new', url: 'https://example.com/hooks/gas', status: 200, ms: 142 },
    { ts: '14:15:44', event: 'signal.confirm', url: 'https://example.com/hooks/gas', status: 200, ms: 98 },
    { ts: '13:58:22', event: 'price.alert', url: 'https://n8n.example.com/webhook', status: 200, ms: 215 },
    { ts: '13:30:10', event: 'ea.heartbeat', url: 'https://example.com/hooks/gas', status: 500, ms: 30 },
    { ts: '12:44:55', event: 'signal.new', url: 'https://n8n.example.com/webhook', status: 200, ms: 178 },
];

const SAMPLE_PAYLOAD = `{
  "event": "signal.new",
  "timestamp": "2025-03-08T14:32:01Z",
  "data": {
    "pair": "XAUUSD",
    "type": "BUY",
    "grade": "A+",
    "entry": "3310.00",
    "sl": "3295.00",
    "tp1": "3335.00",
    "tp2": "3355.00",
    "confidence": 9,
    "rr": "1:2.5"
  }
}`;

export default function WebhookView() {
    const [showKey, setShowKey] = useState(false);
    const [copied, setCopied] = useState('');
    const [hooks, setHooks] = useState([
        { id: 1, url: 'https://example.com/hooks/gas', events: ['signal.new', 'signal.confirm'], active: true },
    ]);
    const [form, setForm] = useState({ url: '', events: [] });
    const [showForm, setShowForm] = useState(false);

    const copy = (text, key) => {
        navigator.clipboard.writeText(text);
        setCopied(key);
        setTimeout(() => setCopied(''), 2000);
    };

    const toggleEvent = (ev) => {
        setForm(f => ({ ...f, events: f.events.includes(ev) ? f.events.filter(e => e !== ev) : [...f.events, ev] }));
    };

    const addHook = () => {
        if (!form.url || form.events.length === 0) return;
        setHooks(prev => [...prev, { id: Date.now(), ...form, active: true }]);
        setForm({ url: '', events: [] });
        setShowForm(false);
    };

    return (
        <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-4xl mx-auto">
            {/* Header */}
            <div className="flex items-center gap-2">
                <Webhook size={20} className="text-[var(--accent)]" />
                <div>
                    <h2 className="text-xl font-display font-black uppercase text-[var(--text-primary)]">API / Webhook</h2>
                    <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Integrasi GAS ke Sistem Eksternal via Webhook & REST API</p>
                </div>
            </div>

            {/* API Key */}
            <div className="p-5 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">API Key Anda</p>
                <div className="flex items-center gap-2">
                    <code className="flex-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-xs font-mono text-[var(--accent)] truncate">
                        {showKey ? API_KEY : '••••••••••••••••••••••••••••••••••••••••••••'}
                    </code>
                    <button onClick={() => setShowKey(!showKey)} className="p-2.5 bg-[var(--bg-hover)] rounded-lg hover:bg-[var(--bg-panel)] transition-colors">
                        {showKey ? <EyeOff size={14} className="text-[var(--text-dim)]" /> : <Eye size={14} className="text-[var(--text-dim)]" />}
                    </button>
                    <button onClick={() => copy(API_KEY, 'apikey')} className="p-2.5 bg-[var(--bg-hover)] rounded-lg hover:bg-[var(--bg-panel)] transition-colors">
                        {copied === 'apikey' ? <CheckCircle size={14} className="text-[var(--success)]" /> : <Copy size={14} className="text-[var(--text-dim)]" />}
                    </button>
                    <button className="p-2.5 bg-[var(--bg-hover)] rounded-lg hover:bg-[var(--bg-panel)] transition-colors">
                        <RefreshCw size={14} className="text-[var(--text-dim)]" />
                    </button>
                </div>
                <p className="text-[9px] text-[var(--text-dim)] mt-2">Gunakan header: <code className="text-[var(--accent)]">Authorization: Bearer {'<api_key>'}</code></p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Webhooks */}
                <div className="space-y-4">
                    <div className="flex items-center justify-between">
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Webhook Endpoints</p>
                        <button onClick={() => setShowForm(!showForm)} className="flex items-center gap-1 text-[10px] font-black text-[var(--accent)] hover:opacity-80 transition-opacity">
                            <Plus size={12} /> Tambah
                        </button>
                    </div>

                    {showForm && (
                        <div className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--accent)]/30 space-y-3">
                            <input value={form.url} onChange={e => setForm(f => ({ ...f, url: e.target.value }))} placeholder="https://your-app.com/webhooks/gas"
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 text-xs font-bold text-[var(--text-primary)] outline-none focus:border-[var(--accent)]" />
                            <div className="flex flex-wrap gap-1.5">
                                {EVENTS.map(ev => (
                                    <button key={ev} onClick={() => toggleEvent(ev)}
                                        className={`px-2 py-1 rounded text-[8px] font-black transition-all ${form.events.includes(ev) ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] text-[var(--text-dim)] border border-[var(--border-color)]'}`}>
                                        {ev}
                                    </button>
                                ))}
                            </div>
                            <div className="flex justify-end gap-2">
                                <button onClick={() => setShowForm(false)} className="text-xs font-bold text-[var(--text-dim)]">Batal</button>
                                <button onClick={addHook} className="px-3 py-1.5 bg-[var(--accent)] text-black font-black rounded-lg text-xs">Simpan</button>
                            </div>
                        </div>
                    )}

                    {hooks.map(h => (
                        <div key={h.id} className="p-4 rounded-xl bg-[var(--bg-card)] border border-[var(--border-color)]">
                            <div className="flex items-start gap-3">
                                <div className={`mt-1 w-2 h-2 rounded-full shrink-0 ${h.active ? 'bg-[var(--success)]' : 'bg-[var(--text-dim)]'}`} />
                                <div className="flex-1 min-w-0">
                                    <p className="text-xs font-bold text-[var(--text-primary)] truncate">{h.url}</p>
                                    <div className="flex flex-wrap gap-1 mt-1.5">
                                        {h.events.map(ev => (
                                            <span key={ev} className="text-[7px] bg-[var(--accent)]/10 text-[var(--accent)] font-black px-1.5 py-0.5 rounded">{ev}</span>
                                        ))}
                                    </div>
                                </div>
                                <button onClick={() => setHooks(prev => prev.filter(x => x.id !== h.id))} className="text-[var(--text-dim)] hover:text-[var(--danger)] transition-colors">
                                    <Trash2 size={14} />
                                </button>
                            </div>
                        </div>
                    ))}

                    {/* REST Endpoints */}
                    <div className="mt-6">
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-3">REST API Endpoints</p>
                        {[
                            { method: 'GET', path: '/terminal/signal/latest', desc: 'Sinyal AI terbaru' },
                            { method: 'GET', path: '/terminal/overview', desc: 'Data pasar lengkap' },
                            { method: 'GET', path: '/terminal/calendar', desc: 'Kalender ekonomi' },
                            { method: 'POST', path: '/terminal/ai/chat', desc: 'AI Chat/Analisa' },
                        ].map((ep, i) => (
                            <div key={i} className="flex items-center gap-3 py-2 border-b border-[var(--border-color)]">
                                <span className={`text-[8px] font-black px-1.5 py-0.5 rounded shrink-0 ${ep.method === 'GET' ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--accent)]/10 text-[var(--accent)]'}`}>{ep.method}</span>
                                <code className="text-[9px] font-mono text-[var(--text-secondary)] flex-1 truncate">{ep.path}</code>
                                <span className="text-[9px] text-[var(--text-dim)] hidden sm:block">{ep.desc}</span>
                                <button onClick={() => copy(`${ep.method} /terminal${ep.path}`, ep.path)} className="shrink-0">
                                    {copied === ep.path ? <CheckCircle size={12} className="text-[var(--success)]" /> : <Copy size={12} className="text-[var(--text-dim)]" />}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Logs + Payload */}
                <div className="space-y-6">
                    {/* Sample Payload */}
                    <div>
                        <div className="flex items-center justify-between mb-3">
                            <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)]">Contoh Payload</p>
                            <button onClick={() => copy(SAMPLE_PAYLOAD, 'payload')} className="flex items-center gap-1 text-[9px] font-black text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors">
                                {copied === 'payload' ? <CheckCircle size={10} className="text-[var(--success)]" /> : <Copy size={10} />}
                                Copy
                            </button>
                        </div>
                        <pre className="p-4 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)] text-[9px] font-mono text-[var(--text-secondary)] overflow-x-auto">
                            {SAMPLE_PAYLOAD}
                        </pre>
                    </div>

                    {/* Delivery Logs */}
                    <div>
                        <p className="text-[10px] font-black uppercase tracking-[0.2em] text-[var(--text-dim)] mb-3">Log Pengiriman Terbaru</p>
                        <div className="space-y-1.5">
                            {WEBHOOK_LOGS.map((log, i) => (
                                <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-[var(--bg-card)] border border-[var(--border-color)]">
                                    <span className="text-[8px] font-mono text-[var(--text-dim)] shrink-0">{log.ts}</span>
                                    <span className="text-[8px] font-black text-[var(--accent)] shrink-0">{log.event}</span>
                                    <span className="text-[8px] text-[var(--text-dim)] flex-1 truncate hidden sm:block">{log.url}</span>
                                    <span className={`text-[8px] font-black px-1.5 py-0.5 rounded shrink-0 ${log.status === 200 ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>{log.status}</span>
                                    <span className="text-[8px] text-[var(--text-dim)] shrink-0">{log.ms}ms</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
