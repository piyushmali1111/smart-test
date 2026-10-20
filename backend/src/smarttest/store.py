"""Loads precomputed artifacts into memory once at server startup."""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import joblib

from smarttest.config import ARTIFACTS_DIR
from smarttest.graph.model import DependencyGraph


class ArtifactStore:
    """In-memory cache for all precomputed artifacts."""

    def __init__(self, artifacts_dir: Path = ARTIFACTS_DIR):
        self.artifacts_dir = artifacts_dir
        self.is_loaded: bool = False

        self.meta: Dict[str, Any] = {}
        self.raw_graph: Dict[str, Any] = {}
        self.dep_graph: Optional[DependencyGraph] = None
        self.tests_list: List[Dict[str, Any]] = []
        self.tests_map: Dict[str, Dict[str, Any]] = {}
        self.coverage_summary: Dict[str, Any] = {}
        self.churn_map: Dict[str, float] = {}
        self.mutants_list: List[Dict[str, Any]] = []
        self.holdout_mutants: List[Dict[str, Any]] = []
        self.history: Dict[str, Any] = {}
        self.model_bundle: Optional[Dict[str, Any]] = None
        self.models_data: Dict[str, Any] = {}
        self.results_data: Dict[str, Any] = {}
        self.scalability_data: List[Dict[str, Any]] = []

    def load(self) -> None:
        """Loads and parses all artifacts from disk. Fails fast if artifacts are missing."""
        required_files = [
            "meta.json",
            "graph.json",
            "tests.json",
            "coverage.json",
            "churn.json",
            "mutants.json",
            "history.json",
            "model.joblib",
            "models.json",
            "results.json",
            "scalability.json",
        ]

        missing = [f for f in required_files if not (self.artifacts_dir / f).exists()]
        if missing:
            raise FileNotFoundError(
                f"Missing required artifacts: {missing}. Run 'make build' first."
            )

        with open(self.artifacts_dir / "meta.json", "r", encoding="utf-8") as f:
            self.meta = json.load(f)

        with open(self.artifacts_dir / "graph.json", "r", encoding="utf-8") as f:
            self.raw_graph = json.load(f)
            self.dep_graph = DependencyGraph(
                self.raw_graph.get("nodes", []),
                self.raw_graph.get("edges", []),
            )

        with open(self.artifacts_dir / "tests.json", "r", encoding="utf-8") as f:
            self.tests_list = json.load(f)
            self.tests_map = {t["id"]: t for t in self.tests_list}

        with open(self.artifacts_dir / "coverage.json", "r", encoding="utf-8") as f:
            self.coverage_summary = json.load(f)

        with open(self.artifacts_dir / "churn.json", "r", encoding="utf-8") as f:
            self.churn_map = json.load(f)

        with open(self.artifacts_dir / "mutants.json", "r", encoding="utf-8") as f:
            self.mutants_list = json.load(f)
            self.holdout_mutants = [
                m for m in self.mutants_list if m.get("split") == "holdout"
            ]

        with open(self.artifacts_dir / "history.json", "r", encoding="utf-8") as f:
            self.history = json.load(f)

        self.model_bundle = joblib.load(self.artifacts_dir / "model.joblib")

        with open(self.artifacts_dir / "models.json", "r", encoding="utf-8") as f:
            self.models_data = json.load(f)

        with open(self.artifacts_dir / "results.json", "r", encoding="utf-8") as f:
            self.results_data = json.load(f)

        with open(self.artifacts_dir / "scalability.json", "r", encoding="utf-8") as f:
            self.scalability_data = json.load(f)

        self.is_loaded = True


# Global singleton instance
store = ArtifactStore()
