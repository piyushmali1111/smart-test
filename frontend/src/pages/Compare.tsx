import React, { useState } from 'react';
import { useScenarioStore } from '../store/useScenarioStore';
import { useCompareQuery } from '../hooks/useScenarioData';
import { Card } from '../components/ui/Card';
import { FramedPanel } from '../components/ui/FramedPanel';
import { Badge } from '../components/ui/Badge';
import { SegmentedControl } from '../components/ui/SegmentedControl';
import { RuntimeChart } from '../components/charts/RuntimeChart';
import { ValueBarChart } from '../components/charts/ValueBarChart';
import { Insight } from '../components/ui/Insight';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { Zap, Cpu, GitFork, Star, Gauge } from 'lucide-react';
import type { AlgorithmCompareResult } from '../api/types';

export const Compare: React.FC = () => {
  const { changedIds, budgetSec } = useScenarioStore();
  const [scaleMode, setScaleMode] = useState<'linear' | 'log'>('linear');

  const { data: compareData, isLoading, isError, refetch } = useCompareQuery({
    changed: changedIds,
    budgetSec,
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-64 rounded-card" />
          <Skeleton className="h-64 rounded-card" />
          <Skeleton className="h-64 rounded-card" />
        </div>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Skeleton className="h-80 rounded-card" />
          <Skeleton className="h-80 rounded-card" />
        </div>
      </div>
    );
  }

  if (isError || !compareData) {
    return (
      <ErrorState
        message="Failed to load algorithm comparison data."
        onRetry={refetch}
      />
    );
  }

  const { results, scalability } = compareData;

  const greedy = results.find(r => r.algorithm === 'greedy') || results[0];
  const dp = results.find(r => r.algorithm === 'dp') || results[1];

  const minRuntime = Math.min(...results.map(r => r.runtimeMs));
  const maxValue = Math.max(...results.map(r => r.totalRisk));

  const speedup = (dp.runtimeMs / Math.max(0.1, greedy.runtimeMs)).toFixed(1);
  const gap = greedy.optimalityGapPct.toFixed(1);

  const getAlgorithmMeta = (res: AlgorithmCompareResult) => {
    switch (res.algorithm) {
      case 'greedy':
        return {
          title: 'Greedy Heuristic',
          subtitle: 'O(n log n) ratio sort',
          icon: Zap,
          accentColor: 'text-lavender',
        };
      case 'dp':
        return {
          title: 'Dynamic Programming',
          subtitle: 'O(n · W) pseudo-polynomial',
          icon: Cpu,
          accentColor: 'text-accent',
        };
      case 'bnb':
        return {
          title: 'Branch & Bound',
          subtitle: 'Best-first state tree search',
          icon: GitFork,
          accentColor: 'text-brand',
        };
    }
  };

  return (
    <div className="space-y-6">
      {/* 1. Three Algorithm Cards Side-by-Side */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {results.map((res) => {
          const meta = getAlgorithmMeta(res);
          const Icon = meta.icon;
          const isOptimal = res.totalRisk >= maxValue - 1e-4;
          const isFastest = res.runtimeMs === minRuntime;

          return (
            <Card
              key={res.algorithm}
              glow={isOptimal}
              className={`p-5 flex flex-col justify-between ${
                isOptimal ? 'border-border-strong shadow-glow-sm' : ''
              }`}
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2">
                    <div className="flex h-8 w-8 items-center justify-center rounded-panel bg-bg-3 border border-border text-brand">
                      <Icon className="h-4 w-4" />
                    </div>
                    <div>
                      <h3 className="font-heading text-base font-bold text-text-main">
                        {meta.title}
                      </h3>
                      <p className="text-[11px] font-mono text-text-dim">{meta.subtitle}</p>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1 items-end">
                    {isOptimal && (
                      <Badge variant="success" icon={<Star className="h-2.5 w-2.5" />}>
                        Optimal
                      </Badge>
                    )}
                    {isFastest && (
                      <Badge variant="brand" icon={<Gauge className="h-2.5 w-2.5" />}>
                        Fastest
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Big gradient risk value */}
                <FramedPanel className="my-4 text-center py-4">
                  <span className="text-[10px] font-semibold uppercase tracking-wider text-text-muted block">
                    Total Risk Captured
                  </span>
                  <div className="font-mono text-4xl sm:text-5xl font-extrabold text-gradient my-1">
                    {res.totalRisk.toFixed(2)}
                  </div>
                </FramedPanel>

                {/* 4 Small Mono Stats */}
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="rounded-panel bg-bg-3 p-2 border border-border/40">
                    <span className="text-[10px] uppercase text-text-dim block">Time Used</span>
                    <span className="font-bold text-text-main">{res.totalTimeSec.toFixed(1)} s</span>
                  </div>
                  <div className="rounded-panel bg-bg-3 p-2 border border-border/40">
                    <span className="text-[10px] uppercase text-text-dim block">Tests Run</span>
                    <span className="font-bold text-text-main">{res.testsSelected}</span>
                  </div>
                  <div className="rounded-panel bg-bg-3 p-2 border border-border/40">
                    <span className="text-[10px] uppercase text-text-dim block">Runtime</span>
                    <span className="font-bold text-accent">{res.runtimeMs.toFixed(2)} ms</span>
                  </div>
                  <div className="rounded-panel bg-bg-3 p-2 border border-border/40">
                    <span className="text-[10px] uppercase text-text-dim block">Optimality Gap</span>
                    <span className={`font-bold ${res.optimalityGapPct === 0 ? 'text-success' : 'text-warn'}`}>
                      {res.optimalityGapPct.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>

              {res.memoryKb && (
                <div className="mt-3 pt-3 border-t border-border/40 flex justify-between text-[11px] font-mono text-text-dim">
                  <span>Peak Memory</span>
                  <span>{res.memoryKb} KB</span>
                </div>
              )}
            </Card>
          );
        })}
      </div>

      {/* 2 & 3. Scalability Chart + Value Achieved Bar Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Scalability Chart (7 cols) */}
        <div className="lg:col-span-7">
          <Card
            title="Scalability vs Test Suite Size"
            subtitle="Runtime growth across increasing problem scale"
            menu
            headerAction={
              <SegmentedControl<'linear' | 'log'>
                size="sm"
                value={scaleMode}
                onChange={setScaleMode}
                options={[
                  { value: 'linear', label: 'Linear' },
                  { value: 'log', label: 'Log Scale' },
                ]}
              />
            }
          >
            <RuntimeChart data={scalability} scaleMode={scaleMode} height={290} />
          </Card>
        </div>

        {/* Value Achieved Bars (5 cols) */}
        <div className="lg:col-span-5">
          <Card
            title="Value Achieved"
            subtitle="Fault detection risk captured within current budget"
            menu
          >
            <ValueBarChart data={results} height={290} />
          </Card>
        </div>
      </div>

      {/* 4. One Computed Insight Line */}
      <Insight>
        {`Greedy is ${speedup}× faster than DP and within ${gap}% of theoretical optimal.`}
      </Insight>
    </div>
  );
};
