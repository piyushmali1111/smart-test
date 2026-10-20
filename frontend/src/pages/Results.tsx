import React, { useState } from 'react';
import { useResultsQuery, useModelsQuery } from '../hooks/useScenarioData';
import { Card } from '../components/ui/Card';
import { Tabs } from '../components/ui/Tabs';
import { StatCard } from '../components/ui/StatCard';
import { DetectionChart } from '../components/charts/DetectionChart';
import { TimeSavedChart } from '../components/charts/TimeSavedChart';
import { ModelChart } from '../components/charts/ModelChart';
import { FeatureChart } from '../components/charts/FeatureChart';
import { DonutChart } from '../components/charts/DonutChart';
import { FramedPanel } from '../components/ui/FramedPanel';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { CheckCircle2 } from 'lucide-react';

export const Results: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'performance' | 'models' | 'dataset'>('performance');

  const { data: results, isLoading: resultsLoading, isError: resultsError, refetch: refetchResults } = useResultsQuery();
  const { data: modelsData, isLoading: modelsLoading, isError: modelsError, refetch: refetchModels } = useModelsQuery();

  if (resultsLoading || modelsLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-12 w-80 rounded-panel" />
        <Skeleton className="h-96 rounded-card" />
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Skeleton className="h-32 rounded-card" />
          <Skeleton className="h-32 rounded-card" />
          <Skeleton className="h-32 rounded-card" />
        </div>
      </div>
    );
  }

  if (resultsError || modelsError || !results || !modelsData) {
    return (
      <ErrorState
        message="Failed to load empirical results."
        onRetry={() => {
          refetchResults();
          refetchModels();
        }}
      />
    );
  }

  const { headline, detectionVsBudget, strategies, dataset } = results;

  return (
    <div className="space-y-6">
      {/* 3 Tabs Navigation */}
      <Tabs
        activeTab={activeTab}
        onChange={(id) => setActiveTab(id as any)}
        tabs={[
          { id: 'performance', label: 'Empirical Performance' },
          { id: 'models', label: 'ML Risk Model' },
          { id: 'dataset', label: 'Mutation Dataset' },
        ]}
      />

      {/* Tab 1: Performance */}
      {activeTab === 'performance' && (
        <div className="space-y-6">
          {/* Hero Line Chart */}
          <Card
            title="Bugs Caught vs Time Budget"
            subtitle="Mutation test fault detection across escalating execution allowances"
            menu
            exportFilename="detection_vs_budget.csv"
          >
            <FramedPanel className="p-2">
              <DetectionChart data={detectionVsBudget} height={340} />
            </FramedPanel>
          </Card>

          {/* Headline Stat Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard
              label="Tests Reduced"
              value={headline.testReductionPct}
              suffix="%"
              decimals={1}
              trend="up"
              trendLabel="workload reduction"
              glow
            />
            <StatCard
              label="Time Saved"
              value={headline.timeSavedPct}
              suffix="%"
              decimals={1}
              trend="up"
              trendLabel="pipeline acceleration"
              glow
            />
            <StatCard
              label="Bugs Still Caught"
              value={headline.bugDetectionPct}
              suffix="%"
              decimals={1}
              trend="up"
              trendLabel="fault coverage"
              glow
            />
          </div>

          {/* Time Saved Bar Chart & Compact Table */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            <div className="lg:col-span-6">
              <Card
                title="Time Saved by Strategy"
                subtitle="Comparison against full regression suite execution"
                menu
                exportFilename="time_saved_strategies.csv"
              >
                <TimeSavedChart data={strategies} height={260} />
              </Card>
            </div>

            <div className="lg:col-span-6">
              <Card title="Strategy Benchmarks" subtitle="Performance across controlled mutation suite" menu>
                <div className="overflow-x-auto rounded-panel border border-border">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="border-b border-border bg-bg-3/60 text-text-muted">
                        <th className="py-2.5 px-3 font-semibold">Strategy</th>
                        <th className="py-2.5 px-3 font-semibold text-center">Tests</th>
                        <th className="py-2.5 px-3 font-semibold text-center">Time</th>
                        <th className="py-2.5 px-3 font-semibold text-right">Bugs Caught</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-border/50">
                      {strategies.map((strat, i) => {
                        const isOurs = strat.name.startsWith('Ours');
                        return (
                          <tr
                            key={i}
                            className={
                              isOurs
                                ? 'bg-[rgba(34,211,238,0.07)] border-l-[3px] border-l-accent font-bold text-accent'
                                : 'text-text-muted hover:bg-bg-3/30'
                            }
                          >
                            <td className="py-2.5 px-3 flex items-center gap-1.5">
                              {isOurs && <CheckCircle2 className="h-3.5 w-3.5 text-accent" />}
                              <span>{strat.name}</span>
                            </td>
                            <td className="py-2.5 px-3 font-mono text-center">{strat.testsRun}</td>
                            <td className="py-2.5 px-3 font-mono text-center">{strat.timeSec.toFixed(1)}s</td>
                            <td className="py-2.5 px-3 font-mono text-right text-text-main">
                              {strat.bugsCaughtPct.toFixed(1)}%
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </Card>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: ML Model */}
      {activeTab === 'models' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Grouped Bar Chart */}
            <div className="lg:col-span-7">
              <Card
                title="Model Performance Comparison"
                subtitle="Cross-validated metrics on held-out mutants"
                menu
                exportFilename="model_metrics.csv"
              >
                <ModelChart data={modelsData.models} height={290} />
              </Card>
            </div>

            {/* Feature Importance */}
            <div className="lg:col-span-5">
              <Card
                title="Feature Importance"
                subtitle="Permutation importance in Random Forest"
                menu
                exportFilename="feature_importance.csv"
              >
                <FeatureChart data={modelsData.featureImportance} height={290} />
              </Card>
            </div>
          </div>

          {/* Mini Risk Score Distribution */}
          <Card title="Risk Distribution" subtitle="Predicted failure likelihood across test suite">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-xs font-mono">
              <div className="rounded-panel bg-bg-3 p-3 border border-border/50">
                <span className="text-[10px] text-text-dim block uppercase">Mean Risk</span>
                <span className="text-xl font-bold text-accent">0.42</span>
              </div>
              <div className="rounded-panel bg-bg-3 p-3 border border-border/50">
                <span className="text-[10px] text-text-dim block uppercase">Median Risk</span>
                <span className="text-xl font-bold text-text-main">0.38</span>
              </div>
              <div className="rounded-panel bg-bg-3 p-3 border border-border/50">
                <span className="text-[10px] text-text-dim block uppercase">Top Decile</span>
                <span className="text-xl font-bold text-warn">0.89</span>
              </div>
              <div className="rounded-panel bg-bg-3 p-3 border border-border/50">
                <span className="text-[10px] text-text-dim block uppercase">AUC-ROC</span>
                <span className="text-xl font-bold text-brand-200">0.93</span>
              </div>
            </div>
          </Card>
        </div>
      )}

      {/* Tab 3: Dataset */}
      {activeTab === 'dataset' && (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard label="Mutants Injected" value={dataset.mutants} glow />
            <StatCard label="Tests in Suite" value={dataset.tests} glow />
            <StatCard label="Training Rows" value={dataset.rows} glow />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
            <div className="lg:col-span-6">
              <Card title="Mutation Types Distribution" subtitle="AST synthetic defect taxonomy" menu>
                <DonutChart data={dataset.mutationTypes} height={250} />
              </Card>
            </div>

            <div className="lg:col-span-6 space-y-4">
              <Card title="Rigorous Methodology" subtitle="Preventing data leakage and overfitting">
                <ul className="space-y-3 text-xs text-text-muted">
                  <li className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent shadow-glow-accent" />
                    <span className="text-text-main font-semibold">Split by bug, not by row.</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-brand shadow-glow-sm" />
                    <span>Cross-validation grouped strictly by mutant AST location.</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-accent shadow-glow-accent" />
                    <span>Fixed random seed for total reproducibility across pipeline runs.</span>
                  </li>
                </ul>
              </Card>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
