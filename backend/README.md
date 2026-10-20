# Smart Test Selection Engine (Backend)

An intelligent test selection engine for college Design and Analysis of Algorithms (DAA) projects. When developers modify code, the engine performs static dependency reachability analysis on a call graph, identifies candidate test suites, predicts fault-detection risk via a machine learning classifier, and optimizes test subset selection under dynamic execution time budgets using Set Cover and 0/1 Knapsack optimization.

```
+-----------------------------------------------------------------------------------+
|                            SMART TEST SELECTION ENGINE                            |
+-----------------------------------------------------------------------------------+
|  1. Code Modification                                                             |
|     Changed Functions -> AST Static Call Graph -> Reverse Reachability (BFS/DFS)  |
|                                                                                   |
|  2. SCC Condensation                                                              |
|     Tarjan's SCC -> Condense Cycles -> Kahn's Algorithm (Topological Call Levels) |
|                                                                                   |
|  3. Candidate Identification                                                      |
|     Coverage Attribution -> Test-to-Function Intersection                         |
|                                                                                   |
|  4. ML Risk Scoring                                                               |
|     Feature Extraction (12 Features) -> Calibrated Model -> Noisy-OR Multi-Change   |
|                                                                                   |
|  5. Two-Phase Optimization                                                        |
|     Phase 1: Risk-Weighted Greedy Set Cover (Protect Affected Code)              |
|     Phase 2: Knapsack Value Maximization (DP 0/1 vs Greedy vs Branch & Bound)     |
|                                                                                   |
|  6. REST API & Reactive Dashboard                                                 |
|     FastAPI Engine -> CamelCase Schemas -> React 18 + Vite (Midnight Indigo UI)   |
+-----------------------------------------------------------------------------------+
```

---

## 1. Quick Start

### Prerequisites
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (recommended) or standard `pip`

### Installation & Build
```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
uv venv
.\.venv\Scripts\activate
uv pip install -e ".[dev]"

# Execute the complete offline pipeline (Builds graph, coverage, mutants, ML model, experiments)
python -m smarttest.cli build-all

# Run the backend REST API server on port 8000
python -m uvicorn smarttest.api.main:app --reload --port 8000 --host 0.0.0.0
```

### Connect to Frontend
In `frontend/.env`:
```ini
VITE_USE_MOCK=false
VITE_API_BASE_URL=http://localhost:8000
```
Then start the Vite dev server:
```bash
npm --prefix frontend run dev
```

---

## 2. Mapping DAA Topics to Hand-Written Algorithms

In accordance with strict DAA requirements, all core graph and combinatorial optimization algorithms are **implemented by hand** from scratch without third-party graph or solver libraries.

| Algorithm | Hand-Written File | DAA Complexity | Role in Engine |
|---|---|---|---|
| **Multi-Source BFS** | `src/smarttest/graph/algorithms.py` | $O(V + E)$ | Computes minimum condensed distance from changed functions to all reachable nodes |
| **Iterative DFS** | `src/smarttest/graph/algorithms.py` | $O(V + E)$ | Computes reachability sets avoiding Python recursion limits |
| **Tarjan's SCC** | `src/smarttest/graph/algorithms.py` | $O(V + E)$ | Detects circular dependencies and groups mutually recursive functions |
| **Kahn's Topological Sort** | `src/smarttest/graph/algorithms.py` | $O(V + E)$ | Computes topological order and longest-path call hierarchy depth on condensed DAG |
| **Weighted Greedy Set Cover** | `src/smarttest/selection/set_cover.py` | $O(n \cdot \|C\|)$ | Phase 1: Maximizes protected affected functions weighted by inverse distance $w_f = 1 / (1 + d_f)$ |
| **Greedy Knapsack** | `src/smarttest/selection/knapsack_greedy.py` | $O(n \log n)$ | Phase 2 Heuristic: Sorts remaining tests by risk/duration density ratio |
| **0/1 Dynamic Programming** | `src/smarttest/selection/knapsack_dp.py` | $O(n \cdot W)$ | Phase 2 Optimal: Integer-discretized DP table with boolean backtracking matrix |
| **Branch and Bound** | `src/smarttest/selection/branch_bound.py` | Worst case $O(2^n)$ | Phase 2 Exact: Pruned DFS with fractional knapsack upper bound and timeout safety |

---

## 3. Dataset Creation & Anti-Leakage Protocol

1. **Mutant Generation:** 450 synthetic bugs injected across 5 AST mutation categories (Arithmetic, Comparison, Boolean, Constant, Statement) across all modules in `shop/`.
2. **Killed vs Survived:** Candidate tests executed against mutants in isolated sandboxes. Mutants killed by at least 1 test are kept for the ML dataset; surviving mutants are tracked for mutation score calculation.
3. **Round-Based Temporal History:** Mutants are assigned across 10 chronological rounds:
   - **Rounds 1–7 (`train`):** Model training and GroupKFold cross-validation.
   - **Rounds 8–10 (`holdout`):** Reserved exclusively for final held-out evaluation and empirical experiments.
4. **Zero-Leakage Invariance:**
   - History features for a mutant in round $k$ are derived strictly from rounds $< k$.
   - Cross-validation uses `GroupKFold(n_splits=5)` grouped by `mutant_id` so rows from the same mutant never cross fold boundaries.
   - Live serving inference uses frozen historical statistics compiled up through round 7 (`history.json`).

---

## 4. Honest Limitations & Design Assumptions

- **Static Call Graph Approximations:** AST static resolution traces direct calls, aliased imports, and module attribute accesses. Dynamic dispatches, reflection, and third-party library internals are recorded as unresolved calls.
- **Simulated Test Durations:** To demonstrate large-scale Knapsack time trade-offs without incurring multi-minute waits in a classroom demo, tests declare realistic I/O delays via `simulate_io()` which are added to wall-clock time (`durationsSimulated: true`).
- **Synthetic Module Churn:** Churn frequencies are seeded and simulated to emulate real git commit velocity.
- **Multi-Change Probabilistic Approximation:** The ML model is trained on single-fault mutants. When multiple functions change simultaneously, risks are aggregated via the standard Noisy-OR assumption: $r_{\text{combined}} = 1 - \prod (1 - r_i)$.

---

## 5. REST API Endpoints & Example Requests

All endpoints accept and return camelCase JSON.

### Health Check
```bash
curl -X GET http://localhost:8000/api/health
```

### Metadata & Controls Sizing
```bash
curl -X GET http://localhost:8000/api/meta
```

### Static Call Graph
```bash
curl -X GET http://localhost:8000/api/graph
```

### Impact & Candidate Tests
```bash
curl -X POST http://localhost:8000/api/affected \
  -H "Content-Type: application/json" \
  -d '{"changed": ["cart.calculate_total"]}'
```

### Test Selection Optimization
```bash
curl -X POST http://localhost:8000/api/select \
  -H "Content-Type: application/json" \
  -d '{"changed": ["cart.calculate_total"], "budgetSec": 30.0, "algorithm": "dp"}'
```

### Algorithm Comparison
```bash
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{"changed": ["cart.calculate_total"], "budgetSec": 30.0}'
```

### Empirical Results & Strategies
```bash
curl -X GET http://localhost:8000/api/results
```

### ML Models & Permutation Importance
```bash
curl -X GET http://localhost:8000/api/models
```

### Historical Commit Replay
```bash
curl -X POST http://localhost:8000/api/replay \
  -H "Content-Type: application/json" \
  -d '{"budgetSec": 30.0, "numChanges": 20, "seed": 42}'
```
