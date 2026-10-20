"""Selection pipeline coordinating Phase 1 (Set Cover), Phase 2 (Knapsack), and Baselines."""

import time
import tracemalloc
from typing import List, Dict, Set, Tuple, Any, Optional

from smarttest.selection.set_cover import run_greedy_set_cover
from smarttest.selection.knapsack_greedy import solve_greedy_knapsack
from smarttest.selection.knapsack_dp import solve_dp_knapsack
from smarttest.selection.branch_bound import solve_branch_and_bound


def select_tests(
    candidate_tests: List[Dict[str, Any]],
    affected_functions: Set[str],
    distance_map: Dict[str, int],
    budget_sec: float,
    algorithm: str = "dp",
) -> Dict[str, Any]:
    """Runs two-phase selection: Phase 1 (Set Cover) + Phase 2 (Knapsack).

    Returns:
        Dictionary with:
            - selected: list of test IDs
            - totalTimeSec: float
            - totalRisk: float
            - coveragePct: float
            - algorithmRuntimeMs: float
            - nodesExplored: int (B&B only)
            - timedOut: bool (B&B only)
            - uncoverableCount: int
            - memoryKb: float
    """
    tracemalloc.start()
    t_start = time.perf_counter()

    if not candidate_tests or budget_sec <= 0.0 or not affected_functions:
        elapsed_ms = max(0.1, round((time.perf_counter() - t_start) * 1000.0, 2))
        _, peak_mem = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        return {
            "selected": [],
            "totalTimeSec": 0.0,
            "totalRisk": 0.0,
            "coveragePct": 0.0,
            "algorithmRuntimeMs": elapsed_ms,
            "nodesExplored": 1,
            "timedOut": False,
            "uncoverableCount": len(affected_functions),
            "memoryKb": round(peak_mem / 1024.0, 1),
        }

    # Phase 1: Set Cover
    (
        phase1_chosen,
        remaining_tests,
        rem_budget,
        covered_set,
        uncoverable_count,
    ) = run_greedy_set_cover(
        candidate_tests=candidate_tests,
        affected_functions=affected_functions,
        distance_map=distance_map,
        budget_sec=budget_sec,
    )

    # Phase 2: Knapsack on remaining candidate tests
    phase2_chosen: List[Dict[str, Any]] = []
    p2_time = 0.0
    p2_risk = 0.0
    nodes_explored = 0
    timed_out = False

    alg_lower = algorithm.lower()
    if alg_lower == "greedy":
        phase2_chosen, p2_time, p2_risk = solve_greedy_knapsack(
            remaining_tests, rem_budget
        )
    elif alg_lower == "bnb":
        phase2_chosen, p2_time, p2_risk, nodes_explored, timed_out = (
            solve_branch_and_bound(remaining_tests, rem_budget)
        )
    else:  # default "dp"
        phase2_chosen, p2_time, p2_risk = solve_dp_knapsack(
            remaining_tests, rem_budget
        )

    # Combine selected tests
    final_selected = phase1_chosen + phase2_chosen
    selected_ids = [t["id"] for t in final_selected]

    total_time = round(sum(float(t["timeSec"]) for t in final_selected), 2)
    total_risk = round(sum(float(t.get("risk", 0.0)) for t in final_selected), 4)

    # Update coverage including Phase 2 tests
    for t in phase2_chosen:
        covered_set.update(set(t.get("covers", [])) & affected_functions)

    coverable_total = len(affected_functions) - uncoverable_count
    if coverable_total > 0:
        coverage_pct = round((len(covered_set) / coverable_total) * 100.0, 1)
    else:
        coverage_pct = 100.0 if affected_functions else 0.0

    elapsed_ms = max(0.1, round((time.perf_counter() - t_start) * 1000.0, 2))
    _, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    return {
        "selected": selected_ids,
        "totalTimeSec": total_time,
        "totalRisk": total_risk,
        "coveragePct": coverage_pct,
        "algorithmRuntimeMs": elapsed_ms,
        "nodesExplored": nodes_explored,
        "timedOut": timed_out,
        "uncoverableCount": uncoverable_count,
        "memoryKb": max(1.0, round(peak_mem / 1024.0, 1)),
    }


def compare_algorithms(
    candidate_tests: List[Dict[str, Any]],
    affected_functions: Set[str],
    distance_map: Dict[str, int],
    budget_sec: float,
) -> List[Dict[str, Any]]:
    """Runs Greedy, DP, and B&B on the exact same instance and computes optimality gaps."""
    dp_res = select_tests(
        candidate_tests, affected_functions, distance_map, budget_sec, algorithm="dp"
    )
    dp_risk = dp_res["totalRisk"]

    greedy_res = select_tests(
        candidate_tests, affected_functions, distance_map, budget_sec, algorithm="greedy"
    )
    bnb_res = select_tests(
        candidate_tests, affected_functions, distance_map, budget_sec, algorithm="bnb"
    )

    def calc_gap(val: float, opt: float) -> float:
        if opt <= 0.0:
            return 0.0
        gap = max(0.0, (opt - val) / opt * 100.0)
        return round(gap, 1)

    return [
        {
            "algorithm": "greedy",
            "totalRisk": greedy_res["totalRisk"],
            "totalTimeSec": greedy_res["totalTimeSec"],
            "testsSelected": len(greedy_res["selected"]),
            "runtimeMs": greedy_res["algorithmRuntimeMs"],
            "memoryKb": greedy_res["memoryKb"],
            "optimalityGapPct": calc_gap(greedy_res["totalRisk"], dp_risk),
        },
        {
            "algorithm": "dp",
            "totalRisk": dp_res["totalRisk"],
            "totalTimeSec": dp_res["totalTimeSec"],
            "testsSelected": len(dp_res["selected"]),
            "runtimeMs": dp_res["algorithmRuntimeMs"],
            "memoryKb": dp_res["memoryKb"],
            "optimalityGapPct": 0.0,
        },
        {
            "algorithm": "bnb",
            "totalRisk": bnb_res["totalRisk"],
            "totalTimeSec": bnb_res["totalTimeSec"],
            "testsSelected": len(bnb_res["selected"]),
            "runtimeMs": bnb_res["algorithmRuntimeMs"],
            "memoryKb": bnb_res["memoryKb"],
            "optimalityGapPct": calc_gap(bnb_res["totalRisk"], dp_risk),
        },
    ]


def select_baseline_dependency_only(
    candidate_tests: List[Dict[str, Any]],
    distance_map: Dict[str, int],
    budget_sec: float,
) -> List[str]:
    """Baseline: tests sorted by min dependency distance ascending, ties by id."""
    def test_dist(t: Dict[str, Any]) -> int:
        dists = [distance_map.get(f, 999) for f in t.get("covers", [])]
        return min(dists) if dists else 999

    sorted_tests = sorted(
        candidate_tests,
        key=lambda t: (test_dist(t), str(t.get("id", ""))),
    )

    selected: List[str] = []
    used_time = 0.0
    for t in sorted_tests:
        if used_time + t["timeSec"] <= budget_sec + 1e-9:
            selected.append(t["id"])
            used_time += t["timeSec"]

    return selected


def select_baseline_risk_only(
    candidate_tests: List[Dict[str, Any]],
    budget_sec: float,
) -> List[str]:
    """Baseline: tests sorted by predicted risk descending, ties by id."""
    sorted_tests = sorted(
        candidate_tests,
        key=lambda t: (-float(t.get("risk", 0.0)), str(t.get("id", ""))),
    )

    selected: List[str] = []
    used_time = 0.0
    for t in sorted_tests:
        if used_time + t["timeSec"] <= budget_sec + 1e-9:
            selected.append(t["id"])
            used_time += t["timeSec"]

    return selected


def select_baseline_random(
    suite_tests: List[Dict[str, Any]],
    budget_sec: float,
    rng,
) -> List[str]:
    """Baseline: random permutation of the whole suite."""
    shuffled = suite_tests.copy()
    rng.shuffle(shuffled)

    selected: List[str] = []
    used_time = 0.0
    for t in shuffled:
        if used_time + t["timeSec"] <= budget_sec + 1e-9:
            selected.append(t["id"])
            used_time += t["timeSec"]

    return selected
