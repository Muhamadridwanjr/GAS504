import React, { useEffect, useRef, memo } from 'react';

function TradingViewWidget({ pair, theme }) {
    const container = useRef();
    const symbolMap = {
        'XAUUSD': 'OANDA:XAUUSD',
        'BTCUSD': 'BINANCE:BTCUSDT',
        'ETHUSD': 'BINANCE:ETHUSDT',
        'EURUSD': 'FX:EURUSD',
        'GBPUSD': 'FX:GBPUSD',
        'USDJPY': 'FX:USDJPY',
        'XAGUSD': 'OANDA:XAGUSD',
        'US30': 'CAPITALCOM:US30',
        'US500': 'CAPITALCOM:US500',
        'DXY': 'CAPITALCOM:DXY'
    };

    const symbol = symbolMap[pair.symbol] || `FX:${pair.symbol}`;

    useEffect(() => {
        const script = document.createElement("script");
        script.src = "https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js";
        script.type = "text/javascript";
        script.async = true;
        script.innerHTML = JSON.stringify({
            "autosize": true,
            "symbol": symbol,
            "interval": "15",
            "timezone": "Etc/UTC",
            "theme": theme === 'light' ? 'light' : 'dark',
            "style": "1",
            "locale": "en",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "calendar": false,
            "studies": [
                "STD;EMA",
                "STD;MA%20Exp;50",
                "STD;MA%20Exp;200",
                "STD;MACD",
                "STD;RSI"
            ],
            "support_host": "https://www.tradingview.com"
        });

        // Clear previous if any
        if (container.current) {
            container.current.innerHTML = '';
            container.current.appendChild(script);
        }
    }, [symbol, theme]);

    return (
        <div className="tradingview-widget-container" ref={container} style={{ height: "100%", width: "100%" }}>
            <div className="tradingview-widget-container__widget" style={{ height: "calc(100% - 32px)", width: "100%" }}></div>
        </div>
    );
}

export default memo(TradingViewWidget);
