import React from 'react';
import {
  ResponsiveContainer,
  ComposedChart,
  Area,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { chartColors, CustomChartTooltip } from './theme';
import type { DetectionPoint } from '../../api/types';

interface DetectionChartProps {
  data: DetectionPoint[];
  height?: number;
}

export const DetectionChart: React.FC<DetectionChartProps> = ({ data, height = 320 }) => {
  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 12, right: 16, bottom: 4, left: -10 }}>
          <defs>
            <linearGradient id="oursAreaGrad" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#22D3EE" stopOpacity={0.28} />
              <stop offset="100%" stopColor="#22D3EE" stopOpacity={0.0} />
            </linearGradient>
          </defs>

          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="budgetSec"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 12, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v}s`}
          />

          <YAxis
            domain={[0, 100]}
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 12, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v}%`}
          />

          <Tooltip content={<CustomChartTooltip unit="%" />} />

          {/* Run All baseline (near-white, thin) */}
          <Line
            type="monotone"
            dataKey="runAll"
            name="Run All"
            stroke={chartColors.runAll}
            strokeWidth={1.5}
            dot={false}
            animationDuration={700}
          />

          {/* Random baseline (slate, dashed) */}
          <Line
            type="monotone"
            dataKey="random"
            name="Random"
            stroke={chartColors.slate}
            strokeWidth={2}
            strokeDasharray="4 4"
            dot={false}
            animationDuration={700}
          />

          {/* Dependency-only (amber) */}
          <Line
            type="monotone"
            dataKey="dependencyOnly"
            name="Dependency-Only"
            stroke={chartColors.warn}
            strokeWidth={2}
            dot={false}
            animationDuration={700}
          />

          {/* Ours (hero series: cyan, area fill, thick) */}
          <Area
            type="monotone"
            dataKey="ours"
            name="Ours (ML + Knapsack)"
            stroke={chartColors.accent}
            strokeWidth={3}
            fill="url(#oursAreaGrad)"
            dot={{ r: 3, fill: chartColors.accent, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: '#FFFFFF', stroke: chartColors.accent, strokeWidth: 2 }}
            animationDuration={700}
          />
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
};
