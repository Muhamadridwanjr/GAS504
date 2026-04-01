import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';

export default function LinkTelegramPage() {
  const { user, token } = useAuth();
  const params = new URLSearchParams(window.location.search);
  const code   = params.get('code') || '';

  const [status, setStatus] = useState('idle'); // idle | loading | ok | error
  const [msg,    setMsg]    = useState('');

  // Auto-link as soon as we have both code + token
  useEffect(() => {
    if (code && token && status === 'idle') doLink();
  }, [token, code]);

  async function doLink() {
    if (!code) { setStatus('error'); setMsg('Kode tidak ditemukan di URL. Ulangi dari bot Telegram.'); return; }
    if (!token) {
      // Save code to sessionStorage so we can resume after login
      sessionStorage.setItem('tg-link-code', code);
      window.location.href = `/login?next=${encodeURIComponent(window.location.href)}`;
      return;
    }
    setStatus('loading');
    try {
      const res = await fetch('/web/api/v1/telegram/link-v2', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ code }),
      });
      const data = await res.json();
      if (!res.ok) { setStatus('error'); setMsg(data.detail || 'Gagal menghubungkan akun.'); return; }
      sessionStorage.removeItem('tg-link-code');
      setStatus('ok');
      setMsg(data.message || 'Akun berhasil dihubungkan!');
    } catch {
      setStatus('error');
      setMsg('Gagal terhubung ke server. Coba lagi.');
    }
  }

  const s = {
    wrap:  { minHeight:'100vh', display:'flex', alignItems:'center', justifyContent:'center',
              background:'#F0F2F8', fontFamily:"'Segoe UI',Arial,sans-serif", padding:16 },
    card:  { background:'#fff', borderRadius:16, padding:'40px 36px', maxWidth:420, width:'100%',
              boxShadow:'0 4px 24px rgba(0,0,0,0.10)', textAlign:'center', border:'1.5px solid #E8D9A0' },
    logo:  { width:52, height:52, borderRadius:10, border:'2px solid #C9930A', marginBottom:16 },
    h2:    { color:'#1A1A2E', fontSize:20, fontWeight:800, margin:'0 0 8px' },
    sub:   { color:'#6B7280', fontSize:13, marginBottom:24 },
    code:  { background:'#F9FAFB', border:'1.5px solid #E5E7EB', borderRadius:8, padding:'10px 16px',
              fontFamily:'monospace', fontSize:22, letterSpacing:6, fontWeight:800,
              color:'#C9930A', margin:'0 0 20px', wordBreak:'break-all' },
    btn:   (bg='#C9930A') => ({ background:bg, color:'#fff', border:'none', borderRadius:8,
              padding:'12px 32px', fontWeight:800, fontSize:14, cursor:'pointer',
              width:'100%', marginTop:16 }),
    ok:    { color:'#059669', fontWeight:700, fontSize:15, margin:'16px 0 0' },
    err:   { color:'#DC2626', fontWeight:600, fontSize:13, margin:'16px 0 0' },
    muted: { color:'#6B7280', fontSize:12, marginTop:12, lineHeight:1.6 },
  };

  return (
    <div style={s.wrap}>
      <div style={s.card}>
        <img src="https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg" alt="GAS" style={s.logo} />
        <h2 style={s.h2}>Hubungkan Telegram ke GAS</h2>
        <p style={s.sub}>Golden AI Strategy Bot</p>

        {code && <div style={s.code}>{code}</div>}

        {/* Not logged in — prompt to login */}
        {!token && status === 'idle' && (
          <>
            <p style={{ color:'#6B7280', fontSize:13, marginBottom:4 }}>
              Kamu perlu login ke akun GAS terlebih dahulu.
            </p>
            <button style={s.btn()} onClick={doLink}>
              🔐 Login & Hubungkan
            </button>
          </>
        )}

        {/* Logged in, waiting / auto-processing */}
        {token && status === 'idle' && (
          <p style={{ color:'#6B7280', fontSize:13 }}>⏳ Memproses penghubungan akun...</p>
        )}

        {status === 'loading' && (
          <p style={{ color:'#6B7280', fontSize:13 }}>⏳ Menghubungkan akun...</p>
        )}

        {status === 'ok' && (
          <>
            <p style={s.ok}>✅ {msg}</p>
            <p style={s.muted}>
              Kembali ke bot Telegram dan ketik <strong>/start</strong> untuk mulai
              menggunakan GAS Bot AI Analysis.
            </p>
            <button style={s.btn('#059669')} onClick={() => window.location.href = '/'}>
              🚀 Buka Terminal GAS
            </button>
          </>
        )}

        {status === 'error' && (
          <>
            <p style={s.err}>❌ {msg}</p>
            <p style={s.muted}>
              Kode link berlaku <strong>15 menit</strong>. Jika kadaluwarsa, ketik
              /link lagi di bot untuk kode baru.
            </p>
            <button style={s.btn('#1D4ED8')} onClick={() => window.location.href = '/'}>
              Kembali ke Terminal
            </button>
          </>
        )}
      </div>
    </div>
  );
}
