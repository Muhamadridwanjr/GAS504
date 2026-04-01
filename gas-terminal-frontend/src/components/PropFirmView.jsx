import React, { useState } from 'react';
import { Shield, CheckCircle, AlertTriangle, RefreshCw, Zap, Target, TrendingDown } from 'lucide-react';
import { callAIFeature } from '../services/api';

const FIRMS = [
  { id: 'ftmo', name: 'FTMO', phase1Profit: 10, phase2Profit: 5, dailyDD: 5, maxDD: 10, minDays: 10 },
  { id: 'myforex', name: 'MyFunded Trader', phase1Profit: 8, phase2Profit: 5, dailyDD: 5, maxDD: 12, minDays: 5 },
  { id: 'tntp', name: 'The Funded Trader', phase1Profit: 8, phase2Profit: 5, dailyDD: 5, maxDD: 10, minDays: 8 },
  { id: 'e8', name: 'E8 Markets', phase1Profit: 8, phase2Profit: 5, dailyDD: 5, maxDD: 8, minDays: 0 },
  { id: 'fidelcrest', name: 'Fidelcrest', phase1Profit: 10, phase2Profit: 5, dailyDD: 5, maxDD: 10, minDays: 3 },
];

export default function PropFirmView() {
  const [selectedFirm, setSelectedFirm] = useState(FIRMS[0]);
  const [balance, setBalance] = useState('100000');
  const [currentEquity, setCurrentEquity] = useState('');
  const [todayProfit, setTodayProfit] = useState('');
  const [totalProfit, setTotalProfit] = useState('');
  const [tradingDays, setTradingDays] = useState('1');
  const [loading, setLoading] = useState(false);
  const [aiAdvice, setAiAdvice] = useState('');

  const bal = parseFloat(balance) || 0;
  const eq = parseFloat(currentEquity) || bal;
  const todayPnl = parseFloat(todayProfit) || 0;
  const netPnl = parseFloat(totalProfit) || 0;
  const days = parseInt(tradingDays) || 1;

  const dailyDDUsed = bal > 0 ? Math.abs(Math.min(0, todayPnl / bal * 100)) : 0;
  const maxDDUsed = bal > 0 ? Math.abs(Math.min(0, (eq - bal) / bal * 100)) : 0;
  const profitProgress = bal > 0 ? Math.max(0, netPnl / bal * 100) : 0;

  const rules = [
    { label: 'Profit Target', current: profitProgress, target: selectedFirm.phase1Profit, unit: '%', pass: profitProgress >= selectedFirm.phase1Profit, invert: false },
    { label: 'Daily DD Limit', current: dailyDDUsed, target: selectedFirm.dailyDD, unit: '%', pass: dailyDDUsed < selectedFirm.dailyDD, invert: true },
    { label: 'Max DD Limit', current: maxDDUsed, target: selectedFirm.maxDD, unit: '%', pass: maxDDUsed < selectedFirm.maxDD, invert: true },
    { label: 'Min Trading Days', current: days, target: selectedFirm.minDays, unit: ' hari', pass: days >= selectedFirm.minDays || selectedFirm.minDays === 0, invert: false },
  ];

  const allPass = rules.every(r => r.pass);

  const fetchAdvice = async () => {
    setLoading(true);
    try {
      const res = await callAIFeature('propfirm', {
        firm: selectedFirm.id,
        balance: bal, equity: eq,
        today_pnl: todayPnl, total_pnl: netPnl,
        days_traded: days
      });
      setAiAdvice(res?.result?.summary || res?.result || '');
    } catch {
      setAiAdvice('Gagal memuat saran AI. Coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Shield size={20} className="text-[var(--accent)]" />
        <div>
          <h2 className="text-xl font-display font-black uppercase">Prop Firm Assistant</h2>
          <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Jaga DD sesuai rules FTMO/MFF · 8 cr / call</p>
        </div>
        <span className="text-[8px] bg-green-500/20 text-green-400 border border-green-500/30 font-black px-2 py-0.5 rounded uppercase ml-auto">Plus+</span>
      </div>

      {/* Firm Selector */}
      <div className="flex gap-2 flex-wrap">
        {FIRMS.map(f => (
          <button key={f.id} onClick={() => setSelectedFirm(f)}
            className={`px-3 py-2 rounded-xl text-[10px] font-black border transition-all ${selectedFirm.id === f.id ? 'bg-[var(--accent)] text-black border-[var(--accent)]' : 'border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
            {f.name}
          </button>
        ))}
      </div>

      {/* Firm Rules Info */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {[
          { label: 'Profit Target', value: `${selectedFirm.phase1Profit}%` },
          { label: 'Phase 2 Target', value: `${selectedFirm.phase2Profit}%` },
          { label: 'Daily DD Max', value: `${selectedFirm.dailyDD}%` },
          { label: 'Max Total DD', value: `${selectedFirm.maxDD}%` },
          { label: 'Min Days', value: selectedFirm.minDays === 0 ? 'Bebas' : `${selectedFirm.minDays} hari` },
        ].map((r, i) => (
          <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-3 text-center">
            <p className="text-[8px] font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">{r.label}</p>
            <p className="text-sm font-black text-[var(--text-primary)]">{r.value}</p>
          </div>
        ))}
      </div>

      {/* Input Form */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        {[
          { label: 'Account Balance (USD)', key: 'balance', value: balance, set: setBalance, type: 'number' },
          { label: 'Current Equity', key: 'eq', value: currentEquity, set: setCurrentEquity, placeholder: balance, type: 'number' },
          { label: "Today's PnL (USD)", key: 'today', value: todayProfit, set: setTodayProfit, placeholder: '0', type: 'number' },
          { label: 'Total Net PnL (USD)', key: 'net', value: totalProfit, set: setTotalProfit, placeholder: '0', type: 'number' },
          { label: 'Trading Days', key: 'days', value: tradingDays, set: setTradingDays, type: 'number' },
        ].map(f => (
          <div key={f.key}>
            <label className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)] block mb-1.5">{f.label}</label>
            <input type={f.type} value={f.value} onChange={e => f.set(e.target.value)} placeholder={f.placeholder}
              className="w-full bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl px-3 py-2.5 text-sm font-bold outline-none focus:border-[var(--accent)] transition-colors" />
          </div>
        ))}
      </div>

      {/* Status Overview */}
      <div className={`p-4 rounded-2xl border-2 ${allPass ? 'border-green-500/40 bg-green-500/5' : 'border-yellow-400/40 bg-yellow-400/5'}`}>
        <div className="flex items-center gap-3 mb-4">
          {allPass ? <CheckCircle size={20} className="text-green-400" /> : <AlertTriangle size={20} className="text-yellow-400" />}
          <p className={`text-sm font-black ${allPass ? 'text-green-400' : 'text-yellow-400'}`}>
            {allPass ? '✅ Semua Rules Terpenuhi — Aman Lanjut!' : '⚠️ Cek Rules Berikut Sebelum Trading'}
          </p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {rules.map((r, i) => (
            <div key={i} className={`p-3 rounded-xl border ${r.pass ? 'border-green-500/20 bg-green-500/5' : 'border-red-500/20 bg-red-500/5'}`}>
              <div className="flex justify-between items-center mb-2">
                <span className="text-[10px] font-black text-[var(--text-dim)]">{r.label}</span>
                <span className={`text-[9px] font-black ${r.pass ? 'text-green-400' : 'text-red-400'}`}>
                  {r.pass ? '✓ OK' : '✗ FAIL'} · {r.current.toFixed(1)}{r.unit} / {r.target}{r.unit}
                </span>
              </div>
              <div className="h-2 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                <div className="h-full rounded-full transition-all"
                  style={{
                    width: `${Math.min(100, (r.current / r.target) * 100)}%`,
                    background: r.invert ? (r.pass ? 'var(--success)' : 'var(--danger)') : (r.pass ? 'var(--success)' : 'var(--accent)')
                  }} />
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Compliance Advice */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
        <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center justify-between">
          <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">AI Compliance Advisor</p>
          <button onClick={fetchAdvice} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[var(--accent)] text-black text-[9px] font-black hover:opacity-90 disabled:opacity-50">
            {loading ? <RefreshCw size={10} className="animate-spin" /> : <Zap size={10} />}
            Get Advice · 8cr
          </button>
        </div>
        <div className="p-5">
          {aiAdvice ? (
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap">{aiAdvice}</p>
          ) : (
            <div className="text-center py-6 text-[var(--text-dim)]">
              <Shield size={24} className="mx-auto mb-2 opacity-30" />
              <p className="text-xs font-bold">Isi data trading kamu lalu klik "Get Advice"</p>
              <p className="text-[10px] mt-1">AI akan analisa compliance kamu terhadap rules {selectedFirm.name}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
