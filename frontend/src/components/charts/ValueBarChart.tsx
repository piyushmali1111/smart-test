import React from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from 'recharts';
import { chartColors, CustomChartTooltip } from './theme';
import type { AlgorithmCompareResult } from '../../api/types';

interface ValueBarChartProps {
  data: AlgorithmCompareResult[];
  height?: number;
}

export const ValueBarChart: React.FC<ValueBarChartProps> = ({ data, height = 280 }) => {
  const chartData = data.map((d) => ({
    name:
      d.algorithm === 'greedy'
        ? 'Greedy'
        : d.algorithm === 'dp'
        ? 'DP Knapsack'
        : 'Branch & Bound',
    algorithm: d.algorithm,
    riskValue: d.totalRisk,
    isOptimal: d.optimalityGapPct === 0,
  }));

  const getBarColor = (algorithm: string) => {
    switch (algorithm) {
      case 'greedy':
        return chartColors.lavender;
      case 'dp':
        return chartColors.accent;
      case 'bnb':
        return chartColors.brand;
      default:
        return chartColors.accent;
    }
  };

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 12, right: 16, bottom: 4, left: -10 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="name"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11 }}
          />

          <YAxis
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
          />

          <Tooltip content={<CustomChartTooltip unit=" risk" />} />

          <Bar dataKey="riskValue" name="Total Risk Score" radius={[6, 6, 0, 0]} animationDuration={700}>
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={getBarColor(entry.algorithm)}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
