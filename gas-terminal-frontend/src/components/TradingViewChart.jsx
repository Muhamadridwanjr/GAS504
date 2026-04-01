import React, { useEffect, useRef, useState } from 'react';
import { createChart, ColorType, CandlestickSeries, HistogramSeries, LineSeries } from 'lightweight-charts';
import { fetchChartData } from '../services/api';

export default function TradingViewChart({ pair, currentPrice, theme, timeframe = '15m' }) {
    const chartContainerRef = useRef(null);
    const chartRef = useRef(null);
    const seriesRef = useRef(null);
    const volumeSeriesRef = useRef(null);
    const latestCandleRef = useRef(null);
    const [error, setError] = useState(null);

    // Normalize timeframe for the API (e.g., '15m' -> 'M15', '1h' -> 'H1')
    const getApiTimeframe = (tf) => {
        const t = tf.toUpperCase();
        if (t.endsWith('M') && t.length > 1) return 'M' + t.slice(0, -1);
        if (t.endsWith('H') && t.length > 1) return 'H' + t.slice(0, -1);
        if (t.endsWith('D') && t.length > 1) return 'D' + t.slice(0, -1);
        return t;
    };

    useEffect(() => {
        if (!chartContainerRef.current) return;
        let chart;

        const isDark = document.documentElement.getAttribute('data-theme') !== 'light';
        const style = getComputedStyle(document.documentElement);
        const borderCol = style.getPropertyValue('--border-color').trim() || '#1c1d24';
        const textDimCol = style.getPropertyValue('--text-dim').trim() || '#aaaaaa';
        const colors = {
            bg: style.getPropertyValue('--bg-panel').trim() || '#0d0e12',
            text: textDimCol,
            grid: borderCol.length >= 7 ? borderCol + '80' : borderCol, // Add transparency if hex
            border: borderCol,
            watermark: textDimCol.length >= 7 ? textDimCol + '20' : textDimCol,
        };

        try {
            // Initialize Chart
            chart = createChart(chartContainerRef.current, {
                autoSize: true,
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
                    text: 'GOLDEN AI STRATEGY',
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

            const volumeSeries = chart.addSeries(HistogramSeries, {
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '', // set as an overlay
            });
            chart.priceScale('').applyOptions({
                scaleMargins: {
                    top: 0.8, // highest point of the series will be at 80%
                    bottom: 0,
                },
            });

            chartRef.current = chart;
            seriesRef.current = candlestickSeries;
            volumeSeriesRef.current = volumeSeries;

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
                    const activeTf = getApiTimeframe(timeframe);
                    // Request an EMA 20 indicator specifically
                    const res = await fetchChartData(pair.symbol, activeTf, 100, [{ type: "EMA", period: 20 }]);

                    if (res && res.data && res.data.length > 0) {
                        const formattedData = res.data.map(d => ({
                            time: d.time,
                            open: d.open,
                            high: d.high,
                            low: d.low,
                            close: d.close,
                            volume: d.volume || 0
                        })).sort((a, b) => a.time - b.time);

                        candlestickSeries.setData(formattedData);

                        // Set volume data
                        const volumeData = formattedData.map(d => ({
                            time: d.time,
                            value: d.volume,
                            color: d.close >= d.open ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'
                        }));
                        volumeSeries.setData(volumeData);

                        // Set EMA indicator if present
                        if (res.indicators && res.indicators.results) {
                            const emaResult = res.indicators.results.find(i => i.name === 'EMA' && i.period === 20);

                            if (emaResult && emaResult.values) {
                                const emaSeries = chart.addSeries(LineSeries, {
                                    color: '#eab308', // Yellow
                                    lineWidth: 2,
                                    crosshairMarkerVisible: false,
                                });

                                const emaData = formattedData.map((d, i) => {
                                    // The indicator results might have fewer values than OHLC if not enough data
                                    const val = emaResult.values[i];
                                    return (val !== null && val !== undefined && val !== 0 && !isNaN(val))
                                        ? { time: d.time, value: val }
                                        : null;
                                }).filter(Boolean);

                                if (emaData.length > 0) {
                                    emaSeries.setData(emaData);
                                }
                            }
                        }

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
    }, [pair.symbol, theme, timeframe]);

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

                if (volumeSeriesRef.current) {
                    const isUp = updatedCandle.close >= updatedCandle.open;
                    volumeSeriesRef.current.update({
                        time: updatedCandle.time,
                        value: updatedCandle.volume || 0,
                        color: isUp ? 'rgba(16, 185, 129, 0.4)' : 'rgba(239, 68, 68, 0.4)'
                    });
                }

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
