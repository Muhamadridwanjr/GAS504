import React, { useEffect, useRef, memo } from 'react';

// Auto-convert any pair symbol → TradingView symbol string
function getTVSymbol(pair) {
    const sym = pair?.symbol;
    if (!sym) return 'BINANCE:BTCUSDT';

    // ── Futures: BTC/USDT:USDT → BINANCE:BTCUSDT.P ───────────
    if (sym.includes(':USDT')) {
        const base = sym.split('/')[0];
        return `BINANCE:${base}USDT.P`;
    }

    // ── Crypto spot: BTC/USDT → BINANCE:BTCUSDT ──────────────
    if (sym.includes('/USDT')) {
        const base = sym.split('/')[0];
        return `BINANCE:${base}USDT`;
    }

    // ── MT5 / Exness explicit maps ────────────────────────────
    const explicit = {
        // ── Forex Major ──────────────────────────────────────
        'AUDUSD': 'FX:AUDUSD',   'EURUSD': 'FX:EURUSD',   'GBPUSD': 'FX:GBPUSD',
        'NZDUSD': 'FX:NZDUSD',   'USDCAD': 'FX:USDCAD',   'USDCHF': 'FX:USDCHF',
        'USDJPY': 'FX:USDJPY',
        // ── Forex Minor ──────────────────────────────────────
        'AUDCAD': 'FX:AUDCAD',   'AUDCHF': 'FX:AUDCHF',   'AUDJPY': 'FX:AUDJPY',
        'AUDNZD': 'FX:AUDNZD',   'CADCHF': 'FX:CADCHF',   'CADJPY': 'FX:CADJPY',
        'CHFJPY': 'FX:CHFJPY',   'EURAUD': 'FX:EURAUD',   'EURCAD': 'FX:EURCAD',
        'EURCHF': 'FX:EURCHF',   'EURGBP': 'FX:EURGBP',   'EURJPY': 'FX:EURJPY',
        'EURNZD': 'FX:EURNZD',   'GBPAUD': 'FX:GBPAUD',   'GBPCAD': 'FX:GBPCAD',
        'GBPCHF': 'FX:GBPCHF',   'GBPJPY': 'FX:GBPJPY',   'GBPNZD': 'FX:GBPNZD',
        'HKDJPY': 'FX:HKDJPY',   'NZDCAD': 'FX:NZDCAD',   'NZDCHF': 'FX:NZDCHF',
        'NZDJPY': 'FX:NZDJPY',   'USDCNH': 'FX:USDCNH',   'USDHKD': 'FX:USDHKD',
        'USDTHB': 'FX:USDTHB',
        // ── Precious Metals ──────────────────────────────────
        'XAUUSD': 'OANDA:XAUUSD', 'XAGUSD': 'OANDA:XAGUSD',
        'XAGAUD': 'OANDA:XAGAUD', 'XAGGBP': 'OANDA:XAGGBP', 'XAGEUR': 'OANDA:XAGEUR',
        'XPDUSD': 'TVC:XPDUSD',   'XPTUSD': 'TVC:XPTUSD',
        // ── Industrial Metals ────────────────────────────────
        'XALUSD': 'TVC:ALUMINIUM', 'XCUUSD': 'CAPITALCOM:COPPER',
        'XNIUSD': 'TVC:NICKEL',    'XPBUSD': 'TVC:LEAD',    'XZNUSD': 'TVC:ZINC',
        // ── Energy ───────────────────────────────────────────
        'USOIL':  'TVC:USOIL',     'UKOIL':  'TVC:UKOIL',   'XNGUSD': 'TVC:NATURALGAS',
        // ── US Indices ───────────────────────────────────────
        'US30':       'CAPITALCOM:US30',  'US500':      'CAPITALCOM:US500',
        'USTEC':      'CAPITALCOM:US100', 'US30_x10':   'CAPITALCOM:US30',
        'US500_x100': 'CAPITALCOM:US500', 'USTEC_x100': 'CAPITALCOM:US100',
        // ── Europe Indices ───────────────────────────────────
        'DE30':    'CAPITALCOM:DE30',  'UK100':   'CAPITALCOM:UK100',
        'FR40':    'CAPITALCOM:FR40',  'STOXX50': 'CAPITALCOM:EU50',
        // ── Asia-Pacific Indices ─────────────────────────────
        'JP225':  'TVC:NI225',  'HK50':   'TVC:HSI',    'AUS200': 'CAPITALCOM:AUS200',
        // ── Other Index ──────────────────────────────────────
        'DXY':    'TVC:DXY',
        // ── US Stocks ────────────────────────────────────────
        'AAPL': 'NASDAQ:AAPL', 'MSFT': 'NASDAQ:MSFT', 'GOOGL': 'NASDAQ:GOOGL',
        'AMZN': 'NASDAQ:AMZN', 'TSLA': 'NASDAQ:TSLA', 'META':  'NASDAQ:META',
        'NVDA': 'NASDAQ:NVDA', 'NFLX': 'NASDAQ:NFLX', 'AMD':   'NASDAQ:AMD',
        'INTC': 'NASDAQ:INTC', 'V':    'NYSE:V',       'MA':    'NYSE:MA',
        'JPM':  'NYSE:JPM',    'BAC':  'NYSE:BAC',     'WMT':   'NYSE:WMT',
        'DIS':  'NYSE:DIS',    'CRM':  'NYSE:CRM',     'PYPL':  'NASDAQ:PYPL',
        'UBER': 'NYSE:UBER',   'COIN': 'NASDAQ:COIN',  'PLTR':  'NYSE:PLTR',
        // ── Global Stocks ────────────────────────────────────
        'BABA': 'NYSE:BABA',   'TSM':  'NYSE:TSM',    'BIDU':  'NASDAQ:BIDU',
        'NIO':  'NYSE:NIO',    'SONY': 'NYSE:SONY',   'SAP':   'NYSE:SAP',
        'ASML': 'NASDAQ:ASML', 'SHOP': 'NYSE:SHOP',   'MELI':  'NASDAQ:MELI',
        'SE':   'NYSE:SE',     'GRAB': 'NASDAQ:GRAB',  'VALE':  'NYSE:VALE',
        'BHP':  'NYSE:BHP',    'RIO':  'NYSE:RIO',     'HSBA':  'NYSE:HSBC',
        // ── Legacy ───────────────────────────────────────────
        'NAS100': 'CAPITALCOM:US100', 'WTI': 'TVC:USOIL',
        'BTCUSD': 'BINANCE:BTCUSDT',  'ETHUSD': 'BINANCE:ETHUSDT',
        // ── IDX (Indonesia Stock Exchange) ──────────────────────
        'IHSG':   'IDX:COMPOSITE',
        'BBCA':   'IDX:BBCA',  'BBRI':  'IDX:BBRI',  'BMRI':  'IDX:BMRI',
        'BBNI':   'IDX:BBNI',  'BRIS':  'IDX:BRIS',  'NISP':  'IDX:NISP',
        'PNBN':   'IDX:PNBN',  'BBTN':  'IDX:BBTN',  'TLKM':  'IDX:TLKM',
        'ISAT':   'IDX:ISAT',  'EXCL':  'IDX:EXCL',  'TBIG':  'IDX:TBIG',
        'GOTO':   'IDX:GOTO',  'EMTK':  'IDX:EMTK',  'BREN':  'IDX:BREN',
        'ADRO':   'IDX:ADRO',  'PTBA':  'IDX:PTBA',  'ESSA':  'IDX:ESSA',
        'ELSA':   'IDX:ELSA',  'MEDC':  'IDX:MEDC',  'PGAS':  'IDX:PGAS',
        'INCO':   'IDX:INCO',  'ANTM':  'IDX:ANTM',  'TINS':  'IDX:TINS',
        'MDKA':   'IDX:MDKA',  'UNVR':  'IDX:UNVR',  'ICBP':  'IDX:ICBP',
        'INDF':   'IDX:INDF',  'HMSP':  'IDX:HMSP',  'MYOR':  'IDX:MYOR',
        'DLTA':   'IDX:DLTA',  'ULTJ':  'IDX:ULTJ',  'CPIN':  'IDX:CPIN',
        'JPFA':   'IDX:JPFA',  'KLBF':  'IDX:KLBF',  'SIDO':  'IDX:SIDO',
        'MIKA':   'IDX:MIKA',  'HEAL':  'IDX:HEAL',  'ASII':  'IDX:ASII',
        'SMGR':   'IDX:SMGR',  'INKP':  'IDX:INKP',  'TKIM':  'IDX:TKIM',
        'BSDE':   'IDX:BSDE',  'PWON':  'IDX:PWON',  'LPKR':  'IDX:LPKR',
        'SMRA':   'IDX:SMRA',  'ACES':  'IDX:ACES',  'MAPI':  'IDX:MAPI',
        'ERAA':   'IDX:ERAA',  'AALI':  'IDX:AALI',
    };

    return explicit[sym] || 'BINANCE:BTCUSDT';
}

function TradingViewWidget({ pair, theme }) {
    const container = useRef();
    const symbol = getTVSymbol(pair);

    useEffect(() => {
        if (!container.current) return;

        const script = document.createElement('script');
        script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js';
        script.type = 'text/javascript';
        script.async = true;
        script.innerHTML = JSON.stringify({
            autosize: true,
            symbol,
            interval: '15',
            timezone: 'Asia/Jakarta',
            theme: theme === 'light' ? 'light' : 'dark',
            style: '1',
            locale: 'en',
            enable_publishing: false,
            hide_side_toolbar: false,
            allow_symbol_change: true,
            calendar: false,
            studies: [
                'STD;EMA',
                'STD;MA%20Exp;50',
                'STD;MA%20Exp;200',
                'STD;MACD',
                'STD;RSI',
            ],
            support_host: 'https://www.tradingview.com',
        });

        container.current.innerHTML = '';
        container.current.appendChild(script);
    }, [symbol, theme]);

    return (
        <div className="tradingview-widget-container" ref={container} style={{ height: '100%', width: '100%' }}>
            <div className="tradingview-widget-container__widget" style={{ height: 'calc(100% - 32px)', width: '100%' }} />
        </div>
    );
}

export default memo(TradingViewWidget);
