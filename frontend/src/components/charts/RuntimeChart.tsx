import React from 'react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { chartColors, CustomChartTooltip } from './theme';
import type { ScalabilityPoint } from '../../api/types';

interface RuntimeChartProps {
  data: ScalabilityPoint[];
  scaleMode?: 'linear' | 'log';
  height?: number;
}

export const RuntimeChart: React.FC<RuntimeChartProps> = ({
  data,
  scaleMode = 'linear',
  height = 280,
}) => {
  const chartData = data.map(d => ({
    n: d.n,
    Greedy: scaleMode === 'log' ? Math.max(0.01, d.greedyMs) : d.greedyMs,
    'Dynamic Prog': scaleMode === 'log' ? Math.max(0.01, d.dpMs) : d.dpMs,
    'Branch & Bound': scaleMode === 'log' ? Math.max(0.01, d.bnbMs) : d.bnbMs,
  }));

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 12, right: 16, bottom: 4, left: -10 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="n"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v} tests`}
          />

          <YAxis
            scale={scaleMode === 'log' ? 'log' : 'auto'}
            domain={scaleMode === 'log' ? [0.05, 100] : [0, 'auto']}
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v}ms`}
          />

          <Tooltip content={<CustomChartTooltip unit="ms" />} />

          {/* Greedy (lavender) */}
          <Line
            type="monotone"
            dataKey="Greedy"
            stroke={chartColors.lavender}
            strokeWidth={2}
            dot={{ r: 3 }}
            animationDuration={700}
          />

          {/* DP (accent / cyan) */}
          <Line
            type="monotone"
            dataKey="Dynamic Prog"
            stroke={chartColors.accent}
            strokeWidth={2.5}
            dot={{ r: 3 }}
            animationDuration={700}
          />

          {/* Branch & Bound (brand / periwinkle, rising steeply) */}
          <Line
            type="monotone"
            dataKey="Branch & Bound"
            stroke={chartColors.brand}
            strokeWidth={3}
            dot={{ r: 4, fill: chartColors.brand }}
            animationDuration={700}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
