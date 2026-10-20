import React from 'react';
import { cn } from '../../utils/cn';

export interface FramedPanelProps extends React.HTMLAttributes<HTMLDivElement> {
  glow?: boolean;
}

export const FramedPanel: React.FC<FramedPanelProps> = ({
  children,
  className,
  glow = false,
  ...props
}) => {
  return (
    <div
      className={cn(
        'relative rounded-panel border border-border bg-bg-3 p-4 transition-all duration-200 overflow-hidden',
        glow && 'border-border-strong shadow-glow-sm',
        className
      )}
      {...props}
    >
      {/* Subtle top inner highlight */}
      <div className="pointer-events-none absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/5 to-transparent" />
      {children}
    </div>
  );
};
