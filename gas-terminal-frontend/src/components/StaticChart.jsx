import React, { useState, useEffect } from 'react';

export default function StaticChart({ pair, timeframe = 'M15', theme }) {
    const [imgUrl, setImgUrl] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://35.197.97.60:8085/terminal';

    useEffect(() => {
        if (!pair?.symbol) return;

        const fetchChart = async () => {
            setLoading(true);
            setError(null);
            try {
                // We use the direct URL for the image
                const url = `${API_BASE}/chart/${pair.symbol}/render?timeframe=${timeframe}&count=100&t=${Date.now()}`;
                setImgUrl(url);
                setLoading(false);
            } catch (err) {
                console.error("Failed to load static chart:", err);
                setError("Failed to load chart image");
                setLoading(false);
            }
        };

        fetchChart();
        // Refresh every minute for the static chart if needed, 
        // or just rely on manual refresh/component remount
        const interval = setInterval(fetchChart, 60000);
        return () => clearInterval(interval);
    }, [pair?.symbol, timeframe, API_BASE]);

    if (error) {
        return (
            <div className="w-full h-full flex flex-col items-center justify-center p-4 bg-red-500/5 rounded-lg border border-red-500/20">
                <span className="text-red-500 font-bold text-[12px] uppercase mb-1">Expert Chart Error</span>
                <span className="text-[#666] text-[10px]">{error}</span>
            </div>
        );
    }

    return (
        <div className="w-full h-full relative flex items-center justify-center bg-[#0d0e12] overflow-hidden rounded-lg">
            {loading && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/40 z-10">
                    <div className="w-6 h-6 border-2 border-[#fac815] border-t-transparent rounded-full animate-spin"></div>
                </div>
            )}
            {imgUrl && (
                <img
                    src={imgUrl}
                    alt={`${pair.symbol} Expert Chart`}
                    className="max-w-full max-h-full object-contain"
                    onLoad={() => setLoading(false)}
                    onError={() => {
                        setError("Image failed to load");
                        setLoading(false);
                    }}
                />
            )}

            {/* Overlay Info */}
            <div className="absolute top-4 left-4 flex flex-col pointer-events-none">
                <div className="flex items-center gap-2 mb-1">
                    <span className="text-[#fac815] font-black text-sm">{pair.symbol}</span>
                    <span className="bg-[#fac815]/10 text-[#fac815] px-1.5 py-0.5 rounded text-[10px] font-bold uppercase">{timeframe}</span>
                    <span className="bg-white/5 text-[#888] px-1.5 py-0.5 rounded text-[10px] font-bold uppercase">Expert View</span>
                </div>
            </div>
        </div>
    );
}
