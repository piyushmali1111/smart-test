"""Dynamic Programming 0/1 Knapsack algorithm with capacity discretization."""

import math
import numpy as np
from typing import List, Dict, Tuple, Any

from smarttest.config import DP_DISCRETIZATION_UNIT_SEC


def solve_dp_knapsack(
    items: List[Dict[str, Any]],
    budget_sec: float,
) -> Tuple[List[Dict[str, Any]], float, float]:
    """Computes exact optimal 0/1 Knapsack solution using Dynamic Programming.

    Algorithm: Pseudo-polynomial Dynamic Programming with Boolean Backtracking Table
    Time Complexity: O(n * W) where n is item count and W = ceil(budget_sec / unit) is discrete capacity.
    Space Complexity: O(n * W) using a compact NumPy uint8 boolean matrix `keep[n, W + 1]`.

    Times are discretized into integer capacity units:
        w_i = ceil(timeSec / DP_DISCRETIZATION_UNIT_SEC)
        W = floor(budget_sec / DP_DISCRETIZATION_UNIT_SEC)

    Args:
        items: List of candidate test dictionaries with 'id', 'timeSec', and 'risk'.
        budget_sec: Available execution time budget in seconds.

    Returns:
        Tuple of:
            - selected_items: Optimal subset of items.
            - total_time: Sum of execution times of chosen items.
            - total_risk: Sum of risk values of chosen items.
    """
    if budget_sec <= 0.0 or not items:
        return [], 0.0, 0.0

    n = len(items)
    W = int(math.floor((budget_sec + 1e-9) / DP_DISCRETIZATION_UNIT_SEC))
    if W <= 0:
        return [], 0.0, 0.0

    weights = [
        max(1, int(math.ceil((float(item["timeSec"]) - 1e-9) / DP_DISCRETIZATION_UNIT_SEC)))
        for item in items
    ]
    values = [float(item.get("risk", 0.0)) for item in items]

    # dp[w] stores max value achievable with discrete capacity w
    dp = np.zeros(W + 1, dtype=np.float64)
    # keep[i, w] is 1 if item i is selected in state (i, w), else 0
    keep = np.zeros((n, W + 1), dtype=np.uint8)

    for i in range(n):
        wt = weights[i]
        val = values[i]
        for w in range(W, wt - 1, -1):
            if dp[w - wt] + val > dp[w] + 1e-9:
                dp[w] = dp[w - wt] + val
                keep[i, w] = 1

    # Reconstruct chosen subset
    selected: List[Dict[str, Any]] = []
    curr_w = W
    for i in range(n - 1, -1, -1):
        if keep[i, curr_w] == 1:
            selected.append(items[i])
            curr_w -= weights[i]

    selected.reverse()

    total_time = sum(float(it["timeSec"]) for it in selected)
    total_risk = sum(float(it.get("risk", 0.0)) for it in selected)

    return selected, round(total_time, 2), round(total_risk, 4)
