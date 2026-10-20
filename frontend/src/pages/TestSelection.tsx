import React, { useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { useScenarioStore } from '../store/useScenarioStore';
import { useAffectedQuery, useSelectQuery } from '../hooks/useScenarioData';
import { useDebounce } from '../hooks/useDebounce';
import { Card } from '../components/ui/Card';
import { Slider } from '../components/ui/Slider';
import { SegmentedControl } from '../components/ui/SegmentedControl';
import { ProgressRing } from '../components/ui/ProgressRing';
import { BudgetBar } from '../components/selection/BudgetBar';
import { TestsTable } from '../components/selection/TestsTable';
import { Button } from '../components/ui/Button';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { Insight } from '../components/ui/Insight';
import { ArrowRight } from 'lucide-react';
import type { AlgorithmType } from '../api/types';

export const TestSelection: React.FC = () => {
  const navigate = useNavigate();
  const { changedIds, budgetSec, setBudget, algorithm, setAlgorithm } = useScenarioStore();

  const debouncedBudget = useDebounce(budgetSec, 300);

  const { data: affectedData, isLoading: affectedLoading, isError: affectedError, refetch: refetchAffected } =
    useAffectedQuery(changedIds);

  const { data: selectData, isLoading: selectLoading, isError: selectError, refetch: refetchSelect } =
    useSelectQuery({
      changed: changedIds,
      budgetSec: debouncedBudget,
      algorithm,
    });

  const candidateTests = affectedData?.candidateTests || [];
  const selectedIds = selectData?.selected || [];

  const selectedTests = useMemo(() => {
    const selSet = new Set(selectedIds);
    return candidateTests.filter((t) => selSet.has(t.id));
  }, [candidateTests, selectedIds]);

  if (affectedLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-28 rounded-card" />
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Skeleton className="h-32 rounded-card" />
          <Skeleton className="h-32 rounded-card" />
          <Skeleton className="h-32 rounded-card" />
          <Skeleton className="h-32 rounded-card" />
        </div>
        <Skeleton className="h-24 rounded-card" />
        <Skeleton className="h-80 rounded-card" />
      </div>
    );
  }

  if (affectedError || !affectedData) {
    return (
      <ErrorState
        message="Failed to load test selection data."
        onRetry={() => {
          refetchAffected();
          refetchSelect();
        }}
      />
    );
  }

  const fastestTestTime = candidateTests.length > 0
    ? Math.min(...candidateTests.map(t => t.timeSec))
    : 0;

  const isBudgetTooSmall = budgetSec < fastestTestTime;

  const totalTimeUsed = selectData?.totalTimeSec || 0;
  const totalRiskScore = selectData?.totalRisk || 0;
  const coveragePct = selectData?.coveragePct || 0;
  const runtimeMs = selectData?.algorithmRuntimeMs || 0.4;

  return (
    <div className="space-y-6">
      {/* 1. Control Bar */}
      <Card className="p-6">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-center">
          <div className="lg:col-span-7">
            <Slider
              min={5}
              max={150}
              step={5}
              value={budgetSec}
              onChange={setBudget}
              label="Execution Time Budget"
              unit="s"
            />
          </div>

          <div className="lg:col-span-5 flex flex-col sm:flex-row items-start sm:items-center justify-end gap-3">
            <div className="flex flex-col gap-1 w-full sm:w-auto">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-text-dim">
                Optimization Algorithm
              </span>
              <SegmentedControl<AlgorithmType>
                value={algorithm}
                onChange={setAlgorithm}
                options={[
                  { value: 'greedy', label: 'Greedy' },
                  { value: 'dp', label: 'DP 0/1' },
                  { value: 'bnb', label: 'Branch & Bound' },
                ]}
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Warning if budget is below fastest test */}
      {isBudgetTooSmall && (
        <Insight className="border-warn text-warn">
          Budget ({budgetSec}s) is below the fastest test ({fastestTestTime.toFixed(1)}s). Increase budget to run tests.
        </Insight>
      )}

      {/* 2. Four KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* KPI 1: Time Used vs Budget */}
        <Card className="p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Time Budget Used
            </span>
            <div className="mt-1 font-mono text-xl font-bold text-text-main">
              {totalTimeUsed.toFixed(1)} <span className="text-xs text-text-dim">/ {budgetSec}s</span>
            </div>
          </div>
          <ProgressRing
            value={totalTimeUsed}
            max={budgetSec}
            size={76}
            strokeWidth={7}
            unit="s"
          />
        </Card>

        {/* KPI 2: Total Risk Value Captured */}
        <Card className="p-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            Risk Value Captured
          </span>
          <div className="mt-2 font-mono text-3xl font-extrabold text-gradient">
            {totalRiskScore.toFixed(2)}
          </div>
          <span className="text-[11px] text-text-dim mt-1 block">
            Aggregated fault probability
          </span>
        </Card>

        {/* KPI 3: Tests Selected Ratio */}
        <Card className="p-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            Selected Ratio
          </span>
          <div className="mt-2 font-mono text-3xl font-extrabold text-accent">
            {selectedIds.length} <span className="text-lg text-text-dim">/ {candidateTests.length}</span>
          </div>
          <span className="text-[11px] text-text-dim mt-1 block">
            {candidateTests.length > 0
              ? `${Math.round((selectedIds.length / candidateTests.length) * 100)}% of candidates`
              : '0 candidates'}
          </span>
        </Card>

        {/* KPI 4: Coverage % */}
        <Card className="p-4">
          <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
            Code Impact Coverage
          </span>
          <div className="mt-2 font-mono text-3xl font-extrabold text-text-main">
            {coveragePct.toFixed(1)}%
          </div>
          <span className="text-[11px] text-text-dim mt-1 block">
            Affected functions validated
          </span>
        </Card>
      </div>

      {/* 3. Budget Bar (Signature Knapsack Visual) */}
      <Card className="p-5">
        <BudgetBar
          budgetSec={budgetSec}
          selectedTests={selectedTests}
          totalTimeUsed={totalTimeUsed}
        />
      </Card>

      {/* 4. Candidate Tests Table */}
      <Card title="Candidate Tests" subtitle="Prioritized subset under dynamic budget constraint">
        <TestsTable
          tests={candidateTests}
          selectedIds={selectedIds}
          budgetSec={budgetSec}
        />
      </Card>

      {/* 5. Footer Row */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-2">
        <div className="font-mono text-xs text-text-dim">
          Algorithm runtime: <span className="text-accent font-bold">{runtimeMs.toFixed(2)} ms</span> ({algorithm.toUpperCase()})
        </div>

        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate('/compare')}
          icon={<ArrowRight className="h-4 w-4" />}
        >
          Compare Algorithms
        </Button>
      </div>
    </div>
  );
};
