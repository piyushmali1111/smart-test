"""Unit tests for hand-written selection algorithms (Set Cover, Greedy, DP, B&B, Pipeline)."""

import itertools
import pytest

from smarttest.selection.set_cover import run_greedy_set_cover
from smarttest.selection.knapsack_greedy import solve_greedy_knapsack
from smarttest.selection.knapsack_dp import solve_dp_knapsack
from smarttest.selection.branch_bound import solve_branch_and_bound
from smarttest.selection.pipeline import select_tests


def brute_force_knapsack(items, budget_sec, unit=0.1):
    """Computes exact global optimum by evaluating all 2^n subsets."""
    n = len(items)
    best_val = 0.0
    best_subset = []
    best_time = 0.0

    for r in range(n + 1):
        for combo in itertools.combinations(items, r):
            t_sum = sum(it["timeSec"] for it in combo)
            if t_sum <= budget_sec + 1e-9:
                v_sum = sum(it["risk"] for it in combo)
                if v_sum > best_val:
                    best_val = v_sum
                    best_subset = list(combo)
                    best_time = t_sum

    return best_subset, round(best_time, 2), round(best_val, 4)


def test_knapsack_optimality_vs_brute_force_n_small():
    """Verifies DP == Branch and Bound == Brute Force for n <= 12."""
    items = [
        {"id": "t1", "timeSec": 1.2, "risk": 0.8},
        {"id": "t2", "timeSec": 2.5, "risk": 1.5},
        {"id": "t3", "timeSec": 0.8, "risk": 0.6},
        {"id": "t4", "timeSec": 3.0, "risk": 2.1},
        {"id": "t5", "timeSec": 1.5, "risk": 0.9},
        {"id": "t6", "timeSec": 4.0, "risk": 2.8},
        {"id": "t7", "timeSec": 0.5, "risk": 0.4},
        {"id": "t8", "timeSec": 2.0, "risk": 1.3},
    ]

    for budget in [2.0, 4.0, 6.5, 10.0]:
        bf_sel, bf_time, bf_val = brute_force_knapsack(items, budget)
        dp_sel, dp_time, dp_val = solve_dp_knapsack(items, budget)
        bnb_sel, bnb_time, bnb_val, _, timed_out = solve_branch_and_bound(items, budget)

        assert not timed_out
        assert abs(dp_val - bnb_val) < 1e-4, f"DP ({dp_val}) != BnB ({bnb_val}) at budget {budget}"
        # DP & BnB should match or be within discretization tolerance of brute force
        assert dp_val <= bf_val + 1e-4
        assert abs(dp_val - bf_val) < 0.05

        # Greedy should never beat DP
        gr_sel, gr_time, gr_val = solve_greedy_knapsack(items, budget)
        assert gr_val <= dp_val + 1e-4


def test_knapsack_edge_cases():
    items = [
        {"id": "t1", "timeSec": 5.0, "risk": 1.0},
        {"id": "t2", "timeSec": 10.0, "risk": 2.0},
    ]

    # 1. Budget 0 -> empty selection
    sel, t, val = solve_dp_knapsack(items, 0.0)
    assert sel == [] and t == 0.0 and val == 0.0

    # 2. Budget smaller than every test
    sel, t, val = solve_dp_knapsack(items, 2.0)
    assert sel == [] and t == 0.0 and val == 0.0

    # 3. Empty items
    sel, t, val = solve_dp_knapsack([], 10.0)
    assert sel == [] and t == 0.0 and val == 0.0


def test_branch_and_bound_timeout_path():
    """Verifies that hitting time_limit_sec produces feasible solution and sets timedOut=True."""
    # 40 items with diverse ratios and large capacity forcing deep exploration
    items = [
        {"id": f"t_{i}", "timeSec": round(1.0 + (i % 7) * 0.3, 2), "risk": round(1.0 + ((i * 3) % 11) * 0.2, 4)}
        for i in range(40)
    ]
    # Set micro timeout
    sel, t, val, nodes, timed_out = solve_branch_and_bound(items, 25.0, time_limit_sec=0.0001)
    assert timed_out is True
    assert t <= 25.0 + 1e-9


def test_greedy_set_cover_covers_all_when_budget_allows():
    candidate_tests = [
        {"id": "t1", "timeSec": 1.0, "risk": 0.5, "covers": ["f1", "f2"]},
        {"id": "t2", "timeSec": 1.0, "risk": 0.5, "covers": ["f2", "f3"]},
        {"id": "t3", "timeSec": 1.0, "risk": 0.5, "covers": ["f4"]},
    ]
    affected = {"f1", "f2", "f3", "f4"}
    dist_map = {"f1": 0, "f2": 1, "f3": 2, "f4": 1}

    # High budget allows covering all 4 functions
    sel, rem, rem_b, covered, uncov = run_greedy_set_cover(
        candidate_tests, affected, dist_map, budget_sec=10.0
    )
    assert covered == affected
    assert uncov == 0
    assert len(sel) == 3


def test_pipeline_total_time_never_exceeds_budget():
    candidate_tests = [
        {"id": f"t_{i}", "timeSec": 2.0 + (i * 0.5), "risk": 0.5 + i * 0.1, "covers": [f"f_{i}"]}
        for i in range(10)
    ]
    affected = {f"f_{i}" for i in range(10)}
    dist_map = {f"f_{i}": i for i in range(10)}

    for b in [3.0, 5.0, 7.5, 12.0]:
        res = select_tests(candidate_tests, affected, dist_map, budget_sec=b, algorithm="dp")
        assert res["totalTimeSec"] <= b + 1e-9
        assert 0.0 <= res["coveragePct"] <= 100.0
