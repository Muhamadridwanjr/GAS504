import React, { useState, useEffect, useRef } from 'react';
import { Eye, EyeOff, ArrowLeft, Check, Mail, Shield, RefreshCw, Zap, Brain, BarChart2, TrendingUp } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const LOGO = '/logo-new.png';
const MONO = "'JetBrains Mono','Fira Code','Courier New',monospace";

const MODES = [
  { emoji: '💱', name: 'Forex AI',        color: '#f59e0b' },
  { emoji: '₿',  name: 'Binance AI',      color: '#f7931a' },
  { emoji: '🔮', name: 'Polymarket',      color: '#6366f1' },
  { emoji: '🎰', name: 'Memecoin Signal', color: '#9945ff' },
];

const PERKS = [
  { icon: Zap,       text: '21 AI Features · 4 Market Types' },
  { icon: Brain,     text: 'Claude · GPT · Gemini · Grok' },
  { icon: BarChart2, text: 'Live MT5 + Binance Real-Time Data' },
  { icon: TrendingUp,text: '94.2% Signal Accuracy (30d avg)' },
];

export default function SignupPage() {
  const { saveSession } = useAuth();
  const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', confirm: '' });
  const [showPass, setShowPass] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  // OTP state
  const [step, setStep] = useState('form'); // 'form' | 'otp'
  const [otp, setOtp] = useState(['', '', '', '', '', '']);
  const [otpSending, setOtpSending] = useState(false);
  const [cooldown, setCooldown] = useState(0);
  const otpRefs = useRef([]);
  const cooldownRef = useRef(null);

  // Sync theme from localStorage so page respects user preference
  useEffect(() => {
    const saved = localStorage.getItem('gas-theme') || 'dark';
    document.documentElement.setAttribute('data-theme', saved);
  }, []);

  const set = (k) => (e) => setForm(prev => ({ ...prev, [k]: e.target.value }));

  useEffect(() => {
    if (cooldown > 0) {
      cooldownRef.current = setTimeout(() => setCooldown(c => c - 1), 1000);
    }
    return () => clearTimeout(cooldownRef.current);
  }, [cooldown]);

  const validateForm = () => {
    if (!form.username.trim()) return 'Username wajib diisi.';
    if (!form.email.trim() || !form.email.includes('@')) return 'Email tidak valid.';
    if (form.password.length < 8) return 'Password minimal 8 karakter.';
    if (form.password !== form.confirm) return 'Password tidak cocok.';
    return '';
  };

  const handleSendOtp = async () => {
    const err = validateForm();
    if (err) { setError(err); return; }
    setError('');
    setOtpSending(true);
    try {
      await axios.post('/auth/v1/auth/send-otp', {
        email: form.email.trim(),
        username: form.username.trim(),
      });
      setStep('otp');
      setCooldown(60);
      setTimeout(() => otpRefs.current[0]?.focus(), 200);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Gagal kirim OTP. Coba lagi.');
    } finally {
      setOtpSending(false);
    }
  };

  const handleResendOtp = async () => {
    if (cooldown > 0) return;
    setError('');
    setOtpSending(true);
    try {
      await axios.post('/auth/v1/auth/send-otp', {
        email: form.email.trim(),
        username: form.username.trim(),
      });
      setCooldown(60);
      setOtp(['', '', '', '', '', '']);
      setTimeout(() => otpRefs.current[0]?.focus(), 100);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Gagal kirim ulang OTP.');
    } finally {
      setOtpSending(false);
    }
  };

  const handleOtpChange = (i, val) => {
    if (!/^\d?$/.test(val)) return;
    const next = [...otp];
    next[i] = val;
    setOtp(next);
    if (val && i < 5) otpRefs.current[i + 1]?.focus();
  };

  const handleOtpKeyDown = (i, e) => {
    if (e.key === 'Backspace' && !otp[i] && i > 0) {
      otpRefs.current[i - 1]?.focus();
    }
  };

  const handleOtpPaste = (e) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6);
    if (pasted.length === 6) {
      setOtp(pasted.split(''));
      otpRefs.current[5]?.focus();
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const otpCode = otp.join('');
    if (otpCode.length < 6) { setError('Masukkan 6 digit kode OTP.'); return; }
    setError('');
    setLoading(true);
    try {
      const res = await axios.post('/auth/v1/auth/register', {
        username: form.username.trim(),
        email: form.email.trim(),
        full_name: form.full_name.trim(),
        password: form.password,
        otp: otpCode,
      });
      saveSession(res.data.access_token, res.data.user);
    } catch (err) {
      setError(err?.response?.data?.detail || 'Registrasi gagal. Coba lagi.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', background: 'var(--bg-main)', color: 'var(--text-primary)' }}>
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
        .signup-input {
          width: 100%;
          background: var(--bg-panel);
          border: 1.5px solid var(--border-color);
          border-radius: 10px;
          padding: 10px 14px;
          font-size: 13px;
          color: var(--text-primary);
          outline: none;
          transition: border-color 0.2s;
          box-sizing: border-box;
        }
        .signup-input::placeholder { color: var(--text-dim); }
        .signup-input:focus { border-color: var(--accent); }
      `}</style>

      {/* ─── LEFT: Promo Panel (always dark) ─────────────────────────── */}
      <div style={{
        display: 'none',
        flex: 1,
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '60px 56px',
        position: 'relative',
        overflow: 'hidden',
        background: 'linear-gradient(135deg, #0a0a0a 0%, #111 60%, #0d0b00 100%)',
      }} className="signup-left">
        <style>{`
          @media (min-width: 1024px) { .signup-left { display: flex !important; } }
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
            Mulai Trading<br />
            <span style={{ background: 'linear-gradient(135deg,#facc15,#f59e0b)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>Lebih Cerdas</span>
          </h2>
          <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', lineHeight: 1.7, marginBottom: 32, maxWidth: 360 }}>
            Bergabung dengan 12,400+ trader yang memanfaatkan 21 fitur AI untuk Forex, Crypto, Prediction, dan Memecoin.
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
            {PERKS.map((p, i) => {
              const Icon = p.icon;
              return (
                <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 28, height: 28, borderRadius: 8, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                    <Icon size={13} style={{ color: '#facc15' }} />
                  </div>
                  <span style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)', fontWeight: 600 }}>{p.text}</span>
                </div>
              );
            })}
          </div>

          {/* Stats row */}
          <div style={{ display: 'flex', gap: 24, marginTop: 40, paddingTop: 32, borderTop: '1px solid rgba(255,255,255,0.07)' }}>
            {[
              { v: '12,400+', l: 'Traders' },
              { v: 'GRATIS',  l: 'Mulai Sekarang' },
              { v: '21',     l: 'Fitur AI' },
            ].map((s, i) => (
              <div key={i}>
                <div style={{ fontSize: 20, fontWeight: 900, color: '#facc15', fontFamily: MONO }}>{s.v}</div>
                <div style={{ fontSize: 11, color: 'rgba(255,255,255,0.4)', marginTop: 2 }}>{s.l}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ─── RIGHT: Signup Form ─────────────────────────────────────── */}
      <div style={{
        width: '100%',
        maxWidth: 520,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        padding: '40px 32px',
        background: 'var(--bg-card)',
        borderLeft: '1px solid var(--border-color)',
        margin: '0 auto',
        overflowY: 'auto',
      }} className="signup-right">
        <style>{`
          @media (min-width: 1024px) {
            .signup-right { max-width: 520px !important; margin: 0 !important; }
          }
        `}</style>

        {/* Mobile back + logo */}
        <a href="/" style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--text-dim)', fontSize: 12, fontWeight: 700, textDecoration: 'none', marginBottom: 24, transition: 'color 0.2s' }}
          className="lg-hidden"
          onMouseEnter={e => e.currentTarget.style.color = 'var(--accent)'}
          onMouseLeave={e => e.currentTarget.style.color = 'var(--text-dim)'}>
          <ArrowLeft size={13} /> Kembali ke Home
        </a>

        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
          <img src={LOGO} alt="GAS" style={{ width: 40, height: 40, borderRadius: 12, objectFit: 'cover', border: '2px solid var(--border-color)' }} />
          <div>
            <div style={{ fontSize: 15, fontWeight: 900, color: 'var(--accent)', fontFamily: MONO }}>Golden AI Strategy</div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase' }}>AI Trading Platform</div>
          </div>
        </div>

        {/* Step indicator */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: step === 'form' ? 'var(--accent)' : '#4ade80' }}>
            <div style={{
              width: 24, height: 24, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 10, fontWeight: 900, border: '2px solid',
              borderColor: step === 'otp' ? '#4ade80' : 'var(--accent)',
              background: step === 'otp' ? 'rgba(74,222,128,0.1)' : 'var(--accent)',
              color: step === 'otp' ? '#4ade80' : '#000',
            }}>
              {step === 'otp' ? <Check size={11} /> : '1'}
            </div>
            <span style={{ fontSize: 10, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Data Akun</span>
          </div>
          <div style={{ flex: 1, height: 1, background: step === 'otp' ? 'rgba(250,204,21,0.4)' : 'var(--border-color)', transition: 'background 0.3s' }} />
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: step === 'otp' ? 'var(--accent)' : 'var(--text-dim)' }}>
            <div style={{
              width: 24, height: 24, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 10, fontWeight: 900, border: '2px solid',
              borderColor: step === 'otp' ? 'var(--accent)' : 'var(--border-color)',
              background: step === 'otp' ? 'var(--accent)' : 'transparent',
              color: step === 'otp' ? '#000' : 'var(--text-dim)',
            }}>2</div>
            <span style={{ fontSize: 10, fontWeight: 900, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Verifikasi OTP</span>
          </div>
        </div>

        {error && (
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: '10px 14px', fontSize: 12, color: '#f87171', marginBottom: 16, textAlign: 'center' }}>
            {error}
          </div>
        )}

        {/* STEP 1: Form */}
        {step === 'form' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
            <div>
              <h1 style={{ fontSize: 22, fontWeight: 900, color: 'var(--text-primary)', marginBottom: 4 }}>Buat Akun Gratis</h1>
              <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>Email akan diverifikasi · Tanpa kartu kredit</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
              <div>
                <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5 }}>Nama Lengkap</label>
                <input className="signup-input" type="text" value={form.full_name} onChange={set('full_name')} placeholder="John Doe" autoComplete="name" />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5 }}>Username <span style={{ color: '#f87171' }}>*</span></label>
                <input className="signup-input" type="text" value={form.username} onChange={set('username')} placeholder="johndoe" required autoComplete="username" />
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5 }}>Email <span style={{ color: '#f87171' }}>*</span></label>
              <input className="signup-input" type="email" value={form.email} onChange={set('email')} placeholder="john@email.com" required autoComplete="email" />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5 }}>Password <span style={{ color: '#f87171' }}>*</span></label>
              <div style={{ position: 'relative' }}>
                <input className="signup-input" type={showPass ? 'text' : 'password'} value={form.password} onChange={set('password')} placeholder="Min. 8 karakter" required minLength={8} style={{ paddingRight: 40 }} autoComplete="new-password" />
                <button type="button" onClick={() => setShowPass(!showPass)} style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', padding: 0 }}>
                  {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                </button>
              </div>
            </div>

            <div>
              <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 5 }}>Konfirmasi Password <span style={{ color: '#f87171' }}>*</span></label>
              <input className="signup-input" type="password" value={form.confirm} onChange={set('confirm')} placeholder="Ulangi password" required autoComplete="new-password" />
            </div>

            <p style={{ fontSize: 10, color: 'var(--text-dim)', lineHeight: 1.6 }}>
              Dengan mendaftar, kamu setuju dengan{' '}
              <a href="#" style={{ color: 'var(--accent)', textDecoration: 'none' }}>Terms of Service</a>{' '}dan{' '}
              <a href="#" style={{ color: 'var(--accent)', textDecoration: 'none' }}>Privacy Policy</a> kami.
            </p>

            <button onClick={handleSendOtp} disabled={otpSending} style={{
              width: '100%', background: '#facc15', color: '#000', border: 'none',
              borderRadius: 12, padding: '13px', fontSize: 14, fontWeight: 900,
              cursor: otpSending ? 'not-allowed' : 'pointer', opacity: otpSending ? 0.6 : 1,
              boxShadow: '0 4px 20px rgba(250,204,21,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}>
              {otpSending
                ? <><RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Mengirim OTP...</>
                : <><Mail size={14} /> Kirim Kode OTP ke Email</>}
            </button>
          </div>
        )}

        {/* STEP 2: OTP Verification */}
        {step === 'otp' && (
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
            <div style={{ textAlign: 'center' }}>
              <div style={{ width: 56, height: 56, borderRadius: 16, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.2)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 12px' }}>
                <Shield size={24} style={{ color: 'var(--accent)' }} />
              </div>
              <h1 style={{ fontSize: 18, fontWeight: 900, color: 'var(--text-primary)', marginBottom: 4 }}>Verifikasi Email</h1>
              <p style={{ fontSize: 12, color: 'var(--text-dim)' }}>Kode 6 digit dikirim ke</p>
              <p style={{ fontSize: 13, fontWeight: 900, color: 'var(--accent)', marginTop: 4 }}>{form.email}</p>
            </div>

            {/* OTP Input Boxes */}
            <div style={{ display: 'flex', gap: 8, justifyContent: 'center' }} onPaste={handleOtpPaste}>
              {otp.map((digit, i) => (
                <input
                  key={i}
                  ref={el => otpRefs.current[i] = el}
                  type="text"
                  inputMode="numeric"
                  maxLength={1}
                  value={digit}
                  onChange={e => handleOtpChange(i, e.target.value)}
                  onKeyDown={e => handleOtpKeyDown(i, e)}
                  style={{
                    width: 44, height: 56, textAlign: 'center', fontSize: 22, fontWeight: 900,
                    background: 'var(--bg-panel)', borderRadius: 12, outline: 'none',
                    border: `2px solid ${digit ? 'var(--accent)' : 'var(--border-color)'}`,
                    color: digit ? 'var(--accent)' : 'var(--text-primary)',
                    boxShadow: digit ? '0 0 12px rgba(250,204,21,0.2)' : 'none',
                    transition: 'border-color 0.2s, box-shadow 0.2s',
                  }}
                />
              ))}
            </div>

            <button type="submit" disabled={loading || otp.join('').length < 6} style={{
              width: '100%', background: '#facc15', color: '#000', border: 'none',
              borderRadius: 12, padding: '13px', fontSize: 14, fontWeight: 900,
              cursor: (loading || otp.join('').length < 6) ? 'not-allowed' : 'pointer',
              opacity: (loading || otp.join('').length < 6) ? 0.5 : 1,
              boxShadow: '0 4px 20px rgba(250,204,21,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
            }}>
              {loading
                ? <><RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> Membuat Akun...</>
                : <><Check size={14} /> Verifikasi & Buat Akun</>}
            </button>

            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', fontSize: 11 }}>
              <button type="button" onClick={() => { setStep('form'); setError(''); setOtp(['','','','','','']); }}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4, padding: 0 }}>
                <ArrowLeft size={10} /> Edit Data
              </button>
              <button type="button" onClick={handleResendOtp} disabled={cooldown > 0 || otpSending}
                style={{ background: 'none', border: 'none', cursor: cooldown > 0 ? 'not-allowed' : 'pointer', color: 'var(--accent)', fontWeight: 900, opacity: (cooldown > 0 || otpSending) ? 0.4 : 1, display: 'flex', alignItems: 'center', gap: 4, padding: 0 }}>
                {otpSending && <RefreshCw size={10} />}
                {cooldown > 0 ? `Kirim ulang dalam ${cooldown}s` : 'Kirim ulang OTP'}
              </button>
            </div>
          </form>
        )}

        <p style={{ textAlign: 'center', fontSize: 13, color: 'var(--text-dim)', marginTop: 24 }}>
          Sudah punya akun?{' '}
          <a href="/login" style={{ color: 'var(--accent)', fontWeight: 800, textDecoration: 'none' }}>Sign In</a>
        </p>

        {/* Trust badges */}
        <div style={{ marginTop: 32, paddingTop: 20, borderTop: '1px solid var(--border-color)', display: 'flex', justifyContent: 'center', gap: 20, flexWrap: 'wrap' }}>
          {['🔒 SSL Secured', '⚡ 21 AI Features', '💳 Tanpa Kartu Kredit'].map((t, i) => (
            <span key={i} style={{ fontSize: 11, color: 'var(--text-dim)', fontWeight: 600 }}>{t}</span>
          ))}
        </div>
      </div>
    </div>
  );
}
