import React, { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Badge } from '../components/ui/Badge';
import { Button } from '../components/ui/Button';
import { StatCard } from '../components/ui/StatCard';
import { Slider } from '../components/ui/Slider';
import { SegmentedControl } from '../components/ui/SegmentedControl';
import { Tabs } from '../components/ui/Tabs';
import { RiskBar } from '../components/ui/RiskBar';
import { ProgressRing } from '../components/ui/ProgressRing';
import { Tooltip } from '../components/ui/Tooltip';
import { DotsMenu } from '../components/ui/DotsMenu';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { ErrorState } from '../components/ui/ErrorState';
import { Legend } from '../components/ui/Legend';
import { Insight } from '../components/ui/Insight';
import { Toast } from '../components/ui/Toast';
import { Download } from 'lucide-react';

export const Styleguide: React.FC = () => {
  const [sliderVal, setSliderVal] = useState(30);
  const [segmentVal, setSegmentVal] = useState<'greedy' | 'dp' | 'bnb'>('dp');
  const [activeTab, setActiveTab] = useState('tab1');
  const [showToast, setShowToast] = useState(false);

  return (
    <div className="space-y-8 pb-12">
      <div className="border-b border-border pb-4">
        <h2 className="font-heading text-2xl font-bold text-gradient">Midnight Indigo Style Guide</h2>
        <p className="text-xs text-text-muted mt-1">Verification of deep navy, periwinkle, and cyan design tokens</p>
      </div>

      {/* Badges & Buttons */}
      <Card title="Badges & Buttons">
        <div className="space-y-4">
          <div className="flex flex-wrap items-center gap-3">
            <Badge variant="brand">Brand (Periwinkle)</Badge>
            <Badge variant="accent">Accent (Cyan)</Badge>
            <Badge variant="success">Success (Emerald)</Badge>
            <Badge variant="amber">Amber (Warning)</Badge>
            <Badge variant="red">Danger (Red)</Badge>
            <Badge variant="grey">Grey (Slate)</Badge>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button variant="primary" size="md">Primary Button</Button>
            <Button variant="ghost" size="md">Ghost Button</Button>
            <Button variant="primary" size="sm">Small</Button>
            <Button variant="primary" size="lg">Large</Button>
            <Button variant="primary" loading>Loading</Button>
            <Button variant="icon" size="md" title="Icon Button"><Download className="h-4 w-4" /></Button>
          </div>
        </div>
      </Card>

      {/* StatCards & ProgressRing */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <StatCard label="Test Reduction" value={68.4} suffix="%" decimals={1} glow />
        <StatCard label="Time Saved" value={74.2} suffix="%" decimals={1} glow />
        <Card className="flex items-center justify-between p-5">
          <div>
            <span className="text-xs uppercase font-semibold text-text-muted">Progress Ring</span>
            <p className="text-xl font-bold mt-1 text-text-main">30s / 60s</p>
          </div>
          <ProgressRing value={30} max={60} size={70} strokeWidth={7} unit="s" />
        </Card>
      </div>

      {/* Controls: Slider, SegmentedControl, Tabs */}
      <Card title="Interactive Controls">
        <div className="space-y-6">
          <Slider
            min={5}
            max={100}
            value={sliderVal}
            onChange={setSliderVal}
            label="Execution Slider"
          />

          <div className="flex flex-col sm:flex-row items-center gap-6">
            <SegmentedControl
              value={segmentVal}
              onChange={setSegmentVal}
              options={[
                { value: 'greedy', label: 'Greedy' },
                { value: 'dp', label: 'DP 0/1' },
                { value: 'bnb', label: 'Branch & Bound' },
              ]}
            />

            <Tabs
              activeTab={activeTab}
              onChange={setActiveTab}
              tabs={[
                { id: 'tab1', label: 'Tab Alpha', count: 3 },
                { id: 'tab2', label: 'Tab Beta', count: 12 },
              ]}
            />
          </div>
        </div>
      </Card>

      {/* RiskBar, Tooltip, DotsMenu, Legend, Insight */}
      <Card title="Visual Details & Feedback">
        <div className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <span className="text-xs text-text-muted mb-1 block">Risk Bar (0.85)</span>
              <RiskBar value={0.85} />
            </div>
            <div>
              <span className="text-xs text-text-muted mb-1 block">Risk Bar (0.35)</span>
              <RiskBar value={0.35} />
            </div>
          </div>

          <div className="flex items-center gap-6 pt-2">
            <Tooltip content="Dark glass tooltip in Midnight Indigo">
              <span className="text-xs text-accent underline cursor-pointer">Hover for Tooltip</span>
            </Tooltip>
            <div className="flex items-center gap-2">
              <span className="text-xs text-text-muted">Dots Menu:</span>
              <DotsMenu />
            </div>
            <Button variant="ghost" size="sm" onClick={() => setShowToast(true)}>Trigger Toast</Button>
          </div>

          <Legend
            items={[
              { label: 'Primary (Cyan)', color: 'var(--accent)' },
              { label: 'Brand (Periwinkle)', color: 'var(--brand)' },
              { label: 'Warning (Affected)', color: 'var(--warn)' },
              { label: 'Baseline', color: 'var(--slate)', dashed: true },
            ]}
          />

          <Insight>Dynamic single-line computed insight with cyan border.</Insight>
        </div>
      </Card>

      {/* States: Skeleton, ErrorState, EmptyState */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card title="Skeleton Loading State">
          <div className="space-y-3">
            <Skeleton className="h-6 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-5/6" />
          </div>
        </Card>

        <Card title="Empty & Error States">
          <div className="space-y-4">
            <ErrorState message="API connection timeout on localhost:8000" onRetry={() => {}} />
            <EmptyState message="No tests selected for this change" actionLabel="Pick Change" onAction={() => {}} />
          </div>
        </Card>
      </div>

      {showToast && (
        <Toast
          message="Midnight Indigo toast notification test"
          type="success"
          onClose={() => setShowToast(false)}
        />
      )}
    </div>
  );
};
