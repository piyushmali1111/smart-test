import React, { useState, useEffect, useRef } from 'react';
import { useScenarioStore } from '../store/useScenarioStore';
import { useReplayQuery } from '../hooks/useScenarioData';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { SegmentedControl } from '../components/ui/SegmentedControl';
import { Slider } from '../components/ui/Slider';
import { Badge } from '../components/ui/Badge';
import { CumulativeReplayChart } from '../components/charts/CumulativeReplayChart';
import { Play, Pause, RotateCcw, Check, X, CheckCircle2 } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export const LiveReplay: React.FC = () => {
  const { budgetSec, setBudget } = useScenarioStore();
  const [numChanges, setNumChanges] = useState<10 | 20 | 50>(20);
  const [speed, setSpeed] = useState<1 | 2 | 4>(2);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  const { data: replayData } = useReplayQuery({ budgetSec, numChanges });

  const timerRef = useRef<number | null>(null);

  const steps = replayData?.steps || [];
  const totalBugs = replayData?.totalBugs || numChanges;
  const totalTestSuite = replayData?.totalTests || 30;

  const activeStep = steps[currentStepIndex - 1] || null;

  const cumulativeTestsRun = activeStep?.cumulativeTestsRun || 0;
  const cumulativeCaught = activeStep?.cumulativeCaught || 0;
  const cumulativeRunAll = activeStep?.cumulativeRunAll || 0;

  const isCompleted = steps.length > 0 && currentStepIndex >= steps.length;

  useEffect(() => {
    if (isPlaying && steps.length > 0) {
      const intervalMs = Math.max(150, Math.round(900 / speed));

      timerRef.current = window.setInterval(() => {
        setCurrentStepIndex((prev) => {
          if (prev >= steps.length) {
            setIsPlaying(false);
            return prev;
          }
          return prev + 1;
        });
      }, intervalMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, steps.length, speed]);

  const handleStart = () => {
    if (isCompleted) {
      setCurrentStepIndex(1);
    } else if (currentStepIndex === 0) {
      setCurrentStepIndex(1);
    }
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentStepIndex(0);
  };

  const recentChanges = steps
    .slice(0, currentStepIndex)
    .reverse()
    .slice(0, 6);

  const chartData = steps.slice(0, currentStepIndex).map((s) => ({
    step: s.step,
    ours: s.cumulativeTestsRun,
    runAll: s.cumulativeRunAll,
  }));

  const gridCount = 90;
  const activeTestIndices = new Set<number>();
  if (activeStep) {
    const seedOffset = activeStep.step * 7;
    for (let i = 0; i < activeStep.testsRun; i++) {
      activeTestIndices.add((seedOffset + i * 4) % gridCount);
    }
  }

  return (
    <div className="space-y-6">
      {/* 1. Control Bar */}
      <Card className="p-5">
        <div className="flex flex-col lg:flex-row items-stretch lg:items-center justify-between gap-4">
          <div className="w-full lg:w-72">
            <Slider
              min={5}
              max={120}
              step={5}
              value={budgetSec}
              onChange={setBudget}
              label="Per-Change Budget"
              unit="s"
            />
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <SegmentedControl<string>
              size="sm"
              value={String(numChanges)}
              onChange={(v) => {
                setNumChanges(Number(v) as any);
                handleReset();
              }}
              options={[
                { value: '10', label: '10 Steps' },
                { value: '20', label: '20 Steps' },
                { value: '50', label: '50 Steps' },
              ]}
            />

            <SegmentedControl<string>
              size="sm"
              value={`${speed}x`}
              onChange={(v) => setSpeed(Number(v.replace('x', '')) as any)}
              options={[
                { value: '1x', label: '1x' },
                { value: '2x', label: '2x' },
                { value: '4x', label: '4x' },
              ]}
            />

            <div className="flex items-center gap-2">
              {!isPlaying ? (
                <Button
                  variant="primary"
                  size="sm"
                  onClick={handleStart}
                  icon={<Play className="h-4 w-4" />}
                >
                  {currentStepIndex === 0 ? 'Start' : 'Resume'}
                </Button>
              ) : (
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handlePause}
                  icon={<Pause className="h-4 w-4" />}
                >
                  Pause
                </Button>
              )}

              <Button
                variant="icon"
                size="sm"
                onClick={handleReset}
                title="Reset Simulation"
              >
                <RotateCcw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </Card>

      {/* 2. Giant Live Counters */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Tests Run Counter */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Cumulative Tests Executed
            </span>
            {isCompleted && (
              <Badge variant="success" icon={<CheckCircle2 className="h-3 w-3" />}>
                Complete
              </Badge>
            )}
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-mono text-5xl sm:text-6xl font-extrabold text-gradient">
              {cumulativeTestsRun}
            </span>
            <span className="font-mono text-xl text-text-dim">
              / {cumulativeRunAll || totalTestSuite * numChanges}
            </span>
          </div>

          {/* Thin progress bar: gradient --brand to --accent */}
          <div className="mt-3 h-1.5 w-full rounded-full bg-bg-4 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-brand to-accent shadow-glow-accent transition-all duration-200"
              style={{
                width: `${
                  cumulativeRunAll > 0
                    ? Math.min(100, (cumulativeTestsRun / cumulativeRunAll) * 100)
                    : 0
                }%`,
              }}
            />
          </div>
          <span className="text-[11px] font-mono text-text-dim mt-2 block">
            {cumulativeRunAll > 0
              ? `${Math.round((1 - cumulativeTestsRun / cumulativeRunAll) * 100)}% execution reduction`
              : 'Waiting to start...'}
          </span>
        </Card>

        {/* Bugs Caught Counter */}
        <Card className="p-6">
          <div className="flex items-center justify-between">
            <span className="text-xs font-semibold uppercase tracking-wider text-text-muted">
              Bugs Detected
            </span>
            <span className="text-xs font-mono text-text-muted">
              Step {currentStepIndex} of {steps.length}
            </span>
          </div>

          <div className="mt-3 flex items-baseline gap-2">
            <span className="font-mono text-5xl sm:text-6xl font-extrabold text-gradient">
              {cumulativeCaught}
            </span>
            <span className="font-mono text-xl text-text-dim">/ {currentStepIndex || totalBugs}</span>
          </div>

          {/* Thin progress bar: gradient --brand to --accent */}
          <div className="mt-3 h-1.5 w-full rounded-full bg-bg-4 overflow-hidden">
            <div
              className="h-full bg-gradient-to-r from-brand to-accent shadow-glow-accent transition-all duration-200"
              style={{
                width: `${
                  currentStepIndex > 0
                    ? Math.min(100, (cumulativeCaught / currentStepIndex) * 100)
                    : 0
                }%`,
              }}
            />
          </div>
          <span className="text-[11px] font-mono text-text-dim mt-2 block">
            {currentStepIndex > 0
              ? `${((cumulativeCaught / currentStepIndex) * 100).toFixed(1)}% detection retention`
              : 'Waiting to start...'}
          </span>
        </Card>
      </div>

      {/* 3 & 4. Live Test Grid + Live Change Feed */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Live Test Grid (7 cols) */}
        <div className="lg:col-span-7">
          <Card
            title="Live Suite Execution"
            subtitle="Flashes indicate executed tests per change commit"
          >
            <div className="grid grid-cols-10 sm:grid-cols-15 gap-1.5 p-3 rounded-panel bg-bg-0/60 border border-border/40">
              {Array.from({ length: gridCount }).map((_, i) => {
                const isActive = activeTestIndices.has(i);
                return (
                  <div
                    key={i}
                    className={`h-4 w-full rounded-sm transition-all duration-300 border ${
                      isActive
                        ? 'bg-accent border-accent/60 shadow-glow-accent scale-105'
                        : 'bg-bg-3 border-[rgba(148,163,255,0.06)] opacity-40'
                    }`}
                  />
                );
              })}
            </div>
            <div className="mt-3 flex items-center justify-between text-xs text-text-dim">
              <span>Suite capacity: {gridCount} test targets</span>
              <span className="font-mono text-accent">
                {activeTestIndices.size} executed this step
              </span>
            </div>
          </Card>
        </div>

        {/* Change Feed (5 cols) */}
        <div className="lg:col-span-5">
          <Card title="Change Feed" subtitle="Real-time simulated commit stream">
            <div className="space-y-2 min-h-[220px]">
              <AnimatePresence>
                {recentChanges.length === 0 ? (
                  <div className="text-center py-10 text-xs text-text-dim">
                    Press Start to begin simulation.
                  </div>
                ) : (
                  recentChanges.map((change) => (
                    <motion.div
                      key={change.step}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0 }}
                      className="flex items-center justify-between rounded-panel border border-border bg-bg-3 p-2.5 text-xs font-mono"
                    >
                      <div className="flex items-center gap-2 truncate">
                        <span className="text-text-dim">#{change.step}</span>
                        <span className="truncate text-text-main font-bold">
                          {change.changedId}
                        </span>
                      </div>

                      <div className="flex items-center gap-2 flex-shrink-0">
                        <span className="text-text-muted">{change.testsRun} tests</span>
                        {change.caught ? (
                          <span className="flex items-center gap-1 text-[11px] text-success bg-success/10 px-2 py-0.5 rounded-full border border-success/30 font-medium">
                            <Check className="h-3 w-3" /> Caught
                          </span>
                        ) : (
                          <span className="flex items-center gap-1 text-[11px] text-danger bg-danger/10 px-2 py-0.5 rounded-full border border-danger/30 font-medium">
                            <X className="h-3 w-3" /> Missed
                          </span>
                        )}
                      </div>
                    </motion.div>
                  ))
                )}
              </AnimatePresence>
            </div>
          </Card>
        </div>
      </div>

      {/* 5. Cumulative Line Chart */}
      <Card
        title="Cumulative Tests Run"
        subtitle="Divergence between Smart Test Selection and Run-All baseline"
        menu
      >
        <CumulativeReplayChart data={chartData} height={260} />
      </Card>
    </div>
  );
};
