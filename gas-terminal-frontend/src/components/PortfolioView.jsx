import React, { useState, useEffect, useRef, useMemo } from 'react';
import {
    TrendingUp, TrendingDown, BarChart2, BookOpen, Target,
    FileText, Download, Filter, ChevronDown, ChevronUp,
    Activity, Zap, Shield, Award, ArrowUpRight, ArrowDownRight,
    Calendar, Clock, DollarSign, Percent, AlertTriangle, Check
} from 'lucide-react';
// ─── MOCK DATA ───────────────────────────────────────────────
const METRICS = {
    balance: 18410.50, equity: 18520.00, startBalance: 10000,
    totalProfit: 12840.50, totalLoss: 3240.80, netPnl: 9599.70,
    winRate: 72.5, totalTrades: 247, wins: 179, losses: 68,
    profitFactor: 2.84, maxDrawdown: 4.2, avgWin: 71.73,
    avgLoss: 47.66, bestTrade: 840, worstTrade: -320,
    sharpe: 2.14, avgRR: 1.8, dailyGoal: 200, todayPnl: 420,
    growthPct: 84.1,
};

function genEquityCurve() {
    const data = []; let val = 10000;
    const start = new Date('2025-09-01');
    for (let i = 0; i < 180; i++) {
        const d = new Date(start); d.setDate(d.getDate() + i);
        if (d.getDay() === 0 || d.getDay() === 6) continue;
        const change = (Math.random() - 0.35) * 180;
        val = Math.max(9200, val + change);
        data.push({ time: d.toISOString().split('T')[0], value: parseFloat(val.toFixed(2)) });
    }
    data[data.length - 1].value = 18410.50;
    return data;
}

function genDailyPnl() {
    const data = []; const start = new Date('2026-01-01');
    for (let i = 0; i < 45; i++) {
        const d = new Date(start); d.setDate(d.getDate() + i);
        if (d.getDay() === 0 || d.getDay() === 6) continue;
        const v = parseFloat(((Math.random() - 0.3) * 500).toFixed(2));
        data.push({ time: d.toISOString().split('T')[0], value: v });
    }
    return data;
}

const EQUITY_DATA = genEquityCurve();
const DAILY_PNL = genDailyPnl();

const JOURNAL = [
    { id: 1, time: '2026-03-07 14:32', asset: 'XAUUSD', dir: 'BUY',  entry: 2031.50, exit: 2048.20, lot: 0.10, rr: 2.4, pnl: +168.00, dur: '2h 14m', tag: 'Trend' },
    { id: 2, time: '2026-03-07 11:20', asset: 'EURUSD', dir: 'SELL', entry: 1.0872, exit: 1.0841, lot: 0.50, rr: 1.8, pnl: +155.00, dur: '45m', tag: 'Breakout' },
    { id: 3, time: '2026-03-07 09:45', asset: 'BTCUSD', dir: 'BUY',  entry: 64100, exit: 63820, lot: 0.01, rr: -1.0, pnl: -28.00, dur: '30m', tag: 'Reversal' },
    { id: 4, time: '2026-03-06 15:10', asset: 'XAUUSD', dir: 'SELL', entry: 2045.80, exit: 2031.20, lot: 0.20, rr: 2.1, pnl: +292.00, dur: '3h 05m', tag: 'Trend' },
    { id: 5, time: '2026-03-06 10:30', asset: 'NAS100', dir: 'BUY',  entry: 19840, exit: 19920, lot: 0.05, rr: 1.6, pnl: +400.00, dur: '1h 22m', tag: 'News' },
    { id: 6, time: '2026-03-05 14:00', asset: 'GBPUSD', dir: 'BUY',  entry: 1.2640, exit: 1.2608, lot: 0.30, rr: -1.0, pnl: -96.00, dur: '55m', tag: 'Reversal' },
    { id: 7, time: '2026-03-05 09:15', asset: 'XAUUSD', dir: 'BUY',  entry: 2018.40, exit: 2038.60, lot: 0.15, rr: 2.8, pnl: +303.00, dur: '4h 10m', tag: 'Trend' },
    { id: 8, time: '2026-03-04 13:45', asset: 'US500',  dir: 'SELL', entry: 5120, exit: 5098, lot: 0.10, rr: 1.9, pnl: +220.00, dur: '2h 30m', tag: 'Breakout' },
    { id: 9, time: '2026-03-04 10:00', asset: 'EURUSD', dir: 'BUY',  entry: 1.0820, exit: 1.0808, lot: 0.50, rr: -1.0, pnl: -60.00, dur: '40m', tag: 'News' },
    { id: 10,time: '2026-03-03 15:30', asset: 'XAUUSD', dir: 'SELL', entry: 2060.10, exit: 2035.40, lot: 0.10, rr: 3.2, pnl: +247.00, dur: '5h 15m', tag: 'Trend' },
];

const ASSET_DIST = [
    { name: 'XAUUSD', pct: 42, color: '#fac815' },
    { name: 'EURUSD', pct: 18, color: '#60a5fa' },
    { name: 'NAS100', pct: 14, color: '#a78bfa' },
    { name: 'BTCUSD', pct: 12, color: '#f97316' },
    { name: 'Others', pct: 14, color: '#6b7280' },
];

const MONTHLY_RETURNS = [
    { m: 'Sep', v: 3.2 }, { m: 'Oct', v: 6.8 }, { m: 'Nov', v: -1.4 },
    { m: 'Dec', v: 9.1 }, { m: 'Jan', v: 12.4 }, { m: 'Feb', v: 7.6 },
    { m: 'Mar', v: 4.1 },
];

const TRADING_PLAN_DEFAULT = `# TRADING PLAN — GAS PRO

## 🎯 TUJUAN TRADING
- Target bulanan: +8% dari balance
- Max drawdown harian: 2%
- Max drawdown total: 5%

## ⏰ SESI TRADING
- London: 15:00 – 18:00 WIB
- New York: 20:00 – 23:00 WIB

## 📋 ATURAN ENTRY
1. Tunggu konfirmasi dari GAS Signal (Level A/B only)
2. Entry hanya pada H1 atau M15 timeframe
3. Risk per trade max 1% dari balance
4. Minimal R:R = 1:2

## 🚫 ATURAN LARANGAN
- Tidak trading saat NFP, FOMC (±30 menit)
- Tidak averaging down
- Tidak revenge trading setelah loss 2x berturut-turut
- Stop trading jika DD harian sudah -2%

## 💰 MANAJEMEN RISIKO
- Lot size: (Balance × 1%) / (SL pips × pip value)
- Tidak buka lebih dari 3 posisi bersamaan
- Selalu pasang SL sebelum entry

## 📝 JURNAL & REVIEW
- Catat setiap trade di journal GAS PRO
- Review mingguan setiap Sabtu pagi
- Monthly review dan adjust plan`;

// ─── CHART HELPERS ───────────────────────────────────────────

function DonutChart({ segments, size = 120, stroke = 22 }) {
    const r = (size - stroke) / 2;
    const circ = 2 * Math.PI * r;
    let offset = 0;
    return (
        <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} className="-rotate-90">
            <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="var(--bg-panel)" strokeWidth={stroke} />
            {segments.map((s, i) => {
                const dash = (s.pct / 100) * circ;
                const gap = circ - dash;
                const el = (
                    <circle key={i} cx={size / 2} cy={size / 2} r={r} fill="none"
                        stroke={s.color} strokeWidth={stroke}
                        strokeDasharray={`${dash} ${gap}`}
                        strokeDashoffset={-offset}
                        strokeLinecap="butt" />
                );
                offset += dash;
                return el;
            })}
        </svg>
    );
}

function MiniBar({ data, height = 80 }) {
    const max = Math.max(...data.map(d => Math.abs(d.v)));
    return (
        <div className="flex items-end gap-0.5 h-20 w-full">
            {data.map((d, i) => {
                const pct = max > 0 ? (Math.abs(d.v) / max) * 100 : 0;
                const isPos = d.v >= 0;
                return (
                    <div key={i} className="flex-1 flex flex-col items-center justify-end group relative" style={{ height: `${height}px` }}>
                        <div className="absolute bottom-full mb-1 text-[8px] font-bold whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity bg-[var(--bg-card)] px-1 py-0.5 rounded z-10">
                            {isPos ? '+' : ''}{d.v}%
                        </div>
                        <div className="w-full rounded-sm transition-all"
                            style={{
                                height: `${pct}%`,
                                minHeight: '2px',
                                background: isPos ? 'var(--success)' : 'var(--danger)',
                                opacity: 0.85,
                            }} />
                        <span className="text-[7px] text-[var(--text-dim)] mt-1 font-bold">{d.m}</span>
                    </div>
                );
            })}
        </div>
    );
}

function WinLossDonut({ wins, losses }) {
    const total = wins + losses;
    const winPct = (wins / total) * 100;
    const segs = [
        { pct: winPct, color: '#10b981' },
        { pct: 100 - winPct, color: '#ef4444' },
    ];
    return (
        <div className="relative flex items-center justify-center">
            <DonutChart segments={segs} size={110} stroke={20} />
            <div className="absolute text-center">
                <p className="text-lg font-black text-[var(--success)]">{winPct.toFixed(1)}%</p>
                <p className="text-[9px] font-bold text-[var(--text-dim)] uppercase">Win</p>
            </div>
        </div>
    );
}

// ─── SVG CHART COMPONENTS ────────────────────────────────────

function EquityChart({ data }) {
    const ref = useRef(null);
    const [dims, setDims] = useState({ w: 600, h: 220 });

    useEffect(() => {
        if (!ref.current) return;
        const ro = new ResizeObserver(([e]) => setDims({ w: e.contentRect.width, h: 220 }));
        ro.observe(ref.current);
        setDims({ w: ref.current.clientWidth || 600, h: 220 });
        return () => ro.disconnect();
    }, []);

    const { w, h } = dims;
    const pad = { top: 10, right: 10, bottom: 28, left: 52 };
    const W = w - pad.left - pad.right;
    const H = h - pad.top - pad.bottom;

    const vals = data.map(d => d.value);
    const minV = Math.min(...vals);
    const maxV = Math.max(...vals);
    const range = maxV - minV || 1;

    const px = (i) => (i / (data.length - 1)) * W;
    const py = (v) => H - ((v - minV) / range) * H;

    const linePath = data.map((d, i) => `${i === 0 ? 'M' : 'L'}${px(i).toFixed(1)},${py(d.value).toFixed(1)}`).join(' ');
    const areaPath = `${linePath} L${px(data.length - 1).toFixed(1)},${H} L0,${H} Z`;

    // Y axis ticks
    const yTicks = [0, 0.25, 0.5, 0.75, 1].map(t => ({
        y: H - t * H,
        label: `$${((minV + t * range) / 1000).toFixed(1)}k`,
    }));
    // X axis ticks (every ~30 data points)
    const xStep = Math.max(1, Math.floor(data.length / 5));
    const xTicks = data.filter((_, i) => i % xStep === 0).map((d, _, arr) => ({
        x: px(data.indexOf(d)),
        label: d.time.slice(5), // MM-DD
    }));

    return (
        <div ref={ref} className="w-full" style={{ height: h }}>
            <svg width={w} height={h} style={{ overflow: 'visible' }}>
                <defs>
                    <linearGradient id="eqGrad" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="0%" stopColor="#fac815" stopOpacity="0.25" />
                        <stop offset="100%" stopColor="#fac815" stopOpacity="0.02" />
                    </linearGradient>
                    <clipPath id="eqClip">
                        <rect x="0" y="0" width={W} height={H} />
                    </clipPath>
                </defs>
                <g transform={`translate(${pad.left},${pad.top})`}>
                    {/* Grid lines */}
                    {yTicks.map((t, i) => (
                        <g key={i}>
                            <line x1={0} y1={t.y} x2={W} y2={t.y} stroke="currentColor" strokeOpacity="0.06" strokeDasharray="3,3" />
                            <text x={-6} y={t.y + 4} textAnchor="end" fontSize="9" fill="currentColor" fillOpacity="0.4" fontFamily="monospace">{t.label}</text>
                        </g>
                    ))}
                    {/* X axis ticks */}
                    {xTicks.map((t, i) => (
                        <text key={i} x={t.x} y={H + 16} textAnchor="middle" fontSize="9" fill="currentColor" fillOpacity="0.35" fontFamily="monospace">{t.label}</text>
                    ))}
                    {/* Area + Line */}
                    <g clipPath="url(#eqClip)">
                        <path d={areaPath} fill="url(#eqGrad)" />
                        <path d={linePath} fill="none" stroke="#fac815" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
                    </g>
                    {/* Last value dot */}
                    <circle cx={px(data.length - 1)} cy={py(vals[vals.length - 1])} r="4" fill="#fac815" />
                </g>
            </svg>
        </div>
    );
}

function PnLChart({ data }) {
    const ref = useRef(null);
    const [w, setW] = useState(600);

    useEffect(() => {
        if (!ref.current) return;
        const ro = new ResizeObserver(([e]) => setW(e.contentRect.width));
        ro.observe(ref.current);
        setW(ref.current.clientWidth || 600);
        return () => ro.disconnect();
    }, []);

    const h = 160;
    const pad = { top: 10, right: 10, bottom: 20, left: 48 };
    const W = w - pad.left - pad.right;
    const H = h - pad.top - pad.bottom;

    const vals = data.map(d => d.value);
    const maxAbs = Math.max(...vals.map(Math.abs), 1);
    const barW = Math.max(2, W / data.length - 1);
    const zeroY = H / 2;

    return (
        <div ref={ref} className="w-full" style={{ height: h }}>
            <svg width={w} height={h}>
                <g transform={`translate(${pad.left},${pad.top})`}>
                    {/* Zero line */}
                    <line x1={0} y1={zeroY} x2={W} y2={zeroY} stroke="currentColor" strokeOpacity="0.15" />
                    {/* Grid */}
                    {[-1, -0.5, 0.5, 1].map((t, i) => (
                        <g key={i}>
                            <line x1={0} y1={zeroY - t * (H / 2)} x2={W} y2={zeroY - t * (H / 2)} stroke="currentColor" strokeOpacity="0.05" strokeDasharray="3,3" />
                            <text x={-6} y={zeroY - t * (H / 2) + 4} textAnchor="end" fontSize="8" fill="currentColor" fillOpacity="0.35" fontFamily="monospace">
                                {t > 0 ? '+' : ''}{(t * maxAbs).toFixed(0)}
                            </text>
                        </g>
                    ))}
                    {/* Bars */}
                    {data.map((d, i) => {
                        const barH = Math.abs(d.value) / maxAbs * (H / 2);
                        const x = (i / data.length) * W;
                        const isPos = d.value >= 0;
                        return (
                            <rect
                                key={i}
                                x={x}
                                y={isPos ? zeroY - barH : zeroY}
                                width={barW}
                                height={Math.max(1, barH)}
                                fill={isPos ? 'rgba(16,185,129,0.75)' : 'rgba(239,68,68,0.75)'}
                                rx="1"
                            />
                        );
                    })}
                </g>
            </svg>
        </div>
    );
}

// ─── KPI CARD ────────────────────────────────────────────────

function KpiCard({ label, value, sub, up, icon: Icon, highlight }) {
    return (
        <div className={`bg-[var(--bg-card)] border rounded-xl p-4 flex flex-col gap-2 ${highlight ? 'border-yellow-400/30 bg-yellow-400/5' : 'border-[var(--border-color)]'}`}>
            <div className="flex items-center justify-between">
                <p className="text-[9px] font-black text-[var(--text-dim)] uppercase tracking-widest">{label}</p>
                {Icon && <Icon size={13} className={up === true ? 'text-[var(--success)]' : up === false ? 'text-[var(--danger)]' : 'text-[var(--text-dim)]'} />}
            </div>
            <p className={`text-xl font-black font-mono leading-none ${
                up === true ? 'text-[var(--success)]' : up === false ? 'text-[var(--danger)]' : highlight ? 'text-yellow-400' : 'text-[var(--text-primary)]'
            }`}>{value}</p>
            {sub && <p className="text-[9px] text-[var(--text-dim)] font-bold leading-tight">{sub}</p>}
        </div>
    );
}

// ─── MAIN COMPONENT ──────────────────────────────────────────

export default function PortfolioView({ theme = 'dark' }) {
    const [tab, setTab] = useState('dashboard');
    const [journalFilter, setJournalFilter] = useState('all');
    const [tradingPlan, setTradingPlan] = useState(TRADING_PLAN_DEFAULT);
    const [planSaved, setPlanSaved] = useState(false);
    const [sortCol, setSortCol] = useState('time');
    const [sortAsc, setSortAsc] = useState(false);

    const savePlan = () => {
        localStorage.setItem('gas-trading-plan', tradingPlan);
        setPlanSaved(true);
        setTimeout(() => setPlanSaved(false), 2000);
    };

    useEffect(() => {
        const saved = localStorage.getItem('gas-trading-plan');
        if (saved) setTradingPlan(saved);
    }, []);

    const filteredJournal = useMemo(() => {
        let d = [...JOURNAL];
        if (journalFilter === 'win') d = d.filter(t => t.pnl > 0);
        if (journalFilter === 'loss') d = d.filter(t => t.pnl < 0);
        if (journalFilter === 'buy') d = d.filter(t => t.dir === 'BUY');
        if (journalFilter === 'sell') d = d.filter(t => t.dir === 'SELL');
        d.sort((a, b) => {
            if (sortCol === 'pnl') return sortAsc ? a.pnl - b.pnl : b.pnl - a.pnl;
            if (sortCol === 'rr') return sortAsc ? a.rr - b.rr : b.rr - a.rr;
            return sortAsc ? a.id - b.id : b.id - a.id;
        });
        return d;
    }, [journalFilter, sortCol, sortAsc]);

    const exportCSV = () => {
        const rows = ['Time,Asset,Dir,Entry,Exit,Lot,R:R,P&L,Duration,Tag'];
        JOURNAL.forEach(t => rows.push(`${t.time},${t.asset},${t.dir},${t.entry},${t.exit},${t.lot},${t.rr},${t.pnl},${t.dur},${t.tag}`));
        const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
        a.download = 'gas_journal.csv'; a.click();
    };

    const TABS = [
        { id: 'dashboard', label: '📊 Dashboard', icon: BarChart2 },
        { id: 'journal',   label: '📒 Journal',   icon: BookOpen },
        { id: 'backtest',  label: '🔬 Backtest',  icon: Activity },
        { id: 'plan',      label: '📋 Trading Plan', icon: FileText },
    ];

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-8 max-w-7xl mx-auto space-y-5">

            {/* ── PAGE HEADER ── */}
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-2xl font-display font-black uppercase">Portfolio</h2>
                    <p className="text-[11px] text-[var(--text-dim)] font-bold mt-0.5">Updated live · Mar 2026 · Paper Account</p>
                </div>
                <div className="flex items-center gap-2">
                    <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--success)]/10 border border-[var(--success)]/20">
                        <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)] animate-pulse" />
                        <span className="text-[10px] font-black text-[var(--success)] uppercase">Live</span>
                    </div>
                </div>
            </div>

            {/* ── TABS ── */}
            <div className="flex gap-1 overflow-x-auto scrollbar-none bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-1">
                {TABS.map(t => (
                    <button key={t.id} onClick={() => setTab(t.id)}
                        className={`px-4 py-2 rounded-lg text-xs font-black whitespace-nowrap transition-all ${tab === t.id ? 'bg-[var(--accent)] text-black shadow' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                        {t.label}
                    </button>
                ))}
            </div>

            {/* ══════════════════════════════════════════════
                TAB: DASHBOARD
            ══════════════════════════════════════════════ */}
            {tab === 'dashboard' && (
                <div className="space-y-5">

                    {/* KPI Row 1 — Account */}
                    <div className="grid grid-cols-2 sm:grid-cols-3 xl:grid-cols-6 gap-3">
                        <KpiCard label="Balance" value={`$${METRICS.balance.toLocaleString()}`} sub="Saldo akun bersih" icon={DollarSign} highlight />
                        <KpiCard label="Equity" value={`$${METRICS.equity.toLocaleString()}`} sub="+$109.50 floating" icon={TrendingUp} up={true} />
                        <KpiCard label="Net P&L" value={`+$${METRICS.netPnl.toLocaleString()}`} sub={`+${METRICS.growthPct}% dari modal`} icon={ArrowUpRight} up={true} />
                        <KpiCard label="Today P&L" value={`+$${METRICS.todayPnl}`} sub="vs target $200" icon={Zap} up={true} />
                        <KpiCard label="Max DD" value={`-${METRICS.maxDrawdown}%`} sub="Drawdown maks" icon={AlertTriangle} up={false} />
                        <KpiCard label="Profit Factor" value={METRICS.profitFactor} sub="Target > 2.0" icon={Award} up={true} />
                    </div>

                    {/* KPI Row 2 — Trading Stats */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3">
                        {[
                            { label: 'Total Trades', value: METRICS.totalTrades, icon: BarChart2 },
                            { label: 'Win Rate', value: `${METRICS.winRate}%`, icon: Percent, up: true },
                            { label: 'Wins', value: METRICS.wins, icon: TrendingUp, up: true },
                            { label: 'Losses', value: METRICS.losses, icon: TrendingDown, up: false },
                            { label: 'Avg Win', value: `$${METRICS.avgWin}`, icon: ArrowUpRight, up: true },
                            { label: 'Avg Loss', value: `-$${METRICS.avgLoss}`, icon: ArrowDownRight, up: false },
                            { label: 'Best Trade', value: `+$${METRICS.bestTrade}`, icon: Award, up: true },
                            { label: 'Sharpe', value: METRICS.sharpe, icon: Activity },
                        ].map((k, i) => (
                            <KpiCard key={i} label={k.label} value={k.value} icon={k.icon} up={k.up} />
                        ))}
                    </div>

                    {/* Funded Tracker */}
                    <div className="bg-[var(--bg-card)] border border-yellow-400/20 rounded-xl p-5">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center gap-2">
                                <Shield size={16} className="text-yellow-400" />
                                <span className="text-xs font-black uppercase tracking-widest text-yellow-400">Funded Tracker</span>
                            </div>
                            <span className="text-[9px] font-black px-2 py-1 rounded-full bg-green-400/10 text-green-400 border border-green-400/20 uppercase">Phase 1 · Passing</span>
                        </div>
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                            {[
                                { label: 'Profit Target', current: METRICS.growthPct, target: 10, unit: '%', color: 'bg-green-500' },
                                { label: 'Daily DD Limit', current: 1.2, target: 5, unit: '%', color: 'bg-yellow-400', invert: true },
                                { label: 'Max DD Limit', current: METRICS.maxDrawdown, target: 10, unit: '%', color: 'bg-yellow-400', invert: true },
                            ].map((r, i) => (
                                <div key={i}>
                                    <div className="flex items-center justify-between text-[10px] font-bold text-[var(--text-dim)] mb-2">
                                        <span>{r.label}</span>
                                        <span className="text-[var(--text-primary)]">{r.current}{r.unit} / {r.target}{r.unit}</span>
                                    </div>
                                    <div className="h-2.5 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                                        <div className={`h-full ${r.color} rounded-full transition-all`}
                                            style={{ width: `${Math.min(100, (r.current / r.target) * 100)}%` }} />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Charts Row 1: Equity + Win/Loss */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">

                        {/* Equity Curve */}
                        <div className="xl:col-span-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                            <div className="flex items-center justify-between mb-4">
                                <div>
                                    <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)]">Equity Curve</p>
                                    <p className="text-lg font-black text-[var(--success)] mt-0.5">+{METRICS.growthPct}% Growth</p>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] text-[var(--text-dim)]">Start: $10,000</p>
                                    <p className="text-[10px] text-[var(--text-dim)]">Now: $18,410</p>
                                </div>
                            </div>
                            <EquityChart data={EQUITY_DATA} theme={theme} />
                        </div>

                        {/* Win/Loss + Asset Dist */}
                        <div className="flex flex-col gap-4">
                            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5 flex-1">
                                <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">Win / Loss Ratio</p>
                                <div className="flex items-center gap-5">
                                    <WinLossDonut wins={METRICS.wins} losses={METRICS.losses} />
                                    <div className="space-y-2">
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-sm bg-[var(--success)]" />
                                            <span className="text-xs font-bold">Win: {METRICS.wins}</span>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            <div className="w-2.5 h-2.5 rounded-sm bg-[var(--danger)]" />
                                            <span className="text-xs font-bold">Loss: {METRICS.losses}</span>
                                        </div>
                                        <div className="mt-2 pt-2 border-t border-[var(--border-color)]">
                                            <p className="text-[9px] text-[var(--text-dim)]">R:R Avg</p>
                                            <p className="text-base font-black text-[var(--accent)]">{METRICS.avgRR}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5 flex-1">
                                <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-3">Asset Distribution</p>
                                <div className="space-y-2">
                                    {ASSET_DIST.map((a, i) => (
                                        <div key={i} className="flex items-center gap-2">
                                            <div className="w-2 h-2 rounded-full shrink-0" style={{ background: a.color }} />
                                            <span className="text-[10px] font-bold flex-1">{a.name}</span>
                                            <div className="flex-1 h-1.5 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                                                <div className="h-full rounded-full transition-all" style={{ width: `${a.pct}%`, background: a.color }} />
                                            </div>
                                            <span className="text-[10px] font-mono text-[var(--text-dim)] w-7 text-right">{a.pct}%</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Charts Row 2: Daily P&L + Monthly Returns */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
                        <div className="xl:col-span-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                            <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">Daily P&L</p>
                            <p className="text-[10px] text-[var(--text-dim)] mb-3">Januari – Maret 2026</p>
                            <PnLChart data={DAILY_PNL} theme={theme} />
                        </div>

                        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                            <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Monthly Returns</p>
                            <MiniBar data={MONTHLY_RETURNS} />
                            <div className="mt-3 space-y-1.5">
                                {MONTHLY_RETURNS.map((m, i) => (
                                    <div key={i} className="flex items-center justify-between text-[10px]">
                                        <span className="text-[var(--text-dim)] font-bold w-8">{m.m}</span>
                                        <div className="flex-1 mx-2 h-1 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                                            <div className="h-full rounded-full" style={{
                                                width: `${Math.abs(m.v) * 7}%`,
                                                background: m.v >= 0 ? 'var(--success)' : 'var(--danger)'
                                            }} />
                                        </div>
                                        <span className={`font-black font-mono w-12 text-right ${m.v >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                            {m.v >= 0 ? '+' : ''}{m.v}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>

                    {/* Daily Goal */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                        <div className="flex items-center justify-between mb-3">
                            <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)]">Daily Goal Progress</p>
                            <span className={`text-[10px] font-black px-2 py-1 rounded-full ${METRICS.todayPnl >= METRICS.dailyGoal ? 'bg-green-400/10 text-green-400' : 'bg-yellow-400/10 text-yellow-400'}`}>
                                {METRICS.todayPnl >= METRICS.dailyGoal ? '✓ Target Tercapai!' : `$${METRICS.dailyGoal - METRICS.todayPnl} lagi`}
                            </span>
                        </div>
                        <div className="flex items-center gap-4">
                            <div className="flex-1">
                                <div className="h-4 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                                    <div className="h-full bg-gradient-to-r from-yellow-400 to-green-500 rounded-full transition-all duration-1000"
                                        style={{ width: `${Math.min(100, (METRICS.todayPnl / METRICS.dailyGoal) * 100)}%` }} />
                                </div>
                            </div>
                            <span className="text-sm font-black font-mono text-[var(--success)] whitespace-nowrap">
                                +${METRICS.todayPnl} / ${METRICS.dailyGoal}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* ══════════════════════════════════════════════
                TAB: JOURNAL
            ══════════════════════════════════════════════ */}
            {tab === 'journal' && (
                <div className="space-y-4">
                    {/* Journal Header Stats */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                        <KpiCard label="Total Trades" value={JOURNAL.length} icon={BarChart2} />
                        <KpiCard label="Total P&L" value={`+$${JOURNAL.reduce((a, t) => a + t.pnl, 0).toFixed(2)}`} up={true} icon={TrendingUp} />
                        <KpiCard label="Best Trade" value={`+$${Math.max(...JOURNAL.map(t => t.pnl))}`} up={true} icon={Award} />
                        <KpiCard label="Worst Trade" value={`$${Math.min(...JOURNAL.map(t => t.pnl)).toFixed(2)}`} up={false} icon={AlertTriangle} />
                    </div>

                    {/* Filter Bar */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-3 flex flex-wrap items-center gap-2">
                        <Filter size={13} className="text-[var(--text-dim)] shrink-0" />
                        {[
                            { key: 'all', label: 'Semua' },
                            { key: 'win', label: '✅ Win' },
                            { key: 'loss', label: '❌ Loss' },
                            { key: 'buy', label: '🟢 Buy' },
                            { key: 'sell', label: '🔴 Sell' },
                        ].map(f => (
                            <button key={f.key} onClick={() => setJournalFilter(f.key)}
                                className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${journalFilter === f.key ? 'bg-[var(--accent)] text-black' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)]'}`}>
                                {f.label}
                            </button>
                        ))}
                        <div className="flex-1" />
                        <button onClick={exportCSV}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-[var(--border-color)] text-[10px] font-black text-[var(--text-dim)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-hover)] transition-all">
                            <Download size={11} /> Export CSV
                        </button>
                    </div>

                    {/* Journal Table */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                        <div className="overflow-x-auto scrollbar-none">
                            <table className="w-full text-xs min-w-[800px]">
                                <thead>
                                    <tr className="bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                                        {[
                                            { col: 'time', label: 'Waktu' },
                                            { col: null, label: 'Aset' },
                                            { col: null, label: 'Arah' },
                                            { col: null, label: 'Entry' },
                                            { col: null, label: 'Exit' },
                                            { col: null, label: 'Lot' },
                                            { col: 'rr', label: 'R:R' },
                                            { col: 'pnl', label: 'P&L' },
                                            { col: null, label: 'Durasi' },
                                            { col: null, label: 'Tag' },
                                        ].map((h, i) => (
                                            <th key={i}
                                                onClick={h.col ? () => { if (sortCol === h.col) setSortAsc(p => !p); else { setSortCol(h.col); setSortAsc(false); } } : undefined}
                                                className={`px-4 py-3 text-left font-black text-[var(--text-dim)] uppercase tracking-wider ${h.col ? 'cursor-pointer hover:text-[var(--text-primary)] select-none' : ''}`}>
                                                <div className="flex items-center gap-1">
                                                    {h.label}
                                                    {h.col && sortCol === h.col && (sortAsc ? <ChevronUp size={10} /> : <ChevronDown size={10} />)}
                                                </div>
                                            </th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {filteredJournal.map((r, i) => (
                                        <tr key={r.id} className={`border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors ${i % 2 === 0 ? '' : 'bg-[var(--bg-main)]/30'}`}>
                                            <td className="px-4 py-3 text-[var(--text-dim)] font-mono whitespace-nowrap">{r.time}</td>
                                            <td className="px-4 py-3 font-black text-[var(--text-primary)]">{r.asset}</td>
                                            <td className="px-4 py-3">
                                                <span className={`px-2 py-0.5 rounded text-[9px] font-black tracking-widest ${r.dir === 'BUY' ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>
                                                    {r.dir}
                                                </span>
                                            </td>
                                            <td className="px-4 py-3 font-mono text-[var(--text-secondary)]">{r.entry}</td>
                                            <td className="px-4 py-3 font-mono text-[var(--text-secondary)]">{r.exit}</td>
                                            <td className="px-4 py-3 font-mono text-[var(--text-dim)]">{r.lot}</td>
                                            <td className="px-4 py-3 font-mono">
                                                <span className={r.rr > 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}>
                                                    {r.rr > 0 ? '+' : ''}{r.rr}
                                                </span>
                                            </td>
                                            <td className={`px-4 py-3 font-mono font-black text-sm ${r.pnl > 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                {r.pnl > 0 ? '+' : ''}${r.pnl.toFixed(2)}
                                            </td>
                                            <td className="px-4 py-3 text-[var(--text-dim)] whitespace-nowrap">
                                                <span className="flex items-center gap-1"><Clock size={10} />{r.dur}</span>
                                            </td>
                                            <td className="px-4 py-3">
                                                <span className="text-[9px] font-black px-2 py-0.5 rounded-full bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-dim)]">
                                                    {r.tag}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <div className="px-4 py-3 border-t border-[var(--border-color)] flex items-center justify-between bg-[var(--bg-panel)]">
                            <span className="text-[10px] text-[var(--text-dim)]">Menampilkan {filteredJournal.length} dari {JOURNAL.length} trade</span>
                            <span className={`text-sm font-black font-mono ${filteredJournal.reduce((a, t) => a + t.pnl, 0) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                Total: {filteredJournal.reduce((a, t) => a + t.pnl, 0) >= 0 ? '+' : ''}${filteredJournal.reduce((a, t) => a + t.pnl, 0).toFixed(2)}
                            </span>
                        </div>
                    </div>
                </div>
            )}

            {/* ══════════════════════════════════════════════
                TAB: BACKTEST
            ══════════════════════════════════════════════ */}
            {tab === 'backtest' && (
                <div className="space-y-5">
                    {/* Strategy selector */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4 flex flex-wrap items-center gap-3">
                        <span className="text-xs font-black text-[var(--text-dim)] uppercase tracking-widest">Strategy:</span>
                        {['GAS Trend v2.1', 'SMC Breakout', 'MA Crossover'].map((s, i) => (
                            <button key={i} className={`px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${i === 0 ? 'bg-[var(--accent)] text-black' : 'border border-[var(--border-color)] text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                                {s}
                            </button>
                        ))}
                        <div className="flex-1" />
                        <span className="text-[9px] font-bold text-[var(--text-dim)] bg-[var(--bg-panel)] px-2 py-1 rounded-lg border border-[var(--border-color)]">
                            Jan 2023 – Mar 2026 · XAUUSD M15
                        </span>
                    </div>

                    {/* Backtest KPIs */}
                    <div className="grid grid-cols-2 sm:grid-cols-4 xl:grid-cols-8 gap-3">
                        {[
                            { label: 'Total Trades', value: '1,847', icon: BarChart2 },
                            { label: 'Win Rate', value: '71.3%', up: true, icon: Percent },
                            { label: 'Profit Factor', value: '2.71', up: true, icon: Award },
                            { label: 'Net Profit', value: '+842%', up: true, icon: TrendingUp },
                            { label: 'Max DD', value: '-8.4%', up: false, icon: AlertTriangle },
                            { label: 'Sharpe', value: '1.98', icon: Activity },
                            { label: 'Avg R:R', value: '1.76', icon: Target },
                            { label: 'Best Month', value: '+18.2%', up: true, icon: Calendar },
                        ].map((k, i) => <KpiCard key={i} {...k} />)}
                    </div>

                    {/* Equity Curve (backtest) */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                        <div className="flex items-center justify-between mb-4">
                            <div>
                                <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)]">Backtest Equity Curve</p>
                                <p className="text-sm text-[var(--text-dim)] mt-0.5">GAS Trend v2.1 · $10,000 initial capital</p>
                            </div>
                            <span className="text-xl font-black text-[var(--success)]">+842%</span>
                        </div>
                        <EquityChart data={EQUITY_DATA.map((d, i) => ({ ...d, value: 10000 + i * 44 + Math.sin(i / 8) * 500 }))} theme={theme} />
                    </div>

                    {/* Monthly Returns Table */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                        <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                            <span className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)]">Monthly Backtest Returns</span>
                        </div>
                        <div className="p-5 grid grid-cols-4 sm:grid-cols-6 xl:grid-cols-12 gap-2">
                            {Array.from({ length: 36 }, (_, i) => {
                                const v = parseFloat(((Math.random() - 0.28) * 14).toFixed(1));
                                const d = new Date('2023-01-01'); d.setMonth(d.getMonth() + i);
                                return { label: d.toLocaleString('default', { month: 'short' }) + " '" + String(d.getFullYear()).slice(2), v };
                            }).map((m, i) => (
                                <div key={i} className={`rounded-lg p-2 text-center border ${m.v >= 0 ? 'bg-green-500/10 border-green-500/20' : 'bg-red-500/10 border-red-500/20'}`}>
                                    <p className={`text-[9px] font-black ${m.v >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                        {m.v >= 0 ? '+' : ''}{m.v}%
                                    </p>
                                    <p className="text-[8px] text-[var(--text-dim)] mt-0.5">{m.label}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* ══════════════════════════════════════════════
                TAB: TRADING PLAN
            ══════════════════════════════════════════════ */}
            {tab === 'plan' && (
                <div className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {[
                            { label: 'Monthly Target', value: '+8%', icon: Target, color: 'text-yellow-400' },
                            { label: 'Max Daily DD', value: '2%', icon: Shield, color: 'text-blue-400' },
                            { label: 'Risk per Trade', value: '1%', icon: AlertTriangle, color: 'text-orange-400' },
                        ].map((s, i) => (
                            <div key={i} className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4 flex items-center gap-3">
                                <s.icon size={20} className={s.color} />
                                <div>
                                    <p className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">{s.label}</p>
                                    <p className={`text-xl font-black font-mono ${s.color}`}>{s.value}</p>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                        <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)] flex items-center justify-between">
                            <span className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)]">Trading Plan Editor</span>
                            <div className="flex items-center gap-2">
                                {planSaved && (
                                    <span className="text-[10px] font-black text-green-400 flex items-center gap-1">
                                        <Check size={11} /> Saved!
                                    </span>
                                )}
                                <button onClick={savePlan}
                                    className="px-4 py-1.5 bg-[var(--accent)] text-black text-[10px] font-black rounded-lg hover:opacity-90 transition-opacity">
                                    Simpan Plan
                                </button>
                            </div>
                        </div>
                        <textarea
                            value={tradingPlan}
                            onChange={e => setTradingPlan(e.target.value)}
                            rows={28}
                            className="w-full bg-transparent p-5 text-xs font-mono text-[var(--text-secondary)] leading-relaxed outline-none resize-none placeholder:text-[var(--text-dim)]"
                            placeholder="Tulis trading plan kamu di sini..."
                        />
                    </div>

                    {/* Rules Checklist */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                        <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Daily Checklist Sebelum Trading</p>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                            {[
                                'Cek economic calendar hari ini',
                                'Review signal GAS PRO terbaru',
                                'Hitung lot size berdasarkan balance',
                                'Set SL/TP sebelum entry',
                                'Cek sentimen market (Risk On/Off)',
                                'Tidak trading kalau mood negatif',
                                'Max 3 posisi terbuka sekaligus',
                                'Stop jika DD harian sudah -2%',
                            ].map((item, i) => {
                                const [checked, setChecked] = useState(false);
                                return (
                                    <label key={i} className="flex items-center gap-2.5 cursor-pointer group">
                                        <div onClick={() => setChecked(p => !p)}
                                            className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all shrink-0 ${checked ? 'bg-[var(--success)] border-[var(--success)]' : 'border-[var(--border-color)] group-hover:border-[var(--text-dim)]'}`}>
                                            {checked && <Check size={10} className="text-white" />}
                                        </div>
                                        <span className={`text-xs transition-all ${checked ? 'line-through text-[var(--text-dim)]' : 'text-[var(--text-secondary)]'}`}>{item}</span>
                                    </label>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
