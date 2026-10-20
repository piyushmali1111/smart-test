import React from 'react';
import { cn } from '../../utils/cn';

export interface RiskBarProps {
  value: number; // 0 to 1
  showValue?: boolean;
  className?: string;
}

export const RiskBar: React.FC<RiskBarProps> = ({
  value,
  showValue = true,
  className,
}) => {
  const clamped = Math.min(1, Math.max(0, value));
  const pct = Math.round(clamped * 100);

  return (
    <div className={cn('flex items-center gap-2.5 w-full', className)}>
      <div className="relative h-2 w-full flex-1 rounded-full bg-bg-4 overflow-hidden border border-border/50">
        <div
          className="h-full rounded-full bg-gradient-to-r from-brand-600 to-accent transition-all duration-300 shadow-[0_0_8px_rgba(34,211,238,0.2)]"
          style={{ width: `${pct}%` }}
        />
      </div>
      {showValue && (
        <span className="font-mono text-xs font-semibold text-accent w-10 text-right">
          {clamped.toFixed(2)}
        </span>
      )}
    </div>
  );
};
