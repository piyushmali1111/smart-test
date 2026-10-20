import React from 'react';
import { cn } from '../../utils/cn';

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: 'brand' | 'accent' | 'success' | 'amber' | 'red' | 'grey';
  children: React.ReactNode;
  icon?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  variant = 'brand',
  children,
  icon,
  className,
  ...props
}) => {
  const variantStyles = {
    brand: 'border-[rgba(108,140,255,0.35)] bg-[rgba(108,140,255,0.10)] text-brand-200 shadow-glow-sm',
    accent: 'border-accent/40 bg-accent/10 text-accent shadow-glow-accent',
    success: 'border-success/40 bg-success/10 text-success shadow-[0_0_12px_rgba(52,211,153,0.15)]',
    amber: 'border-warn/40 bg-warn/10 text-warn',
    red: 'border-danger/40 bg-danger/10 text-danger',
    grey: 'border-slate/30 bg-bg-3 text-text-muted',
  };

  return (
    <span
      className={cn(
        'inline-flex items-center gap-1.5 rounded-pill border px-2.5 py-0.5 text-xs font-semibold tracking-wide transition-all',
        variantStyles[variant],
        className
      )}
      {...props}
    >
      {icon && <span className="flex-shrink-0 text-[10px]">{icon}</span>}
      <span>{children}</span>
    </span>
  );
};
