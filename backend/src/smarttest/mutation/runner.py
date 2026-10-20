"""Mutation runner injecting AST faults, executing candidate tests, and logging outcomes."""

import ast
import copy
import json
import random
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import List, Dict, Set, Tuple, Any, Optional

from smarttest.config import (
    BACKEND_DIR,
    SAMPLE_PROJECT_DIR,
    SHOP_DIR,
    SEED,
    TARGET_MUTANTS,
    MUTANT_TIMEOUT_SEC,
    TOTAL_ROUNDS,
    TRAIN_ROUNDS_MAX,
)
from smarttest.mutation.operators import (
    enumerate_mutants_in_ast,
    SingleMutationTransformer,
    MutantCandidate,
)
from smarttest.graph.model import DependencyGraph


def _run_single_mutant_worker(
    mutant_id: str,
    func_id: str,
    file_rel_path: str,
    mut_candidate: MutantCandidate,
    candidate_test_ids: List[str],
    backend_dir_str: str,
    sample_proj_str: str,
) -> Dict[str, Any]:
    """Applies mutation to source file in a temp workspace, runs candidate tests, records results."""
    backend_dir = Path(backend_dir_str)
    sample_proj_dir = Path(sample_proj_str)
    shop_dir = sample_proj_dir / "shop"

    source_file = backend_dir / file_rel_path
    with open(source_file, "r", encoding="utf-8") as f:
        orig_code = f.read()

    orig_tree = ast.parse(orig_code, filename=str(source_file))

    # Apply mutation
    transformer = SingleMutationTransformer(
        target_lineno=mut_candidate.lineno,
        target_col=mut_candidate.col_offset,
        mutation_type=mut_candidate.transformer_type,
        replacement=mut_candidate.replacement,
    )
    mutated_tree = transformer.visit(orig_tree)
    ast.fix_missing_locations(mutated_tree)

    try:
        mutated_code = ast.unparse(mutated_tree)
        compile(mutated_code, str(source_file), "exec")
    except Exception as e:
        return {
            "id": mutant_id,
            "status": "syntax_error",
            "failingTests": [],
            "killed": False,
        }

    # Run candidate tests in a temporary directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_backend = Path(tmp_dir) / "backend"
        # Copy backend minimally (pyproject.toml, sample_project)
        shutil.copytree(sample_proj_dir, tmp_backend / "sample_project")
        shutil.copy2(backend_dir / "pyproject.toml", tmp_backend / "pyproject.toml")

        # Overwrite the target shop file with mutated code
        target_shop_file = tmp_backend / file_rel_path
        with open(target_shop_file, "w", encoding="utf-8") as f:
            f.write(mutated_code)

        # Execute candidate tests
        pytest_cmd = [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "--tb=no",
        ] + candidate_test_ids

        failing_tests: List[str] = []
        try:
            res = subprocess.run(
                pytest_cmd,
                cwd=str(tmp_backend),
                capture_output=True,
                text=True,
                timeout=MUTANT_TIMEOUT_SEC,
            )
            # Parse failures from stdout
            for line in res.stdout.splitlines():
                line = line.strip()
                if line.startswith("FAILED "):
                    # Format: FAILED sample_project/tests/test_cart.py::test_calculate_total_basic - AssertionError...
                    parts = line.split(" ", 2)
                    if len(parts) >= 2:
                        test_node_id = parts[1].replace("\\", "/")
                        failing_tests.append(test_node_id)
        except subprocess.TimeoutExpired:
            return {
                "id": mutant_id,
                "status": "timeout",
                "failingTests": [],
                "killed": False,
            }
        except Exception:
            return {
                "id": mutant_id,
                "status": "error",
                "failingTests": [],
                "killed": False,
            }

    killed = len(failing_tests) > 0
    return {
        "id": mutant_id,
        "status": "killed" if killed else "survived",
        "failingTests": sorted(list(set(failing_tests))),
        "killed": killed,
    }


class MutationRunner:
    """Manages mutant candidate enumeration, stratified sampling, and execution."""

    def __init__(
        self,
        dep_graph: DependencyGraph,
        coverage_summary: Dict[str, Any],
        functions_map: Dict[str, Any],
    ):
        self.dep_graph = dep_graph
        self.coverage_summary = coverage_summary
        self.functions_map = functions_map
        self.rng = random.Random(SEED)

    def run_mutation_pipeline(
        self, target_count: int = TARGET_MUTANTS, max_workers: int = 4
    ) -> List[Dict[str, Any]]:
        """Enumerates, samples, executes, and rounds mutants."""
        # 1. Enumerate all possible mutants
        all_candidates: List[Tuple[str, str, MutantCandidate]] = []
        # (func_id, file_rel_path, candidate)

        py_files = sorted(list(SHOP_DIR.glob("*.py")))
        for py_path in py_files:
            rel_path = str(py_path.relative_to(BACKEND_DIR)).replace("\\", "/")
            try:
                with open(py_path, "r", encoding="utf-8") as f:
                    content = f.read()
                tree = ast.parse(content, filename=str(py_path))
            except Exception:
                continue

            # Map line numbers to function IDs
            mod_funcs = [
                (f["startLine"], f["endLine"], f_id)
                for f_id, f in self.functions_map.items()
                if Path(f.get("file", "")).name == py_path.name
            ]

            candidates = enumerate_mutants_in_ast(tree)
            for cand in candidates:
                # Find enclosing function
                enclosing_func = None
                for s_l, e_l, f_id in mod_funcs:
                    if s_l <= cand.lineno <= e_l:
                        enclosing_func = f_id
                        break
                if enclosing_func:
                    all_candidates.append((enclosing_func, rel_path, cand))

        # 2. Stratified sampling by function and category
        by_func: Dict[str, List[Tuple[str, str, MutantCandidate]]] = {}
        for item in all_candidates:
            f_id = item[0]
            by_func.setdefault(f_id, []).append(item)

        sampled_pool: List[Tuple[str, str, MutantCandidate]] = []
        # Ensure at least 3-5 mutants per function where possible
        for f_id, fun_cands in by_func.items():
            self.rng.shuffle(fun_cands)
            take_n = min(len(fun_cands), max(4, target_count // len(by_func)))
            sampled_pool.extend(fun_cands[:take_n])

        if len(sampled_pool) < target_count and len(all_candidates) > len(sampled_pool):
            remaining = [c for c in all_candidates if c not in sampled_pool]
            self.rng.shuffle(remaining)
            needed = target_count - len(sampled_pool)
            sampled_pool.extend(remaining[:needed])

        self.rng.shuffle(sampled_pool)
        sampled_pool = sampled_pool[:target_count]

        # 3. Assign IDs, Rounds (1..10), and Splits (train vs holdout)
        mutant_records: List[Dict[str, Any]] = []
        task_args = []

        for idx, (f_id, rel_path, cand) in enumerate(sampled_pool, start=1):
            m_id = f"mut_{idx:04d}"
            # Round assignment 1..10
            m_round = (idx % TOTAL_ROUNDS) + 1
            m_split = "train" if m_round <= TRAIN_ROUNDS_MAX else "holdout"

            # Determine candidate tests for this mutant's affected set
            affected, _ = self.dep_graph.get_affected_and_distances([f_id])
            affected_ids = {a["id"] for a in affected}

            cand_tests: List[str] = []
            for t_id, funcs in self.coverage_summary.get("testToFunctions", {}).items():
                if set(funcs) & affected_ids:
                    cand_tests.append(t_id)

            if not cand_tests:
                # Fallback to tests covering f_id directly
                cand_tests = self.coverage_summary.get("functionToTests", {}).get(f_id, [])

            record = {
                "id": m_id,
                "functionId": f_id,
                "file": rel_path,
                "line": cand.lineno,
                "operatorCategory": cand.category,
                "originalSnippet": cand.orig_repr,
                "mutatedSnippet": cand.mut_repr,
                "round": m_round,
                "split": m_split,
                "candidateTests": cand_tests,
                "killed": False,
                "failingTests": [],
            }
            mutant_records.append(record)

            task_args.append((
                m_id,
                f_id,
                rel_path,
                cand,
                cand_tests,
                str(BACKEND_DIR),
                str(SAMPLE_PROJECT_DIR),
            ))

        # 4. Execute mutants in parallel
        results_by_id: Dict[str, Dict[str, Any]] = {}
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {
                executor.submit(_run_single_mutant_worker, *arg): arg[0]
                for arg in task_args
            }
            for future in as_completed(future_to_id):
                m_id = future_to_id[future]
                try:
                    res = future.result()
                    results_by_id[m_id] = res
                except Exception as exc:
                    results_by_id[m_id] = {
                        "id": m_id,
                        "status": "error",
                        "failingTests": [],
                        "killed": False,
                    }

        # Merge results into mutant_records
        final_mutants: List[Dict[str, Any]] = []
        for rec in mutant_records:
            res = results_by_id.get(rec["id"], {})
            rec["killed"] = res.get("killed", False)
            rec["failingTests"] = res.get("failingTests", [])
            rec["status"] = res.get("status", "unknown")
            final_mutants.append(rec)

        return final_mutants
