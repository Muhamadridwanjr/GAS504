import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Send, Search, Cpu } from 'lucide-react';

export default function AIBloombergTerminal() {
    const [input, setInput] = useState('');
    const [history, setHistory] = useState([
        { type: 'system', content: 'GOLDEN AI CORE INITIALIZED. READY FOR COMMANDS.' },
        { type: 'ai', content: 'Sistem Terhubung ke MT5 Feed. Menunggu instruksi analisa...' }
    ]);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history]);

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!input.trim()) return;

        const userMsg = input.toUpperCase();
        setHistory(prev => [...prev, { type: 'user', content: userMsg }]);
        setInput('');

        // Simulation
        setTimeout(() => {
            let reply = "PERINTAH TIDAK DIKENALI. GUNAKAN 'HELP' UNTUK DAFTAR PERINTAH.";
            if (userMsg.includes('ANALISA')) reply = "MENGANALISA MARKET XAUUSD... SENTIMEN: BULLISH. LIQUIDITY DETECTED AT 2028.50.";
            if (userMsg.includes('HELP')) reply = "AVAILABLE COMMANDS: ANALISA [PAIR], STATUS, SIGNAL, MARKET_SCAN.";

            setHistory(prev => [...prev, { type: 'ai', content: reply }]);
        }, 600);
    };

    return (
        <div className="flex flex-col h-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-[var(--card-shadow)]">
            <div className="flex items-center justify-between px-4 py-2 bg-[var(--bg-card)] border-b border-[var(--border-color)]">
                <div className="flex items-center gap-2">
                    <Terminal size={12} className="text-[var(--accent)]" />
                    <span className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)]">GAS Terminal V2.0</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)] pulse-dot" />
                    <span className="text-[8px] font-bold text-[var(--text-dim)] uppercase">System Live</span>
                </div>
            </div>

            <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3 scrollbar-none font-mono text-[10px]">
                {history.map((msg, i) => (
                    <div key={i} className={`flex gap-3 ${msg.type === 'user' ? 'justify-end' : ''}`}>
                        <div className={`max-w-[85%] p-2 rounded-lg ${msg.type === 'user' ? 'bg-[var(--accent)] text-black font-bold' :
                                msg.type === 'system' ? 'text-[var(--text-dim)] border-l-2 border-[var(--text-dim)] pl-3' :
                                    'bg-[var(--bg-hover)] text-[var(--text-primary)] border border-[var(--border-color)]'
                            }`}>
                            {msg.type === 'ai' && <div className="flex items-center gap-1 mb-1 text-[8px] font-black text-[var(--accent)]"><Cpu size={10} /> GAS AI</div>}
                            <p className="leading-relaxed">{msg.content}</p>
                        </div>
                    </div>
                ))}
            </div>

            <form onSubmit={handleSubmit} className="p-3 bg-[var(--bg-card)] border-t border-[var(--border-color)] flex items-center gap-2">
                <span className="text-[var(--accent)] font-bold text-xs">{'>'}</span>
                <input
                    type="text"
                    value={input}
                    onChange={e => setInput(e.target.value)}
                    placeholder="Tanya AI atau masukkan perintah..."
                    className="flex-1 bg-transparent outline-none text-[10px] font-mono text-[var(--text-primary)] placeholder:text-[var(--text-dim)] uppercase"
                />
                <button type="submit" className="text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors">
                    <Send size={14} />
                </button>
            </form>
        </div>
    );
}
