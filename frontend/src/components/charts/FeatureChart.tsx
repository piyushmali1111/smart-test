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
import type { FeatureImportance } from '../../api/types';

interface FeatureChartProps {
  data: FeatureImportance[];
  height?: number;
}

export const FeatureChart: React.FC<FeatureChartProps> = ({ data, height = 280 }) => {
  const sorted = [...data]
    .sort((a, b) => a.importance - b.importance)
    .map(d => ({
      ...d,
      pct: Number((d.importance * 100).toFixed(1)),
    }));

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          layout="vertical"
          data={sorted}
          margin={{ top: 10, right: 20, bottom: 4, left: 40 }}
        >
          <defs>
            <linearGradient id="featureBarGrad" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0%" stopColor="#6C8CFF" />
              <stop offset="100%" stopColor="#22D3EE" />
            </linearGradient>
          </defs>

          <CartesianGrid stroke={chartColors.grid} strokeDasharray="3 3" horizontal={false} />

          <XAxis
            type="number"
            stroke="transparent"
            domain={[0, 45]}
            tick={{ fill: chartColors.textMuted, fontSize: 11, fontFamily: 'JetBrains Mono' }}
            tickFormatter={(v) => `${v}%`}
          />

          <YAxis
            type="category"
            dataKey="feature"
            stroke="transparent"
            tick={{ fill: chartColors.textMuted, fontSize: 11 }}
            width={120}
          />

          <Tooltip content={<CustomChartTooltip unit="%" />} />

          <Bar
            dataKey="pct"
            name="Importance"
            fill="url(#featureBarGrad)"
            radius={[0, 6, 6, 0]}
            animationDuration={700}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};
