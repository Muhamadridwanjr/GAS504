import React, { useState, useEffect } from 'react';
import { Clock, Zap, RefreshCw, Globe, TrendingUp, Moon, Sun, AlertTriangle } from 'lucide-react';
import { callAIFeature } from '../services/api';
import StyleSelector from './StyleSelector';

const SESSIONS = [
  {
    id: 'sydney', name: 'Sydney', emoji: '🇦🇺',
    openUTC: 22, closeUTC: 7,
    openWIB: 5, closeWIB: 14,
    pairs: ['AUDUSD', 'NZDUSD', 'AUDJPY'],
    characteristics: 'Volume rendah, range kecil. Cocok untuk scalping Aussie pairs.',
    color: '#60a5fa',
  },
  {
    id: 'tokyo', name: 'Tokyo / Asia', emoji: '🇯🇵',
    openUTC: 0, closeUTC: 9,
    openWIB: 7, closeWIB: 16,
    pairs: ['USDJPY', 'EURJPY', 'AUDJPY', 'XAUUSD'],
    characteristics: 'Volume sedang. JPY pairs aktif. Range gold terbatas.',
    color: '#f97316',
  },
  {
    id: 'london', name: 'London', emoji: '🇬🇧',
    openUTC: 8, closeUTC: 17,
    openWIB: 15, closeWIB: 24,
    pairs: ['EURUSD', 'GBPUSD', 'EURGBP', 'XAUUSD'],
    characteristics: 'Volume tinggi. Tren kuat sering dimulai di sesi ini. Ideal untuk Forex majors.',
    color: '#8b5cf6',
  },
  {
    id: 'newyork', name: 'New York', emoji: '🇺🇸',
    openUTC: 13, closeUTC: 22,
    openWIB: 20, closeWIB: 5,
    pairs: ['EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'US500', 'NAS100'],
    characteristics: 'Volume tertinggi. Overlap London + NY paling volatil. Rilis data ekonomi AS.',
    color: '#10b981',
  },
  {
    id: 'overlap', name: 'London–NY Overlap', emoji: '⚡',
    openUTC: 13, closeUTC: 17,
    openWIB: 20, closeWIB: 24,
    pairs: ['EURUSD', 'GBPUSD', 'XAUUSD', 'US500'],
    characteristics: '⭐ TERBAIK! Volume dan likuiditas maksimal. Range terlebar, sinyal paling kuat.',
    color: '#fac815',
    highlight: true,
  },
];

function getUTCHour() {
  return new Date().getUTCHours() + new Date().getUTCMinutes() / 60;
}

function isSessionActive(session) {
  const h = getUTCHour();
  if (session.openUTC < session.closeUTC) {
    return h >= session.openUTC && h < session.closeUTC;
  } else {
    // Crosses midnight
    return h >= session.openUTC || h < session.closeUTC;
  }
}

export default function SessionView() {
  const [currentUTCH] = useState(getUTCHour());
  const [loading, setLoading] = useState(false);
  const [aiTip, setAiTip] = useState('');
  const [pairs] = useState(['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']);
  const [pair, setPair] = useState('XAUUSD');
  const [style, setStyle] = useState('intraday');

  const activeSession = SESSIONS.find(s => isSessionActive(s));
  const now = new Date();
  const wibHour = (now.getUTCHours() + 7) % 24;
  const wibMin = now.getUTCMinutes();
  const timeStr = `${String(wibHour).padStart(2,'0')}:${String(wibMin).padStart(2,'0')} WIB`;

  const fetchBestSession = async () => {
    setLoading(true);
    try {
      const res = await callAIFeature('session', { pair, style, params: { current_utc_hour: Math.floor(currentUTCH) } });
      const tip = res?.recommendation || res?.result?.summary || res?.result || '';
      setAiTip(tip);
    } catch (err) {
      setAiTip('Gagal memuat saran: ' + (err?.response?.data?.detail || err?.message || 'Coba lagi.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Clock size={20} className="text-[var(--accent)]" />
        <div>
          <h2 className="text-xl font-display font-black uppercase">Session Optimizer</h2>
          <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">AI rekomendasi sesi terbaik · 1 cr / call</p>
        </div>
        <span className="text-[8px] bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/30 font-black px-2 py-0.5 rounded uppercase ml-auto">Free</span>
      </div>

      {/* Live Clock */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-5 flex items-center justify-between">
        <div>
          <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Waktu Sekarang</p>
          <p className="text-4xl font-black font-mono text-[var(--accent)] mt-1">{timeStr}</p>
          <p className="text-[10px] text-[var(--text-dim)] mt-1">{now.toUTCString().slice(0, 22)} UTC</p>
        </div>
        <div className="text-right">
          <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Sesi Aktif</p>
          {activeSession ? (
            <div className="mt-1">
              <p className="text-sm font-black" style={{ color: activeSession.color }}>{activeSession.emoji} {activeSession.name}</p>
              {activeSession.highlight && <span className="text-[8px] font-black bg-yellow-400 text-black px-2 py-0.5 rounded mt-1 inline-block">TERBAIK</span>}
            </div>
          ) : (
            <p className="text-sm font-black text-[var(--text-dim)]">Tidak ada sesi</p>
          )}
        </div>
      </div>

      {/* Sessions Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {SESSIONS.map(s => {
          const active = isSessionActive(s);
          return (
            <div key={s.id} className={`rounded-xl border p-5 transition-all ${active ? 'shadow-lg' : ''}`}
              style={{ borderColor: active ? s.color + '60' : 'var(--border-color)', background: active ? s.color + '08' : 'var(--bg-card)' }}>
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{s.emoji}</span>
                  <p className="text-sm font-black" style={{ color: active ? s.color : 'var(--text-primary)' }}>{s.name}</p>
                </div>
                {active && (
                  <div className="flex items-center gap-1.5 px-2 py-0.5 rounded-full" style={{ background: s.color + '20', border: `1px solid ${s.color}40` }}>
                    <div className="w-1.5 h-1.5 rounded-full animate-pulse" style={{ background: s.color }} />
                    <span className="text-[8px] font-black" style={{ color: s.color }}>LIVE</span>
                  </div>
                )}
              </div>

              <div className="space-y-2 mb-3">
                <div className="flex justify-between text-[10px]">
                  <span className="text-[var(--text-dim)] font-bold">WIB Open</span>
                  <span className="font-black text-[var(--text-primary)]">{String(s.openWIB).padStart(2,'0')}:00</span>
                </div>
                <div className="flex justify-between text-[10px]">
                  <span className="text-[var(--text-dim)] font-bold">WIB Close</span>
                  <span className="font-black text-[var(--text-primary)]">{String(s.closeWIB % 24).padStart(2,'0')}:00</span>
                </div>
              </div>

              <p className="text-[9px] text-[var(--text-dim)] leading-relaxed mb-3">{s.characteristics}</p>

              <div className="flex flex-wrap gap-1">
                {s.pairs.map(p => (
                  <span key={p} className="text-[8px] font-black px-1.5 py-0.5 rounded" style={{ background: s.color + '15', color: s.color }}>{p}</span>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Pair Selector + AI Tip */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
        <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)] space-y-2">
          <div className="flex items-center gap-3 flex-wrap">
            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">AI Session Tip untuk:</p>
            <div className="flex gap-2 flex-wrap">
              {pairs.map(p => (
                <button key={p} onClick={() => setPair(p)}
                  className={`px-2.5 py-1 rounded-lg text-[9px] font-black border transition-all ${pair === p ? 'bg-[var(--accent)] text-black border-[var(--accent)]' : 'border-[var(--border-color)] text-[var(--text-dim)]'}`}>
                  {p}
                </button>
              ))}
            </div>
            <button onClick={fetchBestSession} disabled={loading} className="ml-auto flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[var(--accent)] text-black text-[9px] font-black hover:opacity-90 disabled:opacity-50">
              {loading ? <RefreshCw size={10} className="animate-spin" /> : <Zap size={10} />}
              Get Tip · 1cr
            </button>
          </div>
          <StyleSelector value={style} onChange={setStyle} showMatrix={false} compact={true} />
        </div>
        <div className="p-5">
          {aiTip ? (
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{aiTip}</p>
          ) : (
            <div className="text-center py-4 text-[var(--text-dim)]">
              <Globe size={20} className="mx-auto mb-2 opacity-30" />
              <p className="text-[10px] font-bold">Klik "Get Tip" untuk rekomendasi sesi terbaik dari AI</p>
            </div>
          )}
        </div>
      </div>

      {/* Best time note */}
      <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-yellow-400/10 border border-yellow-400/30">
        <AlertTriangle size={14} className="text-yellow-400 shrink-0 mt-0.5" />
        <p className="text-[10px] text-yellow-300 leading-relaxed">
          <strong>Pro Tip:</strong> Waktu terbaik untuk XAUUSD adalah London–NY Overlap (20:00–00:00 WIB). 
          Range hariannya bisa 15–30x lebih besar dari sesi Asia. Hindari trading di luar jam ini kecuali ada news.
        </p>
      </div>
    </div>
  );
}
