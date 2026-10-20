import React from 'react';
import { cn } from '../../utils/cn';

export interface SkeletonProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: 'rectangular' | 'circular' | 'text';
}

export const Skeleton: React.FC<SkeletonProps> = ({
  variant = 'rectangular',
  className,
  ...props
}) => {
  return (
    <div
      className={cn(
        'relative overflow-hidden bg-bg-3 border border-border/40',
        'before:absolute before:inset-0 before:-translate-x-full before:animate-[shimmer_1.8s_infinite] before:bg-gradient-to-r before:from-transparent before:via-brand/10 before:to-transparent',
        variant === 'circular' && 'rounded-full',
        variant === 'rectangular' && 'rounded-panel',
        variant === 'text' && 'h-4 w-full rounded',
        className
      )}
      {...props}
    />
  );
};
