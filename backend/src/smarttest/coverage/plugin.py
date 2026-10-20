"""Pytest plugin to record per-test execution duration and simulated latency."""

import time
import json
from pathlib import Path
from typing import Dict, Any
import pytest

from sample_project.tests.helpers import get_and_reset_simulated_seconds

_TIMING_OUTPUT_PATH = Path(".pytest_timings.json")
_TEST_RECORDS: Dict[str, Dict[str, Any]] = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    """Hooks into test execution to measure wall-clock time and simulated latency."""
    # Reset helper state before test begins
    get_and_reset_simulated_seconds()
    start_time = time.perf_counter()

    # Yield to let pytest run the standard test protocol
    yield

    duration_wall = time.perf_counter() - start_time
    simulated_sec = get_and_reset_simulated_seconds()
    total_sec = max(0.05, round(duration_wall + simulated_sec, 2))

    # Determine node id and relative path
    node_id = str(item.nodeid).replace("\\", "/")
    parts = node_id.split("::")
    file_path = parts[0]
    test_name = parts[-1]

    _TEST_RECORDS[node_id] = {
        "id": node_id,
        "name": test_name,
        "file": file_path,
        "measuredSec": round(duration_wall, 4),
        "simulatedSec": round(simulated_sec, 2),
        "timeSec": total_sec,
        "passed": True,
    }


def pytest_runtest_makereport(item, call):
    """Captures test failure / error status."""
    if call.when == "call" and call.excinfo is not None:
        node_id = str(item.nodeid).replace("\\", "/")
        if node_id in _TEST_RECORDS:
            _TEST_RECORDS[node_id]["passed"] = False


def pytest_sessionfinish(session, exitstatus):
    """Writes test timings to disk upon session completion."""
    with open(_TIMING_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(_TEST_RECORDS, f, indent=2)
