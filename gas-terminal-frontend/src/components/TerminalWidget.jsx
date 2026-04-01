import React, { useState } from 'react';
import { Bot, X, Maximize2, Minimize2, Zap } from 'lucide-react';
import AIBloombergTerminal from './AIBloombergTerminal';

export default function TerminalWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  return (
    <>
      {/* AI Mentor chip — small square, sits just above pair ticker + bottom nav */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-[100px] right-3 z-50 w-10 h-10 rounded-xl shadow-lg bg-[var(--bg-card)] border border-[var(--accent)]/40 flex flex-col items-center justify-center gap-0.5 hover:border-[var(--accent)] hover:bg-[var(--accent-soft)] active:scale-95 transition-all duration-150"
          title="GAS AI Mentor"
        >
          <Bot size={15} className="text-[var(--accent)]" />
          <span className="text-[7px] font-black text-[var(--accent)] uppercase tracking-wider leading-none">AI</span>
        </button>
      )}

      {/* Widget Window */}
      {isOpen && (
        <div
          className={`fixed right-0 z-50 transition-all duration-300 ease-out transform ${
            isExpanded
              ? 'bottom-0 w-full h-[calc(100vh-40px)] md:w-[600px] md:h-[80vh] md:bottom-[100px] md:right-3 md:rounded-2xl'
              : 'bottom-[100px] right-3 w-[calc(100vw-24px)] sm:w-[380px] h-[480px] rounded-2xl'
          } bg-[var(--bg-main)] border border-[var(--border-color)] shadow-2xl flex flex-col overflow-hidden`}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-3 py-3 bg-[var(--bg-card)] border-b border-[var(--border-color)] shrink-0">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-yellow-400/20 flex items-center justify-center">
                <Bot size={14} className="text-[var(--accent)]" />
              </div>
              <span className="text-[11px] font-black uppercase tracking-widest text-[var(--accent)]">AI Mentor Terminal</span>
            </div>
            <div className="flex items-center gap-1.5">
              <button 
                onClick={() => setIsExpanded(!isExpanded)} 
                className="w-7 h-7 flex items-center justify-center rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-white"
                title={isExpanded ? "Restore" : "Maximize"}
              >
                {isExpanded ? <Minimize2 size={13} /> : <Maximize2 size={13} />}
              </button>
              <button 
                onClick={() => setIsOpen(false)} 
                className="w-7 h-7 flex items-center justify-center rounded-lg bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:text-red-400"
                title="Close"
              >
                <X size={15} />
              </button>
            </div>
          </div>

          {/* Terminal Content */}
          <div className="flex-1 overflow-hidden relative">
            <AIBloombergTerminal isFullHeight={true} hideHeader={true} />
          </div>
        </div>
      )}
    </>
  );
}
