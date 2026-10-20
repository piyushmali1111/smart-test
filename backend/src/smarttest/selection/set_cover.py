"""Risk-weighted Greedy Set Cover algorithm for Phase 1 of test selection."""

from typing import List, Dict, Set, Tuple, Any


def run_greedy_set_cover(
    candidate_tests: List[Dict[str, Any]],
    affected_functions: Set[str],
    distance_map: Dict[str, int],
    budget_sec: float,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], float, Set[str], int]:
    """Selects a minimum-cost subset of tests to maximize coverage of affected functions.

    Algorithm: Weighted Greedy Set Cover with Risk Scaling
    Time Complexity: O(n * |C|) where n is the number of candidate tests and |C| is affected functions.
    Space Complexity: O(n + |C|) for tracking covered elements and remaining budget.

    Weight for each function: w_f = 1.0 / (1.0 + distance_f).
    Selection criterion: repeatedly select candidate test maximizing:
        (sum of w_f for newly covered functions) * (0.5 + risk) / timeSec
    subject to timeSec <= remaining_budget.

    Args:
        candidate_tests: Candidate tests with fields: 'id', 'timeSec', 'risk', 'covers'.
        affected_functions: Set of function IDs in the affected impact set.
        distance_map: Dictionary mapping function ID -> condensed graph distance.
        budget_sec: Total available execution time budget in seconds.

    Returns:
        Tuple of:
            - phase1_selected: Tests chosen in Phase 1.
            - remaining_tests: Candidate tests not chosen in Phase 1.
            - remaining_budget: Unspent budget after Phase 1.
            - covered_functions: Set of affected functions successfully covered.
            - uncoverable_count: Number of affected functions not covered by ANY candidate test.
    """
    if budget_sec <= 0.0 or not candidate_tests or not affected_functions:
        # Determine uncoverable count
        all_covered_by_any: Set[str] = set()
        for t in candidate_tests:
            all_covered_by_any.update(set(t.get("covers", [])) & affected_functions)
        uncoverable = len(affected_functions - all_covered_by_any)
        return [], candidate_tests.copy(), budget_sec, set(), uncoverable

    # Weights for each affected function
    weights: Dict[str, float] = {
        f_id: 1.0 / (1.0 + float(distance_map.get(f_id, 0)))
        for f_id in affected_functions
    }

    # Find which functions are coverable by candidate tests
    all_coverable: Set[str] = set()
    for t in candidate_tests:
        all_coverable.update(set(t.get("covers", [])) & affected_functions)

    uncoverable_count = len(affected_functions - all_coverable)

    selected: List[Dict[str, Any]] = []
    selected_ids: Set[str] = set()
    covered: Set[str] = set()
    remaining_budget = budget_sec

    remaining_pool = [t for t in candidate_tests]

    while remaining_pool and covered != all_coverable:
        best_test = None
        best_score = -1.0

        for t in remaining_pool:
            t_time = max(0.01, float(t["timeSec"]))
            if t_time > remaining_budget:
                continue

            t_covers = set(t.get("covers", [])) & affected_functions
            new_covered = t_covers - covered
            if not new_covered:
                continue

            new_weight = sum(weights[f] for f in new_covered)
            risk = float(t.get("risk", 0.0))
            score = (new_weight * (0.5 + risk)) / t_time

            if score > best_score:
                best_score = score
                best_test = t
            elif abs(score - best_score) < 1e-9 and best_test is not None:
                # Tie-breaker: smaller timeSec, then lexicographical ID
                if t_time < float(best_test["timeSec"]) or (
                    abs(t_time - float(best_test["timeSec"])) < 1e-9
                    and t["id"] < best_test["id"]
                ):
                    best_score = score
                    best_test = t

        if best_test is None or best_score <= 0.0:
            # No remaining test can cover any new function within remaining budget
            break

        selected.append(best_test)
        selected_ids.add(best_test["id"])
        remaining_budget -= float(best_test["timeSec"])
        remaining_budget = max(0.0, round(remaining_budget, 4))
        covered.update(set(best_test.get("covers", [])) & affected_functions)

        remaining_pool = [t for t in remaining_pool if t["id"] != best_test["id"]]

    remaining_tests = [t for t in candidate_tests if t["id"] not in selected_ids]
    return selected, remaining_tests, remaining_budget, covered, uncoverable_count
