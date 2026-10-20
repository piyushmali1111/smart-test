"""Command Line Interface for running offline build stages and experiments."""

import argparse
import datetime
import json
import random
import sys
from pathlib import Path
from typing import Tuple, List, Dict, Any, Optional
import pandas as pd
import joblib

from smarttest.config import (
    ARTIFACTS_DIR,
    PLOTS_DIR,
    SHOP_DIR,
    SEED,
    TARGET_MUTANTS,
    BUDGET_RANGE,
    REFERENCE_BUDGET_SEC,
)
from smarttest.graph.parser import CallGraphParser
from smarttest.graph.model import DependencyGraph
from smarttest.coverage.collector import CoverageCollector
from smarttest.mutation.runner import MutationRunner
from smarttest.ml.dataset import build_dataset_and_history
from smarttest.ml.train import train_and_select_best_model
from smarttest.ml.evaluate import evaluate_models_on_holdout
from smarttest.experiments.detection import run_detection_experiments
from smarttest.experiments.scalability import run_scalability_experiments
from smarttest.experiments.plots import generate_all_plots


def stage_graph(force: bool = False) -> DependencyGraph:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = ARTIFACTS_DIR / "graph.json"
    if out_file.exists() and not force:
        print(f"[graph] Artifact {out_file} already exists. Skipping.")
        with open(out_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return DependencyGraph(data["nodes"], data["edges"])

    print("[graph] Parsing codebase with AST...")
    parser = CallGraphParser(SHOP_DIR)
    funcs, edges, unresolved = parser.parse_codebase()

    nodes = [f.to_dict() for f in funcs.values()]
    edge_dicts = [{"source": u, "target": v} for u, v in edges]
    dep_graph = DependencyGraph(nodes, edge_dicts)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(dep_graph.to_dict(), f, indent=2)

    print(f"[graph] Saved {len(nodes)} functions, {len(edge_dicts)} call edges to {out_file}")
    return dep_graph


def stage_coverage(dep_graph: DependencyGraph, force: bool = False) -> Tuple[List[Dict[str, Any]], Dict[str, Any], Dict[str, float]]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    tests_file = ARTIFACTS_DIR / "tests.json"
    cov_file = ARTIFACTS_DIR / "coverage.json"
    churn_file = ARTIFACTS_DIR / "churn.json"

    # Churn map (seeded simulated churn per module)
    churn_map: Dict[str, float] = {}
    if churn_file.exists() and not force:
        with open(churn_file, "r", encoding="utf-8") as f:
            churn_map = json.load(f)
    else:
        rng = random.Random(SEED)
        modules = sorted(list({n["id"].split(".")[0] for n in dep_graph.raw_nodes}))
        churn_map = {m: round(rng.uniform(0.15, 0.90), 2) for m in modules}
        with open(churn_file, "w", encoding="utf-8") as f:
            json.dump(churn_map, f, indent=2)

    if tests_file.exists() and cov_file.exists() and not force:
        print("[coverage] Coverage artifacts already exist. Skipping.")
        with open(tests_file, "r", encoding="utf-8") as f:
            tests_list = json.load(f)
        with open(cov_file, "r", encoding="utf-8") as f:
            cov_summary = json.load(f)
        return tests_list, cov_summary, churn_map

    print("[coverage] Running test suite under coverage.py with dynamic contexts...")
    funcs_dict = {n["id"]: n for n in dep_graph.raw_nodes}
    collector = CoverageCollector(funcs_dict)
    tests_list, cov_summary = collector.run_suite_and_collect()

    with open(tests_file, "w", encoding="utf-8") as f:
        json.dump(tests_list, f, indent=2)

    with open(cov_file, "w", encoding="utf-8") as f:
        json.dump(cov_summary, f, indent=2)

    print(f"[coverage] Saved {len(tests_list)} tests (suite time: {cov_summary['suiteTimeSec']}s) to {tests_file}")
    return tests_list, cov_summary, churn_map


def stage_mutate(
    dep_graph: DependencyGraph,
    cov_summary: Dict[str, Any],
    force: bool = False,
) -> List[Dict[str, Any]]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    out_file = ARTIFACTS_DIR / "mutants.json"
    if out_file.exists() and not force:
        print(f"[mutate] Artifact {out_file} already exists. Skipping.")
        with open(out_file, "r", encoding="utf-8") as f:
            return json.load(f)

    print(f"[mutate] Generating and running {TARGET_MUTANTS} mutants...")
    funcs_dict = {n["id"]: n for n in dep_graph.raw_nodes}
    runner = MutationRunner(dep_graph, cov_summary, funcs_dict)
    mutants = runner.run_mutation_pipeline(target_count=TARGET_MUTANTS, max_workers=4)

    killed_count = sum(1 for m in mutants if m.get("killed", False))
    mutation_score = round(killed_count / len(mutants) * 100.0, 1) if mutants else 0.0

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(mutants, f, indent=2)

    print(f"[mutate] Mutants finished: {len(mutants)} total, {killed_count} killed (Score: {mutation_score}%) -> {out_file}")
    return mutants


def stage_dataset(
    mutants: List[Dict[str, Any]],
    tests_list: List[Dict[str, Any]],
    dep_graph: DependencyGraph,
    churn_map: Dict[str, float],
    force: bool = False,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    dataset_file = ARTIFACTS_DIR / "dataset.csv"
    history_file = ARTIFACTS_DIR / "history.json"

    if dataset_file.exists() and history_file.exists() and not force:
        print("[dataset] Dataset artifacts already exist. Skipping.")
        df = pd.read_csv(dataset_file)
        with open(history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        return df, history

    print("[dataset] Constructing leak-free training dataset and frozen serving history...")
    df, history = build_dataset_and_history(mutants, tests_list, dep_graph, churn_map)

    df.to_csv(dataset_file, index=False)
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2)

    print(f"[dataset] Saved dataset with {len(df)} rows to {dataset_file}")
    return df, history


def stage_train(df: pd.DataFrame, force: bool = False) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    model_file = ARTIFACTS_DIR / "model.joblib"
    models_file = ARTIFACTS_DIR / "models.json"

    if model_file.exists() and models_file.exists() and not force:
        print("[train] Model artifacts already exist. Skipping.")
        bundle = joblib.load(model_file)
        with open(models_file, "r", encoding="utf-8") as f:
            models_data = json.load(f)
        return bundle, models_data

    print("[train] Training models with GroupKFold CV and calibrating probabilities...")
    df_train = df[df["split"] == "train"]
    df_holdout = df[df["split"] == "holdout"]

    bundle, best_name, cv_scores = train_and_select_best_model(df_train)
    joblib.dump(bundle, model_file)

    print(f"[train] Best model selected: {best_name} (CV PR-AUC: {cv_scores[best_name]:.3f})")

    print("[train] Evaluating on holdout split and computing permutation importance...")
    models_data = evaluate_models_on_holdout(bundle, df_train, df_holdout)

    with open(models_file, "w", encoding="utf-8") as f:
        json.dump(models_data, f, indent=2)

    print(f"[train] Saved models data to {models_file}")
    return bundle, models_data


def stage_experiments(
    mutants: List[Dict[str, Any]],
    tests_list: List[Dict[str, Any]],
    dep_graph: DependencyGraph,
    model_bundle: Dict[str, Any],
    history: Dict[str, Any],
    churn_map: Dict[str, float],
    models_data: Dict[str, Any],
    df: pd.DataFrame,
    force: bool = False,
) -> None:
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    results_file = ARTIFACTS_DIR / "results.json"
    scalability_file = ARTIFACTS_DIR / "scalability.json"
    meta_file = ARTIFACTS_DIR / "meta.json"

    holdout_mutants = [
        m for m in mutants if m.get("split") == "holdout" and m.get("killed", False)
    ]

    print("[experiments] Running bug detection experiments across budget grid...")
    det_vs_budget, strategies, headline = run_detection_experiments(
        holdout_mutants=holdout_mutants,
        all_tests=tests_list,
        dep_graph=dep_graph,
        model_bundle=model_bundle,
        history=history,
        churn_map=churn_map,
    )

    # Mutation types breakdown
    cat_counts: Dict[str, int] = {}
    for m in mutants:
        cat = m.get("operatorCategory", "other")
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    mutation_types = [{"type": k, "count": v} for k, v in sorted(cat_counts.items())]

    killed_total = sum(1 for m in mutants if m.get("killed", False))
    mutation_score = round(killed_total / len(mutants) * 100.0, 1) if mutants else 0.0

    dataset_summary = {
        "mutants": len(mutants),
        "killedMutants": killed_total,
        "mutationScore": mutation_score,
        "tests": len(tests_list),
        "rows": len(df),
        "mutationTypes": mutation_types,
    }

    results_data = {
        "headline": headline,
        "detectionVsBudget": det_vs_budget,
        "strategies": strategies,
        "dataset": dataset_summary,
        "referenceBudgetSec": REFERENCE_BUDGET_SEC,
        "holdoutMutants": len(holdout_mutants),
    }

    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(results_data, f, indent=2)

    print("[experiments] Running scalability benchmark (Greedy, DP, B&B)...")
    scalability_results, opt_stats = run_scalability_experiments()

    with open(scalability_file, "w", encoding="utf-8") as f:
        json.dump(scalability_results, f, indent=2)

    # Provenance meta.json
    suite_time = round(sum(float(t["timeSec"]) for t in tests_list), 2)
    meta_data = {
        "projectName": "shop",
        "numFunctions": len(dep_graph.raw_nodes),
        "numTests": len(tests_list),
        "suiteTimeSec": suite_time,
        "durationsSimulated": True,
        "budgetRange": BUDGET_RANGE,
        "seed": SEED,
        "builtAt": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "mutationScore": mutation_score,
        "optimalityGapStats": opt_stats,
    }

    with open(meta_file, "w", encoding="utf-8") as f:
        json.dump(meta_data, f, indent=2)

    print("[experiments] Rendering publication-quality dark theme charts...")
    generate_all_plots(
        detection_data=det_vs_budget,
        strategies_data=strategies,
        models_data=models_data,
        scalability_data=scalability_results,
        output_dir=PLOTS_DIR,
    )
    print(f"[experiments] All artifacts and plots generated in {ARTIFACTS_DIR}")


def build_all(force: bool = False):
    print("=== Starting Smart Test Selection Offline Pipeline ===")
    t0 = datetime.datetime.now()

    dep_graph = stage_graph(force=force)
    tests_list, cov_summary, churn_map = stage_coverage(dep_graph, force=force)
    mutants = stage_mutate(dep_graph, cov_summary, force=force)
    df, history = stage_dataset(mutants, tests_list, dep_graph, churn_map, force=force)
    model_bundle, models_data = stage_train(df, force=force)
    stage_experiments(
        mutants=mutants,
        tests_list=tests_list,
        dep_graph=dep_graph,
        model_bundle=model_bundle,
        history=history,
        churn_map=churn_map,
        models_data=models_data,
        df=df,
        force=force,
    )

    elapsed = (datetime.datetime.now() - t0).total_seconds()
    print(f"=== Pipeline Complete in {elapsed:.1f} seconds ===")


def main():
    parser = argparse.ArgumentParser(description="Smart Test Selection CLI")
    subparsers = parser.add_subparsers(dest="command")

    for cmd in ["graph", "coverage", "mutate", "dataset", "train", "experiments", "build-all"]:
        sp = subparsers.add_parser(cmd)
        sp.add_argument("--force", action="store_true", help="Force recomputation of artifacts")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "graph":
        stage_graph(force=args.force)
    elif args.command == "coverage":
        g = stage_graph(force=False)
        stage_coverage(g, force=args.force)
    elif args.command == "mutate":
        g = stage_graph(force=False)
        _, cov, _ = stage_coverage(g, force=False)
        stage_mutate(g, cov, force=args.force)
    elif args.command == "dataset":
        g = stage_graph(force=False)
        tests, cov, churn = stage_coverage(g, force=False)
        m = stage_mutate(g, cov, force=False)
        stage_dataset(m, tests, g, churn, force=args.force)
    elif args.command == "train":
        g = stage_graph(force=False)
        tests, cov, churn = stage_coverage(g, force=False)
        m = stage_mutate(g, cov, force=False)
        df, _ = stage_dataset(m, tests, g, churn, force=False)
        stage_train(df, force=args.force)
    elif args.command == "experiments":
        g = stage_graph(force=False)
        tests, cov, churn = stage_coverage(g, force=False)
        m = stage_mutate(g, cov, force=False)
        df, hist = stage_dataset(m, tests, g, churn, force=False)
        bundle, models_data = stage_train(df, force=False)
        stage_experiments(m, tests, g, bundle, hist, churn, models_data, df, force=args.force)
    elif args.command == "build-all":
        build_all(force=args.force)


if __name__ == "__main__":
    main()
