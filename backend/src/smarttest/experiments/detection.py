"""Empirical detection experiments comparing selection strategies across budget allocations."""

import random
from typing import List, Dict, Set, Any, Tuple
import numpy as np

from smarttest.config import SEED, BUDGET_GRID, REFERENCE_BUDGET_SEC
from smarttest.graph.model import DependencyGraph
from smarttest.selection.pipeline import (
    select_tests,
    select_baseline_dependency_only,
    select_baseline_risk_only,
    select_baseline_random,
)
from smarttest.ml.predict import predict_test_risks


def run_detection_experiments(
    holdout_mutants: List[Dict[str, Any]],
    all_tests: List[Dict[str, Any]],
    dep_graph: DependencyGraph,
    model_bundle: Dict[str, Any],
    history: Dict[str, Any],
    churn_map: Dict[str, float],
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], Dict[str, Any]]:
    """Evaluates all strategies over budget grid on holdout killed mutants.

    Returns:
        - detectionVsBudget: List of records for the detection chart
        - strategies: Strategy summary table at REFERENCE_BUDGET_SEC
        - headline: Key overall impact metrics
    """
    tests_meta_map = {t["id"]: t for t in all_tests}
    suite_size = len(all_tests)
    suite_time = sum(float(t["timeSec"]) for t in all_tests)

    total_holdout_bugs = max(1, len(holdout_mutants))

    # Pre-score candidate tests for each holdout mutant
    mutant_eval_data: List[Dict[str, Any]] = []
    for m in holdout_mutants:
        func_id = m["functionId"]
        failing_tests = set(m.get("failingTests", []))
        affected, dist_map = dep_graph.get_affected_and_distances([func_id])
        affected_set = {a["id"] for a in affected}

        cand_tests = [
            tests_meta_map[t_id]
            for t_id in m.get("candidateTests", [])
            if t_id in tests_meta_map
        ]

        scored_cands = predict_test_risks(
            changed_functions=[func_id],
            candidate_tests=cand_tests,
            model_bundle=model_bundle,
            dep_graph=dep_graph,
            history=history,
            churn_map=churn_map,
        )

        mutant_eval_data.append({
            "func_id": func_id,
            "failing_tests": failing_tests,
            "affected_set": affected_set,
            "dist_map": dist_map,
            "scored_cands": scored_cands,
        })

    detection_vs_budget: List[Dict[str, Any]] = []

    for budget in BUDGET_GRID:
        ours_caught = 0
        dep_caught = 0
        risk_caught = 0
        random_caught_counts = []

        # 20 random seeds for stable Monte-Carlo baseline
        rng_list = [random.Random(SEED + i * 37) for i in range(20)]

        for ed in mutant_eval_data:
            failing = ed["failing_tests"]
            cands = ed["scored_cands"]
            aff_set = ed["affected_set"]
            d_map = ed["dist_map"]

            # 1. Ours (Two-phase selection with DP)
            ours_sel = select_tests(cands, aff_set, d_map, budget, algorithm="dp")["selected"]
            if set(ours_sel) & failing:
                ours_caught += 1

            # 2. Dependency-only
            dep_sel = select_baseline_dependency_only(cands, d_map, budget)
            if set(dep_sel) & failing:
                dep_caught += 1

            # 3. Risk-only
            risk_sel = select_baseline_risk_only(cands, budget)
            if set(risk_sel) & failing:
                risk_caught += 1

            # 4. Random (over whole suite, averaged over 20 repeats)
            mut_rand_hits = 0
            for rng in rng_list:
                rand_sel = select_baseline_random(all_tests, budget, rng)
                if set(rand_sel) & failing:
                    mut_rand_hits += 1
            random_caught_counts.append(mut_rand_hits / 20.0)

        ours_pct = round((ours_caught / total_holdout_bugs) * 100.0, 1)
        dep_pct = round((dep_caught / total_holdout_bugs) * 100.0, 1)
        risk_pct = round((risk_caught / total_holdout_bugs) * 100.0, 1)
        rand_pct = round((sum(random_caught_counts) / total_holdout_bugs) * 100.0, 1)

        detection_vs_budget.append({
            "budgetSec": budget,
            "ours": ours_pct,
            "riskBased": risk_pct,
            "dependencyOnly": dep_pct,
            "random": rand_pct,
            "runAll": 100.0,
        })

    # Strategy summary at REFERENCE_BUDGET_SEC
    ref_budget = REFERENCE_BUDGET_SEC
    stats_acc = {
        "Ours": {"tests": [], "time": [], "caught": 0},
        "Risk-Based": {"tests": [], "time": [], "caught": 0},
        "Dependency-Only": {"tests": [], "time": [], "caught": 0},
        "Random": {"tests": [], "time": [], "caught": 0},
        "Run All": {"tests": [suite_size] * len(mutant_eval_data), "time": [suite_time] * len(mutant_eval_data), "caught": total_holdout_bugs},
    }

    rng = random.Random(SEED + 999)
    for ed in mutant_eval_data:
        failing = ed["failing_tests"]
        cands = ed["scored_cands"]
        aff_set = ed["affected_set"]
        d_map = ed["dist_map"]

        # Ours
        res = select_tests(cands, aff_set, d_map, ref_budget, algorithm="dp")
        sel = res["selected"]
        stats_acc["Ours"]["tests"].append(len(sel))
        stats_acc["Ours"]["time"].append(res["totalTimeSec"])
        if set(sel) & failing:
            stats_acc["Ours"]["caught"] += 1

        # Risk-Based
        r_sel = select_baseline_risk_only(cands, ref_budget)
        stats_acc["Risk-Based"]["tests"].append(len(r_sel))
        stats_acc["Risk-Based"]["time"].append(sum(tests_meta_map[t]["timeSec"] for t in r_sel))
        if set(r_sel) & failing:
            stats_acc["Risk-Based"]["caught"] += 1

        # Dependency-Only
        d_sel = select_baseline_dependency_only(cands, d_map, ref_budget)
        stats_acc["Dependency-Only"]["tests"].append(len(d_sel))
        stats_acc["Dependency-Only"]["time"].append(sum(tests_meta_map[t]["timeSec"] for t in d_sel))
        if set(d_sel) & failing:
            stats_acc["Dependency-Only"]["caught"] += 1

        # Random
        rnd_sel = select_baseline_random(all_tests, ref_budget, rng)
        stats_acc["Random"]["tests"].append(len(rnd_sel))
        stats_acc["Random"]["time"].append(sum(tests_meta_map[t]["timeSec"] for t in rnd_sel))
        if set(rnd_sel) & failing:
            stats_acc["Random"]["caught"] += 1

    strategies_summary: List[Dict[str, Any]] = []
    for strat_name, s_data in stats_acc.items():
        mean_tests = round(float(np.mean(s_data["tests"])), 1)
        mean_time = round(float(np.mean(s_data["time"])), 1)
        caught_pct = round((s_data["caught"] / total_holdout_bugs) * 100.0, 1)
        strategies_summary.append({
            "name": strat_name,
            "testsRun": mean_tests,
            "timeSec": mean_time,
            "bugsCaughtPct": caught_pct,
        })

    # Headline numbers for Ours vs Suite
    ours_summary = next(s for s in strategies_summary if s["name"] == "Ours")
    test_red = max(0.0, round((1.0 - (ours_summary["testsRun"] / suite_size)) * 100.0, 1))
    time_saved = max(0.0, round((1.0 - (ours_summary["timeSec"] / suite_time)) * 100.0, 1))
    bug_det = ours_summary["bugsCaughtPct"]

    headline = {
        "testReductionPct": test_red,
        "timeSavedPct": time_saved,
        "bugDetectionPct": bug_det,
    }

    return detection_vs_budget, strategies_summary, headline
