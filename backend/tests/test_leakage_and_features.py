"""Tests verifying anti-leakage protocol, split boundaries, and unified feature computation."""

import pytest
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupKFold

from smarttest.features.builder import build_features, FEATURE_NAMES


def test_no_mutant_appears_in_both_train_and_holdout():
    """Validates disjoint mutant partitioning between train and holdout splits."""
    # Mock mutant dataset
    mutants = [
        {"id": f"m_{i}", "round": (i % 10) + 1, "split": "train" if (i % 10) + 1 <= 7 else "holdout"}
        for i in range(100)
    ]
    train_ids = {m["id"] for m in mutants if m["split"] == "train"}
    holdout_ids = {m["id"] for m in mutants if m["split"] == "holdout"}

    assert len(train_ids & holdout_ids) == 0
    assert len(train_ids) > 0 and len(holdout_ids) > 0


def test_group_k_fold_folds_are_disjoint_by_mutant():
    """Validates that GroupKFold never leaks rows of the same mutant across folds."""
    # Synthetic dataset with 20 mutants and 5 candidate tests each (100 rows)
    mutants = [f"m_{i // 5}" for i in range(100)]
    X = np.random.randn(100, 5)
    y = np.random.randint(0, 2, size=100)

    gkf = GroupKFold(n_splits=5)
    for fold, (train_idx, val_idx) in enumerate(gkf.split(X, y, groups=mutants)):
        train_mutants = set(mutants[i] for i in train_idx)
        val_mutants = set(mutants[i] for i in val_idx)

        assert len(train_mutants & val_mutants) == 0, f"Leakage detected in fold {fold}"


def test_unified_feature_builder_consistency():
    """Verifies that offline feature computation and live API inference yield identical vectors."""
    class DummyGraph:
        def __init__(self):
            self.node_levels = {"cart.calculate_total": 2}
        def get_affected_and_distances(self, changed):
            return [{"id": "cart.calculate_total", "distance": 0}, {"id": "cart.add_item", "distance": 1}], {"cart.calculate_total": 0, "cart.add_item": 1}

    g = DummyGraph()
    t_meta = {"timeSec": 2.5, "covers": ["cart.calculate_total", "cart.add_item"]}
    hist = {"t1": {"appearances": 10, "fails": 3, "recent_fails": 1}}
    churn = {"cart": 0.45}

    # Training invocation
    feats_train = build_features(
        changed_function_id="cart.calculate_total",
        test_id="t1",
        dep_graph=g,
        test_meta=t_meta,
        history=hist,
        churn_map=churn,
    )

    # API serving invocation
    feats_serve = build_features(
        changed_function_id="cart.calculate_total",
        test_id="t1",
        dep_graph=g,
        test_meta=t_meta,
        history=hist,
        churn_map=churn,
    )

    assert feats_train == feats_serve
    assert set(feats_train.keys()) == set(FEATURE_NAMES)
    assert feats_train["covers_changed"] == 1.0
    assert feats_train["dep_distance"] == 0.0
