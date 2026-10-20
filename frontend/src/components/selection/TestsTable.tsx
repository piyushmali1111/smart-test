import React, { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Badge } from '../ui/Badge';
import { RiskBar } from '../ui/RiskBar';
import { Check, Search, ArrowUpDown } from 'lucide-react';
import type { CandidateTest } from '../../api/types';
import { cn } from '../../utils/cn';

interface TestsTableProps {
  tests: CandidateTest[];
  selectedIds: string[];
  budgetSec: number;
}

type SortField = 'name' | 'timeSec' | 'risk' | 'covers';
type SortOrder = 'asc' | 'desc';

export const TestsTable: React.FC<TestsTableProps> = ({
  tests,
  selectedIds,
  budgetSec,
}) => {
  const [search, setSearch] = useState('');
  const [selectedOnly, setSelectedOnly] = useState(false);
  const [sortField, setSortField] = useState<SortField>('risk');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');

  const selectedSet = useMemo(() => new Set(selectedIds), [selectedIds]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder(field === 'name' ? 'asc' : 'desc');
    }
  };

  const filteredTests = useMemo(() => {
    return tests
      .filter((t) => {
        if (selectedOnly && !selectedSet.has(t.id)) return false;
        if (!search.trim()) return true;
        const q = search.toLowerCase();
        return (
          t.name.toLowerCase().includes(q) ||
          t.covers.some((c) => c.toLowerCase().includes(q))
        );
      })
      .sort((a, b) => {
        let valA: any = a[sortField];
        let valB: any = b[sortField];
        if (sortField === 'covers') {
          valA = a.covers.length;
          valB = b.covers.length;
        }
        if (valA < valB) return sortOrder === 'asc' ? -1 : 1;
        if (valA > valB) return sortOrder === 'asc' ? 1 : -1;
        return 0;
      });
  }, [tests, selectedOnly, search, selectedSet, sortField, sortOrder]);

  return (
    <div className="w-full space-y-4">
      {/* Table controls */}
      <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-text-dim" />
          <input
            type="text"
            placeholder="Search candidate tests..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full rounded-panel border border-border bg-bg-3 pl-9 pr-3 py-1.5 text-xs text-text-main placeholder:text-text-dim focus:border-brand focus:outline-none transition-colors"
          />
        </div>

        <div className="flex items-center gap-3 w-full sm:w-auto justify-end">
          <label className="flex items-center gap-2 text-xs text-text-muted cursor-pointer select-none">
            <input
              type="checkbox"
              checked={selectedOnly}
              onChange={(e) => setSelectedOnly(e.target.checked)}
              className="rounded border-border bg-bg-4 text-accent focus:ring-brand"
            />
            <span>Selected only ({selectedIds.length})</span>
          </label>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-panel border border-border bg-bg-2">
        <table className="w-full text-left border-collapse text-xs">
          <thead>
            <tr className="border-b border-border bg-bg-3/60 text-text-muted select-none">
              <th className="py-2.5 px-3 w-10"></th>
              <th
                onClick={() => handleSort('name')}
                className="py-2.5 px-3 font-semibold cursor-pointer hover:text-accent transition-colors"
              >
                <div className="flex items-center gap-1.5">
                  <span>Test Case</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                onClick={() => handleSort('timeSec')}
                className="py-2.5 px-3 font-semibold cursor-pointer hover:text-accent transition-colors w-24"
              >
                <div className="flex items-center gap-1.5">
                  <span>Time</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                onClick={() => handleSort('risk')}
                className="py-2.5 px-3 font-semibold cursor-pointer hover:text-accent transition-colors w-40"
              >
                <div className="flex items-center gap-1.5">
                  <span>Risk Score</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th
                onClick={() => handleSort('covers')}
                className="py-2.5 px-3 font-semibold cursor-pointer hover:text-accent transition-colors w-20 text-center"
              >
                <div className="flex items-center justify-center gap-1.5">
                  <span>Covers</span>
                  <ArrowUpDown className="h-3 w-3" />
                </div>
              </th>
              <th className="py-2.5 px-3 font-semibold w-28 text-right">Status</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border/50">
            <AnimatePresence>
              {filteredTests.map((test) => {
                const isSelected = selectedSet.has(test.id);
                const isTooSlow = !isSelected && test.timeSec > budgetSec;
                const simpleName = test.name.replace(/^tests\//, '');

                return (
                  <motion.tr
                    key={test.id}
                    layout
                    initial={{ opacity: 0 }}
                    animate={{ opacity: isSelected ? 1 : 0.45 }}
                    exit={{ opacity: 0 }}
                    transition={{ duration: 0.15 }}
                    className={cn(
                      'group transition-colors relative',
                      isSelected
                        ? 'bg-[rgba(34,211,238,0.06)] hover:bg-[rgba(34,211,238,0.1)] border-l-[3px] border-l-accent'
                        : 'hover:bg-bg-3/50 hover:opacity-80'
                    )}
                  >
                    {/* Active left indicator */}
                    <td className="py-2.5 px-3">
                      {isSelected ? (
                        <div className="flex h-5 w-5 items-center justify-center rounded-full bg-accent/20 text-accent">
                          <Check className="h-3 w-3" />
                        </div>
                      ) : (
                        <div className="h-5 w-5 rounded-full border border-border/40" />
                      )}
                    </td>

                    {/* Test Name */}
                    <td className="py-2.5 px-3 font-mono">
                      <span className={cn('font-medium truncate block max-w-md', isSelected ? 'text-text-main font-semibold' : 'text-text-muted')}>
                        {simpleName}
                      </span>
                    </td>

                    {/* Time */}
                    <td className="py-2.5 px-3 font-mono text-text-main font-semibold">
                      {test.timeSec.toFixed(1)} s
                    </td>

                    {/* Risk bar */}
                    <td className="py-2.5 px-3">
                      <RiskBar value={test.risk} />
                    </td>

                    {/* Covers chip */}
                    <td className="py-2.5 px-3 text-center">
                      <span className="inline-block rounded-full bg-bg-4 px-2 py-0.5 font-mono text-[11px] text-text-muted border border-border/40">
                        {test.covers.length}
                      </span>
                    </td>

                    {/* Status badge */}
                    <td className="py-2.5 px-3 text-right">
                      {isSelected ? (
                        <Badge variant="accent">Selected</Badge>
                      ) : isTooSlow ? (
                        <Badge variant="amber">Too slow</Badge>
                      ) : (
                        <Badge variant="grey">Skipped</Badge>
                      )}
                    </td>
                  </motion.tr>
                );
              })}
            </AnimatePresence>
          </tbody>
        </table>
      </div>
    </div>
  );
};
