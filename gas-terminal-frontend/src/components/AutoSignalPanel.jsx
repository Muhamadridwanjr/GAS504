import React, { useState, useEffect, useCallback, useRef } from 'react';
import { RefreshCw, Zap, Activity, Clock, Star } from 'lucide-react';
import { callAIFeature } from '../services/api';
import { useAuth } from '../context/AuthContext';

const MARKET_PAIRS = {
  forex:  ['XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'XAGUSD'],
  crypto: ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT'],
  stock:  ['BBCA', 'BBRI', 'BMRI', 'TLKM', 'GOTO'],
  meme:   ['PEPE', 'WIF', 'BONK', 'DOGE', 'SHIB'],
  poly:   ['BTC-2025', 'ETH-2025', 'FED-RATE', 'US-GDP', 'GOLD-EOY'],
};
const MARKET_STYLES = {
  forex: ['scalping','intraday'], crypto: ['scalping','intraday'],
  stock: ['intraday','swing'],    meme:  ['scalping'],  poly: ['intraday'],
};
const MARKET_EMOJI = { forex:'📊', crypto:'₿', stock:'🇮🇩', meme:'🪙', poly:'🔮' };

// ── Plan → signal label & header style ────────────────────────────────────────
const PLAN_LABEL = {
  essential: { header: '⚡ AUTO SIGNAL',         badge: '⚡', grade_style: '★★★☆☆' },
  plus:      { header: '⚡ SMART SIGNAL',        badge: '📊', grade_style: '★★★★☆' },
  premium:   { header: '🚀 PRO SIGNAL',          badge: '🔥', grade_style: '★★★★☆' },
  ultimate:  { header: '🏦 INSTITUTIONAL SIGNAL',badge: '🏦', grade_style: '★★★★★' },
  ultra:     { header: '🧠 HEDGE FUND SIGNAL',   badge: '💀', grade_style: '★★★★★' },
};

function starRating(prob) {
  if (prob >= 85) return '★★★★★';
  if (prob >= 75) return '★★★★☆';
  if (prob >= 65) return '★★★☆☆';
  if (prob >= 55) return '★★☆☆☆';
  return '★☆☆☆☆';
}

function fmt(v, d = 2) {
  if (v == null) return '—';
  return typeof v === 'number' ? v.toFixed(d) : v;
}

function SignalCard({ s, planDepth = 'essential', market = 'forex' }) {
  const isBuy    = s.signal === 'BUY'  || s.signal === 'YES';
  const isSell   = s.signal === 'SELL' || s.signal === 'NO';
  const isPoly   = market === 'poly';
  const isMeme   = market === 'meme';
  const isCrypto = market === 'crypto';
  const isStock  = market === 'stock';

  const sigColor    = isBuy ? 'text-green-400' : isSell ? 'text-red-400' : 'text-yellow-400';
  const borderColor = isBuy ? 'border-green-500/40' : isSell ? 'border-red-500/40' : 'border-yellow-500/30';
  const bgColor     = isBuy ? 'bg-green-500/5'      : isSell ? 'bg-red-500/5'      : 'bg-yellow-500/5';
  const sigEmoji    = isBuy ? '🟢' : isSell ? '🔴' : '🟡';
  const mktEmoji    = MARKET_EMOJI[market] || '📊';

  const prob    = s.probability || s.probability_yes || 0;
  const isValid = prob >= 60 && s.signal !== 'NEUTRAL';

  const styleLabel = s.style ? s.style.toUpperCase() : '';
  const trendLabel = isBuy ? 'UP' : isSell ? 'DOWN' : 'SIDEWAYS';
  const stars      = starRating(prob);

  // TP display by plan depth
  const tpLine = (() => {
    const tps = [s.tp1, s.tp2, s.tp3].filter(Boolean);
    if (planDepth === 'essential') return tps[0] ? fmt(tps[0]) : '—';
    if (planDepth === 'plus')      return tps.slice(0,2).map(fmt).filter(v => v !== '—').join(' / ') || '—';
    return tps.map(fmt).filter(v => v !== '—').join(' / ') || '—';
  })();

  const scoreVal   = s.score || s.edge_score || s.smart_score || null;
  const scoreLabel = planDepth === 'ultra' ? 'SMART SCORE' : planDepth === 'ultimate' ? 'EDGE' : 'SCORE';

  const headerTitle = planDepth === 'essential' ? '⚡ AUTO SIGNAL'
    : planDepth === 'plus'    ? '⚡ SMART SIGNAL'
    : planDepth === 'premium' ? '🚀 PRO SIGNAL'
    : planDepth === 'ultimate'? '🏦 INSTITUTIONAL SIGNAL'
    : '🧠 HEDGE FUND SIGNAL';

  const statusText = !isValid ? null
    : planDepth === 'essential' ? '⚡ VALID'
    : planDepth === 'plus'      ? '⚡ SETUP ACTIVE'
    : planDepth === 'premium'   ? '🔥 HIGH PROBABILITY'
    : planDepth === 'ultimate'  ? '🔥 STRONG SETUP'
    : '🔥 ELITE SETUP';

  const sigLabel = (() => {
    const base = `${sigEmoji} ${s.signal}`;
    if (planDepth === 'essential' || planDepth === 'plus') return base;
    const ot = s.order_type || '';
    if (ot && !ot.includes('NOW') && !ot.includes('WAIT') && ot !== s.signal) {
      const short = ot.replace('BUY ','').replace('SELL ','');
      return `${base} (${short})`;
    }
    return base;
  })();

  // ── Polymarket card ──────────────────────────────────────────────────────
  if (isPoly) {
    const pYes = s.probability_yes || prob;
    const pNo  = s.probability_no  || (100 - pYes);
    return (
      <div className={`rounded-2xl border ${borderColor} ${bgColor} p-4 font-mono`}>
        <div className="text-[9px] text-[var(--text-dim)] uppercase tracking-widest mb-1">{headerTitle}</div>
        <div className="text-[8px] text-[var(--border-subtle)] mb-2">─────────────</div>
        <div className="text-[11px] font-black text-[var(--text-primary)] mb-3">{mktEmoji} {s.pair}</div>
        <div className="text-[10px] mb-3">
          <span className="text-green-400 font-black">🟢 YES: {pYes}%</span>
          <span className="text-[var(--text-dim)] mx-2">|</span>
          <span className="text-red-400 font-black">🔴 NO: {pNo}%</span>
        </div>
        <div className="border-t border-[var(--border-subtle)] pt-2 space-y-0.5">
          <div className="text-[10px] text-amber-400">⭐ {stars} ({prob}%)</div>
          <div className={`text-[10px] font-black ${sigColor}`}>🎯 {prob}%</div>
          {isValid && <div className="text-[10px] font-black text-green-400">⚡ VALID</div>}
        </div>
      </div>
    );
  }

  // ── Meme card ───────────────────────────────────────────────────────────
  if (isMeme) {
    return (
      <div className={`rounded-2xl border ${borderColor} ${bgColor} p-4 font-mono`}>
        <div className="text-[9px] text-[var(--text-dim)] uppercase tracking-widest mb-1">{headerTitle}</div>
        <div className="text-[8px] text-[var(--border-subtle)] mb-2">─────────────</div>
        <div className="text-[11px] font-black text-[var(--text-primary)] mb-2">{mktEmoji} {s.pair}</div>
        <div className="space-y-0.5 text-[10px] mb-2">
          <div className={`font-black ${sigColor}`}>{sigEmoji} {s.signal}</div>
          {s.entry && <div className="text-[var(--text-secondary)]">💰 {fmt(s.entry)}</div>}
          {s.rug_risk_pct != null && <div className="text-red-400">⚠️ RUG: {s.rug_risk_pct}%</div>}
          {s.scam_risk_score != null && <div className="text-yellow-400">🔐 TRUST: {100 - s.scam_risk_score}</div>}
        </div>
        <div className="text-[9px] font-black text-red-400 mb-2">⚠️ HIGH RISK — DYOR</div>
        <div className="border-t border-[var(--border-subtle)] pt-2 space-y-0.5">
          <div className="text-[10px] text-amber-400">⭐ {stars}</div>
          <div className={`text-[10px] font-black ${sigColor}`}>🎯 {prob}%</div>
        </div>
      </div>
    );
  }

  // ── Standard card (forex / crypto / stock) ───────────────────────────────
  return (
    <div className={`rounded-2xl border ${borderColor} ${bgColor} p-4 font-mono`}>
      {/* Header */}
      <div className="text-[9px] text-[var(--text-dim)] uppercase tracking-widest mb-1">{headerTitle}</div>
      <div className="text-[8px] text-[var(--border-subtle)] mb-2">─────────────</div>

      {/* Pair + style */}
      <div className="text-[11px] font-black text-[var(--text-primary)] mb-2">
        {mktEmoji} {s.pair}{styleLabel ? ` | ${styleLabel}` : ''}
      </div>

      {/* Signal direction */}
      <div className={`text-[11px] font-black ${sigColor} mb-2`}>{sigLabel}</div>

      {/* Entry / SL / TP */}
      <div className="space-y-0.5 text-[10px] mb-2">
        {s.entry && <div className="text-[var(--text-secondary)]">💰 {fmt(s.entry)}</div>}
        {s.sl    && <div className="text-red-400">🛑 {fmt(s.sl)}</div>}
        {tpLine !== '—' && <div className="text-green-400">🎯 {tpLine}</div>}
      </div>

      {/* Trend */}
      <div className="text-[10px] text-[var(--text-secondary)] mb-0.5">
        📈 TREND: <span className={`font-black ${sigColor}`}>{trendLabel}</span>
      </div>

      {/* Momentum (plus+) */}
      {planDepth !== 'essential' && s.momentum && (
        <div className="text-[10px] text-[var(--text-secondary)] mb-0.5">
          📊 MOMENTUM: <span className="font-black text-[var(--text-primary)] uppercase">{s.momentum}</span>
        </div>
      )}

      {/* SMC structure (premium+) */}
      {['premium','ultimate','ultra'].includes(planDepth) && s.smc_structure && (
        <div className="text-[10px] text-[var(--text-secondary)] mb-0.5">
          📈 STRUCTURE: <span className="font-black text-[var(--text-primary)]">{s.smc_structure}</span>
        </div>
      )}

      {/* DXY / macro (ultimate+) */}
      {['ultimate','ultra'].includes(planDepth) && (s.dxy_confirmation || s.correlation_signal) && (
        <div className="text-[10px] text-amber-400 mb-0.5">
          🌍 DXY: <span className="font-black">{s.correlation_signal || s.dxy_confirmation}</span>
        </div>
      )}

      {/* Crypto: volume spike */}
      {isCrypto && s.volume_spike && (
        <div className="text-[10px] text-blue-400 mb-0.5">📊 VOLUME: SPIKE</div>
      )}
      {/* Crypto: BTC dominance (ultimate+) */}
      {isCrypto && ['ultimate','ultra'].includes(planDepth) && s.btc_dominance_impact && (
        <div className="text-[10px] text-purple-400 mb-0.5">
          🌍 BTC DOM: <span className="font-black uppercase">{s.btc_dominance_impact}</span>
        </div>
      )}

      {/* Stock: IHSG (ultimate+) */}
      {isStock && ['ultimate','ultra'].includes(planDepth) && s.ihsg_correlation && (
        <div className="text-[10px] text-amber-400 mb-0.5">
          🌍 IHSG: <span className="font-black uppercase">{s.ihsg_correlation}</span>
        </div>
      )}

      {/* Stars + probability + score */}
      <div className="border-t border-[var(--border-subtle)] pt-2 mt-2 space-y-0.5">
        <div className="text-[10px] text-amber-400">⭐ {stars} ({prob}%)</div>
        <div className={`text-[10px] font-black ${sigColor}`}>🎯 {prob}%</div>
        {scoreVal != null && (
          <div className="text-[10px] text-[var(--accent)]">📊 {scoreLabel}: {scoreVal}</div>
        )}
      </div>

      {/* Status badge */}
      {statusText && (
        <div className={`mt-2 text-[10px] font-black ${sigColor}`}>{statusText}</div>
      )}
    </div>
  );
}

export default function AutoSignalPanel({ market = 'forex', planDepth = 'essential' }) {
  const { user, isAdmin } = useAuth();
  const pairs = MARKET_PAIRS[market] || MARKET_PAIRS.forex;
  const styles = MARKET_STYLES[market] || ['intraday'];

  // Derive model_tier from planDepth
  const tierMap = { essential:'basic', plus:'advanced', premium:'pro', ultimate:'ultra', ultra:'agent' };
  const modelTier = tierMap[planDepth] || 'basic';

  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);
  const [intervalMin, setIntervalMin] = useState(5);
  const [error, setError] = useState('');
  const timerRef = useRef(null);

  const runScan = useCallback(async () => {
    setLoading(true);
    setError('');
    const results = [];
    for (const pair of pairs.slice(0, 3)) {
      try {
        const res = await callAIFeature('signal', {
          pair, style: styles[0], model_tier: modelTier, market,
        });
        results.push({
          pair,
          signal: res.signal || 'NEUTRAL',
          probability: res.probability || res.probability_yes || 0,
          probability_yes: res.probability_yes,
          probability_no: res.probability_no,
          entry: res.entry, sl: res.sl,
          tp1: res.tp1, tp2: res.tp2, tp3: res.tp3,
          grade: res.grade || 'C',
          style: res.style || '',
          momentum: res.momentum || '',
          trigger: res.trigger || '',
          dxy_confirmation: res.dxy_confirmation || '',
          correlation_signal: res.correlation_signal || '',
          rug_risk_pct: res.rug_risk_pct,
          scam_risk_score: res.scam_risk_score,
          plan_depth: res.plan_depth || planDepth,
        });
      } catch (e) {
        results.push({ pair, signal: 'NEUTRAL', probability: 0, error: true });
      }
    }
    setSignals(results);
    setLastUpdate(new Date());
    setLoading(false);
  }, [market, pairs, styles, modelTier]);

  useEffect(() => {
    if (autoRefresh) {
      timerRef.current = setInterval(runScan, intervalMin * 60 * 1000);
    }
    return () => clearInterval(timerRef.current);
  }, [autoRefresh, intervalMin, runScan]);

  const now = lastUpdate
    ? lastUpdate.toLocaleTimeString('id-ID', { timeZone: 'Asia/Jakarta', hour: '2-digit', minute: '2-digit' })
    : '--:--';

  return (
    <div className="space-y-3">
      {/* Controls */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="flex items-center gap-1.5 flex-1">
          <Activity size={12} className="text-[var(--accent)]" />
          <span className="text-[10px] font-black text-[var(--text-primary)] uppercase">Auto Signal · {market.toUpperCase()}</span>
          <span className="text-[8px] text-[var(--text-dim)] bg-[var(--bg-panel)] border border-[var(--border-color)] px-1.5 py-0.5 rounded">{planDepth.toUpperCase()}</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-[8px] text-[var(--text-dim)]">Auto</span>
          <button
            onClick={() => setAutoRefresh(p => !p)}
            className={`w-8 h-4 rounded-full transition-colors relative ${autoRefresh ? 'bg-[var(--accent)]' : 'bg-[var(--border-color)]'}`}
          >
            <span className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition-transform ${autoRefresh ? 'translate-x-4' : 'translate-x-0.5'}`} />
          </button>
          {autoRefresh && (
            <select value={intervalMin} onChange={e => setIntervalMin(+e.target.value)}
              className="text-[8px] bg-[var(--bg-panel)] border border-[var(--border-color)] rounded px-1 text-[var(--text-dim)]">
              <option value={1}>1m</option><option value={5}>5m</option>
              <option value={15}>15m</option><option value={30}>30m</option>
            </select>
          )}
        </div>
        <button onClick={runScan} disabled={loading}
          className="flex items-center gap-1 px-2.5 py-1.5 rounded-lg bg-[var(--accent)] text-black text-[9px] font-black disabled:opacity-50">
          {loading ? <RefreshCw size={11} className="animate-spin" /> : <Zap size={11} className="fill-black" />}
          {loading ? 'Scanning...' : 'Scan Now'}
        </button>
      </div>

      {lastUpdate && (
        <div className="flex items-center gap-1 text-[8px] text-[var(--text-dim)]">
          <Clock size={9} />
          <span>Update: {now} WIB</span>
          {autoRefresh && <span className="text-[var(--accent)]">· Auto {intervalMin}m</span>}
        </div>
      )}

      {error && <div className="text-[9px] text-red-400 p-2 bg-red-500/10 rounded-lg border border-red-500/30">{error}</div>}

      {signals.length === 0 && !loading && (
        <div className="text-center py-10 text-[var(--text-dim)]">
          <Activity size={28} className="mx-auto mb-2 opacity-20" />
          <p className="text-[9px]">Klik "Scan Now" untuk generate auto signal</p>
          <p className="text-[8px] opacity-50 mt-1">Top 3 pairs · {planDepth.toUpperCase()} mode</p>
        </div>
      )}

      {loading && (
        <div className="space-y-3">
          {[0,1,2].map(i => (
            <div key={i} className="h-32 rounded-2xl bg-[var(--bg-panel)] border border-[var(--border-color)] animate-pulse" />
          ))}
        </div>
      )}

      {!loading && signals.map((s, i) => (
        <SignalCard key={i} s={s} planDepth={s.plan_depth || planDepth} market={market} />
      ))}
    </div>
  );
}
