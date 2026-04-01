import React, { useState, useEffect } from 'react';
import { Globe, Github, Cpu, Activity, ShieldCheck, User, Clock } from 'lucide-react';

// WIB = UTC+7. Date.now() is UTC ms. Adding 7h then reading UTC getters gives Jakarta time.
// This avoids getTimezoneOffset() which is browser-local and causes double-offset bugs.
const WIB_MS  = 7 * 60 * 60 * 1000;
const pad     = n => String(n).padStart(2, '0');
const DAYS    = ['Minggu','Senin','Selasa','Rabu','Kamis','Jumat','Sabtu'];
const MONTHS  = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'];

function getWIB() {
    const d   = new Date(Date.now() + WIB_MS);          // shift UTC → Jakarta
    const h   = d.getUTCHours(),   m = d.getUTCMinutes(), s = d.getUTCSeconds();
    const dow = d.getUTCDay(),   day = d.getUTCDate(), mon = d.getUTCMonth(), yr = d.getUTCFullYear();
    return {
        time: `${pad(h)}:${pad(m)}:${pad(s)}`,
        date: `${DAYS[dow]}, ${day} ${MONTHS[mon]} ${yr}`,
    };
}

export default function TerminalFooter({ isConnected }) {
    const [wib, setWib] = useState(getWIB());

    useEffect(() => {
        const timer = setInterval(() => setWib(getWIB()), 1000);
        return () => clearInterval(timer);
    }, []);

    return (
        <footer className="h-6 bg-[var(--bg-card)] border-t border-[var(--border-color)] flex items-center justify-between px-3 text-[9px] font-mono z-[100] shrink-0">
            {/* Left: Author & Version */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5 group cursor-pointer">
                    <User size={10} className="text-[var(--accent)]" />
                    <span className="text-[var(--text-dim)] uppercase font-bold">Owner:</span>
                    <span className="text-[var(--text-primary)] font-black hover:text-[var(--accent)] transition-colors">MUHAMADRIDWANJR</span>
                </div>
                <div className="h-3 w-px bg-[var(--border-color)]" />
                <div className="flex items-center gap-1.5">
                    <Cpu size={10} className="text-blue-400" />
                    <span className="text-[var(--text-dim)] uppercase font-bold">Build:</span>
                    <span className="text-[var(--text-primary)] font-black tracking-tight">V3.0.4-PRO [AI TEAM]</span>
                </div>
            </div>

            {/* Middle: Status */}
            <div className="hidden md:flex items-center gap-6">
                <div className="flex items-center gap-1.5">
                    <ShieldCheck size={10} className="text-[var(--success)]" />
                    <span className="text-[var(--success)] font-black uppercase tracking-tighter">Golden AI Security Active</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <Activity size={10} className={isConnected ? 'text-[var(--success)]' : 'text-[var(--danger)]'} />
                    <span className="text-[var(--text-dim)] uppercase font-bold">Network:</span>
                    <span className={isConnected ? 'text-[var(--success)] font-black' : 'text-[var(--danger)] font-black'}>
                        {isConnected ? 'STABLE' : 'OFFLINE'}
                    </span>
                </div>
                <div className="flex gap-3">
                    <a href="https://github.com/Muhamadridwanjr" target="_blank" rel="noreferrer"
                        className="text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">
                        <Github size={10} />
                    </a>
                    <a href="#" className="text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">
                        <Globe size={10} />
                    </a>
                </div>
            </div>

            {/* Right: WIB Jakarta Clock */}
            <div className="flex items-center gap-2 shrink-0">
                <Clock size={10} className="text-[var(--accent)]" />
                <span className="text-[var(--text-dim)] font-bold uppercase">Jakarta WIB:</span>
                <span className="text-[var(--accent)] font-black tabular-nums tracking-tight">{wib.time}</span>
                <span className="hidden sm:inline text-[var(--text-dim)] font-bold">•</span>
                <span className="hidden sm:inline text-[var(--text-primary)] font-bold">{wib.date}</span>
                <div className="flex items-center gap-1 px-2 py-0.5 bg-[var(--accent-soft)] rounded border border-[var(--accent)]/20 animate-pulse ml-1">
                    <div className="w-1 h-1 bg-[var(--accent)] rounded-full" />
                    <span className="text-[8px] text-[var(--accent)] font-black tracking-widest uppercase">Live</span>
                </div>
            </div>
        </footer>
    );
}
