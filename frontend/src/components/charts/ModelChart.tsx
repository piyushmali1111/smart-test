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
import type { ModelMetric } from '../../api/types';

interface ModelChartProps {
  data: ModelMetric[];
  height?: number;
}

export const ModelChart: React.FC<ModelChartProps> = ({ data, height = 280 }) => {
  const metrics = [
    {
      metric: 'Accuracy',
      ...Object.fromEntries(data.map(m => [m.name, m.accuracy * 100])),
    },
    {
      metric: 'Precision',
      ...Object.fromEntries(data.map(m => [m.name, m.precision * 100])),
    },
    {
      metric: 'Recall',
      ...Object.fromEntries(data.map(m => [m.name, m.recall * 100])),
    },
    {
      metric: 'F1 Score',
      ...Object.fromEntries(data.map(m => [m.name, m.f1 * 100])),
    },
  ];

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={metrics} margin={{ top: 10, right: 10, bottom: 4, left: -10 }}>
          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" vertical={false} />

          <XAxis
            dataKey="metric"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 12 }}
          />

          <YAxis
            domain={[60, 100]}
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v}%`}
          />

          <Tooltip content={<CustomChartTooltip unit="%" />} />

          <Bar
            dataKey="Random Forest"
            name="Random Forest"
            fill={chartColors.brand}
            radius={[6, 6, 0, 0]}
            animationDuration={700}
          />

          <Bar
            dataKey="Gradient Boosting"
            name="Gradient Boosting"
            fill={chartColors.accent}
            radius={[6, 6, 0, 0]}
            animationDuration={700}
          />

          <Bar
            dataKey="Logistic Regression"
            name="Logistic Regression"
            fill={chartColors.lavender}
            radius={[6, 6, 0, 0]}
            animationDuration={700}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
