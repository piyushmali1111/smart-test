"""Runs the test suite under coverage.py with dynamic contexts to build the test-to-function map."""

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
import coverage

from smarttest.config import (
    BACKEND_DIR,
    SAMPLE_PROJECT_DIR,
    SAMPLE_TESTS_DIR,
    ARTIFACTS_DIR,
)
from smarttest.graph.parser import CallGraphParser


class CoverageCollector:
    """Orchestrates test suite execution under coverage and attributes lines to functions."""

    def __init__(self, functions_map: Dict[str, Any]):
        self.functions_map = functions_map
        # Pre-index functions by (file_path, line_range)
        # file_path is relative, e.g. "sample_project/shop/cart.py" or absolute
        self.file_funcs: Dict[str, List[Tuple[int, int, str]]] = {}
        for func_id, func in self.functions_map.items():
            f_path = str(func.get("file", "")).replace("\\", "/")
            f_name = Path(f_path).name
            if f_name not in self.file_funcs:
                self.file_funcs[f_name] = []
            self.file_funcs[f_name].append(
                (func["startLine"], func["endLine"], func_id)
            )

    def run_suite_and_collect(self) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Executes full pytest suite under coverage, mapping covered lines to function IDs."""
        timing_file = BACKEND_DIR / ".pytest_timings.json"
        if timing_file.exists():
            timing_file.unlink()

        # Run pytest under coverage using subprocess
        cmd = [
            sys.executable,
            "-m",
            "coverage",
            "run",
            "-m",
            "pytest",
            "-q",
            "-p",
            "smarttest.coverage.plugin",
            str(SAMPLE_TESTS_DIR),
        ]

        result = subprocess.run(
            cmd,
            cwd=str(BACKEND_DIR),
            capture_output=True,
            text=True,
        )

        if not timing_file.exists():
            raise RuntimeError(
                f"Coverage collection failed to generate timings file:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
            )

        with open(timing_file, "r", encoding="utf-8") as f:
            timings: Dict[str, Dict[str, Any]] = json.load(f)

        # Baseline assertion: every test must pass on unmodified code
        failed_tests = [t for t, rec in timings.items() if not rec.get("passed", False)]
        if failed_tests:
            raise RuntimeError(
                f"Baseline failure: {len(failed_tests)} tests failed on unmodified code:\n{failed_tests[:5]}"
            )

        # Load coverage data
        cov = coverage.Coverage()
        cov.load()
        cov_data = cov.get_data()

        test_to_funcs: Dict[str, Set[str]] = {t_id: set() for t_id in timings}
        func_to_tests: Dict[str, Set[str]] = {f_id: set() for f_id in self.functions_map}

        for measured_file in cov_data.measured_files():
            file_name = Path(measured_file).name
            if file_name not in self.file_funcs:
                continue

            func_ranges = self.file_funcs[file_name]
            contexts_by_line = cov_data.contexts_by_lineno(measured_file)

            for line_no, contexts in contexts_by_line.items():
                # Find enclosing function
                matched_func_id = None
                for start_l, end_l, f_id in func_ranges:
                    if start_l <= line_no <= end_l:
                        matched_func_id = f_id
                        break

                if not matched_func_id:
                    continue

                for ctx in contexts:
                    if not ctx:
                        continue
                    # Format: sample_project.tests.test_cart.test_calculate_total_basic
                    parts = ctx.split(".")
                    if len(parts) >= 2:
                        test_file = "/".join(parts[:-1]) + ".py"
                        test_func_name = parts[-1]
                        test_id = f"{test_file}::{test_func_name}"

                        if test_id in test_to_funcs:
                            test_to_funcs[test_id].add(matched_func_id)
                            func_to_tests[matched_func_id].add(test_id)

        # Build tests list
        tests_list: List[Dict[str, Any]] = []
        for t_id, rec in timings.items():
            covered = sorted(list(test_to_funcs.get(t_id, set())))
            tests_list.append({
                "id": t_id,
                "name": rec["name"],
                "file": rec["file"],
                "timeSec": rec["timeSec"],
                "covers": covered,
            })

        tests_list.sort(key=lambda t: t["id"])

        suite_time = round(sum(t["timeSec"] for t in tests_list), 2)
        covered_funcs = set()
        for funcs in test_to_funcs.values():
            covered_funcs.update(funcs)

        coverage_summary = {
            "totalTests": len(tests_list),
            "totalFunctions": len(self.functions_map),
            "coveredFunctions": len(covered_funcs),
            "suiteTimeSec": suite_time,
            "testToFunctions": {t_id: sorted(list(f_ids)) for t_id, f_ids in test_to_funcs.items()},
            "functionToTests": {f_id: sorted(list(t_ids)) for f_id, t_ids in func_to_tests.items()},
        }

        return tests_list, coverage_summary
