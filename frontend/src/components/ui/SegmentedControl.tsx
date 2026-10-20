import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

export interface Option<T extends string = string> {
  value: T;
  label: string;
  badge?: string;
}

export interface SegmentedControlProps<T extends string = string> {
  options: Option<T>[];
  value: T;
  onChange: (val: T) => void;
  size?: 'sm' | 'md';
  className?: string;
  name?: string;
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  size = 'md',
  className,
  name = 'segmented-control',
}: SegmentedControlProps<T>) {
  return (
    <div
      className={cn(
        'relative inline-flex items-center rounded-pill bg-bg-3 p-1 border border-border',
        className
      )}
      role="radiogroup"
    >
      {options.map((opt) => {
        const isActive = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={isActive}
            onClick={() => onChange(opt.value)}
            className={cn(
              'relative z-10 flex items-center justify-center font-medium rounded-pill transition-colors cursor-pointer select-none',
              size === 'sm' ? 'px-3 py-1 text-xs' : 'px-4 py-1.5 text-xs sm:text-sm',
              isActive ? 'text-text-main font-semibold' : 'text-text-muted hover:text-text-main'
            )}
          >
            {isActive && (
              <motion.div
                layoutId={`segment-highlight-${name}`}
                className="absolute inset-0 rounded-pill bg-[rgba(108,140,255,0.16)] border border-[rgba(108,140,255,0.5)] shadow-glow-sm"
                transition={{ type: 'spring', stiffness: 350, damping: 30 }}
              />
            )}
            <span className="relative z-20 flex items-center gap-1.5">
              {opt.label}
              {opt.badge && (
                <span className="rounded-full bg-brand/20 px-1.5 py-0.2 text-[10px] text-brand-200">
                  {opt.badge}
                </span>
              )}
            </span>
          </button>
        );
      })}
    </div>
  );
}
