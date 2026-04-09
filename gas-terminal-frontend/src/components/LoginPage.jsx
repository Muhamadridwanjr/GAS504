import React, { useState, useEffect } from 'react';
import { ArrowLeft, Zap, BarChart2, Shield, Brain, TrendingUp, Check } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const LOGO = '/logo-new.png';
const MONO = "'JetBrains Mono','Fira Code','Courier New',monospace";

const MODES = [
  { emoji: '💱', name: 'Forex AI',         color: '#f59e0b' },
  { emoji: '₿',  name: 'Binance AI',       color: '#f7931a' },
  { emoji: '🔮', name: 'Polymarket',       color: '#6366f1' },
  { emoji: '🎰', name: 'Memecoin Signal',  color: '#9945ff' },
];

const FEATURES = [
  { icon: Zap,       text: '21 AI Features · 4 Market Types' },
  { icon: Brain,     text: 'Claude · GPT · Gemini · Grok' },
  { icon: BarChart2, text: 'Live MT5 + Binance Real-Time Data' },
  { icon: Shield,    text: 'Anti-Rug · Risk Manager · Alerts' },
  { icon: TrendingUp,text: '94.2% Signal Accuracy (30d avg)' },
];

export default function LoginPage() {
  const { saveSession } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError]       = useState('');
  const [loading, setLoading]   = useState(false);

  // Sync theme from localStorage so page respects user preference
  useEffect(() => {
    const saved = localStorage.getItem('gas-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
  }, []);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      // Capture ?next= before saveSession changes the URL
      const next = new URLSearchParams(window.location.search).get('next');
      const res = await axios.post('/auth/v1/auth/login', { username, password });
      saveSession(res.data.access_token, res.data.user);
      if (next) window.location.href = next;
    } catch (err) {
      setError(err?.response?.data?.detail || 'Login gagal. Periksa username dan password.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-main)', color: 'var(--text-primary)' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
        .login-input {
          width: 100%;
          background: var(--bg-panel);
          border: 1.5px solid var(--border-color);
          border-radius: 10px;
          padding: 11px 14px;
          font-size: 14px;
          color: var(--text-primary);
          outline: none;
          transition: border-color 0.2s;
          box-sizing: border-box;
        }
        .login-input::placeholder { color: var(--text-dim); }
        .login-input:focus { border-color: var(--accent); }
      `}</style>

      {/* ─── LEFT: Promo Panel ─────────────────────────────────────── */}
      <div style={{
        display: 'none',
        flex: 1,
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '60px 56px',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #111 60%, #0d0b00 100%)',
      }} className="login-left">
        <style>{`
          @media (min-width: 1024px) { .login-left { display: flex !important; } }
        `}</style>

        {/* Glow effects */}
        <div style={{ position: 'absolute', top: '20%', left: '-10%', width: 400, height: 400, borderRadius: '50%', background: 'rgba(250,204,21,0.06)', filter: 'blur(80px)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: '10%', right: '-5%', width: 300, height: 300, borderRadius: '50%', background: 'rgba(153,69,255,0.05)', filter: 'blur(70px)', pointerEvents: 'none' }} />
        {/* Grid bg */}
        <div style={{
          position: 'absolute', inset: 0, zIndex: 0,
          backgroundImage: 'linear-gradient(rgba(255,255,255,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,0.03) 1px,transparent 1px)',
          backgroundSize: '48px 48px',
          maskImage: 'radial-gradient(ellipse 80% 80% at 30% 50%,black 20%,transparent 100%)',
          WebkitMaskImage: 'radial-gradient(ellipse 80% 80% at 30% 50%,black 20%,transparent 100%)',
        }} />

        <div style={{ position: 'relative', zIndex: 1 }}>
          {/* Back link */}
          <a href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'rgba(255,255,255,0.4)', fontSize: 12, fontWeight: 700, textDecoration: 'none', marginBottom: 48, transition: 'color 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.color = '#facc15'}
            onMouseLeave={e => e.currentTarget.style.color = 'rgba(255,255,255,0.4)'}>
            <ArrowLeft size={13} /> Kembali ke Home
          </a>

          {/* Brand */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 32 }}>
            <img src={LOGO} alt="GAS" style={{ width: 48, height: 48, borderRadius: 14, objectFit: 'cover', border: '2px solid rgba(250,204,21,0.3)' }} />
            <div>
              <div style={{ fontSize: 18, fontWeight: 900, color: '#facc15', fontFamily: MONO }}>Golden AI</div>
              <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.5)', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase' }}>Strategy Platform</div>
            </div>
          </div>

          {/* Headline */}
          <h2 style={{ fontSize: 'clamp(28px,3vw,40px)', fontWeight: 900, lineHeight: 1.1, marginBottom: 12, fontFamily: MONO, color: '#fff' }}>
            The #1 AI Trading<br />
            <span style={{ background: 'linear-gradient(135deg,#facc15,#f59e0b)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Super App</span>
          </h2>
          <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7, marginBottom: 32, maxWidth: 360 }}>
            Multi market · 21 AI features · Real-time intelligence untuk Forex, Crypto, Prediction, dan Memecoin.
          </p>

          {/* 4 mode chips */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 36 }}>
            {MODES.map((m, i) => (
              <div key={i} style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                padding: '6px 12px', borderRadius: 8, fontSize: 12, fontWeight: 700,
                background: `${m.color}15`, border: `1px solid ${m.color}35`, color: m.color,
              }}>
                {m.emoji} {m.name}
              </div>
            ))}
          </div>

          {/* Feature list */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {FEATURES.map((f, i) => {
              const Icon = f.icon;
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 8, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Icon size={13} style={{ color: '#facc15' }} />
                  </div>
                  <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>{f.text}</span>
                </div>
              );
            })}
          </div>

          {/* Stats row */}
          <div style={{ display: 'flex', gap: 24, marginTop: 40, paddingTop: 32, borderTop: '1px solid rgba(255,255,255,0.07)' }}>
            {[
              { v: '12,400+', l: 'Traders' },
              { v: '94.2%',   l: 'Akurasi' },
              { v: '21',      l: 'Fitur AI' },
            ].map((s, i) => (
              <div key={i}>
                <div style={{ fontSize: 20, fontWeight: 900, color: '#facc15', fontFamily: MONO }}>{s.v}</div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ─── RIGHT: Login Form ─────────────────────────────────────── */}
      <div style={{
        width: '100%',
        maxWidth: 480,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '40px 32px',
        background: 'var(--bg-card)',
        borderLeft: '1px solid var(--border-color)',
        margin: '0 auto',
      }} className="login-right">
        <style>{`
          @media (min-width: 1024px) {
            .login-right { max-width: 460px !important; margin: 0 !important; }
          }
        `}</style>

        {/* Mobile back + logo */}
        <a href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--text-dim)', fontSize: 12, fontWeight: 700, textDecoration: 'none', marginBottom: 32, transition: 'color 0.2s' }}
          className="lg-hidden"
          onMouseEnter={e => e.currentTarget.style.color = 'var(--accent)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--text-dim)'}>
          <ArrowLeft size={13} /> Kembali ke Home
        </a>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 32 }}>
          <img src={LOGO} alt="GAS" style={{ width: 40, height: 40, borderRadius: 12, objectFit: 'cover', border: '2px solid var(--border-color)' }} />
          <div>
            <div style={{ fontSize: 15, fontWeight: 900, color: 'var(--accent)', fontFamily: MONO }}>Golden AI Strategy</div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }}>AI Trading Platform</div>
          </div>
        </div>

        <h1 style={{ fontSize: 24, fontWeight: 900, color: 'var(--text-primary)', marginBottom: 6, letterSpacing: '-0.5px' }}>Selamat Datang</h1>
        <p style={{ fontSize: 13, color: 'var(--text-dim)', marginBottom: 32 }}>Masuk ke akun Golden AI Strategy kamu</p>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: '10px 14px', fontSize: 12, color: '#f87171', marginBottom: 20, textAlign: 'center' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          <div>
            <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Username / Email</label>
            <input
              className="login-input"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              placeholder="Username atau email"
              required
              autoComplete="username"
            />
          </div>

          <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
              <label style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Password</label>
              <a href="#" style={{ fontSize: 11, color: 'var(--accent)', fontWeight: 700, textDecoration: 'none' }}>Lupa password?</a>
            </div>
            <input
              className="login-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              autoComplete="current-password"
            />
          </div>

          <button type="submit" disabled={loading} style={{
            width: '100%', background: '#facc15', color: '#000', border: 'none',
            borderRadius: 12, padding: '13px', fontSize: 15, fontWeight: 900,
            cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1,
            boxShadow: '0 4px 20px rgba(250,204,21,0.35)', transition: 'transform 0.15s, box-shadow 0.15s',
            marginTop: 4,
          }}
          onMouseEnter={e => { if (!loading) { e.currentTarget.style.transform = 'translateY(-2px)'; e.currentTarget.style.boxShadow = '0 8px 32px rgba(250,204,21,0.5)'; } }}
          onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 4px 20px rgba(250,204,21,0.35)'; }}>
            {loading ? 'Masuk...' : 'Masuk →'}
          </button>
        </form>

        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-dim)', marginTop: 28 }}>
          Belum punya akun?{' '}
          <a href="/signup" style={{ color: 'var(--accent)', fontWeight: 800, textDecoration: 'none' }}>Daftar Gratis</a>
        </p>

        {/* Trust badges */}
        <div style={{ marginTop: 40, paddingTop: 24, borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap' }}>
          {['🔒 SSL Secured', '⚡ 21 AI Features', '💳 Tanpa Kartu Kredit'].map((t, i) => (
            <span key={i} style={{ fontSize: 11, color: 'var(--text-dim)', fontWeight: 600 }}>{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
