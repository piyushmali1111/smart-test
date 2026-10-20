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

interface CumulativePoint {
  step: number;
  ours: number;
  runAll: number;
}

interface CumulativeReplayChartProps {
  data: CumulativePoint[];
  height?: number;
}

export const CumulativeReplayChart: React.FC<CumulativeReplayChartProps> = ({
  data,
  height = 240,
}) => {
  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 10, right: 16, bottom: 4, left: -5 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="step"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `#${v}`}
          />

          <YAxis
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
          />

          <Tooltip content={<CustomChartTooltip unit=" tests" />} />

          {/* Run All (slate) */}
          <Line
            type="monotone"
            dataKey="runAll"
            name="Run-All Suite"
            stroke={chartColors.slate}
            strokeWidth={2}
            strokeDasharray="3 3"
            dot={false}
            isAnimationActive={false}
          />

          {/* Ours (cyan accent) */}
          <Line
            type="monotone"
            dataKey="ours"
            name="Smart Test Selection"
            stroke={chartColors.accent}
            strokeWidth={3}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};
