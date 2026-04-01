import React, { useState, useRef, useEffect } from 'react';
import { GraduationCap, Send, Bot, User, RefreshCw, Zap, BookOpen, Target } from 'lucide-react';
import { callAIFeature, fetchUserCredits } from '../services/api';
import StyleSelector from './StyleSelector';

const QUICK_TOPICS = [
  'Review trade XAUUSD saya yang rugi — kenapa salah?',
  'Bagaimana cara improve win rate dari 55% ke 70%?',
  'Analisa psikologi trading saya minggu ini',
  'Cara set TP yang lebih optimal dengan SMC',
  'Evaluasi money management saya',
  'Kenapa saya sering cut loss terlalu cepat?',
];

const MENTOR_TIPS = [
  { icon: '🎯', title: 'Trade Review', desc: 'Ceritakan trade terakhirmu, AI Mentor akan review entry, SL, dan TP kamu' },
  { icon: '📊', title: 'Strategy Audit', desc: 'Tanya apakah strategimu cocok untuk kondisi market saat ini' },
  { icon: '🧠', title: 'Psychology Fix', desc: 'Identifikasi bias dan kebiasaan buruk yang merugikan' },
  { icon: '📈', title: 'Improvement Plan', desc: 'Dapatkan rencana personal untuk meningkatkan performa' },
];

export default function MentorModeView() {
  const [messages, setMessages] = useState([{
    type: 'ai',
    content: 'Halo Trader! Saya AI Mentor GAS — siap review trade, strategi, dan mindset kamu layaknya senior trader profesional. Ceritakan apa yang ingin kamu perbaiki hari ini?\n\n*Setiap sesi menggunakan 10 kredit*',
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [credits, setCredits] = useState(null);
  const [style, setStyle] = useState('swing');
  const scrollRef = useRef(null);

  useEffect(() => {
    fetchUserCredits().then(d => setCredits(d?.credits ?? d?.balance ?? null)).catch(() => {});
  }, []);

  useEffect(() => {
    if (scrollRef.current) scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
  }, [messages]);

  const sendMessage = async (text) => {
    const t = text.trim();
    if (!t || loading) return;
    setMessages(prev => [...prev, { type: 'user', content: t }]);
    setInput('');
    setLoading(true);
    setMessages(prev => [...prev, { type: 'typing' }]);
    try {
      const res = await callAIFeature('mentor', { pair: 'XAUUSD', timeframe: 'H1', style, question: t });
      const reply = res?.result?.response || res?.result?.summary || res?.result || res?.recommendation || 'Tidak ada respon. Coba lagi.';
      setMessages(prev => [...prev.filter(m => m.type !== 'typing'), {
        type: 'ai',
        content: typeof reply === 'string' ? reply : JSON.stringify(reply),
      }]);
      // Refresh credit balance after each mentor call (costs 10 cr)
      fetchUserCredits().then(d => setCredits(d?.credits ?? d?.quota ?? null)).catch(() => {});
    } catch (err) {
      const detail = err?.response?.data?.detail || err?.message || 'Unknown error';
      setMessages(prev => [...prev.filter(m => m.type !== 'typing'), {
        type: 'error', content: 'Error: ' + detail
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-120px)] max-h-[900px]">
      {/* Header */}
      <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border-color)] bg-[var(--bg-card)] shrink-0">
        <div className="w-9 h-9 rounded-xl bg-yellow-400/20 flex items-center justify-center">
          <GraduationCap size={18} className="text-[var(--accent)]" />
        </div>
        <div className="flex-1">
          <h2 className="text-sm font-black uppercase tracking-wide">AI Mentor Mode</h2>
          <p className="text-[9px] text-[var(--text-dim)] font-bold">Senior Trader AI · Kimi Moonshot · 10 cr / sesi</p>
        </div>
        <span className="text-[8px] bg-purple-500/20 text-purple-400 border border-purple-500/30 font-black px-2 py-0.5 rounded uppercase">Ultimate</span>
        <div className="flex items-center gap-1 px-2 py-1 rounded-lg bg-yellow-400/10 border border-yellow-400/20">
          <Zap size={10} className="text-yellow-400" />
          <span className="text-[9px] font-black text-yellow-400">{credits !== null ? `${credits} cr` : '...'}</span>
        </div>
      </div>

      {/* Style Selector */}
      <div className="px-4 py-2 border-b border-[var(--border-color)] bg-[var(--bg-panel)] shrink-0">
        <StyleSelector value={style} onChange={setStyle} showMatrix={false} compact={true} />
      </div>

      {/* Tips bar */}
      <div className="px-4 py-2 border-b border-[var(--border-color)] bg-[var(--bg-panel)] shrink-0">
        <div className="flex gap-3 overflow-x-auto scrollbar-none">
          {MENTOR_TIPS.map((t, i) => (
            <button key={i} onClick={() => sendMessage(t.desc)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-[var(--border-color)] bg-[var(--bg-card)] hover:border-[var(--accent)]/40 transition-all shrink-0">
              <span className="text-sm">{t.icon}</span>
              <span className="text-[10px] font-black text-[var(--text-secondary)] whitespace-nowrap">{t.title}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto px-4 py-4 space-y-4 scrollbar-none">
        {messages.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.type === 'user' ? 'flex-row-reverse' : ''}`}>
            {m.type !== 'typing' && (
              <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 ${m.type === 'user' ? 'bg-[var(--accent)]/20' : m.type === 'error' ? 'bg-red-500/20' : 'bg-yellow-400/20'}`}>
                {m.type === 'user' ? <User size={14} className="text-[var(--accent)]" /> : <GraduationCap size={14} className="text-yellow-400" />}
              </div>
            )}
            {m.type === 'typing' ? (
              <div className="flex items-center gap-1.5 px-4 py-3 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl rounded-tl-sm">
                {[0, 1, 2].map(d => <div key={d} className="w-1.5 h-1.5 bg-[var(--text-dim)] rounded-full animate-bounce" style={{ animationDelay: `${d * 0.15}s` }} />)}
              </div>
            ) : (
              <div className={`max-w-[85%] px-4 py-3 rounded-2xl text-xs leading-relaxed font-medium ${m.type === 'user' ? 'bg-[var(--accent)] text-black rounded-tr-sm' : m.type === 'error' ? 'bg-red-500/10 text-red-400 border border-red-500/20 rounded-tl-sm' : 'bg-[var(--bg-card)] border border-[var(--border-color)] text-[var(--text-secondary)] rounded-tl-sm'}`}>
                {m.content}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Quick Topics */}
      <div className="px-4 py-2 border-t border-[var(--border-color)] bg-[var(--bg-panel)] shrink-0">
        <div className="flex gap-2 overflow-x-auto scrollbar-none pb-1">
          {QUICK_TOPICS.map((q, i) => (
            <button key={i} onClick={() => sendMessage(q)}
              className="shrink-0 px-3 py-1.5 rounded-lg text-[9px] font-black border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:border-[var(--accent)]/40 transition-all whitespace-nowrap">
              {q.length > 40 ? q.slice(0, 40) + '…' : q}
            </button>
          ))}
        </div>
      </div>

      {/* Input */}
      <form onSubmit={e => { e.preventDefault(); sendMessage(input); }}
        className="flex items-center gap-3 px-4 py-3 border-t border-[var(--border-color)] bg-[var(--bg-card)] shrink-0">
        <input
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder="Tanya atau ceritakan trade kamu ke AI Mentor..."
          className="flex-1 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl px-4 py-2.5 text-xs font-medium outline-none focus:border-[var(--accent)] placeholder:text-[var(--text-dim)]"
        />
        <button type="submit" disabled={!input.trim() || loading}
          className="w-9 h-9 rounded-xl bg-[var(--accent)] flex items-center justify-center shrink-0 hover:opacity-90 disabled:opacity-40 transition-all">
          {loading ? <RefreshCw size={14} className="text-black animate-spin" /> : <Send size={14} className="text-black" />}
        </button>
      </form>
    </div>
  );
}
