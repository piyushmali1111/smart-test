import axios from 'axios';
import type {
  GraphResponse,
  AffectedResponse,
  SelectRequest,
  SelectResponse,
  CompareRequest,
  CompareResponse,
  ResultsResponse,
  ModelsResponse,
  ReplayRequest,
  ReplayResponse,
} from './types';
import * as mockAdapter from '../mocks/adapter';

export const isMockMode = import.meta.env.VITE_USE_MOCK !== 'false';
export const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export async function fetchGraph(): Promise<GraphResponse> {
  if (isMockMode) {
    return mockAdapter.mockGetGraph();
  }
  const { data } = await api.get<GraphResponse>('/api/graph');
  return data;
}

export async function fetchAffected(changed: string[]): Promise<AffectedResponse> {
  if (isMockMode) {
    return mockAdapter.mockGetAffected(changed);
  }
  const { data } = await api.post<AffectedResponse>('/api/affected', { changed });
  return data;
}

export async function fetchSelect(req: SelectRequest): Promise<SelectResponse> {
  if (isMockMode) {
    return mockAdapter.mockSelect(req);
  }
  const { data } = await api.post<SelectResponse>('/api/select', req);
  return data;
}

export async function fetchCompare(req: CompareRequest): Promise<CompareResponse> {
  if (isMockMode) {
    return mockAdapter.mockCompare(req);
  }
  const { data } = await api.post<CompareResponse>('/api/compare', req);
  return data;
}

export async function fetchResults(): Promise<ResultsResponse> {
  if (isMockMode) {
    return mockAdapter.mockGetResults();
  }
  const { data } = await api.get<ResultsResponse>('/api/results');
  return data;
}

export async function fetchModels(): Promise<ModelsResponse> {
  if (isMockMode) {
    return mockAdapter.mockGetModels();
  }
  const { data } = await api.get<ModelsResponse>('/api/models');
  return data;
}

export async function fetchReplay(req: ReplayRequest): Promise<ReplayResponse> {
  if (isMockMode) {
    return mockAdapter.mockReplay(req);
  }
  const { data } = await api.post<ReplayResponse>('/api/replay', req);
  return data;
}

export async function checkBackendHealth(): Promise<boolean> {
  if (isMockMode) {
    return true;
  }
  try {
    await api.get('/health', { timeout: 2500 });
    return true;
  } catch {
    return false;
  }
}
