import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  GitBranch,
  ListChecks,
  Scale,
  BarChart3,
  Play,
  ShieldCheck,
} from 'lucide-react';
import { ScenarioChip } from './ScenarioChip';
import { Tooltip } from '../ui/Tooltip';
import { cn } from '../../utils/cn';

interface SidebarProps {
  collapsed?: boolean;
}

export const Sidebar: React.FC<SidebarProps> = ({ collapsed = false }) => {
  const navItems = [
    { to: '/', label: 'Overview', icon: LayoutDashboard },
    { to: '/analysis', label: 'Change Analysis', icon: GitBranch },
    { to: '/selection', label: 'Test Selection', icon: ListChecks },
    { to: '/compare', label: 'Compare', icon: Scale },
    { to: '/results', label: 'Results', icon: BarChart3 },
    { to: '/replay', label: 'Live Replay', icon: Play },
  ];

  return (
    <aside
      className={cn(
        'fixed top-0 bottom-0 left-0 z-40 flex flex-col justify-between border-r border-border bg-bg-1 p-3 transition-all duration-300',
        collapsed ? 'w-[72px]' : 'w-[240px]'
      )}
    >
      <div>
        {/* Logo header */}
        <div className="flex h-14 items-center gap-3 px-2 mb-4">
          <div className="flex h-9 w-9 items-center justify-center rounded-panel border border-brand/40 bg-brand/10 text-brand shadow-glow-sm">
            <ShieldCheck className="h-5 w-5" />
          </div>
          {!collapsed && (
            <div className="flex flex-col">
              <span className="font-heading text-lg font-bold tracking-tight text-text-main">
                Smart<span className="text-accent">Test</span>
              </span>
              <span className="text-[10px] uppercase font-semibold text-text-dim tracking-wider">
                DAA Engine
              </span>
            </div>
          )}
        </div>

        {/* Navigation links */}
        <nav className="space-y-1.5" aria-label="Main Navigation">
          {navItems.map((item) => {
            const Icon = item.icon;
            const linkContent = (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'group relative flex h-11 items-center rounded-pill px-3 font-medium text-sm transition-all duration-150',
                    isActive
                      ? 'bg-[rgba(108,140,255,0.12)] text-brand-200 shadow-glow-sm'
                      : 'text-text-muted hover:bg-bg-4 hover:text-text-main',
                    collapsed ? 'justify-center' : 'justify-start gap-3'
                  )
                }
              >
                {({ isActive }) => (
                  <>
                    {/* Active left indicator bar */}
                    {isActive && (
                      <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r-full bg-brand shadow-glow-sm" />
                    )}
                    <Icon className="h-4 w-4 flex-shrink-0" />
                    {!collapsed && <span className="truncate">{item.label}</span>}
                  </>
                )}
              </NavLink>
            );

            if (collapsed) {
              return (
                <Tooltip key={item.to} content={item.label} position="right">
                  {linkContent}
                </Tooltip>
              );
            }

            return linkContent;
          })}
        </nav>
      </div>

      {/* Bottom scenario context chip */}
      <div className="pt-4 border-t border-border/50">
        <ScenarioChip collapsed={collapsed} />
      </div>
    </aside>
  );
};
