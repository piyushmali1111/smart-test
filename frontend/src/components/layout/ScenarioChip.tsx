import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useScenarioStore } from '../../store/useScenarioStore';
import { ShieldAlert, Clock, ChevronRight } from 'lucide-react';
import { cn } from '../../utils/cn';

interface ScenarioChipProps {
  collapsed?: boolean;
}

export const ScenarioChip: React.FC<ScenarioChipProps> = ({ collapsed = false }) => {
  const navigate = useNavigate();
  const { changedIds, budgetSec } = useScenarioStore();
  const primaryChange = changedIds[0]?.split('.').pop() || 'none';

  if (collapsed) {
    return (
      <button
        onClick={() => navigate('/analysis')}
        title={`Scenario: ${primaryChange} (${budgetSec}s)`}
        className="flex w-full flex-col items-center justify-center rounded-panel border border-border bg-bg-3 p-2 hover:border-border-strong hover:bg-bg-4 transition-all"
      >
        <span className="h-2 w-2 rounded-full bg-accent shadow-glow-sm mb-1" />
        <span className="font-mono text-[10px] text-accent">{budgetSec}s</span>
      </button>
    );
  }

  return (
    <div
      onClick={() => navigate('/analysis')}
      className={cn(
        'group cursor-pointer rounded-panel border border-border bg-bg-3 p-3 transition-all duration-200',
        'hover:border-border-strong hover:bg-bg-4 hover:shadow-glow-sm'
      )}
    >
      <div className="flex items-center justify-between text-[11px] font-semibold uppercase tracking-wider text-text-muted mb-2">
        <span>Current Scenario</span>
        <ChevronRight className="h-3.5 w-3.5 text-text-dim group-hover:text-brand transition-colors" />
      </div>

      <div className="space-y-1.5 text-xs font-mono">
        <div className="flex items-center gap-1.5 text-text-main truncate">
          <ShieldAlert className="h-3.5 w-3.5 text-warn flex-shrink-0" />
          <span className="truncate text-text-main font-semibold">
            {primaryChange}
            {changedIds.length > 1 ? ` (+${changedIds.length - 1})` : ''}
          </span>
        </div>
        <div className="flex items-center gap-1.5 text-text-muted">
          <Clock className="h-3.5 w-3.5 text-brand flex-shrink-0" />
          <span className="text-text-main font-bold">{budgetSec} s</span>
          <span className="text-text-dim text-[10px]">limit</span>
        </div>
      </div>
    </div>
  );
};
