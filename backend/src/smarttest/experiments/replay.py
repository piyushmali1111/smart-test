"""Replay simulation evaluating cumulative efficiency across an historical sequence of commits."""

import random
from typing import List, Dict, Any, Optional

from smarttest.graph.model import DependencyGraph
from smarttest.selection.pipeline import select_tests
from smarttest.ml.predict import predict_test_risks


def simulate_replay(
    holdout_mutants: List[Dict[str, Any]],
    all_tests: List[Dict[str, Any]],
    dep_graph: DependencyGraph,
    model_bundle: Dict[str, Any],
    history: Dict[str, Any],
    churn_map: Dict[str, float],
    budget_sec: float,
    num_changes: int = 20,
    seed: int = 42,
) -> Dict[str, Any]:
    """Simulates a sequence of code commits using holdout mutants.

    Strictly uses held-out killed mutants to prevent evaluation contamination.
    """
    tests_meta_map = {t["id"]: t for t in all_tests}
    suite_size = len(all_tests)

    killed_holdout = [m for m in holdout_mutants if m.get("killed", False)]
    if not killed_holdout:
        return {
            "totalTests": num_changes * suite_size,
            "totalBugs": num_changes,
            "steps": [],
            "sampledWithReplacement": False,
        }

    rng = random.Random(seed)
    with_replacement = num_changes > len(killed_holdout)

    if with_replacement:
        sampled_mutants = rng.choices(killed_holdout, k=num_changes)
    else:
        sampled_mutants = rng.sample(killed_holdout, k=num_changes)

    steps: List[Dict[str, Any]] = []
    cum_tests_run = 0
    cum_caught = 0
    cum_run_all = 0

    for step_idx, m in enumerate(sampled_mutants, start=1):
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

        sel_res = select_tests(
            candidate_tests=scored_cands,
            affected_functions=affected_set,
            distance_map=dist_map,
            budget_sec=budget_sec,
            algorithm="dp",
        )
        selected_ids = sel_res["selected"]
        n_tests = len(selected_ids)

        is_caught = bool(set(selected_ids) & failing_tests)

        cum_tests_run += n_tests
        cum_caught += 1 if is_caught else 0
        cum_run_all += suite_size

        steps.append({
            "step": step_idx,
            "changedId": func_id,
            "testsRun": n_tests,
            "cumulativeTestsRun": cum_tests_run,
            "caught": is_caught,
            "cumulativeCaught": cum_caught,
            "cumulativeRunAll": cum_run_all,
        })

    return {
        "totalTests": num_changes * suite_size,
        "totalBugs": num_changes,
        "steps": steps,
        "sampledWithReplacement": with_replacement,
    }
