"""Scalability benchmark measuring runtime, memory, and optimality gaps across problem scale."""

import time
import tracemalloc
import random
from typing import List, Dict, Any, Tuple
import numpy as np

from smarttest.config import SEED
from smarttest.selection.knapsack_greedy import solve_greedy_knapsack
from smarttest.selection.knapsack_dp import solve_dp_knapsack
from smarttest.selection.branch_bound import solve_branch_and_bound


def run_scalability_experiments() -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Evaluates Greedy, DP, and Branch & Bound algorithms as item count n scales."""
    rng = random.Random(SEED)
    np_rng = np.random.default_rng(SEED)

    scales = [10, 20, 50, 100, 200, 500, 1000, 2000]
    scalability_results: List[Dict[str, Any]] = []

    for n in scales:
        # Generate synthetic tests
        items = []
        for i in range(n):
            # Realistic lognormal time between 0.1s and 30s
            t_sec = float(np.clip(np_rng.lognormal(mean=0.8, sigma=0.9), 0.1, 35.0))
            # Risk between 0.05 and 0.95
            r_val = float(np_rng.beta(a=1.5, b=2.5))
            items.append({
                "id": f"synth_test_{i}",
                "timeSec": round(t_sec, 2),
                "risk": round(r_val, 4),
            })

        # Realistic budget around 20% of total synthetic time
        tot_time = sum(it["timeSec"] for it in items)
        budget = max(5.0, round(tot_time * 0.20, 1))

        # Benchmark Greedy (median of 5 runs)
        greedy_times = []
        for _ in range(5):
            t0 = time.perf_counter()
            solve_greedy_knapsack(items, budget)
            greedy_times.append((time.perf_counter() - t0) * 1000.0)
        greedy_ms = round(float(np.median(greedy_times)), 2)

        # Benchmark DP
        dp_times = []
        for _ in range(5):
            t0 = time.perf_counter()
            solve_dp_knapsack(items, budget)
            dp_times.append((time.perf_counter() - t0) * 1000.0)
        dp_ms = round(float(np.median(dp_times)), 2)

        # Benchmark Branch and Bound
        # For large n > 200, B&B may hit its 2.0s timeout
        bnb_times = []
        bnb_timed_out = False
        for _ in range(3 if n <= 200 else 1):
            t0 = time.perf_counter()
            _, _, _, _, timed_out = solve_branch_and_bound(items, budget, time_limit_sec=2.0)
            bnb_times.append((time.perf_counter() - t0) * 1000.0)
            if timed_out:
                bnb_timed_out = True
        bnb_ms = round(float(np.median(bnb_times)), 2)

        scalability_results.append({
            "n": n,
            "greedyMs": greedy_ms,
            "dpMs": dp_ms,
            "bnbMs": bnb_ms,
            "bnbTimedOut": bnb_timed_out,
        })

    # Optimality gap evaluation over 200 random instances (n=20..50)
    gaps = []
    for _ in range(200):
        n_inst = rng.randint(15, 45)
        inst_items = []
        for i in range(n_inst):
            t_sec = float(np.clip(np_rng.lognormal(mean=0.8, sigma=0.8), 0.2, 25.0))
            r_val = float(np_rng.uniform(0.1, 0.95))
            inst_items.append({"id": f"t_{i}", "timeSec": round(t_sec, 2), "risk": round(r_val, 4)})
        b_sec = round(sum(it["timeSec"] for it in inst_items) * rng.uniform(0.15, 0.40), 1)

        _, _, dp_val = solve_dp_knapsack(inst_items, b_sec)
        _, _, gr_val = solve_greedy_knapsack(inst_items, b_sec)

        if dp_val > 0:
            gap = max(0.0, (dp_val - gr_val) / dp_val * 100.0)
            gaps.append(gap)

    optimality_stats = {
        "meanGapPct": round(float(np.mean(gaps)), 2),
        "maxGapPct": round(float(np.max(gaps)), 2),
        "medianGapPct": round(float(np.median(gaps)), 2),
        "instancesTested": len(gaps),
    }

    return scalability_results, optimality_stats
