import React, { useEffect, useState } from 'react';
import { Card } from './Card';
import { cn } from '../../utils/cn';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

export interface StatCardProps {
  label: string;
  value: number;
  prefix?: string;
  suffix?: string;
  decimals?: number;
  trend?: 'up' | 'down' | 'neutral';
  trendLabel?: string;
  glow?: boolean;
  className?: string;
}

export const StatCard: React.FC<StatCardProps> = ({
  label,
  value,
  prefix = '',
  suffix = '',
  decimals = 0,
  trend,
  trendLabel,
  glow = false,
  className,
}) => {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    let startTimestamp: number | null = null;
    const duration = 900;
    const startValue = 0;

    let frameId: number;

    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / duration, 1);
      const easeOut = 1 - Math.pow(1 - progress, 3);
      const current = startValue + (value - startValue) * easeOut;
      setDisplayValue(current);

      if (progress < 1) {
        frameId = requestAnimationFrame(step);
      } else {
        setDisplayValue(value);
      }
    };

    frameId = requestAnimationFrame(step);
    return () => cancelAnimationFrame(frameId);
  }, [value]);

  const formattedNum = displayValue.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });

  return (
    <Card glow={glow} className={cn("p-5", className)}>
      <div className="flex flex-col justify-between h-full">
        <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
          {label}
        </span>

        <div className="my-2 flex items-baseline gap-1">
          {prefix && <span className="font-mono text-2xl font-bold text-accent">{prefix}</span>}
          <span className="font-mono text-4xl sm:text-5xl font-extrabold tracking-tight text-gradient">
            {formattedNum}
          </span>
          {suffix && <span className="font-mono text-2xl font-bold text-accent">{suffix}</span>}
        </div>

        {trend && (
          <div className="flex items-center gap-1.5 text-xs">
            {trend === 'up' && <TrendingUp className="h-3.5 w-3.5 text-success" />}
            {trend === 'down' && <TrendingDown className="h-3.5 w-3.5 text-danger" />}
            {trend === 'neutral' && <Minus className="h-3.5 w-3.5 text-text-muted" />}
            {trendLabel && (
              <span className={cn(
                "font-medium",
                trend === 'up' ? "text-success" : trend === 'down' ? "text-danger" : "text-text-muted"
              )}>
                {trendLabel}
              </span>
            )}
          </div>
        )}
      </div>
    </Card>
  );
};
