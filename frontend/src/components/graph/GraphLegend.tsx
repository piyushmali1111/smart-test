import React from 'react';
import { Legend } from '../ui/Legend';

export const GraphLegend: React.FC = () => {
  return (
    <Legend
      items={[
        { label: 'Changed', color: 'var(--danger)' },
        { label: 'Affected (Impact)', color: 'var(--warn)' },
        { label: 'Unaffected', color: 'var(--slate)' },
        { label: 'SCC Cycle', color: 'var(--lavender)', dashed: true },
      ]}
    />
  );
};
