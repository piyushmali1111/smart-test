import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { FramedPanel } from '../ui/FramedPanel';
import { Button } from '../ui/Button';
import { SegmentedControl } from '../ui/SegmentedControl';

interface TestGridProps {
  totalCount?: number;
  selectedIndices?: number[];
  activeStepIndex?: number;
  interactive?: boolean;
}

export const TestGrid: React.FC<TestGridProps> = ({
  totalCount = 180,
  selectedIndices,
  interactive = true,
}) => {
  const [mode, setMode] = useState<'smart' | 'all'>('smart');
  const [animationKey, setAnimationKey] = useState(0);

  const defaultSelected = [
    3, 7, 14, 21, 28, 35, 42, 53, 62, 77, 84, 91, 105, 118, 126, 139, 147, 155, 168, 172,
  ];

  const activeIndices = new Set(
    mode === 'all'
      ? Array.from({ length: totalCount }, (_, i) => i)
      : (selectedIndices || defaultSelected)
  );

  const selectedCount = mode === 'all' ? totalCount : (selectedIndices?.length || defaultSelected.length);

  return (
    <FramedPanel glow className="p-5">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 mb-4">
        <div className="flex items-center gap-3">
          <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            Test Suite Execution Grid
          </span>
          <span className="font-mono text-xs text-accent bg-bg-4 px-2 py-0.5 rounded-full border border-border">
            {selectedCount} / {totalCount} tests active
          </span>
        </div>

        {interactive && (
          <div className="flex items-center gap-2">
            <SegmentedControl
              size="sm"
              value={mode}
              onChange={(val) => {
                setMode(val);
                setAnimationKey(k => k + 1);
              }}
              options={[
                { value: 'smart', label: 'Smart Selection' },
                { value: 'all', label: 'Run Everything' },
              ]}
            />
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setAnimationKey(k => k + 1)}
              className="text-xs"
            >
              Replay
            </Button>
          </div>
        )}
      </div>

      {/* Grid */}
      <div
        key={animationKey}
        className="grid grid-cols-12 sm:grid-cols-20 md:grid-cols-24 lg:grid-cols-30 gap-1.5 p-3 rounded-panel bg-bg-0/60 border border-border/40"
      >
        {Array.from({ length: totalCount }).map((_, i) => {
          const isSelected = activeIndices.has(i);
          return (
            <motion.div
              key={i}
              initial={{ scale: 0.8, opacity: 0.3 }}
              animate={{
                scale: 1,
                opacity: isSelected ? 1 : 0.4,
              }}
              transition={{
                delay: (i % 24) * 0.008,
                duration: 0.2,
              }}
              title={`Test #${i + 1}: ${isSelected ? 'Selected for execution' : 'Skipped'}`}
              className={`h-3 w-full rounded-sm transition-colors duration-200 border ${
                isSelected
                  ? 'bg-gradient-to-r from-brand to-accent border-accent/40 shadow-glow-accent'
                  : 'bg-bg-3 border-[rgba(148,163,255,0.06)] hover:bg-bg-4'
              }`}
            />
          );
        })}
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-text-dim">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-sm bg-bg-3 border border-[rgba(148,163,255,0.06)] inline-block" />
          <span>Skipped ({totalCount - selectedCount})</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 rounded-sm bg-gradient-to-r from-brand to-accent shadow-glow-accent inline-block" />
          <span className="text-accent font-medium">Selected ({selectedCount})</span>
        </div>
      </div>
    </FramedPanel>
  );
};
