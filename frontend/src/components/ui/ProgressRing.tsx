import React from 'react';
import { cn } from '../../utils/cn';

export interface ProgressRingProps {
  value: number;
  max?: number;
  size?: number;
  strokeWidth?: number;
  label?: string;
  unit?: string;
  className?: string;
}

export const ProgressRing: React.FC<ProgressRingProps> = ({
  value,
  max = 100,
  size = 110,
  strokeWidth = 9,
  label,
  unit = '%',
  className,
}) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const pct = Math.min(100, Math.max(0, (value / max) * 100));
  const offset = circumference - (pct / 100) * circumference;

  const isHigh = pct >= 90;
  const strokeColor = isHigh ? 'var(--warn)' : 'url(#progressRingGrad)';
  const glowStyle = isHigh
    ? { filter: 'drop-shadow(0px 0px 6px rgba(251, 191, 36, 0.4))' }
    : { filter: 'drop-shadow(0px 0px 6px rgba(34, 211, 238, 0.3))' };

  return (
    <div className={cn('relative inline-flex flex-col items-center justify-center', className)}>
      <svg width={size} height={size} className="transform -rotate-90">
        <defs>
          <linearGradient id="progressRingGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="var(--brand)" />
            <stop offset="100%" stopColor="var(--accent)" />
          </linearGradient>
        </defs>
        {/* Track */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="var(--bg-4)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        {/* Fill */}
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke={strokeColor}
          strokeWidth={strokeWidth}
          strokeDasharray={circumference}
          strokeDashoffset={offset}
          strokeLinecap="round"
          fill="transparent"
          style={glowStyle}
          className="transition-all duration-500 ease-out"
        />
      </svg>

      {/* Center text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <span className="font-mono text-xl sm:text-2xl font-extrabold text-text-main">
          {Math.round(value)}
          <span className="text-xs font-normal text-text-muted ml-0.5">{unit}</span>
        </span>
        {label && (
          <span className="text-[10px] uppercase font-semibold text-text-dim tracking-wider mt-0.5">
            {label}
          </span>
        )}
      </div>
    </div>
  );
};
