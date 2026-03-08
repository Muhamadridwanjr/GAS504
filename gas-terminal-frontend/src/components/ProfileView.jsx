import React, { useState, useEffect, useRef } from 'react';
import {
    User, Mail, Lock, Shield, Zap, Trophy, Star,
    Camera, Check, Eye, EyeOff, Copy, Crown,
    LogOut, Trash2, ChevronRight, Clock, TrendingUp, Award
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';

const TIER_META = {
    free:      { label: 'Free',      color: 'text-gray-400',  bg: 'bg-gray-400/10',  border: 'border-gray-400/20' },
    essential: { label: 'Essential', color: 'text-blue-400',  bg: 'bg-blue-400/10',  border: 'border-blue-400/20' },
    plus:      { label: 'Plus',      color: 'text-purple-400',bg: 'bg-purple-400/10',border: 'border-purple-400/20' },
    premium:   { label: 'Premium',   color: 'text-yellow-400',bg: 'bg-yellow-400/10',border: 'border-yellow-400/20' },
    ultimate:  { label: 'Ultimate',  color: 'text-orange-400',bg: 'bg-orange-400/10',border: 'border-orange-400/20' },
};

const TIER_ICON = { free: Star, essential: Zap, plus: Crown, premium: Trophy, ultimate: Award };

function StatCard({ label, value, sub, color = '' }) {
    return (
        <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-4">
            <p className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-2">{label}</p>
            <p className={`text-2xl font-black font-mono ${color || 'text-[var(--text-primary)]'}`}>{value}</p>
            {sub && <p className="text-[10px] text-[var(--text-dim)] mt-1">{sub}</p>}
        </div>
    );
}

function Toggle({ label, checked, onChange }) {
    return (
        <label className="flex items-center justify-between cursor-pointer group">
            <span className="text-sm font-medium text-[var(--text-secondary)] group-hover:text-[var(--text-primary)] transition-colors">{label}</span>
            <div onClick={onChange} className={`w-10 h-5 rounded-full relative transition-colors ${checked ? 'bg-[var(--accent)]' : 'bg-[var(--bg-hover)] border border-[var(--border-color)]'}`}>
                <div className={`absolute top-1 w-3 h-3 rounded-full bg-white transition-all shadow ${checked ? 'left-6' : 'left-1'}`} />
            </div>
        </label>
    );
}

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

    const [profileForm, setProfileForm] = useState({
        full_name: user?.full_name || '',
        email: user?.email || '',
    });
    const [passForm, setPassForm] = useState({ old_password: '', new_password: '', confirm: '' });

    useEffect(() => {
        if (!user?.id) return;
        fetch(`/billing-api/api/v1/billing/status/${user.id}`)
            .then(r => r.json())
            .then(setBilling)
            .catch(() => {});
    }, [user?.id]);

    const saveProfile = async () => {
        setSaving(true); setError(''); setSaved(false);
        try {
            const res = await axios.patch('/auth/v1/auth/profile', profileForm, {
                headers: { Authorization: `Bearer ${token}` }
            });
            saveSession(token, { ...user, ...res.data });
            setSaved(true);
            setTimeout(() => setSaved(false), 2000);
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
            setTimeout(() => setSaved(false), 2000);
        } catch (e) {
            setError(e?.response?.data?.detail || 'Gagal mengubah password.');
        } finally { setSaving(false); }
    };

    const copyReferral = () => {
        navigator.clipboard.writeText(`https://gasstrategy.io/ref/${user?.username || user?.id}`);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    const tierKey = billing?.tier || 'free';
    const meta = TIER_META[tierKey] || TIER_META.free;
    const TierIcon = TIER_ICON[tierKey] || Star;

    const initials = user?.full_name
        ? user.full_name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
        : user?.username?.slice(0, 2).toUpperCase() || 'GA';

    const joinDate = user?.id
        ? 'Mar 2026'
        : '—';

    const xpProgress = billing ? (billing.level_score % 100) : 0;
    const xpToNext = 100 - xpProgress;

    const TABS = [
        { id: 'profile', label: 'Profil' },
        { id: 'security', label: 'Keamanan' },
        { id: 'plan', label: 'Plan & Usage' },
        { id: 'notifications', label: 'Notifikasi' },
        { id: 'referral', label: 'Referral' },
    ];

    return (
        <div className="p-4 md:p-8 max-w-4xl mx-auto pb-24 md:pb-8">

            {/* ── Header Card ── */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 mb-6 relative overflow-hidden">
                <div className="absolute top-0 right-0 w-64 h-64 bg-[var(--accent)]/3 blur-[80px] rounded-full pointer-events-none" />
                <div className="relative z-10 flex flex-col sm:flex-row items-start sm:items-center gap-5">
                    {/* Avatar */}
                    <div className="relative shrink-0">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-yellow-400 to-yellow-600 flex items-center justify-center text-black font-black text-2xl font-display shadow-[0_8px_24px_rgba(250,204,21,0.3)]">
                            {user?.avatar_url
                                ? <img src={user.avatar_url} alt="avatar" className="w-full h-full rounded-2xl object-cover" />
                                : initials
                            }
                        </div>
                        <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-[var(--bg-card)] rounded-full flex items-center justify-center border border-[var(--border-color)] cursor-pointer hover:bg-[var(--bg-hover)]">
                            <Camera size={11} className="text-[var(--text-dim)]" />
                        </div>
                    </div>

                    {/* Info */}
                    <div className="flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                            <h1 className="text-xl font-black font-display truncate">{user?.full_name || user?.username}</h1>
                            <span className={`text-[9px] font-black px-2 py-0.5 rounded-full border ${meta.bg} ${meta.color} ${meta.border} uppercase tracking-widest`}>
                                {meta.label}
                            </span>
                            {user?.role === 'admin' && (
                                <span className="text-[9px] font-black px-2 py-0.5 rounded-full border bg-red-400/10 text-red-400 border-red-400/20 uppercase tracking-widest">Admin</span>
                            )}
                        </div>
                        <p className="text-sm text-[var(--text-dim)] mb-3">@{user?.username} · {user?.email}</p>

                        {/* XP Bar */}
                        {billing && (
                            <div className="max-w-xs">
                                <div className="flex items-center justify-between text-[10px] font-bold text-[var(--text-dim)] mb-1">
                                    <span className="flex items-center gap-1"><Trophy size={10} className="text-yellow-400" /> Level {billing.level}</span>
                                    <span>{billing.level_score} XP · +{xpToNext} ke level {billing.level + 1}</span>
                                </div>
                                <div className="h-1.5 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                                    <div className="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 transition-all duration-1000 rounded-full" style={{ width: `${xpProgress}%` }} />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Stats */}
                    <div className="flex gap-4 sm:gap-6 shrink-0">
                        {[
                            { label: 'Bergabung', value: joinDate },
                            { label: 'Quota', value: billing ? `${billing.quota}` : '—' },
                            { label: 'Booster', value: billing ? `${billing.boost}` : '—' },
                        ].map((s, i) => (
                            <div key={i} className="text-center">
                                <p className="text-lg font-black font-mono text-[var(--accent)]">{s.value}</p>
                                <p className="text-[9px] font-bold text-[var(--text-dim)] uppercase tracking-wide">{s.label}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* ── Tabs ── */}
            <div className="flex gap-1 overflow-x-auto scrollbar-none bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1 mb-6">
                {TABS.map(t => (
                    <button key={t.id} onClick={() => { setTab(t.id); setError(''); setSaved(false); }}
                        className={`px-4 py-2 rounded-lg text-xs font-black whitespace-nowrap transition-all ${tab === t.id ? 'bg-[var(--accent)] text-black shadow' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                        {t.label}
                    </button>
                ))}
            </div>

            {/* ── Tab Content ── */}
            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6">

                {/* Feedback */}
                {error && <p className="text-[11px] text-[var(--danger)] bg-[var(--danger)]/10 border border-[var(--danger)]/20 rounded-lg px-3 py-2 mb-4">{error}</p>}
                {saved && <p className="text-[11px] text-[var(--success)] bg-[var(--success)]/10 border border-[var(--success)]/20 rounded-lg px-3 py-2 mb-4 flex items-center gap-2"><Check size={12} /> Perubahan disimpan!</p>}

                {/* ── PROFILE TAB ── */}
                {tab === 'profile' && (
                    <div className="space-y-6">
                        <div>
                            <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Informasi Akun</h3>
                            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                                {[
                                    { label: 'Nama Lengkap', key: 'full_name', type: 'text', placeholder: 'John Doe' },
                                    { label: 'Email', key: 'email', type: 'email', placeholder: 'john@email.com' },
                                ].map(f => (
                                    <div key={f.key}>
                                        <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1.5 block">{f.label}</label>
                                        <input type={f.type} value={profileForm[f.key]}
                                            onChange={e => setProfileForm(p => ({ ...p, [f.key]: e.target.value }))}
                                            placeholder={f.placeholder}
                                            className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors" />
                                    </div>
                                ))}
                                <div>
                                    <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1.5 block">Username</label>
                                    <input disabled value={`@${user?.username || ''}`}
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-dim)] opacity-60 cursor-not-allowed" />
                                </div>
                                <div>
                                    <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1.5 block">Role</label>
                                    <input disabled value={user?.role?.toUpperCase() || 'USER'}
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-dim)] opacity-60 cursor-not-allowed" />
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-end">
                            <button onClick={saveProfile} disabled={saving}
                                className="px-6 py-2.5 bg-[var(--accent)] text-black font-black text-sm rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center gap-2">
                                {saving ? <div className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <Check size={14} />}
                                {saving ? 'Menyimpan...' : 'Simpan Profil'}
                            </button>
                        </div>

                        {/* Danger zone */}
                        <div className="pt-4 border-t border-[var(--border-color)]">
                            <h3 className="text-sm font-black uppercase tracking-widest text-[var(--danger)] mb-3">Danger Zone</h3>
                            <div className="flex flex-col sm:flex-row gap-3">
                                <button onClick={logout}
                                    className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[var(--border-color)] text-xs font-black text-[var(--text-dim)] hover:text-[var(--danger)] hover:border-[var(--danger)]/30 transition-all">
                                    <LogOut size={13} /> Sign Out dari Semua Perangkat
                                </button>
                                <button className="flex items-center gap-2 px-4 py-2.5 rounded-xl border border-[var(--danger)]/20 text-xs font-black text-[var(--danger)] hover:bg-[var(--danger)]/5 transition-all">
                                    <Trash2 size={13} /> Hapus Akun
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* ── SECURITY TAB ── */}
                {tab === 'security' && (
                    <div className="space-y-6 max-w-md">
                        <div>
                            <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Ganti Password</h3>
                            <div className="space-y-3">
                                {[
                                    { label: 'Password Lama', key: 'old_password', show: 'old' },
                                    { label: 'Password Baru', key: 'new_password', show: 'new' },
                                    { label: 'Konfirmasi Password Baru', key: 'confirm', show: 'confirm' },
                                ].map(f => (
                                    <div key={f.key}>
                                        <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1.5 block">{f.label}</label>
                                        <div className="relative">
                                            <input type={showPass[f.show] ? 'text' : 'password'}
                                                value={passForm[f.key]}
                                                onChange={e => setPassForm(p => ({ ...p, [f.key]: e.target.value }))}
                                                placeholder="••••••••" minLength={f.key !== 'old_password' ? 8 : undefined}
                                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 pr-10 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors" />
                                            <button type="button" onClick={() => setShowPass(p => ({ ...p, [f.show]: !p[f.show] }))}
                                                className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-dim)] hover:text-[var(--text-primary)]">
                                                {showPass[f.show] ? <EyeOff size={13} /> : <Eye size={13} />}
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <button onClick={changePassword} disabled={saving}
                                className="mt-4 w-full py-2.5 bg-[var(--accent)] text-black font-black text-sm rounded-xl hover:opacity-90 disabled:opacity-50 flex items-center justify-center gap-2">
                                {saving ? <div className="w-3.5 h-3.5 border-2 border-black/30 border-t-black rounded-full animate-spin" /> : <Lock size={14} />}
                                {saving ? 'Menyimpan...' : 'Ubah Password'}
                            </button>
                        </div>

                        <div className="border-t border-[var(--border-color)] pt-5">
                            <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">Sesi Aktif</h3>
                            <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-4 flex items-center justify-between">
                                <div className="flex items-center gap-3">
                                    <div className="w-2.5 h-2.5 rounded-full bg-[var(--success)] animate-pulse" />
                                    <div>
                                        <p className="text-xs font-bold">Perangkat Ini · Browser</p>
                                        <p className="text-[10px] text-[var(--text-dim)]">Login aktif sekarang</p>
                                    </div>
                                </div>
                                <span className="text-[9px] font-black text-[var(--success)] uppercase">Aktif</span>
                            </div>
                        </div>
                    </div>
                )}

                {/* ── PLAN TAB ── */}
                {tab === 'plan' && (
                    <div className="space-y-6">
                        {billing ? (
                            <>
                                {/* Current Plan */}
                                <div>
                                    <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Plan Aktif</h3>
                                    <div className={`rounded-2xl p-5 border-2 ${meta.border} ${meta.bg} flex items-center justify-between`}>
                                        <div className="flex items-center gap-4">
                                            <div className={`w-12 h-12 rounded-xl ${meta.bg} border ${meta.border} flex items-center justify-center`}>
                                                <TierIcon size={22} className={meta.color} />
                                            </div>
                                            <div>
                                                <p className={`text-lg font-black ${meta.color}`}>{meta.label} Plan</p>
                                                <p className="text-xs text-[var(--text-dim)]">Level {billing.level} · {billing.level_score} XP total</p>
                                            </div>
                                        </div>
                                        <button onClick={() => window.location.hash = '#pricing'}
                                            className="text-xs font-black px-4 py-2 rounded-xl bg-[var(--accent)] text-black hover:opacity-90 transition-opacity">
                                            Upgrade
                                        </button>
                                    </div>
                                </div>

                                {/* Usage Stats */}
                                <div>
                                    <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Penggunaan Bulan Ini</h3>
                                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                                        <StatCard label="Quota Tersisa" value={`${billing.quota}`} sub="Analisa bulanan" color="text-[var(--accent)]" />
                                        <StatCard label="Booster" value={`${billing.boost}`} sub="Analisa tambahan" color="text-[var(--success)]" />
                                        <StatCard label="Digunakan Hari Ini" value={`${billing.daily_usage}`} sub="Dari limit harian" />
                                    </div>
                                    {/* Usage bar */}
                                    <div className="mt-4 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-4">
                                        <div className="flex items-center justify-between text-[10px] font-bold text-[var(--text-dim)] mb-2">
                                            <span>Daily Usage</span>
                                            <span>{billing.daily_usage} / {billing.daily_limit || 2} analisa</span>
                                        </div>
                                        <div className="h-2 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                                            <div className="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full transition-all"
                                                style={{ width: `${Math.min(100, (billing.daily_usage / (billing.daily_limit || 2)) * 100)}%` }} />
                                        </div>
                                    </div>
                                </div>

                                {/* XP Progress */}
                                <div>
                                    <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Level & XP</h3>
                                    <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-5">
                                        <div className="flex items-center gap-4 mb-4">
                                            <div className="w-12 h-12 rounded-xl bg-yellow-400 flex items-center justify-center text-black font-black text-xl">
                                                {billing.level}
                                            </div>
                                            <div>
                                                <p className="font-black">Level {billing.level}</p>
                                                <p className="text-xs text-[var(--text-dim)]">{billing.level_score} XP · +{xpToNext} XP ke level {billing.level + 1}</p>
                                            </div>
                                        </div>
                                        <div className="h-3 bg-[var(--bg-hover)] rounded-full overflow-hidden">
                                            <div className="h-full bg-gradient-to-r from-yellow-400 to-yellow-600 rounded-full transition-all" style={{ width: `${xpProgress}%` }} />
                                        </div>
                                        <div className="mt-4 grid grid-cols-2 gap-3">
                                            {[
                                                { label: 'Analisa Market', xp: '+1 XP' },
                                                { label: 'Signal Profit', xp: '+5 XP' },
                                                { label: 'Referral', xp: '+10 XP' },
                                                { label: 'Daily Login', xp: '+1 XP' },
                                            ].map((item, i) => (
                                                <div key={i} className="flex items-center justify-between p-2 rounded-lg bg-[var(--bg-hover)]">
                                                    <span className="text-[10px] text-[var(--text-dim)]">{item.label}</span>
                                                    <span className="text-[10px] font-black text-yellow-400">{item.xp}</span>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </>
                        ) : (
                            <div className="text-center py-8 text-[var(--text-dim)]">
                                <Zap size={32} className="mx-auto mb-3 opacity-30" />
                                <p className="text-sm">Memuat data billing...</p>
                            </div>
                        )}
                    </div>
                )}

                {/* ── NOTIFICATIONS TAB ── */}
                {tab === 'notifications' && (
                    <div className="space-y-5 max-w-md">
                        <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Preferensi Notifikasi</h3>
                        <div className="space-y-4">
                            {[
                                { key: 'signals', label: 'Signal AI Baru', sub: 'Notifikasi saat signal baru masuk' },
                                { key: 'news', label: 'Breaking News Market', sub: 'Berita berdampak tinggi dari calendar' },
                                { key: 'billing', label: 'Info Billing & Quota', sub: 'Peringatan saat quota hampir habis' },
                            ].map(item => (
                                <div key={item.key} className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-4">
                                    <div className="flex items-start justify-between gap-3">
                                        <div>
                                            <p className="text-sm font-bold mb-0.5">{item.label}</p>
                                            <p className="text-[10px] text-[var(--text-dim)]">{item.sub}</p>
                                        </div>
                                        <Toggle
                                            checked={notifPrefs[item.key]}
                                            onChange={() => setNotifPrefs(p => ({ ...p, [item.key]: !p[item.key] }))}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                        <button className="w-full py-2.5 bg-[var(--accent)] text-black font-black text-sm rounded-xl hover:opacity-90 transition-opacity">
                            Simpan Preferensi
                        </button>
                    </div>
                )}

                {/* ── REFERRAL TAB ── */}
                {tab === 'referral' && (
                    <div className="space-y-6">
                        <div className="bg-gradient-to-br from-yellow-400/10 to-transparent border border-yellow-400/20 rounded-2xl p-6 text-center">
                            <Trophy size={40} className="text-yellow-400 mx-auto mb-3" />
                            <h3 className="text-xl font-black font-display mb-2">Undang Teman, Dapat <span className="text-yellow-400">+10 XP</span></h3>
                            <p className="text-sm text-[var(--text-dim)] mb-5">Setiap teman yang mendaftar via link kamu, kamu dapat 10 XP bonus.</p>
                            <div className="bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl flex items-center gap-2 p-3 max-w-sm mx-auto">
                                <code className="flex-1 text-xs text-[var(--text-secondary)] truncate font-mono">
                                    gasstrategy.io/ref/{user?.username || user?.id?.slice(0, 8)}
                                </code>
                                <button onClick={copyReferral}
                                    className="shrink-0 px-3 py-1.5 bg-[var(--accent)] text-black text-[10px] font-black rounded-lg flex items-center gap-1.5 hover:opacity-90 transition-opacity">
                                    {copied ? <Check size={11} /> : <Copy size={11} />}
                                    {copied ? 'Copied!' : 'Copy'}
                                </button>
                            </div>
                        </div>

                        <div>
                            <h3 className="text-sm font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Reward Referral</h3>
                            <div className="space-y-3">
                                {[
                                    { milestone: '1 teman', reward: '+10 XP', status: 'locked' },
                                    { milestone: '5 teman', reward: '+1 Booster Gratis', status: 'locked' },
                                    { milestone: '10 teman', reward: '1 Bulan Premium Gratis', status: 'locked' },
                                ].map((r, i) => (
                                    <div key={i} className="flex items-center justify-between p-4 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl opacity-60">
                                        <div>
                                            <p className="text-sm font-bold">{r.milestone}</p>
                                            <p className="text-xs text-[var(--text-dim)]">{r.reward}</p>
                                        </div>
                                        <div className="w-6 h-6 rounded-full border border-[var(--border-color)] flex items-center justify-center">
                                            <Lock size={10} className="text-[var(--text-dim)]" />
                                        </div>
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
