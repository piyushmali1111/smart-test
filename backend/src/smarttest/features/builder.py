"""Unified feature builder for ML training and live API inference."""

import math
from typing import Dict, List, Set, Any, Optional

FEATURE_NAMES = [
    "dep_distance",
    "covers_changed",
    "n_affected_covered",
    "frac_affected_covered",
    "test_breadth",
    "test_time",
    "log_test_time",
    "hist_fail_rate",
    "recent_fail_count",
    "blast_radius",
    "topo_level",
    "module_churn",
]


def build_features(
    changed_function_id: str,
    test_id: str,
    dep_graph: Any,
    test_meta: Dict[str, Any],
    history: Optional[Dict[str, Any]] = None,
    churn_map: Optional[Dict[str, float]] = None,
    precomputed_affected: Optional[Tuple[List[Dict[str, Any]], Dict[str, int]]] = None,
) -> Dict[str, float]:
    """Computes the 12 features for a (changed_function_id, test_id) pair.

    Single source of truth used by both offline training and live REST API serving.

    Args:
        changed_function_id: Target function ID undergoing code modification.
        test_id: Unique test identifier.
        dep_graph: DependencyGraph instance.
        test_meta: Test metadata dictionary containing 'timeSec' and 'covers'.
        history: Historical stats {test_id: {'fails': int, 'appearances': int, 'recent_fails': int}}.
        churn_map: Map of module_name -> simulated churn score [0..1].
        precomputed_affected: Optional cached (affected_list, distance_map) to accelerate bulk processing.

    Returns:
        Dictionary mapping feature name -> float value.
    """
    if precomputed_affected:
        affected_list, dist_map = precomputed_affected
    else:
        affected_list, dist_map = dep_graph.get_affected_and_distances([changed_function_id])

    affected_set = {a["id"] for a in affected_list}
    test_covers: Set[str] = set(test_meta.get("covers", []))

    # 1. dep_distance: min distance from changed function to any function test covers
    intersect = test_covers & affected_set
    if intersect:
        min_dist = min(dist_map.get(f, 99) for f in intersect)
    else:
        min_dist = 99.0

    # 2. covers_changed
    covers_changed = 1.0 if changed_function_id in test_covers else 0.0

    # 3. n_affected_covered
    n_affected = float(len(intersect))

    # 4. frac_affected_covered
    blast_radius = float(max(1, len(affected_set)))
    frac_affected = n_affected / blast_radius

    # 5. test_breadth
    test_breadth = float(len(test_covers))

    # 6. test_time and 7. log_test_time
    test_time = float(test_meta.get("timeSec", 1.0))
    log_test_time = math.log(max(0.01, test_time) + 1.0)

    # 8. hist_fail_rate and 9. recent_fail_count
    if history and test_id in history:
        h_rec = history[test_id]
        fails = h_rec.get("fails", 0)
        appearances = h_rec.get("appearances", 0)
        hist_fail_rate = (fails + 1.0) / (appearances + 2.0)
        recent_fails = float(h_rec.get("recent_fails", 0))
    else:
        # Prior smoothing for cold-start / round 1
        hist_fail_rate = 1.0 / 2.0
        recent_fails = 0.0

    # 10. blast_radius (already computed)

    # 11. topo_level
    topo_level = float(dep_graph.node_levels.get(changed_function_id, 0))

    # 12. module_churn
    mod_name = changed_function_id.split(".")[0]
    module_churn = float(churn_map.get(mod_name, 0.5)) if churn_map else 0.5

    return {
        "dep_distance": float(min_dist),
        "covers_changed": covers_changed,
        "n_affected_covered": n_affected,
        "frac_affected_covered": frac_affected,
        "test_breadth": test_breadth,
        "test_time": test_time,
        "log_test_time": log_test_time,
        "hist_fail_rate": hist_fail_rate,
        "recent_fail_count": recent_fails,
        "blast_radius": blast_radius,
        "topo_level": topo_level,
        "module_churn": module_churn,
    }
