import React, { useState, useEffect } from 'react';
import {
  User, Mail, Lock, Shield, Zap, Trophy, Star,
  Check, Eye, EyeOff, Copy, Crown,
  LogOut, Trash2, TrendingUp, Award, Sparkles,
  Bell, Gift, ChevronRight, RefreshCw
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

/* ─── Constants ──────────────────────────────────────────────── */
const MONO = "'JetBrains Mono','Fira Code','Courier New',monospace";

const TIER_META = {
  free:      { label: 'Free',      color: '#9ca3af', bg: 'rgba(156,163,175,0.1)', border: 'rgba(156,163,175,0.2)' },
  essential: { label: 'Essential', color: '#60a5fa', bg: 'rgba(96,165,250,0.1)',  border: 'rgba(96,165,250,0.2)' },
  plus:      { label: 'Plus',      color: '#a78bfa', bg: 'rgba(167,139,250,0.1)', border: 'rgba(167,139,250,0.2)' },
  premium:   { label: 'Premium',   color: '#facc15', bg: 'rgba(250,204,21,0.1)',  border: 'rgba(250,204,21,0.2)' },
  ultimate:  { label: 'Ultimate',  color: '#fb923c', bg: 'rgba(251,146,60,0.1)',  border: 'rgba(251,146,60,0.2)' },
};
const TIER_ICON = { free: Star, essential: Zap, plus: Crown, premium: Trophy, ultimate: Award };

const LEVEL_BADGES = [
  { level: 1,  emoji: '🌱', label: 'Rookie',       color: '#6b7280', glow: 'rgba(107,114,128,0.3)' },
  { level: 2,  emoji: '📊', label: 'Apprentice',   color: '#60a5fa', glow: 'rgba(96,165,250,0.3)' },
  { level: 3,  emoji: '⚡', label: 'Trader',       color: '#34d399', glow: 'rgba(52,211,153,0.3)' },
  { level: 4,  emoji: '📈', label: 'Analyst',      color: '#818cf8', glow: 'rgba(129,140,248,0.3)' },
  { level: 5,  emoji: '🎯', label: 'Strategist',   color: '#f472b6', glow: 'rgba(244,114,182,0.3)' },
  { level: 6,  emoji: '🔥', label: 'Expert',       color: '#fb923c', glow: 'rgba(251,146,60,0.3)' },
  { level: 7,  emoji: '💎', label: 'Master',       color: '#38bdf8', glow: 'rgba(56,189,248,0.3)' },
  { level: 8,  emoji: '🚀', label: 'Elite',        color: '#a78bfa', glow: 'rgba(167,139,250,0.3)' },
  { level: 9,  emoji: '👑', label: 'Champion',     color: '#facc15', glow: 'rgba(250,204,21,0.3)' },
  { level: 10, emoji: '🌟', label: 'Legend',       color: '#facc15', glow: 'rgba(250,204,21,0.4)' },
  { level: 11, emoji: '🏆', label: 'Grand Master', color: '#f59e0b', glow: 'rgba(245,158,11,0.4)' },
  { level: 12, emoji: '⚔️', label: 'Warrior',     color: '#ef4444', glow: 'rgba(239,68,68,0.3)' },
  { level: 13, emoji: '🦅', label: 'Eagle',        color: '#0ea5e9', glow: 'rgba(14,165,233,0.3)' },
  { level: 14, emoji: '🌊', label: 'Wave Rider',   color: '#06b6d4', glow: 'rgba(6,182,212,0.3)' },
  { level: 15, emoji: '🌙', label: 'Night Hunter', color: '#7c3aed', glow: 'rgba(124,58,237,0.3)' },
  { level: 20, emoji: '🥇', label: 'GAS GOD',      color: '#facc15', glow: 'rgba(250,204,21,0.6)' },
];

/* ─── Preset Avatars (DiceBear generative art) ───────────────── */
const PRESET_AVATARS = [
  // Abstract / Ethereum-style shapes
  { id: 's1',  url: 'https://api.dicebear.com/7.x/shapes/svg?seed=alpha&backgroundColor=facc15',  label: 'Alpha',    cat: 'Abstract' },
  { id: 's2',  url: 'https://api.dicebear.com/7.x/shapes/svg?seed=delta&backgroundColor=818cf8',  label: 'Delta',    cat: 'Abstract' },
  { id: 's3',  url: 'https://api.dicebear.com/7.x/shapes/svg?seed=omega&backgroundColor=34d399',  label: 'Omega',    cat: 'Abstract' },
  { id: 's4',  url: 'https://api.dicebear.com/7.x/shapes/svg?seed=sigma&backgroundColor=f472b6',  label: 'Sigma',    cat: 'Abstract' },
  { id: 's5',  url: 'https://api.dicebear.com/7.x/shapes/svg?seed=nexus&backgroundColor=38bdf8',  label: 'Nexus',    cat: 'Abstract' },
  { id: 's6',  url: 'https://api.dicebear.com/7.x/shapes/svg?seed=vault&backgroundColor=fb923c',  label: 'Vault',    cat: 'Abstract' },
  // Robot / Tech
  { id: 'b1',  url: 'https://api.dicebear.com/7.x/bottts/svg?seed=GAS01&backgroundColor=1e293b',  label: 'Bot-01',   cat: 'Robot' },
  { id: 'b2',  url: 'https://api.dicebear.com/7.x/bottts/svg?seed=GAS02&backgroundColor=1e293b',  label: 'Bot-02',   cat: 'Robot' },
  { id: 'b3',  url: 'https://api.dicebear.com/7.x/bottts/svg?seed=GAS03&backgroundColor=1e293b',  label: 'Bot-03',   cat: 'Robot' },
  { id: 'b4',  url: 'https://api.dicebear.com/7.x/bottts/svg?seed=GAS04&backgroundColor=1e293b',  label: 'Bot-04',   cat: 'Robot' },
  // Thumbs / Characters
  { id: 't1',  url: 'https://api.dicebear.com/7.x/thumbs/svg?seed=trader&backgroundColor=0f172a', label: 'Trader',   cat: 'Karakter' },
  { id: 't2',  url: 'https://api.dicebear.com/7.x/thumbs/svg?seed=whale&backgroundColor=0f172a',  label: 'Whale',    cat: 'Karakter' },
  { id: 't3',  url: 'https://api.dicebear.com/7.x/thumbs/svg?seed=bull&backgroundColor=0f172a',   label: 'Bull',     cat: 'Karakter' },
  { id: 't4',  url: 'https://api.dicebear.com/7.x/thumbs/svg?seed=bear&backgroundColor=0f172a',   label: 'Bear',     cat: 'Karakter' },
  // Pixel Art
  { id: 'p1',  url: 'https://api.dicebear.com/7.x/pixel-art/svg?seed=degen&backgroundColor=1a1a2e', label: 'Degen',  cat: 'Pixel' },
  { id: 'p2',  url: 'https://api.dicebear.com/7.x/pixel-art/svg?seed=hodl&backgroundColor=1a1a2e',  label: 'HODL',   cat: 'Pixel' },
  { id: 'p3',  url: 'https://api.dicebear.com/7.x/pixel-art/svg?seed=ape&backgroundColor=1a1a2e',   label: 'Ape',    cat: 'Pixel' },
  { id: 'p4',  url: 'https://api.dicebear.com/7.x/pixel-art/svg?seed=satoshi&backgroundColor=1a1a2e', label: 'Satoshi', cat: 'Pixel' },
];

const AVATAR_CATS = ['Semua', 'Abstract', 'Robot', 'Karakter', 'Pixel'];

/* ─── Sub-components ─────────────────────────────────────────── */
function StatCard({ label, value, sub, accent }) {
  return (
    <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 14, padding: '16px 18px' }}>
      <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 8 }}>{label}</p>
      <p style={{ fontSize: 24, fontWeight: 900, fontFamily: MONO, color: accent || 'var(--text-primary)' }}>{value}</p>
      {sub && <p style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 4 }}>{sub}</p>}
    </div>
  );
}

function Toggle({ checked, onChange }) {
  return (
    <div onClick={onChange} style={{
      width: 40, height: 22, borderRadius: 11, position: 'relative', cursor: 'pointer',
      background: checked ? '#facc15' : 'var(--bg-hover)', border: '1px solid var(--border-color)',
      transition: 'background 0.2s',
    }}>
      <div style={{
        position: 'absolute', top: 3, width: 14, height: 14, borderRadius: '50%', background: '#fff',
        transition: 'left 0.2s', left: checked ? 22 : 3,
        boxShadow: '0 1px 4px rgba(0,0,0,0.2)',
      }} />
    </div>
  );
}

/* ─── Avatar Picker Modal ─────────────────────────────────────── */
function AvatarPicker({ currentUrl, onSelect, onClose }) {
  const [cat, setCat] = useState('Semua');
  const [hovered, setHovered] = useState(null);
  const filtered = cat === 'Semua' ? PRESET_AVATARS : PRESET_AVATARS.filter(a => a.cat === cat);

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 100,
      background: 'rgba(0,0,0,0.75)', backdropFilter: 'blur(6px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      padding: '20px',
    }} onClick={onClose}>
      <div onClick={e => e.stopPropagation()} style={{
        background: 'var(--bg-card)', border: '1px solid var(--border-color)',
        borderRadius: 20, padding: '28px', width: '100%', maxWidth: 520,
        maxHeight: '85vh', overflowY: 'auto',
      }}>
        {/* Header */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <h2 style={{ fontSize: 18, fontWeight: 900, color: 'var(--text-primary)' }}>Pilih Avatar</h2>
            <p style={{ fontSize: 11, color: 'var(--text-dim)', marginTop: 2 }}>18 avatar generatif · Ethereum-style · Gratis</p>
          </div>
          <button onClick={onClose} style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 8, width: 32, height: 32, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-dim)' }}>✕</button>
        </div>

        {/* Category filter */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 20 }}>
          {AVATAR_CATS.map(c => (
            <button key={c} onClick={() => setCat(c)} style={{
              padding: '4px 12px', borderRadius: 20, fontSize: 11, fontWeight: 700, cursor: 'pointer', border: '1px solid',
              borderColor: cat === c ? '#facc15' : 'var(--border-color)',
              background: cat === c ? 'rgba(250,204,21,0.15)' : 'var(--bg-panel)',
              color: cat === c ? '#facc15' : 'var(--text-dim)',
            }}>{c}</button>
          ))}
        </div>

        {/* Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 12 }}>
          {filtered.map(av => {
            const isSelected = currentUrl === av.url;
            const isHov = hovered === av.id;
            return (
              <div key={av.id} onClick={() => onSelect(av.url)}
                onMouseEnter={() => setHovered(av.id)}
                onMouseLeave={() => setHovered(null)}
                style={{
                  cursor: 'pointer', borderRadius: 14, overflow: 'hidden',
                  border: `2px solid ${isSelected ? '#facc15' : isHov ? 'rgba(250,204,21,0.4)' : 'var(--border-color)'}`,
                  boxShadow: isSelected ? '0 0 20px rgba(250,204,21,0.35)' : isHov ? '0 0 12px rgba(250,204,21,0.2)' : 'none',
                  transform: isHov ? 'scale(1.04)' : 'scale(1)',
                  transition: 'all 0.15s',
                  position: 'relative',
                }}>
                <img src={av.url} alt={av.label} style={{ width: '100%', aspectRatio: '1', display: 'block' }} />
                {isSelected && (
                  <div style={{ position: 'absolute', top: 4, right: 4, background: '#facc15', borderRadius: '50%', width: 18, height: 18, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Check size={10} style={{ color: '#000' }} />
                  </div>
                )}
                <div style={{ background: 'var(--bg-panel)', padding: '4px 6px', textAlign: 'center' }}>
                  <span style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-dim)' }}>{av.label}</span>
                </div>
              </div>
            );
          })}
        </div>

        <p style={{ fontSize: 10, color: 'var(--text-dim)', textAlign: 'center', marginTop: 16 }}>
          Klik avatar untuk memilih · Powered by DiceBear
        </p>
      </div>
    </div>
  );
}

/* ─── Telegram Link Tab ──────────────────────────────────────── */
function TelegramLinkTab({ token, tgStatus, setTgStatus, tgLinkUrl, setTgLinkUrl, tgMsg, setTgMsg }) {
  const [loading, setLoading] = useState(false);
  const [linkCode, setLinkCode] = useState('');

  useEffect(() => {
    // Check if already linked
    axios.get('/web/api/v1/telegram/me', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => { if (r.data.linked) setTgStatus('linked'); })
      .catch(() => {});
  }, [token]);

  async function generateLink() {
    // User must generate link from the bot (/link command)
    // Here we show instructions + the link URL if they have a code
    setTgStatus('instructions');
  }

  async function submitCode() {
    if (!linkCode.trim()) return;
    setLoading(true);
    setTgMsg('');
    try {
      const res = await axios.post('/web/api/v1/telegram/link-v2',
        { code: linkCode.trim().toUpperCase() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setTgStatus('linked');
      setTgMsg(res.data.message || 'Akun Telegram berhasil dihubungkan!');
    } catch (e) {
      setTgMsg(e?.response?.data?.detail || 'Kode tidak valid atau sudah kadaluwarsa.');
    } finally {
      setLoading(false);
    }
  }

  async function unlink() {
    setLoading(true);
    try {
      await axios.delete('/web/api/v1/telegram/unlink', { headers: { Authorization: `Bearer ${token}` } });
      setTgStatus(null);
      setTgMsg('Akun Telegram berhasil dilepas.');
    } catch {
      setTgMsg('Gagal melepas akun.');
    } finally {
      setLoading(false);
    }
  }

  const card = { background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 16, padding: '24px', marginBottom: 16 };
  const btn  = (bg = 'var(--accent)', clr = '#000') => ({
    padding: '10px 22px', background: bg, color: clr, border: 'none',
    borderRadius: 10, fontSize: 13, fontWeight: 800, cursor: 'pointer',
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
      {/* Header */}
      <div style={{ ...card, textAlign: 'center' }}>
        <div style={{ fontSize: 40, marginBottom: 8 }}>✈️</div>
        <h3 style={{ fontSize: 18, fontWeight: 900, color: 'var(--text-primary)', margin: '0 0 6px' }}>
          GAS Telegram Bot
        </h3>
        <p style={{ fontSize: 13, color: 'var(--text-dim)', marginBottom: 0, lineHeight: 1.6 }}>
          Hubungkan akun GAS ke bot Telegram untuk AI Analysis langsung di chat.<br/>
          <strong style={{ color: 'var(--accent)' }}>Hanya untuk plan Ultimate & Ultra.</strong>
        </p>
      </div>

      {/* Status: Linked */}
      {tgStatus === 'linked' && (
        <div style={{ ...card, borderColor: '#22c55e', background: 'rgba(34,197,94,0.06)', textAlign: 'center' }}>
          <div style={{ fontSize: 32, marginBottom: 8 }}>✅</div>
          <p style={{ fontSize: 14, fontWeight: 700, color: '#22c55e', margin: '0 0 8px' }}>
            Akun Telegram Terhubung!
          </p>
          <p style={{ fontSize: 12, color: 'var(--text-dim)', marginBottom: 16, lineHeight: 1.6 }}>
            Buka bot <strong>@goldenaistrategy_bot</strong> dan ketik /start untuk mulai.
          </p>
          {tgMsg && <p style={{ color: '#22c55e', fontSize: 12, marginBottom: 12 }}>{tgMsg}</p>}
          <button style={btn('#ef4444', '#fff')} onClick={unlink} disabled={loading}>
            {loading ? '...' : '🔗 Putuskan Koneksi'}
          </button>
        </div>
      )}

      {/* Not linked: instructions + code input */}
      {tgStatus !== 'linked' && (
        <>
          <div style={card}>
            <p style={{ fontSize: 11, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>
              Cara Menghubungkan
            </p>
            {[
              { n: '1', text: 'Buka bot Telegram: @goldenaistrategy_bot' },
              { n: '2', text: 'Ketik /link → bot akan kirimkan kode 8 karakter' },
              { n: '3', text: 'Masukkan kode tersebut di form di bawah ini' },
            ].map(s => (
              <div key={s.n} style={{ display: 'flex', gap: 12, alignItems: 'flex-start', marginBottom: 12 }}>
                <div style={{ width: 24, height: 24, borderRadius: '50%', background: 'var(--accent)', color: '#000', fontSize: 11, fontWeight: 900, display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>{s.n}</div>
                <p style={{ fontSize: 13, color: 'var(--text-secondary)', margin: 0, lineHeight: 1.5 }}>{s.text}</p>
              </div>
            ))}
            <a href="https://t.me/goldenaistrategy_bot" target="_blank" rel="noopener noreferrer"
               style={{ display: 'inline-block', marginTop: 4, padding: '8px 18px', background: '#0088cc', color: '#fff', borderRadius: 8, fontSize: 12, fontWeight: 700, textDecoration: 'none' }}>
              📲 Buka Bot Telegram
            </a>
          </div>

          <div style={card}>
            <p style={{ fontSize: 11, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
              Masukkan Kode dari Bot
            </p>
            <div style={{ display: 'flex', gap: 10 }}>
              <input
                value={linkCode}
                onChange={e => setLinkCode(e.target.value.toUpperCase())}
                placeholder="Contoh: AB3X9Y2Z"
                maxLength={8}
                style={{ flex: 1, padding: '10px 14px', background: 'var(--bg-panel)', border: '1.5px solid var(--border-color)', borderRadius: 10, fontSize: 15, fontWeight: 800, color: 'var(--text-primary)', letterSpacing: 4, fontFamily: 'monospace', textTransform: 'uppercase' }}
              />
              <button style={btn()} onClick={submitCode} disabled={loading || !linkCode.trim()}>
                {loading ? '...' : 'Hubungkan'}
              </button>
            </div>
            {tgMsg && (
              <p style={{ fontSize: 12, marginTop: 10, color: tgMsg.includes('berhasil') ? '#22c55e' : '#ef4444', fontWeight: 600 }}>
                {tgMsg}
              </p>
            )}
          </div>
        </>
      )}
    </div>
  );
}

/* ─── Main Component ─────────────────────────────────────────── */
export default function ProfileView() {
  const { user, token, logout, saveSession } = useAuth();
  const [billing, setBilling] = useState(null);
  const [tab, setTab] = useState('profile');
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [error, setError] = useState('');
  const [showPass, setShowPass] = useState({ old: false, new: false, confirm: false });
  const [copied, setCopied] = useState(false);
  const [notifPrefs, setNotifPrefs] = useState({ signals: true, news: true, billing: true });
  const [avatarPickerOpen, setAvatarPickerOpen] = useState(false);
  const [pendingAvatar, setPendingAvatar] = useState(null);
  const [tgStatus, setTgStatus] = useState(null);   // null | 'linked' | 'linking'
  const [tgLinkUrl, setTgLinkUrl] = useState('');
  const [tgMsg, setTgMsg] = useState('');

  const [profileForm, setProfileForm] = useState({
    full_name: user?.full_name || '',
    email: user?.email || '',
  });
  const [passForm, setPassForm] = useState({ old_password: '', new_password: '', confirm: '' });

  useEffect(() => {
    if (!user?.id) return;
    axios.get('/web/api/v1/billing/status', { headers: { Authorization: `Bearer ${token}` } })
      .then(r => setBilling(r.data))
      .catch(() => {});
  }, [user?.id, token]);

  const currentAvatarUrl = pendingAvatar || user?.avatar_url || null;

  const initials = user?.full_name
    ? user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
    : user?.username?.slice(0, 2).toUpperCase() || 'GA';

  const tierKey = billing?.tier || 'free';
  const meta = TIER_META[tierKey] || TIER_META.free;
  const TierIcon = TIER_ICON[tierKey] || Star;
  const lvl = billing?.level || 1;
  const badge = LEVEL_BADGES.find(b => b.level === lvl) || LEVEL_BADGES[0];
  const xp = billing?.xp || 0;
  const xpProgress = billing?.xp_progress ?? (xp % 100);
  const xpNeeded = billing?.xp_needed ?? 100;
  const xpPct = xpNeeded > 0 ? Math.min(100, Math.round((xpProgress / xpNeeded) * 100)) : 0;

  const saveProfile = async () => {
    setSaving(true); setError(''); setSaved(false);
    try {
      const payload = { ...profileForm };
      if (pendingAvatar) payload.avatar_url = pendingAvatar;
      const res = await axios.patch('/auth/v1/auth/profile', payload, {
        headers: { Authorization: `Bearer ${token}` }
      });
      saveSession(token, { ...user, ...res.data, ...(pendingAvatar ? { avatar_url: pendingAvatar } : {}) });
      setPendingAvatar(null);
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Gagal menyimpan profil.');
    } finally { setSaving(false); }
  };

  const changePassword = async () => {
    setError('');
    if (passForm.new_password !== passForm.confirm) { setError('Password baru tidak cocok.'); return; }
    if (passForm.new_password.length < 8) { setError('Password minimal 8 karakter.'); return; }
    setSaving(true);
    try {
      await axios.post('/auth/v1/auth/change-password', {
        old_password: passForm.old_password,
        new_password: passForm.new_password,
      }, { headers: { Authorization: `Bearer ${token}` } });
      setPassForm({ old_password: '', new_password: '', confirm: '' });
      setSaved(true);
      setTimeout(() => setSaved(false), 2500);
    } catch (e) {
      setError(e?.response?.data?.detail || 'Gagal mengubah password.');
    } finally { setSaving(false); }
  };

  const copyReferral = () => {
    navigator.clipboard.writeText(`https://gasstrategyai.xyz/ref/${user?.username || user?.id}`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const TABS = [
    { id: 'profile',       label: '👤 Profil' },
    { id: 'security',      label: '🔒 Keamanan' },
    { id: 'plan',          label: '⚡ Plan & XP' },
    { id: 'notifications', label: '🔔 Notifikasi' },
    { id: 'referral',      label: '🎁 Referral' },
    { id: 'telegram',      label: '✈️ Telegram Bot' },
  ];

  return (
    <div style={{ padding: '24px 24px 80px', maxWidth: 860, margin: '0 auto' }}>
      <style>{`
        @keyframes pulse-gold { 0%,100%{box-shadow:0 0 20px rgba(250,204,21,0.3)} 50%{box-shadow:0 0 36px rgba(250,204,21,0.6)} }
        .profile-input {
          width: 100%; background: var(--bg-panel); border: 1.5px solid var(--border-color);
          border-radius: 10px; padding: 10px 14px; font-size: 13px; color: var(--text-primary);
          outline: none; transition: border-color 0.2s; box-sizing: border-box;
        }
        .profile-input:focus { border-color: var(--accent); }
        .profile-input::placeholder { color: var(--text-dim); }
        .profile-input:disabled { opacity: 0.5; cursor: not-allowed; }
      `}</style>

      {/* Avatar Picker Modal */}
      {avatarPickerOpen && (
        <AvatarPicker
          currentUrl={currentAvatarUrl}
          onSelect={url => { setPendingAvatar(url); setAvatarPickerOpen(false); }}
          onClose={() => setAvatarPickerOpen(false)}
        />
      )}

      {/* ── Header Card ────────────────────────────────────────── */}
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 20, marginBottom: 20, overflow: 'hidden', position: 'relative' }}>

        {/* Banner / Cover */}
        <div style={{
          height: 100,
          background: 'linear-gradient(135deg, #0a0a0a 0%, #1a1200 40%, #0d0b00 60%, #111 100%)',
          position: 'relative', overflow: 'hidden',
        }}>
          <div style={{ position: 'absolute', top: '-30%', left: '10%', width: 200, height: 200, borderRadius: '50%', background: 'rgba(250,204,21,0.08)', filter: 'blur(50px)' }} />
          <div style={{ position: 'absolute', top: '10%', right: '5%', width: 150, height: 150, borderRadius: '50%', background: `${meta.bg}`, filter: 'blur(40px)' }} />
          {/* Tier badge on banner */}
          <div style={{ position: 'absolute', top: 12, right: 16, display: 'flex', alignItems: 'center', gap: 6, background: `${meta.bg}`, border: `1px solid ${meta.border}`, borderRadius: 20, padding: '4px 10px' }}>
            <TierIcon size={11} style={{ color: meta.color }} />
            <span style={{ fontSize: 10, fontWeight: 900, color: meta.color, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{meta.label}</span>
          </div>
        </div>

        {/* Avatar + Info row */}
        <div style={{ padding: '0 24px 24px', display: 'flex', flexWrap: 'wrap', alignItems: 'flex-end', gap: 16 }}>
          {/* Avatar (overlaps banner) */}
          <div style={{ marginTop: -44, position: 'relative' }}>
            <div style={{
              width: 88, height: 88, borderRadius: 20, overflow: 'hidden',
              border: '3px solid var(--bg-card)',
              background: 'linear-gradient(135deg,#facc15,#f59e0b)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 28, fontWeight: 900, color: '#000', fontFamily: MONO,
              boxShadow: currentAvatarUrl ? '0 0 24px rgba(250,204,21,0.3)' : '0 8px 24px rgba(0,0,0,0.4)',
            }}>
              {currentAvatarUrl
                ? <img src={currentAvatarUrl} alt="avatar" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                : initials
              }
            </div>
            {/* Edit badge */}
            <button onClick={() => setAvatarPickerOpen(true)} style={{
              position: 'absolute', bottom: -4, right: -4,
              width: 26, height: 26, borderRadius: '50%',
              background: '#facc15', border: '2px solid var(--bg-card)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              cursor: 'pointer', boxShadow: '0 2px 8px rgba(250,204,21,0.4)',
            }} title="Ganti avatar">
              <Sparkles size={11} style={{ color: '#000' }} />
            </button>
          </div>

          {/* Name + meta */}
          <div style={{ flex: 1, minWidth: 200, paddingTop: 12 }}>
            <div style={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8, marginBottom: 2 }}>
              <h1 style={{ fontSize: 20, fontWeight: 900, color: 'var(--text-primary)' }}>{user?.full_name || user?.username}</h1>
              {user?.role === 'admin' && (
                <span style={{ fontSize: 9, fontWeight: 900, padding: '2px 8px', borderRadius: 20, background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)', color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Admin</span>
              )}
            </div>
            <p style={{ fontSize: 12, color: 'var(--text-dim)', marginBottom: 10 }}>@{user?.username} · {user?.email}</p>

            {/* XP Bar */}
            {billing && (
              <div style={{ maxWidth: 280 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, fontWeight: 700, color: 'var(--text-dim)', marginBottom: 4 }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                    <span>{badge.emoji}</span>
                    <span style={{ color: badge.color }}>{badge.label}</span>
                    <span>· Lv.{lvl}</span>
                  </span>
                  <span>{xp} XP</span>
                </div>
                <div style={{ height: 6, background: 'var(--bg-panel)', borderRadius: 3, overflow: 'hidden' }}>
                  <div style={{ height: '100%', width: `${xpPct}%`, background: `linear-gradient(90deg, ${badge.color}, #facc15)`, borderRadius: 3, transition: 'width 1s' }} />
                </div>
              </div>
            )}
          </div>

          {/* Stats */}
          <div style={{ display: 'flex', gap: 24, paddingTop: 12 }}>
            {[
              { label: 'Kredit', value: billing ? `${billing.credits ?? billing.quota ?? 0}` : '—', color: '#facc15' },
              { label: 'Booster', value: billing ? `${billing.boost ?? 0}` : '—', color: '#34d399' },
              { label: 'Level', value: `${lvl}`, color: badge.color },
            ].map((s, i) => (
              <div key={i} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 22, fontWeight: 900, fontFamily: MONO, color: s.color }}>{s.value}</div>
                <div style={{ fontSize: 9, fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginTop: 2 }}>{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Tabs ──────────────────────────────────────────────── */}
      <div style={{ display: 'flex', gap: 4, background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 14, padding: 4, marginBottom: 20, overflowX: 'auto' }}>
        {TABS.map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); setError(''); setSaved(false); }} style={{
            padding: '8px 14px', borderRadius: 10, fontSize: 12, fontWeight: 800, whiteSpace: 'nowrap', cursor: 'pointer', border: 'none', transition: 'all 0.15s',
            background: tab === t.id ? 'var(--accent)' : 'transparent',
            color: tab === t.id ? '#000' : 'var(--text-dim)',
            boxShadow: tab === t.id ? '0 2px 12px rgba(250,204,21,0.3)' : 'none',
          }}>{t.label}</button>
        ))}
      </div>

      {/* ── Tab Content ───────────────────────────────────────── */}
      <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: 20, padding: '24px' }}>

        {/* Feedback banners */}
        {error && (
          <div style={{ background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)', borderRadius: 10, padding: '10px 14px', fontSize: 12, color: '#f87171', marginBottom: 16 }}>{error}</div>
        )}
        {saved && (
          <div style={{ background: 'rgba(52,211,153,0.08)', border: '1px solid rgba(52,211,153,0.2)', borderRadius: 10, padding: '10px 14px', fontSize: 12, color: '#34d399', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Check size={13} /> Perubahan berhasil disimpan!
          </div>
        )}
        {pendingAvatar && tab === 'profile' && (
          <div style={{ background: 'rgba(250,204,21,0.08)', border: '1px solid rgba(250,204,21,0.2)', borderRadius: 10, padding: '10px 14px', fontSize: 12, color: '#facc15', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
            <Sparkles size={13} /> Avatar baru dipilih — klik <strong>Simpan Profil</strong> untuk menyimpan.
          </div>
        )}

        {/* ── PROFILE TAB ── */}
        {tab === 'profile' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>

            {/* Avatar Picker Section */}
            <div>
              <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>Foto Profil</p>
              <div style={{ display: 'flex', alignItems: 'center', gap: 16, background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 14, padding: '16px' }}>
                {/* Current avatar preview */}
                <div style={{ width: 64, height: 64, borderRadius: 14, overflow: 'hidden', background: 'linear-gradient(135deg,#facc15,#f59e0b)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 20, fontWeight: 900, color: '#000', flexShrink: 0, border: '2px solid var(--border-color)' }}>
                  {currentAvatarUrl
                    ? <img src={currentAvatarUrl} alt="preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    : <span style={{ fontFamily: MONO }}>{initials}</span>
                  }
                </div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', marginBottom: 3 }}>Avatar Generatif</p>
                  <p style={{ fontSize: 11, color: 'var(--text-dim)', lineHeight: 1.5 }}>Pilih dari 18 avatar unik bergaya Ethereum · NFT · Pixel Art. Gratis & tidak perlu upload foto.</p>
                </div>
                <button onClick={() => setAvatarPickerOpen(true)} style={{
                  padding: '9px 18px', background: '#facc15', color: '#000', border: 'none',
                  borderRadius: 10, fontSize: 12, fontWeight: 900, cursor: 'pointer',
                  boxShadow: '0 4px 14px rgba(250,204,21,0.3)', whiteSpace: 'nowrap', flexShrink: 0,
                }}>
                  ✨ Pilih Avatar
                </button>
              </div>
            </div>

            {/* Info fields */}
            <div>
              <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>Informasi Akun</p>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(200px,1fr))', gap: 14 }}>
                {[
                  { label: 'Nama Lengkap', key: 'full_name', type: 'text', placeholder: 'John Doe' },
                  { label: 'Email', key: 'email', type: 'email', placeholder: 'john@email.com' },
                ].map(f => (
                  <div key={f.key}>
                    <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>{f.label}</label>
                    <input className="profile-input" type={f.type} value={profileForm[f.key]}
                      onChange={e => setProfileForm(p => ({ ...p, [f.key]: e.target.value }))}
                      placeholder={f.placeholder} />
                  </div>
                ))}
                <div>
                  <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Username</label>
                  <input className="profile-input" disabled value={`@${user?.username || ''}`} />
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>Role</label>
                  <input className="profile-input" disabled value={user?.role?.toUpperCase() || 'USER'} />
                </div>
              </div>
            </div>

            {/* User ID */}
            <div>
              <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>User ID · EA Config Key</label>
              <div style={{ position: 'relative' }}>
                <input className="profile-input" disabled value={user?.id || ''} style={{ paddingRight: 42, fontFamily: MONO, color: 'var(--accent)', opacity: 0.85 }} />
                <button onClick={() => { navigator.clipboard.writeText(user?.id || ''); setSaved(true); setTimeout(() => setSaved(false), 1500); }}
                  style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', padding: 0 }}>
                  <Copy size={13} />
                </button>
              </div>
            </div>

            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button onClick={saveProfile} disabled={saving} style={{
                padding: '11px 28px', background: '#facc15', color: '#000', border: 'none',
                borderRadius: 12, fontSize: 14, fontWeight: 900, cursor: saving ? 'not-allowed' : 'pointer',
                opacity: saving ? 0.6 : 1, boxShadow: '0 4px 18px rgba(250,204,21,0.35)',
                display: 'flex', alignItems: 'center', gap: 8,
              }}>
                {saving ? <RefreshCw size={14} style={{ animation: 'spin 1s linear infinite' }} /> : <Check size={14} />}
                {saving ? 'Menyimpan...' : 'Simpan Profil'}
              </button>
            </div>

            {/* Danger zone */}
            <div style={{ paddingTop: 20, borderTop: '1px solid var(--border-color)' }}>
              <p style={{ fontSize: 10, fontWeight: 800, color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>Danger Zone</p>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
                <button onClick={logout} style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 16px', background: 'none', border: '1px solid var(--border-color)', borderRadius: 10, fontSize: 12, fontWeight: 800, color: 'var(--text-dim)', cursor: 'pointer' }}>
                  <LogOut size={13} /> Sign Out
                </button>
                <button style={{ display: 'flex', alignItems: 'center', gap: 8, padding: '9px 16px', background: 'none', border: '1px solid rgba(239,68,68,0.25)', borderRadius: 10, fontSize: 12, fontWeight: 800, color: '#f87171', cursor: 'pointer' }}>
                  <Trash2 size={13} /> Hapus Akun
                </button>
              </div>
            </div>
          </div>
        )}

        {/* ── SECURITY TAB ── */}
        {tab === 'security' && (
          <div style={{ maxWidth: 440, display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div>
              <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>Ganti Password</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {[
                  { label: 'Password Lama', key: 'old_password', show: 'old' },
                  { label: 'Password Baru', key: 'new_password', show: 'new' },
                  { label: 'Konfirmasi Password Baru', key: 'confirm', show: 'confirm' },
                ].map(f => (
                  <div key={f.key}>
                    <label style={{ display: 'block', fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 6 }}>{f.label}</label>
                    <div style={{ position: 'relative' }}>
                      <input className="profile-input" type={showPass[f.show] ? 'text' : 'password'}
                        value={passForm[f.key]}
                        onChange={e => setPassForm(p => ({ ...p, [f.key]: e.target.value }))}
                        placeholder="••••••••" style={{ paddingRight: 42 }} />
                      <button type="button" onClick={() => setShowPass(p => ({ ...p, [f.show]: !p[f.show] }))}
                        style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', color: 'var(--text-dim)', padding: 0 }}>
                        {showPass[f.show] ? <EyeOff size={14} /> : <Eye size={14} />}
                      </button>
                    </div>
                  </div>
                ))}
              </div>
              <button onClick={changePassword} disabled={saving} style={{
                marginTop: 16, width: '100%', padding: '11px', background: '#facc15', color: '#000', border: 'none',
                borderRadius: 12, fontSize: 14, fontWeight: 900, cursor: saving ? 'not-allowed' : 'pointer',
                opacity: saving ? 0.6 : 1, display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
              }}>
                {saving ? <RefreshCw size={14} /> : <Lock size={14} />}
                {saving ? 'Menyimpan...' : 'Ubah Password'}
              </button>
            </div>

            <div style={{ borderTop: '1px solid var(--border-color)', paddingTop: 20 }}>
              <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>Sesi Aktif</p>
              <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 12, padding: '14px 16px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 8, height: 8, borderRadius: '50%', background: '#34d399', boxShadow: '0 0 6px #34d399' }} />
                  <div>
                    <p style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)' }}>Perangkat Ini · Browser</p>
                    <p style={{ fontSize: 10, color: 'var(--text-dim)' }}>Login aktif sekarang</p>
                  </div>
                </div>
                <span style={{ fontSize: 9, fontWeight: 900, color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Aktif</span>
              </div>
            </div>
          </div>
        )}

        {/* ── PLAN TAB ── */}
        {tab === 'plan' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {billing ? (
              <>
                {/* Active plan card */}
                <div style={{ borderRadius: 16, padding: 20, border: `2px solid ${meta.border}`, background: meta.bg, display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ width: 52, height: 52, borderRadius: 14, background: meta.bg, border: `1px solid ${meta.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <TierIcon size={22} style={{ color: meta.color }} />
                    </div>
                    <div>
                      <p style={{ fontSize: 18, fontWeight: 900, color: meta.color, fontFamily: MONO }}>{meta.label} Plan</p>
                      <p style={{ fontSize: 11, color: 'var(--text-dim)' }}>Level {lvl} · {xp} XP total</p>
                    </div>
                  </div>
                  <button onClick={() => window.location.hash = '#pricing'} style={{
                    padding: '9px 20px', background: '#facc15', color: '#000', border: 'none',
                    borderRadius: 10, fontSize: 12, fontWeight: 900, cursor: 'pointer',
                  }}>Upgrade ↗</button>
                </div>

                {/* Stats grid */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(160px,1fr))', gap: 14 }}>
                  <StatCard label="Kredit Tersisa" value={`${billing.credits ?? billing.quota ?? 0}`} sub="Saldo kredit aktif" accent="#facc15" />
                  <StatCard label="Booster Pack" value={`${billing.boost ?? 0}`} sub="Analisa tambahan" accent="#34d399" />
                  <StatCard label="Level" value={`${lvl}`} sub={badge.label} accent={badge.color} />
                </div>

                {/* XP Progress */}
                <div>
                  <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 14 }}>Level & XP Progress</p>
                  <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 14, padding: 20 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 16 }}>
                      <div style={{ width: 52, height: 52, borderRadius: 14, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24, background: badge.glow, boxShadow: `0 0 20px ${badge.glow}` }}>
                        {badge.emoji}
                      </div>
                      <div>
                        <p style={{ fontWeight: 900, fontSize: 15, color: badge.color, fontFamily: MONO }}>Level {lvl} — {badge.label}</p>
                        <p style={{ fontSize: 11, color: 'var(--text-dim)' }}>{xp} XP · {billing.xp_to_next ?? (xpNeeded - xpProgress)} XP lagi ke Level {lvl + 1}</p>
                      </div>
                    </div>
                    <div style={{ height: 10, background: 'var(--bg-hover)', borderRadius: 5, overflow: 'hidden', marginBottom: 16 }}>
                      <div style={{ height: '100%', width: `${xpPct}%`, background: `linear-gradient(90deg,${badge.color},#facc15)`, borderRadius: 5, transition: 'width 1s' }} />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2,1fr)', gap: 8 }}>
                      {[
                        { label: 'Analisa Market', xp: '+1 XP' },
                        { label: 'Signal Profit', xp: '+5 XP' },
                        { label: 'Referral Teman', xp: '+10 XP' },
                        { label: 'Daily Login', xp: '+1 XP' },
                      ].map((item, i) => (
                        <div key={i} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '8px 12px', background: 'var(--bg-hover)', borderRadius: 8 }}>
                          <span style={{ fontSize: 11, color: 'var(--text-dim)' }}>{item.label}</span>
                          <span style={{ fontSize: 11, fontWeight: 900, color: '#facc15', fontFamily: MONO }}>{item.xp}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              </>
            ) : (
              <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-dim)' }}>
                <Zap size={36} style={{ margin: '0 auto 12px', opacity: 0.3 }} />
                <p style={{ fontSize: 13 }}>Memuat data billing...</p>
              </div>
            )}
          </div>
        )}

        {/* ── NOTIFICATIONS TAB ── */}
        {tab === 'notifications' && (
          <div style={{ maxWidth: 480, display: 'flex', flexDirection: 'column', gap: 20 }}>
            <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>Preferensi Notifikasi</p>
            {[
              { key: 'signals', label: 'Signal AI Baru', sub: 'Notifikasi saat signal baru masuk', icon: '⚡' },
              { key: 'news', label: 'Breaking News Market', sub: 'Berita berdampak tinggi dari kalender ekonomi', icon: '📰' },
              { key: 'billing', label: 'Info Billing & Kredit', sub: 'Peringatan saat kredit atau booster hampir habis', icon: '💳' },
            ].map(item => (
              <div key={item.key} style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 12, padding: '14px 16px', display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(250,204,21,0.08)', border: '1px solid rgba(250,204,21,0.15)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 16, flexShrink: 0 }}>{item.icon}</div>
                <div style={{ flex: 1 }}>
                  <p style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{item.label}</p>
                  <p style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 2 }}>{item.sub}</p>
                </div>
                <Toggle checked={notifPrefs[item.key]} onChange={() => setNotifPrefs(p => ({ ...p, [item.key]: !p[item.key] }))} />
              </div>
            ))}
            <button style={{ padding: '11px', background: '#facc15', color: '#000', border: 'none', borderRadius: 12, fontSize: 14, fontWeight: 900, cursor: 'pointer', boxShadow: '0 4px 14px rgba(250,204,21,0.3)' }}>
              Simpan Preferensi
            </button>
          </div>
        )}

        {/* ── TELEGRAM BOT TAB ── */}
        {tab === 'telegram' && (
          <TelegramLinkTab token={token} tgStatus={tgStatus} setTgStatus={setTgStatus}
                           tgLinkUrl={tgLinkUrl} setTgLinkUrl={setTgLinkUrl}
                           tgMsg={tgMsg} setTgMsg={setTgMsg} />
        )}

        {/* ── REFERRAL TAB ── */}
        {tab === 'referral' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            {/* Banner */}
            <div style={{ background: 'linear-gradient(135deg,rgba(250,204,21,0.08),transparent)', border: '1px solid rgba(250,204,21,0.2)', borderRadius: 16, padding: '28px 24px', textAlign: 'center' }}>
              <div style={{ fontSize: 40, marginBottom: 12 }}>🎁</div>
              <h3 style={{ fontSize: 20, fontWeight: 900, color: 'var(--text-primary)', marginBottom: 6 }}>
                Undang Teman, Dapat <span style={{ color: '#facc15' }}>+10 XP</span>
              </h3>
              <p style={{ fontSize: 13, color: 'var(--text-dim)', marginBottom: 20, lineHeight: 1.6 }}>
                Setiap teman yang mendaftar via link kamu, kamu dapat 10 XP bonus langsung.
              </p>
              <div style={{ background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 12, display: 'flex', alignItems: 'center', gap: 10, padding: '12px 14px', maxWidth: 420, margin: '0 auto' }}>
                <code style={{ flex: 1, fontSize: 11, color: 'var(--text-secondary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontFamily: MONO }}>
                  gasstrategyai.xyz/ref/{user?.username || user?.id?.slice(0, 8)}
                </code>
                <button onClick={copyReferral} style={{
                  padding: '6px 14px', background: '#facc15', color: '#000', border: 'none',
                  borderRadius: 8, fontSize: 11, fontWeight: 900, cursor: 'pointer', flexShrink: 0,
                  display: 'flex', alignItems: 'center', gap: 6,
                }}>
                  {copied ? <Check size={12} /> : <Copy size={12} />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
            </div>

            {/* Milestones */}
            <div>
              <p style={{ fontSize: 10, fontWeight: 800, color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>Reward Referral</p>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {[
                  { milestone: '1 teman',   reward: '+10 XP bonus',             icon: '🏅' },
                  { milestone: '5 teman',   reward: '1 Booster Pack Gratis',     icon: '🎯' },
                  { milestone: '10 teman',  reward: '1 Bulan Premium Gratis',    icon: '👑' },
                ].map((r, i) => (
                  <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 14, padding: '14px 16px', background: 'var(--bg-panel)', border: '1px solid var(--border-color)', borderRadius: 12, opacity: 0.6 }}>
                    <span style={{ fontSize: 20 }}>{r.icon}</span>
                    <div style={{ flex: 1 }}>
                      <p style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)' }}>{r.milestone}</p>
                      <p style={{ fontSize: 11, color: 'var(--text-dim)' }}>{r.reward}</p>
                    </div>
                    <Lock size={12} style={{ color: 'var(--text-dim)' }} />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
