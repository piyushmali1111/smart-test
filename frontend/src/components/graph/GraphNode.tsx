import React, { memo } from 'react';
import { Handle, Position, type NodeProps } from '@xyflow/react';
import { Code, FileCode, RotateCw } from 'lucide-react';
import { cn } from '../../utils/cn';

export interface CustomNodeData {
  label: string;
  file: string;
  kind: 'file' | 'function';
  status: 'changed' | 'affected' | 'unaffected';
  distance?: number;
  inCycle?: boolean;
}

export const GraphNodeComponent = memo(({ data }: NodeProps) => {
  const nodeData = data as unknown as CustomNodeData;
  const { label, file, kind, status, distance, inCycle } = nodeData;

  const statusStyles = {
    changed: 'border-danger bg-danger/10 text-danger shadow-[0_0_12px_rgba(248,113,113,0.25)]',
    affected:
      distance === 1
        ? 'border-[#F59E0B] bg-warn/10 text-[#F59E0B] shadow-[0_0_10px_rgba(245,158,11,0.2)]'
        : 'border-warn/70 bg-warn/5 text-warn shadow-[0_0_8px_rgba(251,191,36,0.15)]',
    unaffected: 'border-border/50 bg-bg-2 text-slate opacity-40',
  };

  const simpleLabel = label.split('.').pop() || label;

  return (
    <div
      className={cn(
        'group relative min-w-[150px] rounded-panel border px-3 py-2 text-left transition-all duration-200 select-none cursor-pointer',
        inCycle && 'border-dashed border-[rgba(165,180,252,0.6)]',
        statusStyles[status]
      )}
    >
      {/* Target input handle (Left) */}
      <Handle
        type="target"
        position={Position.Left}
        className="!h-2 !w-2 !rounded-full !border !border-border !bg-bg-4"
      />

      <div className="flex items-center justify-between gap-1.5 mb-1">
        <div className="flex items-center gap-1.5 truncate">
          {kind === 'file' ? (
            <FileCode className="h-3.5 w-3.5 flex-shrink-0" />
          ) : (
            <Code className="h-3.5 w-3.5 flex-shrink-0" />
          )}
          <span className="font-mono text-xs font-bold text-text-main truncate">
            {simpleLabel}
          </span>
        </div>

        {inCycle && (
          <span className="flex items-center gap-0.5 rounded-full bg-lavender/20 px-1 py-0.2 text-[9px] font-bold text-lavender">
            <RotateCw className="h-2.5 w-2.5" />
            Cycle
          </span>
        )}
      </div>

      <div className="flex items-center justify-between text-[10px] text-text-dim font-mono">
        <span className="truncate max-w-[90px]">{file.split('/').pop()}</span>
        {distance !== undefined && (
          <span className="font-semibold text-text-muted">d={distance}</span>
        )}
      </div>

      {/* Source output handle (Right) */}
      <Handle
        type="source"
        position={Position.Right}
        className="!h-2 !w-2 !rounded-full !border !border-border !bg-bg-4"
      />
    </div>
  );
});

GraphNodeComponent.displayName = 'GraphNodeComponent';
