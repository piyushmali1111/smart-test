import { useQuery } from '@tanstack/react-query';
import {
  fetchGraph,
  fetchAffected,
  fetchSelect,
  fetchCompare,
  fetchResults,
  fetchModels,
  fetchReplay,
} from '../api/client';
import type { AlgorithmType, ReplayRequest } from '../api/types';

export function useGraphQuery() {
  return useQuery({
    queryKey: ['graph'],
    queryFn: fetchGraph,
    staleTime: Infinity,
  });
}

export function useAffectedQuery(changed: string[]) {
  return useQuery({
    queryKey: ['affected', changed.slice().sort().join(',')],
    queryFn: () => fetchAffected(changed),
    staleTime: 60000,
  });
}

export function useSelectQuery(params: {
  changed: string[];
  budgetSec: number;
  algorithm: AlgorithmType;
}) {
  return useQuery({
    queryKey: ['select', params.changed.slice().sort().join(','), params.budgetSec, params.algorithm],
    queryFn: () => fetchSelect(params),
    staleTime: 30000,
  });
}

export function useCompareQuery(params: {
  changed: string[];
  budgetSec: number;
}) {
  return useQuery({
    queryKey: ['compare', params.changed.slice().sort().join(','), params.budgetSec],
    queryFn: () => fetchCompare(params),
    staleTime: 30000,
  });
}

export function useResultsQuery() {
  return useQuery({
    queryKey: ['results'],
    queryFn: fetchResults,
    staleTime: Infinity,
  });
}

export function useModelsQuery() {
  return useQuery({
    queryKey: ['models'],
    queryFn: fetchModels,
    staleTime: Infinity,
  });
}

export function useReplayQuery(params: ReplayRequest, enabled = true) {
  return useQuery({
    queryKey: ['replay', params.budgetSec, params.numChanges],
    queryFn: () => fetchReplay(params),
    enabled,
    staleTime: 60000,
  });
}
