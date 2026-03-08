import React, { useState } from 'react';
import { Zap, ArrowLeft } from 'lucide-react';
import axios from 'axios';
import { getGoogleLoginUrl } from '../services/auth';
import { useAuth } from '../context/AuthContext';

export default function LoginPage() {
    const { saveSession } = useAuth();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [googleLoading, setGoogleLoading] = useState(false);

    const handleLogin = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);
        try {
            const res = await axios.post('/auth/v1/auth/login', { username, password });
            saveSession(res.data.access_token, res.data.user);
        } catch (err) {
            setError(err?.response?.data?.detail || 'Login gagal. Periksa username dan password.');
        } finally {
            setLoading(false);
        }
    };

    const handleGoogleLogin = async () => {
        setError('');
        setGoogleLoading(true);
        try {
            const url = await getGoogleLoginUrl();
            window.location.href = url;
        } catch {
            setError('Gagal terhubung ke auth service.');
            setGoogleLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-[var(--bg-main)] flex items-center justify-center px-4">
            <div className="w-full max-w-sm">
                <a href="/" className="inline-flex items-center gap-2 text-[var(--text-dim)] hover:text-[var(--text-primary)] transition-colors text-xs font-bold mb-6">
                    <ArrowLeft size={12} /> Kembali ke Home
                </a>
                {/* Logo */}
                <div className="flex items-center justify-center gap-3 mb-8">
                    <img src="https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg" alt="GAS" className="w-10 h-10 rounded-xl object-cover ring-2 ring-yellow-400/30" />
                    <span className="text-xl font-black tracking-tight font-display">
                        GOLDEN <span className="text-[var(--accent)]">AI</span>
                    </span>
                </div>

                {/* Card */}
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-2xl p-6 flex flex-col gap-5">
                    <div className="text-center">
                        <h1 className="text-base font-black text-[var(--text-primary)] mb-1">Selamat Datang</h1>
                        <p className="text-xs text-[var(--text-dim)]">Masuk ke GAS PRO Terminal</p>
                    </div>

                    {error && (
                        <p className="text-[11px] text-[var(--danger)] bg-[var(--danger)]/10 border border-[var(--danger)]/20 rounded-lg px-3 py-2 text-center">
                            {error}
                        </p>
                    )}

                    {/* Username/Password form */}
                    <form onSubmit={handleLogin} className="flex flex-col gap-3">
                        <div>
                            <label className="text-[10px] font-bold text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Username</label>
                            <input
                                type="text"
                                value={username}
                                onChange={e => setUsername(e.target.value)}
                                placeholder="Username atau email"
                                required
                                autoComplete="username"
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]"
                            />
                        </div>
                        <div>
                            <label className="text-[10px] font-bold text-[var(--text-dim)] uppercase tracking-widest mb-1 block">Password</label>
                            <input
                                type="password"
                                value={password}
                                onChange={e => setPassword(e.target.value)}
                                placeholder="••••••••"
                                required
                                autoComplete="current-password"
                                className="w-full bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-lg px-3 py-2.5 text-sm text-[var(--text-primary)] outline-none focus:border-[var(--accent)] transition-colors placeholder:text-[var(--text-dim)]"
                            />
                        </div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full bg-[var(--accent)] text-black font-black text-sm py-2.5 rounded-lg hover:opacity-90 transition-opacity disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Masuk...' : 'Masuk'}
                        </button>
                    </form>

                    {/* Divider */}
                    <div className="flex items-center gap-2">
                        <div className="flex-1 border-t border-[var(--border-color)]" />
                        <span className="text-[10px] text-[var(--text-dim)]">atau</span>
                        <div className="flex-1 border-t border-[var(--border-color)]" />
                    </div>

                    {/* Google login */}
                    <button
                        onClick={handleGoogleLogin}
                        disabled={googleLoading}
                        className="w-full flex items-center justify-center gap-3 bg-white text-gray-800 font-bold text-sm py-2.5 px-4 rounded-xl hover:bg-gray-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-sm border border-gray-200"
                    >
                        <svg width="16" height="16" viewBox="0 0 24 24">
                            <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                            <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                            <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                            <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                        </svg>
                        {googleLoading ? 'Mengarahkan...' : 'Masuk dengan Google'}
                    </button>
                </div>

                <p className="text-center text-xs text-[var(--text-dim)] mt-4">
                    Belum punya akun?{' '}
                    <a href="/signup" className="text-[var(--accent)] font-bold hover:underline">Daftar Gratis</a>
                </p>
            </div>
        </div>
    );
}
