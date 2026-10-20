import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { StatCard } from '../components/ui/StatCard';
import { TestGrid } from '../components/visuals/TestGrid';
import { PipelineStrip } from '../components/visuals/PipelineStrip';
import { useResultsQuery } from '../hooks/useScenarioData';
import { projectConfig } from '../config/project';
import { ArrowRight, BarChart2, ShieldCheck } from 'lucide-react';
import { Skeleton } from '../components/ui/Skeleton';

export const Overview: React.FC = () => {
  const navigate = useNavigate();
  const { data: results, isLoading } = useResultsQuery();

  const headline = results?.headline || {
    testReductionPct: 68.4,
    timeSavedPct: 74.2,
    bugDetectionPct: 94.6,
  };

  return (
    <div className="space-y-10 pb-8">
      {/* Hero Section */}
      <section className="flex flex-col items-center text-center pt-4 sm:pt-8 max-w-3xl mx-auto space-y-4">
        {/* Pill Badge */}
        <Badge variant="brand" icon={<ShieldCheck className="h-3.5 w-3.5" />}>
          {projectConfig.year} · {projectConfig.course}
        </Badge>

        {/* Hero Headline */}
        <h1 className="font-heading text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight text-gradient leading-tight">
          Smart Test Selection
        </h1>

        {/* Subtitle */}
        <p className="text-base sm:text-lg text-text-muted max-w-xl font-normal">
          {projectConfig.subtitle}
        </p>

        {/* CTA Buttons */}
        <div className="flex items-center gap-4 pt-2">
          <Button
            variant="primary"
            size="lg"
            onClick={() => navigate('/analysis')}
            icon={<ArrowRight className="h-4 w-4" />}
          >
            Start Demo
          </Button>
          <Button
            variant="ghost"
            size="lg"
            onClick={() => navigate('/results')}
            icon={<BarChart2 className="h-4 w-4" />}
          >
            View Results
          </Button>
        </div>
      </section>

      {/* Signature Test Grid Visual */}
      <section>
        <TestGrid totalCount={180} />
      </section>

      {/* 5-Step Pipeline Strip */}
      <section>
        <div className="mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-text-dim">
            Algorithmic Pipeline
          </span>
        </div>
        <PipelineStrip />
      </section>

      {/* 3 Headline KPI StatCards */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {isLoading ? (
          <>
            <Skeleton className="h-36 rounded-card" />
            <Skeleton className="h-36 rounded-card" />
            <Skeleton className="h-36 rounded-card" />
          </>
        ) : (
          <>
            <StatCard
              label="Tests Reduced"
              value={headline.testReductionPct}
              suffix="%"
              decimals={1}
              trend="up"
              trendLabel="vs full test suite"
              glow
            />
            <StatCard
              label="CI Time Saved"
              value={headline.timeSavedPct}
              suffix="%"
              decimals={1}
              trend="up"
              trendLabel="accelerated turnaround"
              glow
            />
            <StatCard
              label="Bugs Still Caught"
              value={headline.bugDetectionPct}
              suffix="%"
              decimals={1}
              trend="up"
              trendLabel="mutation test verification"
              glow
            />
          </>
        )}
      </section>

      {/* Footer Line */}
      <footer className="pt-8 border-t border-border/40 text-center text-xs text-text-dim">
        <p>
          {projectConfig.team} · {projectConfig.institution} · {projectConfig.semester}
        </p>
      </footer>
    </div>
  );
};
