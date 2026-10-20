"""Tests verifying deterministic reproducibility across selection and simulation runs."""

from smarttest.experiments.scalability import run_scalability_experiments
from smarttest.selection.knapsack_greedy import solve_greedy_knapsack
from smarttest.selection.knapsack_dp import solve_dp_knapsack
from smarttest.selection.branch_bound import solve_branch_and_bound


def test_knapsack_algorithms_determinism():
    items = [
        {"id": f"t_{i}", "timeSec": round(1.2 + (i % 5) * 0.4, 2), "risk": round(0.5 + (i % 7) * 0.1, 4)}
        for i in range(25)
    ]
    budget = 14.5

    # Run DP twice
    dp_sel1, dp_t1, dp_r1 = solve_dp_knapsack(items, budget)
    dp_sel2, dp_t2, dp_r2 = solve_dp_knapsack(items, budget)
    assert dp_sel1 == dp_sel2
    assert dp_t1 == dp_t2
    assert dp_r1 == dp_r2

    # Run Greedy twice
    gr_sel1, gr_t1, gr_r1 = solve_greedy_knapsack(items, budget)
    gr_sel2, gr_t2, gr_r2 = solve_greedy_knapsack(items, budget)
    assert gr_sel1 == gr_sel2

    # Run B&B twice
    bnb_sel1, bnb_t1, bnb_r1, n1, _ = solve_branch_and_bound(items, budget)
    bnb_sel2, bnb_t2, bnb_r2, n2, _ = solve_branch_and_bound(items, budget)
    assert bnb_sel1 == bnb_sel2
    assert n1 == n2
