import React, { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { isMockMode, checkBackendHealth } from '../../api/client';
import { Badge } from '../ui/Badge';
import { DotsMenu } from '../ui/DotsMenu';
import { Tooltip } from '../ui/Tooltip';
import { Database, Server } from 'lucide-react';

interface TopBarProps {
  collapsed?: boolean;
}

export const TopBar: React.FC<TopBarProps> = ({ collapsed = false }) => {
  const location = useLocation();
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null);

  useEffect(() => {
    let mounted = true;
    checkBackendHealth().then((isHealthy) => {
      if (mounted) setBackendOnline(isHealthy);
    });
    return () => {
      mounted = false;
    };
  }, []);

  const routeTitles: Record<string, { title: string; breadcrumb: string }> = {
    '/': { title: 'Overview', breadcrumb: 'Dashboard' },
    '/analysis': { title: 'Change Analysis', breadcrumb: 'Code Impact Graph' },
    '/selection': { title: 'Test Selection', breadcrumb: 'Knapsack Optimization' },
    '/compare': { title: 'Algorithm Comparison', breadcrumb: 'DAA Complexity' },
    '/results': { title: 'Results & Experiments', breadcrumb: 'Empirical Verification' },
    '/replay': { title: 'Live Replay', breadcrumb: 'Simulation' },
    '/styleguide': { title: 'Design System', breadcrumb: 'Style Guide' },
  };

  const current = routeTitles[location.pathname] || {
    title: 'Smart Test Selection',
    breadcrumb: 'System',
  };

  return (
    <header
      className="sticky top-0 z-30 flex h-16 w-full items-center justify-between border-b border-border bg-bg-1/90 px-6 backdrop-blur-md"
      style={{ marginLeft: collapsed ? '72px' : '240px', width: `calc(100% - ${collapsed ? '72px' : '240px'})` }}
    >
      {/* Left: Breadcrumb + Title */}
      <div>
        <span className="block text-[11px] font-semibold uppercase tracking-wider text-text-dim">
          {current.breadcrumb}
        </span>
        <h1 className="font-heading text-xl font-bold tracking-tight text-text-main">
          {current.title}
        </h1>
      </div>

      {/* Center: Signature three-dot motif in cyan */}
      <div className="hidden md:flex items-center">
        <DotsMenu decorativeOnly />
      </div>

      {/* Right: Mode & Backend status indicators */}
      <div className="flex items-center gap-3">
        {isMockMode ? (
          <Badge variant="amber" icon={<Database className="h-3 w-3" />}>
            Sample data
          </Badge>
        ) : (
          <Badge variant="brand" icon={<Server className="h-3 w-3" />}>
            FastAPI Live
          </Badge>
        )}

        {/* Backend health status dot */}
        <Tooltip
          content={
            isMockMode
              ? 'Running locally with deterministic mock engine'
              : backendOnline
              ? 'Connected to FastAPI backend (localhost:8000)'
              : 'Cannot connect to FastAPI backend'
          }
          position="bottom"
        >
          <div className="flex items-center gap-1.5 rounded-full border border-border bg-bg-3 px-2 py-1">
            <span
              className={`h-2 w-2 rounded-full ${
                isMockMode
                  ? 'bg-warn'
                  : backendOnline
                  ? 'bg-success animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.4)]'
                  : 'bg-danger'
              }`}
            />
            <span className="text-[11px] font-mono text-text-muted">
              {isMockMode ? 'Mock' : backendOnline ? 'Live' : 'Offline'}
            </span>
          </div>
        </Tooltip>
      </div>
    </header>
  );
};
