import React from 'react';
import { motion } from 'framer-motion';
import { Tooltip } from '../ui/Tooltip';
import type { CandidateTest } from '../../api/types';

interface BudgetBarProps {
  budgetSec: number;
  selectedTests: CandidateTest[];
  totalTimeUsed: number;
}

export const BudgetBar: React.FC<BudgetBarProps> = ({
  budgetSec,
  selectedTests,
  totalTimeUsed,
}) => {
  const freeTime = Math.max(0, budgetSec - totalTimeUsed);
  const freePct = Math.max(0, (freeTime / budgetSec) * 100);

  return (
    <div className="w-full space-y-2">
      <div className="flex items-center justify-between text-xs font-semibold text-text-muted">
        <span>Knapsack Budget Allocation</span>
        <span className="font-mono text-accent">
          {totalTimeUsed.toFixed(1)} s / {budgetSec} s ({Math.round((totalTimeUsed / budgetSec) * 100)}%)
        </span>
      </div>

      <div className="relative flex h-10 w-full overflow-hidden rounded-panel border border-border bg-bg-3 p-1">
        {selectedTests.map((test) => {
          const widthPct = Math.max(1, (test.timeSec / budgetSec) * 100);
          const shortName = test.name.split('::').pop()?.replace('test_', '') || test.name;

          return (
            <Tooltip
              key={test.id}
              content={`${shortName}: ${test.timeSec}s (Risk: ${test.risk.toFixed(2)})`}
            >
              <motion.div
                layout
                transition={{ type: 'spring', stiffness: 260, damping: 28 }}
                style={{ width: `${widthPct}%` }}
                className="group relative flex h-full items-center justify-center overflow-hidden rounded-sm border-r border-bg-3 bg-gradient-to-r from-brand to-accent px-1 text-[11px] font-mono font-bold text-[#0B1020] shadow-glow-sm hover:brightness-110"
              >
                <span className="truncate group-hover:block hidden sm:block">
                  {shortName}
                </span>
              </motion.div>
            </Tooltip>
          );
        })}

        {/* Free space area (hatched --bg-4) */}
        {freeTime > 0.05 && (
          <Tooltip content={`Unused budget: ${freeTime.toFixed(1)}s`}>
            <div
              style={{ width: `${freePct}%` }}
              className="relative flex h-full items-center justify-center rounded-sm bg-bg-4 bg-[linear-gradient(45deg,rgba(255,255,255,0.03)_25%,transparent_25%,transparent_50%,rgba(255,255,255,0.03)_50%,rgba(255,255,255,0.03)_75%,transparent_75%,transparent)] bg-[length:12px_12px] px-2 text-[10px] font-mono text-text-dim"
            >
              <span className="hidden sm:inline truncate">{freeTime.toFixed(1)}s free</span>
            </div>
          </Tooltip>
        )}
      </div>
    </div>
  );
};
