import React, { useState, useCallback } from 'react';
import { RefreshCw, Brain, TrendingUp, TrendingDown, Minus, Eye } from 'lucide-react';
import { callAIFeature } from '../services/api';
import { useAuth } from '../context/AuthContext';

const MARKET_CONFIG = {
  forex:  { pair: 'XAUUSD', features: ['technical','correlation','hybrid'], label: 'Forex & Gold', emoji: '📊' },
  crypto: { pair: 'BTC/USDT', features: ['technical','sentiment'], label: 'Crypto', emoji: '₿' },
  stock:  { pair: 'BBCA', features: ['technical','fundamental'], label: 'Stock IDX', emoji: '🇮🇩' },
  meme:   { pair: 'PEPE', features: ['sentiment'], label: 'Memecoin', emoji: '🪙' },
  poly:   { pair: 'BTC-2025', features: ['sentiment','fundamental'], label: 'Polymarket', emoji: '🔮' },
};

// Plan-specific overview header
const PLAN_OVERVIEW_HEADER = {
  essential: '🧠 MARKET OVERVIEW',
  plus:      '🧠 SMART OVERVIEW',
  premium:   '🧠 PRO OVERVIEW',
  ultimate:  '🧠 INSTITUTIONAL OVERVIEW',
  ultra:     '🧠 HEDGE FUND OVERVIEW',
};

function BiasTag({ bias }) {
  if (!bias) return null;
  const b = bias.toLowerCase();
  if (b.includes('bull') || b.includes('up')) return <span className="text-[9px] font-black text-green-400 bg-green-400/10 px-1.5 py-0.5 rounded">📈 BULLISH</span>;
  if (b.includes('bear') || b.includes('down')) return <span className="text-[9px] font-black text-red-400 bg-red-400/10 px-1.5 py-0.5 rounded">📉 BEARISH</span>;
  if (b.includes('side') || b.includes('range') || b.includes('neutral')) return <span className="text-[9px] font-black text-yellow-400 bg-yellow-400/10 px-1.5 py-0.5 rounded">📊 SIDEWAYS</span>;
  return <span className="text-[9px] font-black text-[var(--text-dim)] bg-[var(--bg-panel)] px-1.5 py-0.5 rounded">{bias.toUpperCase()}</span>;
}

function TFRow({ label, value }) {
  if (!value) return null;
  const v = (value || '').toLowerCase();
  const color = v.includes('bull') || v.includes('up') ? 'text-green-400' : v.includes('bear') || v.includes('down') ? 'text-red-400' : 'text-yellow-400';
  return (
    <div className="flex items-center justify-between py-1.5 border-b border-[var(--border-subtle)] last:border-0">
      <span className="text-[9px] text-[var(--text-dim)] font-mono">{label}</span>
      <span className={`text-[9px] font-black ${color} uppercase`}>{value}</span>
    </div>
  );
}

function Section({ title, content, color = 'text-[var(--accent)]', bg = 'bg-[var(--bg-panel)]', border = 'border-[var(--border-color)]' }) {
  if (!content) return null;
  return (
    <div className={`rounded-xl border p-3 ${bg} ${border}`}>
      <div className={`text-[8px] font-black uppercase tracking-wider mb-1.5 ${color}`}>{title}</div>
      <p className="text-[9px] text-[var(--text-secondary)] leading-relaxed">{content}</p>
    </div>
  );
}

export default function MarketAnalysisPanel({ market = 'forex', planDepth = 'essential' }) {
  const cfg = MARKET_CONFIG[market] || MARKET_CONFIG.forex;
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeFeature, setActiveFeature] = useState(cfg.features[0]);
  const [pair, setPair] = useState(cfg.pair);
  const [error, setError] = useState('');

  const tierMap = { essential:'basic', plus:'advanced', premium:'pro', ultimate:'ultra', ultra:'agent' };
  const modelTier = tierMap[planDepth] || 'basic';

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const res = await callAIFeature(activeFeature, { pair, market, model_tier: modelTier });
      setResult(res);
    } catch (e) {
      setError(e?.response?.data?.detail || e.message || 'Analysis failed');
    } finally {
      setLoading(false);
    }
  }, [activeFeature, pair, market, modelTier]);

  const overviewHeader = PLAN_OVERVIEW_HEADER[planDepth] || PLAN_OVERVIEW_HEADER.essential;

  // Extract structured data from result
  const sig = result?.signal || result?.ai_signal || '';
  const htf = result?.htf_analysis || result?.htf_bias || '';
  const mtf = result?.mtf_analysis || result?.mtf_trend || '';
  const ltf = result?.ltf_entry || result?.ltf_analysis || '';
  const obs = result?.observation || '';
  const potential = result?.trading_plan || result?.plan_a || '';
  const macro = result?.dxy_confirmation || result?.btc_dominance_impact || result?.ihsg_correlation || '';
  const structure = result?.smc_structure || result?.structure || '';
  const liquidity = result?.liquidity_status || '';
  const scenario1 = result?.scenario_1 || '';
  const scenario2 = result?.scenario_2 || '';
  const reasoning = result?.reasoning || result?.result?.summary || '';
  const smartScore = result?.smart_score || result?.edge_score || result?.score;

  // Zones from key_levels
  const support    = result?.key_levels?.support;
  const resistance = result?.key_levels?.resistance;

  // MTF detail from result
  const mtfDetail = result?.mtf_detail || {};
  const mtfTFs = Object.keys(mtfDetail);

  return (
    <div className="space-y-3">
      {/* Feature selector */}
      <div className="flex gap-1.5 flex-wrap items-center">
        {cfg.features.map(f => (
          <button key={f} onClick={() => setActiveFeature(f)}
            className={`px-2.5 py-1 rounded-lg text-[9px] font-black transition-all capitalize
              ${activeFeature === f ? 'bg-[var(--accent)] text-black' : 'bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)] hover:border-[var(--accent)]/40'}`}>
            {f}
          </button>
        ))}
        <span className="text-[8px] text-[var(--text-dim)] bg-[var(--bg-panel)] border border-[var(--border-color)] px-1.5 py-1 rounded font-black">{planDepth.toUpperCase()}</span>
        <button onClick={runAnalysis} disabled={loading}
          className="ml-auto flex items-center gap-1 px-2.5 py-1 rounded-lg bg-[var(--accent)] text-black text-[9px] font-black disabled:opacity-50">
          {loading ? <RefreshCw size={10} className="animate-spin" /> : <Brain size={10} />}
          {loading ? 'Analyzing...' : 'Analyze'}
        </button>
      </div>

      {error && <div className="text-[9px] text-red-400 p-2 bg-red-500/10 rounded-lg border border-red-500/30">{error}</div>}

      {!result && !loading && (
        <div className="text-center py-10 text-[var(--text-dim)]">
          <Eye size={28} className="mx-auto mb-2 opacity-20" />
          <p className="text-[9px]">Pilih fitur dan klik Analyze</p>
          <p className="text-[8px] opacity-50 mt-1">{planDepth.toUpperCase()} mode · {cfg.emoji} {cfg.label}</p>
        </div>
      )}

      {loading && (
        <div className="space-y-2">
          {[0,1,2,3].map(i => <div key={i} className="h-16 rounded-xl bg-[var(--bg-panel)] border border-[var(--border-color)] animate-pulse" />)}
        </div>
      )}

      {!loading && result && (
        <div className="space-y-2.5">
          {/* ── Overview Header ── */}
          <div className="rounded-2xl border border-[var(--border-color)] bg-[var(--bg-card)] p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <div className="text-[8px] font-black text-[var(--text-dim)] uppercase tracking-widest">{overviewHeader}</div>
                <div className="text-sm font-black text-[var(--text-primary)] mt-0.5">{cfg.emoji} {pair}</div>
              </div>
              <div className="flex flex-col items-end gap-1">
                {sig && <BiasTag bias={sig} />}
                {smartScore != null && (
                  <span className="text-[8px] font-black text-[var(--accent)]">SCORE: {smartScore}/100</span>
                )}
              </div>
            </div>

            {/* ── Multi-TF rows ── */}
            {(htf || mtf || ltf || mtfTFs.length > 0) && (
              <div className="space-y-0 mb-2">
                {htf && <TFRow label="📈 HTF" value={htf.split('.')[0]} />}
                {mtf && <TFRow label="📊 MTF" value={mtf.split('.')[0]} />}
                {ltf && <TFRow label="📉 LTF" value={ltf.split('.')[0]} />}
                {mtfTFs.slice(0,4).map(tf => (
                  <TFRow key={tf} label={`   ${tf}`} value={mtfDetail[tf]?.trend || mtfDetail[tf]?.recommendation || ''} />
                ))}
              </div>
            )}

            {/* ── Zones ── */}
            {(support || resistance) && (
              <div className="flex gap-3 mt-2 text-[9px]">
                {support    && <div><span className="text-[var(--text-dim)]">Support: </span><span className="font-black text-green-400 font-mono">{typeof support === 'number' ? support.toFixed(2) : support}</span></div>}
                {resistance && <div><span className="text-[var(--text-dim)]">Resistance: </span><span className="font-black text-red-400 font-mono">{typeof resistance === 'number' ? resistance.toFixed(2) : resistance}</span></div>}
              </div>
            )}
          </div>

          {/* ── SMC Structure (premium+) ── */}
          {structure && (
            <div className="rounded-xl border border-[var(--accent)]/20 bg-[var(--bg-panel)] p-3">
              <div className="text-[8px] font-black text-[var(--accent)] uppercase mb-1.5">⚡ STRUCTURE</div>
              <div className="text-[9px] font-black text-[var(--text-primary)]">{structure}</div>
              {liquidity && <div className="text-[8px] text-[var(--text-dim)] mt-1">💧 LIQUIDITY: <span className="font-black text-[var(--text-primary)]">{liquidity.toUpperCase()}</span></div>}
            </div>
          )}

          {/* ── Macro Correlation (ultimate+) ── */}
          {macro && (
            <div className="rounded-xl border border-amber-400/20 bg-amber-400/5 p-3">
              <div className="text-[8px] font-black text-amber-400 uppercase mb-1.5">🌍 CORRELATION</div>
              <p className="text-[9px] text-[var(--text-secondary)] leading-relaxed">{macro}</p>
            </div>
          )}

          {/* ── Context / Reasoning ── */}
          {reasoning && (
            <Section title="🌍 CONTEXT" content={reasoning}
              color="text-[var(--text-dim)]" bg="bg-[var(--bg-panel)]" border="border-[var(--border-color)]" />
          )}

          {/* ── Observation ── */}
          {obs && (
            <Section title="🔍 OBSERVATION" content={obs}
              color="text-blue-400" bg="bg-blue-400/5" border="border-blue-400/20" />
          )}

          {/* ── Potential / Trading Plan ── */}
          {potential && (
            <Section title="📌 POTENSI / TRADING PLAN" content={potential}
              color="text-green-400" bg="bg-green-400/5" border="border-green-400/20" />
          )}

          {/* ── Scenarios A/B (ultra) ── */}
          {scenario1 && (
            <div className="rounded-xl border border-purple-400/20 bg-purple-400/5 p-3 space-y-2">
              <div className="text-[8px] font-black text-purple-400 uppercase">🧠 SCENARIO</div>
              <div>
                <div className="text-[8px] font-black text-[var(--text-dim)]">1️⃣ PRIMARY</div>
                <p className="text-[9px] text-[var(--text-secondary)] leading-relaxed">{scenario1}</p>
              </div>
              {scenario2 && (
                <div>
                  <div className="text-[8px] font-black text-[var(--text-dim)]">2️⃣ ALTERNATIVE</div>
                  <p className="text-[9px] text-[var(--text-secondary)] leading-relaxed">{scenario2}</p>
                </div>
              )}
            </div>
          )}

          {/* ── HTF full text (plus+) ── */}
          {htf && htf.length > 30 && (
            <Section title="📈 HTF ANALYSIS" content={htf}
              color="text-[var(--text-dim)]" bg="bg-[var(--bg-panel)]" border="border-[var(--border-color)]" />
          )}

          {/* ── LTF full text (premium+) ── */}
          {ltf && ltf.length > 30 && (
            <Section title="📉 LTF ENTRY" content={ltf}
              color="text-[var(--text-dim)]" bg="bg-[var(--bg-panel)]" border="border-[var(--border-color)]" />
          )}

          {/* ── MTF Detail table ── */}
          {mtfTFs.length > 0 && (
            <div className="rounded-xl border border-[var(--border-color)] bg-[var(--bg-panel)] overflow-hidden">
              <div className="text-[8px] font-black text-[var(--text-dim)] uppercase px-3 pt-2 pb-1">Multi-TF Detail</div>
              <div className="overflow-x-auto">
                <table className="w-full text-[8px]">
                  <thead>
                    <tr className="border-b border-[var(--border-color)] text-[var(--text-dim)]">
                      {['TF','Trend','RSI','MACD','EMA','Price'].map(h => (
                        <th key={h} className="px-2 py-1 text-left font-black">{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {mtfTFs.map(tf => {
                      const d = mtfDetail[tf] || {};
                      const tr = (d.trend || '').toLowerCase();
                      const trColor = tr.includes('bull') ? 'text-green-400' : tr.includes('bear') ? 'text-red-400' : 'text-yellow-400';
                      return (
                        <tr key={tf} className="border-b border-[var(--border-subtle)] hover:bg-[var(--bg-hover)]">
                          <td className="px-2 py-1 font-black text-[var(--accent)] font-mono">{tf}</td>
                          <td className={`px-2 py-1 font-black uppercase ${trColor}`}>{d.trend || '—'}</td>
                          <td className="px-2 py-1 font-mono text-[var(--text-secondary)]">{d.rsi?.toFixed?.(1) ?? d.rsi ?? '—'}</td>
                          <td className="px-2 py-1 text-[var(--text-secondary)] capitalize">{d.macd_signal || '—'}</td>
                          <td className="px-2 py-1 text-[var(--text-secondary)] capitalize">{d.ema_signal || '—'}</td>
                          <td className="px-2 py-1 font-mono text-[var(--text-primary)]">{d.price?.toFixed?.(2) ?? d.price ?? '—'}</td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* ── Note for meme ── */}
          {market === 'meme' && (
            <div className="text-[8px] font-black text-red-400 text-center py-1">⚠️ HIGH RISK MARKET — Gunakan SL ketat dan position size kecil</div>
          )}
        </div>
      )}
    </div>
  );
}
