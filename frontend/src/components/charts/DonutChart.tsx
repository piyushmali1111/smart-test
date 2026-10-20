import React from 'react';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip } from 'recharts';
import { CustomChartTooltip } from './theme';
import type { MutationTypeCount } from '../../api/types';

interface DonutChartProps {
  data: MutationTypeCount[];
  height?: number;
}

export const DonutChart: React.FC<DonutChartProps> = ({ data, height = 240 }) => {
  const colors = [
    '#6C8CFF',  // periwinkle
    '#22D3EE',  // cyan
    '#A5B4FC',  // lavender
    '#2DD4BF',  // teal
    '#64748B',  // slate
  ];

  return (
    <div style={{ width: '100%', height }}>
      <ResponsiveContainer width="100%" height="100%">
        <PieChart>
          <Tooltip content={<CustomChartTooltip unit=" mutants" />} />
          <Pie
            data={data}
            dataKey="count"
            nameKey="type"
            cx="50%"
            cy="50%"
            innerRadius={55}
            outerRadius={85}
            paddingAngle={4}
            animationDuration={700}
          >
            {data.map((_, index) => (
              <Cell key={`cell-${index}`} fill={colors[index % colors.length]} stroke="var(--bg-2)" strokeWidth={2} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
    </div>
  );
};
