"""Dataset builder transforming mutants into a leak-free tabular dataset."""

import json
from pathlib import Path
from typing import List, Dict, Set, Any, Tuple
import pandas as pd

from smarttest.config import ARTIFACTS_DIR, TOTAL_ROUNDS, TRAIN_ROUNDS_MAX
from smarttest.features.builder import build_features, FEATURE_NAMES
from smarttest.graph.model import DependencyGraph


def build_dataset_and_history(
    mutants: List[Dict[str, Any]],
    tests_list: List[Dict[str, Any]],
    dep_graph: DependencyGraph,
    churn_map: Dict[str, float],
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Builds the leak-free tabular dataset and the frozen serving history table.

    Anti-leakage protocol:
    - History features for round k are derived solely from rounds < k.
    - Rows are grouped strictly by mutant_id.
    - Frozen serving history accumulates stats from rounds 1..TRAIN_ROUNDS_MAX.
    """
    tests_meta_map = {t["id"]: t for t in tests_list}

    # Pre-aggregate mutant appearances and failures by round
    # round -> list of mutants
    mutants_by_round: Dict[int, List[Dict[str, Any]]] = {
        r: [] for r in range(1, TOTAL_ROUNDS + 1)
    }
    for m in mutants:
        # Only killed mutants are included in the dataset
        if m.get("killed", False):
            r = m.get("round", 1)
            mutants_by_round.setdefault(r, []).append(m)

    rows = []
    # Test tracking for history: test_id -> {'appearances': int, 'fails': int, 'history_events': list of bool}
    cumulative_history: Dict[str, Dict[str, Any]] = {}
    frozen_serving_history: Dict[str, Any] = {}

    # Cache graph traversals
    affected_cache: Dict[str, Any] = {}

    for current_round in range(1, TOTAL_ROUNDS + 1):
        # 1. Snapshot historical stats available strictly BEFORE current_round
        round_history_snapshot: Dict[str, Any] = {}
        for t_id, data in cumulative_history.items():
            recent_fails = sum(data["history_events"][-5:]) if data["history_events"] else 0
            round_history_snapshot[t_id] = {
                "appearances": data["appearances"],
                "fails": data["fails"],
                "recent_fails": recent_fails,
            }

        if current_round == TRAIN_ROUNDS_MAX + 1:
            # Snapshot history at end of training rounds for live inference
            frozen_serving_history = copy_history_snapshot(round_history_snapshot)

        # 2. Build rows for mutants in current_round
        round_mutants = mutants_by_round.get(current_round, [])
        for m in round_mutants:
            m_id = m["id"]
            func_id = m["functionId"]
            split = m["split"]
            failing_set = set(m.get("failingTests", []))
            candidate_tests = m.get("candidateTests", [])

            if func_id not in affected_cache:
                affected_cache[func_id] = dep_graph.get_affected_and_distances([func_id])
            precomputed = affected_cache[func_id]

            for t_id in candidate_tests:
                if t_id not in tests_meta_map:
                    continue
                t_meta = tests_meta_map[t_id]

                feats = build_features(
                    changed_function_id=func_id,
                    test_id=t_id,
                    dep_graph=dep_graph,
                    test_meta=t_meta,
                    history=round_history_snapshot,
                    churn_map=churn_map,
                    precomputed_affected=precomputed,
                )

                label = 1 if t_id in failing_set else 0

                row = {
                    "mutant_id": m_id,
                    "test_id": t_id,
                    "round": current_round,
                    "split": split,
                    "detected": label,
                }
                row.update(feats)
                rows.append(row)

        # 3. Update cumulative history with outcomes from current_round
        for m in round_mutants:
            failing_set = set(m.get("failingTests", []))
            candidate_tests = m.get("candidateTests", [])
            for t_id in candidate_tests:
                if t_id not in cumulative_history:
                    cumulative_history[t_id] = {
                        "appearances": 0,
                        "fails": 0,
                        "history_events": [],
                    }
                is_fail = 1 if t_id in failing_set else 0
                cumulative_history[t_id]["appearances"] += 1
                cumulative_history[t_id]["fails"] += is_fail
                cumulative_history[t_id]["history_events"].append(is_fail)

    if not frozen_serving_history:
        # If dataset had fewer rounds or all train
        frozen_serving_history = copy_history_snapshot(round_history_snapshot)

    df = pd.DataFrame(rows)
    return df, frozen_serving_history


def copy_history_snapshot(hist: Dict[str, Any]) -> Dict[str, Any]:
    return {
        t_id: {
            "appearances": v["appearances"],
            "fails": v["fails"],
            "recent_fails": v["recent_fails"],
        }
        for t_id, v in hist.items()
    }
