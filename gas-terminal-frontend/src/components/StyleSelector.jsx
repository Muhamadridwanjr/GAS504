import React from 'react';
import { Zap, Clock, TrendingUp, Info } from 'lucide-react';

// Style → Timeframe Matrix per spec update18fiture_v1.01.md
export const STYLE_MATRIX = {
  scalping: { tfs: ['H4', 'H1', 'M15', 'M5'],  roles: ['Macro','Narrative','Setup','Execution'] },
  intraday: { tfs: ['D1', 'H4', 'H1', 'M15'],  roles: ['Macro','Narrative','Setup','Execution'] },
  swing:    { tfs: ['W1', 'D1', 'H4', 'H1'],   roles: ['Macro','Narrative','Setup','Execution'] },
};

export const STYLE_CONFIGS = [
  {
    id: 'scalping',
    label: 'Scalping',
    sub: 'Intra-session · H4→M5',
    emoji: '⚡',
    color: '#f97316',
    bg: 'bg-orange-400/10',
    border: 'border-orange-400/30',
    accent: 'text-orange-400',
    icon: Zap,
    desc: 'Fast setups, tight SL, multiple TP',
  },
  {
    id: 'intraday',
    label: 'Intraday',
    sub: 'Day trade · D1→M15',
    emoji: '🕐',
    color: '#3b82f6',
    bg: 'bg-blue-400/10',
    border: 'border-blue-400/30',
    accent: 'text-blue-400',
    icon: Clock,
    desc: 'Open & close same day',
  },
  {
    id: 'swing',
    label: 'Swing',
    sub: 'Multi-day · W1→H1',
    emoji: '📈',
    color: '#8b5cf6',
    bg: 'bg-purple-400/10',
    border: 'border-purple-400/30',
    accent: 'text-purple-400',
    icon: TrendingUp,
    desc: 'Multi-day position, wider TP',
  },
];

// TF role labels
const TF_ROLE_COLORS = ['text-red-400', 'text-orange-400', 'text-yellow-400', 'text-emerald-400'];

function TFMatrix({ style }) {
  const cfg = STYLE_MATRIX[style];
  if (!cfg) return null;
  return (
    <div className="flex items-center gap-1 flex-wrap">
      {cfg.tfs.map((tf, i) => (
        <React.Fragment key={tf}>
          <div className="flex flex-col items-center">
            <span className={`text-[7px] font-black uppercase tracking-wider ${TF_ROLE_COLORS[i]}`}>
              {cfg.roles[i]}
            </span>
            <span className="text-[9px] font-black px-1.5 py-0.5 rounded bg-[var(--bg-panel)] border border-[var(--border-color)] text-[var(--text-primary)] font-mono">
              {tf}
            </span>
          </div>
          {i < cfg.tfs.length - 1 && (
            <span className="text-[var(--text-dim)] text-[8px] mt-3">→</span>
          )}
        </React.Fragment>
      ))}
    </div>
  );
}

// ── Main StyleSelector Component ──────────────────────────────────────────────
export default function StyleSelector({ value, onChange, showMatrix = true, compact = false }) {
  const selected = STYLE_CONFIGS.find(s => s.id === value) || STYLE_CONFIGS[0];

  if (compact) {
    return (
      <div className="flex items-center gap-1.5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl p-1">
        {STYLE_CONFIGS.map(s => (
          <button
            key={s.id}
            onClick={() => onChange(s.id)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-[10px] font-black transition-all ${
              s.id === value
                ? `${s.bg} ${s.accent} ${s.border} border shadow-sm`
                : 'text-[var(--text-dim)] hover:bg-[var(--bg-hover)]'
            }`}
          >
            <span className="text-xs leading-none">{s.emoji}</span>
            {s.label}
          </button>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2">
        <p className="text-[9px] font-black uppercase tracking-widest text-[var(--text-dim)]">
          Trading Style
        </p>
        <div className="flex items-center gap-1 text-[8px] text-[var(--text-dim)]">
          <Info size={9} />
          <span>Style otomatis menentukan timeframe matrix</span>
        </div>
      </div>

      {/* Style Cards */}
      <div className="grid grid-cols-3 gap-2">
        {STYLE_CONFIGS.map(s => {
          const isSelected = s.id === value;
          const Icon = s.icon;
          return (
            <button
              key={s.id}
              onClick={() => onChange(s.id)}
              className={`relative flex flex-col gap-1.5 p-3 rounded-xl border transition-all text-left hover:scale-[1.02] active:scale-[0.98] ${
                isSelected
                  ? `${s.bg} ${s.border} ring-1 ring-current/30 shadow-md`
                  : 'border-[var(--border-color)] hover:border-[var(--accent)]/30 hover:bg-[var(--bg-hover)] bg-[var(--bg-card)]'
              }`}
            >
              {/* Emoji + label */}
              <div className="flex items-center gap-1.5">
                <span className="text-base leading-none">{s.emoji}</span>
                <div>
                  <div className={`text-[10px] font-black ${isSelected ? s.accent : 'text-[var(--text-primary)]'}`}>
                    {s.label}
                  </div>
                  <div className="text-[7px] text-[var(--text-dim)] font-bold">{s.sub}</div>
                </div>
              </div>
              {/* Desc */}
              <p className={`text-[8px] font-bold leading-relaxed ${isSelected ? s.accent : 'text-[var(--text-dim)]'} opacity-80`}>
                {s.desc}
              </p>
              {/* Selected dot */}
              {isSelected && (
                <div className={`absolute top-2 right-2 w-2 h-2 rounded-full`}
                  style={{ background: s.color }} />
              )}
            </button>
          );
        })}
      </div>

      {/* TF Matrix Display */}
      {showMatrix && (
        <div className="flex items-start gap-3 px-3 py-2.5 bg-[var(--bg-panel)] border border-[var(--border-color)] rounded-xl">
          <span className="text-[8px] font-black text-[var(--text-dim)] uppercase tracking-wider shrink-0 mt-0.5">
            TF Matrix:
          </span>
          <TFMatrix style={value} />
        </div>
      )}
    </div>
  );
}

// Export TFMatrix for use elsewhere
export { TFMatrix };
