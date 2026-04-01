import React, { useState, useEffect, useCallback, useMemo, useRef } from 'react';
import Sparkline from './Sparkline';
import { ChevronUp, ChevronDown, BarChart3, RefreshCw, Activity, TrendingUp, TrendingDown } from 'lucide-react';
import TradingViewChart from './TradingViewChart';
import TradingViewWidget from './TradingViewWidget';
import StaticChart from './StaticChart';
import { fetchBinanceOrderbook } from '../services/api';

// ── Market Session / Status helper ────────────────────────────────────────────
function getMarketStatus(symbol, pairType) {
    const now = new Date();
    const utcDay = now.getUTCDay();   // 0=Sun, 6=Sat
    const utcHour = now.getUTCHours();
    const utcMin = now.getUTCMinutes();

    if (pairType === 'Crypto' || (symbol && symbol.includes('/'))) {
        return { open: true, label: '24/7', color: '#22c55e' };
    }

    // Sat all day → closed
    if (utcDay === 6) return { open: false, label: 'TUTUP · Weekend', color: '#ef4444' };
    // Sun before 22:00 UTC → closed
    if (utcDay === 0 && utcHour < 22) return { open: false, label: 'TUTUP · Weekend', color: '#ef4444' };
    // Fri ≥ 22:00 UTC → closed
    if (utcDay === 5 && utcHour >= 22) return { open: false, label: 'TUTUP · Weekend', color: '#ef4444' };

    // US Index CME daily break 22:00–23:00 UTC
    if ((pairType === 'Index') && ['US30','US500','USTEC','NAS100'].includes(symbol)) {
        if (utcHour === 22) return { open: false, label: 'TUTUP · CME Break', color: '#f59e0b' };
        if (utcHour >= 14 && utcHour < 21) return { open: true, label: 'NYSE Regular', color: '#22c55e' };
        return { open: true, label: 'CME Futures', color: '#3b82f6' };
    }

    // Forex/Commodity session
    let session;
    if (utcHour >= 22 || utcHour < 7) session = 'Sydney/Tokyo';
    else if (utcHour < 8) session = 'Tokyo/London';
    else if (utcHour < 12) session = 'London';
    else if (utcHour < 17) session = 'London/NY';
    else if (utcHour < 21) session = 'New York';
    else session = 'NY Close';

    return { open: true, label: session, color: '#22c55e' };
}

export default function MarketsView({ pairs, prices, directions, onSelect, activePair, theme, chartPair }) {
    const [tab, setTab] = useState('All');
    const [timeframe, setTimeframe] = useState('15m');
    const [chartMode, setChartMode] = useState('interactive');
    const [cryptoTickers, setCryptoTickers] = useState({});
    const [orderbook, setOrderbook] = useState(null);
    const [loadingCrypto, setLoadingCrypto] = useState(true);
    const [loadingOrderbook, setLoadingOrderbook] = useState(false);
    const [cryptoError, setCryptoError] = useState(null);
    const [wsConnected, setWsConnected] = useState(false);
    const wsRef = useRef(null);

    // Derive crypto spot pairs dynamically from props (exclude futures with ':')
    const cryptoPairs = useMemo(() =>
        pairs.filter(p => (p.type === 'Crypto' || p.type === 'Futures') && p.symbol.includes('/')),
        [pairs]
    );
    const cryptoSpotPairs = useMemo(() =>
        pairs.filter(p => p.type === 'Crypto' && p.symbol.includes('/') && !p.symbol.includes(':')),
        [pairs]
    );
    const cryptoSymbols = useMemo(() => cryptoSpotPairs.map(p => p.symbol), [cryptoSpotPairs]);

    const selectedPairData = pairs.find(p => p.symbol === activePair) || pairs[0];

    // Build grouped list with section headers for MT5 tabs
    const getFilteredWithHeaders = (tab) => {
        const mt5 = pairs.filter(p => !p.symbol.includes('/'));
        const withHeaders = (sections) => sections.flatMap(([label, items]) =>
            items.length ? [{ _header: label }, ...items] : []
        );
        if (tab === 'All') return withHeaders([
            ['★ FOREX MAJOR',       mt5.filter(p => p.type === 'Forex' && p.subType === 'Major')],
            ['FOREX MINOR',         mt5.filter(p => p.type === 'Forex' && p.subType === 'Minor')],
            ['✦ PRECIOUS METALS',   mt5.filter(p => p.type === 'Commodity' && p.subType === 'Precious')],
            ['⚙ INDUSTRIAL METALS', mt5.filter(p => p.type === 'Commodity' && p.subType === 'Industrial')],
            ['⚡ ENERGY',            mt5.filter(p => p.type === 'Commodity' && p.subType === 'Energy')],
            ['📊 US INDICES',        mt5.filter(p => p.type === 'Index' && p.subType === 'US')],
            ['📊 EU INDICES',        mt5.filter(p => p.type === 'Index' && p.subType === 'Europe')],
            ['📊 ASIA INDICES',      mt5.filter(p => p.type === 'Index' && p.subType === 'Asia')],
            ['🇺🇸 US STOCKS',        mt5.filter(p => p.type === 'StockUS')],
            ['🌍 GLOBAL STOCKS',     mt5.filter(p => p.type === 'StockGlobal')],
        ]);
        if (tab === 'Forex') return withHeaders([
            ['★ MAJOR PAIRS',       mt5.filter(p => p.type === 'Forex' && p.subType === 'Major')],
            ['MINOR / CROSS PAIRS', mt5.filter(p => p.type === 'Forex' && p.subType === 'Minor')],
        ]);
        if (tab === 'Commodity') return withHeaders([
            ['✦ PRECIOUS METALS',   mt5.filter(p => p.type === 'Commodity' && p.subType === 'Precious')],
            ['⚙ INDUSTRIAL METALS', mt5.filter(p => p.type === 'Commodity' && p.subType === 'Industrial')],
            ['⚡ ENERGY',            mt5.filter(p => p.type === 'Commodity' && p.subType === 'Energy')],
        ]);
        if (tab === 'Index') return withHeaders([
            ['🇺🇸 UNITED STATES',   mt5.filter(p => p.type === 'Index' && p.subType === 'US')],
            ['🇪🇺 EUROPE',          mt5.filter(p => p.type === 'Index' && p.subType === 'Europe')],
            ['🌏 ASIA PACIFIC',     mt5.filter(p => p.type === 'Index' && p.subType === 'Asia')],
            ['OTHER',              mt5.filter(p => p.type === 'Index' && p.subType === 'Other')],
        ]);
        if (tab === 'Stocks') return withHeaders([
            ['🇺🇸 US STOCKS',    mt5.filter(p => p.type === 'StockUS')],
            ['🌍 GLOBAL STOCKS', mt5.filter(p => p.type === 'StockGlobal')],
        ]);
        return [];
    };
    const curPrice = prices[activePair] || selectedPairData?.base || 0;
    const isCrypto = activePair && (activePair.includes('/') || activePair.includes('BTC') || activePair.includes('ETH') || activePair.includes('SOL'));

    const loadOrderbook = useCallback(async (symbol) => {
        if (!symbol || !symbol.includes('/')) return;
        setLoadingOrderbook(true);
        try {
            const data = await fetchBinanceOrderbook(symbol, 8);
            setOrderbook(data);
        } catch {
            setOrderbook(null);
        } finally {
            setLoadingOrderbook(false);
        }
    }, []);

    // ── Binance WebSocket (real-time tickers every 2s) ────────────────────────
    useEffect(() => {
        if (cryptoSymbols.length === 0) return;
        const proto = window.location.protocol === 'https:' ? 'wss' : 'ws';
        const wsUrl = `${proto}://${window.location.host}/terminal/ws/binance`;

        let ws;
        let reconnectTimer;
        let alive = true;

        const connect = () => {
            if (!alive) return;
            ws = new WebSocket(wsUrl);
            wsRef.current = ws;

            ws.onopen = () => {
                setWsConnected(true);
                setCryptoError(null);
                // Send desired symbols
                ws.send(JSON.stringify({ symbols: cryptoSymbols.join(',') }));
            };

            ws.onmessage = (e) => {
                try {
                    const msg = JSON.parse(e.data);
                    if (msg.type === 'tickers' && msg.data) {
                        setCryptoTickers(msg.data);
                        setLoadingCrypto(false);
                    }
                } catch (_) {}
            };

            ws.onerror = () => {
                setWsConnected(false);
                setCryptoError('WebSocket error — retrying...');
            };

            ws.onclose = () => {
                setWsConnected(false);
                if (alive) reconnectTimer = setTimeout(connect, 4000);
            };
        };

        connect();
        return () => {
            alive = false;
            clearTimeout(reconnectTimer);
            if (ws) ws.close();
        };
    }, [cryptoSymbols]);

    useEffect(() => {
        if (activePair && activePair.includes('/')) {
            loadOrderbook(activePair);
        }
    }, [activePair, loadOrderbook]);

    const getTickerForPair = (symbol) => {
        return cryptoTickers[symbol] || null;
    };

    const formatPrice = (val, isFx) => {
        if (!val && val !== 0) return '--';
        return Number(val).toFixed(isFx ? 4 : 2);
    };

    const formatChange = (val) => {
        if (!val && val !== 0) return '--';
        const n = Number(val);
        return `${n >= 0 ? '+' : ''}${n.toFixed(2)}%`;
    };

    return (
        <div className="h-full flex flex-col p-2 md:p-3 space-y-3 overflow-hidden bg-[var(--bg-main)]">
            {/* Top Stat Bar */}
            <div className="flex items-center justify-between px-4 py-2 bg-[var(--bg-card)] border border-[var(--border-color)] rounded-lg shadow-sm">
                <div className="flex items-center gap-4">
                    <div className="flex flex-col">
                        <span className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">Active Market</span>
                        <div className="flex items-center gap-2">
                            <span className="text-lg font-black text-[var(--text-primary)]">{activePair}</span>
                            <span className={`text-xs font-mono font-bold ${directions[activePair] === 'up' ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                {activePair && activePair.includes('/') && cryptoTickers[activePair]
                                    ? formatPrice(cryptoTickers[activePair].last, false)
                                    : curPrice.toFixed(selectedPairData?.type === 'Forex' ? 4 : 2)
                                }
                            </span>
                            {activePair && activePair.includes('/') && cryptoTickers[activePair] && (
                                <span className={`text-[10px] font-mono font-bold px-1.5 py-0.5 rounded ${Number(cryptoTickers[activePair].changePercent) >= 0 ? 'bg-[var(--success)]/10 text-[var(--success)]' : 'bg-[var(--danger)]/10 text-[var(--danger)]'}`}>
                                    {formatChange(cryptoTickers[activePair].changePercent)}
                                </span>
                            )}
                        </div>
                    </div>
                    <div className="h-8 w-px bg-[var(--border-color)] hidden md:block" />
                    <div className="hidden md:flex flex-col">
                        <span className="text-[10px] text-[var(--text-dim)] font-black uppercase tracking-widest">24h Change</span>
                        <span className={`text-xs font-mono font-bold ${(curPrice - selectedPairData?.base) >= 0 ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                            {((curPrice - selectedPairData?.base) / selectedPairData?.base * 100).toFixed(2)}%
                        </span>
                    </div>
                    {/* Binance WebSocket Badge */}
                    {(tab === 'Crypto' || tab === 'Futures') && (
                        <div className={`hidden md:flex items-center gap-1.5 px-2 py-1 rounded-full border ${
                            wsConnected
                                ? 'bg-[var(--accent)]/10 border-[var(--accent)]/30'
                                : 'bg-red-500/10 border-red-500/30'
                        }`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${wsConnected ? 'bg-[var(--accent)] animate-pulse' : 'bg-red-400'}`} />
                            <span className={`text-[9px] font-black uppercase tracking-widest ${wsConnected ? 'text-[var(--accent)]' : 'text-red-400'}`}>
                                {wsConnected ? 'Binance WS Live' : 'Reconnecting...'}
                            </span>
                        </div>
                    )}
                </div>
                <div className="flex items-center gap-2">
                    {(tab === 'Crypto' || tab === 'Futures') && loadingCrypto && (
                        <RefreshCw size={12} className="animate-spin text-[var(--text-dim)]" />
                    )}
                    <div className="flex items-center gap-1 bg-[var(--bg-panel)] p-1 rounded-lg border border-[var(--border-color)] mr-2">
                        <button
                            onClick={() => setChartMode('interactive')}
                            className={`text-[9px] px-2 py-1 rounded transition-all font-black uppercase ${chartMode === 'interactive' ? 'bg-[var(--accent)] text-black' : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)]'}`}
                        >
                            Interactive
                        </button>
                        <button
                            onClick={() => setChartMode('expert')}
                            className={`text-[9px] px-2 py-1 rounded transition-all font-black uppercase ${chartMode === 'expert' ? 'bg-[var(--accent)] text-black' : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)]'}`}
                        >
                            Expert
                        </button>
                    </div>
                    <div className="flex items-center gap-2 bg-[var(--bg-panel)] p-1 rounded-lg border border-[var(--border-color)]">
                        {['1m', '5m', '15m', '1h', '4h', '1d'].map(tf => (
                            <button
                                key={tf}
                                onClick={() => setTimeframe(tf)}
                                className={`text-[9px] px-2.5 py-1.5 rounded transition-all font-black uppercase ${tf === timeframe ? 'bg-[var(--accent)] text-black shadow-lg' : 'text-[var(--text-dim)] hover:text-[var(--text-secondary)] hover:bg-[var(--bg-hover)]'}`}
                            >
                                {tf}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Terminal Grid */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-[280px_1fr_300px] gap-3 min-h-0">

                {/* Left Pane: Market List */}
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl flex flex-col overflow-hidden shadow-xl">
                    {/* Scrollable tabs */}
                    <div className="flex border-b border-[var(--border-color)] bg-[var(--bg-panel)]/50 overflow-x-auto scrollbar-none">
                        {['All', 'Forex', 'Commodity', 'Index', 'Stocks', 'Crypto', 'Futures'].map(t => (
                            <button key={t} onClick={() => setTab(t)}
                                className={`flex-none px-3 py-2 text-[9px] font-black uppercase tracking-widest transition-all whitespace-nowrap ${tab === t ? 'text-[var(--accent)] bg-[var(--bg-hover)] border-b-2 border-[var(--accent)]' : 'text-[var(--text-dim)] hover:text-[var(--text-primary)]'}`}>
                                {t}
                            </button>
                        ))}
                    </div>

                    {/* Crypto / Futures Tabs — Binance Live Data */}
                    {(tab === 'Crypto' || tab === 'Futures') ? (
                        <div className="flex-1 overflow-y-auto scrollbar-none divide-y divide-[var(--border-color)]">
                            {cryptoError && (
                                <div className="px-4 py-3 text-[10px] text-[var(--danger)] font-mono">{cryptoError}</div>
                            )}
                            {cryptoPairs
                                .filter(p => tab === 'Crypto' ? p.type === 'Crypto' : p.type === 'Futures')
                                .map(({ symbol: sym, type: pType }) => {
                                const ticker = cryptoTickers[sym];
                                const isActive = activePair === sym;
                                const chg = ticker ? Number(ticker.changePercent) : 0;
                                const isUp = chg >= 0;
                                const isFutures = pType === 'Futures' || sym.includes(':');
                                return (
                                    <div key={sym} onClick={() => onSelect(sym)}
                                        className={`px-4 py-3 cursor-pointer transition-all hover:bg-[var(--bg-hover)] group ${isActive ? 'bg-[var(--accent-soft)] border-l-2 border-[var(--accent)]' : ''}`}>
                                        <div className="flex justify-between items-start mb-1">
                                            <div className="flex items-center gap-1.5">
                                                <span className={`text-xs font-black ${isActive ? 'text-[var(--accent)]' : 'text-[var(--text-primary)]'}`}>{sym}</span>
                                                <span className={`text-[8px] px-1 py-0.5 rounded font-bold uppercase ${isFutures ? 'bg-purple-500/10 text-purple-400' : 'bg-[var(--accent)]/10 text-[var(--accent)]'}`}>
                                                    {isFutures ? 'PERP' : 'SPOT'}
                                                </span>
                                            </div>
                                            <span className={`text-[11px] font-mono font-bold ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                {ticker ? formatPrice(ticker.last, false) : (loadingCrypto ? '…' : '--')}
                                            </span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className={`text-[9px] font-bold ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'}`}>
                                                {ticker ? formatChange(ticker.changePercent) : ''}
                                            </span>
                                            <span className="text-[9px] text-[var(--text-dim)]">
                                                {ticker ? `Vol: ${Number(ticker.volume || 0).toLocaleString('en', { notation: 'compact', maximumFractionDigits: 1 })}` : ''}
                                            </span>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    ) : (
                        /* MT5 Tabs — grouped with section headers */
                        <div className="flex-1 overflow-y-auto scrollbar-none">
                            {getFilteredWithHeaders(tab).map((item, idx) => {
                                if (item._header) {
                                    return (
                                        <div key={`h-${idx}`} className="px-4 py-1.5 sticky top-0 z-10 bg-[var(--bg-panel)]/95 backdrop-blur-sm border-b border-[var(--border-color)]">
                                            <span className="text-[8px] font-black uppercase tracking-widest text-[var(--accent)]">{item._header}</span>
                                        </div>
                                    );
                                }
                                const p = item;
                                const cur = prices[p.symbol] || p.price || p.base;
                                const isUp = (cur - p.base) >= 0;
                                const isActive = activePair === p.symbol;
                                const decimals = p.type === 'Forex' ? 4
                                    : (p.type === 'StockUS' || p.type === 'StockGlobal') ? 2
                                    : p.base >= 10000 ? 0 : p.base >= 100 ? 2 : p.base >= 1 ? 2 : 4;
                                const mktStatus = getMarketStatus(p.symbol, p.type);
                                const priceDisplay = cur && cur > 0 ? cur.toFixed(decimals) : (p.prev_close ? p.prev_close.toFixed(decimals) : '—');
                                const showStaleLabel = (!cur || cur === 0) && p.prev_close;
                                return (
                                    <div key={p.symbol} onClick={() => onSelect(p.symbol)}
                                        className={`px-4 py-3 cursor-pointer transition-all hover:bg-[var(--bg-hover)] group border-b border-[var(--border-color)] ${isActive ? 'bg-[var(--accent-soft)] border-l-2 border-[var(--accent)]' : ''}`}>
                                        <div className="flex justify-between items-start mb-1">
                                            <div className="flex items-center gap-1.5">
                                                <span className={`text-xs font-black ${isActive ? 'text-[var(--accent)]' : 'text-[var(--text-primary)]'}`}>{p.symbol}</span>
                                                {/* Market open/closed dot */}
                                                <span style={{
                                                    width: 5, height: 5, borderRadius: '50%',
                                                    background: mktStatus.color, display: 'inline-block', flexShrink: 0,
                                                    boxShadow: mktStatus.open ? `0 0 4px ${mktStatus.color}` : 'none',
                                                }} />
                                            </div>
                                            <div className="flex flex-col items-end gap-0.5">
                                                <span key={cur} className={`text-[11px] font-mono font-bold px-1 rounded ${isUp ? 'text-[var(--success)]' : 'text-[var(--danger)]'} ${directions[p.symbol] === 'up' ? 'animate-flash-green' : directions[p.symbol] === 'down' ? 'animate-flash-red' : ''}`}>
                                                    {priceDisplay}
                                                </span>
                                                {showStaleLabel && (
                                                    <span style={{ fontSize: 7, color: '#f59e0b', fontWeight: 700 }}>TUTUP</span>
                                                )}
                                            </div>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <div className="flex items-center gap-1.5">
                                                <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase tracking-tight">{p.name}</span>
                                                {!mktStatus.open && (
                                                    <span style={{
                                                        fontSize: 7, fontWeight: 800, padding: '1px 4px', borderRadius: 3,
                                                        background: 'rgba(239,68,68,0.15)', color: '#ef4444',
                                                        letterSpacing: '0.05em',
                                                    }}>TUTUP</span>
                                                )}
                                                {mktStatus.open && mktStatus.label !== '24/7' && (
                                                    <span style={{
                                                        fontSize: 7, fontWeight: 700, padding: '1px 4px', borderRadius: 3,
                                                        background: 'rgba(34,197,94,0.1)', color: '#22c55e',
                                                    }}>{mktStatus.label}</span>
                                                )}
                                            </div>
                                            <div className="w-12 h-4 opacity-50 group-hover:opacity-100 transition-opacity">
                                                <Sparkline data={p.trend || [50,50,50,50,50,50,50]} color={isUp ? 'var(--success)' : 'var(--danger)'} width={48} height={16} />
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>

                {/* Center Pane: Chart */}
                <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl overflow-hidden shadow-2xl flex flex-col relative">
                    <div className="absolute top-4 left-4 z-10 pointer-events-none opacity-20">
                        <span className="text-4xl font-black text-[var(--text-dim)] uppercase tracking-[0.2em]">{activePair}</span>
                    </div>
                    <div className="flex-1 min-h-0 bg-[var(--bg-panel)]/20">
                        {chartMode === 'interactive' ? (
                            <TradingViewWidget pair={selectedPairData} theme={theme} />
                        ) : (
                            <StaticChart pair={selectedPairData} theme={theme} timeframe={timeframe.toUpperCase()} />
                        )}
                    </div>

                    {/* Bottom Area of Center Pane */}
                    <div className="h-32 border-t border-[var(--border-color)] bg-[var(--bg-panel)] flex gap-4 p-4 overflow-x-auto scrollbar-none">
                        {activePair && cryptoTickers[activePair] ? (
                            <>
                                <div className="flex-1 min-w-[180px] bg-[var(--bg-card)] rounded-lg border border-[var(--border-color)] p-3 flex flex-col justify-between">
                                    <span className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">24h High / Low</span>
                                    <div className="flex items-end justify-between">
                                        <div>
                                            <span className="text-xs font-mono text-[var(--success)] font-black">{formatPrice(cryptoTickers[activePair].high, false)}</span>
                                            <span className="text-[9px] text-[var(--text-dim)] mx-1">/</span>
                                            <span className="text-xs font-mono text-[var(--danger)] font-black">{formatPrice(cryptoTickers[activePair].low, false)}</span>
                                        </div>
                                        <Activity size={14} className="text-[var(--accent)] opacity-60" />
                                    </div>
                                </div>
                                <div className="flex-1 min-w-[180px] bg-[var(--bg-card)] rounded-lg border border-[var(--border-color)] p-3 flex flex-col justify-between">
                                    <span className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">Bid / Ask</span>
                                    <div className="flex items-end justify-between">
                                        <div>
                                            <span className="text-xs font-mono text-[var(--success)] font-black">{formatPrice(cryptoTickers[activePair].bid, false)}</span>
                                            <span className="text-[9px] text-[var(--text-dim)] mx-1">/</span>
                                            <span className="text-xs font-mono text-[var(--danger)] font-black">{formatPrice(cryptoTickers[activePair].ask, false)}</span>
                                        </div>
                                        <TrendingUp size={14} className="text-[var(--accent)] opacity-60" />
                                    </div>
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="flex-1 min-w-[200px] bg-[var(--bg-card)] rounded-lg border border-[var(--border-color)] p-3 flex flex-col justify-between">
                                    <span className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">AI Prediction</span>
                                    <div className="flex items-end justify-between">
                                        <span className="text-xl font-black text-[var(--success)]">STRONGBUY</span>
                                        <span className="text-[10px] text-[var(--text-dim)]">Confidence: 94%</span>
                                    </div>
                                </div>
                                <div className="flex-1 min-w-[200px] bg-[var(--bg-card)] rounded-lg border border-[var(--border-color)] p-3 flex flex-col justify-between">
                                    <span className="text-[9px] text-[var(--text-dim)] font-black uppercase tracking-widest">Market Phase</span>
                                    <div className="flex items-end justify-between">
                                        <span className="text-xl font-black text-[var(--accent)]">ACCUMULATION</span>
                                        <span className="text-[10px] text-[var(--text-dim)]">Volume: High</span>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Right Pane: Stats & Orderbook */}
                <div className="hidden lg:flex flex-col gap-3">
                    {/* Trade Statistics */}
                    <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-5 shadow-xl flex-1">
                        <div className="flex items-center gap-2 mb-4">
                            <BarChart3 size={14} className="text-[var(--accent)]" />
                            <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-primary)]">Trade Statistics</span>
                        </div>
                        {activePair && cryptoTickers[activePair] ? (
                            <div className="space-y-3">
                                {[
                                    { label: 'Last Price', value: formatPrice(cryptoTickers[activePair].last, false), color: 'var(--text-primary)' },
                                    { label: 'High 24h', value: formatPrice(cryptoTickers[activePair].high, false), color: 'var(--success)' },
                                    { label: 'Low 24h', value: formatPrice(cryptoTickers[activePair].low, false), color: 'var(--danger)' },
                                    { label: 'Volume', value: Number(cryptoTickers[activePair].volume || 0).toLocaleString('en', { notation: 'compact', maximumFractionDigits: 2 }), color: 'var(--text-primary)' },
                                    { label: '24h Change', value: formatChange(cryptoTickers[activePair].changePercent), color: Number(cryptoTickers[activePair].changePercent) >= 0 ? 'var(--success)' : 'var(--danger)' },
                                ].map((s, i) => (
                                    <div key={i} className="flex flex-col gap-0.5 border-b border-[var(--border-color)] pb-2 last:border-0">
                                        <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase">{s.label}</span>
                                        <span className="text-sm font-mono font-black" style={{ color: s.color }}>{s.value}</span>
                                    </div>
                                ))}
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {[
                                    { label: 'High 24h', value: (curPrice * 1.002).toFixed(selectedPairData?.type === 'Forex' ? 4 : 2), color: 'var(--success)' },
                                    { label: 'Low 24h', value: (curPrice * 0.998).toFixed(selectedPairData?.type === 'Forex' ? 4 : 2), color: 'var(--danger)' },
                                    { label: 'Volume', value: '1.24B', color: 'var(--text-primary)' },
                                    { label: 'Volatility', value: '1.45%', color: 'var(--accent)' },
                                ].map((s, i) => (
                                    <div key={i} className="flex flex-col gap-1 border-b border-[var(--border-color)] pb-3 last:border-0">
                                        <span className="text-[9px] text-[var(--text-dim)] font-bold uppercase">{s.label}</span>
                                        <span className="text-sm font-mono font-black" style={{ color: s.color }}>{s.value}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Orderbook for Crypto pairs */}
                    {activePair && activePair.includes('/') ? (
                        <div className="bg-[var(--bg-card)] border border-[var(--border-color)] rounded-xl p-4 shadow-xl">
                            <div className="flex items-center justify-between mb-3">
                                <span className="text-[10px] font-black uppercase tracking-widest text-[var(--text-primary)]">Order Book</span>
                                {loadingOrderbook && <RefreshCw size={10} className="text-[var(--accent)] animate-spin" />}
                            </div>
                            {orderbook ? (
                                <div className="space-y-1">
                                    <div className="grid grid-cols-2 gap-1 mb-1">
                                        <span className="text-[8px] text-[var(--success)] font-black uppercase">Bids</span>
                                        <span className="text-[8px] text-[var(--danger)] font-black uppercase text-right">Asks</span>
                                    </div>
                                    {Array.from({ length: Math.min(5, Math.max(orderbook.bids?.length || 0, orderbook.asks?.length || 0)) }).map((_, i) => (
                                        <div key={i} className="grid grid-cols-2 gap-1">
                                            <span className="text-[9px] font-mono text-[var(--success)]">
                                                {orderbook.bids?.[i] ? Number(orderbook.bids[i][0]).toFixed(2) : ''}
                                            </span>
                                            <span className="text-[9px] font-mono text-[var(--danger)] text-right">
                                                {orderbook.asks?.[i] ? Number(orderbook.asks[i][0]).toFixed(2) : ''}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-[9px] text-[var(--text-dim)] font-mono">Loading orderbook...</div>
                            )}
                        </div>
                    ) : (
                        <div className="bg-[var(--bg-card)] border border-l-4 border-l-[var(--accent)] border-[var(--border-color)] rounded-xl p-5 shadow-inner bg-gradient-to-br from-[var(--bg-card)] to-[var(--bg-hover)]">
                            <span className="text-[10px] font-black uppercase tracking-widest text-[var(--accent)] mb-2 block">Terminal Log</span>
                            <div className="font-mono text-[9px] text-[var(--text-dim)] space-y-1">
                                <p>[{new Date().toLocaleTimeString()}] <span className="text-[var(--text-secondary)]">Feed connected</span></p>
                                <p>[{new Date().toLocaleTimeString()}] <span className="text-[var(--success)]">Subscribed to {activePair}</span></p>
                                <p>[{new Date().toLocaleTimeString()}] <span className="text-[var(--text-dim)]">Analyzing liquidity...</span></p>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
