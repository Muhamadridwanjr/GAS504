import React, { useState, useEffect, useRef } from 'react';
import {
    Zap, BarChart2, Shield, Brain, Globe, TrendingUp,
    Star, ChevronRight, Check, Moon, Sun, Menu, X,
    ArrowRight, Play, Quote, Twitter, MessageCircle,
    BookOpen, FileText, Users, Award, ChevronDown
} from 'lucide-react';

const LOGO = 'https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg';

const TIERS = [
    { id: 'essential', name: 'Essential', monthly: 2.99, annual: 29.99, quota: 5, daily: 2, highlight: false, models: ['Gemini 2.5 Pro', 'DeepSeek V3.2', 'Grok 4.1 Fast', 'GPT-5 Mini'] },
    { id: 'plus', name: 'Plus', monthly: 5.99, annual: 59.99, quota: 12, daily: 4, highlight: false, models: ['MoonshotAI Kimi K2.5', 'Gemini 3 Flash Preview', 'Gemini 3 Pro Preview', 'Qwen3.5-35B'] },
    { id: 'premium', name: 'Premium', monthly: 11.99, annual: 119.99, quota: 25, daily: 10, highlight: true, models: ['Gemini 3.1 Flash Lite', 'Gemini 3.1 Pro Preview', 'Claude Opus 4.5', 'Claude Haiku 4.5'] },
    { id: 'ultimate', name: 'Ultimate', monthly: 19.99, annual: 199.99, quota: 50, daily: 15, highlight: false, models: ['Z.ai GLM 5', 'OpenAI GPT-5.4', 'Claude Sonnet 4.6', 'Claude Opus 4.6'] },
];

const REVIEWS = [
    { name: 'Ahmad R.', role: 'Swing Trader · Jakarta', rating: 5, avatar: 'AR', text: 'Win rate saya naik dari 52% ke 71% setelah 3 bulan pakai GAS PRO. AI signal-nya akurat banget, terutama untuk XAUUSD dan GBPJPY.', verified: true },
    { name: 'Siti M.', role: 'Forex Trader · Surabaya', rating: 5, avatar: 'SM', text: 'Serius ini platform terbaik yang pernah saya coba. Real-time signal, analisis makro, dan calendar event semua dalam satu dashboard. Worth every penny!', verified: true },
    { name: 'Budi K.', role: 'Day Trader · Bandung', rating: 5, avatar: 'BK', text: 'Fitur AI Bloomberg Terminal-nya gila sih. Bisa tanya analisa market langsung dan dijawab dengan data real-time. Nggak ada platform lain yang bisa lakuin ini.', verified: true },
    { name: 'Rina P.', role: 'Prop Trader · Bali', rating: 5, avatar: 'RP', text: 'Sudah 6 bulan langganan Premium. Konsistensi signal-nya luar biasa. Tim support juga responsif banget. Highly recommended!', verified: true },
    { name: 'Dani F.', role: 'Crypto & Forex · Medan', rating: 5, avatar: 'DF', text: 'Platform ini mengubah cara saya trading. Dari yang asal-asalan jadi sistematis. ROI bulan pertama sudah cover biaya langganan setahun.', verified: true },
    { name: 'Yoga S.', role: 'Scalper · Yogyakarta', rating: 5, avatar: 'YS', text: 'Multi-timeframe analysis dan entry precision-nya top. Biasanya saya salah timing, sekarang entry selalu di level yang tepat berkat AI GAS.', verified: true },
];

const BLOG_POSTS = [
    { tag: 'Strategy', title: 'Cara Membaca Signal AI dengan Benar untuk Profit Konsisten', date: '15 Jan 2026', read: '5 min', gradient: 'from-yellow-400/20 to-orange-400/20' },
    { tag: 'Analysis', title: 'NFP & FOMC: Panduan Trading Event Makro Menggunakan GAS PRO', date: '8 Jan 2026', read: '8 min', gradient: 'from-blue-400/20 to-purple-400/20' },
    { tag: 'Tutorial', title: 'Setup MT5 dengan GAS EA untuk Eksekusi Otomatis', date: '1 Jan 2026', read: '12 min', gradient: 'from-green-400/20 to-teal-400/20' },
];

const FEATURES = [
    { icon: Brain, title: 'AI Signal Engine', desc: 'Multi-model AI (Claude, GPT, Gemini) menganalisis pasar 24/7 dan menghasilkan signal entry/exit presisi tinggi.', color: 'text-yellow-400', bg: 'bg-yellow-400/10' },
    { icon: BarChart2, title: 'Bloomberg Terminal', desc: 'Terminal AI interaktif untuk tanya jawab analisa market real-time dengan data langsung dari broker MT5.', color: 'text-blue-400', bg: 'bg-blue-400/10' },
    { icon: Globe, title: 'Macro Calendar', desc: 'Economic calendar terintegrasi dengan impact analysis AI untuk setiap event NFP, FOMC, CPI, dan lainnya.', color: 'text-green-400', bg: 'bg-green-400/10' },
    { icon: TrendingUp, title: 'Multi-Asset Coverage', desc: 'Coverage lengkap: Forex, Gold (XAUUSD), Indices (US500, NAS100), Oil, dan Crypto dalam satu platform.', color: 'text-purple-400', bg: 'bg-purple-400/10' },
    { icon: Shield, title: 'Risk Management AI', desc: 'AI menghitung lot size optimal, stop loss, dan take profit berdasarkan volatilitas dan kondisi market terkini.', color: 'text-red-400', bg: 'bg-red-400/10' },
    { icon: Zap, title: 'MT5 EA Integration', desc: 'Expert Advisor eksklusif yang terhubung langsung ke GAS PRO untuk eksekusi signal semi-otomatis.', color: 'text-orange-400', bg: 'bg-orange-400/10' },
];

const STATS = [
    { value: '12,400+', label: 'Active Traders' },
    { value: '94.2%', label: 'Signal Accuracy' },
    { value: '3.8x', label: 'Avg ROI' },
    { value: '24/7', label: 'AI Analysis' },
];

export default function LandingPage() {
    const [theme, setTheme] = useState(() => localStorage.getItem('landing-theme') || 'dark');
    const [isAnnual, setIsAnnual] = useState(false);
    const [menuOpen, setMenuOpen] = useState(false);
    const [scrolled, setScrolled] = useState(false);
    const [activeSection, setActiveSection] = useState('home');
    const [openFaq, setOpenFaq] = useState(null);

    useEffect(() => {
        if (theme === 'dark') {
            document.documentElement.removeAttribute('data-theme');
        } else {
            document.documentElement.setAttribute('data-theme', 'light');
        }
        localStorage.setItem('landing-theme', theme);
    }, [theme]);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 20);
        window.addEventListener('scroll', onScroll);
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    const navigate = (path) => {
        window.location.href = path;
    };

    const scrollTo = (id) => {
        document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });
        setMenuOpen(false);
        setActiveSection(id);
    };

    const isDark = theme === 'dark';

    const FAQS = [
        { q: 'Apakah GAS PRO cocok untuk pemula?', a: 'Ya! GAS PRO dirancang untuk semua level trader. AI akan menjelaskan setiap signal dengan reasoning yang mudah dipahami, termasuk rekomendasi lot size berdasarkan modal Anda.' },
        { q: 'Berapa akurasi signal GAS PRO?', a: 'Berdasarkan backtesting 2 tahun dan live trading 6 bulan terakhir, akurasi signal GAS PRO mencapai 94.2% dengan risk-reward minimal 1:2.' },
        { q: 'Apakah bisa digunakan tanpa MT5?', a: 'Bisa! Dashboard terminal bisa digunakan standalone untuk analisa market. MT5 EA hanya diperlukan untuk eksekusi signal otomatis.' },
        { q: 'Bagaimana sistem refund?', a: 'Kami menyediakan 7-day money back guarantee tanpa pertanyaan. Jika tidak puas dalam 7 hari pertama, kami kembalikan 100% pembayaran Anda.' },
        { q: 'Apakah ada versi gratis?', a: 'Ya, ada tier Free dengan 2 signal per hari menggunakan model AI dasar. Upgrade kapan saja untuk akses penuh tanpa batas.' },
    ];

    return (
        <div className={`min-h-screen font-sans transition-colors duration-300 ${isDark ? 'bg-black text-white' : 'bg-white text-gray-900'}`}>

            {/* ── NAVBAR ── */}
            <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? (isDark ? 'bg-black/90 backdrop-blur border-b border-white/5 shadow-2xl' : 'bg-white/90 backdrop-blur border-b border-black/5 shadow-md') : 'bg-transparent'}`}>
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    {/* Logo */}
                    <button onClick={() => scrollTo('home')} className="flex items-center gap-2.5 shrink-0">
                        <img src={LOGO} alt="GAS Logo" className="w-9 h-9 rounded-xl object-cover ring-2 ring-yellow-400/30" />
                        <span className={`text-base font-black tracking-tight font-display hidden sm:block ${isDark ? 'text-white' : 'text-gray-900'}`}>
                            GOLDEN <span className="text-yellow-400">AI</span>
                        </span>
                    </button>

                    {/* Desktop Nav */}
                    <div className="hidden md:flex items-center gap-6">
                        {['home', 'pricing', 'docs', 'blog', 'review'].map(s => (
                            <button key={s} onClick={() => scrollTo(s)}
                                className={`text-sm font-semibold capitalize transition-colors ${activeSection === s ? 'text-yellow-400' : isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'}`}>
                                {s === 'docs' ? 'Docs' : s === 'blog' ? 'Blog' : s === 'review' ? 'Review' : s.charAt(0).toUpperCase() + s.slice(1)}
                            </button>
                        ))}
                    </div>

                    {/* Right */}
                    <div className="flex items-center gap-2 sm:gap-3">
                        <button onClick={() => setTheme(isDark ? 'light' : 'dark')}
                            className={`p-2 rounded-lg transition-colors ${isDark ? 'text-gray-400 hover:text-white hover:bg-white/10' : 'text-gray-500 hover:text-gray-900 hover:bg-black/5'}`}>
                            {isDark ? <Sun size={16} /> : <Moon size={16} />}
                        </button>
                        <button onClick={() => navigate('/login')}
                            className={`hidden sm:block text-sm font-bold px-4 py-2 rounded-lg transition-colors ${isDark ? 'text-gray-300 hover:text-white hover:bg-white/10' : 'text-gray-600 hover:text-gray-900 hover:bg-black/5'}`}>
                            Sign In
                        </button>
                        <button onClick={() => navigate('/signup')}
                            className="text-sm font-black px-4 py-2 rounded-xl bg-yellow-400 text-black hover:bg-yellow-300 transition-all shadow-[0_4px_14px_rgba(250,204,21,0.4)] hover:shadow-[0_6px_20px_rgba(250,204,21,0.5)] active:scale-95">
                            Sign Up
                        </button>
                        <button onClick={() => setMenuOpen(!menuOpen)} className={`md:hidden p-2 rounded-lg ${isDark ? 'text-white' : 'text-gray-900'}`}>
                            {menuOpen ? <X size={20} /> : <Menu size={20} />}
                        </button>
                    </div>
                </div>

                {/* Mobile menu */}
                {menuOpen && (
                    <div className={`md:hidden border-t ${isDark ? 'bg-black/95 border-white/10' : 'bg-white border-black/10'} px-4 py-4 flex flex-col gap-3`}>
                        {['home', 'pricing', 'docs', 'blog', 'review'].map(s => (
                            <button key={s} onClick={() => scrollTo(s)}
                                className={`text-sm font-semibold capitalize text-left py-2 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>
                                {s.charAt(0).toUpperCase() + s.slice(1)}
                            </button>
                        ))}
                        <div className="flex gap-3 pt-2 border-t border-white/10">
                            <button onClick={() => navigate('/login')} className="flex-1 text-sm font-bold py-2.5 rounded-xl border border-yellow-400/30 text-yellow-400">Sign In</button>
                            <button onClick={() => navigate('/signup')} className="flex-1 text-sm font-black py-2.5 rounded-xl bg-yellow-400 text-black">Sign Up</button>
                        </div>
                    </div>
                )}
            </nav>

            {/* ── HERO ── */}
            <section id="home" className={`relative min-h-screen flex items-center justify-center pt-16 overflow-hidden ${isDark ? 'bg-black' : 'bg-gray-50'}`}>
                {/* Background grid */}
                <div className="absolute inset-0 pointer-events-none">
                    <div className={`absolute inset-0 ${isDark ? 'opacity-[0.03]' : 'opacity-[0.04]'}`}
                        style={{ backgroundImage: 'linear-gradient(rgba(250,200,21,1) 1px, transparent 1px), linear-gradient(90deg, rgba(250,200,21,1) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />
                    <div className={`absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[600px] rounded-full blur-[120px] ${isDark ? 'bg-yellow-400/8' : 'bg-yellow-400/15'}`} />
                    <div className={`absolute bottom-0 right-0 w-96 h-96 rounded-full blur-[100px] ${isDark ? 'bg-yellow-600/5' : 'bg-yellow-300/20'}`} />
                </div>

                <div className="relative z-10 max-w-5xl mx-auto px-4 text-center">
                    {/* Badge */}
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full border border-yellow-400/30 bg-yellow-400/10 mb-8">
                        <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse" />
                        <span className="text-xs font-black text-yellow-400 uppercase tracking-widest">Live · AI-Powered Trading Platform</span>
                    </div>

                    {/* Headline */}
                    <h1 className="font-display font-black text-5xl sm:text-6xl md:text-7xl lg:text-8xl leading-none mb-6">
                        <span className={isDark ? 'text-white' : 'text-gray-900'}>TRADING DENGAN</span>
                        <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-yellow-300 to-yellow-500">
                            KECERDASAN AI
                        </span>
                    </h1>

                    <p className={`text-lg sm:text-xl max-w-2xl mx-auto mb-10 leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                        Platform trading AI pertama di Indonesia yang menggabungkan <strong className={isDark ? 'text-white' : 'text-gray-900'}>signal presisi tinggi</strong>, Bloomberg Terminal interaktif, dan analisa makro real-time dalam satu dashboard terintegrasi.
                    </p>

                    {/* CTA buttons */}
                    <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-16">
                        <button onClick={() => navigate('/signup')}
                            className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-yellow-400 text-black font-black text-base hover:bg-yellow-300 transition-all shadow-[0_8px_30px_rgba(250,204,21,0.4)] hover:shadow-[0_12px_40px_rgba(250,204,21,0.6)] active:scale-95">
                            Mulai Gratis Sekarang
                            <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                        </button>
                        <button onClick={() => scrollTo('review')}
                            className={`flex items-center gap-3 px-8 py-4 rounded-2xl font-bold text-base border transition-all ${isDark ? 'border-white/10 text-white hover:bg-white/5' : 'border-black/10 text-gray-700 hover:bg-black/5'}`}>
                            <Play size={16} className="text-yellow-400" />
                            Lihat Review Trader
                        </button>
                    </div>

                    {/* Stats */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 max-w-3xl mx-auto">
                        {STATS.map((s, i) => (
                            <div key={i} className={`rounded-2xl p-4 border ${isDark ? 'bg-white/3 border-white/8' : 'bg-white border-gray-200 shadow-sm'}`}>
                                <div className="text-2xl font-black text-yellow-400 font-display">{s.value}</div>
                                <div className={`text-xs font-bold uppercase tracking-wider mt-1 ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{s.label}</div>
                            </div>
                        ))}
                    </div>
                </div>

                {/* Scroll indicator */}
                <div className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2 animate-bounce">
                    <span className={`text-[10px] font-bold uppercase tracking-widest ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>Scroll</span>
                    <ChevronDown size={16} className={isDark ? 'text-gray-600' : 'text-gray-400'} />
                </div>
            </section>

            {/* ── FEATURES ── */}
            <section className={`py-24 px-4 ${isDark ? 'bg-[#050505]' : 'bg-white'}`}>
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-400/10 border border-yellow-400/20 mb-4">
                            <Zap size={12} className="text-yellow-400" />
                            <span className="text-xs font-black text-yellow-400 uppercase tracking-widest">Platform Features</span>
                        </div>
                        <h2 className="font-display font-black text-4xl sm:text-5xl mb-4">
                            Semua Yang Kamu Butuhkan
                        </h2>
                        <p className={`text-base max-w-xl mx-auto ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                            Dari signal AI hingga analisa makro — platform yang mengubah trader biasa menjadi trader profesional.
                        </p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                        {FEATURES.map((f, i) => (
                            <div key={i} className={`group p-6 rounded-2xl border transition-all hover:scale-[1.02] hover:shadow-2xl ${isDark ? 'bg-white/3 border-white/6 hover:border-yellow-400/20 hover:bg-white/5' : 'bg-gray-50 border-gray-100 hover:border-yellow-400/30 hover:bg-white'}`}>
                                <div className={`w-12 h-12 rounded-xl ${f.bg} flex items-center justify-center mb-4`}>
                                    <f.icon size={22} className={f.color} />
                                </div>
                                <h3 className="font-display font-black text-lg mb-2">{f.title}</h3>
                                <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{f.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── HOW IT WORKS ── */}
            <section className={`py-24 px-4 ${isDark ? 'bg-black' : 'bg-gray-50'}`}>
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-16">
                        <h2 className="font-display font-black text-4xl sm:text-5xl mb-4">Mulai Dalam <span className="text-yellow-400">3 Langkah</span></h2>
                        <p className={`text-base ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Setup dalam hitungan menit, profit dari hari pertama.</p>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                        {[
                            { step: '01', title: 'Daftar Akun', desc: 'Buat akun gratis dalam 30 detik. Tidak perlu kartu kredit untuk mulai trial.' },
                            { step: '02', title: 'Pilih Plan', desc: 'Pilih tier yang sesuai kebutuhan. Mulai dari Free hingga Ultimate untuk akses penuh.' },
                            { step: '03', title: 'Trade & Profit', desc: 'Terima signal AI real-time, analisa dengan Bloomberg Terminal, dan eksekusi dengan presisi.' },
                        ].map((s, i) => (
                            <div key={i} className="relative text-center">
                                {i < 2 && <div className={`hidden md:block absolute top-8 left-[calc(50%+40px)] right-0 h-px ${isDark ? 'border-t border-dashed border-white/10' : 'border-t border-dashed border-black/10'}`} />}
                                <div className="inline-flex w-16 h-16 rounded-2xl bg-yellow-400 text-black font-black text-xl items-center justify-center font-display mb-4">
                                    {s.step}
                                </div>
                                <h3 className="font-display font-black text-xl mb-2">{s.title}</h3>
                                <p className={`text-sm leading-relaxed ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{s.desc}</p>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── PRICING ── */}
            <section id="pricing" className={`py-24 px-4 ${isDark ? 'bg-[#050505]' : 'bg-white'}`}>
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-12">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-400/10 border border-yellow-400/20 mb-4">
                            <Star size={12} className="text-yellow-400" />
                            <span className="text-xs font-black text-yellow-400 uppercase tracking-widest">Pricing Plans</span>
                        </div>
                        <h2 className="font-display font-black text-4xl sm:text-5xl mb-4">Investasi Yang <span className="text-yellow-400">Sepadan</span></h2>
                        <p className={`text-base mb-8 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>ROI pertama Anda sudah cover biaya langganan. Garansi uang kembali 7 hari.</p>

                        {/* Toggle */}
                        <div className={`inline-flex items-center gap-1 p-1 rounded-full border ${isDark ? 'bg-white/5 border-white/10' : 'bg-gray-100 border-gray-200'}`}>
                            <button onClick={() => setIsAnnual(false)} className={`px-5 py-2 rounded-full text-xs font-black transition-all ${!isAnnual ? 'bg-yellow-400 text-black shadow-md' : isDark ? 'text-gray-400' : 'text-gray-500'}`}>Bulanan</button>
                            <button onClick={() => setIsAnnual(true)} className={`px-5 py-2 rounded-full text-xs font-black transition-all ${isAnnual ? 'bg-yellow-400 text-black shadow-md' : isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                                Tahunan <span className="ml-1 opacity-70">–10%</span>
                            </button>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-5">
                        {TIERS.map((t) => (
                            <div key={t.id} className={`relative rounded-3xl p-7 flex flex-col gap-5 transition-all hover:scale-[1.02] ${
                                t.highlight
                                    ? 'bg-yellow-400 text-black shadow-[0_20px_60px_rgba(250,204,21,0.4)] border-2 border-yellow-300'
                                    : isDark ? 'bg-white/4 border border-white/8 hover:border-yellow-400/20' : 'bg-gray-50 border border-gray-200 hover:border-yellow-400/30'
                            }`}>
                                {t.highlight && <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-black text-yellow-400 text-[10px] font-black px-3 py-1 rounded-full uppercase tracking-widest">Best Value</div>}
                                <div>
                                    <p className={`text-[10px] font-black uppercase tracking-[0.2em] mb-2 ${t.highlight ? 'text-black/60' : 'text-yellow-400'}`}>{t.name}</p>
                                    <div className="flex items-baseline gap-1">
                                        <span className="text-4xl font-black font-display">${isAnnual ? t.annual : t.monthly}</span>
                                        <span className={`text-xs font-bold ${t.highlight ? 'text-black/50' : isDark ? 'text-gray-500' : 'text-gray-400'}`}>/{isAnnual ? 'yr' : 'mo'}</span>
                                    </div>
                                </div>
                                <div className={`text-xs font-bold px-3 py-2 rounded-xl ${t.highlight ? 'bg-black/10' : isDark ? 'bg-white/5' : 'bg-white border border-gray-200'}`}>
                                    <Zap size={12} className={`inline mr-1 ${t.highlight ? 'text-black' : 'text-yellow-400'}`} />
                                    {t.quota} analisa/bulan · {t.daily} per hari
                                </div>
                                <div className="space-y-2 flex-1">
                                    {t.models.map(m => (
                                        <div key={m} className="flex items-center gap-2 text-[11px] font-medium">
                                            <Check size={12} className={t.highlight ? 'text-black/70' : 'text-green-500'} />
                                            <span>{m}</span>
                                        </div>
                                    ))}
                                </div>
                                <button onClick={() => navigate('/signup')}
                                    className={`w-full py-3.5 rounded-2xl font-black text-sm transition-all flex items-center justify-center gap-2 active:scale-95 ${
                                        t.highlight
                                            ? 'bg-black text-yellow-400 hover:bg-black/80'
                                            : 'bg-yellow-400 text-black hover:bg-yellow-300 shadow-[0_4px_14px_rgba(250,204,21,0.3)]'
                                    }`}>
                                    Pilih {t.name} <ChevronRight size={15} />
                                </button>
                            </div>
                        ))}
                    </div>

                    <p className={`text-center text-xs mt-8 ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                        Semua plan termasuk 7-day money back guarantee · Tidak perlu kartu kredit untuk Free tier
                    </p>
                </div>
            </section>

            {/* ── REVIEWS ── */}
            <section id="review" className={`py-24 px-4 ${isDark ? 'bg-black' : 'bg-gray-50'}`}>
                <div className="max-w-7xl mx-auto">
                    <div className="text-center mb-16">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-400/10 border border-yellow-400/20 mb-4">
                            <Star size={12} className="text-yellow-400 fill-yellow-400" />
                            <span className="text-xs font-black text-yellow-400 uppercase tracking-widest">Testimonials</span>
                        </div>
                        <h2 className="font-display font-black text-4xl sm:text-5xl mb-4">
                            Kata Trader <span className="text-yellow-400">Sukses Kami</span>
                        </h2>
                        <div className="flex items-center justify-center gap-1 mb-2">
                            {[...Array(5)].map((_, i) => <Star key={i} size={18} className="text-yellow-400 fill-yellow-400" />)}
                        </div>
                        <p className={`text-sm ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>4.9/5 dari 12,400+ trader aktif</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
                        {REVIEWS.map((r, i) => (
                            <div key={i} className={`p-6 rounded-2xl border transition-all hover:scale-[1.01] ${isDark ? 'bg-white/3 border-white/6 hover:border-yellow-400/20' : 'bg-white border-gray-100 shadow-sm hover:shadow-md'}`}>
                                <Quote size={24} className="text-yellow-400/30 mb-3" />
                                <p className={`text-sm leading-relaxed mb-5 ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>"{r.text}"</p>
                                <div className="flex items-center justify-between">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-yellow-400 flex items-center justify-center text-black font-black text-xs">{r.avatar}</div>
                                        <div>
                                            <div className="font-bold text-sm flex items-center gap-1">
                                                {r.name}
                                                {r.verified && <span className="w-3.5 h-3.5 bg-blue-500 rounded-full flex items-center justify-center"><Check size={8} className="text-white" /></span>}
                                            </div>
                                            <div className={`text-[10px] font-medium ${isDark ? 'text-gray-500' : 'text-gray-400'}`}>{r.role}</div>
                                        </div>
                                    </div>
                                    <div className="flex gap-0.5">{[...Array(r.rating)].map((_, j) => <Star key={j} size={12} className="text-yellow-400 fill-yellow-400" />)}</div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── BLOG ── */}
            <section id="blog" className={`py-24 px-4 ${isDark ? 'bg-[#050505]' : 'bg-white'}`}>
                <div className="max-w-7xl mx-auto">
                    <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-12">
                        <div>
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-400/10 border border-yellow-400/20 mb-4">
                                <BookOpen size={12} className="text-yellow-400" />
                                <span className="text-xs font-black text-yellow-400 uppercase tracking-widest">Blog & Insights</span>
                            </div>
                            <h2 className="font-display font-black text-4xl sm:text-5xl">Artikel <span className="text-yellow-400">Terbaru</span></h2>
                        </div>
                        <button className={`text-sm font-bold flex items-center gap-2 ${isDark ? 'text-gray-400 hover:text-white' : 'text-gray-500 hover:text-gray-900'} transition-colors`}>
                            Lihat Semua <ArrowRight size={14} />
                        </button>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        {BLOG_POSTS.map((p, i) => (
                            <div key={i} className={`group rounded-2xl overflow-hidden border cursor-pointer transition-all hover:scale-[1.01] hover:shadow-xl ${isDark ? 'bg-white/3 border-white/6 hover:border-yellow-400/20' : 'bg-gray-50 border-gray-100 hover:border-yellow-400/30'}`}>
                                <div className={`h-36 bg-gradient-to-br ${p.gradient} flex items-end p-4`}>
                                    <span className="text-xs font-black bg-yellow-400 text-black px-2 py-1 rounded-lg">{p.tag}</span>
                                </div>
                                <div className="p-5">
                                    <h3 className="font-bold text-sm leading-snug mb-3 group-hover:text-yellow-400 transition-colors">{p.title}</h3>
                                    <div className={`flex items-center gap-3 text-[10px] font-bold ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                                        <span>{p.date}</span>
                                        <span>·</span>
                                        <span>{p.read} read</span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── DOCS ── */}
            <section id="docs" className={`py-24 px-4 ${isDark ? 'bg-black' : 'bg-gray-50'}`}>
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-12">
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-yellow-400/10 border border-yellow-400/20 mb-4">
                            <FileText size={12} className="text-yellow-400" />
                            <span className="text-xs font-black text-yellow-400 uppercase tracking-widest">Documentation</span>
                        </div>
                        <h2 className="font-display font-black text-4xl sm:text-5xl mb-4">Dokumentasi <span className="text-yellow-400">Lengkap</span></h2>
                        <p className={`text-base ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>Semua yang kamu butuhkan untuk memaksimalkan GAS PRO.</p>
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                        {[
                            { icon: Zap, title: 'Quick Start Guide', desc: 'Setup akun dan terima signal pertama dalam 5 menit', tag: 'Beginner' },
                            { icon: Brain, title: 'AI Signal Interpretation', desc: 'Cara membaca dan mengeksekusi signal AI dengan benar', tag: 'Strategy' },
                            { icon: BarChart2, title: 'Bloomberg Terminal Guide', desc: 'Panduan lengkap menggunakan AI terminal untuk analisa', tag: 'Advanced' },
                            { icon: Shield, title: 'MT5 EA Setup', desc: 'Instalasi dan konfigurasi Expert Advisor di MetaTrader 5', tag: 'Integration' },
                        ].map((d, i) => (
                            <div key={i} className={`group flex items-start gap-4 p-5 rounded-2xl border cursor-pointer transition-all hover:border-yellow-400/30 ${isDark ? 'bg-white/3 border-white/6 hover:bg-white/5' : 'bg-white border-gray-200 hover:bg-gray-50'}`}>
                                <div className="w-10 h-10 rounded-xl bg-yellow-400/10 flex items-center justify-center shrink-0">
                                    <d.icon size={18} className="text-yellow-400" />
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center justify-between mb-1">
                                        <h3 className="font-bold text-sm">{d.title}</h3>
                                        <span className={`text-[9px] font-black px-2 py-0.5 rounded-full ${isDark ? 'bg-white/10 text-gray-400' : 'bg-gray-100 text-gray-500'}`}>{d.tag}</span>
                                    </div>
                                    <p className={`text-xs ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>{d.desc}</p>
                                </div>
                                <ChevronRight size={14} className={`${isDark ? 'text-gray-600 group-hover:text-yellow-400' : 'text-gray-300 group-hover:text-yellow-400'} transition-colors shrink-0 mt-1`} />
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── FAQ ── */}
            <section className={`py-24 px-4 ${isDark ? 'bg-[#050505]' : 'bg-white'}`}>
                <div className="max-w-3xl mx-auto">
                    <div className="text-center mb-12">
                        <h2 className="font-display font-black text-4xl sm:text-5xl mb-3">Pertanyaan <span className="text-yellow-400">Umum</span></h2>
                    </div>
                    <div className="space-y-3">
                        {FAQS.map((f, i) => (
                            <div key={i} className={`rounded-2xl border overflow-hidden transition-all ${isDark ? 'bg-white/3 border-white/6' : 'bg-gray-50 border-gray-200'}`}>
                                <button onClick={() => setOpenFaq(openFaq === i ? null : i)}
                                    className="w-full flex items-center justify-between px-5 py-4 text-left">
                                    <span className="font-bold text-sm pr-4">{f.q}</span>
                                    <ChevronDown size={16} className={`shrink-0 text-yellow-400 transition-transform ${openFaq === i ? 'rotate-180' : ''}`} />
                                </button>
                                {openFaq === i && (
                                    <div className={`px-5 pb-4 text-sm leading-relaxed ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>{f.a}</div>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </section>

            {/* ── FINAL CTA ── */}
            <section className={`py-24 px-4 ${isDark ? 'bg-black' : 'bg-gray-50'}`}>
                <div className="max-w-4xl mx-auto text-center">
                    <div className={`relative rounded-[2.5rem] p-12 overflow-hidden ${isDark ? 'bg-white/3 border border-white/8' : 'bg-white border border-gray-200 shadow-xl'}`}>
                        <div className="absolute inset-0 pointer-events-none">
                            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-96 h-48 bg-yellow-400/8 blur-[80px] rounded-full" />
                        </div>
                        <div className="relative z-10">
                            <img src={LOGO} alt="GAS Logo" className="w-16 h-16 rounded-2xl object-cover mx-auto mb-6 ring-2 ring-yellow-400/30 shadow-[0_0_30px_rgba(250,204,21,0.2)]" />
                            <h2 className="font-display font-black text-4xl sm:text-5xl mb-4">
                                Siap Ubah Cara <span className="text-yellow-400">Trading Kamu?</span>
                            </h2>
                            <p className={`text-base mb-8 max-w-lg mx-auto ${isDark ? 'text-gray-400' : 'text-gray-500'}`}>
                                Bergabung dengan 12,400+ trader yang sudah merasakan perbedaan trading dengan AI. Mulai gratis, upgrade kapan saja.
                            </p>
                            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                                <button onClick={() => navigate('/signup')}
                                    className="group flex items-center gap-3 px-8 py-4 rounded-2xl bg-yellow-400 text-black font-black text-base hover:bg-yellow-300 transition-all shadow-[0_8px_30px_rgba(250,204,21,0.4)] hover:shadow-[0_12px_40px_rgba(250,204,21,0.6)] active:scale-95">
                                    Daftar Gratis Sekarang
                                    <ArrowRight size={18} className="group-hover:translate-x-1 transition-transform" />
                                </button>
                                <button onClick={() => navigate('/login')}
                                    className={`text-sm font-bold px-6 py-4 rounded-2xl border transition-all ${isDark ? 'border-white/10 text-gray-400 hover:text-white hover:border-white/20' : 'border-gray-200 text-gray-500 hover:text-gray-900'}`}>
                                    Sudah punya akun? Sign In
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── FOOTER ── */}
            <footer className={`border-t ${isDark ? 'bg-black border-white/6' : 'bg-white border-gray-100'}`}>
                <div className="max-w-7xl mx-auto px-4 py-12">
                    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8 mb-12">
                        <div>
                            <div className="flex items-center gap-2.5 mb-4">
                                <img src={LOGO} alt="GAS Logo" className="w-9 h-9 rounded-xl object-cover" />
                                <span className="font-display font-black text-base">GOLDEN <span className="text-yellow-400">AI</span></span>
                            </div>
                            <p className={`text-xs leading-relaxed mb-4 ${isDark ? 'text-gray-500' : 'text-gray-500'}`}>
                                Platform trading AI pertama di Indonesia. AI-powered signals, Bloomberg Terminal, dan analisa makro real-time.
                            </p>
                            <div className="flex gap-3">
                                <a href="#" className={`p-2 rounded-lg transition-colors ${isDark ? 'text-gray-500 hover:text-white hover:bg-white/10' : 'text-gray-400 hover:text-gray-900 hover:bg-gray-100'}`}><Twitter size={16} /></a>
                                <a href="#" className={`p-2 rounded-lg transition-colors ${isDark ? 'text-gray-500 hover:text-white hover:bg-white/10' : 'text-gray-400 hover:text-gray-900 hover:bg-gray-100'}`}><MessageCircle size={16} /></a>
                            </div>
                        </div>
                        {[
                            { title: 'Product', links: ['Features', 'Pricing', 'Changelog', 'Roadmap'] },
                            { title: 'Resources', links: ['Documentation', 'Blog', 'Tutorials', 'API Reference'] },
                            { title: 'Company', links: ['About Us', 'Contact', 'Privacy Policy', 'Terms of Service'] },
                        ].map((col, i) => (
                            <div key={i}>
                                <h4 className={`text-xs font-black uppercase tracking-widest mb-4 ${isDark ? 'text-gray-400' : 'text-gray-400'}`}>{col.title}</h4>
                                <div className="space-y-2.5">
                                    {col.links.map(l => (
                                        <a key={l} href="#" className={`block text-sm transition-colors ${isDark ? 'text-gray-500 hover:text-white' : 'text-gray-500 hover:text-gray-900'}`}>{l}</a>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                    <div className={`border-t pt-8 flex flex-col sm:flex-row items-center justify-between gap-4 ${isDark ? 'border-white/6' : 'border-gray-100'}`}>
                        <p className={`text-xs ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                            © 2026 Golden AI Strategy. All rights reserved.
                        </p>
                        <p className={`text-xs ${isDark ? 'text-gray-600' : 'text-gray-400'}`}>
                            <span className="text-yellow-400 font-bold">GAS PRO</span> · Powered by Multi-Model AI
                        </p>
                    </div>
                </div>
            </footer>
        </div>
    );
}
