import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../utils/cn';

export interface TabItem {
  id: string;
  label: string;
  count?: number;
}

export interface TabsProps {
  tabs: TabItem[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
  name?: string;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onChange,
  className,
  name = 'tabs',
}) => {
  return (
    <div className={cn('flex items-center border-b border-border/80 gap-6', className)}>
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;
        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={cn(
              'relative pb-3 text-sm font-semibold transition-colors cursor-pointer flex items-center gap-2 select-none',
              isActive ? 'text-text-main' : 'text-text-muted hover:text-text-main'
            )}
          >
            <span>{tab.label}</span>
            {tab.count !== undefined && (
              <span className="rounded-full bg-bg-4 px-2 py-0.5 text-xs font-mono text-text-muted">
                {tab.count}
              </span>
            )}
            {isActive && (
              <motion.div
                layoutId={`tab-underline-${name}`}
                className="absolute bottom-0 left-0 right-0 h-0.5 bg-brand"
                transition={{ type: 'spring', stiffness: 380, damping: 30 }}
              />
            )}
          </button>
        );
      })}
    </div>
  );
};
