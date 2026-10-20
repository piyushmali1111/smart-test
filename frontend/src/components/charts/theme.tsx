import React from 'react';

export const chartColors = {
  accent: 'var(--accent)',       // #22D3EE (cyan - hero data)
  brand: 'var(--brand)',         // #6C8CFF (periwinkle)
  lavender: 'var(--lavender)',   // #A5B4FC
  teal: 'var(--teal)',           // #2DD4BF
  slate: 'var(--slate)',         // #94A3B8
  warn: 'var(--warn)',           // #FBBF24
  danger: 'var(--danger)',       // #F87171
  success: 'var(--success)',     // #34D399 (emerald)
  runAll: 'var(--text)',         // #E6EAF5
  border: 'rgba(148, 163, 255, 0.20)',
  grid: 'rgba(148, 163, 184, 0.10)',
  cursor: 'rgba(148, 163, 255, 0.08)',
  textMuted: '#94A0BF',
  cardBg: 'rgba(18, 26, 47, 0.95)',
};

export interface CustomTooltipProps {
  active?: boolean;
  payload?: any[];
  label?: string | number;
  unit?: string;
}

export const CustomChartTooltip: React.FC<CustomTooltipProps> = ({
  active,
  payload,
  label,
  unit = '',
}) => {
  if (!active || !payload || !payload.length) return null;

  return (
    <div className="rounded-panel border border-[rgba(148,163,255,0.20)] bg-[rgba(18,26,47,0.95)] px-3 py-2 text-xs shadow-glow-sm backdrop-blur-md">
      {label !== undefined && (
        <p className="mb-1.5 font-mono text-[11px] font-semibold text-text-muted">
          {label}
        </p>
      )}
      <div className="flex flex-col gap-1">
        {payload.map((entry, idx) => (
          <div key={`item-${idx}`} className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-1.5">
              <span
                className="h-2 w-2 rounded-full"
                style={{ backgroundColor: entry.color || entry.stroke || chartColors.accent }}
              />
              <span className="font-medium text-text-main">{entry.name}:</span>
            </div>
            <span className="font-mono font-bold text-accent">
              {typeof entry.value === 'number' ? entry.value.toFixed(1) : entry.value} {unit}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
};
