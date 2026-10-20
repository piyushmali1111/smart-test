"""Branch and Bound 0/1 Knapsack algorithm with Fractional Upper Bound pruning."""

import time
import math
from typing import List, Dict, Tuple, Any

from smarttest.config import BNB_TIME_LIMIT_SEC, DP_DISCRETIZATION_UNIT_SEC


def solve_branch_and_bound(
    items: List[Dict[str, Any]],
    budget_sec: float,
    time_limit_sec: float = BNB_TIME_LIMIT_SEC,
) -> Tuple[List[Dict[str, Any]], float, float, int, bool]:
    """Computes exact optimal 0/1 Knapsack solution using Branch and Bound with time bounding.

    Algorithm: Depth-First Search Branch and Bound with Fractional Knapsack Upper Bound
    Time Complexity: Worst case O(2^n), heavily pruned by fractional upper bounds in practice.
    Space Complexity: O(n) call/branch recursion depth.

    Pruning condition:
        upper_bound = current_value + fractional_knapsack_bound(remaining_items, remaining_capacity)
        If upper_bound <= best_value, prune branch.

    Args:
        items: List of candidate test dictionaries with 'id', 'timeSec', and 'risk'.
        budget_sec: Available execution time budget in seconds.
        time_limit_sec: Wall-clock timeout threshold in seconds (default 2.0s).

    Returns:
        Tuple of:
            - selected_items: Best subset of items found.
            - total_time: Total time of chosen items.
            - total_risk: Total risk value of chosen items.
            - nodes_explored: Number of state space tree nodes visited.
            - timed_out: True if time limit was reached, False if proved optimal.
    """
    if budget_sec <= 0.0 or not items:
        return [], 0.0, 0.0, 1, False

    W = int(math.floor((budget_sec + 1e-9) / DP_DISCRETIZATION_UNIT_SEC))
    if W <= 0:
        return [], 0.0, 0.0, 1, False

    n = len(items)
    discretized = []
    for it in items:
        wt = max(1, int(math.ceil((float(it["timeSec"]) - 1e-9) / DP_DISCRETIZATION_UNIT_SEC)))
        val = float(it.get("risk", 0.0))
        ratio = val / wt
        discretized.append({"item": it, "w": wt, "v": val, "ratio": ratio})

    # Sort items by value density in descending order: ratio DESC, weight ASC, ID ASC
    discretized.sort(
        key=lambda x: (-x["ratio"], x["w"], str(x["item"].get("id", "")))
    )

    best_val = 0.0
    best_selection: List[Dict[str, Any]] = []
    nodes_explored = 0
    timed_out = False
    start_time = time.perf_counter()

    def fractional_bound(idx: int, capacity: int) -> float:
        """Calculates upper bound using greedy relaxed fractional knapsack."""
        bound = 0.0
        cap = capacity
        for i in range(idx, n):
            wt = discretized[i]["w"]
            val = discretized[i]["v"]
            if wt <= cap:
                cap -= wt
                bound += val
            else:
                bound += val * (cap / wt)
                break
        return bound

    # Initial greedy heuristic to set a strong baseline best_val
    greedy_cap = W
    greedy_val = 0.0
    greedy_chosen = []
    for d in discretized:
        if d["w"] <= greedy_cap:
            greedy_cap -= d["w"]
            greedy_val += d["v"]
            greedy_chosen.append(d["item"])
    best_val = greedy_val
    best_selection = greedy_chosen

    # DFS Branch and Bound stack
    # Each frame: (index, current_val, current_cap, chosen_items)
    stack = [(0, 0.0, W, [])]

    while stack:
        nodes_explored += 1
        if nodes_explored % 50 == 0:
            if time.perf_counter() - start_time > time_limit_sec:
                timed_out = True
                break

        idx, cur_val, cur_cap, chosen = stack.pop()

        if cur_val > best_val + 1e-9:
            best_val = cur_val
            best_selection = chosen

        if idx >= n or cur_cap <= 0:
            continue

        bound = cur_val + fractional_bound(idx, cur_cap)
        if bound <= best_val + 1e-9:
            continue  # Prune branch

        # Branch 1: Exclude item idx (explore right child)
        stack.append((idx + 1, cur_val, cur_cap, chosen))

        # Branch 2: Include item idx (explore left child first)
        d = discretized[idx]
        if d["w"] <= cur_cap:
            stack.append((
                idx + 1,
                cur_val + d["v"],
                cur_cap - d["w"],
                chosen + [d["item"]],
            ))

    total_time = sum(float(it["timeSec"]) for it in best_selection)
    total_risk = sum(float(it.get("risk", 0.0)) for it in best_selection)

    return (
        best_selection,
        round(total_time, 2),
        round(total_risk, 4),
        nodes_explored,
        timed_out,
    )
