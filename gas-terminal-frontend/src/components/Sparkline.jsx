import React from 'react';

export default function Sparkline({ data, color, width = 80, height = 32 }) {
    const min = Math.min(...data), max = Math.max(...data);
    const range = max - min || 1;
    const pts = data.map((v, i) => {
        const x = (i / (data.length - 1)) * width;
        const y = height - ((v - min) / range) * (height - 4) - 2;
        return `${x},${y}`;
    }).join(' ');

    const finalColor = color.startsWith('var(') ? 'currentColor' : color;

    return (
        <svg width={width} height={height} className="overflow-visible" style={{ color: color.startsWith('var(') ? color : 'inherit' }}>
            <polyline points={pts} fill="none" stroke={finalColor} strokeWidth="1.5" strokeLinejoin="round" strokeLinecap="round" />
        </svg>
    );
}
