import React, { useState, useEffect } from 'react';
import { Globe, Github, Cpu, Activity, ShieldCheck, User, ExternalLink } from 'lucide-react';

export default function TerminalFooter({ isConnected }) {
    const [time, setTime] = useState(new Date());

    useEffect(() => {
        const timer = setInterval(() => setTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    const formatTime = (date, timezone = 'Local') => {
        return date.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    };

    return (
        <footer className="h-6 bg-[var(--bg-card)] border-t border-[var(--border-color)] flex items-center justify-between px-3 text-[9px] font-mono z-[100] shrink-0">
            {/* Left Section: Author & Version */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-1.5 group cursor-pointer">
                    <User size={10} className="text-[var(--accent)]" />
                    <span className="text-[var(--text-dim)] uppercase font-bold">Terminal Owner:</span>
                    <span className="text-[var(--text-primary)] font-black hover:text-[var(--accent)] transition-colors">MUHAMADRIDWANJR</span>
                </div>
                <div className="h-3 w-px bg-[var(--border-color)]" />
                <div className="flex items-center gap-1.5">
                    <Cpu size={10} className="text-blue-400" />
                    <span className="text-[var(--text-dim)] uppercase font-bold">Build:</span>
                    <span className="text-[var(--text-primary)] font-black tracking-tight">V3.0.4-PRO [AI TEAM]</span>
                </div>
            </div>

            {/* Middle Section: System Health */}
            <div className="hidden md:flex items-center gap-6">
                <div className="flex items-center gap-1.5">
                    <ShieldCheck size={10} className="text-[var(--success)]" />
                    <span className="text-[var(--success)] font-black uppercase tracking-tighter">GAS Security Active</span>
                </div>
                <div className="flex items-center gap-1.5">
                    <Activity size={10} className={isConnected ? 'text-[var(--success)]' : 'text-[var(--danger)]'} />
                    <span className="text-[var(--text-dim)] uppercase font-bold">Network:</span>
                    <span className={isConnected ? 'text-[var(--success)] font-black' : 'text-[var(--danger)] font-black'}>
                        {isConnected ? 'STABLE' : 'OFFLINE'}
                    </span>
                </div>
                <div className="flex gap-3">
                    <a href="https://github.com/Muhamadridwanjr" target="_blank" rel="noreferrer" className="text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">
                        <Github size={10} />
                    </a>
                    <a href="#" className="text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">
                        <Globe size={10} />
                    </a>
                </div>
            </div>

            {/* Right Section: Multi-Clock */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2">
                    <span className="text-[var(--text-dim)] font-bold">LDN:</span>
                    <span className="text-[var(--text-primary)] font-black">{formatTime(time)}</span>
                </div>
                <div className="flex items-center gap-2">
                    <span className="text-[var(--accent)] font-bold">TERMINAL:</span>
                    <span className="text-[var(--accent)] font-black">{formatTime(time)}</span>
                </div>
                <div className="flex items-center gap-1.5 px-2 py-0.5 bg-[var(--accent-soft)] rounded border border-[var(--accent)]/20 animate-pulse">
                    <div className="w-1 h-1 bg-[var(--accent)] rounded-full" />
                    <span className="text-[8px] text-[var(--accent)] font-black tracking-widest uppercase">Live-Link</span>
                </div>
            </div>
        </footer>
    );
}
