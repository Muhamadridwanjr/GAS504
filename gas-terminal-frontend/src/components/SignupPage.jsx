import React, { useState } from 'react';
import { Zap, Eye, EyeOff, ArrowLeft, Check } from 'lucide-react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';

const LOGO = 'https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg';

export default function SignupPage() {
    const { saveSession } = useAuth();
    const [form, setForm] = useState({ username: '', email: '', full_name: '', password: '', confirm: '' });
    const [showPass, setShowPass] = useState(false);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const set = (k) => (e) => setForm(prev => ({ ...prev, [k]: e.target.value }));

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (form.password !== form.confirm) { setError('Password tidak cocok.'); return; }
        if (form.password.length < 8) { setError('Password minimal 8 karakter.'); return; }
        setLoading(true);
        try {
            const res = await axios.post('/auth/v1/auth/register', {
                username: form.username,
                email: form.email,
                full_name: form.full_name,
                password: form.password,
            });
            saveSession(res.data.access_token, res.data.user);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Registrasi gagal. Coba lagi.');
        } finally {
            setLoading(false);
        }
    };

    const PERKS = ['Signal AI real-time', '2 analisa gratis per hari', 'Bloomberg Terminal akses', 'Tanpa kartu kredit'];

    return (
        <div className="min-h-screen bg-[var(--bg-main)] flex items-center justify-center px-4 py-12 relative">
            {/* Background glow */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[600px] h-[400px] bg-yellow-400/5 blur-[100px] rounded-full" />
            </div>

            <div className="relative z-10 w-full max-w-4xl grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">

                {/* Left: Perks */}
                <div className="hidden lg:block">
                    <a href="/" className="inline-flex items-center gap-2 text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors text-sm font-bold mb-8">
                        <ArrowLeft size={14} /> Kembali ke Home
                    </a>
                    <div className="flex items-center gap-3 mb-6">
                        <img src={LOGO} alt="GAS" className="w-12 h-12 rounded-2xl object-cover ring-2 ring-yellow-400/30" />
                        <div>
                            <span className="text-lg font-black font-display">GOLDEN <span className="text-[var(--accent)]">AI</span></span>
                            <p className="text-[10px] text-[var(--text-dim)] font-bold uppercase tracking-widest">Strategy Platform</p>
                        </div>
                    </div>
                    <h2 className="text-3xl font-black font-display leading-tight mb-3">
                        Mulai Trading<br /><span className="text-[var(--accent)]">Lebih Cerdas</span>
                    </h2>
                    <p className="text-sm text-[var(--text-dim)] mb-8 leading-relaxed">
                        Bergabung dengan 12,400+ trader yang sudah merasakan manfaat AI trading signal.
                    </p>
                    <div className="space-y-3">
                        {PERKS.map((p, i) => (
                            <div key={i} className="flex items-center gap-3">
                                <div className="w-6 h-6 rounded-full bg-yellow-400/10 border border-yellow-400/30 flex items-center justify-center shrink-0">
                                    <Check size={12} className="text-[var(--accent)]" />
                                </div>
                                <span className="text-sm font-bold text-[var(--text-secondary)]">{p}</span>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Right: Form */}
                <div>
                    <a href="/" className="lg:hidden inline-flex items-center gap-2 text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors text-sm font-bold mb-6">
                        <ArrowLeft size={14} /> Home
                    </a>

                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 sm:p-8">
                        <div className="flex items-center gap-2 mb-6 lg:hidden">
                            <img src={LOGO} alt="GAS" className="w-8 h-8 rounded-xl object-cover" />
                            <span className="font-black font-display">GOLDEN <span className="text-[var(--accent)]">AI</span></span>
                        </div>

                        <h1 className="text-xl font-black text-[var(--text-primary)] mb-1">Buat Akun Gratis</h1>
                        <p className="text-xs text-[var(--text-dim)] mb-6">Tidak perlu kartu kredit · Langsung aktif</p>

                        {error && (
                            <p className="text-[11px] text-[var(--danger)] bg-[var(--danger)]/10 border border-[var(--danger)]/20 rounded-lg px-3 py-2 mb-4 text-center">
                                {error}
                            </p>
                        )}

                        <form onSubmit={handleSubmit} className="flex flex-col gap-3.5">
                            <div className="grid grid-cols-2 gap-3">
                                <div>
                                    <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Nama Lengkap</label>
                                    <input type="text" value={form.full_name} onChange={set('full_name')} placeholder="John Doe" required
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]" />
                                </div>
                                <div>
                                    <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Username</label>
                                    <input type="text" value={form.username} onChange={set('username')} placeholder="johndoe" required
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]" />
                                </div>
                            </div>

                            <div>
                                <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Email</label>
                                <input type="email" value={form.email} onChange={set('email')} placeholder="john@email.com" required
                                    className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]" />
                            </div>

                            <div>
                                <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Password</label>
                                <div className="relative">
                                    <input type={showPass ? 'text' : 'password'} value={form.password} onChange={set('password')} placeholder="Min. 8 karakter" required minLength={8}
                                        className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 pr-10 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]" />
                                    <button type="button" onClick={() => setShowPass(!showPass)} className="absolute right-3 top-1/2 -translate-y-1/2 text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors">
                                        {showPass ? <EyeOff size={14} /> : <Eye size={14} />}
                                    </button>
                                </div>
                            </div>

                            <div>
                                <label className="text-[10px] font-black text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Konfirmasi Password</label>
                                <input type="password" value={form.confirm} onChange={set('confirm')} placeholder="Ulangi password" required
                                    className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]" />
                            </div>

                            <p className="text-[10px] text-[var(--text-dim)] leading-relaxed">
                                Dengan mendaftar, kamu setuju dengan <a href="#" className="text-[var(--accent)] hover:underline">Terms of Service</a> dan <a href="#" className="text-[var(--accent)] hover:underline">Privacy Policy</a> kami.
                            </p>

                            <button type="submit" disabled={loading}
                                className="w-full bg-[var(--accent)] text-black font-black text-sm py-3 rounded-xl hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_4px_14px_rgba(250,204,21,0.3)] hover:shadow-[0_6px_20px_rgba(250,204,21,0.5)]">
                                {loading ? 'Membuat akun...' : 'Buat Akun Gratis'}
                            </button>
                        </form>

                        <div className="flex items-center gap-2 my-4">
                            <div className="flex-1 border-t border-[var(--border-color)]" />
                            <span className="text-[10px] text-[var(--text-dim)]">atau</span>
                            <div className="flex-1 border-t border-[var(--border-color)]" />
                        </div>

                        <p className="text-center text-xs text-[var(--text-dim)]">
                            Sudah punya akun?{' '}
                            <a href="/login" className="text-[var(--accent)] font-bold hover:underline">Sign In</a>
                        </p>
                    </div>
                </div>
            </div>
        </div>
    );
}
