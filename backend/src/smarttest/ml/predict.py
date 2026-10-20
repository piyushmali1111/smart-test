"""Inference scoring predicting test failure risk given code changes."""

from typing import List, Dict, Set, Any
import numpy as np

from smarttest.features.builder import build_features, FEATURE_NAMES
from smarttest.graph.model import DependencyGraph


def predict_test_risks(
    changed_functions: List[str],
    candidate_tests: List[Dict[str, Any]],
    model_bundle: Dict[str, Any],
    dep_graph: DependencyGraph,
    history: Dict[str, Any],
    churn_map: Dict[str, float],
) -> List[Dict[str, Any]]:
    """Predicts risk score for each candidate test across single or multiple code changes.

    Multi-change composition:
        Uses the Noisy-OR probabilistic combination:
        combined_risk = 1.0 - product(1.0 - risk_per_change)
    """
    if not candidate_tests or not changed_functions:
        return candidate_tests

    model = model_bundle["model"]
    feature_order = model_bundle.get("feature_names", FEATURE_NAMES)

    # Precompute affected sets for each changed function
    change_affected: Dict[str, Any] = {}
    for c_id in changed_functions:
        change_affected[c_id] = dep_graph.get_affected_and_distances([c_id])

    tests_with_risk: List[Dict[str, Any]] = []

    for test in candidate_tests:
        t_id = test["id"]
        risks_per_change: List[float] = []

        for c_id in changed_functions:
            precomputed = change_affected[c_id]
            feats = build_features(
                changed_function_id=c_id,
                test_id=t_id,
                dep_graph=dep_graph,
                test_meta=test,
                history=history,
                churn_map=churn_map,
                precomputed_affected=precomputed,
            )

            feat_vector = np.array([[feats[name] for name in feature_order]], dtype=np.float64)
            proba = float(model.predict_proba(feat_vector)[0, 1])
            risks_per_change.append(proba)

        # Noisy-OR combination across multiple changes
        prod_not_caught = 1.0
        for r in risks_per_change:
            prod_not_caught *= max(0.0, 1.0 - r)
        combined_risk = max(0.01, min(0.99, 1.0 - prod_not_caught))

        t_copy = dict(test)
        t_copy["risk"] = round(combined_risk, 4)
        tests_with_risk.append(t_copy)

    # Sort candidate tests by risk descending
    tests_with_risk.sort(key=lambda t: (-t["risk"], t["timeSec"], t["id"]))
    return tests_with_risk
