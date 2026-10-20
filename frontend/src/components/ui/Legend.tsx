import React from 'react';
import { cn } from '../../utils/cn';

export interface LegendItem {
  label: string;
  color: string; // CSS color string or class
  dashed?: boolean;
}

export interface LegendProps {
  items: LegendItem[];
  className?: string;
}

export const Legend: React.FC<LegendProps> = ({ items, className }) => {
  return (
    <div className={cn('flex flex-wrap items-center gap-4 text-xs font-medium text-text-muted', className)}>
      {items.map((item, index) => (
        <div key={index} className="flex items-center gap-2">
          {item.dashed ? (
            <span
              className="inline-block w-4 h-0 border-t-2 border-dashed"
              style={{ borderColor: item.color }}
            />
          ) : (
            <span
              className="inline-block h-2.5 w-2.5 rounded-full shadow-glow-sm"
              style={{ backgroundColor: item.color }}
            />
          )}
          <span>{item.label}</span>
        </div>
      ))}
    </div>
  );
};
