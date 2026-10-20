import React from 'react';
import { useNavigate } from 'react-router-dom';
import { GitCommit, Network, BrainCircuit, SlidersHorizontal, Play } from 'lucide-react';
import { cn } from '../../utils/cn';

export const PipelineStrip: React.FC = () => {
  const navigate = useNavigate();

  const steps = [
    { label: 'Change', icon: GitCommit, path: '/analysis', desc: 'Code Churn' },
    { label: 'Graph', icon: Network, path: '/analysis', desc: 'Call Impact' },
    { label: 'ML Risk', icon: BrainCircuit, path: '/results', desc: 'Risk Model' },
    { label: 'Optimize', icon: SlidersHorizontal, path: '/selection', desc: 'Knapsack' },
    { label: 'Run', icon: Play, path: '/replay', desc: 'Execution' },
  ];

  return (
    <div className="relative flex flex-col md:flex-row items-center justify-between gap-4 py-4 w-full">
      {steps.map((step, index) => {
        const Icon = step.icon;
        const isLast = index === steps.length - 1;

        return (
          <React.Fragment key={step.label}>
            {/* Step Node Card in FramedPanel style */}
            <button
              onClick={() => navigate(step.path)}
              className={cn(
                'group relative flex flex-1 flex-col items-center justify-center rounded-panel border border-border bg-bg-3 p-4 transition-all duration-200 w-full md:w-auto',
                'hover:-translate-y-1 hover:border-brand hover:shadow-glow-sm hover:bg-bg-4 cursor-pointer'
              )}
            >
              <div className="mb-2 flex h-10 w-10 items-center justify-center rounded-full border border-brand/30 bg-brand/10 text-brand shadow-glow-sm group-hover:scale-110 transition-transform">
                <Icon className="h-5 w-5" />
              </div>
              <span className="font-heading text-sm font-bold text-text-main group-hover:text-brand-200">
                {step.label}
              </span>
              <span className="text-[11px] font-mono text-text-dim mt-0.5">
                {step.desc}
              </span>
            </button>

            {/* Connecting dashed line with pulse effect */}
            {!isLast && (
              <div className="hidden md:flex flex-1 items-center justify-center relative px-2">
                <div className="h-[2px] w-full border-t border-dashed border-[rgba(148,163,255,0.35)] relative">
                  {/* Glowing moving dot in cyan accent */}
                  <div
                    className="absolute top-1/2 -mt-1 h-2 w-2 rounded-full bg-accent shadow-glow-accent animate-[pulse_2s_infinite]"
                    style={{ left: `${(index % 2) * 50 + 25}%` }}
                  />
                </div>
              </div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};
