import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CandlestickSeries } from 'lightweight-charts';
import { fetchChartData } from '../services/api';

export default function TradingViewChart({ pair, currentPrice, theme }) {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const seriesRef = useRef(null);
    const latestCandleRef = useRef(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!chartContainerRef.current) return;
        let chart;

        const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
        const style = getComputedStyle(document.documentElement);
        const colors = {
            bg: style.getPropertyValue('--bg-panel').trim() || '#0d0e12',
            text: style.getPropertyValue('--text-dim').trim() || '#aaa',
            grid: style.getPropertyValue('--border-color').trim() + '80', // Add transparency
            border: style.getPropertyValue('--border-color').trim() || '#1c1d24',
            watermark: style.getPropertyValue('--text-dim').trim() + '20',
        };

        try {
            // Initialize Chart
            chart = createChart(chartContainerRef.current, {
                layout: {
                    background: { type: ColorType.Solid, color: colors.bg },
                    textColor: colors.text,
                    fontFamily: 'Outfit, sans-serif',
                },
                grid: {
                    vertLines: { color: colors.grid },
                    horzLines: { color: colors.grid },
                },
                crosshair: {
                    mode: 0,
                    vertLine: { labelBackgroundColor: '#fac815' },
                    horzLine: { labelBackgroundColor: '#fac815' },
                },
                rightPriceScale: {
                    borderColor: colors.border,
                    alignLabels: true,
                },
                timeScale: {
                    borderColor: colors.border,
                    timeVisible: true,
                    secondsVisible: false,
                    barSpacing: 8,
                },
                watermark: {
                    visible: true,
                    fontSize: 48,
                    horzAlign: 'center',
                    vertAlign: 'center',
                    color: colors.watermark,
                    text: 'GASSTRATEGYAI',
                },
                handleScroll: true,
                handleScale: true,
            });

            const candlestickSeries = chart.addSeries(CandlestickSeries, {
                upColor: '#10b981',
                downColor: '#ef4444',
                borderVisible: false,
                wickUpColor: '#10b981',
                wickDownColor: '#ef4444',
            });

            chartRef.current = chart;
            seriesRef.current = candlestickSeries;

            const handleResize = () => {
                if (chartContainerRef.current && chart) {
                    chart.applyOptions({
                        width: chartContainerRef.current.clientWidth,
                        height: chartContainerRef.current.clientHeight
                    });
                }
            };

            window.addEventListener('resize', handleResize);

            // Fetch History
            const loadHistory = async () => {
                try {
                    const res = await fetchChartData(pair.symbol, 'M15', 100);
                    if (res && res.data && res.data.length > 0) {
                        const formattedData = res.data.map(d => ({
                            time: d.time,
                            open: d.open,
                            high: d.high,
                            low: d.low,
                            close: d.close
                        })).sort((a, b) => a.time - b.time);

                        candlestickSeries.setData(formattedData);
                        if (formattedData.length > 0) {
                            latestCandleRef.current = formattedData[formattedData.length - 1];
                        }
                        chart.timeScale().fitContent();
                    }
                } catch (err) {
                    console.error("Failed to fetch history for TradingView", pair.symbol, err);
                }
            };

            loadHistory();

            return () => {
                window.removeEventListener('resize', handleResize);
                if (chart) chart.remove();
            };
        } catch (e) {
            console.error("Chart initialization crash", e);
            setError(e.message);
        }
    }, [pair.symbol, theme]);

    // Handle real-time price updates
    useEffect(() => {
        try {
            if (seriesRef.current && currentPrice && latestCandleRef.current) {
                const currentObj = latestCandleRef.current;
                const updatedCandle = {
                    ...currentObj,
                    close: Number(currentPrice),
                    high: Math.max(Number(currentObj.high), Number(currentPrice)),
                    low: Math.min(Number(currentObj.low), Number(currentPrice))
                };
                seriesRef.current.update(updatedCandle);
                latestCandleRef.current = updatedCandle;
            }
        } catch (e) {
            console.error("Real-time chart update error", e);
        }
    }, [currentPrice]);

    if (error) {
        return (
            <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-red-500/5 rounded-lg border border-red-500/20">
                <span className="text-red-500 font-black text-[10px] uppercase mb-1">Chart Failed</span>
                <span className="text-[#666] text-[9px] text-center max-w-[200px]">{error}</span>
            </div>
        );
    }

    return (
        <div ref={chartContainerRef} className="w-full h-full relative" />
    );
}
