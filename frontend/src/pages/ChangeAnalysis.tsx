import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGraphQuery, useAffectedQuery } from '../hooks/useScenarioData';
import { useScenarioStore } from '../store/useScenarioStore';
import { DependencyGraph } from '../components/graph/DependencyGraph';
import { GraphLegend } from '../components/graph/GraphLegend';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Insight } from '../components/ui/Insight';
import { Skeleton } from '../components/ui/Skeleton';
import { ErrorState } from '../components/ui/ErrorState';
import { ArrowRight, GitCommit, Search, ShieldAlert, CheckSquare, RotateCw } from 'lucide-react';

export const ChangeAnalysis: React.FC = () => {
  const navigate = useNavigate();
  const { changedIds, toggleChanged, setChanged } = useScenarioStore();
  const [search, setSearch] = useState('');

  const { data: graphData, isLoading: graphLoading, isError: graphError, refetch: refetchGraph } = useGraphQuery();
  const { data: affectedData, isLoading: affectedLoading, isError: affectedError, refetch: refetchAffected } = useAffectedQuery(changedIds);

  if (graphLoading || affectedLoading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 h-[720px]">
        <div className="lg:col-span-8">
          <Skeleton className="h-full rounded-card" />
        </div>
        <div className="lg:col-span-4 space-y-4">
          <Skeleton className="h-48 rounded-card" />
          <Skeleton className="h-48 rounded-card" />
        </div>
      </div>
    );
  }

  if (graphError || affectedError || !graphData || !affectedData) {
    return (
      <ErrorState
        message="Failed to load dependency graph or affected functions."
        onRetry={() => {
          refetchGraph();
          refetchAffected();
        }}
      />
    );
  }

  const filteredNodes = graphData.nodes.filter(n =>
    n.label.toLowerCase().includes(search.toLowerCase())
  );

  const affectedCount = affectedData.affected.length;
  const candidateTestsCount = affectedData.candidateTests.length;
  const cycleCount = affectedData.sccGroups.length;

  return (
    <div className="space-y-6">
      {/* 2-Column Layout: Graph (68%) + Controls/Stats (32%) */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        {/* Left: Interactive Dependency Graph */}
        <div className="lg:col-span-8 h-[680px] flex flex-col">
          <div className="mb-2 flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Call Graph & Reachability
            </span>
            <GraphLegend />
          </div>

          <div className="flex-1 min-h-0">
            <DependencyGraph
              graphData={graphData}
              affectedData={affectedData}
              onNodeClick={(id, shiftKey) => toggleChanged(id, shiftKey)}
            />
          </div>
        </div>

        {/* Right: Pick Change & Stats Panel */}
        <div className="lg:col-span-4 space-y-6">
          <Card title="Pick Change" subtitle="Select altered function to propagate impact">
            <div className="space-y-4">
              {/* Search select input */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-dim" />
                <input
                  type="text"
                  placeholder="Filter functions..."
                  value={search}
                  onChange={(e) => setSearch(e.target.value)}
                  className="w-full rounded-panel border border-border bg-bg-3 pl-9 pr-3 py-2 text-xs text-text-main placeholder:text-text-dim focus:border-brand focus:outline-none"
                />
              </div>

              {/* Function List */}
              <div className="max-h-56 overflow-y-auto space-y-1 rounded-panel border border-border/60 bg-bg-3/40 p-2">
                {filteredNodes.map((node) => {
                  const isSelected = changedIds.includes(node.id);
                  return (
                    <button
                      key={node.id}
                      type="button"
                      onClick={() => setChanged([node.id])}
                      className={`flex w-full items-center justify-between rounded-btn px-2.5 py-1.5 text-xs font-mono transition-all text-left ${
                        isSelected
                          ? 'border border-danger/60 bg-danger/15 text-danger font-bold'
                          : 'text-text-muted hover:bg-bg-4 hover:text-text-main'
                      }`}
                    >
                      <div className="flex items-center gap-1.5 truncate">
                        <GitCommit className="h-3.5 w-3.5 flex-shrink-0" />
                        <span className="truncate">{node.label}</span>
                      </div>
                      {isSelected && (
                        <span className="text-[10px] uppercase font-bold text-danger">Changed</span>
                      )}
                    </button>
                  );
                })}
              </div>

              {/* Impact Metrics Rows */}
              <div className="space-y-2 pt-2 border-t border-border/50">
                <div className="flex items-center justify-between rounded-panel bg-bg-3 p-3">
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <ShieldAlert className="h-4 w-4 text-warn" />
                    <span>Affected Functions</span>
                  </div>
                  <span className="font-mono text-base font-bold text-warn">
                    {affectedCount}
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-panel bg-bg-3 p-3">
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <CheckSquare className="h-4 w-4 text-accent" />
                    <span>Candidate Tests</span>
                  </div>
                  <span className="font-mono text-base font-bold text-accent">
                    {candidateTestsCount}
                  </span>
                </div>

                <div className="flex items-center justify-between rounded-panel bg-bg-3 p-3">
                  <div className="flex items-center gap-2 text-xs text-text-muted">
                    <RotateCw className="h-4 w-4 text-lavender" />
                    <span>SCC Cycle Groups</span>
                  </div>
                  <span className="font-mono text-base font-bold text-lavender">
                    {cycleCount}
                  </span>
                </div>
              </div>

              {/* Continue button */}
              <Button
                variant="primary"
                size="lg"
                className="w-full"
                onClick={() => navigate('/selection')}
                icon={<ArrowRight className="h-4 w-4" />}
              >
                Continue to Selection
              </Button>
            </div>
          </Card>

          {/* Computed Dynamic Insight */}
          <Insight>
            {`${changedIds.length} change${changedIds.length > 1 ? 's' : ''} reaches ${affectedCount} affected functions across ${candidateTestsCount} tests.`}
          </Insight>
        </div>
      </div>
    </div>
  );
};
