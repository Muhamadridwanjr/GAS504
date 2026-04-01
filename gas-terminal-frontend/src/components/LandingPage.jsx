import React, { useState, useEffect, useRef } from 'react';
import {
    Zap, BarChart2, Shield, Brain, Globe, TrendingUp,
    Star, ChevronRight, Check, Moon, Sun, Menu, X,
    ArrowRight, Quote, BookOpen, Users, Award, ChevronDown,
    Layers, Newspaper, ScanLine, Building2, GraduationCap,
    Link, Activity, Calendar, Droplet, RefreshCw, Bot, Target, Filter,
    Clock
} from 'lucide-react';
import PricingView from './PricingView';

const LOGO = 'https://i.ibb.co.com/603h1JF3/photo-2026-01-27-22-14-18.jpg';

const MONO = "'JetBrains Mono', 'Fira Code', 'Courier New', monospace";

/* ─────────────────────────── DATA ─────────────────────────── */

const FEATURE_GROUPS = [
    {
        category: '📊 Technical Analysis System',
        color: 'blue',
        accent: 'rgb(59,130,246)',
        bgAccent: 'rgba(59,130,246,0.12)',
        borderAccent: 'rgba(59,130,246,0.3)',
        features: [
            { icon: BarChart2,  name: 'Technical Analysis AI',  credits: 3,  plan: 'Essential+', planKey: 'essential', desc: 'Deteksi ADX, RSI, MACD, BB secara otomatis' },
            { icon: Zap,        name: 'Signal System AI',        credits: 3,  plan: 'Essential+', planKey: 'essential', desc: 'Generate sinyal ENTER/EXIT dengan SL, TP, RR ratio' },
            { icon: Activity,   name: 'Smart Alert',             credits: 1,  plan: 'Essential+', planKey: 'essential', desc: 'Push notifikasi ke Telegram/WA saat setup muncul' },
            { icon: Calendar,   name: 'Session Optimizer',       credits: 1,  plan: 'Essential+', planKey: 'essential', desc: 'Rekomendasi sesi terbaik Asian/London/NY' },
            { icon: Link,       name: 'Correlation Tracker',     credits: 3,  plan: 'Plus+',      planKey: 'plus',      desc: 'Monitor korelasi XAUUSD↔DXY↔US10Y↔SPX' },
            { icon: ScanLine,   name: 'Multi-Symbol Scanner',    credits: 15, plan: 'Ultimate',   planKey: 'ultimate',  desc: 'Scan 20+ pair sekaligus secara paralel' },
        ],
    },
    {
        category: '🌍 Fundamental Analysis System',
        color: 'green',
        accent: 'rgb(34,197,94)',
        bgAccent: 'rgba(34,197,94,0.12)',
        borderAccent: 'rgba(34,197,94,0.3)',
        features: [
            { icon: Globe,     name: 'Fundamental Analysis AI', credits: 5,  plan: 'Plus+',     planKey: 'plus',    desc: 'Analisa dampak GDP, NFP, CPI, Fed Rate' },
            { icon: Newspaper, name: 'Economic Calendar AI',    credits: 4,  plan: 'Plus+',     planKey: 'plus',    desc: 'Prediksi dampak news event sebelum rilis' },
            { icon: Droplet,   name: 'Sentiment Market AI',     credits: 5,  plan: 'Plus+',     planKey: 'plus',    desc: 'Fear/greed index, COT data, smart money' },
            { icon: BookOpen,  name: 'AI Market Briefing',      credits: 10, plan: 'Premium+',  planKey: 'premium', desc: 'Daily & weekly summary kondisi market' },
        ],
    },
    {
        category: '⚡ Hybrid & Risk System',
        color: 'yellow',
        accent: 'rgb(250,204,21)',
        bgAccent: 'rgba(250,204,21,0.12)',
        borderAccent: 'rgba(250,204,21,0.3)',
        features: [
            { icon: Layers,    name: 'Hybrid System AI',       credits: 8,  plan: 'Premium+', planKey: 'premium', desc: 'TA + FA + Sentiment jadi 1 confluence score 0-100' },
            { icon: Shield,    name: 'Risk Manager AI',         credits: 3,  plan: 'Plus+',    planKey: 'plus',    desc: 'Auto kalkulasi lot size, portfolio heat, max DD' },
            { icon: RefreshCw, name: 'Drawdown Recovery',       credits: 5,  plan: 'Premium+', planKey: 'premium', desc: 'AI adjust strategy saat dalam drawdown' },
            { icon: TrendingUp,name: 'AI Backtesting Engine',   credits: 20, plan: 'Ultimate', planKey: 'ultimate',desc: 'Test strategi di historical data' },
        ],
    },
    {
        category: '🧠 Psychology & Growth',
        color: 'purple',
        accent: 'rgb(168,85,247)',
        bgAccent: 'rgba(168,85,247,0.12)',
        borderAccent: 'rgba(168,85,247,0.3)',
        features: [
            { icon: Brain,        name: 'Psychology Coach AI',  credits: 5,  plan: 'Premium+', planKey: 'premium', desc: 'Deteksi FOMO, revenge trading, emotion score' },
            { icon: Bot,          name: 'AI Trade Journal',     credits: 8,  plan: 'Premium+', planKey: 'premium', desc: 'Auto-record trade, identifikasi bad patterns' },
            { icon: GraduationCap,name: 'AI Mentor Mode',       credits: 10, plan: 'Ultimate', planKey: 'ultimate',desc: 'Review trade seperti senior trader' },
            { icon: Building2,    name: 'Prop Firm Assistant',  credits: 8,  plan: 'Premium+', planKey: 'premium', desc: 'Jaga DD sesuai rules FTMO, MFF' },
        ],
    },
    {
        category: '🤖 AI Agent Trading System',
        color: 'rose',
        accent: 'rgb(244,63,94)',
        bgAccent: 'rgba(244,63,94,0.12)',
        borderAccent: 'rgba(244,63,94,0.35)',
        isNew: true,
        features: [
            { icon: Bot,          name: 'AI Agent Execute',      credits: 5,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'Multi-model agent otomatis: BUY/SELL/NO TRADE dengan confidence' },
            { icon: Activity,     name: 'Agent Lab Competition', credits: 10, plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'Jalankan 4 agent paralel, bandingkan winrate & PnL' },
            { icon: BarChart2,    name: 'Agent Performance',     credits: 0,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'Tracking winrate, drawdown, auto-disable jika performance buruk' },
            { icon: Zap,          name: 'EA Auto-Trading',       credits: 0,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: '1 EA = 1 Agent, signal langsung execute ke MT5' },
        ],
    },
    {
        category: '🔮 Polymarket Signal AI',
        color: 'indigo',
        accent: 'rgb(99,102,241)',
        bgAccent: 'rgba(99,102,241,0.12)',
        borderAccent: 'rgba(99,102,241,0.3)',
        isNew: true,
        features: [
            { icon: Globe,        name: 'Prediction Feed',         credits: 0,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'Live Polymarket prediction markets: Crypto, Forex, Macro, Politics' },
            { icon: Brain,        name: 'Signal AI Prediction',    credits: 5,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'GAS AI engine generates YES/NO probability signals for any market' },
            { icon: Activity,     name: 'AI Agent Prediction',     credits: 5,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: '4 AI models (Claude, GPT, Gemini, Grok) each predict independently' },
            { icon: Target,       name: 'Consensus Engine',        credits: 0,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'Aggregates all model outputs into a single high-confidence verdict' },
            { icon: Filter,       name: 'Category Filter',         credits: 0,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: '8 categories: Crypto, Forex/Gold, Macro, Intraday, Technical, Politics, Sports' },
            { icon: BarChart2,    name: 'Analytics & History',     credits: 0,  plan: 'Ultra Ultimate', planKey: 'ultra', desc: 'Prediction stats, action breakdown, and full session history' },
        ],
    },
    {
        category: '🎰 Memecoin Signal AI',
        color: 'purple',
        accent: 'rgb(153,69,255)',
        bgAccent: 'rgba(153,69,255,0.12)',
        borderAccent: 'rgba(153,69,255,0.3)',
        isNew: true,
        features: [
            { icon: Zap,       name: 'Dexscreener Live Feed',    credits: 0, plan: 'Premium+', planKey: 'premium', desc: 'Real-time trending tokens across Solana, ETH, Base, BSC, Arbitrum' },
            { icon: Shield,    name: 'Anti-Rug Detection',       credits: 0, plan: 'Premium+', planKey: 'premium', desc: 'Heuristic rug scoring: liquidity, buy pressure, token age, TX diversity' },
            { icon: Activity,  name: 'Composite Score (0-100)',  credits: 5, plan: 'Premium+', planKey: 'premium', desc: 'Multi-factor score combining rug safety, volume, momentum, liquidity' },
            { icon: Brain,     name: '4-Model AI Signal',        credits: 5, plan: 'Premium+', planKey: 'premium', desc: 'Claude, GPT, Gemini, Grok analyze each token for BUY/AVOID decision' },
            { icon: Globe,     name: 'Multi-Chain (5 chains)',   credits: 0, plan: 'Premium+', planKey: 'premium', desc: 'Scan Solana + Ethereum + Base + BSC + Arbitrum simultaneously' },
            { icon: RefreshCw, name: 'Auto-Refresh Scanner',     credits: 0, plan: 'Premium+', planKey: 'premium', desc: 'Live token scanner with 30s auto-refresh and chain filter' },
        ],
    },
];

const PLAN_BADGE = {
    essential: { label: 'Essential+',     bg: 'rgba(100,116,139,0.3)', color: '#94a3b8', border: 'rgba(100,116,139,0.4)' },
    plus:      { label: 'Plus+',          bg: 'rgba(59,130,246,0.2)',  color: '#60a5fa', border: 'rgba(59,130,246,0.4)' },
    premium:   { label: 'Premium+',       bg: 'rgba(250,204,21,0.15)', color: '#facc15', border: 'rgba(250,204,21,0.4)' },
    ultimate:  { label: 'Ultimate',       bg: 'rgba(168,85,247,0.2)',  color: '#c084fc', border: 'rgba(168,85,247,0.4)' },
    ultra:     { label: 'Ultra Ultimate', bg: 'rgba(244,63,94,0.2)',   color: '#fb7185', border: 'rgba(244,63,94,0.4)' },
};

const TIERS = [
    {
        id: 'essential', name: 'Essential', emoji: '⚡',
        monthly: 2.99, annual: 26.88,
        credits: 100, rollover: null,
        featureCount: 4,
        highlight: false, glow: null,
        models: ['DeepSeek V3.2', 'GPT-5 Mini', 'Grok 4.1 Fast', 'Gemini 2.5 Pro'],
        topFeatures: ['Technical Analysis AI', 'Signal System AI', 'Smart Alert', 'Session Optimizer'],
        cta: 'Start Essential',
    },
    {
        id: 'plus', name: 'Plus', emoji: '🚀',
        monthly: 5.99, annual: 53.88,
        credits: 200, rollover: null,
        featureCount: 9,
        highlight: false, glow: null,
        models: ['Qwen3.5-35B', 'Gemini 3 Flash', 'Kimi K2.5', 'Gemini 3 Pro'],
        topFeatures: ['Fundamental Analysis AI', 'Economic Calendar AI', 'Sentiment Market AI', 'Risk Manager AI', 'Correlation Tracker'],
        cta: 'Start Plus',
    },
    {
        id: 'premium', name: 'Premium', emoji: '⭐',
        monthly: 11.99, annual: 107.88,
        credits: 400, rollover: '1×',
        featureCount: 15,
        highlight: true, glow: 'rgba(250,204,21,0.2)',
        models: ['Gemini 3.1 Flash Lite', 'Claude Haiku 4.5', 'Gemini 3.1 Pro', 'Claude Opus 4.5'],
        topFeatures: ['Hybrid System AI', 'AI Market Briefing', 'Drawdown Recovery', 'Psychology Coach AI', 'AI Trade Journal', 'Prop Firm Assistant'],
        cta: 'Start Premium',
        popular: true,
    },
    {
        id: 'ultimate', name: 'Ultimate', emoji: '👑',
        monthly: 19.99, annual: 179.88,
        credits: 700, rollover: '1.5×',
        featureCount: 18,
        highlight: false, glow: 'rgba(168,85,247,0.25)',
        models: ['Z.ai GLM 5', 'Claude Sonnet 4.6', 'GPT-5.4', 'Claude Opus 4.6'],
        topFeatures: ['All 18 AI Features', 'Multi-Symbol Scanner', 'AI Backtesting Engine', 'AI Mentor Mode', 'Priority Support'],
        cta: 'Start Ultimate',
    },
    {
        id: 'ultra', name: 'Ultra Ultimate', emoji: '🤖',
        monthly: 39.99, annual: 359.88,
        credits: 1500, rollover: '2×',
        featureCount: 21,
        highlight: true, glow: 'rgba(244,63,94,0.3)',
        models: ['Claude Sonnet 4.6', 'GPT-5.4', 'Gemini Pro 3.1', 'Grok 4.2'],
        topFeatures: ['All 21 AI Features', 'AI Agent System (#19)', 'Polymarket Signal AI (#20)', 'Memecoin Signal AI (#21)', 'Auto-Trading EA', 'Agent Marketplace'],
        cta: '🤖 Start Ultra Ultimate',
        isNew: true,
    },
];

const BOOSTERS = [
    { name: 'Bronze', emoji: '🥉', price: 1.99, duration: '7 days', credits: 50, color: '#cd7f32', bg: 'rgba(205,127,50,0.12)', border: 'rgba(205,127,50,0.3)' },
    { name: 'Silver', emoji: '🥈', price: 4.99, duration: '14 days', credits: 150, color: '#94a3b8', bg: 'rgba(148,163,184,0.12)', border: 'rgba(148,163,184,0.3)' },
    { name: 'Gold',   emoji: '🥇', price: 9.99, duration: '30 days', credits: 350, color: '#facc15', bg: 'rgba(250,204,21,0.12)', border: 'rgba(250,204,21,0.3)' },
];

const REVIEWS = [
    { name: 'Ahmad R.',  role: 'Swing Trader · Jakarta',    rating: 5, avatar: 'AR', text: 'Win rate saya naik dari 52% ke 71% setelah 3 bulan pakai gasstrategy. AI signal-nya akurat banget, terutama untuk XAUUSD dan GBPJPY.', verified: true },
    { name: 'Siti M.',   role: 'Forex Trader · Surabaya',   rating: 5, avatar: 'SM', text: 'Serius ini platform terbaik yang pernah saya coba. Real-time signal, analisis makro, dan calendar event semua dalam satu dashboard. Worth every penny!', verified: true },
    { name: 'Budi K.',   role: 'Day Trader · Bandung',      rating: 5, avatar: 'BK', text: 'Fitur AI Terminal-nya gila sih. Bisa tanya analisa market langsung dan dijawab dengan data real-time. Nggak ada platform lain yang bisa lakuin ini.', verified: true },
    { name: 'Rina P.',   role: 'Prop Trader · Bali',        rating: 5, avatar: 'RP', text: 'Sudah 6 bulan langganan Premium. Konsistensi signal-nya luar biasa. Tim support juga responsif banget. Highly recommended!', verified: true },
    { name: 'Dani F.',   role: 'Crypto & Forex · Medan',    rating: 5, avatar: 'DF', text: 'Platform ini mengubah cara saya trading. Dari yang asal-asalan jadi sistematis. ROI bulan pertama sudah cover biaya langganan setahun.', verified: true },
    { name: 'Yoga S.',   role: 'Scalper · Yogyakarta',      rating: 5, avatar: 'YS', text: 'Multi-timeframe analysis dan entry precision-nya top. Biasanya saya salah timing, sekarang entry selalu di level yang tepat berkat AI Golden AI Strategy.', verified: true },
];

const FAQS = [
    { q: 'Apa itu credit dan bagaimana cara kerjanya?', a: 'Credit adalah satuan penggunaan fitur AI. Setiap fitur memiliki biaya kredit berbeda (1–20cr per request). Credit direset setiap bulan, dan dengan plan Premium/Ultimate kredit yang tersisa bisa di-rollover ke bulan berikutnya.' },
    { q: 'Apakah saya bisa upgrade atau downgrade plan kapan saja?', a: 'Ya, Anda bisa upgrade atau downgrade plan kapan saja. Saat upgrade, perbedaan harga akan dihitung secara prorata. Perubahan berlaku di siklus billing berikutnya untuk downgrade.' },
    { q: 'Platform apa saja yang didukung?', a: 'Golden AI Strategy mendukung Forex (30+ pairs), Crypto (BTC, ETH, dll), Indices (US500, NAS100, FTSE), Commodities (Gold, Oil), dan IDX Saham Indonesia — semua dalam satu platform terintegrasi.' },
    { q: 'Apakah ada garansi uang kembali?', a: 'Ya, kami memberikan garansi uang kembali 7 hari tanpa pertanyaan untuk semua plan baru. Jika Anda tidak puas dalam 7 hari pertama, kami akan mengembalikan pembayaran penuh.' },
    { q: 'Bagaimana cara menghubungkan akun MT5?', a: 'Setelah berlangganan, Anda dapat mengunduh EA (Expert Advisor) eksklusif Golden AI Strategy dari dashboard, kemudian pasang di platform MT5 Anda. Setup selesai dalam kurang dari 5 menit.' },
];

const STATS = [
    { value: '12,400+', label: 'Traders Aktif',    icon: Users },
    { value: '94.2%',   label: 'Akurasi Signal',   icon: Target },
    { value: '21',      label: 'Fitur AI',         icon: Zap },
    { value: '24/7',    label: 'AI Analysis',      icon: Clock },
];

const TRADING_MODES = [
    {
        emoji: '💱',
        name: 'Forex AI',
        tag: 'MT5 · Exness · Gold · Indices',
        desc: 'Sinyal AI untuk XAUUSD, EURUSD, GBPUSD, USDJPY dengan analisis teknikal + fundamental terintegrasi.',
        color: '#f59e0b',
        glowColor: 'rgba(245,158,11,0.25)',
        features: ['Live MT5 Data', 'TA + FA Combined', 'Session Aware', 'Multi-Timeframe'],
        plan: 'Plus+',
    },
    {
        emoji: '₿',
        name: 'Binance AI',
        tag: 'Crypto · Spot · Futures',
        desc: 'Monitor top 20 crypto dengan volume analysis, momentum detection, dan AI signal otomatis.',
        color: '#f7931a',
        glowColor: 'rgba(247,147,26,0.25)',
        features: ['Live Binance Data', 'Volume Analysis', 'Momentum Scanner', 'Top 20 Pairs'],
        plan: 'Plus+',
    },
    {
        emoji: '🔮',
        name: 'Polymarket Signal',
        tag: 'Prediction Markets · YES/NO',
        desc: '4-model weighted consensus untuk prediction markets. 7-tier signal strength: STRONG BUY YES → STRONG BUY NO.',
        color: '#6366f1',
        glowColor: 'rgba(99,102,241,0.25)',
        features: ['4 AI Models', 'Weighted Consensus', 'GAS Event Generator', '7-Tier Signals'],
        plan: 'Ultra',
    },
    {
        emoji: '🎰',
        name: 'Memecoin Signal',
        tag: 'Dexscreener · Anti-Rug',
        desc: 'Scan token baru di Solana, ETH, Base, BSC. Deteksi rug pull otomatis. BUY EARLY / DANGER signals.',
        color: '#9945ff',
        glowColor: 'rgba(153,69,255,0.25)',
        features: ['Anti-Rug Detection', 'Score 0-100', '5 Chains', 'Live Feed'],
        plan: 'Premium+',
    },
];

/* ─────────────────────────── HOOKS ─────────────────────────── */

function useIntersection(ref, options = {}) {
    const [visible, setVisible] = useState(false);
    useEffect(() => {
        const el = ref.current;
        if (!el) return;
        const obs = new IntersectionObserver(([entry]) => {
            if (entry.isIntersecting) { setVisible(true); obs.disconnect(); }
        }, { threshold: 0.12, ...options });
        obs.observe(el);
        return () => obs.disconnect();
    }, []);
    return visible;
}

/* ─────────────────────────── SMALL COMPONENTS ─────────────────────────── */

function FadeIn({ children, delay = 0, className = '' }) {
    const ref = useRef(null);
    const visible = useIntersection(ref);
    return (
        <div
            ref={ref}
            className={className}
            style={{
                opacity: visible ? 1 : 0,
                transform: visible ? 'translateY(0)' : 'translateY(28px)',
                transition: `opacity 0.65s ease ${delay}ms, transform 0.65s ease ${delay}ms`,
            }}
        >
            {children}
        </div>
    );
}

function StarRow({ n = 5 }) {
    return (
        <div style={{ display: 'flex', gap: 2 }}>
            {Array.from({ length: n }).map((_, i) => (
                <Star key={i} size={14} style={{ fill: '#facc15', color: '#facc15' }} />
            ))}
        </div>
    );
}

/* ─────────────────────────── MAIN COMPONENT ─────────────────────────── */

export default function LandingPage() {
    const [theme, setTheme] = useState(() => {
        try { return localStorage.getItem('landing-theme') || 'dark'; } catch { return 'dark'; }
    });
    const [billing, setBilling] = useState('monthly');
    const [menuOpen, setMenuOpen] = useState(false);
    const [faqOpen, setFaqOpen] = useState(null);
    const [scrolled, setScrolled] = useState(false);

    const dark = theme === 'dark';

    useEffect(() => {
        try { localStorage.setItem('landing-theme', theme); } catch {}
        document.documentElement.style.colorScheme = theme;
    }, [theme]);

    useEffect(() => {
        const onScroll = () => setScrolled(window.scrollY > 40);
        window.addEventListener('scroll', onScroll, { passive: true });
        return () => window.removeEventListener('scroll', onScroll);
    }, []);

    const css = {
        '--bg-main':     dark ? '#0a0a0a' : '#f8fafc',
        '--bg-card':     dark ? '#111111' : '#ffffff',
        '--bg-card2':    dark ? '#161616' : '#f1f5f9',
        '--text-primary':dark ? '#f1f5f9' : '#0f172a',
        '--text-muted':  dark ? '#94a3b8' : '#64748b',
        '--border':      dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.08)',
        '--accent':      '#facc15',
    };

    const scrollTo = (id) => {
        setMenuOpen(false);
        const el = document.getElementById(id);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
    };

    /* ── NAVBAR ── */
    const Navbar = (
        <nav style={{
            position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
            background: scrolled
                ? (dark ? 'rgba(10,10,10,0.92)' : 'rgba(248,250,252,0.92)')
                : 'transparent',
            backdropFilter: scrolled ? 'blur(20px)' : 'none',
            borderBottom: scrolled ? `1px solid var(--border)` : '1px solid transparent',
            transition: 'all 0.3s ease',
        }}>
            <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', height: 64, gap: 16 }}>
                {/* Logo */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexShrink: 0 }}>
                    <img src={LOGO} alt="Golden AI Strategy Logo" style={{ width: 36, height: 36, borderRadius: 8, objectFit: 'cover' }} />
                    <span style={{ fontWeight: 800, fontSize: 18, color: 'var(--accent)', letterSpacing: '-0.5px' }}>Golden AI Strategy</span>
                </div>

                {/* Desktop nav */}
                <div style={{ display: 'flex', gap: 6, marginLeft: 32, flex: 1 }} className="nav-desktop">
                    {[
                        { label: 'Home',     href: null,   action: () => window.scrollTo({ top: 0, behavior: 'smooth' }) },
                        { label: 'Features', href: null,   action: () => scrollTo('features') },
                        { label: 'Pricing',  href: 'https://pricing.gasstrategyai.xyz', action: null },
                        { label: 'Docs',     href: 'https://docs.gasstrategyai.xyz',    action: null },
                        { label: 'Blog',     href: 'https://blog.gasstrategyai.xyz',    action: null },
                        { label: 'Review',   href: null,   action: () => scrollTo('reviews') },
                    ].map(({ label, href, action }) => (
                        href
                        ? <a key={label} href={href} target="_blank" rel="noreferrer" style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: 'var(--text-muted)', fontSize: 14, fontWeight: 500,
                            padding: '6px 12px', borderRadius: 8, textDecoration: 'none',
                            transition: 'color 0.2s, background 0.2s',
                          }}
                          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.background = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'; }}
                          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'none'; }}
                          >{label}</a>
                        : <button key={label} onClick={action} style={{
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: 'var(--text-muted)', fontSize: 14, fontWeight: 500,
                            padding: '6px 12px', borderRadius: 8,
                            transition: 'color 0.2s, background 0.2s',
                          }}
                          onMouseEnter={e => { e.currentTarget.style.color = 'var(--text-primary)'; e.currentTarget.style.background = dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)'; }}
                          onMouseLeave={e => { e.currentTarget.style.color = 'var(--text-muted)'; e.currentTarget.style.background = 'none'; }}
                          >{label}</button>
                    ))}
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginLeft: 'auto' }}>
                    {/* Theme toggle */}
                    <button onClick={() => setTheme(dark ? 'light' : 'dark')} style={{
                        background: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
                        border: `1px solid var(--border)`, borderRadius: 8,
                        width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        cursor: 'pointer', color: 'var(--text-muted)', transition: 'all 0.2s',
                    }}>
                        {dark ? <Sun size={16} /> : <Moon size={16} />}
                    </button>

                    {/* Auth buttons — desktop */}
                    <button onClick={() => window.location.href = '/login'} className="nav-desktop" style={{
                        background: 'none', border: `1px solid var(--border)`, borderRadius: 8,
                        padding: '7px 16px', fontSize: 14, fontWeight: 500,
                        color: 'var(--text-primary)', cursor: 'pointer', transition: 'all 0.2s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
                    onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
                    >Masuk</button>

                    <button onClick={() => window.location.href = '/signup'} className="nav-desktop" style={{
                        background: '#facc15', border: 'none', borderRadius: 8,
                        padding: '8px 18px', fontSize: 14, fontWeight: 700,
                        color: '#000', cursor: 'pointer', transition: 'opacity 0.2s',
                    }}
                    onMouseEnter={e => e.currentTarget.style.opacity = '0.88'}
                    onMouseLeave={e => e.currentTarget.style.opacity = '1'}
                    >Daftar Gratis</button>

                    {/* Hamburger */}
                    <button className="nav-mobile-btn" onClick={() => setMenuOpen(!menuOpen)} style={{
                        background: dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.06)',
                        border: `1px solid var(--border)`, borderRadius: 8,
                        width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        cursor: 'pointer', color: 'var(--text-primary)',
                    }}>
                        {menuOpen ? <X size={18} /> : <Menu size={18} />}
                    </button>
                </div>
            </div>

            {/* Mobile menu */}
            {menuOpen && (
                <div style={{
                    background: dark ? '#111' : '#fff',
                    borderTop: `1px solid var(--border)`,
                    padding: '12px 24px 20px',
                }}>
                    {[
                        { label: 'Home',     href: null, action: () => { scrollTo('home'); setMenuOpen(false); } },
                        { label: 'Features', href: null, action: () => { scrollTo('features'); setMenuOpen(false); } },
                        { label: 'Pricing',  href: 'https://pricing.gasstrategyai.xyz', action: null },
                        { label: 'Docs',     href: 'https://docs.gasstrategyai.xyz',    action: null },
                        { label: 'Blog',     href: 'https://blog.gasstrategyai.xyz',    action: null },
                        { label: 'Review',   href: null, action: () => { scrollTo('reviews'); setMenuOpen(false); } },
                    ].map(({ label, href, action }) => (
                        href
                        ? <a key={label} href={href} target="_blank" rel="noreferrer" style={{
                            display: 'block', width: '100%', textAlign: 'left', textDecoration: 'none',
                            color: 'var(--text-muted)', fontSize: 15, padding: '10px 0',
                            borderBottom: `1px solid var(--border)`,
                          }}>{label} ↗</a>
                        : <button key={label} onClick={action} style={{
                            display: 'block', width: '100%', textAlign: 'left',
                            background: 'none', border: 'none', cursor: 'pointer',
                            color: 'var(--text-muted)', fontSize: 15, padding: '10px 0',
                            borderBottom: `1px solid var(--border)`,
                          }}>{label}</button>
                    ))}
                    <div style={{ display: 'flex', gap: 10, marginTop: 16 }}>
                        <button onClick={() => window.location.href = '/login'} style={{
                            flex: 1, background: 'none', border: `1px solid var(--border)`, borderRadius: 8,
                            padding: '10px', fontSize: 14, fontWeight: 600, color: 'var(--text-primary)', cursor: 'pointer',
                        }}>Masuk</button>
                        <button onClick={() => window.location.href = '/signup'} style={{
                            flex: 1, background: '#facc15', border: 'none', borderRadius: 8,
                            padding: '10px', fontSize: 14, fontWeight: 700, color: '#000', cursor: 'pointer',
                        }}>Daftar Gratis</button>
                    </div>
                </div>
            )}
        </nav>
    );

    /* ── HERO ── */
    const Hero = (
        <section style={{
            minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center',
            position: 'relative', overflow: 'hidden',
            background: dark
                ? 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(250,204,21,0.1) 0%, transparent 70%), #0a0a0a'
                : 'radial-gradient(ellipse 80% 60% at 50% 0%, rgba(250,204,21,0.14) 0%, transparent 70%), #f8fafc',
            paddingTop: 80,
            paddingBottom: 60,
        }}>
            {/* Animated grid background */}
            <div style={{
                position: 'absolute', inset: 0, zIndex: 0,
                backgroundImage: `linear-gradient(var(--border) 1px, transparent 1px), linear-gradient(90deg, var(--border) 1px, transparent 1px)`,
                backgroundSize: '60px 60px',
                maskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%)',
                WebkitMaskImage: 'radial-gradient(ellipse 80% 80% at 50% 50%, black 30%, transparent 100%)',
            }} />

            {/* Glow orbs */}
            <div style={{ position: 'absolute', top: '15%', left: '5%', width: 500, height: 500, borderRadius: '50%', background: 'rgba(250,204,21,0.05)', filter: 'blur(100px)', zIndex: 0 }} />
            <div style={{ position: 'absolute', bottom: '10%', right: '5%', width: 420, height: 420, borderRadius: '50%', background: 'rgba(168,85,247,0.06)', filter: 'blur(100px)', zIndex: 0 }} />
            <div style={{ position: 'absolute', top: '40%', right: '20%', width: 280, height: 280, borderRadius: '50%', background: 'rgba(99,102,241,0.04)', filter: 'blur(70px)', zIndex: 0 }} />

            <div style={{ position: 'relative', zIndex: 1, maxWidth: 1200, margin: '0 auto', padding: '0 24px', display: 'grid', gridTemplateColumns: '1fr auto', gap: 60, alignItems: 'center' }} className="hero-grid">
                {/* Left: text content */}
                <div style={{ textAlign: 'left' }}>
                    {/* Top trusted badge */}
                    <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: 8,
                        background: 'rgba(250,204,21,0.12)', border: '1px solid rgba(250,204,21,0.3)',
                        borderRadius: 100, padding: '6px 16px', marginBottom: 24,
                        fontSize: 13, color: '#facc15', fontWeight: 700,
                        animation: 'fadeInDown 0.7s ease forwards',
                    }}>
                        <span>✦</span>
                        Trusted by 12,400+ Active Traders
                    </div>

                    {/* Main headline */}
                    <h1 style={{
                        fontWeight: 900, lineHeight: 1.0, marginBottom: 12, letterSpacing: '-2px',
                        animation: 'fadeInUp 0.8s ease 0.1s both',
                    }}>
                        <div style={{
                            fontSize: 'clamp(40px, 5.5vw, 72px)',
                            color: 'var(--text-primary)',
                            fontFamily: MONO,
                        }}>
                            The #1 AI Trading
                        </div>
                        <div style={{
                            fontSize: 'clamp(50px, 7vw, 96px)',
                            background: 'linear-gradient(135deg, #facc15 0%, #f59e0b 50%, #fb923c 100%)',
                            WebkitBackgroundClip: 'text',
                            WebkitTextFillColor: 'transparent',
                            backgroundClip: 'text',
                            fontFamily: MONO,
                            letterSpacing: '-3px',
                        }}>
                            Super App
                        </div>
                    </h1>

                    {/* Sub tagline */}
                    <div style={{
                        fontSize: 15, color: 'var(--text-muted)', marginBottom: 24,
                        fontFamily: MONO,
                        animation: 'fadeInUp 0.8s ease 0.18s both',
                        display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 8,
                    }}>
                        <span>Multi Market</span>
                        <span style={{ color: '#facc15', fontSize: 10 }}>●</span>
                        <span style={{ color: '#f59e0b' }}>MT5 Forex</span>
                        <span style={{ color: '#facc15', fontSize: 10 }}>●</span>
                        <span style={{ color: '#f7931a' }}>Binance Crypto</span>
                        <span style={{ color: '#facc15', fontSize: 10 }}>●</span>
                        <span style={{ color: '#6366f1' }}>Polymarket</span>
                        <span style={{ color: '#facc15', fontSize: 10 }}>●</span>
                        <span style={{ color: '#9945ff' }}>Memecoin</span>
                    </div>

                    {/* Description */}
                    <p style={{
                        fontSize: 'clamp(15px, 2vw, 18px)', color: 'var(--text-muted)',
                        lineHeight: 1.7, marginBottom: 16, maxWidth: 560,
                        animation: 'fadeInUp 0.8s ease 0.22s both',
                    }}>
                        21 fitur AI + 4 model intelligence{' '}
                        <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>(Claude, GPT, Gemini, Grok)</span>{' '}
                        untuk trading Forex, Crypto, Prediction, dan Memecoin dalam satu platform.
                    </p>

                    {/* NEW agent badge */}
                    <div style={{
                        display: 'inline-flex', alignItems: 'center', gap: 8,
                        background: 'rgba(244,63,94,0.1)', border: '1px solid rgba(244,63,94,0.3)',
                        borderRadius: 100, padding: '6px 16px', marginBottom: 40, fontSize: 12,
                        color: '#fb7185', fontWeight: 700, animation: 'fadeInUp 0.8s ease 0.26s both',
                    }}>
                        🤖 NEW · Feature #19: AI Agent Trading System — Auto Execute · 4 AI Models
                    </div>

                    {/* CTA Buttons */}
                    <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', marginBottom: 56, animation: 'fadeInUp 0.8s ease 0.32s both' }}>
                        <button onClick={() => window.location.href = '/signup'} style={{
                            background: '#facc15', color: '#000', border: 'none',
                            padding: '16px 36px', borderRadius: 16, fontSize: 16, fontWeight: 800,
                            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
                            boxShadow: '0 0 40px rgba(250,204,21,0.4)',
                            transition: 'transform 0.2s, box-shadow 0.2s',
                            letterSpacing: '-0.2px',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 0 70px rgba(250,204,21,0.55)'; }}
                        onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(250,204,21,0.4)'; }}
                        >
                            Mulai Gratis <ArrowRight size={18} />
                        </button>
                        <button onClick={() => window.location.href = '/login'} style={{
                            background: 'transparent',
                            border: '1.5px solid rgba(255,255,255,0.25)', color: dark ? '#f1f5f9' : '#0f172a',
                            padding: '16px 36px', borderRadius: 16, fontSize: 16, fontWeight: 600,
                            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
                            transition: 'border-color 0.2s, color 0.2s',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.borderColor = '#facc15'; e.currentTarget.style.color = '#facc15'; }}
                        onMouseLeave={e => { e.currentTarget.style.borderColor = 'rgba(255,255,255,0.25)'; e.currentTarget.style.color = dark ? '#f1f5f9' : '#0f172a'; }}
                        >
                            Lihat Demo ▶
                        </button>
                        <a href="https://gasstrategyai.xyz/download/GAS-Terminal-v2.0.apk" download style={{ textDecoration: 'none' }}>
                            <button style={{
                                background: 'transparent',
                                border: '1.5px solid rgba(0,229,255,0.5)', color: '#00e5ff',
                                padding: '16px 28px', borderRadius: 16, fontSize: 15, fontWeight: 700,
                                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
                                transition: 'all 0.2s',
                            }}
                            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(0,229,255,0.1)'; e.currentTarget.style.borderColor = '#00e5ff'; }}
                            onMouseLeave={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.borderColor = 'rgba(0,229,255,0.5)'; }}
                            >
                                📱 Download Android
                            </button>
                        </a>
                    </div>
                </div>

                {/* Right: floating terminal card */}
                <div className="hero-terminal-card" style={{
                    flexShrink: 0,
                    animation: 'fadeInRight 0.9s ease 0.4s both',
                }}>
                    <div style={{
                        background: dark ? 'rgba(17,17,17,0.95)' : 'rgba(255,255,255,0.98)',
                        border: `1px solid rgba(250,204,21,0.25)`,
                        borderRadius: 20,
                        padding: '24px',
                        width: 300,
                        boxShadow: '0 0 60px rgba(250,204,21,0.12), 0 24px 64px rgba(0,0,0,0.4)',
                        backdropFilter: 'blur(20px)',
                    }}>
                        {/* Header */}
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20, paddingBottom: 16, borderBottom: `1px solid ${dark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}` }}>
                            <div style={{ width: 36, height: 36, borderRadius: 10, background: 'rgba(250,204,21,0.15)', border: '1px solid rgba(250,204,21,0.3)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Bot size={18} style={{ color: '#facc15' }} />
                            </div>
                            <div>
                                <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--text-primary)', fontFamily: MONO }}>GAS AI Engine</div>
                                <div style={{ fontSize: 11, color: '#4ade80', fontFamily: MONO, display: 'flex', alignItems: 'center', gap: 4 }}>
                                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#4ade80', display: 'inline-block', animation: 'pulse 2s infinite' }} />
                                    4 Models Active
                                </div>
                            </div>
                        </div>

                        {/* Win rate bar */}
                        <div style={{ marginBottom: 18 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 6 }}>
                                <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: MONO }}>Win Rate (30d)</span>
                                <span style={{ fontSize: 12, fontWeight: 800, color: '#4ade80', fontFamily: MONO }}>84%</span>
                            </div>
                            <div style={{ height: 6, borderRadius: 4, background: dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)', overflow: 'hidden' }}>
                                <div style={{ height: '100%', width: '84%', borderRadius: 4, background: 'linear-gradient(90deg, #4ade80, #22c55e)', transition: 'width 1s ease' }} />
                            </div>
                        </div>

                        {/* Pairs */}
                        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 18 }}>
                            {[
                                { pair: 'XAUUSD', price: '3,312.45', change: '+0.82%', up: true },
                                { pair: 'BTC/USDT', price: '67,420', change: '+2.14%', up: true },
                                { pair: 'EUR/USD', price: '1.0847', change: '-0.11%', up: false },
                            ].map(item => (
                                <div key={item.pair} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '8px 10px', borderRadius: 8, background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.03)', border: `1px solid ${dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)'}` }}>
                                    <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', fontFamily: MONO }}>{item.pair}</span>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--text-primary)', fontFamily: MONO }}>${item.price}</div>
                                        <div style={{ fontSize: 10, color: item.up ? '#4ade80' : '#f87171', fontFamily: MONO }}>{item.up ? '↑' : '↓'} {item.change}</div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Signal badge */}
                        <div style={{
                            background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.3)',
                            borderRadius: 10, padding: '10px 14px',
                            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                        }}>
                            <span style={{ fontSize: 11, color: 'var(--text-muted)', fontFamily: MONO }}>AI Signal</span>
                            <span style={{ fontSize: 12, fontWeight: 800, color: '#4ade80', fontFamily: MONO }}>STRONG BUY ↑</span>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );

    /* ── STATS ── */
    const StatsSection = (
        <section style={{
            padding: '80px 24px',
            background: dark
                ? 'linear-gradient(180deg, #0a0a0a 0%, #0d0d0d 100%)'
                : 'linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%)',
            borderTop: `1px solid ${dark ? 'rgba(250,204,21,0.08)' : 'rgba(250,204,21,0.15)'}`,
            borderBottom: `1px solid ${dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.06)'}`,
        }}>
            <div style={{ maxWidth: 960, margin: '0 auto' }}>
                <FadeIn>
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 24 }} className="stats-grid">
                        {STATS.map((s, i) => {
                            const Icon = s.icon;
                            return (
                                <div key={i} style={{
                                    background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(255,255,255,0.8)',
                                    border: `1px solid ${dark ? 'rgba(250,204,21,0.12)' : 'rgba(250,204,21,0.2)'}`,
                                    borderRadius: 20, padding: '32px 20px', textAlign: 'center',
                                    transition: 'transform 0.2s, border-color 0.2s, box-shadow 0.2s',
                                    cursor: 'default',
                                }}
                                onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.borderColor = 'rgba(250,204,21,0.35)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(250,204,21,0.08)'; }}
                                onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.borderColor = dark ? 'rgba(250,204,21,0.12)' : 'rgba(250,204,21,0.2)'; e.currentTarget.style.boxShadow = 'none'; }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 14 }}>
                                        <div style={{ width: 44, height: 44, borderRadius: 12, background: 'rgba(250,204,21,0.12)', border: '1px solid rgba(250,204,21,0.25)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                            <Icon size={20} style={{ color: '#facc15' }} />
                                        </div>
                                    </div>
                                    <div style={{ fontSize: 'clamp(28px, 3.5vw, 40px)', fontWeight: 900, color: '#facc15', fontFamily: MONO, letterSpacing: '-1px', lineHeight: 1.1 }}>{s.value}</div>
                                    <div style={{ fontSize: 13, color: 'var(--text-muted)', marginTop: 8, fontWeight: 500 }}>{s.label}</div>
                                </div>
                            );
                        })}
                    </div>
                </FadeIn>
            </div>
        </section>
    );

    /* ── FEATURES ── */
    const Features = (
        <section id="features" style={{ padding: '112px 24px', background: dark ? '#0d0d0d' : '#f1f5f9' }}>
            <div style={{ maxWidth: 1280, margin: '0 auto' }}>
                <FadeIn>
                    <div style={{ textAlign: 'center', marginBottom: 72 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.25)', borderRadius: 100, padding: '6px 16px', marginBottom: 20, fontSize: 13, color: '#facc15', fontWeight: 700 }}>
                            🛠️ 21 AI Features · 4 Market Types
                        </div>
                        <h2 style={{ fontSize: 'clamp(30px, 4.5vw, 52px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1.5px', marginBottom: 18, lineHeight: 1.1 }}>
                            Semua yang Kamu Butuhkan untuk{' '}
                            <span style={{ color: '#facc15' }}>Trading Profesional</span>
                        </h2>
                        <p style={{ color: 'var(--text-muted)', fontSize: 18, maxWidth: 580, margin: '0 auto', lineHeight: 1.65 }}>
                            Dari analisis teknikal hingga AI Agent Trading otomatis — semua tersedia dalam ekosistem AI yang terintegrasi penuh.
                        </p>
                    </div>
                </FadeIn>

                {FEATURE_GROUPS.map((group, gi) => (
                    <div key={gi} style={{ marginBottom: 64 }}>
                        <FadeIn delay={gi * 60}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 28 }}>
                                <div style={{ height: 2, flex: 1, background: `linear-gradient(90deg, ${group.accent}, transparent)` }} />
                                <h3 style={{ fontSize: 18, fontWeight: 700, color: 'var(--text-primary)', whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 8 }}>
                                    {group.category}
                                    {group.isNew && <span style={{ fontSize: 10, fontWeight: 800, color: '#fb7185', background: 'rgba(244,63,94,0.12)', border: '1px solid rgba(244,63,94,0.3)', borderRadius: 6, padding: '2px 8px', letterSpacing: '0.5px' }}>NEW</span>}
                                </h3>
                                <div style={{ height: 2, flex: 1, background: `linear-gradient(270deg, ${group.accent}, transparent)` }} />
                            </div>
                        </FadeIn>

                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(290px, 1fr))', gap: 18 }}>
                            {group.features.map((feat, fi) => {
                                const Icon = feat.icon;
                                const badge = PLAN_BADGE[feat.planKey];
                                return (
                                    <FadeIn key={fi} delay={gi * 40 + fi * 60}>
                                        <div style={{
                                            background: 'var(--bg-card)',
                                            border: `1px solid var(--border)`,
                                            borderRadius: 16, padding: '22px 22px 20px',
                                            transition: 'border-color 0.25s, transform 0.2s, box-shadow 0.25s',
                                            cursor: 'default',
                                            height: '100%',
                                        }}
                                        onMouseEnter={e => {
                                            e.currentTarget.style.borderColor = group.borderAccent;
                                            e.currentTarget.style.transform = 'translateY(-4px)';
                                            e.currentTarget.style.boxShadow = `0 12px 48px ${group.bgAccent}`;
                                        }}
                                        onMouseLeave={e => {
                                            e.currentTarget.style.borderColor = 'var(--border)';
                                            e.currentTarget.style.transform = 'translateY(0)';
                                            e.currentTarget.style.boxShadow = 'none';
                                        }}
                                        >
                                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                                                <div style={{ width: 44, height: 44, borderRadius: 12, background: group.bgAccent, display: 'flex', alignItems: 'center', justifyContent: 'center', border: `1px solid ${group.borderAccent}` }}>
                                                    <Icon size={20} style={{ color: group.accent }} />
                                                </div>
                                                <div style={{ display: 'flex', gap: 6, alignItems: 'center', flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                                                    {feat.credits > 0 && (
                                                        <span style={{ fontSize: 11, fontWeight: 700, color: '#facc15', background: 'rgba(250,204,21,0.12)', border: '1px solid rgba(250,204,21,0.25)', borderRadius: 6, padding: '2px 8px', fontFamily: MONO }}>
                                                            {feat.credits}cr
                                                        </span>
                                                    )}
                                                    <span style={{ fontSize: 11, fontWeight: 700, color: badge.color, background: badge.bg, border: `1px solid ${badge.border}`, borderRadius: 6, padding: '2px 8px' }}>
                                                        {badge.label}
                                                    </span>
                                                </div>
                                            </div>
                                            <div style={{ fontWeight: 700, fontSize: 15, color: 'var(--text-primary)', marginBottom: 8 }}>{feat.name}</div>
                                            <div style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.6, marginBottom: 16 }}>{feat.desc}</div>
                                            <a href="/signup" style={{ fontSize: 12, color: group.accent, fontWeight: 600, textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: 4, transition: 'gap 0.2s' }}
                                            onMouseEnter={e => e.currentTarget.style.gap = '8px'}
                                            onMouseLeave={e => e.currentTarget.style.gap = '4px'}
                                            >
                                                Coba Sekarang <ChevronRight size={13} />
                                            </a>
                                        </div>
                                    </FadeIn>
                                );
                            })}
                        </div>
                    </div>
                ))}

                {/* View all CTA */}
                <FadeIn>
                    <div style={{ textAlign: 'center', marginTop: 16 }}>
                        <button onClick={() => window.location.href = '/signup'} style={{
                            background: 'rgba(250,204,21,0.08)', border: '1.5px solid rgba(250,204,21,0.3)',
                            color: '#facc15', borderRadius: 12, padding: '13px 32px',
                            fontSize: 15, fontWeight: 700, cursor: 'pointer',
                            display: 'inline-flex', alignItems: 'center', gap: 8,
                            transition: 'background 0.2s, box-shadow 0.2s',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = 'rgba(250,204,21,0.15)'; e.currentTarget.style.boxShadow = '0 0 30px rgba(250,204,21,0.15)'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'rgba(250,204,21,0.08)'; e.currentTarget.style.boxShadow = 'none'; }}
                        >
                            Lihat Semua 21 Fitur AI <ArrowRight size={16} />
                        </button>
                    </div>
                </FadeIn>
            </div>
        </section>
    );

    /* ── 4 TRADING MODES ── */
    const TradingModes = (
        <section style={{
            padding: '112px 24px',
            background: dark
                ? 'linear-gradient(180deg, #080808 0%, #0a0a0a 100%)'
                : 'linear-gradient(180deg, #ffffff 0%, #f8fafc 100%)',
        }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
                <FadeIn>
                    <div style={{ textAlign: 'center', marginBottom: 72 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(99,102,241,0.1)', border: '1px solid rgba(99,102,241,0.25)', borderRadius: 100, padding: '6px 16px', marginBottom: 20, fontSize: 13, color: '#818cf8', fontWeight: 700 }}>
                            🌐 Multi Market Platform
                        </div>
                        <h2 style={{ fontSize: 'clamp(30px, 4.5vw, 52px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1.5px', marginBottom: 18, lineHeight: 1.1 }}>
                            4 Cara Trading,{' '}
                            <span style={{ color: '#facc15' }}>1 Platform</span>
                        </h2>
                        <p style={{ color: 'var(--text-muted)', fontSize: 17, maxWidth: 600, margin: '0 auto', lineHeight: 1.65 }}>
                            Setiap market punya logika AI yang berbeda — dioptimasi khusus untuk Forex, Crypto, Prediction, dan Memecoin.
                        </p>
                    </div>
                </FadeIn>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 24 }} className="modes-grid">
                    {TRADING_MODES.map((mode, i) => (
                        <FadeIn key={i} delay={i * 80}>
                            <div style={{
                                background: dark ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.9)',
                                border: `1px solid ${dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)'}`,
                                borderRadius: 20, padding: '32px',
                                transition: 'transform 0.25s, border-color 0.25s, box-shadow 0.25s',
                                cursor: 'default', height: '100%',
                            }}
                            onMouseEnter={e => {
                                e.currentTarget.style.transform = 'translateY(-5px)';
                                e.currentTarget.style.borderColor = mode.color + '55';
                                e.currentTarget.style.boxShadow = `0 16px 64px ${mode.glowColor}`;
                            }}
                            onMouseLeave={e => {
                                e.currentTarget.style.transform = 'translateY(0)';
                                e.currentTarget.style.borderColor = dark ? 'rgba(255,255,255,0.07)' : 'rgba(0,0,0,0.07)';
                                e.currentTarget.style.boxShadow = 'none';
                            }}
                            >
                                {/* Header */}
                                <div style={{ display: 'flex', alignItems: 'flex-start', gap: 16, marginBottom: 20 }}>
                                    <div style={{ fontSize: 40, lineHeight: 1, flexShrink: 0 }}>{mode.emoji}</div>
                                    <div>
                                        <div style={{ fontSize: 22, fontWeight: 900, color: 'var(--text-primary)', fontFamily: MONO, letterSpacing: '-0.5px', marginBottom: 6 }}>{mode.name}</div>
                                        <span style={{
                                            fontSize: 11, fontWeight: 700, color: mode.color,
                                            background: mode.color + '18',
                                            border: `1px solid ${mode.color}40`,
                                            borderRadius: 6, padding: '3px 10px',
                                        }}>{mode.tag}</span>
                                    </div>
                                </div>

                                {/* Description */}
                                <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.7, marginBottom: 20 }}>{mode.desc}</p>

                                {/* Feature chips */}
                                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 20 }}>
                                    {mode.features.map((f, fi) => (
                                        <span key={fi} style={{
                                            fontSize: 11, fontWeight: 600, color: 'var(--text-muted)',
                                            background: dark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.05)',
                                            border: `1px solid var(--border)`,
                                            borderRadius: 6, padding: '4px 10px',
                                            display: 'flex', alignItems: 'center', gap: 5,
                                        }}>
                                            <Check size={10} style={{ color: mode.color }} /> {f}
                                        </span>
                                    ))}
                                </div>

                                {/* Plan badge */}
                                <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                                    <span style={{
                                        fontSize: 11, fontWeight: 800, color: mode.color,
                                        background: mode.color + '15',
                                        border: `1px solid ${mode.color}35`,
                                        borderRadius: 8, padding: '4px 12px',
                                    }}>
                                        {mode.plan} plan
                                    </span>
                                </div>
                            </div>
                        </FadeIn>
                    ))}
                </div>
            </div>
        </section>
    );

    /* ── PRICING ── */
    const Pricing = (
        <section id="pricing" style={{ background: 'var(--bg-main)', paddingTop: 16, paddingBottom: 16 }}>
            <FadeIn>
                <div style={{ textAlign: 'center', padding: '64px 24px 0' }}>
                    <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.25)', borderRadius: 100, padding: '6px 16px', marginBottom: 20, fontSize: 13, color: '#facc15', fontWeight: 700 }}>
                        💳 Simple Transparent Pricing
                    </div>
                    <h2 style={{ fontSize: 'clamp(28px, 4vw, 50px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1.5px', marginBottom: 16, lineHeight: 1.1 }}>
                        Pilih Plan yang{' '}
                        <span style={{ color: '#facc15' }}>Sesuai</span>
                    </h2>
                    <p style={{ color: 'var(--text-muted)', fontSize: 17, maxWidth: 500, margin: '0 auto', lineHeight: 1.65 }}>
                        Mulai gratis, upgrade kapan saja. Tidak ada biaya tersembunyi.
                    </p>
                </div>
            </FadeIn>
            <PricingView publicMode={true} />
        </section>
    );

    /* ── REVIEWS ── */
    const Reviews = (
        <section id="reviews" style={{ padding: '112px 24px', background: dark ? '#0d0d0d' : '#f1f5f9' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
                <FadeIn>
                    <div style={{ textAlign: 'center', marginBottom: 64 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.25)', borderRadius: 100, padding: '6px 16px', marginBottom: 20, fontSize: 13, color: '#facc15', fontWeight: 700 }}>
                            <Star size={13} style={{ fill: '#facc15' }} /> Testimoni Trader
                        </div>
                        <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1.2px', marginBottom: 16, lineHeight: 1.1 }}>
                            Dipercaya{' '}
                            <span style={{ color: '#facc15', fontFamily: MONO }}>12,400+</span>{' '}
                            Trader Aktif
                        </h2>
                        <p style={{ color: 'var(--text-muted)', fontSize: 17, maxWidth: 480, margin: '0 auto', lineHeight: 1.65 }}>
                            Bergabung dengan komunitas trader yang sudah membuktikan hasilnya.
                        </p>
                    </div>
                </FadeIn>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(330px, 1fr))', gap: 24 }}>
                    {REVIEWS.map((r, ri) => (
                        <FadeIn key={ri} delay={ri * 60}>
                            <div style={{
                                background: 'var(--bg-card)', border: `1px solid var(--border)`,
                                borderRadius: 18, padding: '28px',
                                transition: 'border-color 0.2s, transform 0.2s, box-shadow 0.2s',
                                height: '100%',
                            }}
                            onMouseEnter={e => { e.currentTarget.style.borderColor = 'rgba(250,204,21,0.25)'; e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(250,204,21,0.07)'; }}
                            onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border)'; e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = 'none'; }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16, alignItems: 'flex-start' }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                        <div style={{ width: 46, height: 46, borderRadius: '50%', background: 'linear-gradient(135deg, #facc15, #f59e0b)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: 14, color: '#000', flexShrink: 0 }}>
                                            {r.avatar}
                                        </div>
                                        <div>
                                            <div style={{ fontWeight: 700, fontSize: 14, color: 'var(--text-primary)' }}>{r.name}</div>
                                            <div style={{ fontSize: 12, color: 'var(--text-muted)', marginTop: 2 }}>{r.role}</div>
                                        </div>
                                    </div>
                                    {r.verified && (
                                        <div style={{ fontSize: 11, color: '#4ade80', background: 'rgba(74,222,128,0.1)', border: '1px solid rgba(74,222,128,0.2)', borderRadius: 6, padding: '2px 8px', fontWeight: 600, flexShrink: 0 }}>
                                            ✓ Verified
                                        </div>
                                    )}
                                </div>
                                <StarRow n={r.rating} />
                                <p style={{ fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.7, marginTop: 14 }}>"{r.text}"</p>
                            </div>
                        </FadeIn>
                    ))}
                </div>
            </div>
        </section>
    );

    /* ── FAQ ── */
    const FAQ = (
        <section style={{ padding: '96px 24px', background: dark ? 'var(--bg-main)' : '#ffffff' }}>
            <div style={{ maxWidth: 800, margin: '0 auto' }}>
                <FadeIn>
                    <div style={{ textAlign: 'center', marginBottom: 60 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(250,204,21,0.1)', border: '1px solid rgba(250,204,21,0.25)', borderRadius: 100, padding: '6px 16px', marginBottom: 20, fontSize: 13, color: '#facc15', fontWeight: 700 }}>
                            <BookOpen size={13} /> FAQ
                        </div>
                        <h2 style={{ fontSize: 'clamp(26px, 3.5vw, 42px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1px', marginBottom: 14 }}>
                            Pertanyaan yang Sering Ditanyakan
                        </h2>
                    </div>
                </FadeIn>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {FAQS.map((faq, fi) => (
                        <FadeIn key={fi} delay={fi * 60}>
                            <div style={{ background: 'var(--bg-card)', border: `1px solid ${faqOpen === fi ? 'rgba(250,204,21,0.35)' : 'var(--border)'}`, borderRadius: 14, overflow: 'hidden', transition: 'border-color 0.2s' }}>
                                <button onClick={() => setFaqOpen(faqOpen === fi ? null : fi)} style={{
                                    width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                                    padding: '20px 22px', background: 'none', border: 'none',
                                    cursor: 'pointer', color: 'var(--text-primary)', fontSize: 15, fontWeight: 600,
                                    textAlign: 'left', gap: 12,
                                }}>
                                    {faq.q}
                                    <ChevronDown size={18} style={{ flexShrink: 0, color: 'var(--text-muted)', transform: faqOpen === fi ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.25s' }} />
                                </button>
                                {faqOpen === fi && (
                                    <div style={{ padding: '0 22px 20px', fontSize: 14, color: 'var(--text-muted)', lineHeight: 1.75, borderTop: `1px solid var(--border)`, paddingTop: 16 }}>
                                        {faq.a}
                                    </div>
                                )}
                            </div>
                        </FadeIn>
                    ))}
                </div>
            </div>
        </section>
    );

    /* ── FINAL CTA SECTION ── */
    const FinalCTA = (
        <section style={{
            padding: '100px 24px',
            background: dark
                ? 'radial-gradient(ellipse 70% 70% at 50% 50%, rgba(250,204,21,0.07) 0%, rgba(168,85,247,0.04) 50%, transparent 100%), #080808'
                : 'radial-gradient(ellipse 70% 70% at 50% 50%, rgba(250,204,21,0.12) 0%, rgba(168,85,247,0.05) 50%, transparent 100%), #f8fafc',
        }}>
            <div style={{ maxWidth: 760, margin: '0 auto', textAlign: 'center' }}>
                <FadeIn>
                    <div style={{
                        background: dark ? 'rgba(255,255,255,0.02)' : 'rgba(255,255,255,0.85)',
                        border: `1px solid ${dark ? 'rgba(250,204,21,0.18)' : 'rgba(250,204,21,0.3)'}`,
                        borderRadius: 28, padding: '64px 48px',
                        boxShadow: dark ? '0 0 80px rgba(250,204,21,0.06)' : '0 8px 60px rgba(250,204,21,0.1)',
                    }}>
                        <div style={{ fontSize: 40, marginBottom: 24 }}>⚡</div>
                        <h2 style={{ fontSize: 'clamp(28px, 4vw, 48px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1.5px', marginBottom: 18, lineHeight: 1.1 }}>
                            Siap Trading Lebih <span style={{ color: '#facc15' }}>Cerdas?</span>
                        </h2>
                        <p style={{ fontSize: 17, color: 'var(--text-muted)', lineHeight: 1.65, marginBottom: 40, maxWidth: 480, margin: '0 auto 40px' }}>
                            Join{' '}
                            <span style={{ color: '#facc15', fontFamily: MONO, fontWeight: 800 }}>12,400+</span>{' '}
                            trader yang sudah profit dengan Golden AI Strategy. Mulai gratis, tidak perlu kartu kredit.
                        </p>
                        <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
                            <button onClick={() => window.location.href = '/signup'} style={{
                                background: '#facc15', color: '#000', border: 'none',
                                padding: '16px 40px', borderRadius: 16, fontSize: 16, fontWeight: 800,
                                cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 10,
                                boxShadow: '0 0 40px rgba(250,204,21,0.4)',
                                transition: 'transform 0.2s, box-shadow 0.2s',
                            }}
                            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 0 70px rgba(250,204,21,0.55)'; }}
                            onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = '0 0 40px rgba(250,204,21,0.4)'; }}
                            >
                                Mulai Gratis Sekarang <ArrowRight size={18} />
                            </button>
                            <button onClick={() => window.open('https://t.me/gasstrategy', '_blank')} style={{
                                background: 'transparent',
                                border: `1.5px solid ${dark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.15)'}`,
                                color: 'var(--text-primary)',
                                padding: '16px 32px', borderRadius: 16, fontSize: 16, fontWeight: 600,
                                cursor: 'pointer',
                                transition: 'border-color 0.2s, color 0.2s',
                            }}
                            onMouseEnter={e => { e.currentTarget.style.borderColor = '#facc15'; e.currentTarget.style.color = '#facc15'; }}
                            onMouseLeave={e => { e.currentTarget.style.borderColor = dark ? 'rgba(255,255,255,0.2)' : 'rgba(0,0,0,0.15)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
                            >
                                Hubungi Kami
                            </button>
                        </div>
                    </div>
                </FadeIn>
            </div>
        </section>
    );

    /* ── DOWNLOAD PAGE ── */
    const PLATFORM_CARDS = [
        {
            key: 'apkmirror',
            available: true,
            href: 'https://gasstrategyai.xyz/download/GAS-Terminal-v2.0.apk',
            download: true,
            logo: (
                <svg viewBox="0 0 48 48" width="44" height="44" fill="none">
                    <rect width="48" height="48" rx="12" fill="#1a73e8"/>
                    <path d="M24 8L8 36h32L24 8z" fill="white" opacity="0.9"/>
                    <circle cx="24" cy="34" r="4" fill="#facc15"/>
                    <path d="M18 28l6-12 6 12" stroke="white" strokeWidth="2" fill="none" strokeLinejoin="round"/>
                </svg>
            ),
            name: 'APKMirror',
            subtitle: 'Direct APK Download',
            badge: 'AVAILABLE',
            badgeColor: '#00e676',
            badgeBg: 'rgba(0,230,118,0.12)',
            borderColor: 'rgba(0,230,118,0.4)',
            glowColor: 'rgba(0,230,118,0.2)',
            meta: 'v2.0.0  •  25 MB  •  Android 7+',
            metaColor: '#00e676',
        },
        {
            key: 'playstore',
            available: false,
            logo: (
                <svg viewBox="0 0 48 48" width="44" height="44" fill="none">
                    <rect width="48" height="48" rx="12" fill="#0f0f0f"/>
                    <path d="M12 10l26 14-26 14V10z" fill="url(#ps_grad)"/>
                    <defs>
                        <linearGradient id="ps_grad" x1="12" y1="10" x2="38" y2="38" gradientUnits="userSpaceOnUse">
                            <stop stopColor="#00d4aa"/>
                            <stop offset="0.5" stopColor="#00bcd4"/>
                            <stop offset="1" stopColor="#4caf50"/>
                        </linearGradient>
                    </defs>
                </svg>
            ),
            name: 'Google Play',
            subtitle: 'Play Store',
            badge: 'COMING SOON',
            badgeColor: '#888',
            badgeBg: 'rgba(255,255,255,0.06)',
            borderColor: 'rgba(255,255,255,0.08)',
            glowColor: 'transparent',
            meta: 'Under review',
            metaColor: '#555',
        },
        {
            key: 'appstore',
            available: false,
            logo: (
                <svg viewBox="0 0 48 48" width="44" height="44" fill="none">
                    <rect width="48" height="48" rx="12" fill="#1c1c1e"/>
                    <path d="M24 10c-1.5 0-3.5 1.8-3.5 4 0 .2 0 .4.02.6H17c-1.5 0-2.5 1-2.5 2.5v14c0 1.5 1 2.5 2.5 2.5h14c1.5 0 2.5-1 2.5-2.5v-14c0-1.5-1-2.5-2.5-2.5h-3.52c.02-.2.02-.4.02-.6 0-2.2-2-4-3.5-4z" fill="white" opacity="0.15"/>
                    <path d="M30 22l-8.5 5V17L30 22z" fill="white" opacity="0.9"/>
                    <circle cx="24" cy="10.5" r="1.5" fill="white" opacity="0.5"/>
                </svg>
            ),
            name: 'App Store',
            subtitle: 'iOS / iPadOS',
            badge: 'COMING SOON',
            badgeColor: '#888',
            badgeBg: 'rgba(255,255,255,0.06)',
            borderColor: 'rgba(255,255,255,0.08)',
            glowColor: 'transparent',
            meta: 'In development',
            metaColor: '#555',
        },
        {
            key: 'windows',
            available: false,
            logo: (
                <svg viewBox="0 0 48 48" width="44" height="44" fill="none">
                    <rect width="48" height="48" rx="12" fill="#0078d4" opacity="0.15"/>
                    <rect x="10" y="10" width="12" height="12" rx="1.5" fill="#0078d4"/>
                    <rect x="26" y="10" width="12" height="12" rx="1.5" fill="#0078d4"/>
                    <rect x="10" y="26" width="12" height="12" rx="1.5" fill="#0078d4"/>
                    <rect x="26" y="26" width="12" height="12" rx="1.5" fill="#0078d4"/>
                </svg>
            ),
            name: 'Windows',
            subtitle: 'Desktop App',
            badge: 'COMING SOON',
            badgeColor: '#888',
            badgeBg: 'rgba(255,255,255,0.06)',
            borderColor: 'rgba(255,255,255,0.08)',
            glowColor: 'transparent',
            meta: 'Windows 10/11',
            metaColor: '#555',
        },
        {
            key: 'linux',
            available: false,
            logo: (
                <svg viewBox="0 0 48 48" width="44" height="44" fill="none">
                    <rect width="48" height="48" rx="12" fill="#f7941d" opacity="0.12"/>
                    <ellipse cx="24" cy="18" rx="8" ry="10" fill="#f7941d" opacity="0.7"/>
                    <circle cx="20" cy="16" r="2" fill="white"/>
                    <circle cx="28" cy="16" r="2" fill="white"/>
                    <path d="M17 28c0 0 3-4 7-4s7 4 7 4" stroke="#f7941d" strokeWidth="2" fill="none" strokeLinecap="round"/>
                    <path d="M15 34l4-6M33 34l-4-6" stroke="#f7941d" strokeWidth="2" strokeLinecap="round"/>
                </svg>
            ),
            name: 'Linux',
            subtitle: 'Desktop App',
            badge: 'COMING SOON',
            badgeColor: '#888',
            badgeBg: 'rgba(255,255,255,0.06)',
            borderColor: 'rgba(255,255,255,0.08)',
            glowColor: 'transparent',
            meta: 'Ubuntu / Debian',
            metaColor: '#555',
        },
        {
            key: 'web',
            available: true,
            href: '/dashboard',
            download: false,
            logo: (
                <svg viewBox="0 0 48 48" width="44" height="44" fill="none">
                    <rect width="48" height="48" rx="12" fill="rgba(250,204,21,0.12)"/>
                    <circle cx="24" cy="24" r="12" stroke="#facc15" strokeWidth="2.5" fill="none"/>
                    <ellipse cx="24" cy="24" rx="6" ry="12" stroke="#facc15" strokeWidth="2" fill="none"/>
                    <line x1="12" y1="24" x2="36" y2="24" stroke="#facc15" strokeWidth="2"/>
                    <line x1="14" y1="18" x2="34" y2="18" stroke="#facc15" strokeWidth="1.5" opacity="0.5"/>
                    <line x1="14" y1="30" x2="34" y2="30" stroke="#facc15" strokeWidth="1.5" opacity="0.5"/>
                </svg>
            ),
            name: 'Web App',
            subtitle: 'Browser Terminal',
            badge: 'AVAILABLE',
            badgeColor: '#facc15',
            badgeBg: 'rgba(250,204,21,0.12)',
            borderColor: 'rgba(250,204,21,0.35)',
            glowColor: 'rgba(250,204,21,0.15)',
            meta: 'No install needed',
            metaColor: '#facc15',
        },
    ];

    const MobileDownload = (
        <section id="download" style={{
            padding: '100px 24px',
            background: dark
                ? 'radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,229,255,0.05) 0%, transparent 60%), #080808'
                : 'radial-gradient(ellipse 80% 50% at 50% 0%, rgba(0,229,255,0.07) 0%, transparent 60%), #f0f9ff',
            borderTop: `1px solid ${dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.07)'}`,
        }}>
            <div style={{ maxWidth: 1100, margin: '0 auto' }}>
                <FadeIn>
                    {/* Header */}
                    <div style={{ textAlign: 'center', marginBottom: 64 }}>
                        <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(0,229,255,0.1)', border: '1px solid rgba(0,229,255,0.25)', borderRadius: 999, padding: '6px 18px', marginBottom: 22 }}>
                            <span style={{ fontSize: 15 }}>📲</span>
                            <span style={{ fontSize: 12, fontWeight: 700, color: '#00e5ff', fontFamily: MONO, letterSpacing: '0.08em' }}>DOWNLOAD GAS TERMINAL</span>
                        </div>
                        <h2 style={{ fontSize: 'clamp(28px, 4.5vw, 52px)', fontWeight: 900, color: 'var(--text-primary)', letterSpacing: '-1.5px', marginBottom: 16, lineHeight: 1.08 }}>
                            Tersedia di Semua <span style={{ color: '#facc15' }}>Platform</span>
                        </h2>
                        <p style={{ fontSize: 16, color: 'var(--text-muted)', lineHeight: 1.65, maxWidth: 540, margin: '0 auto' }}>
                            Akses GAS Terminal dari mana saja — Android, iOS, Windows, Linux, atau langsung dari browser. Trading tanpa batas.
                        </p>
                    </div>

                    {/* Platform Cards Grid */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
                        gap: 20,
                        marginBottom: 56,
                    }}>
                        {PLATFORM_CARDS.map(p => {
                            const card = (
                                <div style={{
                                    background: dark ? 'rgba(255,255,255,0.03)' : '#fff',
                                    border: `1.5px solid ${p.borderColor}`,
                                    borderRadius: 20,
                                    padding: '28px 24px',
                                    display: 'flex', flexDirection: 'column', gap: 16,
                                    position: 'relative', overflow: 'hidden',
                                    transition: 'all 0.25s',
                                    cursor: p.available ? 'pointer' : 'not-allowed',
                                    opacity: p.available ? 1 : 0.55,
                                    boxShadow: p.available ? `0 0 40px ${p.glowColor}` : 'none',
                                }}
                                onMouseEnter={e => { if (p.available) { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.boxShadow = `0 8px 60px ${p.glowColor}`; }}}
                                onMouseLeave={e => { e.currentTarget.style.transform = 'translateY(0)'; e.currentTarget.style.boxShadow = p.available ? `0 0 40px ${p.glowColor}` : 'none'; }}
                                >
                                    {/* Glow blob */}
                                    {p.available && <div style={{ position: 'absolute', top: -20, right: -20, width: 100, height: 100, borderRadius: '50%', background: p.glowColor, filter: 'blur(30px)', pointerEvents: 'none' }}/>}

                                    {/* Top row: logo + badge */}
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        {p.logo}
                                        <div style={{
                                            fontSize: 10, fontWeight: 800, fontFamily: MONO, letterSpacing: '0.06em',
                                            color: p.badgeColor, background: p.badgeBg,
                                            border: `1px solid ${p.borderColor}`,
                                            borderRadius: 999, padding: '4px 10px',
                                        }}>{p.badge}</div>
                                    </div>

                                    {/* Name */}
                                    <div>
                                        <div style={{ fontSize: 20, fontWeight: 800, color: 'var(--text-primary)', marginBottom: 3 }}>{p.name}</div>
                                        <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>{p.subtitle}</div>
                                    </div>

                                    {/* Meta */}
                                    <div style={{ fontSize: 12, fontFamily: MONO, color: p.metaColor, marginTop: 'auto' }}>{p.meta}</div>

                                    {/* CTA */}
                                    {p.available && (
                                        <div style={{
                                            display: 'flex', alignItems: 'center', gap: 8,
                                            background: p.key === 'web' ? 'rgba(250,204,21,0.1)' : 'rgba(0,230,118,0.1)',
                                            border: `1px solid ${p.key === 'web' ? 'rgba(250,204,21,0.3)' : 'rgba(0,230,118,0.3)'}`,
                                            borderRadius: 10, padding: '10px 14px',
                                        }}>
                                            <span style={{ fontSize: 14 }}>{p.key === 'web' ? '🌐' : '⬇️'}</span>
                                            <span style={{ fontSize: 13, fontWeight: 700, color: p.key === 'web' ? '#facc15' : '#00e676' }}>
                                                {p.key === 'web' ? 'Buka Web App' : 'Download Sekarang'}
                                            </span>
                                            <ArrowRight size={14} color={p.key === 'web' ? '#facc15' : '#00e676'} style={{ marginLeft: 'auto' }} />
                                        </div>
                                    )}
                                    {!p.available && (
                                        <div style={{
                                            display: 'flex', alignItems: 'center', gap: 8,
                                            background: 'rgba(255,255,255,0.04)',
                                            borderRadius: 10, padding: '10px 14px',
                                        }}>
                                            <Clock size={14} color="#555" />
                                            <span style={{ fontSize: 13, color: '#555' }}>Segera Hadir</span>
                                        </div>
                                    )}
                                </div>
                            );
                            return p.available
                                ? <a key={p.key} href={p.href} download={p.download || undefined} style={{ textDecoration: 'none' }}>{card}</a>
                                : <div key={p.key}>{card}</div>;
                        })}
                    </div>

                    {/* Install Instructions */}
                    <div style={{
                        background: dark ? 'rgba(255,255,255,0.03)' : 'rgba(0,0,0,0.04)',
                        border: `1px solid ${dark ? 'rgba(0,230,118,0.15)' : 'rgba(0,230,118,0.25)'}`,
                        borderRadius: 20, padding: '32px 36px',
                        maxWidth: 680, margin: '0 auto',
                        display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24,
                    }}>
                        <div>
                            <div style={{ fontSize: 14, fontWeight: 800, color: '#00e676', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span>📋</span> Cara Install APK Android
                            </div>
                            {[
                                'Download APK via tombol APKMirror',
                                'Settings → Security → Install Unknown Apps',
                                'Buka file APK → tap Install',
                                'Login akun GAS → mulai trading!',
                            ].map((step, i) => (
                                <div key={i} style={{ display: 'flex', gap: 10, alignItems: 'flex-start', marginBottom: 10 }}>
                                    <div style={{ flexShrink: 0, width: 20, height: 20, borderRadius: '50%', background: 'rgba(0,230,118,0.15)', border: '1px solid rgba(0,230,118,0.35)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 10, fontWeight: 800, color: '#00e676', fontFamily: MONO }}>{i + 1}</div>
                                    <span style={{ fontSize: 12, color: 'var(--text-muted)', lineHeight: 1.6 }}>{step}</span>
                                </div>
                            ))}
                        </div>
                        <div>
                            <div style={{ fontSize: 14, fontWeight: 800, color: '#facc15', marginBottom: 16, display: 'flex', alignItems: 'center', gap: 8 }}>
                                <span>⚡</span> Requirements
                            </div>
                            {[
                                ['Android', '7.0 (Nougat) atau lebih baru'],
                                ['RAM', 'Minimal 2 GB'],
                                ['Storage', '100 MB free space'],
                                ['Internet', 'Koneksi aktif diperlukan'],
                            ].map(([label, val]) => (
                                <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10, fontSize: 12 }}>
                                    <span style={{ color: 'var(--text-muted)' }}>{label}</span>
                                    <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{val}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </FadeIn>
            </div>
        </section>
    );

    /* ── FOOTER ── */
    const Footer = (
        <footer style={{ background: dark ? '#080808' : '#f1f5f9', borderTop: `1px solid var(--border)`, padding: '60px 24px 36px' }}>
            <div style={{ maxWidth: 1200, margin: '0 auto' }}>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: 40, marginBottom: 48 }}>
                    {/* Brand */}
                    <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14 }}>
                            <img src={LOGO} alt="Golden AI Strategy" style={{ width: 34, height: 34, borderRadius: 8, objectFit: 'cover' }} />
                            <span style={{ fontWeight: 800, fontSize: 17, color: '#facc15' }}>Golden AI Strategy</span>
                        </div>
                        <p style={{ fontSize: 13, color: 'var(--text-muted)', lineHeight: 1.7, maxWidth: 200 }}>
                            Platform AI trading terdepan untuk Forex, Crypto, dan IDX Saham Indonesia.
                        </p>
                    </div>

                    {/* Product */}
                    <div>
                        <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Product</div>
                        {['Features', 'Pricing', 'Booster', 'Changelog'].map(l => (
                            <a key={l} href="#" style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', textDecoration: 'none', marginBottom: 8, transition: 'color 0.2s' }}
                            onMouseEnter={e => e.currentTarget.style.color = '#facc15'}
                            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
                            >{l}</a>
                        ))}
                    </div>

                    {/* Company */}
                    <div>
                        <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Company</div>
                        {[
                            { label: 'About',    href: '#' },
                            { label: 'Blog',     href: 'https://blog.gasstrategyai.xyz' },
                            { label: 'Docs',     href: 'https://docs.gasstrategyai.xyz' },
                            { label: 'Careers',  href: '#' },
                            { label: 'Contact',  href: '#' },
                        ].map(({ label, href }) => (
                            <a key={label} href={href} target={href !== '#' ? '_blank' : undefined} rel="noreferrer"
                            style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', textDecoration: 'none', marginBottom: 8, transition: 'color 0.2s' }}
                            onMouseEnter={e => e.currentTarget.style.color = '#facc15'}
                            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
                            >{label}{href !== '#' ? ' ↗' : ''}</a>
                        ))}
                    </div>

                    {/* Legal */}
                    <div>
                        <div style={{ fontWeight: 700, fontSize: 13, color: 'var(--text-primary)', marginBottom: 14, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Legal</div>
                        {['Privacy Policy', 'Terms of Service', 'Refund Policy', 'Risk Disclaimer'].map(l => (
                            <a key={l} href="#" style={{ display: 'block', fontSize: 13, color: 'var(--text-muted)', textDecoration: 'none', marginBottom: 8, transition: 'color 0.2s' }}
                            onMouseEnter={e => e.currentTarget.style.color = '#facc15'}
                            onMouseLeave={e => e.currentTarget.style.color = 'var(--text-muted)'}
                            >{l}</a>
                        ))}
                    </div>
                </div>

                <div style={{ borderTop: `1px solid var(--border)`, paddingTop: 28, display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12 }}>
                    <div style={{ fontSize: 13, color: 'var(--text-muted)' }}>
                        © 2026 <span style={{ color: '#facc15', fontWeight: 700 }}>Golden AI Strategy</span>. All rights reserved.
                    </div>
                    <div style={{ fontSize: 12, color: 'var(--text-muted)' }}>
                        Trading involves risk. Past performance is not indicative of future results.
                    </div>
                </div>
            </div>
        </footer>
    );

    /* ── RENDER ── */
    return (
        <div style={{ ...css, background: 'var(--bg-main)', color: 'var(--text-primary)', fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", minHeight: '100vh' }}>
            <style>{`
                @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700;800&display=swap');
                * { box-sizing: border-box; margin: 0; padding: 0; }
                html { scroll-behavior: smooth; }
                @keyframes fadeInDown {
                    from { opacity: 0; transform: translateY(-16px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(24px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes fadeInRight {
                    from { opacity: 0; transform: translateX(32px); }
                    to { opacity: 1; transform: translateX(0); }
                }
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.4; }
                }
                .nav-desktop { display: flex !important; }
                .nav-mobile-btn { display: none !important; }
                @media (max-width: 768px) {
                    .nav-desktop { display: none !important; }
                    .nav-mobile-btn { display: flex !important; }
                }
                @media (max-width: 900px) {
                    .hero-grid { grid-template-columns: 1fr !important; }
                    .hero-terminal-card { display: none !important; }
                    .modes-grid { grid-template-columns: 1fr !important; }
                    .stats-grid { grid-template-columns: repeat(2, 1fr) !important; }
                }
                @media (max-width: 480px) {
                    .stats-grid { grid-template-columns: repeat(2, 1fr) !important; }
                }
            `}</style>

            {Navbar}
            {Hero}
            {StatsSection}
            {Features}
            {TradingModes}
            {Pricing}
            {Reviews}
            {MobileDownload}
            {FAQ}
            {FinalCTA}
            {Footer}
        </div>
    );
}
