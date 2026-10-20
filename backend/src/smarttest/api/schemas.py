"""Pydantic schemas with automatic camelCase serialization for REST API."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    """Base Pydantic model configuring camelCase alias serialization and extra field acceptance."""
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="allow",
    )


class HealthResponse(CamelModel):
    status: str = "ok"


class BudgetRange(CamelModel):
    min: float
    max: float
    step: float
    default: float


class MetaResponse(CamelModel):
    project_name: str
    num_functions: int
    num_tests: int
    suite_time_sec: float
    durations_simulated: bool
    budget_range: BudgetRange
    seed: int
    built_at: str


class GraphNode(CamelModel):
    id: str
    label: str
    file: str
    kind: str
    topo_level: Optional[int] = None


class GraphEdge(CamelModel):
    source: str
    target: str


class GraphResponse(CamelModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class AffectedNode(CamelModel):
    id: str
    distance: int


class CandidateTest(CamelModel):
    id: str
    name: str
    time_sec: float
    risk: float
    covers: List[str]


class AffectedRequest(CamelModel):
    changed: List[str] = Field(..., min_length=1, max_length=5)


class AffectedResponse(CamelModel):
    affected: List[AffectedNode]
    candidate_tests: List[CandidateTest]
    scc_groups: List[List[str]]


class SelectRequest(CamelModel):
    changed: List[str] = Field(..., min_length=1, max_length=5)
    budget_sec: float
    algorithm: str = "dp"


class SelectResponse(CamelModel):
    selected: List[str]
    total_time_sec: float
    total_risk: float
    coverage_pct: float
    algorithm_runtime_ms: float
    nodes_explored: Optional[int] = None
    timed_out: Optional[bool] = None
    uncoverable_count: Optional[int] = None
    memory_kb: Optional[float] = None


class CompareRequest(CamelModel):
    changed: List[str] = Field(..., min_length=1, max_length=5)
    budget_sec: float


class AlgorithmCompareResult(CamelModel):
    algorithm: str
    total_risk: float
    total_time_sec: float
    tests_selected: int
    runtime_ms: float
    memory_kb: float
    optimality_gap_pct: float


class ScalabilityRow(CamelModel):
    n: int
    greedy_ms: float
    dp_ms: float
    bnb_ms: float
    bnb_timed_out: Optional[bool] = None


class CompareResponse(CamelModel):
    results: List[AlgorithmCompareResult]
    scalability: List[ScalabilityRow]


class Headline(CamelModel):
    test_reduction_pct: float
    time_saved_pct: float
    bug_detection_pct: float


class DetectionRow(CamelModel):
    budget_sec: float
    ours: float
    risk_based: Optional[float] = None
    dependency_only: Optional[float] = None
    random: float
    run_all: float = 100.0


class StrategySummary(CamelModel):
    name: str
    tests_run: float
    time_sec: float
    bugs_caught_pct: float


class DatasetSummary(CamelModel):
    mutants: int
    tests: int
    rows: int
    mutation_types: List[Dict[str, Any]]


class ResultsResponse(CamelModel):
    headline: Headline
    detection_vs_budget: List[DetectionRow]
    strategies: List[StrategySummary]
    dataset: DatasetSummary
    reference_budget_sec: Optional[float] = None
    mutation_score: Optional[float] = None
    holdout_mutants: Optional[int] = None


class ModelMetric(CamelModel):
    name: str
    accuracy: float
    precision: float
    recall: float
    f1: float
    roc_auc: Optional[float] = None
    pr_auc: Optional[float] = None


class FeatureImportance(CamelModel):
    feature: str
    importance: float


class ModelsResponse(CamelModel):
    models: List[ModelMetric]
    feature_importance: List[FeatureImportance]
    selected_model: Optional[str] = None


class ReplayRequest(CamelModel):
    budget_sec: float
    num_changes: int = 20
    seed: Optional[int] = None


class ReplayStep(CamelModel):
    step: int
    changed_id: str
    tests_run: int
    cumulative_tests_run: int
    caught: bool
    cumulative_caught: int
    cumulative_run_all: int


class ReplayResponse(CamelModel):
    total_tests: int
    total_bugs: int
    steps: List[ReplayStep]
    sampled_with_replacement: Optional[bool] = None
