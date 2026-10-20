import React from 'react';
import { cn } from '../../utils/cn';

export interface SliderProps {
  min: number;
  max: number;
  step?: number;
  value: number;
  onChange: (val: number) => void;
  unit?: string;
  label?: string;
  className?: string;
}

export const Slider: React.FC<SliderProps> = ({
  min,
  max,
  step = 1,
  value,
  onChange,
  unit = 's',
  label,
  className,
}) => {
  const percentage = Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));

  return (
    <div className={cn("w-full flex flex-col gap-2 select-none", className)}>
      <div className="flex items-center justify-between text-xs font-semibold text-text-muted">
        {label && <span className="uppercase tracking-wider">{label}</span>}
        <span className="font-mono text-sm font-bold text-accent">
          {value} {unit}
        </span>
      </div>

      <div className="relative flex items-center h-8">
        {/* Track */}
        <div className="relative w-full h-1.5 rounded-full bg-bg-4 overflow-hidden border border-border">
          {/* Filled track: gradient --brand to --accent */}
          <div
            className="absolute left-0 top-0 bottom-0 bg-gradient-to-r from-brand to-accent transition-all duration-75"
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Real hidden accessible range input */}
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          aria-label={label || "Budget slider"}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20"
        />

        {/* Visual custom thumb: white with 3px --brand ring and --glow-sm */}
        <div
          className="pointer-events-none absolute h-5 w-5 -ml-2.5 rounded-full border-[3px] border-brand bg-white shadow-glow-sm flex items-center justify-center transition-all duration-75 z-10"
          style={{ left: `${percentage}%` }}
        />
      </div>

      <div className="flex justify-between text-[11px] font-mono text-text-dim">
        <span>{min} {unit}</span>
        <span>{Math.round((min + max) / 2)} {unit}</span>
        <span>{max} {unit}</span>
      </div>
    </div>
  );
};
