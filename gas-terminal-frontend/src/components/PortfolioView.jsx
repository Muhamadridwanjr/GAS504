import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import axios from 'axios';
import {
    TrendingUp, TrendingDown, BarChart2, BookOpen, Target,
    FileText, Download, Filter, ChevronDown, ChevronUp,
    Activity, Zap, Shield, Award, ArrowUpRight, ArrowDownRight,
    Calendar, Clock, DollarSign, Percent, AlertTriangle, Check,
    RefreshCw, Wifi, WifiOff
} from 'lucide-react';
import { fetchPortfolioLive, fetchOpenPositions, fetchAccountStatus } from '../services/api';

const WEB_API = '/web/api/v1';
const getHeaders = () => ({ Authorization: `Bearer ${localStorage.getItem('gas-token') || ''}` });
// ─── CONSTANTS ──────────────────────────────────────────────────────────────
const JOURNAL_KEY = 'gas-journal-trades';

const MOCK_METRICS = {
    balance: 10000, equity: 10000, startBalance: 10000,
    totalProfit: 0, totalLoss: 0, netPnl: 0,
    winRate: 0, totalTrades: 0, wins: 0, losses: 0,
    profitFactor: 0, maxDrawdown: 0, avgWin: 0,
    avgLoss: 0, bestTrade: 0, worstTrade: 0,
    sharpe: 0, avgRR: 0, dailyGoal: 200, todayPnl: 0,
    growthPct: 0,
};

const ASSET_COLORS = ['#fac815', '#60a5fa', '#a78bfa', '#f97316', '#10b981', '#6b7280'];

const TRADING_PLAN_DEFAULT = `# TRADING PLAN — Golden AI Strategy

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
- Catat setiap trade di journal Golden AI Strategy
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

// ─── CHECKLIST ITEM (extracted so useState is valid at top level) ────────────
function ChecklistItem({ label }) {
    const [checked, setChecked] = React.useState(false);
    return (
        <label className="flex items-center gap-2.5 cursor-pointer group">
            <div onClick={() => setChecked(p => !p)}
                className={`w-4 h-4 rounded border-2 flex items-center justify-center transition-all shrink-0 ${checked ? 'bg-[var(--success)] border-[var(--success)]' : 'border-[var(--border-color)] group-hover:border-[var(--text-dim)]'}`}>
                {checked && <Check size={10} className="text-white" />}
            </div>
            <span className={`text-xs transition-all ${checked ? 'line-through text-[var(--text-dim)]' : 'text-[var(--text-secondary)]'}`}>{label}</span>
        </label>
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

    // ── Live MT5 data ──────────────────────────────────────────────────
    const [liveData, setLiveData] = useState(null);
    const [liveLoading, setLiveLoading] = useState(true);
    const [liveStatus, setLiveStatus] = useState('loading');
    const [openPositions, setOpenPositions] = useState([]);
    const [accountMode, setAccountMode] = useState('offline'); // 'user_ea' | 'main_ea' | 'offline'
    const [localJournal, setLocalJournal] = useState([]);
    const [journalLoading, setJournalLoading] = useState(false);

    const loadJournal = useCallback(async () => {
        setJournalLoading(true);
        try {
            const res = await axios.get(`${WEB_API}/journal/`, { headers: getHeaders() });
            const entries = (res.data?.entries || []).map(e => ({
                id: e.id,
                time: e.created_at ? new Date(e.created_at).toLocaleDateString('id-ID') : '',
                date: e.created_at ? e.created_at.slice(0, 7) : '',
                pair: e.pair || '',
                type: e.direction || '',
                entry: parseFloat(e.entry_price) || 0,
                exit: parseFloat(e.exit_price) || 0,
                sl: parseFloat(e.sl) || 0,
                lot: parseFloat(e.lot) || 0,
                pnl: parseFloat(e.pnl) || 0,
                notes: e.notes || '',
                source: e.source || 'manual',
            }));
            setLocalJournal(entries);
        } catch {
            setLocalJournal([]);
        } finally {
            setJournalLoading(false);
        }
    }, []);

    const loadLiveData = async () => {
        setLiveLoading(true);
        try {
            const [data, posData, statusData] = await Promise.all([
                fetchPortfolioLive(),
                fetchOpenPositions(),
                fetchAccountStatus(),
            ]);
            if (data && data.balance !== null) {
                setLiveData(data);
                setLiveStatus(data.status);
            } else {
                setLiveStatus('no_heartbeat');
            }
            if (posData?.positions) setOpenPositions(posData.positions);
            if (statusData?.mode) setAccountMode(statusData.mode);
        } catch (e) {
            setLiveStatus('error');
        } finally {
            setLiveLoading(false);
        }
    };

    useEffect(() => {
        loadLiveData();
        loadJournal();
        const iv = setInterval(loadLiveData, 10000);
        return () => clearInterval(iv);
    }, [loadJournal]);

    // Build METRICS from live data (falls back to MOCK_METRICS)
    const METRICS = useMemo(() => {
        if (liveData && liveData.balance) {
            const balance = liveData.balance;
            const equity = liveData.equity;
            const floatingPnl = liveData.floating_pnl || 0;
            const startBalance = MOCK_METRICS.startBalance;
            const netPnl = balance - startBalance;
            const growthPct = startBalance > 0 ? parseFloat(((netPnl / startBalance)*100).toFixed(1)) : 0;
            return {
                ...MOCK_METRICS,
                balance,
                equity,
                startBalance,
                netPnl,
                floatingPnl,
                growthPct,
                open_positions: openPositions.length || liveData.open_positions || 0,
                todayPnl: floatingPnl,
            };
        }
        return MOCK_METRICS;
    }, [liveData, openPositions]);


    // Refresh journal from backend when switching to journal tab
    useEffect(() => {
        if (tab === 'journal') loadJournal();
    }, [tab, loadJournal]);

    // Chart data from live API (empty arrays show empty-state in charts)
    const equityData = liveData?.equity_history || liveData?.equity_curve || [];
    const dailyPnlData = liveData?.daily_pnl || liveData?.pnl_history || [];

    // Asset distribution derived from journal trades
    const assetDist = useMemo(() => {
        if (localJournal.length === 0) return [];
        const counts = {};
        localJournal.forEach(t => { counts[t.pair] = (counts[t.pair] || 0) + 1; });
        const total = localJournal.length;
        return Object.entries(counts)
            .sort((a, b) => b[1] - a[1])
            .slice(0, 6)
            .map(([name, count], i) => ({ name, pct: Math.round((count / total) * 100), color: ASSET_COLORS[i] }));
    }, [localJournal]);

    // Monthly returns derived from journal trades
    const monthlyReturns = useMemo(() => {
        if (localJournal.length === 0) return [];
        const grouped = {};
        localJournal.forEach(t => {
            const key = t.date ? t.date.slice(0, 7) : null;
            if (!key) return;
            grouped[key] = (grouped[key] || 0) + (t.pnl || 0);
        });
        const bal = METRICS.balance || 10000;
        return Object.entries(grouped)
            .sort(([a], [b]) => a.localeCompare(b))
            .slice(-7)
            .map(([key, pnl]) => ({
                m: key.slice(5),
                v: parseFloat(((pnl / bal) * 100).toFixed(1))
            }));
    }, [localJournal, METRICS.balance]);

    // Journal mapped to table schema
    const journalForTable = useMemo(() => localJournal.map(t => ({
        id: t.id,
        time: t.date || '',
        asset: t.pair || '',
        dir: t.type || '',
        entry: t.entry || 0,
        exit: t.exit || 0,
        lot: t.lot || 0,
        rr: '—',
        pnl: t.pnl || 0,
        dur: '—',
        tag: 'Manual',
    })), [localJournal]);

    const savePlan = async () => {
        try {
            await axios.post(`${WEB_API}/plan/`, {
                notes: tradingPlan,
                title: "My Trading Plan",
            }, { headers: getHeaders() });
        } catch {
            // Fallback to localStorage if API unavailable
            localStorage.setItem('gas-trading-plan', tradingPlan);
        }
        setPlanSaved(true);
        setTimeout(() => setPlanSaved(false), 2000);
    };

    useEffect(() => {
        // Load plan from backend first, localStorage as fallback
        axios.get(`${WEB_API}/plan/`, { headers: getHeaders() })
            .then(res => {
                const notes = res.data?.plan?.notes;
                if (notes) setTradingPlan(notes);
                else {
                    const saved = localStorage.getItem('gas-trading-plan');
                    if (saved) setTradingPlan(saved);
                }
            })
            .catch(() => {
                const saved = localStorage.getItem('gas-trading-plan');
                if (saved) setTradingPlan(saved);
            });
    }, []);

    const filteredJournal = useMemo(() => {
        let d = [...journalForTable];
        if (journalFilter === 'win') d = d.filter(t => t.pnl > 0);
        if (journalFilter === 'loss') d = d.filter(t => t.pnl < 0);
        if (journalFilter === 'buy') d = d.filter(t => t.dir === 'BUY');
        if (journalFilter === 'sell') d = d.filter(t => t.dir === 'SELL');
        d.sort((a, b) => {
            if (sortCol === 'pnl') return sortAsc ? a.pnl - b.pnl : b.pnl - a.pnl;
            return sortAsc ? a.id - b.id : b.id - a.id;
        });
        return d;
    }, [journalForTable, journalFilter, sortCol, sortAsc]);

    const exportCSV = () => {
        const rows = ['Time,Asset,Dir,Entry,Exit,Lot,P&L,Tag'];
        journalForTable.forEach(t => rows.push(`${t.time},${t.asset},${t.dir},${t.entry},${t.exit},${t.lot},${t.pnl},${t.tag}`));
        const blob = new Blob([rows.join('\n')], { type: 'text/csv' });
        const a = document.createElement('a'); a.href = URL.createObjectURL(blob);
        a.download = 'gas_journal.csv'; a.click();
    };

    const TABS = [
        { id: 'dashboard', label: '📊 Dashboard', icon: BarChart2 },
        { id: 'positions', label: `📌 Positions ${openPositions.length > 0 ? `(${openPositions.length})` : ''}`, icon: Activity },
        { id: 'journal',   label: '📒 Journal',   icon: BookOpen },
        { id: 'backtest',  label: '🔬 Backtest',  icon: Activity },
        { id: 'plan',      label: '📋 Trading Plan', icon: FileText },
    ];

    const modeLabel = accountMode === 'user_ea' ? '🟢 User EA' : accountMode === 'main_ea' ? '🟡 Main EA' : '🔴 Offline';
    const acctSubtitle = liveData?.account_id
        ? `MT5 #${liveData.account_id} · ${liveData.broker || ''} · ${liveData.currency || 'USD'}`
        : liveData?.symbol
        ? `MT5 EA · ${liveData.symbol} · Main EA`
        : 'MT5 EA · Waiting for heartbeat...';

    return (
        <div className="p-4 md:p-6 pb-24 md:pb-8 max-w-7xl mx-auto space-y-5">

            {/* ── PAGE HEADER ── */}
            <div className="flex items-center justify-between flex-wrap gap-3">
                <div>
                    <h2 className="text-2xl font-display font-black uppercase">Portfolio</h2>
                    <p className="text-[11px] text-[var(--text-dim)] font-bold mt-0.5">{acctSubtitle}</p>
                </div>
                <div className="flex items-center gap-2">
                    <button onClick={loadLiveData} className="text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors">
                        <RefreshCw size={13} className={liveLoading ? 'animate-spin' : ''} />
                    </button>
                    {liveStatus === 'live' ? (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[var(--success)]/10 border border-[var(--success)]/20">
                            <Wifi size={11} className="text-[var(--success)]" />
                            <div className="w-1.5 h-1.5 rounded-full bg-[var(--success)] animate-pulse" />
                            <span className="text-[10px] font-black text-[var(--success)] uppercase">MT5 Live</span>
                        </div>
                    ) : liveStatus === 'loading' ? (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-yellow-400/10 border border-yellow-400/20">
                            <RefreshCw size={11} className="text-yellow-400 animate-spin" />
                            <span className="text-[10px] font-black text-yellow-400 uppercase">Connecting...</span>
                        </div>
                    ) : (
                        <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-red-500/10 border border-red-500/20">
                            <WifiOff size={11} className="text-red-400" />
                            <span className="text-[10px] font-black text-red-400 uppercase">EA Offline</span>
                        </div>
                    )}
                </div>
            </div>

            {/* EA Offline Banner */}
            {liveStatus === 'no_heartbeat' && (
                <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-yellow-400/10 border border-yellow-400/30">
                    <AlertTriangle size={15} className="text-yellow-400 shrink-0" />
                    <div>
                        <p className="text-xs font-black text-yellow-400">EA Heartbeat Tidak Diterima</p>
                        <p className="text-[10px] text-[var(--text-dim)]">Pastikan EA Golden AI Strategy v4.0 berjalan di MT5 dan terhubung ke GAS_SECURE_GATEWAY</p>
                    </div>
                </div>
            )}

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
                TAB: POSITIONS (Live MT5 Open Trades)
            ══════════════════════════════════════════════ */}
            {tab === 'positions' && (
                <div className="space-y-4">
                    {/* Mode Badge */}
                    <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border ${accountMode === 'user_ea' ? 'bg-green-500/5 border-green-500/20' : accountMode === 'main_ea' ? 'bg-yellow-400/5 border-yellow-400/20' : 'bg-red-500/5 border-red-500/20'}`}>
                        <span className="text-base">{accountMode === 'user_ea' ? '🟢' : accountMode === 'main_ea' ? '🟡' : '🔴'}</span>
                        <div className="flex-1">
                            <p className="text-xs font-black text-[var(--text-primary)]">
                                Mode: {accountMode === 'user_ea' ? 'Per-User EA (Akurat)' : accountMode === 'main_ea' ? 'Main EA (Shared)' : 'Offline'}
                            </p>
                            <p className="text-[10px] text-[var(--text-dim)]">
                                {accountMode === 'user_ea'
                                    ? `Akun: #${liveData?.account_id || '?'} · ${liveData?.broker || ''} · ${liveData?.leverage || '?'}x Leverage`
                                    : accountMode === 'main_ea'
                                    ? 'Kirim EA per-user untuk melihat posisi akun kamu sendiri'
                                    : 'Tidak ada EA terhubung. Setup EA User di bawah.'}
                            </p>
                        </div>
                        {liveData?.account_id && (
                            <span className="text-[9px] font-black px-2 py-1 rounded-lg bg-[var(--accent)]/10 text-[var(--accent)]">
                                {liveData.currency || 'USD'} Account
                            </span>
                        )}
                    </div>

                    {/* Live Account KPIs */}
                    {liveData?.balance && (
                        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                            <KpiCard label="Balance" value={`$${parseFloat(liveData.balance).toLocaleString()}`} sub="Saldo akun" icon={DollarSign} highlight />
                            <KpiCard label="Equity" value={`$${parseFloat(liveData.equity).toLocaleString()}`} sub="Termasuk floating" icon={TrendingUp} up={liveData.floating_pnl >= 0} />
                            <KpiCard label="Floating P&L" value={`${liveData.floating_pnl >= 0 ? '+' : ''}$${parseFloat(liveData.floating_pnl || 0).toFixed(2)}`} sub="Posisi terbuka" icon={Activity} up={liveData.floating_pnl >= 0} />
                            <KpiCard label="Free Margin" value={`$${parseFloat(liveData.free_margin || liveData.equity || 0).toLocaleString()}`} sub="Margin tersedia" icon={Shield} />
                        </div>
                    )}

                    {/* Positions Table */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                        <div className="px-5 py-3 bg-[var(--bg-panel)] border-b border-[var(--border-color)] flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <div className={`w-2 h-2 rounded-full ${openPositions.length > 0 ? 'bg-green-400 animate-pulse' : 'bg-gray-500'}`} />
                                <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-dim)]">
                                    Open Positions ({openPositions.length})
                                </span>
                            </div>
                            <button onClick={loadLiveData} className="text-[var(--text-dim)] hover:text-[var(--accent)] transition-colors">
                                <RefreshCw size={12} className={liveLoading ? 'animate-spin' : ''} />
                            </button>
                        </div>
                        {openPositions.length > 0 ? (
                            <div className="overflow-x-auto">
                                <table className="w-full text-xs min-w-[700px]">
                                    <thead>
                                        <tr className="bg-[var(--bg-panel)] border-b border-[var(--border-color)]">
                                            {['Ticket', 'Symbol', 'Arah', 'Lot', 'Entry', 'Current', 'P&L', 'Swap', 'Magic'].map(h => (
                                                <th key={h} className="px-4 py-2.5 text-left text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">{h}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {openPositions.map((pos, i) => {
                                            const pnl = parseFloat(pos.pnl || 0);
                                            const isWin = pnl >= 0;
                                            return (
                                                <tr key={i} className="border-b border-[var(--border-color)] hover:bg-[var(--bg-hover)] transition-colors">
                                                    <td className="px-4 py-3 font-mono text-[var(--text-dim)] text-[11px]">{pos.ticket || '—'}</td>
                                                    <td className="px-4 py-3 font-black text-[var(--text-primary)]">{pos.symbol}</td>
                                                    <td className="px-4 py-3">
                                                        <span className={`px-2 py-0.5 rounded text-[9px] font-black tracking-widest ${pos.direction === 'BUY' ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'}`}>
                                                            {pos.direction}
                                                        </span>
                                                    </td>
                                                    <td className="px-4 py-3 font-mono text-[var(--text-secondary)]">{pos.lot}</td>
                                                    <td className="px-4 py-3 font-mono text-[var(--text-secondary)]">{pos.entry_price}</td>
                                                    <td className="px-4 py-3 font-mono text-[var(--text-secondary)]">{pos.current_price || '—'}</td>
                                                    <td className={`px-4 py-3 font-mono font-black text-sm ${isWin ? 'text-green-400' : 'text-red-400'}`}>
                                                        {isWin ? '+' : ''}${pnl.toFixed(2)}
                                                    </td>
                                                    <td className="px-4 py-3 font-mono text-[var(--text-dim)] text-[11px]">{pos.swap || 0}</td>
                                                    <td className="px-4 py-3 font-mono text-[var(--text-dim)] text-[11px]">{pos.magic || '—'}</td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                                {/* Summary Row */}
                                <div className="px-5 py-3 bg-[var(--bg-panel)] border-t border-[var(--border-color)] flex justify-between items-center">
                                    <span className="text-[10px] text-[var(--text-dim)]">{openPositions.length} posisi terbuka</span>
                                    <span className={`text-sm font-black font-mono ${openPositions.reduce((s, p) => s + parseFloat(p.pnl || 0), 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                                        Total: {openPositions.reduce((s, p) => s + parseFloat(p.pnl || 0), 0) >= 0 ? '+' : ''}
                                        ${openPositions.reduce((s, p) => s + parseFloat(p.pnl || 0), 0).toFixed(2)}
                                    </span>
                                </div>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center py-12 text-[var(--text-dim)] space-y-3">
                                <Activity size={28} className="opacity-20" />
                                <p className="text-xs font-black">Tidak ada posisi terbuka</p>
                                <p className="text-[10px]">
                                    {accountMode === 'offline'
                                        ? 'Setup EA per-user untuk melihat posisi realtime'
                                        : 'Semua posisi sudah ditutup — tidak ada trade aktif'}
                                </p>
                            </div>
                        )}
                    </div>

                    {/* EA Setup Guide for this user */}
                    {accountMode !== 'user_ea' && (
                        <div className="bg-[var(--bg-card)] border border-[var(--accent)]/20 rounded-xl overflow-hidden">
                            <div className="px-5 py-3 bg-[var(--accent)]/10 border-b border-[var(--accent)]/20">
                                <p className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)]">🚀 Setup Per-User EA untuk akun kamu</p>
                            </div>
                            <div className="p-5 space-y-3">
                                <p className="text-xs text-[var(--text-secondary)] leading-relaxed">
                                    Pasang <strong>GAS_AccountHeartbeat.ex5</strong> di MT5 kamu, lalu isi parameter berikut:
                                </p>
                                <div className="bg-[var(--bg-panel)] rounded-xl p-4 font-mono text-[10px] space-y-1.5">
                                    <div className="flex gap-2"><span className="text-[var(--text-dim)] w-24">UserID</span><span className="text-[var(--accent)]">{liveData?.user_id || '<isi user ID kamu>'}</span></div>
                                    <div className="flex gap-2"><span className="text-[var(--text-dim)] w-24">GAS_GATEWAY</span><span className="text-yellow-400">GAS_SECURE_GATEWAY</span></div>
                                    <div className="flex gap-2"><span className="text-[var(--text-dim)] w-24">Interval</span><span className="text-green-400">10 detik</span></div>
                                </div>
                                <p className="text-[10px] text-[var(--text-dim)]">
                                    Download: <span className="text-[var(--accent)] font-bold">GAS_AccountHeartbeat.mq5</span> tersedia di Dashboard → Files
                                </p>
                            </div>
                        </div>
                    )}
                </div>
            )}

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
                                    <p className="text-[10px] text-[var(--text-dim)]">Start: ${METRICS.startBalance.toLocaleString()}</p>
                                    <p className="text-[10px] text-[var(--text-dim)]">Now: ${METRICS.balance.toLocaleString()}</p>
                                </div>
                            </div>
                            {equityData.length > 1 ? (
                                <EquityChart data={equityData} theme={theme} />
                            ) : (
                                <div className="flex items-center justify-center h-32 text-[var(--text-dim)]">
                                    <div className="text-center">
                                        <Activity size={24} className="mx-auto mb-2 opacity-20" />
                                        <p className="text-xs font-bold">Koneksi EA MT5 untuk melihat equity curve</p>
                                    </div>
                                </div>
                            )}
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
                                {assetDist.length > 0 ? (
                                    <div className="space-y-2">
                                        {assetDist.map((a, i) => (
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
                                ) : (
                                    <div className="flex items-center justify-center h-20 text-center">
                                        <p className="text-[10px] text-[var(--text-dim)]">Catat trade di Journal<br/>untuk melihat distribusi aset</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>

                    {/* Charts Row 2: Daily P&L + Monthly Returns */}
                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-5">
                        <div className="xl:col-span-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                            <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-1">Daily P&L</p>
                            <p className="text-[10px] text-[var(--text-dim)] mb-3">Data dari EA MT5</p>
                            {dailyPnlData.length > 0 ? (
                                <PnLChart data={dailyPnlData} theme={theme} />
                            ) : (
                                <div className="flex items-center justify-center h-32 text-[var(--text-dim)]">
                                    <div className="text-center">
                                        <BarChart2 size={24} className="mx-auto mb-2 opacity-20" />
                                        <p className="text-xs font-bold">Koneksi EA MT5 untuk melihat Daily P&L</p>
                                    </div>
                                </div>
                            )}
                        </div>

                        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                            <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Monthly Returns</p>
                            {monthlyReturns.length > 0 ? (
                                <>
                                    <MiniBar data={monthlyReturns} />
                                    <div className="mt-3 space-y-1.5">
                                        {monthlyReturns.map((m, i) => (
                                            <div key={i} className="flex items-center justify-between text-[10px]">
                                                <span className="text-[var(--text-dim)] font-bold w-8">{m.m}</span>
                                                <div className="flex-1 mx-2 h-1 bg-[var(--bg-panel)] rounded-full overflow-hidden">
                                                    <div className="h-full rounded-full" style={{
                                                        width: `${Math.min(100, Math.abs(m.v) * 7)}%`,
                                                        background: m.v >= 0 ? 'var(--success)' : 'var(--danger)'
                                                    }} />
                                                </div>
                                                <span className={`font-black font-mono w-12 text-right ${m.v >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                    {m.v >= 0 ? '+' : ''}{m.v}%
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </>
                            ) : (
                                <div className="flex items-center justify-center h-32 text-center">
                                    <p className="text-[10px] text-[var(--text-dim)]">Catat trade di Journal<br/>untuk melihat monthly returns</p>
                                </div>
                            )}
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
                        <KpiCard label="Total Trades" value={journalForTable.length} icon={BarChart2} />
                        <KpiCard label="Total P&L" value={journalForTable.length ? `${journalForTable.reduce((a, t) => a + t.pnl, 0) >= 0 ? '+' : ''}$${journalForTable.reduce((a, t) => a + t.pnl, 0).toFixed(2)}` : '$0'} up={journalForTable.reduce((a, t) => a + t.pnl, 0) >= 0} icon={TrendingUp} />
                        <KpiCard label="Best Trade" value={journalForTable.length ? `+$${Math.max(...journalForTable.map(t => t.pnl)).toFixed(2)}` : '$0'} up={true} icon={Award} />
                        <KpiCard label="Worst Trade" value={journalForTable.length ? `$${Math.min(...journalForTable.map(t => t.pnl)).toFixed(2)}` : '$0'} up={false} icon={AlertTriangle} />
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

                    {journalForTable.length === 0 && (
                        <div className="text-center py-12 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl">
                            <BookOpen size={32} className="mx-auto mb-3 opacity-20 text-[var(--text-dim)]" />
                            <p className="text-sm font-bold text-[var(--text-dim)]">Journal masih kosong</p>
                            <p className="text-[10px] text-[var(--text-dim)] mt-1">Buka tab Journal di sidebar untuk mencatat trade pertama kamu</p>
                        </div>
                    )}

                    {/* Journal Table */}
                    {journalForTable.length > 0 && (
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
                            <span className="text-[10px] text-[var(--text-dim)]">Menampilkan {filteredJournal.length} dari {journalForTable.length} trade</span>
                            <span className={`text-sm font-black font-mono ${filteredJournal.reduce((a, t) => a + t.pnl, 0) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                Total: {filteredJournal.reduce((a, t) => a + t.pnl, 0) >= 0 ? '+' : ''}${filteredJournal.reduce((a, t) => a + t.pnl, 0).toFixed(2)}
                            </span>
                        </div>
                    </div>
                    )}
                </div>
            )}

            {/* ══════════════════════════════════════════════
                TAB: BACKTEST
            ══════════════════════════════════════════════ */}
            {tab === 'backtest' && (
                <div className="space-y-5">
                    {/* Redirect to AI Backtesting feature */}
                    <div className="bg-[var(--bg-card)] border border-[var(--accent)]/20 rounded-xl p-6 text-center space-y-4">
                        <div className="w-12 h-12 rounded-xl bg-[var(--accent)]/10 border border-[var(--accent)]/20 flex items-center justify-center mx-auto">
                            <Activity size={22} className="text-[var(--accent)]" />
                        </div>
                        <div>
                            <h3 className="text-base font-black text-[var(--text-primary)]">AI Backtesting</h3>
                            <p className="text-xs text-[var(--text-dim)] mt-1 max-w-md mx-auto">
                                Gunakan fitur AI Backtesting di sidebar untuk menjalankan backtest real dengan data MT5 — hasil statistik aktual, equity curve, dan monthly returns akan muncul di sini.
                            </p>
                        </div>
                        <div className="flex flex-wrap justify-center gap-3 text-[10px] text-[var(--text-dim)]">
                            {['Total Trades', 'Win Rate', 'Profit Factor', 'Max DD', 'Sharpe', 'Avg R:R'].map(s => (
                                <span key={s} className="px-3 py-1.5 rounded-lg border border-[var(--border-color)] bg-[var(--bg-panel)] font-bold">{s}: —</span>
                            ))}
                        </div>
                        <p className="text-[10px] text-[var(--accent)] font-bold">Buka menu AI → Backtesting untuk menjalankan backtest · 20 cr</p>
                    </div>

                    {/* Placeholder sections (will show real data after BacktestView is run) */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5">
                        <p className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)] mb-4">Equity Curve</p>
                        <div className="flex items-center justify-center h-32 text-[var(--text-dim)]">
                            <div className="text-center">
                                <BarChart2 size={24} className="mx-auto mb-2 opacity-20" />
                                <p className="text-xs font-bold">Jalankan AI Backtesting untuk melihat equity curve</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden">
                        <div className="px-5 py-3 border-b border-[var(--border-color)] bg-[var(--bg-panel)]">
                            <span className="text-xs font-black uppercase tracking-widest text-[var(--text-dim)]">Monthly Backtest Returns</span>
                        </div>
                        <div className="flex items-center justify-center py-12 text-[var(--text-dim)]">
                            <p className="text-xs font-bold">Belum ada data backtest</p>
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
                                'Review signal Golden AI Strategy terbaru',
                                'Hitung lot size berdasarkan balance',
                                'Set SL/TP sebelum entry',
                                'Cek sentimen market (Risk On/Off)',
                                'Tidak trading kalau mood negatif',
                                'Max 3 posisi terbuka sekaligus',
                                'Stop jika DD harian sudah -2%',
                            ].map((item, i) => (
                                <ChecklistItem key={i} label={item} />
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
