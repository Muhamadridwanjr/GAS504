import React, { useState, useRef, useEffect, useCallback } from 'react';
import {
  Terminal, Send, Cpu, ChevronRight, Zap,
  TrendingUp, Globe, Radio, RefreshCw, BarChart2, Layers
} from 'lucide-react';
import { sendAIChat } from '../services/api';

// ─── Pairs & analysis modes ──────────────────────────────────────────────────
const PAIRS = ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'GBPJPY', 'BTCUSD', 'NASDAQ', 'US30'];

const MODES = {
  TECH: { label: 'Technical', icon: TrendingUp, color: 'text-emerald-400', border: 'border-emerald-400/40', bg: 'bg-emerald-400/10 hover:bg-emerald-400/20', cmd: (p) => `ANLS ${p}` },
  FUND: { label: 'Fundamental', icon: Globe, color: 'text-blue-400', border: 'border-blue-400/40', bg: 'bg-blue-400/10 hover:bg-blue-400/20', cmd: (p) => `FUND ${p}` },
  HYBRID: { label: 'Hybrid', icon: Layers, color: 'text-purple-400', border: 'border-purple-400/40', bg: 'bg-purple-400/10 hover:bg-purple-400/20', cmd: (p) => `ANLS ${p} FUND` },
};

const MARKET_CMDS = [
  { label: 'NEWS', sub: 'Berita', cmd: 'NEWS', icon: Radio, color: 'text-amber-400', bg: 'bg-amber-400/10 hover:bg-amber-400/20', border: 'border-amber-400/40' },
  { label: 'SGNL', sub: 'Sinyal', cmd: 'SGNL', icon: Zap, color: 'text-cyan-400', bg: 'bg-cyan-400/10 hover:bg-cyan-400/20', border: 'border-cyan-400/40' },
  { label: 'HELP', sub: 'Panduan', cmd: 'HELP', icon: Terminal, color: 'text-slate-400', bg: 'bg-slate-400/10 hover:bg-slate-400/20', border: 'border-slate-400/40' },
];

const ALL_MODELS = [
  { id: 'KIMI-2.5', label: 'Kimi V2.5 (High Speed)' },
  { id: 'DEEPSEEK-V3', label: 'DeepSeek V3 (Technical)' },
  { id: 'DEEPSEEK-R1', label: 'DeepSeek R1 (SMC Logic)' },
  { id: 'GEMINI-2.0-FLASH', label: 'Gemini 2.0 Flash' },
  { id: 'GEMINI-2.0-PRO', label: 'Gemini 2.0 Pro' },
  { id: 'GPT-OSS-120B', label: 'GPT OSS 120B' },
  { id: 'GLM-4.7', label: 'GLM 4.7 (Macro)' },
  { id: 'QWEN-3', label: 'Qwen 3 (Quant Logic)' },
  { id: 'MINIMAX-M2', label: 'MiniMax-M2' },
  { id: 'CLAUDE-3.5-HAIKU', label: 'Claude 3.5 Haiku' },
  { id: 'CLAUDE-3.7-SONNET', label: 'Claude 3.7 Sonnet' },
  { id: 'CLAUDE-OPUS-4', label: 'Claude Opus 4' },
];

// ─── Structured AI output renderer ──────────────────────────────────────────
function RenderAI({ text }) {
  const lines = String(text).split('\n');
  const elements = [];
  let inCode = false;
  let codeLines = [];

  lines.forEach((raw, i) => {
    const line = raw;
    const trimmed = line.trim();

    // Code block toggle
    if (trimmed.startsWith('```')) {
      if (inCode) {
        elements.push(
          <pre key={`code-${i}`} className="bg-black/40 border border-[var(--border-color)] rounded p-2 text-[9px] text-emerald-300 font-mono overflow-x-auto my-1 whitespace-pre-wrap">
            {codeLines.join('\n')}
          </pre>
        );
        codeLines = [];
        inCode = false;
      } else {
        inCode = true;
      }
      return;
    }
    if (inCode) { codeLines.push(line); return; }

    // Blank line
    if (!trimmed) { elements.push(<div key={i} className="h-1.5" />); return; }

    // Horizontal rule ---
    if (trimmed === '---' || trimmed.match(/^─{3,}$/)) {
      elements.push(<div key={i} className="my-2 border-t border-[var(--border-color)] opacity-40" />);
      return;
    }

    // ## Section header (with emoji)
    if (trimmed.startsWith('## ') || trimmed.startsWith('##')) {
      const txt = trimmed.replace(/^#+\s*/, '');
      elements.push(
        <p key={i} className="text-[var(--accent)] font-black text-[10px] mt-3 mb-1 uppercase tracking-wide">
          {txt}
        </p>
      );
      return;
    }

    // # Top header
    if (trimmed.startsWith('# ')) {
      const txt = trimmed.replace(/^#\s*/, '');
      elements.push(
        <p key={i} className="text-[var(--text-primary)] font-black text-[11px] mt-3 mb-1">
          {txt}
        </p>
      );
      return;
    }

    // **bold** standalone line
    if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      elements.push(
        <p key={i} className="text-[var(--text-primary)] font-bold text-[10px]">
          {trimmed.replace(/\*\*/g, '')}
        </p>
      );
      return;
    }

    // Bullet / list
    if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.match(/^\d+\.\s/)) {
      elements.push(
        <p key={i} className="text-[var(--text-secondary)] text-[10px] pl-3 leading-relaxed">
          {trimmed}
        </p>
      );
      return;
    }

    // Warning/note lines
    if (trimmed.startsWith('[!]') || trimmed.startsWith('⚠') || trimmed.startsWith('> ')) {
      elements.push(
        <p key={i} className="text-yellow-400/80 text-[9px] italic pl-2 border-l border-yellow-400/30">
          {trimmed.replace(/^>\s*/, '')}
        </p>
      );
      return;
    }

    // Trading data lines: "Entry  : 1234" / "SL     : 1200" / "RR     : 1:2"
    const colonIdx = trimmed.indexOf(':');
    const isDataLine = colonIdx > 0 && colonIdx < 18 && !trimmed.startsWith('http') && !trimmed.startsWith('//');
    if (isDataLine) {
      const key = trimmed.slice(0, colonIdx).trimEnd();
      const value = trimmed.slice(colonIdx + 1).trim();
      // Highlight special values
      const isBuy = value.includes('BUY') || value.includes('🚀') || value.includes('BULLISH');
      const isSell = value.includes('SELL') || value.includes('🔴') || value.includes('BEARISH');
      const isWait = value.includes('WAIT') || value.includes('⏳');
      const valClass = isBuy ? 'text-emerald-400 font-bold'
        : isSell ? 'text-red-400 font-bold'
          : isWait ? 'text-yellow-400 font-bold'
            : 'text-[var(--text-primary)]';
      elements.push(
        <p key={i} className="text-[10px] leading-relaxed font-mono">
          <span className="text-[var(--text-dim)] inline-block min-w-[80px]">{key}</span>
          <span className="text-[var(--text-dim)]">: </span>
          <span className={valClass}>{value}</span>
        </p>
      );
      return;
    }

    // Default paragraph
    // Inline **bold** support
    const parts = trimmed.split(/(\*\*[^*]+\*\*)/g);
    elements.push(
      <p key={i} className="text-[var(--text-secondary)] text-[10px] leading-relaxed">
        {parts.map((part, j) =>
          part.startsWith('**') && part.endsWith('**')
            ? <strong key={j} className="text-[var(--text-primary)]">{part.slice(2, -2)}</strong>
            : part
        )}
      </p>
    );
  });

  return <div className="space-y-0">{elements}</div>;
}

// ─── Main component ───────────────────────────────────────────────────────────
export default function AIBloombergTerminal({ isFullHeight = false }) {
  const [history, setHistory] = useState([
    { type: 'system', content: 'GAS BLOOMBERG TERMINAL V3.0 — READY' },
    { type: 'hint', content: 'Pilih pair + mode analisa di bawah, atau ketik perintah manual' },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [activeModel, setActiveModel] = useState('GEMINI-2.0-FLASH');
  const [selectedMode, setSelectedMode] = useState('TECH');  // TECH | FUND | HYBRID
  const [cmdHistory, setCmdHistory] = useState([]);
  const [cmdIdx, setCmdIdx] = useState(-1);
  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [history]);

  const submitCommand = useCallback(async (cmd) => {
    const text = cmd.trim().toUpperCase();
    if (!text || loading) return;

    if (text.startsWith('MODE ')) {
      const m = text.split(' ')[1];
      if (m) setActiveModel(m);
    }

    setHistory(prev => [...prev, { type: 'user', content: text }]);
    setCmdHistory(prev => [text, ...prev.slice(0, 49)]);
    setCmdIdx(-1);
    setInput('');
    setLoading(true);
    setHistory(prev => [...prev, { type: 'typing' }]);

    try {
      const data = await sendAIChat({ prompt: text, type: 'general', model_id: activeModel });
      const reply = data?.result?.summary || 'Tidak ada respon dari AI Engine.';
      setHistory(prev => [
        ...prev.filter(m => m.type !== 'typing'),
        { type: 'ai', content: reply, model: data?.result?.model },
      ]);
    } catch (err) {
      console.error('AI chat error:', err);
      setHistory(prev => [
        ...prev.filter(m => m.type !== 'typing'),
        { type: 'error', content: `KONEKSI GAGAL: ${err?.response?.data?.detail || err.message || 'AI Engine tidak dapat dijangkau.'}` },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [loading]);

  const handleSubmit = (e) => { e.preventDefault(); submitCommand(input); };
  const handleKeyDown = (e) => {
    if (e.key === 'ArrowUp') { e.preventDefault(); const i = Math.min(cmdIdx + 1, cmdHistory.length - 1); setCmdIdx(i); setInput(cmdHistory[i] || ''); }
    if (e.key === 'ArrowDown') { e.preventDefault(); const i = Math.max(cmdIdx - 1, -1); setCmdIdx(i); setInput(i === -1 ? '' : cmdHistory[i] || ''); }
  };

  const modelLabel = activeModel === 'FLASH' ? 'Gemini 2.0 Flash' : activeModel === 'PRO' ? 'Gemini 1.5 Pro' : activeModel;
  const mode = MODES[selectedMode];
  const ModeIcon = mode.icon;

  return (
    <div className={`flex flex-col bg-[var(--bg-panel)] font-mono ${isFullHeight ? 'h-full' : 'h-full border-t lg:border-t-0 lg:border-l border-[var(--border-color)]'} overflow-hidden`}>

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between px-3 py-2 bg-[var(--bg-card)] border-b border-[var(--border-color)] shrink-0">
        <div className="flex items-center gap-2">
          <Terminal size={11} className="text-[var(--accent)]" />
          <span className="text-[9px] font-black uppercase tracking-widest text-[var(--accent)]">GAS Terminal</span>
          <div className="relative group ml-1">
            <select
              value={activeModel}
              onChange={(e) => setActiveModel(e.target.value)}
              className="bg-[var(--bg-panel)] text-[8px] font-black text-[var(--accent)] border border-[var(--border-color)] px-1.5 py-0.5 rounded outline-none cursor-pointer hover:border-[var(--accent)]/50 transition-all appearance-none pr-4"
            >
              {ALL_MODELS.map(m => <option key={m.id} value={m.id}>{m.label}</option>)}
            </select>
            <div className="absolute right-1 top-1/2 -translate-y-1/2 pointer-events-none opacity-50">
              <ChevronRight size={7} className="rotate-90 text-[var(--accent)]" />
            </div>
          </div>
        </div>
        <div className="flex items-center gap-2">
          {loading && <RefreshCw size={9} className="text-[var(--accent)] animate-spin" />}
          <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)]" />
          <button onClick={() => setHistory([{ type: 'system', content: 'CLEARED' }])} className="text-[8px] text-[var(--text-dim)] hover:text-[var(--text-secondary)] font-bold uppercase">CLR</button>
        </div>
      </div>

      {/* ── Message History ──────────────────────────────────────────────── */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2 scrollbar-none min-h-0">
        {history.map((msg, i) => {
          if (msg.type === 'user') return (
            <div key={i} className="flex justify-end">
              <div className="max-w-[80%] bg-[var(--accent)] text-black px-2.5 py-1.5 rounded-lg rounded-tr-sm">
                <div className="flex items-center gap-1 mb-0.5">
                  <ChevronRight size={7} /><span className="text-[7px] font-black uppercase opacity-60">INPUT</span>
                </div>
                <p className="text-[10px] font-black">{msg.content}</p>
              </div>
            </div>
          );
          if (msg.type === 'typing') return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-5 h-5 rounded bg-[var(--accent-soft)] flex items-center justify-center shrink-0">
                <Cpu size={9} className="text-[var(--accent)]" />
              </div>
              <div className="bg-[var(--bg-hover)] border border-[var(--border-color)] px-3 py-2 rounded-lg rounded-tl-sm">
                <div className="flex gap-1 items-center h-3">
                  {[0, 150, 300].map(d => <span key={d} className="w-1 h-1 rounded-full bg-[var(--accent)] animate-bounce" style={{ animationDelay: `${d}ms` }} />)}
                </div>
              </div>
            </div>
          );
          if (msg.type === 'system') return (
            <div key={i} className="flex items-center gap-2 py-0.5">
              <div className="h-px flex-1 bg-[var(--border-color)]" />
              <span className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-widest px-2">{msg.content}</span>
              <div className="h-px flex-1 bg-[var(--border-color)]" />
            </div>
          );
          if (msg.type === 'hint') return (
            <div key={i} className="text-center py-1">
              <span className="text-[8px] text-[var(--text-dim)] italic">{msg.content}</span>
            </div>
          );
          if (msg.type === 'error') return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-5 h-5 rounded bg-red-500/10 flex items-center justify-center shrink-0">
                <Zap size={9} className="text-red-400" />
              </div>
              <div className="bg-red-500/5 border border-red-500/20 px-3 py-2 rounded-lg rounded-tl-sm max-w-[90%]">
                <p className="text-[9px] text-red-400 font-bold">{msg.content}</p>
              </div>
            </div>
          );
          // type === 'ai'
          return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-5 h-5 rounded bg-[var(--accent-soft)] flex items-center justify-center shrink-0 mt-0.5">
                <Cpu size={9} className="text-[var(--accent)]" />
              </div>
              <div className="bg-[var(--bg-hover)] border border-[var(--border-color)] px-3 py-2 rounded-lg rounded-tl-sm max-w-[90%] min-w-0">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className="text-[7px] font-black text-[var(--accent)] uppercase tracking-widest">GAS AI</span>
                  {msg.model && <span className="text-[6px] text-[var(--text-dim)] bg-[var(--bg-card)] px-1 py-0.5 rounded font-bold">{msg.model}</span>}
                </div>
                <RenderAI text={msg.content} />
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Input Bar ───────────────────────────────────────────────────── */}
      <form onSubmit={handleSubmit} className="px-3 py-2 bg-[var(--bg-card)] border-t border-[var(--border-color)] flex items-center gap-2 shrink-0">
        <ChevronRight size={11} className="text-[var(--accent)] shrink-0" />
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="ketik perintah manual… (ANLS XAUUSD, FUND, NEWS, HELP)"
          disabled={loading}
          className="flex-1 bg-transparent outline-none text-[10px] font-mono text-[var(--text-primary)] placeholder:text-[var(--text-dim)] uppercase disabled:opacity-50"
        />
        <button type="submit" disabled={loading || !input.trim()}
          className="text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors disabled:opacity-30">
          <Send size={13} />
        </button>
      </form>

      {/* ── Command Panel (below input) ─────────────────────────────────── */}
      <div className="border-t border-[var(--border-color)] bg-[var(--bg-card)] shrink-0">

        {/* Mode selector row */}
        <div className="flex items-center gap-1 px-3 pt-2 pb-1">
          <span className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-widest mr-1">Mode:</span>
          {Object.entries(MODES).map(([key, m]) => {
            const Icon = m.icon;
            const active = selectedMode === key;
            return (
              <button key={key} onClick={() => setSelectedMode(key)}
                className={`flex items-center gap-1 px-2 py-1 rounded border text-[8px] font-black uppercase transition-all ${active ? `${m.color} ${m.border} bg-[var(--accent-soft)]` : 'text-[var(--text-dim)] border-[var(--border-color)] hover:border-[var(--text-dim)]'}`}>
                <Icon size={8} />{key}
              </button>
            );
          })}
          {/* Market + Model quick buttons */}
          <div className="ml-auto flex gap-1">
            {MARKET_CMDS.map(c => {
              const Icon = c.icon;
              return (
                <button key={c.cmd} onClick={() => submitCommand(c.cmd)} disabled={loading}
                  className={`flex items-center gap-1 px-2 py-1 rounded border text-[8px] font-black uppercase transition-all disabled:opacity-30 ${c.color} ${c.border} ${c.bg}`}>
                  <Icon size={8} />{c.label}
                </button>
              );
            })}
          </div>
        </div>

        {/* Pair grid */}
        <div className="flex flex-wrap gap-1 px-3 pb-2">
          {PAIRS.map(pair => (
            <button
              key={pair}
              onClick={() => submitCommand(mode.cmd(pair))}
              disabled={loading}
              className={`flex flex-col items-center px-2.5 py-1.5 rounded border transition-all disabled:opacity-30 min-w-[52px] ${mode.border} ${mode.bg}`}
            >
              <span className={`text-[9px] font-black leading-none ${mode.color}`}>{pair}</span>
              <span className="text-[7px] text-[var(--text-dim)] mt-0.5 leading-none">{mode.label}</span>
            </button>
          ))}

          {/* Hybrid info badge */}
          {selectedMode === 'HYBRID' && (
            <div className="flex items-center gap-1 px-2 py-1 rounded border border-purple-400/20 bg-purple-400/5 ml-1">
              <BarChart2 size={8} className="text-purple-400" />
              <span className="text-[7px] text-purple-300">Tech + Macro dalam satu analisa</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
