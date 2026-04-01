import React, { useEffect, useState, useRef } from 'react';

const LOGO = 'https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg';
const MONO = "'JetBrains Mono','Fira Mono','Courier New',monospace";

const STEPS = [
  { id: 'engine',  label: 'Connecting AI engines',       sub: 'Claude · GPT-4o · Gemini · Grok',     pct: 18  },
  { id: 'market',  label: 'Loading market data',          sub: 'MT5 WebSocket · Binance · DXFeed',     pct: 38  },
  { id: 'init',    label: 'Initializing 21 AI features',  sub: 'Signal · Technical · Sentiment · SMC', pct: 62  },
  { id: 'signal',  label: 'Syncing signal pipeline',      sub: 'Forex · Crypto · Polymarket · Meme',   pct: 82  },
  { id: 'ready',   label: 'System Ready',                 sub: 'All systems operational',              pct: 100 },
];

const TICKERS = [
  { s: 'XAUUSD', p: '3,327.40', c: '+0.84%', up: true },
  { s: 'BTC/USDT', p: '103,420', c: '+2.13%', up: true },
  { s: 'EURUSD', p: '1.0821', c: '-0.12%', up: false },
  { s: 'ETH/USDT', p: '3,874', c: '+1.55%', up: true },
  { s: 'GBPUSD', p: '1.2734', c: '+0.08%', up: true },
  { s: 'DXY', p: '103.71', c: '-0.21%', up: false },
  { s: 'USDJPY', p: '148.92', c: '+0.32%', up: true },
  { s: 'SOL/USDT', p: '178.34', c: '+3.21%', up: true },
];

/* animated ring sizes */
const RINGS = [
  { size: 160, delay: 0,    opacity: 0.12 },
  { size: 240, delay: 0.6,  opacity: 0.07 },
  { size: 340, delay: 1.2,  opacity: 0.04 },
];

export default function LoadingScreen() {
  const [step, setStep]     = useState(0);
  const [theme, setTheme]   = useState('dark');
  const [tick, setTick]     = useState(0);
  const tickRef             = useRef(null);

  /* ── theme sync ─────────────────────────────────── */
  useEffect(() => {
    const saved = localStorage.getItem('gas-theme') || 'dark';
    setTheme(saved);
    document.documentElement.setAttribute('data-theme', saved);
  }, []);

  /* ── step progression ───────────────────────────── */
  useEffect(() => {
    if (step >= STEPS.length - 1) return;
    const delays = [520, 680, 720, 600];
    const t = setTimeout(() => setStep(s => s + 1), delays[step] ?? 500);
    return () => clearTimeout(t);
  }, [step]);

  /* ── ticker scroll offset ────────────────────────── */
  useEffect(() => {
    tickRef.current = setInterval(() => setTick(t => t + 1), 60);
    return () => clearInterval(tickRef.current);
  }, []);

  const dark = theme === 'dark';
  const cur = STEPS[step];

  /* ── theme tokens ───────────────────────────────── */
  const T = {
    bg:        dark ? '#0a0a0a'              : '#f1f5f9',
    bgCard:    dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.04)',
    border:    dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)',
    textPri:   dark ? '#ffffff'              : '#0f172a',
    textDim:   dark ? 'rgba(255,255,255,0.35)' : 'rgba(15,23,42,0.45)',
    textMid:   dark ? 'rgba(255,255,255,0.6)'  : 'rgba(15,23,42,0.65)',
    barTrack:  dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.08)',
    tickBg:    dark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)',
    gridLine:  dark ? 'rgba(255,255,255,0.025)' : 'rgba(0,0,0,0.04)',
  };

  /* ticker items doubled for seamless loop */
  const tickerItems = [...TICKERS, ...TICKERS];
  const offsetPx = (tick * 0.6) % (TICKERS.length * 120);

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: T.bg,
      display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center',
      overflow: 'hidden',
    }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
        @keyframes ringPulse {
          0%,100% { transform: translate(-50%,-50%) scale(1); opacity: var(--ro); }
          50%      { transform: translate(-50%,-50%) scale(1.08); opacity: calc(var(--ro)*0.4); }
        }
        @keyframes shimmer {
          0%   { background-position: -200% center; }
          100% { background-position: 200% center; }
        }
        @keyframes logoBreathe {
          0%,100% { box-shadow: 0 0 24px rgba(250,204,21,0.25), 0 0 0 1px rgba(250,204,21,0.2); }
          50%     { box-shadow: 0 0 48px rgba(250,204,21,0.5),  0 0 0 2px rgba(250,204,21,0.4); }
        }
        @keyframes dotBlink {
          0%,80%,100% { opacity: 0.2; transform: scale(0.8); }
          40%         { opacity: 1;   transform: scale(1); }
        }
        @keyframes fadeSlideUp {
          from { opacity: 0; transform: translateY(6px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .load-step-done  { animation: fadeSlideUp 0.3s ease both; }
        .load-step-active { animation: fadeSlideUp 0.25s ease both; }
      `}</style>

      {/* ── Background grid ────────────────────────────── */}
      <div style={{
        position: 'absolute', inset: 0, zIndex: 0,
        backgroundImage: `linear-gradient(${T.gridLine} 1px,transparent 1px),linear-gradient(90deg,${T.gridLine} 1px,transparent 1px)`,
        backgroundSize: '56px 56px',
        maskImage: 'radial-gradient(ellipse 70% 70% at 50% 50%, black 10%, transparent 100%)',
        WebkitMaskImage: 'radial-gradient(ellipse 70% 70% at 50% 50%, black 10%, transparent 100%)',
      }} />

      {/* ── Ambient glow ───────────────────────────────── */}
      <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%,-50%)', zIndex: 0, pointerEvents: 'none' }}>
        {RINGS.map((r, i) => (
          <div key={i} style={{
            position: 'absolute',
            top: '50%', left: '50%',
            width: r.size, height: r.size,
            borderRadius: '50%',
            border: `1px solid rgba(250,204,21,${r.opacity * 3})`,
            background: `radial-gradient(circle, rgba(250,204,21,${r.opacity}) 0%, transparent 70%)`,
            '--ro': r.opacity,
            animation: `ringPulse 3s ease-in-out ${r.delay}s infinite`,
          }} />
        ))}
      </div>

      {/* ── Corner decorations ─────────────────────────── */}
      {[
        { top: 20, left: 20 },
        { top: 20, right: 20 },
        { bottom: 20, left: 20 },
        { bottom: 20, right: 20 },
      ].map((pos, i) => (
        <div key={i} style={{
          position: 'absolute', ...pos, zIndex: 1,
          width: 28, height: 28,
          borderTop: i < 2 ? `1.5px solid rgba(250,204,21,0.25)` : 'none',
          borderBottom: i >= 2 ? `1.5px solid rgba(250,204,21,0.25)` : 'none',
          borderLeft: (i === 0 || i === 2) ? `1.5px solid rgba(250,204,21,0.25)` : 'none',
          borderRight: (i === 1 || i === 3) ? `1.5px solid rgba(250,204,21,0.25)` : 'none',
        }} />
      ))}

      {/* ── Version tag ───────────────────────────────── */}
      <div style={{ position: 'absolute', top: 20, left: '50%', transform: 'translateX(-50%)', zIndex: 2 }}>
        <span style={{ fontSize: 9, fontWeight: 700, color: T.textDim, fontFamily: MONO, letterSpacing: '0.12em', textTransform: 'uppercase' }}>
          GAS v3.0 · AI Trading Platform
        </span>
      </div>

      {/* ── Main content ───────────────────────────────── */}
      <div style={{ position: 'relative', zIndex: 2, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 32, padding: '0 24px' }}>

        {/* Logo */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 14 }}>
          <div style={{
            width: 76, height: 76, borderRadius: 22, overflow: 'hidden',
            animation: 'logoBreathe 2.4s ease-in-out infinite',
          }}>
            <img src={LOGO} alt="GAS" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 22, fontWeight: 900, fontFamily: MONO, letterSpacing: '-0.5px', background: 'linear-gradient(135deg,#facc15,#f59e0b,#facc15)', backgroundSize: '200%', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text', animation: 'shimmer 2.5s linear infinite' }}>
              Golden AI Strategy
            </div>
            <div style={{ fontSize: 10, fontWeight: 700, color: T.textDim, letterSpacing: '0.22em', textTransform: 'uppercase', marginTop: 4, fontFamily: MONO }}>
              AI · Trading · Intelligence
            </div>
          </div>
        </div>

        {/* Step list */}
        <div style={{ width: 300 }}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginBottom: 20 }}>
            {STEPS.map((s, i) => {
              const done   = i < step;
              const active = i === step;
              const future = i > step;
              return (
                <div key={s.id}
                  className={done ? 'load-step-done' : active ? 'load-step-active' : ''}
                  style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    opacity: future ? 0.25 : 1,
                    transition: 'opacity 0.3s',
                  }}>
                  {/* Status dot */}
                  <div style={{
                    width: 18, height: 18, borderRadius: '50%', flexShrink: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: done ? 'rgba(52,211,153,0.15)' : active ? 'rgba(250,204,21,0.15)' : T.bgCard,
                    border: `1px solid ${done ? 'rgba(52,211,153,0.4)' : active ? 'rgba(250,204,21,0.5)' : T.border}`,
                    transition: 'all 0.3s',
                  }}>
                    {done
                      ? <svg width="9" height="9" viewBox="0 0 10 8" fill="none"><path d="M1 4l3 3 5-6" stroke="#34d399" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/></svg>
                      : active
                        ? <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#facc15', animation: 'dotBlink 1.2s ease infinite' }} />
                        : <div style={{ width: 5, height: 5, borderRadius: '50%', background: T.border }} />
                    }
                  </div>

                  {/* Label */}
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 11, fontWeight: done ? 700 : active ? 800 : 600, color: done ? T.textMid : active ? T.textPri : T.textDim, fontFamily: MONO, whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {s.label}
                    </div>
                    {active && (
                      <div style={{ fontSize: 9, color: T.textDim, marginTop: 1, fontFamily: MONO, animation: 'fadeSlideUp 0.2s ease' }}>{s.sub}</div>
                    )}
                  </div>

                  {/* Right pct */}
                  <span style={{ fontSize: 9, fontWeight: 800, fontFamily: MONO, color: done ? '#34d399' : active ? '#facc15' : T.textDim, flexShrink: 0 }}>
                    {done ? '✓' : active ? `${s.pct}%` : ''}
                  </span>
                </div>
              );
            })}
          </div>

          {/* Progress bar */}
          <div>
            <div style={{ height: 3, borderRadius: 2, background: T.barTrack, overflow: 'hidden', marginBottom: 6 }}>
              <div style={{
                height: '100%',
                width: `${cur.pct}%`,
                borderRadius: 2,
                background: cur.pct === 100
                  ? 'linear-gradient(90deg,#34d399,#10b981)'
                  : 'linear-gradient(90deg,#facc15,#f59e0b,#facc15)',
                backgroundSize: '200%',
                animation: cur.pct < 100 ? 'shimmer 1.8s linear infinite' : 'none',
                transition: 'width 0.6s cubic-bezier(0.4,0,0.2,1)',
              }} />
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: 9, color: T.textDim, fontFamily: MONO }}>
                {cur.pct < 100 ? 'Initializing...' : 'All systems go'}
              </span>
              <span style={{ fontSize: 9, fontWeight: 900, fontFamily: MONO, color: cur.pct === 100 ? '#34d399' : '#facc15' }}>
                {cur.pct}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* ── Bottom ticker strip ─────────────────────────── */}
      <div style={{
        position: 'absolute', bottom: 0, left: 0, right: 0, zIndex: 3,
        borderTop: `1px solid ${T.border}`,
        background: T.tickBg,
        backdropFilter: 'blur(8px)',
        overflow: 'hidden', height: 34,
        display: 'flex', alignItems: 'center',
      }}>
        {/* Left label */}
        <div style={{ padding: '0 12px', borderRight: `1px solid ${T.border}`, height: '100%', display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          <span style={{ fontSize: 9, fontWeight: 900, color: '#facc15', fontFamily: MONO, letterSpacing: '0.1em' }}>LIVE</span>
        </div>

        {/* Scrolling tickers */}
        <div style={{ flex: 1, overflow: 'hidden', position: 'relative' }}>
          <div style={{
            display: 'flex', gap: 0,
            transform: `translateX(-${offsetPx}px)`,
            willChange: 'transform',
          }}>
            {tickerItems.map((t, i) => (
              <div key={i} style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '0 20px', height: 34, flexShrink: 0, minWidth: 120,
                borderRight: `1px solid ${T.border}`,
              }}>
                <span style={{ fontSize: 10, fontWeight: 900, color: T.textMid, fontFamily: MONO }}>{t.s}</span>
                <span style={{ fontSize: 10, fontWeight: 700, color: T.textPri, fontFamily: MONO }}>{t.p}</span>
                <span style={{ fontSize: 9, fontWeight: 800, color: t.up ? '#34d399' : '#f87171', fontFamily: MONO }}>{t.c}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Right tag */}
        <div style={{ padding: '0 12px', borderLeft: `1px solid ${T.border}`, height: '100%', display: 'flex', alignItems: 'center', flexShrink: 0 }}>
          <span style={{ fontSize: 9, fontWeight: 700, color: T.textDim, fontFamily: MONO, letterSpacing: '0.08em' }}>21 AI</span>
        </div>
      </div>

      {/* ── Top scan line (subtle) ─────────────────────── */}
      <div style={{
        position: 'absolute', top: 0, left: 0, right: 0, height: 1,
        background: 'linear-gradient(90deg,transparent,rgba(250,204,21,0.4),transparent)',
        zIndex: 4,
      }} />
    </div>
  );
}
