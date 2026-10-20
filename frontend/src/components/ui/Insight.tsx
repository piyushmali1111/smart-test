import React from 'react';
import { cn } from '../../utils/cn';
import { Sparkles } from 'lucide-react';

export interface InsightProps {
  children: React.ReactNode;
  className?: string;
}

export const Insight: React.FC<InsightProps> = ({ children, className }) => {
  return (
    <div
      className={cn(
        'flex items-center gap-2.5 rounded-r-panel border-l-2 border-accent bg-[rgba(34,211,238,0.06)] px-4 py-2.5 text-xs sm:text-sm font-medium text-text-main backdrop-blur-sm',
        className
      )}
    >
      <Sparkles className="h-4 w-4 text-accent flex-shrink-0 animate-pulse" />
      <span className="truncate">{children}</span>
    </div>
  );
};
