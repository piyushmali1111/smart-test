import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts';
import { chartColors, CustomChartTooltip } from './theme';
import type { StrategyResult } from '../../api/types';

interface TimeSavedChartProps {
  data: StrategyResult[];
  height?: number;
}

export const TimeSavedChart: React.FC<TimeSavedChartProps> = ({ data, height = 260 }) => {
  const formatted = data.map((d) => ({
    ...d,
    timeSavedSec: Math.max(0, 155.0 - d.timeSec),
  }));

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={formatted} margin={{ top: 10, right: 10, bottom: 4, left: -10 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="name"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11 }}
            tickFormatter={(v) => v.split(' ')[0]}
          />

          <YAxis
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v}s`}
          />

          <Tooltip content={<CustomChartTooltip unit="s" />} />

          <Bar
            dataKey="timeSec"
            name="Execution Time"
            radius={[6, 6, 0, 0]}
            fill={chartColors.warn}
            animationDuration={700}
          />

          <Bar
            dataKey="timeSavedSec"
            name="Time Saved"
            radius={[6, 6, 0, 0]}
            fill={chartColors.accent}
            animationDuration={700}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
