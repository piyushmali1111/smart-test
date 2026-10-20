"""Greedy heuristic 0/1 Knapsack algorithm for Phase 2 value maximization."""

from typing import List, Dict, Tuple, Any


def solve_greedy_knapsack(
    items: List[Dict[str, Any]],
    budget_sec: float,
) -> Tuple[List[Dict[str, Any]], float, float]:
    """Selects subset of items using the greedy ratio heuristic (risk / time).

    Algorithm: Greedy Heuristic 0/1 Knapsack
    Time Complexity: O(n log n) dominated by the sorting step, where n is item count.
    Space Complexity: O(n) for sorting and storing selected items.

    Items are sorted in descending order of value density (r_i / t_i). Ties are broken
    by smaller execution time, then by item ID.

    Args:
        items: List of candidate test dictionaries with 'id', 'timeSec', and 'risk'.
        budget_sec: Available execution time budget in seconds.

    Returns:
        Tuple of:
            - selected_items: Chosen items.
            - total_time: Sum of execution times of chosen items.
            - total_risk: Sum of risk values of chosen items.
    """
    if budget_sec <= 0.0 or not items:
        return [], 0.0, 0.0

    # Sort key: (-ratio, timeSec, id)
    def sort_key(item: Dict[str, Any]):
        t = max(0.01, float(item["timeSec"]))
        r = float(item.get("risk", 0.0))
        ratio = r / t
        return (-ratio, t, str(item.get("id", "")))

    sorted_items = sorted(items, key=sort_key)

    selected: List[Dict[str, Any]] = []
    total_time = 0.0
    total_risk = 0.0

    for item in sorted_items:
        t = float(item["timeSec"])
        if total_time + t <= budget_sec + 1e-9:
            selected.append(item)
            total_time += t
            total_risk += float(item.get("risk", 0.0))

    return selected, round(total_time, 2), round(total_risk, 4)
