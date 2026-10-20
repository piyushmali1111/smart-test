"""FastAPI Application providing the REST API for Smart Test Selection."""

import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from smarttest.config import CORS_ORIGINS
from smarttest.store import store
from smarttest.selection.pipeline import select_tests, compare_algorithms
from smarttest.ml.predict import predict_test_risks
from smarttest.experiments.replay import simulate_replay
from smarttest.api.schemas import (
    HealthResponse,
    MetaResponse,
    GraphResponse,
    AffectedRequest,
    AffectedResponse,
    SelectRequest,
    SelectResponse,
    CompareRequest,
    CompareResponse,
    ResultsResponse,
    ModelsResponse,
    ReplayRequest,
    ReplayResponse,
)

logger = logging.getLogger("smarttest.api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes artifact store on API startup."""
    try:
        store.load()
        logger.info("ArtifactStore loaded successfully.")
    except Exception as e:
        logger.warning("ArtifactStore failed to load: %s", str(e))
    yield


app = FastAPI(
    title="Smart Test Selection API",
    description="Intelligent test selection engine utilizing Graph Algorithms, ML, and Knapsack optimization.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"error": "validation_error", "detail": str(exc)},
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": "http_error", "detail": exc.detail},
    )


def _check_store_loaded():
    if not store.is_loaded or store.dep_graph is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Artifacts are not loaded. Run 'make build' first.",
        )


def _validate_changed_functions(changed: List[str]):
    if not changed:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Field 'changed' must contain at least 1 function ID.",
        )
    if len(changed) > 5:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="A maximum of 5 changed functions is supported per request.",
        )

    unknown = [c for c in changed if c not in store.dep_graph.node_to_scc]
    if unknown:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Unknown function ID(s): {unknown}",
        )


@app.get("/health", response_model=HealthResponse)
@app.get("/api/health", response_model=HealthResponse)
def get_health():
    return {"status": "ok"}


@app.get("/api/meta", response_model=MetaResponse)
def get_meta():
    _check_store_loaded()
    return store.meta


@app.get("/api/graph", response_model=GraphResponse)
def get_graph():
    _check_store_loaded()
    return store.dep_graph.to_dict()


@app.post("/api/affected", response_model=AffectedResponse)
def post_affected(req: AffectedRequest):
    _check_store_loaded()
    _validate_changed_functions(req.changed)

    affected_list, dist_map = store.dep_graph.get_affected_and_distances(req.changed)
    affected_ids = {a["id"] for a in affected_list}

    # Find candidate tests whose coverage intersects the affected set
    raw_candidates = []
    for test in store.tests_list:
        test_covers = set(test.get("covers", []))
        covers_affected = sorted(list(test_covers & affected_ids))
        if covers_affected:
            t_copy = dict(test)
            t_copy["covers"] = covers_affected
            raw_candidates.append(t_copy)

    # Score candidates using calibrated ML model
    scored_candidates = predict_test_risks(
        changed_functions=req.changed,
        candidate_tests=raw_candidates,
        model_bundle=store.model_bundle,
        dep_graph=store.dep_graph,
        history=store.history,
        churn_map=store.churn_map,
    )

    return {
        "affected": affected_list,
        "candidateTests": scored_candidates,
        "sccGroups": store.dep_graph.scc_groups,
    }


@app.post("/api/select", response_model=SelectResponse)
def post_select(req: SelectRequest):
    _check_store_loaded()
    _validate_changed_functions(req.changed)

    if req.budget_sec <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Budget must be greater than 0 seconds.",
        )

    alg = req.algorithm.lower()
    if alg not in ("greedy", "dp", "bnb"):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unknown algorithm '{req.algorithm}'. Must be 'greedy', 'dp', or 'bnb'.",
        )

    # 1. Compute affected
    affected_list, dist_map = store.dep_graph.get_affected_and_distances(req.changed)
    affected_ids = {a["id"] for a in affected_list}

    # 2. Extract candidate tests
    raw_cands = []
    for test in store.tests_list:
        test_covers = set(test.get("covers", []))
        covers_affected = sorted(list(test_covers & affected_ids))
        if covers_affected:
            t_copy = dict(test)
            t_copy["covers"] = covers_affected
            raw_cands.append(t_copy)

    # 3. Score with ML
    scored_cands = predict_test_risks(
        changed_functions=req.changed,
        candidate_tests=raw_cands,
        model_bundle=store.model_bundle,
        dep_graph=store.dep_graph,
        history=store.history,
        churn_map=store.churn_map,
    )

    # 4. Run two-phase selection
    result = select_tests(
        candidate_tests=scored_cands,
        affected_functions=affected_ids,
        distance_map=dist_map,
        budget_sec=req.budget_sec,
        algorithm=alg,
    )

    return result


@app.post("/api/compare", response_model=CompareResponse)
def post_compare(req: CompareRequest):
    _check_store_loaded()
    _validate_changed_functions(req.changed)

    if req.budget_sec <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Budget must be greater than 0 seconds.",
        )

    affected_list, dist_map = store.dep_graph.get_affected_and_distances(req.changed)
    affected_ids = {a["id"] for a in affected_list}

    raw_cands = []
    for test in store.tests_list:
        test_covers = set(test.get("covers", []))
        covers_affected = sorted(list(test_covers & affected_ids))
        if covers_affected:
            t_copy = dict(test)
            t_copy["covers"] = covers_affected
            raw_cands.append(t_copy)

    scored_cands = predict_test_risks(
        changed_functions=req.changed,
        candidate_tests=raw_cands,
        model_bundle=store.model_bundle,
        dep_graph=store.dep_graph,
        history=store.history,
        churn_map=store.churn_map,
    )

    results = compare_algorithms(
        candidate_tests=scored_cands,
        affected_functions=affected_ids,
        distance_map=dist_map,
        budget_sec=req.budget_sec,
    )

    return {
        "results": results,
        "scalability": store.scalability_data,
    }


@app.get("/api/results", response_model=ResultsResponse)
def get_results():
    _check_store_loaded()
    return store.results_data


@app.get("/api/models", response_model=ModelsResponse)
def get_models():
    _check_store_loaded()
    return store.models_data


@app.post("/api/replay", response_model=ReplayResponse)
def post_replay(req: ReplayRequest):
    _check_store_loaded()

    if req.budget_sec <= 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Budget must be greater than 0 seconds.",
        )
    if not (1 <= req.num_changes <= 100):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="numChanges must be between 1 and 100.",
        )

    replay_seed = req.seed if req.seed is not None else 42

    res = simulate_replay(
        holdout_mutants=store.holdout_mutants,
        all_tests=store.tests_list,
        dep_graph=store.dep_graph,
        model_bundle=store.model_bundle,
        history=store.history,
        churn_map=store.churn_map,
        budget_sec=req.budget_sec,
        num_changes=req.num_changes,
        seed=replay_seed,
    )

    return res
