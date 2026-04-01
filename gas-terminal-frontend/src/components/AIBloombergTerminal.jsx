import React, { useState, useRef, useEffect, useCallback } from 'react';
import { MessageCircle, Send, Cpu, ChevronRight, Zap, RefreshCw, CreditCard, Bot, Sparkles, User } from 'lucide-react';
import { sendAIChat } from '../services/api';
import { useAuth } from '../context/AuthContext';

// ─── Plan → Model mapping ────────────────────────────────────────────────────
const PLAN_MODELS = {
  essential: { id: 'gpt-5-mini', label: 'GPT-5 Mini', multiplier: '1.0×', creditCost: 3 },
  plus: { id: 'gemini-3-flash', label: 'Gemini 3 Flash', multiplier: '1.0×', creditCost: 3 },
  premium: { id: 'claude-haiku-4.5', label: 'Claude Haiku 4.5', multiplier: '1.0×', creditCost: 5 },
  ultimate: { id: 'claude-sonnet-4.6', label: 'Claude Sonnet 4.6', multiplier: '1.0×', creditCost: 5 },
};

// ─── Quick prompts ────────────────────────────────────────────────────────────
const QUICK_PROMPTS = [
  'Analisa XAUUSD H4 hari ini',
  'Cara hitung lot size dengan benar',
  'Jelaskan Smart Money Concept (SMC)',
  'Setup trading EURUSD London session',
  'Cara overcome FOMO saat trading',
  'Apa itu Supply & Demand zone?',
];

// ─── Markdown / structured AI output renderer ────────────────────────────────
function RenderAI({ text }) {
  const lines = String(text).split('\n');
  const elements = [];
  let inCode = false;
  let codeLines = [];

  lines.forEach((raw, i) => {
    const line = raw;
    const trimmed = line.trim();

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

    if (!trimmed) { elements.push(<div key={i} className="h-1.5" />); return; }

    if (trimmed === '---' || trimmed.match(/^─{3,}$/)) {
      elements.push(<div key={i} className="my-2 border-t border-[var(--border-color)] opacity-40" />);
      return;
    }

    if (trimmed.startsWith('## ') || trimmed.startsWith('##')) {
      const txt = trimmed.replace(/^#+\s*/, '');
      elements.push(
        <p key={i} className="text-[var(--accent)] font-black text-[10px] mt-3 mb-1 uppercase tracking-wide">
          {txt}
        </p>
      );
      return;
    }

    if (trimmed.startsWith('# ')) {
      const txt = trimmed.replace(/^#\s*/, '');
      elements.push(
        <p key={i} className="text-[var(--text-primary)] font-black text-[11px] mt-3 mb-1">
          {txt}
        </p>
      );
      return;
    }

    if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      elements.push(
        <p key={i} className="text-[var(--text-primary)] font-bold text-[10px]">
          {trimmed.replace(/\*\*/g, '')}
        </p>
      );
      return;
    }

    if (trimmed.startsWith('- ') || trimmed.startsWith('• ') || trimmed.match(/^\d+\.\s/)) {
      elements.push(
        <p key={i} className="text-[var(--text-secondary)] text-[10px] pl-3 leading-relaxed">
          {trimmed}
        </p>
      );
      return;
    }

    if (trimmed.startsWith('[!]') || trimmed.startsWith('⚠') || trimmed.startsWith('> ')) {
      elements.push(
        <p key={i} className="text-yellow-400/80 text-[9px] italic pl-2 border-l border-yellow-400/30">
          {trimmed.replace(/^>\s*/, '')}
        </p>
      );
      return;
    }

    const colonIdx = trimmed.indexOf(':');
    const isDataLine = colonIdx > 0 && colonIdx < 18 && !trimmed.startsWith('http') && !trimmed.startsWith('//');
    if (isDataLine) {
      const key = trimmed.slice(0, colonIdx).trimEnd();
      const value = trimmed.slice(colonIdx + 1).trim();
      const isBuy = value.includes('BUY') || value.includes('BULLISH');
      const isSell = value.includes('SELL') || value.includes('BEARISH');
      const isWait = value.includes('WAIT');
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
export default function AIBloombergTerminal({ isFullHeight = false, hideHeader = false }) {
  const { user } = useAuth();
  const plan = (user?.plan || 'essential').toLowerCase();
  const planModel = PLAN_MODELS[plan] || PLAN_MODELS.essential;

  const [credits, setCredits] = useState(87);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState([
    {
      type: 'welcome',
      content: 'Halo! Saya AI Mentor Golden AI Strategy. Tanya apa saja tentang trading — analisa pasar, strategi, risk management, atau psychology. Setiap pesan menggunakan kredit sesuai plan Anda.',
    },
  ]);

  const scrollRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  const sendMessage = useCallback(async (prompt) => {
    const text = prompt.trim();
    if (!text || loading) return;

    if (credits <= 0) return;

    setMessages(prev => [...prev, { type: 'user', content: text }]);
    setInput('');
    setLoading(true);
    setMessages(prev => [...prev, { type: 'typing' }]);

    try {
      const data = await sendAIChat({ prompt: text, type: 'mentor', model_id: planModel.id });
      const reply = data?.result?.summary || data?.result || 'Tidak ada respon dari AI Mentor.';
      setCredits(prev => Math.max(0, prev - planModel.creditCost));
      setMessages(prev => [
        ...prev.filter(m => m.type !== 'typing'),
        {
          type: 'ai',
          content: typeof reply === 'string' ? reply : JSON.stringify(reply),
          model: planModel.label,
          creditsUsed: planModel.creditCost,
        },
      ]);
    } catch (err) {
      console.error('AI mentor error:', err);
      setMessages(prev => [
        ...prev.filter(m => m.type !== 'typing'),
        {
          type: 'error',
          content: `Koneksi gagal: ${err?.response?.data?.detail || err.message || 'AI Mentor tidak dapat dijangkau.'}`,
        },
      ]);
    } finally {
      setLoading(false);
      inputRef.current?.focus();
    }
  }, [loading, credits, planModel]);

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(input);
  };

  const handleClear = () => {
    setMessages([
      {
        type: 'system',
        content: 'Chat dibersihkan',
      },
    ]);
  };

  const outOfCredits = credits <= 0;

  return (
    <div className={`flex flex-col bg-[var(--bg-panel)] ${isFullHeight ? 'h-full' : 'h-full border-t lg:border-t-0 lg:border-l border-[var(--border-color)]'} overflow-hidden`}>

      {/* ── Header ─────────────────────────────────────────────────────────── */}
      {!hideHeader && (
      <div className="flex items-center justify-between px-3 py-2 bg-[var(--bg-card)] border-b border-[var(--border-color)] shrink-0">
        <div className="flex items-center gap-2 min-w-0">
          <div className="w-5 h-5 rounded bg-yellow-400/10 flex items-center justify-center shrink-0">
            <Bot size={10} className="text-[var(--accent)]" />
          </div>
          <div className="flex flex-col min-w-0">
            <span className="text-[9px] font-black uppercase tracking-widest text-[var(--accent)] leading-none">AI Mentor</span>
            <span className="text-[7px] text-[var(--text-dim)] font-bold truncate leading-none mt-0.5">{planModel.label}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Credit balance */}
          <div className={`flex items-center gap-1 px-2 py-1 rounded border text-[8px] font-black ${credits <= 10 ? 'border-red-500/40 bg-red-500/10 text-red-400' : 'border-yellow-400/30 bg-yellow-400/10 text-[var(--accent)]'}`}>
            <Zap size={8} />
            <span>{credits} cr</span>
          </div>
          {loading && <RefreshCw size={9} className="text-[var(--accent)] animate-spin" />}
          <button
            onClick={handleClear}
            className="text-[8px] text-[var(--text-dim)] hover:text-[var(--text-secondary)] font-bold uppercase tracking-widest transition-colors"
          >
            CLR
          </button>
        </div>
      </div>
      )}

      {/* ── Messages area ──────────────────────────────────────────────────── */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-3 py-3 space-y-3 scrollbar-none min-h-0">

        {messages.map((msg, i) => {

          if (msg.type === 'welcome') return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-6 h-6 rounded-full bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center shrink-0 mt-0.5">
                <Sparkles size={10} className="text-[var(--accent)]" />
              </div>
              <div className="bg-[var(--bg-hover)] border border-yellow-400/20 px-3 py-2.5 rounded-xl rounded-tl-sm max-w-[90%]">
                <div className="flex items-center gap-1.5 mb-1.5">
                  <span className="text-[7px] font-black text-[var(--accent)] uppercase tracking-widest">AI Mentor · Golden AI Strategy</span>
                </div>
                <p className="text-[10px] text-[var(--text-secondary)] leading-relaxed">{msg.content}</p>
              </div>
            </div>
          );

          if (msg.type === 'system') return (
            <div key={i} className="flex items-center gap-2 py-1">
              <div className="h-px flex-1 bg-[var(--border-color)]" />
              <span className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-widest px-2">{msg.content}</span>
              <div className="h-px flex-1 bg-[var(--border-color)]" />
            </div>
          );

          if (msg.type === 'user') return (
            <div key={i} className="flex justify-end gap-2 items-end">
              <div className="max-w-[80%] bg-[var(--accent)] text-black px-3 py-2 rounded-xl rounded-br-sm">
                <p className="text-[10px] font-bold leading-relaxed">{msg.content}</p>
              </div>
              <div className="w-5 h-5 rounded-full bg-[var(--bg-hover)] border border-[var(--border-color)] flex items-center justify-center shrink-0">
                <User size={9} className="text-[var(--text-dim)]" />
              </div>
            </div>
          );

          if (msg.type === 'typing') return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-6 h-6 rounded-full bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center shrink-0">
                <Cpu size={9} className="text-[var(--accent)]" />
              </div>
              <div className="bg-[var(--bg-hover)] border border-[var(--border-color)] px-3 py-2.5 rounded-xl rounded-tl-sm">
                <div className="flex gap-1 items-center h-3">
                  {[0, 150, 300].map(d => (
                    <span key={d} className="w-1.5 h-1.5 rounded-full bg-[var(--accent)] animate-bounce" style={{ animationDelay: `${d}ms` }} />
                  ))}
                </div>
              </div>
            </div>
          );

          if (msg.type === 'error') return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-6 h-6 rounded-full bg-red-500/10 border border-red-500/20 flex items-center justify-center shrink-0">
                <Zap size={9} className="text-red-400" />
              </div>
              <div className="bg-red-500/5 border border-red-500/20 px-3 py-2 rounded-xl rounded-tl-sm max-w-[90%]">
                <p className="text-[9px] text-red-400 font-bold leading-relaxed">{msg.content}</p>
              </div>
            </div>
          );

          // type === 'ai'
          return (
            <div key={i} className="flex gap-2 items-start">
              <div className="w-6 h-6 rounded-full bg-yellow-400/10 border border-yellow-400/20 flex items-center justify-center shrink-0 mt-0.5">
                <Cpu size={9} className="text-[var(--accent)]" />
              </div>
              <div className="bg-[var(--bg-hover)] border border-[var(--border-color)] px-3 py-2.5 rounded-xl rounded-tl-sm max-w-[90%] min-w-0">
                <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                  <span className="text-[7px] font-black text-[var(--accent)] uppercase tracking-widest">AI Mentor</span>
                  {msg.model && (
                    <span className="text-[6px] text-[var(--text-dim)] bg-[var(--bg-card)] px-1.5 py-0.5 rounded font-bold border border-[var(--border-color)]">
                      {msg.model}
                    </span>
                  )}
                  {msg.creditsUsed && (
                    <span className="text-[6px] text-yellow-400/60 font-bold">
                      -{msg.creditsUsed} cr
                    </span>
                  )}
                </div>
                <RenderAI text={msg.content} />
              </div>
            </div>
          );
        })}
      </div>

      {/* ── Quick prompt chips ─────────────────────────────────────────────── */}
      <div className="px-3 py-2 border-t border-[var(--border-color)] bg-[var(--bg-card)] shrink-0">
        <p className="text-[7px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1.5">Tanya cepat:</p>
        <div className="flex flex-wrap gap-1">
          {QUICK_PROMPTS.map((prompt, i) => (
            <button
              key={i}
              onClick={() => sendMessage(prompt)}
              disabled={loading || outOfCredits}
              className="text-[8px] font-bold text-[var(--text-secondary)] bg-[var(--bg-panel)] border border-[var(--border-color)] px-2 py-1 rounded-full hover:border-[var(--accent)]/50 hover:text-[var(--accent)] transition-all disabled:opacity-40 disabled:cursor-not-allowed leading-none"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>

      {/* ── Input bar ──────────────────────────────────────────────────────── */}
      <div className="px-3 py-2 bg-[var(--bg-card)] border-t border-[var(--border-color)] shrink-0">
        {outOfCredits ? (
          <div className="flex items-center justify-between gap-3 py-1">
            <p className="text-[9px] text-red-400 font-bold">Kredit habis. Top up untuk melanjutkan.</p>
            <button className="flex items-center gap-1.5 px-3 py-1.5 bg-[var(--accent)] text-black text-[9px] font-black rounded-lg hover:opacity-90 transition-opacity shrink-0">
              <CreditCard size={10} />
              Top Up Credits
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="flex items-center gap-2">
            <div className="flex-1 flex items-center gap-2 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2 focus-within:border-[var(--accent)]/50 transition-colors">
              <MessageCircle size={11} className="text-[var(--text-dim)] shrink-0" />
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder="Tanya tentang trading…"
                disabled={loading}
                className="flex-1 bg-transparent outline-none text-[10px] text-[var(--text-primary)] placeholder:text-[var(--text-dim)] disabled:opacity-50"
              />
            </div>
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="flex items-center gap-1.5 px-3 py-2 bg-[var(--accent)] text-black text-[8px] font-black rounded-lg hover:opacity-90 transition-opacity disabled:opacity-40 disabled:cursor-not-allowed shrink-0"
            >
              <Send size={10} />
              <span className="hidden sm:inline">Kirim ({planModel.creditCost} cr)</span>
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
