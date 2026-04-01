import React, { useState, useEffect } from 'react';
import { Activity, RefreshCw, Zap, TrendingUp, TrendingDown } from 'lucide-react';
import { callAIFeature } from '../services/api';

const PAIRS = ['XAUUSD', 'DXY', 'US10Y', 'EURUSD', 'BTC/USDT', 'ETH/USDT', 'US500', 'WTI'];


function corrColor(v) {
  if (v === 1) return '#6b7280';
  if (v > 0.7) return '#ef4444';
  if (v > 0.4) return '#f97316';
  if (v > 0.15) return '#fac815';
  if (v >= -0.15) return '#6b7280';
  if (v > -0.4) return '#fac815';
  if (v > -0.7) return '#f97316';
  return '#3b82f6';
}

function corrLabel(v) {
  if (v === 1) return '–';
  if (v > 0.7) return 'Kuat +';
  if (v > 0.4) return 'Sedang +';
  if (v > 0.15) return 'Lemah +';
  if (v >= -0.15) return 'Netral';
  if (v > -0.4) return 'Lemah -';
  if (v > -0.7) return 'Sedang -';
  return 'Kuat -';
}

export default function CorrelationView() {
  const [focusPair, setFocusPair] = useState('XAUUSD');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const fetchCorrelation = async (pair) => {
    setLoading(true);
    setError('');
    try {
      const res = await callAIFeature('correlation', { pair, timeframe: 'H1' });
      setResult(res);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Gagal memuat data korelasi. Pastikan EA MT5 aktif.');
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCorrelation(focusPair); }, [focusPair]);

  // Normalize response — could be { correlation_matrix: {}, correlations: {}, pairs: {} }
  const matrix = result?.correlation_matrix || result?.matrix || result?.correlations || {};
  const correlations = matrix[focusPair] || {};
  const allPairsInResult = Object.keys(matrix).length > 0 ? Object.keys(matrix) : PAIRS;
  const sorted = Object.entries(correlations)
    .filter(([k]) => k !== focusPair)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]));
  const aiAnalysis = result?.ai_summary || result?.summary || result?.analysis || result?.result?.summary || result?.result || '';

  return (
    <div className="p-4 md:p-6 space-y-6 pb-24 md:pb-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center gap-3">
        <Activity size={20} className="text-[var(--accent)]" />
        <div>
          <h2 className="text-xl font-display font-black uppercase">Correlation Tracker</h2>
          <p className="text-[10px] text-[var(--text-dim)] uppercase tracking-widest font-bold">Monitor korelasi antar aset real-time · 3 cr / call</p>
        </div>
        <span className="text-[8px] bg-blue-500/20 text-blue-400 border border-blue-500/30 font-black px-2 py-0.5 rounded uppercase ml-auto">Essential+</span>
      </div>

      {/* Pair selector */}
      <div className="flex gap-2 flex-wrap items-center">
        {PAIRS.map(p => (
          <button key={p} onClick={() => setFocusPair(p)}
            className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all border ${focusPair === p ? 'bg-[var(--accent)] text-black border-[var(--accent)]' : 'border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
            {p}
          </button>
        ))}
        {loading && <span className="text-[9px] text-[var(--text-dim)] animate-pulse font-mono ml-2">Memuat AI korelasi...</span>}
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl p-3 border" style={{ background: 'rgba(239,68,68,0.05)', borderColor: 'rgba(239,68,68,0.2)' }}>
          <p className="text-xs font-black text-red-400">⚠️ {error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Correlation Bar Chart */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">
              Korelasi {focusPair} vs Aset Lain
            </p>
          </div>
          <div className="p-5 space-y-4">
            {sorted.map(([pair, val]) => (
              <div key={pair}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-xs font-black text-[var(--text-primary)]">{pair}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] font-bold" style={{ color: corrColor(val) }}>{corrLabel(val)}</span>
                    <span className="text-xs font-black font-mono" style={{ color: corrColor(val) }}>{val > 0 ? '+' : ''}{val.toFixed(2)}</span>
                  </div>
                </div>
                <div className="h-2.5 bg-[var(--bg-panel)] rounded-full overflow-hidden relative">
                  {val >= 0 ? (
                    <div className="absolute left-1/2 top-0 h-full rounded-full"
                      style={{ width: `${Math.abs(val) * 50}%`, background: corrColor(val) }} />
                  ) : (
                    <div className="absolute right-1/2 top-0 h-full rounded-full"
                      style={{ width: `${Math.abs(val) * 50}%`, background: corrColor(val) }} />
                  )}
                  <div className="absolute left-1/2 top-0 h-full w-px bg-[var(--border-color)]" />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Matrix heatmap (compact) */}
        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
          <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
            <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">Correlation Matrix Heatmap</p>
          </div>
          <div className="p-4 overflow-x-auto">
            {Object.keys(matrix).length > 0 ? (
              <table className="text-[8px] font-bold w-full">
                <thead>
                  <tr>
                    <th className="text-[var(--text-dim)] pb-2 pr-2 text-left w-16"> </th>
                    {allPairsInResult.map(p => <th key={p} className="text-[var(--text-dim)] pb-2 px-1 text-center">{p.slice(0, 3)}</th>)}
                  </tr>
                </thead>
                <tbody>
                  {allPairsInResult.map(row => (
                    <tr key={row}>
                      <td className="text-[var(--text-primary)] font-black pr-2 py-1 whitespace-nowrap">{row.slice(0, 6)}</td>
                      {allPairsInResult.map(col => {
                        const v = matrix[row]?.[col] ?? (row === col ? 1 : 0);
                        return (
                          <td key={col} className="py-1 px-1 text-center rounded" style={{ color: v === 1 ? 'var(--text-dim)' : corrColor(v), background: v === 1 ? 'transparent' : `${corrColor(v)}18` }}>
                            {v === 1 ? '—' : (v > 0 ? '+' : '') + Number(v).toFixed(2)}
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="text-center py-8 text-[var(--text-dim)]">
                <p className="text-xs font-bold">{loading ? 'Memuat matrix korelasi...' : 'Pilih pair untuk melihat matrix korelasi'}</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Analysis */}
      <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
        <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)] flex items-center justify-between">
          <p className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">AI Correlation Analysis</p>
          <button onClick={() => fetchCorrelation(focusPair)} disabled={loading}
            className="flex items-center gap-1.5 px-3 py-1 rounded-lg bg-[var(--accent)] text-black text-[9px] font-black hover:opacity-90 transition-opacity disabled:opacity-50">
            {loading ? <RefreshCw size={10} className="animate-spin" /> : <Zap size={10} />}
            {loading ? 'Loading...' : 'Refresh · 3cr'}
          </button>
        </div>
        <div className="p-5">
          {aiAnalysis ? (
            <p className="text-xs text-[var(--text-secondary)] leading-relaxed">{aiAnalysis}</p>
          ) : loading ? (
            <p className="text-[9px] text-[var(--text-dim)] animate-pulse font-mono text-center py-4">AI menganalisa korelasi {focusPair}...</p>
          ) : (
            <div className="text-center py-6 text-[var(--text-dim)]">
              <Activity size={24} className="mx-auto mb-2 opacity-30" />
              <p className="text-xs font-bold">Pilih pair di atas untuk memuat analisa korelasi real-time</p>
              <p className="text-[10px] mt-1">3 kredit · data dari MT5 EA</p>
            </div>
          )}
        </div>
      </div>

      {/* Legend */}
      <div className="flex flex-wrap gap-4 text-[9px] font-bold">
        {[
          { color: '#ef4444', label: 'Korelasi Sangat Positif (>0.7)' },
          { color: '#f97316', label: 'Korelasi Positif (0.4–0.7)' },
          { color: '#fac815', label: 'Lemah (0.15–0.4)' },
          { color: '#6b7280', label: 'Netral (±0.15)' },
          { color: '#3b82f6', label: 'Korelasi Negatif Kuat (<-0.7)' },
        ].map((l, i) => (
          <div key={i} className="flex items-center gap-1.5">
            <div className="w-2.5 h-2.5 rounded" style={{ background: l.color }} />
            <span className="text-[var(--text-dim)]">{l.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
