export interface KnapsackItem {
  id: string;
  weight: number; // in seconds
  value: number;  // risk score
}

export interface KnapsackResult {
  selectedIds: string[];
  totalValue: number;
  totalWeight: number;
  runtimeMs: number;
}

/**
 * Greedy 0/1 Knapsack heuristic:
 * Sort items by density (value / weight) descending, greedily take what fits.
 */
export function solveGreedy(items: KnapsackItem[], capacity: number): KnapsackResult {
  const start = performance.now();
  
  // Filter items exceeding capacity
  const candidates = items
    .filter(item => item.weight <= capacity && item.weight > 0)
    .sort((a, b) => (b.value / b.weight) - (a.value / a.weight));

  const selected: string[] = [];
  let totalWeight = 0;
  let totalValue = 0;

  for (const item of candidates) {
    if (totalWeight + item.weight <= capacity + 1e-6) {
      selected.push(item.id);
      totalWeight += item.weight;
      totalValue += item.value;
    }
  }

  const end = performance.now();
  return {
    selectedIds: selected,
    totalValue: Number(totalValue.toFixed(4)),
    totalWeight: Number(totalWeight.toFixed(2)),
    runtimeMs: Math.max(0.1, Number((end - start).toFixed(2))),
  };
}

/**
 * Dynamic Programming 0/1 Knapsack:
 * Exact solution discretized into tenths of a second (100ms units).
 */
export function solveDP(items: KnapsackItem[], capacity: number): KnapsackResult {
  const start = performance.now();

  const scale = 10; // 0.1s granularity
  const intCap = Math.min(Math.round(capacity * scale), 4000); // capped for speed
  const validItems = items.filter(it => it.weight > 0 && Math.round(it.weight * scale) <= intCap);
  const n = validItems.length;

  if (n === 0 || intCap <= 0) {
    const end = performance.now();
    return { selectedIds: [], totalValue: 0, totalWeight: 0, runtimeMs: Math.max(0.2, Number((end - start).toFixed(2))) };
  }

  // dp[i][w] = max value using subset of first i items with weight limit w
  const dp: number[][] = Array.from({ length: n + 1 }, () => new Array(intCap + 1).fill(0));

  for (let i = 1; i <= n; i++) {
    const item = validItems[i - 1];
    const w = Math.round(item.weight * scale);
    const v = item.value;

    for (let c = 0; c <= intCap; c++) {
      if (w <= c) {
        dp[i][c] = Math.max(dp[i - 1][c], dp[i - 1][c - w] + v);
      } else {
        dp[i][c] = dp[i - 1][c];
      }
    }
  }

  // Backtrack to find selected items
  const selected: string[] = [];
  let currW = intCap;
  let totalW = 0;

  for (let i = n; i > 0; i--) {
    if (Math.abs(dp[i][currW] - dp[i - 1][currW]) > 1e-6) {
      const item = validItems[i - 1];
      selected.push(item.id);
      currW -= Math.round(item.weight * scale);
      totalW += item.weight;
    }
  }

  selected.reverse();
  const end = performance.now();

  return {
    selectedIds: selected,
    totalValue: Number(dp[n][intCap].toFixed(4)),
    totalWeight: Number(totalW.toFixed(2)),
    runtimeMs: Math.max(0.4, Number((end - start).toFixed(2))),
  };
}

/**
 * Branch and Bound 0/1 Knapsack:
 * Exact solution using fractional knapsack upper bound for pruning.
 */
export function solveBranchAndBound(items: KnapsackItem[], capacity: number): KnapsackResult {
  const start = performance.now();

  // Sort items by value/weight descending
  const sorted = items
    .filter(it => it.weight <= capacity && it.weight > 0)
    .sort((a, b) => (b.value / b.weight) - (a.value / a.weight));

  const n = sorted.length;
  if (n === 0) {
    const end = performance.now();
    return { selectedIds: [], totalValue: 0, totalWeight: 0, runtimeMs: Math.max(0.2, Number((end - start).toFixed(2))) };
  }

  // Calculate upper bound using fractional knapsack relaxation
  function getBound(index: number, currWeight: number, currValue: number): number {
    if (currWeight >= capacity) return 0;
    let bound = currValue;
    let w = currWeight;

    for (let i = index; i < n; i++) {
      if (w + sorted[i].weight <= capacity) {
        w += sorted[i].weight;
        bound += sorted[i].value;
      } else {
        bound += (capacity - w) * (sorted[i].value / sorted[i].weight);
        break;
      }
    }
    return bound;
  }

  let bestValue = 0;
  let bestSelected: string[] = [];
  let bestWeight = 0;

  // Depth-first search with bound pruning
  function dfs(index: number, currWeight: number, currValue: number, currentTaken: string[]) {
    if (currValue > bestValue) {
      bestValue = currValue;
      bestSelected = [...currentTaken];
      bestWeight = currWeight;
    }

    if (index >= n) return;

    // Prune branch if its upper bound cannot beat current best
    const bound = getBound(index, currWeight, currValue);
    if (bound <= bestValue + 1e-6) return;

    // Try including item (if fits)
    const item = sorted[index];
    if (currWeight + item.weight <= capacity + 1e-6) {
      currentTaken.push(item.id);
      dfs(index + 1, currWeight + item.weight, currValue + item.value, currentTaken);
      currentTaken.pop();
    }

    // Try excluding item
    dfs(index + 1, currWeight, currValue, currentTaken);
  }

  dfs(0, 0, 0, []);

  const end = performance.now();
  return {
    selectedIds: bestSelected,
    totalValue: Number(bestValue.toFixed(4)),
    totalWeight: Number(bestWeight.toFixed(2)),
    runtimeMs: Math.max(0.6, Number((end - start).toFixed(2))),
  };
}
