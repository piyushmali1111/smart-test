"""Contract verification tests ensuring REST API strictly conforms to frontend JSON shapes."""

import pytest
from fastapi.testclient import TestClient

from smarttest.api.main import app
from smarttest.store import store
from smarttest.graph.model import DependencyGraph


@pytest.fixture(scope="module", autouse=True)
def setup_mock_store():
    """Seeds the in-memory store with minimal mock artifacts if real artifacts not built."""
    if not store.is_loaded:
        store.raw_graph = {
            "nodes": [
                {"id": "cart.calculate_total", "label": "calculate_total", "file": "shop/cart.py", "kind": "function", "topoLevel": 2},
                {"id": "cart.add_item", "label": "add_item", "file": "shop/cart.py", "kind": "function", "topoLevel": 1},
            ],
            "edges": [{"source": "cart.calculate_total", "target": "cart.add_item"}],
        }
        store.dep_graph = DependencyGraph(store.raw_graph["nodes"], store.raw_graph["edges"])
        store.meta = {
            "projectName": "shop",
            "numFunctions": 2,
            "numTests": 5,
            "suiteTimeSec": 12.5,
            "durationsSimulated": True,
            "budgetRange": {"min": 5.0, "max": 100.0, "step": 5.0, "default": 30.0},
            "seed": 42,
            "builtAt": "2026-10-20T10:00:00Z",
        }
        store.tests_list = [
            {"id": "sample_project/tests/test_cart.py::test_calculate_total_basic", "name": "test_calculate_total_basic", "file": "sample_project/tests/test_cart.py", "timeSec": 2.5, "covers": ["cart.calculate_total"]}
        ]
        store.churn_map = {"cart": 0.5}
        store.history = {}

        # Dummy model
        class DummyModel:
            def predict_proba(self, X):
                import numpy as np
                return np.array([[0.1, 0.85]] * len(X))

        store.model_bundle = {"model": DummyModel(), "feature_names": ["dep_distance"]}
        store.models_data = {
            "models": [{"name": "Random Forest", "accuracy": 0.9, "precision": 0.85, "recall": 0.88, "f1": 0.86, "rocAuc": 0.92, "prAuc": 0.89}],
            "featureImportance": [{"feature": "Dependency Distance", "importance": 0.45}],
            "selectedModel": "Random Forest",
        }
        store.results_data = {
            "headline": {"testReductionPct": 65.0, "timeSavedPct": 60.0, "bugDetectionPct": 92.0},
            "detectionVsBudget": [{"budgetSec": 30.0, "ours": 92.0, "random": 45.0, "runAll": 100.0}],
            "strategies": [{"name": "Ours", "testsRun": 5.0, "timeSec": 12.0, "bugsCaughtPct": 92.0}],
            "dataset": {"mutants": 100, "killedMutants": 80, "mutationScore": 80.0, "tests": 5, "rows": 200, "mutationTypes": [{"type": "arithmetic", "count": 25}]},
        }
        store.scalability_data = [{"n": 100, "greedyMs": 0.1, "dpMs": 2.5, "bnbMs": 1.2}]
        store.holdout_mutants = [
            {"id": "m1", "functionId": "cart.calculate_total", "split": "holdout", "killed": True, "failingTests": ["sample_project/tests/test_cart.py::test_calculate_total_basic"], "candidateTests": ["sample_project/tests/test_cart.py::test_calculate_total_basic"]}
        ]
        store.is_loaded = True


client = TestClient(app)


def test_api_health_contract():
    res = client.get("/api/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_api_meta_contract():
    res = client.get("/api/meta")
    assert res.status_code == 200
    data = res.json()
    assert "projectName" in data
    assert "budgetRange" in data
    assert "suiteTimeSec" in data
    assert "durationsSimulated" in data


def test_api_graph_contract():
    res = client.get("/api/graph")
    assert res.status_code == 200
    data = res.json()
    assert "nodes" in data and "edges" in data
    assert isinstance(data["nodes"], list)
    assert isinstance(data["edges"], list)


def test_api_affected_contract():
    payload = {"changed": ["cart.calculate_total"]}
    res = client.post("/api/affected", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "affected" in data
    assert "candidateTests" in data
    assert "sccGroups" in data


def test_api_select_contract():
    payload = {"changed": ["cart.calculate_total"], "budgetSec": 30.0, "algorithm": "dp"}
    res = client.post("/api/select", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "selected" in data
    assert "totalTimeSec" in data
    assert "totalRisk" in data
    assert "coveragePct" in data
    assert "algorithmRuntimeMs" in data


def test_api_compare_contract():
    payload = {"changed": ["cart.calculate_total"], "budgetSec": 30.0}
    res = client.post("/api/compare", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "results" in data
    assert "scalability" in data
    assert len(data["results"]) == 3


def test_api_results_contract():
    res = client.get("/api/results")
    assert res.status_code == 200
    data = res.json()
    assert "headline" in data
    assert "detectionVsBudget" in data
    assert "strategies" in data
    assert "dataset" in data


def test_api_models_contract():
    res = client.get("/api/models")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert "featureImportance" in data


def test_api_replay_contract():
    payload = {"budgetSec": 30.0, "numChanges": 5, "seed": 42}
    res = client.post("/api/replay", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "totalTests" in data
    assert "totalBugs" in data
    assert "steps" in data
    assert len(data["steps"]) == 5


def test_api_validation_errors():
    # 1. Unknown function ID -> 404
    res = client.post("/api/affected", json={"changed": ["nonexistent_function"]})
    assert res.status_code == 404
    err = res.json()
    assert "error" in err and "detail" in err

    # 2. Invalid budget -> 422
    res = client.post("/api/select", json={"changed": ["cart.calculate_total"], "budgetSec": -10.0})
    assert res.status_code == 422
    err = res.json()
    assert "error" in err and "detail" in err
