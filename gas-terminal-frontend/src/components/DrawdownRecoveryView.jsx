import React, { useState } from 'react';
import { TrendingDown, Shield, AlertTriangle, Zap, RefreshCw, CheckCircle } from 'lucide-react';
import { callAIFeature } from '../services/api';

const DD_STAGES = [
  { level: '1–3%', color: '#10b981', label: 'AMAN', advice: 'Lanjutkan trading normal. Monitor posisi terbuka.' },
  { level: '3–5%', color: '#fac815', label: 'WASPADA', advice: 'Kurangi ukuran lot 50%. Hindari pair volatile.' },
  { level: '5–8%', color: '#f97316', label: 'BAHAYA', advice: 'Stop buka posisi baru. Tutup posisi yang rugi.' },
  { level: '>8%', color: '#ef4444', label: 'KRITIS', advice: 'Stop trading hari ini. Review strategi besok.' },
];

export default function DrawdownRecoveryView() {
  const [balance, setBalance] = useState('10000');
  const [currentEquity, setCurrentEquity] = useState('');
  const [loading, setLoading] = useState(false);
  const [aiPlan, setAiPlan] = useState('');

  const bal = parseFloat(balance) || 0;
  const eq = parseFloat(currentEquity) || bal;
  const ddAmt = Math.max(0, bal - eq);
  const ddPct = bal > 0 ? (ddAmt / bal) * 100 : 0;

  const getCurrentStage = () => {
    if (ddPct < 3) return DD_STAGES[0];
    if (ddPct < 5) return DD_STAGES[1];
    if (ddPct < 8) return DD_STAGES[2];
    return DD_STAGES[3];
  };
  const stage = getCurrentStage();

  const fetchAIPlan = async () => {
    setLoading(true);
    try {
      const res = await callAIFeature('drawdown', {
        pair: 'XAUUSD',
        params: { balance: bal, equity: eq, drawdown_pct: parseFloat(ddPct.toFixed(2)) }
      });
      const plan = res?.result?.summary || res?.result?.plan || res?.result || res?.recommendation || '';
      setAiPlan(typeof plan === 'string' ? plan : JSON.stringify(plan));
    } catch (err) {
      setAiPlan('Gagal memuat rencana AI: ' + (err?.response?.data?.detail || err?.message || 'Coba lagi.'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <TrendingDown size={20} className="text-[var(--accent)]" />
        <div>
          <h2 className="text-xl font-display font-black uppercase">Drawdown Recovery</h2>
          <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">AI adjust strategy saat drawdown · 5 cr / call</p>
        </div>
        <span className="text-[8px] bg-orange-500/20 text-orange-400 border border-orange-500/30 font-black px-2 py-0.5 rounded uppercase ml-auto">Plus+</span>
      </div>

      {/* Input */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1.5">Balance Awal (USD)</label>
          <input type="number" value={balance} onChange={e => setBalance(e.target.value)}
            className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-3 text-sm font-bold outline-none focus:border-[var(--accent)] transition-colors" />
        </div>
        <div>
          <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1.5">Equity Sekarang (USD)</label>
          <input type="number" value={currentEquity} onChange={e => setCurrentEquity(e.target.value)}
            placeholder={balance}
            className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-4 py-3 text-sm font-bold outline-none focus:border-[var(--danger)] transition-colors" />
        </div>
      </div>

      {/* DD Meter */}
      <div className="bg-[var(--bg-card)] border rounded-2xl p-6 space-y-4" style={{ borderColor: stage.color + '40' }}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">Current Drawdown</p>
            <p className="text-4xl font-black font-mono mt-1" style={{ color: stage.color }}>
              -{ddPct.toFixed(2)}%
            </p>
            <p className="text-xs font-bold mt-1 text-[var(--text-dim)]">-${ddAmt.toFixed(2)} dari modal</p>
          </div>
          <div className="text-center">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center text-2xl" style={{ background: stage.color + '20' }}>
              {ddPct < 3 ? '✅' : ddPct < 5 ? '⚠️' : ddPct < 8 ? '🚨' : '💀'}
            </div>
            <p className="text-[10px] font-black mt-2" style={{ color: stage.color }}>{stage.label}</p>
          </div>
        </div>

        {/* DD Bar */}
        <div>
          <div className="flex justify-between text-[9px] font-bold text-[var(--text-dim)] mb-1.5">
            <span>0%</span><span>3%</span><span>5%</span><span>8%</span><span>10%+</span>
          </div>
          <div className="h-4 bg-[var(--bg-panel)] rounded-full overflow-hidden relative">
            <div className="h-full rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, ddPct * 10)}%`, background: `linear-gradient(90deg, #10b981, #fac815, #f97316, #ef4444)` }} />
          </div>
        </div>

        <div className="flex items-start gap-2 px-4 py-3 rounded-xl" style={{ background: stage.color + '10', border: `1px solid ${stage.color}30` }}>
          <AlertTriangle size={14} style={{ color: stage.color }} className="shrink-0 mt-0.5" />
          <p className="text-xs font-bold" style={{ color: stage.color }}>{stage.advice}</p>
        </div>
      </div>

      {/* Stage Guide */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {DD_STAGES.map((s, i) => (
          <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4 text-center">
            <p className="text-[9px] font-black uppercase tracking-widest mb-1" style={{ color: s.color }}>{s.label}</p>
            <p className="text-lg font-black font-mono" style={{ color: s.color }}>{s.level}</p>
            <p className="text-[8px] text-[var(--text-dim)] mt-2 leading-relaxed">{s.advice.split('.')[0]}</p>
          </div>
        ))}
      </div>

      {/* Recovery Rules */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
        <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
          <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Aturan Recovery Standar</p>
        </div>
        <div className="divide-y divide-[var(--border-color)]">
          {[
            { icon: '🛑', rule: 'Stop trading hari ini jika DD harian ≥ 5%' },
            { icon: '📉', rule: 'Kurangi lot size 50% jika DD total 3–5%' },
            { icon: '⏸️', rule: 'Pause trading 1 hari penuh jika DD >8%' },
            { icon: '📋', rule: 'Review jurnal trading sebelum lanjut' },
            { icon: '🎯', rule: 'Target recovery max 2% per hari, jangan rakus' },
            { icon: '🧠', rule: 'Jangan revenge trading — emosi = musuh terbesar' },
          ].map((r, i) => (
            <div key={i} className="flex items-center gap-3 px-5 py-3 hover:bg-[var(--bg-hover)] transition-colors">
              <span className="text-base shrink-0">{r.icon}</span>
              <p className="text-xs font-bold text-[var(--text-secondary)]">{r.rule}</p>
            </div>
          ))}
        </div>
      </div>

      {/* AI Recovery Plan */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
        <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center justify-between">
          <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">AI Recovery Plan</p>
          <button onClick={fetchAIPlan} disabled={loading || !currentEquity}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[var(--accent)] text-black text-[9px] font-black hover:opacity-90 disabled:opacity-50">
            {loading ? <RefreshCw size={10} className="animate-spin" /> : <Zap size={10} />}
            Get Plan · 5cr
          </button>
        </div>
        <div className="p-5">
          {aiPlan ? (
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">{aiPlan}</p>
          ) : (
            <div className="text-center py-6 text-[var(--text-dim)]">
              <Shield size={24} className="mx-auto mb-2 opacity-30" />
              <p className="text-xs font-bold">Masukkan equity sekarang lalu klik "Get Plan"</p>
              <p className="text-[10px] mt-1">AI akan buat rencana recovery yang disesuaikan dengan DD kamu</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
