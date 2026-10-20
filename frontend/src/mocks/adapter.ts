import graphData from './data/graph.json';
import testsData from './data/tests.json';
import resultsData from './data/results.json';
import modelsData from './data/models.json';
import replayData from './data/replay.json';
import { solveGreedy, solveDP, solveBranchAndBound, type KnapsackItem } from './algorithms';
import { createRng } from './seed';
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
  CandidateTest,
  AlgorithmCompareResult,
} from '../api/types';

/**
 * Tarjan's Strongly Connected Components algorithm
 */
function findSCC(nodes: string[], adj: Map<string, string[]>): string[][] {
  let index = 0;
  const indices = new Map<string, number>();
  const lowlinks = new Map<string, number>();
  const onStack = new Set<string>();
  const stack: string[] = [];
  const sccs: string[][] = [];

  function strongConnect(v: string) {
    indices.set(v, index);
    lowlinks.set(v, index);
    index++;
    stack.push(v);
    onStack.add(v);

    const neighbors = adj.get(v) || [];
    for (const w of neighbors) {
      if (!indices.has(w)) {
        strongConnect(w);
        lowlinks.set(v, Math.min(lowlinks.get(v)!, lowlinks.get(w)!));
      } else if (onStack.has(w)) {
        lowlinks.set(v, Math.min(lowlinks.get(v)!, indices.get(w)!));
      }
    }

    if (lowlinks.get(v) === indices.get(v)) {
      const scc: string[] = [];
      let w: string;
      do {
        w = stack.pop()!;
        onStack.delete(w);
        scc.push(w);
      } while (w !== v);

      if (scc.length > 1) {
        sccs.push(scc);
      }
    }
  }

  for (const node of nodes) {
    if (!indices.has(node)) {
      strongConnect(node);
    }
  }

  return sccs;
}

export async function mockGetGraph(): Promise<GraphResponse> {
  // Simulate tiny network tick
  await new Promise(r => setTimeout(r, 40));
  return graphData as GraphResponse;
}

export async function mockGetAffected(changed: string[]): Promise<AffectedResponse> {
  await new Promise(r => setTimeout(r, 40));

  const validChanged = changed.length > 0 ? changed : ['cart.calculate_total'];
  const nodes = graphData.nodes.map(n => n.id);
  const adj = new Map<string, string[]>();
  const revAdj = new Map<string, string[]>();

  for (const n of nodes) {
    adj.set(n, []);
    revAdj.set(n, []);
  }

  for (const edge of graphData.edges) {
    adj.get(edge.source)?.push(edge.target);
    revAdj.get(edge.target)?.push(edge.source);
  }

  // Find SCC groups (circular dependencies)
  const sccGroups = findSCC(nodes, adj);

  // BFS downstream & upstream to find affected code
  // In change impact analysis: if A uses B and B changed, A is affected. Also what changed calls is affected.
  const distances = new Map<string, number>();
  const queue: { id: string; dist: number }[] = [];

  for (const ch of validChanged) {
    distances.set(ch, 0);
    queue.push({ id: ch, dist: 0 });
  }

  while (queue.length > 0) {
    const { id, dist } = queue.shift()!;
    // Bidirectional reachability in call graphs
    const neighbors = [...(adj.get(id) || []), ...(revAdj.get(id) || [])];
    for (const neighbor of neighbors) {
      if (!distances.has(neighbor)) {
        distances.set(neighbor, dist + 1);
        queue.push({ id: neighbor, dist: dist + 1 });
      }
    }
  }

  const affected = Array.from(distances.entries()).map(([id, distance]) => ({
    id,
    distance,
  })).sort((a, b) => a.distance - b.distance);

  const affectedSet = new Set(distances.keys());

  // Deterministic seed based on changed nodes string
  let seedVal = 42;
  for (const ch of validChanged) {
    for (let i = 0; i < ch.length; i++) {
      seedVal = (seedVal * 31 + ch.charCodeAt(i)) >>> 0;
    }
  }
  const rng = createRng(seedVal);

  // Candidate tests are tests that cover at least one affected/changed function
  const candidateTests: CandidateTest[] = [];
  for (const test of testsData) {
    const coveredAffected = test.covers.filter(c => affectedSet.has(c));
    if (coveredAffected.length > 0) {
      // Find min distance among covered functions
      const minDistance = Math.min(
        ...coveredAffected.map(c => distances.get(c) ?? 99)
      );

      // Risk score: closer distance = higher risk, plus subtle deterministic variance
      let baseRisk = 0.92;
      if (minDistance === 1) baseRisk = 0.78;
      else if (minDistance === 2) baseRisk = 0.58;
      else if (minDistance >= 3) baseRisk = 0.38;

      const variance = (rng() - 0.5) * 0.12;
      const risk = Math.min(0.99, Math.max(0.15, Number((baseRisk + variance).toFixed(2))));

      candidateTests.push({
        id: test.id,
        name: test.name,
        timeSec: test.timeSec,
        risk,
        covers: test.covers,
      });
    }
  }

  // Sort by risk descending
  candidateTests.sort((a, b) => b.risk - a.risk);

  return {
    affected,
    candidateTests,
    sccGroups,
  };
}

export async function mockSelect(req: SelectRequest): Promise<SelectResponse> {
  const affectedRes = await mockGetAffected(req.changed);
  const items: KnapsackItem[] = affectedRes.candidateTests.map(t => ({
    id: t.id,
    weight: t.timeSec,
    value: t.risk,
  }));

  let result;
  if (req.algorithm === 'greedy') {
    result = solveGreedy(items, req.budgetSec);
  } else if (req.algorithm === 'bnb') {
    result = solveBranchAndBound(items, req.budgetSec);
  } else {
    result = solveDP(items, req.budgetSec);
  }

  // Compute coverage of affected functions
  const selectedTestIds = new Set(result.selectedIds);
  const coveredFunctions = new Set<string>();
  for (const t of affectedRes.candidateTests) {
    if (selectedTestIds.has(t.id)) {
      for (const fn of t.covers) {
        coveredFunctions.add(fn);
      }
    }
  }

  const affectedTotal = affectedRes.affected.length;
  const coveragePct = affectedTotal > 0
    ? Math.min(100, Number(((coveredFunctions.size / affectedTotal) * 100).toFixed(1)))
    : 100;

  return {
    selected: result.selectedIds,
    totalTimeSec: result.totalWeight,
    totalRisk: result.totalValue,
    coveragePct,
    algorithmRuntimeMs: result.runtimeMs,
  };
}

export async function mockCompare(req: CompareRequest): Promise<CompareResponse> {
  const affectedRes = await mockGetAffected(req.changed);
  const items: KnapsackItem[] = affectedRes.candidateTests.map(t => ({
    id: t.id,
    weight: t.timeSec,
    value: t.risk,
  }));

  const greedyRes = solveGreedy(items, req.budgetSec);
  const dpRes = solveDP(items, req.budgetSec);
  const bnbRes = solveBranchAndBound(items, req.budgetSec);

  const optimalValue = Math.max(dpRes.totalValue, bnbRes.totalValue);

  function getGap(val: number): number {
    if (optimalValue <= 0) return 0;
    return Math.max(0, Number((((optimalValue - val) / optimalValue) * 100).toFixed(1)));
  }

  const results: AlgorithmCompareResult[] = [
    {
      algorithm: 'greedy',
      totalRisk: greedyRes.totalValue,
      totalTimeSec: greedyRes.totalWeight,
      testsSelected: greedyRes.selectedIds.length,
      runtimeMs: greedyRes.runtimeMs,
      memoryKb: 48,
      optimalityGapPct: getGap(greedyRes.totalValue),
    },
    {
      algorithm: 'dp',
      totalRisk: dpRes.totalValue,
      totalTimeSec: dpRes.totalWeight,
      testsSelected: dpRes.selectedIds.length,
      runtimeMs: dpRes.runtimeMs,
      memoryKb: 320,
      optimalityGapPct: 0,
    },
    {
      algorithm: 'bnb',
      totalRisk: bnbRes.totalValue,
      totalTimeSec: bnbRes.totalWeight,
      testsSelected: bnbRes.selectedIds.length,
      runtimeMs: bnbRes.runtimeMs,
      memoryKb: 128,
      optimalityGapPct: 0,
    },
  ];

  const scalability = [
    { n: 10, greedyMs: 0.1, dpMs: 0.8, bnbMs: 0.4 },
    { n: 20, greedyMs: 0.2, dpMs: 1.9, bnbMs: 1.2 },
    { n: 30, greedyMs: 0.4, dpMs: 3.5, bnbMs: 3.8 },
    { n: 40, greedyMs: 0.5, dpMs: 5.2, bnbMs: 8.6 },
    { n: 50, greedyMs: 0.7, dpMs: 7.1, bnbMs: 18.2 },
    { n: 60, greedyMs: 0.9, dpMs: 9.4, bnbMs: 34.5 },
    { n: 75, greedyMs: 1.1, dpMs: 12.8, bnbMs: 68.4 },
  ];

  return {
    results,
    scalability,
  };
}

export async function mockGetResults(): Promise<ResultsResponse> {
  await new Promise(r => setTimeout(r, 40));
  return resultsData as ResultsResponse;
}

export async function mockGetModels(): Promise<ModelsResponse> {
  await new Promise(r => setTimeout(r, 40));
  return modelsData as ModelsResponse;
}

export async function mockReplay(req: ReplayRequest): Promise<ReplayResponse> {
  await new Promise(r => setTimeout(r, 40));
  const count = Math.min(req.numChanges, replayData.changes.length);
  const rawSlice = replayData.changes.slice(0, count);

  let cumulativeTestsRun = 0;
  let cumulativeCaught = 0;
  let cumulativeRunAll = 0;

  // Scale tests run slightly by budget
  const budgetScale = Math.min(1.2, Math.max(0.6, req.budgetSec / 30));

  const steps = rawSlice.map((item, idx) => {
    const testsRun = Math.max(1, Math.round(item.testsRun * budgetScale));
    cumulativeTestsRun += testsRun;
    if (item.caught) cumulativeCaught += 1;
    cumulativeRunAll += replayData.totalTests;

    return {
      step: idx + 1,
      changedId: item.changedId,
      testsRun,
      cumulativeTestsRun,
      caught: item.caught,
      cumulativeCaught,
      cumulativeRunAll,
    };
  });

  return {
    totalTests: replayData.totalTests,
    totalBugs: count,
    steps,
  };
}
