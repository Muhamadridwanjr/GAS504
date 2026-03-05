export const PAIRS = [
    { symbol: 'XAUUSD', name: 'Gold / USD', base: 2034.50, vol: 0.8, type: 'Commodity', trend: [30, 45, 40, 60, 55, 75, 70, 65, 80, 75] },
    { symbol: 'BTCUSD', name: 'Bitcoin / USD', base: 64230.15, vol: 25.0, type: 'Crypto', trend: [50, 40, 70, 60, 90, 80, 100, 85, 95, 90] },
    { symbol: 'NVDA', name: 'NVIDIA Corp.', base: 176.32, vol: 1.5, type: 'Stock', trend: [60, 55, 65, 75, 70, 85, 90, 80, 88, 92] },
    { symbol: 'EURUSD', name: 'Euro / USD', base: 1.0854, vol: 0.0006, type: 'Forex', trend: [20, 25, 22, 30, 28, 35, 32, 38, 30, 36] },
    { symbol: 'TSLA', name: 'Tesla Inc.', base: 247.10, vol: 3.2, type: 'Stock', trend: [80, 70, 75, 65, 60, 70, 80, 75, 85, 78] },
    { symbol: 'USDJPY', name: 'USD / Yen', base: 149.85, vol: 0.12, type: 'Forex', trend: [40, 50, 45, 55, 60, 58, 65, 62, 70, 67] },
];

export const GLOBAL_INDICES = [
    { name: 'S&P 500', value: 5274.39, change: -14.39, pct: -0.27 },
    { name: 'DOW30', value: 38772.81, change: -213.81, pct: -0.55 },
    { name: 'HANGSENG', value: 25183.57, change: +123.57, pct: +0.49 },
    { name: 'NIKKEI225', value: 40142.15, change: +122.15, pct: +0.31 },
    { name: 'SHANGHAI', value: 3829.23, change: -12.23, pct: -0.32 },
    { name: 'FTSE', value: 9624.89, change: -122.89, pct: -1.26 },
];

export const NEWS_FEED = [
    "🔥 FED beri sinyal tahan suku bunga Q3",
    "📈 Emas melonjak usai rilis data CPI rendah",
    "🚀 BTC tembus resistensi kuat $65k",
    "💡 Pasar global reli didorong sektor teknologi",
    "⚡ NVIDIA catat rekor pendapatan Q4",
];

export const AI_ANALYSIS = {
    trend: "BULLISH", strength: 8.7,
    logic: [
        "Liquidity sweep terdeteksi di 2028.50",
        "Order block tervalidasi pada H1",
        "Momentum bullish divergence (RSI)",
    ],
};

export const MACRO_DATA = [
    { title: "Fed Rate", value: "5.50%", impact: "HIGH", bias: "BEARISH USD" },
    { title: "CPI YoY", value: "3.2%", impact: "HIGH", bias: "BULLISH GOLD" },
    { title: "NFP", value: "187K", impact: "MEDIUM", bias: "USD NEUTRAL" },
    { title: "DXY", value: "104.2", impact: "MEDIUM", bias: "USD STRONG" },
];

import {
    Zap, BrainCircuit, Activity, ShieldCheck, Filter, Calendar, BarChart2, Droplet,
    Bell, Bot, Webhook, BookOpen, Users, Trophy, CreditCard
} from 'lucide-react';

export const MORE_CATEGORIES = [
    {
        title: "Alat AI Premium", highlight: true, items: [
            { id: 'ai_signal', label: 'Sinyal AI Pro', icon: Zap, pro: true },
            { id: 'ai_analysis', label: 'Analisa Multi-TF', icon: BrainCircuit, pro: true },
            { id: 'ai_backtest', label: 'Mesin Backtest', icon: Activity, pro: true },
            { id: 'risk_manager', label: 'Manajemen Risiko', icon: ShieldCheck, pro: true },
        ]
    },
    {
        title: "Alat Trading", items: [
            { id: 'screener', label: 'Screener Aset', icon: Filter },
            { id: 'calendars', label: 'Kalender Ekonomi', icon: Calendar },
            { id: 'sentiment', label: 'Sentimen Pasar', icon: BarChart2 },
            { id: 'liquidity', label: 'Peta Likuiditas', icon: Droplet },
        ]
    },
    {
        title: "Otomatisasi", items: [
            { id: 'alerts', label: 'Peringatan Harga', icon: Bell },
            { id: 'telegram', label: 'Bot Telegram', icon: Bot },
            { id: 'webhook', label: 'API / Webhook', icon: Webhook },
        ]
    },
    {
        title: "Utilitas & Komunitas", items: [
            { id: 'journal', label: 'Jurnal Trading', icon: BookOpen },
            { id: 'forum', label: 'Forum VIP', icon: Users },
            { id: 'leaderboard', label: 'Papan Peringkat', icon: Trophy },
            { id: 'subscription', label: 'Langganan', icon: CreditCard },
        ]
    },
];
